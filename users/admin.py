from django.contrib import admin
from users.models import User
from users.models import Builder
from users.models import Trade
from users.models import Client
from users.models import BuilderEmployee


# Register your models here.


class UserAdmin(admin.ModelAdmin):
    list_display = ["id", "email", "username", "user_type", "first_name", "last_name"]


admin.site.register(User, UserAdmin)


class BuilderAdmin(admin.ModelAdmin):
    list_display = ["id", "user"]


admin.site.register(Builder, BuilderAdmin)


class BuilderEmployeeAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "builder", "role"]


admin.site.register(BuilderEmployee, BuilderEmployeeAdmin)


class TradeAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "builder"]


admin.site.register(Trade, TradeAdmin)


class ClientAdmin(admin.ModelAdmin):
    list_display = ["id", "user"]


admin.site.register(Client, ClientAdmin)
