# apps/referrals/services.py

from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from apps.users.models import Profile, User

from .models import Referral, ReferralReward


class ReferralService:
    """
    Business logic for the referral system.
    """

    DEFAULT_REWARD = Decimal("100.00")

    @staticmethod
    @transaction.atomic
    def create_referral(
        *,
        referred_user: User,
        referral_code: str,
    ) -> Referral:
        """
        Create a referral relationship using a referral code.
        """

        if Referral.objects.filter(referred_user=referred_user).exists():
            raise ValueError("User has already been referred.")

        try:
            referrer_profile = Profile.objects.select_related("user").get(
                referral_code=referral_code
            )
        except Profile.DoesNotExist as exc:
            raise ValueError("Invalid referral code.") from exc

        referrer = referrer_profile.user

        if referrer.id == referred_user.id:
            raise ValueError("Users cannot refer themselves.")

        referral = Referral.objects.create(
            referrer=referrer,
            referred_user=referred_user,
            referral_code_used=referral_code,
            reward_amount=ReferralService.DEFAULT_REWARD,
            status=Referral.Status.PENDING,
        )

        return referral

    @staticmethod
    @transaction.atomic
    def qualify_referral(referral: Referral) -> Referral:
        """
        Mark a referral as qualified.
        """

        if referral.status != Referral.Status.PENDING:
            raise ValueError("Referral is not pending.")

        referral.status = Referral.Status.QUALIFIED
        referral.qualified_at = timezone.now()

        referral.save(
            update_fields=[
                "status",
                "qualified_at",
            ]
        )

        return referral

    @staticmethod
    @transaction.atomic
    def reward_referral(referral: Referral) -> ReferralReward:
        """
        Mark a referral as rewarded.

        Actual wallet credits and ledger entries should be
        delegated to the transactions/wallet services.
        """

        if referral.status == Referral.Status.REWARDED:
            raise ValueError("Referral has already been rewarded.")

        if referral.status != Referral.Status.QUALIFIED:
            raise ValueError("Referral must be qualified before rewarding.")

        reward, _ = ReferralReward.objects.get_or_create(
            referral=referral,
            defaults={
                "amount": referral.reward_amount,
                "status": ReferralReward.Status.PENDING,
            },
        )

        # TODO:
        # Create a Transaction using TransactionService.
        # Credit the referrer's wallet.
        # Store the transaction on reward.transaction.

        reward.status = ReferralReward.Status.COMPLETED
        reward.save(update_fields=["status"])

        referral.status = Referral.Status.REWARDED
        referral.rewarded_at = timezone.now()
        referral.save(
            update_fields=[
                "status",
                "rewarded_at",
            ]
        )

        return reward

    @staticmethod
    @transaction.atomic
    def cancel_referral(referral: Referral) -> Referral:
        """
        Cancel a referral.
        """

        referral.status = Referral.Status.CANCELLED
        referral.save(update_fields=["status"])

        return referral
