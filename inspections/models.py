from typing import Iterable
from django.db import models
import uuid


class Inspection(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, null=True, blank=True)
    warranty_type = models.CharField(max_length=128, null=True, blank=True)
    no_of_def = models.IntegerField(default=0)
    builder = models.ForeignKey(
        "users.User", on_delete=models.CASCADE, related_name="inspections"
    )

    def __str__(self) -> str:
        return f"{self.id} {self.name}"


class HomeInspection(models.Model):
    inspection = models.ForeignKey("inspections.Inspection", on_delete=models.CASCADE)
    home = models.ForeignKey("projects.Home", on_delete=models.CASCADE)
    created_at = models.DateField(auto_now_add=True)
    is_reviewed = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f"{self.id} {self.inspection.name}"


class Deficiency(models.Model):
    STATUS_TYPES = (
        ("complete", "Complete"),
        ("incomplete", "Incomplete"),
        ("pending_approval", "Pending Approval"),
    )
    home_inspection = models.ForeignKey(
        "inspections.HomeInspection",
        on_delete=models.CASCADE,
        related_name="deficiencies",
    )
    location = models.CharField(max_length=128, null=True, blank=True)
    trade = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="deficiencies",
    )
    description = models.TextField()
    created_at = models.DateField(auto_now_add=True, null=True, blank=True)
    status = models.CharField(max_length=64, choices=STATUS_TYPES, default="incomplete")
    is_reviewed = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f"{self.id} {self.home_inspection}"

    def save(self, *args, **kwargs):
        """Maintain no_of_def in Inspection model"""

        super().save(*args, **kwargs)
        self.home_inspection.inspection.no_of_def += 1
        self.home_inspection.inspection.save()


class DefImage(models.Model):
    deficiency = models.ForeignKey(
        "inspections.Deficiency", on_delete=models.CASCADE, related_name="images"
    )
    image = models.CharField(max_length=256)


class HomeInspectionReview(models.Model):
    home_inspection = models.OneToOneField(
        "inspections.HomeInspection", on_delete=models.CASCADE, related_name="review"
    )
    created_at = models.DateField(auto_now_add=True)
    designate = models.BooleanField(default=False)
    owner_signature_image = models.CharField(max_length=256, null=True, blank=True)
    inspector_signature_image = models.CharField(max_length=256, null=True, blank=True)

    def save(self, *args, **kwargs):
        """Sets the is_reviewed field of home inspection to True when review is done"""
        super().save(*args, **kwargs)
        self.home_inspection.is_reviewed = True
        self.home_inspection.save()
