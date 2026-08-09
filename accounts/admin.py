
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from unfold.admin import ModelAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin, ModelAdmin):

    list_display = (
        "username",
        "email",
        "role",
        "organization",
        "is_active",
    )

    list_filter = (
        "role",
        "organization",
        "is_active",
    )

    search_fields = (
        "username",
        "email",
    )

    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (
            "Personal Information",
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "email",
                )
            },
        ),
        (
            "TeamFlow",
            {
                "fields": (
                    "organization",
                    "role",
                )
            },
        ),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (
            "Important Dates",
            {
                "fields": (
                    "last_login",
                    "date_joined",
                )
            },
        ),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "username",
                    "email",
                    "password1",
                    "password2",
                    "role",
                    "organization",
                ),
            },
        ),
    )

