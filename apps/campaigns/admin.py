from django.contrib import admin

from .models import (
    Campaign,
    CampaignMedia,
    CampaignTask,
    CampaignParticipation,
    CampaignSubmission,
    CampaignReward,
    CampaignFunding,
)


@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):

    list_display = (
        "title",
        "sponsor",
        "campaign_type",
        "status",
        "budget",
        "remaining_budget",
        "start_date",
        "end_date",
        "created_at",
    )

    list_filter = (
        "status",
        "campaign_type",
        "visibility",
    )

    search_fields = (
        "title",
        "description",
        "sponsor__username",
        "slug",
    )

    readonly_fields = (
        "id",
        "budget",
        "remaining_budget",
        "created_at",
        "updated_at",
    )

    ordering = ("-created_at",)


@admin.register(CampaignMedia)
class CampaignMediaAdmin(admin.ModelAdmin):

    list_display = (
        "campaign",

    )

    search_fields = ("campaign__title",)

    readonly_fields = (
        "id",

    )


@admin.register(CampaignTask)
class CampaignTaskAdmin(admin.ModelAdmin):

    list_display = (
        "title",
        "campaign",
        "task_type",
        "verification_type",
        "reward",
        "max_completions",
    )

    list_filter = (
        "task_type",
        "verification_type",
    )

    search_fields = (
        "title",
        "campaign__title",
    )

    readonly_fields = ("id",)


@admin.register(CampaignParticipation)
class CampaignParticipationAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "campaign",
        "status",
        "reward_paid",
        "reward_amount",
        "joined_at",
        "completed_at",
    )

    list_filter = (
        "status",
        "reward_paid",
    )

    search_fields = (
        "user__username",
        "campaign__title",
    )

    readonly_fields = (
        "id",
        "joined_at",
        "completed_at",
    )

    ordering = ("-joined_at",)


@admin.register(CampaignSubmission)
class CampaignSubmissionAdmin(admin.ModelAdmin):

    list_display = (
        "participation",
        "task",
        "status",
        "verified_by",
    )

    list_filter = (
        "status",
    )

    search_fields = (
        "participation__user__username",
        "participation__campaign__title",
        "task__title",
    )

    readonly_fields = (
        "id",
    )

@admin.register(CampaignReward)
class CampaignRewardAdmin(admin.ModelAdmin):

    list_display = (
        "participation",
        "wallet",
        "amount",
        "status",
        "paid_at",
    )

    list_filter = ("status",)

    search_fields = (
        "participation__user__username",
        "participation__campaign__title",
    )

    readonly_fields = (
        "id",
        "transaction",
        "wallet",
        "amount",
        "paid_at",
    )

    ordering = ("-paid_at",)

    def has_add_permission(
        self,
        request,
    ):
        return False

    def has_delete_permission(
        self,
        request,
        obj=None,
    ):
        return False


@admin.register(CampaignFunding)
class CampaignFundingAdmin(admin.ModelAdmin):

    list_display = (
        "campaign",
        "sponsor",
        "funding_type",
        "amount",
        "status",
        "completed_at",

    )

    list_filter = (
        "funding_type",
        "status",
    )

    search_fields = (
        "campaign__title",
        "sponsor__username",
    )

    readonly_fields = (
        "id",
        "transaction",
        "wallet",
        "amount",
        "funding_type",
        "status",
        "completed_at",

    )


    def has_add_permission(
        self,
        request,
    ):
        return False

    def has_delete_permission(
        self,
        request,
        obj=None,
    ):
        return False
