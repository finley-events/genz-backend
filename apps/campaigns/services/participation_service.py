# apps/campaigns/services/participation_service.py

from django.db import transaction as db_transaction
from django.utils import timezone

from ..models import (
    Campaign,
    CampaignParticipation,
    CampaignSubmission,
    CampaignTask,
)


class ParticipationService:
    """
    Handles campaign participation lifecycle.

    ```
    No financial logic belongs here.
    Rewards are handled by CampaignRewardService.
    """

    @classmethod
    @db_transaction.atomic
    def join_campaign(
        cls,
        *,
        campaign: Campaign,
        user,
    ) -> CampaignParticipation:
        """
        Join an active campaign.
        """

        if campaign.status != Campaign.Status.ACTIVE:
            raise ValueError("Only active campaigns can be joined.")

        now = timezone.now()

        if now < campaign.start_date:
            raise ValueError("Campaign has not started.")

        if now > campaign.end_date:
            raise ValueError("Campaign has ended.")

        exists = CampaignParticipation.objects.filter(
            campaign=campaign,
            user=user,
        ).exists()

        if exists:
            raise ValueError("User has already joined this campaign.")

        if (
            campaign.max_participants > 0
            and campaign.current_participants >= campaign.max_participants
        ):
            raise ValueError("Campaign participant limit reached.")

        participation = CampaignParticipation.objects.create(
            campaign=campaign,
            user=user,
            status=CampaignParticipation.Status.JOINED,
        )

        campaign.current_participants += 1

        campaign.save(
            update_fields=[
                "current_participants",
            ]
        )

        return participation

    @classmethod
    @db_transaction.atomic
    def submit_task(
        cls,
        *,
        participation: CampaignParticipation,
        task: CampaignTask,
        proof_url: str | None = None,
        proof_image=None,
        notes: str = "",
    ) -> CampaignSubmission:
        """
        Submit proof for a task.
        """

        if participation.status == (CampaignParticipation.Status.REWARDED):
            raise ValueError("Participation already rewarded.")

        if task.campaign != participation.campaign:
            raise ValueError("Task does not belong to campaign.")

        exists = CampaignSubmission.objects.filter(
            participation=participation,
            task=task,
        ).exists()

        if exists:
            raise ValueError("Task already submitted.")

        submission = CampaignSubmission.objects.create(
            participation=participation,
            task=task,
            proof_url=proof_url,
            proof_image=proof_image,
            notes=notes,
            status=CampaignSubmission.Status.PENDING,
        )

        participation.status = CampaignParticipation.Status.SUBMITTED

        participation.save(
            update_fields=[
                "status",
            ]
        )

        return submission

    @classmethod
    @db_transaction.atomic
    def verify_submission(
        cls,
        *,
        submission: CampaignSubmission,
        verified_by,
    ) -> CampaignSubmission:
        """
        Approve a submission.
        """

        if submission.status != CampaignSubmission.Status.PENDING:
            raise ValueError("Only pending submissions can be approved.")

        submission.status = CampaignSubmission.Status.APPROVED

        submission.verified_by = verified_by
        submission.verified_at = timezone.now()

        submission.save(
            update_fields=[
                "status",
                "verified_by",
                "verified_at",
            ]
        )

        participation = submission.participation

        participation.status = CampaignParticipation.Status.VERIFIED

        participation.save(
            update_fields=[
                "status",
            ]
        )

        return submission

    @classmethod
    @db_transaction.atomic
    def reject_submission(
        cls,
        *,
        submission: CampaignSubmission,
        verified_by,
    ) -> CampaignSubmission:
        """
        Reject a submission.
        """

        if submission.status != CampaignSubmission.Status.PENDING:
            raise ValueError("Only pending submissions can be rejected.")

        submission.status = CampaignSubmission.Status.REJECTED

        submission.verified_by = verified_by
        submission.verified_at = timezone.now()

        submission.save(
            update_fields=[
                "status",
                "verified_by",
                "verified_at",
            ]
        )

        participation = submission.participation

        participation.status = CampaignParticipation.Status.REJECTED

        participation.save(
            update_fields=[
                "status",
            ]
        )

        return submission

    @classmethod
    @db_transaction.atomic
    def complete_participation(
        cls,
        *,
        participation: CampaignParticipation,
    ) -> CampaignParticipation:
        """
        Called after reward payout succeeds.
        """

        if participation.status != CampaignParticipation.Status.VERIFIED:
            raise ValueError("Participation must be verified first.")

        participation.status = CampaignParticipation.Status.REWARDED

        participation.reward_paid = True
        participation.completed_at = timezone.now()

        participation.save(
            update_fields=[
                "status",
                "reward_paid",
                "completed_at",
            ]
        )

        return participation
