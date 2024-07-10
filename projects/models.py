from django.db import models
import uuid


class Project(models.Model):
    STATUS_TYPES = (("active", "Active"), ("hold", "Hold"), ("inactive", "Inactive"))
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    logo = models.CharField(max_length=255, null=True, blank=True)
    developer_name = models.CharField(max_length=255, null=True, blank=True)
    vbn = models.CharField(max_length=64, null=True, blank=True)
    province = models.CharField(max_length=128, null=True, blank=True)
    city = models.CharField(max_length=128, null=True, blank=True)
    postal_code = models.CharField(max_length=32, null=True, blank=True)
    address = models.CharField(max_length=610, null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_TYPES, default="active")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    builder = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="projects",
    )
    assignees = models.ManyToManyField("users.User", related_name="employee_projects")
    no_of_homes = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.id} {self.name} {self.builder}"


class Home(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    lot_no = models.CharField(max_length=64, null=True, blank=True)
    street_no = models.CharField(max_length=64, null=True, blank=True)
    address = models.CharField(max_length=256, null=True, blank=True)
    city = models.CharField(max_length=64, null=True, blank=True)
    province = models.CharField(max_length=64, null=True, blank=True)
    postal_code = models.CharField(max_length=32, null=True, blank=True)
    enrollment_no = models.CharField(max_length=128, unique=True)
    warranty_start_date = models.DateField(null=True, blank=True)
    home_type = models.CharField(max_length=64, null=True, blank=True)
    client = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        related_name="homes",
        null=True,
        blank=True,
    )
    project = models.ForeignKey(
        "projects.Project", on_delete=models.CASCADE, related_name="homes"
    )

    def __str__(self):
        return f"{self.id} {self.enrollment_no}"


class BluePrint(models.Model):
    label = models.CharField(max_length=64, null=True, blank=True)
    category = models.CharField(max_length=64, null=True, blank=True)
    home = models.ForeignKey(
        "projects.Home", on_delete=models.CASCADE, null=True, blank=True
    )

    def __str__(self):
        return f"{self.label} {self.category}"


class BluePrintImage(models.Model):
    """
    Model to store blue print images because a blueprint can have multiple images
    """

    blue_print = models.ForeignKey(
        "projects.BluePrint", related_name="images", on_delete=models.CASCADE
    )
    image = models.CharField(max_length=256, null=True, blank=True)

    def __str__(self):
        return f"{self.id} {self.blue_print, self.image}"
