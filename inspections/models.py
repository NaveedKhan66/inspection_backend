from typing import Iterable
from django.db import models
import uuid
from django.utils import timezone


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
    created_at = models.DateTimeField(auto_now_add=True)
    is_reviewed = models.BooleanField(default=False)
    owner_visibility = models.BooleanField(default=False)
    inspector = models.CharField(max_length=128, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    due_date = models.DateField(null=True, blank=True)

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
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=64, choices=STATUS_TYPES, default="incomplete")
    is_reviewed = models.BooleanField(default=False)
    completion_date = models.DateField(null=True, blank=True)

    def __str__(self) -> str:
        return f"{self.id} {self.home_inspection}"

    def save(self, *args, **kwargs):
        """Maintain no_of_def in Inspection model and set completion date if status is complete"""

        is_new = self.pk is None
        # Check if the status is being updated to 'complete'
        if self.status == "complete" and self.completion_date is None:
            self.completion_date = timezone.now().date()

        super().save(*args, **kwargs)

        # Only increase the deficiency count if the deficiency is created
        if is_new:
            self.home_inspection.inspection.no_of_def += 1
            self.home_inspection.inspection.save()


class DefImage(models.Model):
    deficiency = models.ForeignKey(
        "inspections.Deficiency", on_delete=models.CASCADE, related_name="images"
    )
    image = models.CharField(max_length=256)


class DeficiencyUpdateLog(models.Model):
    deficiency = models.ForeignKey(
        Deficiency, on_delete=models.CASCADE, related_name="update_logs"
    )
    actor_name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    description = models.TextField()

    def __str__(self):
        return f"Update on Deficiency {self.deficiency.id} by {self.actor_name}"


class DeficiencyNotification(models.Model):
    deficiency = models.ForeignKey(
        Deficiency, on_delete=models.CASCADE, related_name="notifications"
    )
    actor_name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    description = models.TextField()
    user = models.ForeignKey(
        "users.User", on_delete=models.CASCADE, related_name="deficiency_notifications"
    )
    read = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification for Deficiency {self.deficiency.id} by {self.actor_name}"


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
