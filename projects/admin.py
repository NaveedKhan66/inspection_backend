from django.contrib import admin
from projects.models import Project


class ProjectAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "builder", "created_at", "updated_at"]


admin.site.register(Project, ProjectAdmin)
