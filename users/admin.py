from django.contrib import admin
from users.models import User

# Register your models here.


class UserAdmin(admin.ModelAdmin):
    list_display = ["id", "email", "username", "user_type", "first_name", "last_name"]


admin.site.register(User, UserAdmin)
