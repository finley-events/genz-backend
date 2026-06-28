# apps/referrals/admin.py

from django.contrib import admin

from .models import Referral, ReferralReward


@admin.register(Referral)
class ReferralAdmin(admin.ModelAdmin):
    list_display = (
        "referrer",
        "referred_user",
        "referral_code_used",
        "status",
        "reward_amount",
        "created_at",
        "qualified_at",
        "rewarded_at",
    )

    list_filter = (
        "status",
        "created_at",
        "qualified_at",
        "rewarded_at",
    )

    search_fields = (
        "referrer__username",
        "referrer__email",
        "referrer__phone_number",
        "referred_user__username",
        "referred_user__email",
        "referred_user__phone_number",
        "referral_code_used",
    )

    readonly_fields = (
        "id",
        "created_at",
        "qualified_at",
        "rewarded_at",
    )

    ordering = ("-created_at",)


@admin.register(ReferralReward)
class ReferralRewardAdmin(admin.ModelAdmin):
    list_display = (
        "referral",
        "transaction",
        "amount",
        "status",
        "created_at",
    )

    list_filter = (
        "status",
        "created_at",
    )

    search_fields = (
        "referral__referrer__username",
        "referral__referrer__email",
        "referral__referred_user__username",
        "referral__referred_user__email",
        "transaction__reference",
    )

    readonly_fields = (
        "id",
        "created_at",
    )

    ordering = ("-created_at",)
