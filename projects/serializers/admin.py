from rest_framework import serializers
from projects.models import Project
from rest_framework.exceptions import ValidationError
from django.contrib.auth import get_user_model
from projects.models import Home, BluePrint, BluePrintImage

User = get_user_model()

# TODO: convert all read_only kwargs into read_only fields


class ProjectSerializer(serializers.ModelSerializer):

    class Meta:
        model = Project
        fields = "__all__"
        extra_kwargs = {
            "id": {"read_only": True},
            "created_at": {"read_only": True},
            "updated_at": {"read_only": True},
            "assignees": {"read_only": True},
        }

    def validate(self, attrs):
        validated_data = super().validate(attrs)
        builder_user = validated_data.get("builder")

        if builder_user:
            if builder_user.user_type != "builder":
                raise ValidationError(
                    {"detail": "Only builder can be assigned to projects"}
                )

        return validated_data


class ProjectAssigneeSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "profile_picture", "role"]

    def get_role(self, obj):
        if obj.user_type == "employee":
            return obj.employee.role
        return None


class ProjectBuilderSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ["id", "first_name", "last_name"]


class ProjectListSerializer(serializers.ModelSerializer):
    assignees = ProjectAssigneeSerializer(many=True)
    builder = ProjectBuilderSerializer()

    class Meta:
        model = Project
        fields = [
            "id",
            "name",
            "no_of_homes",
            "assignees",
            "status",
            "builder",
            "developer_name",
            "vbn",
            "city",
            "province",
            "postal_code",
            "address",
        ]


class ProjectAssigneeUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer to add and remove assignees from the project
    """

    assignees = serializers.ListField(
        child=serializers.UUIDField(format="hex_verbose"),
        write_only=True,
        required=False,
    )
    remove_assignee = serializers.UUIDField(
        format="hex_verbose", write_only=True, required=False
    )

    class Meta:
        model = Project
        fields = ["assignees", "remove_assignee"]

    def update(self, instance, validated_data):
        # addition
        assignees = validated_data.pop("assignees", None)
        if assignees:
            users = User.objects.filter(id__in=assignees, user_type="employee")
            instance.assignees.add(*users)

        # Removal
        remove_assignee = validated_data.pop("remove_assignee", None)
        if remove_assignee:
            try:
                user = User.objects.get(id=remove_assignee)
                instance.assignees.remove(user)
            except User.DoesNotExist:
                pass

        return super().update(instance, validated_data)


class AssigneeSerializer(serializers.ModelSerializer):
    """General assignee serializer for projects"""

    role = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "first_name", "last_name", "email", "profile_picture", "role"]

    def get_role(self, obj):
        if obj.user_type == "employee":
            if obj.employee.role:
                return obj.employee.role
        return None


class ProjectAssigneeListSerializer(serializers.ModelSerializer):
    """Serializer to list all assignees of a project"""

    assignees = AssigneeSerializer(many=True, read_only=True)

    class Meta:
        model = Project
        fields = ["assignees"]


class HomeSerializer(serializers.ModelSerializer):
    """General Home serializer"""

    class Meta:
        model = Home
        fields = "__all__"
        read_only_fields = ["project"]

    def create(self, validated_data):
        if isinstance(validated_data, list):
            # Bulk create
            return Home.objects.bulk_create([Home(**item) for item in validated_data])
        return super().create(validated_data)


class ClientforHomeSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "first_name", "last_name", "email", "phone_no"]


class HomeListRetrieveSerializer(serializers.ModelSerializer):
    """
    Home serializer for list and retrieve which contains
    additional attribute for client
    """

    client = ClientforHomeSerializer()

    class Meta:
        model = Home
        fields = "__all__"


class BluePrintImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = BluePrintImage
        fields = ["id", "image"]


class BluePrintSerializer(serializers.ModelSerializer):
    images = BluePrintImageSerializer(many=True, required=False)

    class Meta:
        model = BluePrint
        fields = ["id", "label", "category", "home", "images"]

    def create(self, validated_data):
        images_data = validated_data.pop("images", [])
        blueprint = BluePrint.objects.create(**validated_data)
        for image_data in images_data:
            BluePrintImage.objects.create(blue_print=blueprint, **image_data)
        return blueprint

    def update(self, instance, validated_data):
        images_data = validated_data.pop("images", [])
        instance.label = validated_data.get("label", instance.label)
        instance.category = validated_data.get("category", instance.category)
        instance.home = validated_data.get("home", instance.home)
        instance.save()

        # Update images
        for image_data in images_data:
            image_id = image_data.get("id")
            if image_id:
                # Update existing image
                image_instance = BluePrintImage.objects.get(
                    id=image_id, blue_print=instance
                )
                image_instance.image = image_data.get("image", image_instance.image)
                image_instance.save()
            else:
                # Create new image
                BluePrintImage.objects.create(blue_print=instance, **image_data)

        return instance
