from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


class UserAdmin(BaseUserAdmin):
    """
    Custom User Admin that uses email as the primary identifier.
    """
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (("Personal info"), {"fields": ("first_name", "last_name", "date_of_birth", "bio")}),
        (("Contact"), {"fields": ("phone_number",)}),
        (("Location"), {"fields": ("country", "city")}),
        (("Professional"), {"fields": ("occupation",)}),
        (("Profile"), {"fields": ("profile_picture",)}),
        (("Verification"), {"fields": ("is_email_verified", "is_phone_verified")}),
        (
            ("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (("Important dates"), {"fields": ("last_login", "date_joined"), "classes": ("collapse",)}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "username", "password1", "password2"),
            },
        ),
    )
    readonly_fields = ("created_at", "updated_at")
    list_display = ("email", "username", "is_email_verified", "is_staff", "is_superuser", "created_at")
    search_fields = ("email", "username", "phone_number", "country", "city")
    list_filter = ("is_email_verified", "is_phone_verified", "is_staff", "is_superuser", "created_at")
    ordering = ("email",)


admin.site.register(User, UserAdmin)

