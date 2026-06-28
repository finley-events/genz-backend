from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import Profile, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        "email",
        "username",
        "phone_number",
        "first_name",
        "last_name",
        "role",
        "is_phone_verified",
        "is_kyc_verified",
        "is_staff",
        "is_active",
    )

    list_filter = (
        "role",
        "is_staff",
        "is_superuser",
        "is_active",
        "is_phone_verified",
        "is_kyc_verified",
    )

    search_fields = (
        "email",
        "username",
        "phone_number",
        "first_name",
        "last_name",
    )

    ordering = ("email",)

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            "Personal Info",
            {
                "fields": (
                    "username",
                    "phone_number",
                    "first_name",
                    "last_name",
                )
            },
        ),
        (
            "Verification",
            {
                "fields": (
                    "is_phone_verified",
                    "is_kyc_verified",
                )
            },
        ),
        (
            "Permissions",
            {
                "fields": (
                    "role",
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Important Dates", {"fields": ("last_login",)}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "username",
                    "phone_number",
                    "password1",
                    "password2",
                    "is_staff",
                    "is_superuser",
                ),
            },
        ),
    )


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "display_name",
        "country",
        "city",
        "badge_level",
        "reputation_score",
    )

    search_fields = (
        "user__email",
        "user__username",
        "display_name",
        "referral_code",
    )

    readonly_fields = (
        "referral_code",
        "created_at",
        "updated_at",
    )
