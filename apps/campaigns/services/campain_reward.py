from decimal import Decimal

from django.db import transaction as db_transaction
from django.utils import timezone

from apps.transactions.models import Transaction
from apps.transactions.services import TransactionService
from apps.wallets.models import Wallet
from apps.wallets.services import WalletService

from apps.core.system_wallet import get_system_wallet

from ..models import (
    CampaignReward,
    CampaignParticipation,
)
from .funding_service import CampaignFundingService


class CampaignRewardService:
    """
    Handles campaign reward lifecycle.

    Financial flow:

        System Wallet
              ↓ debit

        User Wallet
              ↑ credit

        Transaction
              ↓

        Ledger Entries
              ↓

        Wallet Balance Refresh
    """

    @staticmethod
    def calculate_reward(
        participation: CampaignParticipation,
    ) -> Decimal:
        """
        Calculate reward amount.

        Current implementation:
        Use campaign reward_per_action.

        Future:
        - task-based rewards
        - bonus rewards
        - referral multipliers
        """

        return participation.reward_amount

    @classmethod
    @db_transaction.atomic
    def create_reward(
        cls,
        *,
        participation: CampaignParticipation,
    ) -> CampaignReward:
        """
        Create pending reward record.
        """

        if participation.status != CampaignParticipation.Status.VERIFIED:
            raise ValueError("Participation must be verified.")

        existing_reward = CampaignReward.objects.filter(
            participation=participation
        ).first()

        if existing_reward:
            return existing_reward

        user_wallet = Wallet.objects.get(user=participation.user)

        amount = cls.calculate_reward(participation)

        reward = CampaignReward.objects.create(
            participation=participation,
            wallet=user_wallet,
            amount=amount,
            status=CampaignReward.Status.PENDING,
        )

        participation.reward_amount = amount

        participation.save(
            update_fields=[
                "reward_amount",
            ]
        )

        return reward

    @classmethod
    @db_transaction.atomic
    def pay_reward(
        cls,
        *,
        reward: CampaignReward,
    ) -> CampaignReward:
        """
        Execute reward payout.

        System Wallet -> DEBIT
        User Wallet   -> CREDIT
        """

        if reward.status != CampaignReward.Status.PENDING:
            raise ValueError("Reward is not pending.")

        participation = reward.participation

        campaign = participation.campaign

        CampaignFundingService.refresh_budget(campaign)

        if campaign.remaining_budget < reward.amount:
            raise ValueError("Insufficient campaign budget.")

        system_wallet = get_system_wallet()

        transaction = TransactionService.create(
            initiated_by=participation.user,
            transaction_type=(Transaction.TransactionType.CAMPAIGN_REWARD),
            amount=reward.amount,
            description=(f"Campaign reward: " f"{campaign.title}"),
        )

        TransactionService.complete(
            transaction=transaction,
            debit_wallet=system_wallet,
            credit_wallet=reward.wallet,
        )

        WalletService.refresh_balance(system_wallet)

        WalletService.refresh_balance(reward.wallet)

        CampaignReward.objects.filter(
            pk=reward.pk,
        ).update(
            transaction=transaction,
            status=CampaignReward.Status.PAID,
            paid_at=timezone.now(),
        )

        reward.refresh_from_db()

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

        CampaignFundingService.refresh_budget(campaign)

        return reward

    @classmethod
    @db_transaction.atomic
    def reverse_reward(
        cls,
        *,
        reward: CampaignReward,
    ) -> CampaignReward:
        """
        Reverse a paid reward.
        """

        if reward.status != CampaignReward.Status.PAID:
            raise ValueError("Only paid rewards can be reversed.")

        if reward.transaction is None:
            raise ValueError("Reward transaction missing.")

        TransactionService.reverse(reward.transaction)

        WalletService.refresh_balance(reward.wallet)

        WalletService.refresh_balance(get_system_wallet())

        reward.status = CampaignReward.Status.FAILED

        reward.save(
            update_fields=[
                "status",
            ]
        )

        participation = reward.participation

        participation.status = CampaignParticipation.Status.VERIFIED

        participation.reward_paid = False

        participation.save(
            update_fields=[
                "status",
                "reward_paid",
            ]
        )

        CampaignFundingService.refresh_budget(participation.campaign)

        return reward
