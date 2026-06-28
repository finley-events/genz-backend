# apps/wallets/services.py

from decimal import Decimal

from django.db import transaction as db_transaction
from django.db.models import Sum

from apps.transactions.models import LedgerEntry

from .models import Wallet, WalletBalance


class WalletService:
    """
    Service layer for wallet operations.

    The transaction ledger is the source of truth.
    WalletBalance is only a cached representation.
    """

    @staticmethod
    def get_balance(wallet: Wallet) -> WalletBalance:
        """
        Return the cached balance object.
        """
        balance, _ = WalletBalance.objects.get_or_create(
            wallet=wallet,
            defaults={
                "available_balance": Decimal("0"),
                "locked_balance": Decimal("0"),
            },
        )
        return balance

    @staticmethod
    @db_transaction.atomic
    def refresh_balance(wallet: Wallet) -> WalletBalance:
        """
        Recalculate available balance from ledger entries.
        """

        total_credits = LedgerEntry.objects.filter(
            wallet=wallet,
            entry_type=LedgerEntry.EntryType.CREDIT,
        ).aggregate(total=Sum("amount"))["total"] or Decimal("0")

        total_debits = LedgerEntry.objects.filter(
            wallet=wallet,
            entry_type=LedgerEntry.EntryType.DEBIT,
        ).aggregate(total=Sum("amount"))["total"] or Decimal("0")

        balance = WalletService.get_balance(wallet)

        balance.available_balance = total_credits - total_debits
        balance.save(update_fields=["available_balance", "updated_at"])

        return balance

    @staticmethod
    @db_transaction.atomic
    def lock(wallet: Wallet, amount: Decimal) -> WalletBalance:
        """
        Move funds from available balance to locked balance.
        """

        balance = WalletService.get_balance(wallet)

        if balance.available_balance < amount:
            raise ValueError("Insufficient available balance.")

        balance.available_balance -= amount
        balance.locked_balance += amount
        balance.save(
            update_fields=[
                "available_balance",
                "locked_balance",
                "updated_at",
            ]
        )

        return balance

    @staticmethod
    @db_transaction.atomic
    def unlock(wallet: Wallet, amount: Decimal) -> WalletBalance:
        """
        Release locked funds back to available balance.

        """

        balance = WalletService.get_balance(wallet)

        if balance.locked_balance < amount:
            raise ValueError("Insufficient locked balance.")

        balance.locked_balance -= amount
        balance.available_balance += amount
        balance.save(
            update_fields=[
                "available_balance",
                "locked_balance",
                "updated_at",
            ]
        )

        return balance

    @staticmethod
    @db_transaction.atomic
    def consume_locked(wallet: Wallet, amount: Decimal) -> WalletBalance:
        """
        Permanently remove locked funds after a successful withdrawal.

        Used when a withdrawal has already been processed by the payment provider.
        """

        balance = WalletService.get_balance(wallet)

        if balance.locked_balance < amount:
            raise ValueError("Insufficient locked balance.")

        balance.locked_balance -= amount

        balance.save(
            update_fields=[
                "locked_balance",
                "updated_at",
            ]
        )

        return balance
