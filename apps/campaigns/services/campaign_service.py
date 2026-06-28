# apps/campaigns/services.py

from django.db import transaction as db_transaction
from django.utils import timezone

from ..models import Campaign


class CampaignService:

    @staticmethod
    def _validate_owner(campaign, user):
        """
        Ensure the requesting user owns the campaign.
        """

        if campaign.sponsor != user:
            raise PermissionError("You do not have permission to manage this campaign.")

    @staticmethod
    def _validate_editable(campaign):
        """
        Only draft campaigns can be edited.
        """

        if campaign.status != Campaign.Status.DRAFT:
            raise ValueError("Only draft campaigns can be modified.")

    @staticmethod
    def _validate_publishable(campaign):
        """
        Validate campaign before activation.
        """

        if campaign.status != Campaign.Status.DRAFT:
            raise ValueError("Only draft campaigns can be published.")

        if campaign.start_date >= campaign.end_date:
            raise ValueError("End date must be after start date.")

        if campaign.reward_per_action <= 0:
            raise ValueError("Reward per action must be greater than zero.")

        if campaign.remaining_budget <= 0:
            raise ValueError("Campaign must be funded before activation.")

    @classmethod
    @db_transaction.atomic
    def create_campaign(cls, *, sponsor, **data):
        """
        Create a new draft campaign.
        """

        campaign = Campaign.objects.create(
            sponsor=sponsor,
            **data,
        )

        return campaign

    @classmethod
    @db_transaction.atomic
    def update_campaign(
        cls,
        *,
        campaign,
        user,
        **data,
    ):
        """
        Update campaign details.

        Only draft campaigns can be edited.
        """

        cls._validate_owner(campaign, user)
        cls._validate_editable(campaign)

        for field, value in data.items():
            setattr(campaign, field, value)

        campaign.save()

        return campaign

    @classmethod
    @db_transaction.atomic
    def publish_campaign(cls, *, campaign, user):
        """
        Move campaign from DRAFT -> ACTIVE.
        """

        cls._validate_owner(campaign, user)
        cls._validate_publishable(campaign)

        campaign.status = Campaign.Status.ACTIVE

        campaign.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

        return campaign

    @classmethod
    @db_transaction.atomic
    def pause_campaign(cls, *, campaign, user):
        """
        Move campaign from ACTIVE -> PAUSED.
        """

        cls._validate_owner(campaign, user)

        if campaign.status != Campaign.Status.ACTIVE:
            raise ValueError("Only active campaigns can be paused.")

        campaign.status = Campaign.Status.PAUSED

        campaign.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

        return campaign

    @classmethod
    @db_transaction.atomic
    def resume_campaign(cls, *, campaign, user):
        """
        Move campaign from PAUSED -> ACTIVE.
        """

        cls._validate_owner(campaign, user)

        if campaign.status != Campaign.Status.PAUSED:
            raise ValueError("Only paused campaigns can be resumed.")

        campaign.status = Campaign.Status.ACTIVE

        campaign.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

        return campaign

    @classmethod
    @db_transaction.atomic
    def cancel_campaign(cls, *, campaign, user):
        """
        Cancel a campaign.
        """

        cls._validate_owner(campaign, user)

        if campaign.status in (
            Campaign.Status.COMPLETED,
            Campaign.Status.CANCELLED,
        ):
            raise ValueError("Campaign is already closed.")

        campaign.status = Campaign.Status.CANCELLED

        campaign.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

        return campaign

    @classmethod
    @db_transaction.atomic
    def complete_campaign(cls, *, campaign):
        """
        Mark campaign as completed.

        Can be triggered automatically when:
        - budget exhausted
        - end date reached
        - manually by sponsor/admin
        """

        if campaign.status not in (
            Campaign.Status.ACTIVE,
            Campaign.Status.PAUSED,
        ):
            raise ValueError("Only active or paused campaigns can be completed.")

        campaign.status = Campaign.Status.COMPLETED

        campaign.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

        return campaign

    @staticmethod
    def is_active(campaign):
        """
        Check whether a campaign is currently active.
        """

        now = timezone.now()

        return (
            campaign.status == Campaign.Status.ACTIVE
            and campaign.start_date <= now <= campaign.end_date
        )
