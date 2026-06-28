# apps/transactions/services.py

import uuid

from django.db import transaction as db_transaction
from django.utils import timezone

from .models import LedgerEntry, Transaction


class TransactionService:
    """
    Service layer for transaction lifecycle management.
    """

    @staticmethod
    def generate_reference() -> str:
        """
        Generate a unique transaction reference.
        Example: TXN-7B9A4F2C8D1E
        """
        return f"TXN-{uuid.uuid4().hex[:12].upper()}"

    @classmethod
    @db_transaction.atomic
    def create(
        cls,
        *,
        initiated_by,
        transaction_type: str,
        amount,
        description: str = "",
        currency: str = "Z",
    ) -> Transaction:
        """
        Create a new pending transaction.
        """

        return Transaction.objects.create(
            reference=cls.generate_reference(),
            transaction_type=transaction_type,
            status=Transaction.Status.PENDING,
            amount=amount,
            currency=currency,
            description=description,
            initiated_by=initiated_by,
        )

    @staticmethod
    @db_transaction.atomic
    def complete(
        *,
        transaction: Transaction,
        debit_wallet,
        credit_wallet,
    ) -> Transaction:
        """
        Complete a transaction by creating balanced ledger entries.
        """

        if transaction.status != Transaction.Status.PENDING:
            raise ValueError("Only pending transactions can be completed.")

        LedgerEntry.objects.create(
            transaction=transaction,
            wallet=debit_wallet,
            entry_type=LedgerEntry.EntryType.DEBIT,
            amount=transaction.amount,
        )

        LedgerEntry.objects.create(
            transaction=transaction,
            wallet=credit_wallet,
            entry_type=LedgerEntry.EntryType.CREDIT,
            amount=transaction.amount,
        )

        transaction.status = Transaction.Status.COMPLETED
        transaction.completed_at = timezone.now()
        transaction.save(update_fields=["status", "completed_at"])

        return transaction

    @staticmethod
    @db_transaction.atomic
    def fail(
        transaction: Transaction,
    ) -> Transaction:
        """
        Mark a transaction as failed.
        """

        if transaction.status != Transaction.Status.PENDING:
            raise ValueError("Only pending transactions can be failed.")

        transaction.status = Transaction.Status.FAILED
        transaction.save(update_fields=["status"])

        return transaction

    @staticmethod
    @db_transaction.atomic
    def reverse(
        transaction: Transaction,
    ) -> Transaction:
        """
        Reverse a completed transaction by creating
        compensating ledger entries.
        """

        if transaction.status != Transaction.Status.COMPLETED:
            raise ValueError("Only completed transactions can be reversed.")

        entries = LedgerEntry.objects.filter(transaction=transaction)

        for entry in entries:
            LedgerEntry.objects.create(
                transaction=transaction,
                wallet=entry.wallet,
                entry_type=(
                    LedgerEntry.EntryType.CREDIT
                    if entry.entry_type == LedgerEntry.EntryType.DEBIT
                    else LedgerEntry.EntryType.DEBIT
                ),
                amount=entry.amount,
            )

        transaction.status = Transaction.Status.REVERSED
        transaction.save(update_fields=["status"])

        return transaction
