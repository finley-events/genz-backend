from decimal import Decimal

from django.db import transaction as db_transaction
from django.utils import timezone

from apps.transactions.models import Transaction
from apps.transactions.services import TransactionService
from apps.wallets.services import WalletService

from django.db.models import Sum
from ..models import CampaignReward


from ..models import Campaign, CampaignFunding
from apps.core.system_wallet import (
    get_system_wallet,
)


class CampaignFundingService:

    @staticmethod
    def refresh_budget(campaign: Campaign) -> Campaign:

        total_funding = Decimal("0")
        total_refunds = Decimal("0")

        funding_events = CampaignFunding.objects.filter(
            campaign=campaign,
            status=CampaignFunding.Status.COMPLETED,
        )

        for event in funding_events:

            if event.funding_type in (
                CampaignFunding.FundingType.INITIAL,
                CampaignFunding.FundingType.TOP_UP,
                CampaignFunding.FundingType.ADJUSTMENT,
            ):
                total_funding += event.amount

            elif event.funding_type == CampaignFunding.FundingType.REFUND:
                total_refunds += event.amount

        from ..models import CampaignParticipation

        paid_rewards = Decimal("0")

        paid_rewards = CampaignReward.objects.filter(
            participation__campaign=campaign,
            status=CampaignReward.Status.PAID,
        ).aggregate(total=Sum("amount"))["total"] or Decimal("0")

        budget = total_funding - total_refunds
        remaining_budget = budget - paid_rewards

        campaign.budget = budget
        campaign.remaining_budget = remaining_budget

        campaign.save(
            update_fields=[
                "budget",
                "remaining_budget",
            ]
        )

        return campaign

    @classmethod
    @db_transaction.atomic
    def fund_campaign(
        cls,
        *,
        campaign: Campaign,
        sponsor,
        amount: Decimal,
        notes: str = "",
    ) -> CampaignFunding:
        """
        Initial campaign funding.

        Sponsor Wallet
            DEBIT

        System Wallet
            CREDIT
        """

        if amount <= 0:
            raise ValueError("Funding amount must be greater than zero.")

        sponsor_wallet = sponsor.wallet

        WalletService.refresh_balance(sponsor_wallet)

        balance = WalletService.get_balance(sponsor_wallet)

        if balance.available_balance < amount:
            raise ValueError("Insufficient wallet balance.")

        system_wallet = get_system_wallet()

        transaction = TransactionService.create(
            initiated_by=sponsor,
            transaction_type=Transaction.TransactionType.TRANSFER,
            amount=amount,
            description=(f"Campaign funding: " f"{campaign.title}"),
        )

        TransactionService.complete(
            transaction=transaction,
            debit_wallet=sponsor_wallet,
            credit_wallet=system_wallet,
        )

        WalletService.refresh_balance(sponsor_wallet)

        WalletService.refresh_balance(system_wallet)

        funding = CampaignFunding.objects.create(
            campaign=campaign,
            sponsor=sponsor,
            transaction=transaction,
            wallet=sponsor_wallet,
            funding_type=CampaignFunding.FundingType.INITIAL,
            amount=amount,
            notes=notes,
            status=CampaignFunding.Status.COMPLETED,
            completed_at=timezone.now(),
        )

        cls.refresh_budget(campaign)

        return funding

    @classmethod
    @db_transaction.atomic
    def top_up_campaign(
        cls,
        *,
        campaign,
        sponsor,
        amount,
        notes="",
    ):
        """
        Add more funds to an existing campaign.
        """

        funding = cls.fund_campaign(
            campaign=campaign,
            sponsor=sponsor,
            amount=amount,
            notes=notes,
        )

        funding.funding_type = CampaignFunding.FundingType.TOP_UP

        funding.save(
            update_fields=[
                "funding_type",
            ]
        )

        return funding

    @classmethod
    @db_transaction.atomic
    def refund_campaign(
        cls,
        *,
        campaign,
        sponsor,
        amount,
        notes="",
    ):
        """
        Refund unused campaign funds.

        System Wallet
            DEBIT

        Sponsor Wallet
            CREDIT
        """

        cls.refresh_budget(campaign)

        if campaign.remaining_budget < amount:
            raise ValueError("Insufficient campaign balance.")

        sponsor_wallet = sponsor.wallet

        system_wallet = get_system_wallet()

        transaction = TransactionService.create(
            initiated_by=sponsor,
            transaction_type=Transaction.TransactionType.REFUND,
            amount=amount,
            description=(f"Campaign refund: " f"{campaign.title}"),
        )

        TransactionService.complete(
            transaction=transaction,
            debit_wallet=system_wallet,
            credit_wallet=sponsor_wallet,
        )

        WalletService.refresh_balance(sponsor_wallet)

        WalletService.refresh_balance(system_wallet)

        funding = CampaignFunding.objects.create(
            campaign=campaign,
            sponsor=sponsor,
            transaction=transaction,
            wallet=sponsor_wallet,
            funding_type=CampaignFunding.FundingType.REFUND,
            amount=amount,
            status=CampaignFunding.Status.COMPLETED,
            notes=notes,
            completed_at=timezone.now(),
        )

        cls.refresh_budget(campaign)

        return funding
