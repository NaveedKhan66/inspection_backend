from django.contrib import admin
from projects.models import Project, Home, BluePrint, BluePrintImage


class ProjectAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "builder", "created_at", "updated_at"]


admin.site.register(Project, ProjectAdmin)


class HomeAdmin(admin.ModelAdmin):
    list_display = ("id", "lot_no", "enrollment_no", "warranty_start_date", "client")


admin.site.register(Home, HomeAdmin)


class BluePrintAdmin(admin.ModelAdmin):
    list_display = ("id", "label", "category", "home")


admin.site.register(BluePrint, BluePrintAdmin)


class BluePrintImageAdmin(admin.ModelAdmin):
    list_display = ("id", "image", "blue_print")


admin.site.register(BluePrintImage, BluePrintImageAdmin)
