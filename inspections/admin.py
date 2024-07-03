from django.contrib import admin
from inspections.models import (
    Inspection,
    Deficiency,
    DefImage,
    HomeInspection,
    HomeInspectionReview,
)

# Register your models here.


class InspectionAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "warranty_type", "no_of_def", "builder")
    search_fields = ["name"]


admin.site.register(Inspection, InspectionAdmin)


class DeficiencyAdmin(admin.ModelAdmin):
    list_display = ("id", "location", "status", "created_at")


admin.site.register(Deficiency, DeficiencyAdmin)


class DefImageAdmin(admin.ModelAdmin):
    list_display = ("id", "image", "deficiency")


admin.site.register(DefImage, DefImageAdmin)


class HomeInspectionAdmin(admin.ModelAdmin):
    list_display = ("id", "home", "created_at")


admin.site.register(HomeInspection, HomeInspectionAdmin)


class HomeInspectionReviewAdmin(admin.ModelAdmin):
    list_display = ("id", "home_inspection", "created_at")


admin.site.register(HomeInspectionReview, HomeInspectionReviewAdmin)
