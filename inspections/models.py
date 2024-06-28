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


class Deficiency(models.Model):
    inspection = models.ForeignKey(
        "inspections.Inspection", on_delete=models.CASCADE, related_name="deficiencies"
    )
    location = models.CharField(max_length=128, null=True, blank=True)
    trade = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="deficiencies",
    )
    project = models.ForeignKey(
        "projects.Project", on_delete=models.CASCADE, related_name="deficiencies"
    )
    home = models.ForeignKey(
        "projects.Home", on_delete=models.CASCADE, related_name="deficiencies"
    )
    description = models.TextField()

    def save(self, *args, **kwargs):
        """Maintain no_of_def in Inspection model"""

        self.inspection.no_of_def += 1
        self.inspection.save()
        super().save(*args, **kwargs)


class DefImage(models.Model):
    deficiency = models.ForeignKey(
        "inspections.Deficiency", on_delete=models.CASCADE, related_name="images"
    )
    image = models.CharField(max_length=256)
