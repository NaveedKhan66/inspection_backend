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
    postal_code = models.IntegerField(null=True, blank=True)
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
