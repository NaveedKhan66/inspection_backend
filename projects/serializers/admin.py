from rest_framework import serializers
from projects.models import Project
from rest_framework.exceptions import ValidationError
from django.contrib.auth import get_user_model
from projects.models import Home, BluePrint, BluePrintImage
from django.db.models import Q
from users.models import Client

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
        fields = ["id", "profile_picture", "role", "first_name", "last_name"]

    def get_role(self, obj):
        if obj.user_type == "employee":
            if obj.employee:
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
            "logo",
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


def validate_enrollment_no(value):
    if value == None:
        raise serializers.ValidationError("Enrollment number cannot be empty")
    return value


class HomeSerializer(serializers.ModelSerializer):
    """General Home serializer"""

    enrollment_no = serializers.IntegerField(validators=[validate_enrollment_no])

    class Meta:
        model = Home
        fields = "__all__"
        read_only_fields = ["project"]

    def create(self, validated_data):
        if isinstance(validated_data, list):
            # For bulk creation
            enrollment_nos = [item["enrollment_no"] for item in validated_data]
            addresses = [
                item["address"] for item in validated_data if item.get("address")
            ]
            existing_homes = Home.objects.filter(
                Q(enrollment_no__in=enrollment_nos) | Q(address__in=addresses)
            )
            existing_homes_dict = {home.enrollment_no: home for home in existing_homes}

            new_homes = []
            updated_homes = []
            for item in validated_data:
                enrollment_no = item["enrollment_no"]
                if enrollment_no in existing_homes_dict:
                    home = existing_homes_dict[enrollment_no]
                    for key, value in item.items():
                        setattr(home, key, value)
                    updated_homes.append(home)
                else:
                    new_homes.append(Home(**item))

            if new_homes:
                Home.objects.bulk_create(new_homes)

            if updated_homes:
                Home.objects.bulk_update(
                    updated_homes,
                    fields=[
                        f.name
                        for f in Home._meta.fields
                        if f.name not in ["id", "project"]
                    ],
                )

            return new_homes + updated_homes

        else:
            home, created = Home.objects.filter(
                Q(enrollment_no=validated_data.get("enrollment_no"))
                | Q(address=validated_data.get("address"))
            ).update_or_create(defaults=validated_data)

            if created:
                """Handle no_of_homes of project upon creation"""
                home.project.no_of_homes += 1
                home.project.save()
            owner_email = validated_data.get("owner_email")
            owner_name = validated_data.get("owner_name")
            owner_no = validated_data.get("owner_no")
            owner_created = False
            if owner_email:
                try:
                    user = User.objects.get(username=owner_email)
                except User.DoesNotExist:
                    owner_created = True
                    user = User.objects.create(
                        username=owner_email,
                        email=owner_email,
                        first_name=owner_name,
                        phone_no=owner_no,
                        user_type="client",
                    )

                user.set_unusable_password()
                user.save()
                if owner_created:
                    client_profile = Client.objects.create(user=user)

                home.client = user
                home.save()
            return home

    def update(self, instance, validated_data):
        owner_email = validated_data.get("owner_email")
        owner_name = validated_data.get("owner_name")
        owner_no = validated_data.get("owner_no")
        owner_created = False
        if owner_email:
            try:
                user = User.objects.get(username=owner_email)
            except User.DoesNotExist:
                owner_created = True
                user = User.objects.create(
                    username=owner_email,
                    email=owner_email,
                    first_name=owner_name,
                    phone_no=owner_no,
                    user_type="client",
                )

            user.set_unusable_password()
            user.save()
            if owner_created:
                client_profile = Client.objects.create(user=user)
            instance.client = user
            instance.save()
        return super().update(instance, validated_data)


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
