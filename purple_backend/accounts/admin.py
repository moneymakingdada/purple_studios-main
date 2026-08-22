from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    model = User
    list_display = ("email", "username", "first_name", "last_name", "role", "phone", "is_active", "created_at")
    list_filter = ("role", "is_active", "is_email_verified")
    search_fields = ("email", "username", "first_name", "last_name", "phone")
    ordering = ("-created_at",)
    fieldsets = BaseUserAdmin.fieldsets + (
        ("Purple profile", {"fields": ("role", "phone", "avatar", "is_email_verified")}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ("Purple profile", {"fields": ("email", "role", "phone")}),
    )
