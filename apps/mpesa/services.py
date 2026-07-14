import base64
import uuid

from decimal import Decimal

import requests

from typing import cast
from apps.transactions.models import Transaction

from typing import Optional

from django.conf import settings
from django.db import transaction as db_transaction
from django.utils import timezone

from apps.transactions.models import Transaction
from apps.transactions.services import TransactionService

from apps.wallets.services import WalletService
from apps.wallets.system_wallets import SystemWalletService

from .models import MpesaTransaction


class MpesaService:

    @staticmethod
    def generate_reference(prefix: str) -> str:
        return f"{prefix}-{uuid.uuid4().hex[:12].upper()}"

    @staticmethod
    def get_auth_header():
        credentials = f"{settings.PAYHERO_API_KEY}:" f"{settings.PAYHERO_API_SECRET}"

        encoded = base64.b64encode(credentials.encode()).decode()

        return {
            "Authorization": f"Basic {encoded}",
            "Content-Type": "application/json",
        }

    @classmethod
    @db_transaction.atomic
    def initiate_deposit(
        cls,
        *,
        user,
        phone_number: str,
        amount_kes: Decimal,
    ):
        """
        Send STK Push request.
        """

        reference = cls.generate_reference("DEP")

        coin_amount = Decimal(amount_kes) / settings.GENZ_COIN_RATE

        payment = MpesaTransaction.objects.create(
            user=user,
            reference=reference,
            external_reference=reference,
            phone_number=phone_number,
            amount_kes=amount_kes,
            coin_amount=coin_amount,
            transaction_type=(MpesaTransaction.TransactionType.DEPOSIT),
            status=MpesaTransaction.Status.PENDING,
        )

        payload = {
            "amount": int(amount_kes),
            "phone_number": phone_number,
            "channel_id": settings.PAYHERO_CHANNEL_ID,
            "provider": "m-pesa",
            "network_code": "63902",
            "external_reference": reference,
            "customer_name": user.username,
            "callback_url": (settings.PAYHERO_DEPOSIT_CALLBACK_URL),
        }

        payment.raw_request = payload
        payment.save(update_fields=["raw_request"])

        try:

            response = requests.post(
                f"{settings.PAYHERO_BASE_URL}/payments",
                json=payload,
                headers=cls.get_auth_header(),
                timeout=30,
            )

            data = response.json()

            payment.raw_response = data

            if response.ok:
                payment.status = MpesaTransaction.Status.PROCESSING
            else:
                payment.status = MpesaTransaction.Status.FAILED

            payment.save(
                update_fields=[
                    "status",
                    "raw_response",
                    "updated_at",
                ]
            )

            return payment

        except Exception as exc:

            payment.status = MpesaTransaction.Status.FAILED

            payment.failure_reason = str(exc)

            payment.save(
                update_fields=[
                    "status",
                    "failure_reason",
                    "updated_at",
                ]
            )

            raise

    @classmethod
    @db_transaction.atomic
    def initiate_withdrawal(
        cls,
        *,
        user,
        phone_number: str,
        amount_coins: Decimal,
    ):
        """
        Lock funds and submit B2C request.
        """

        wallet = user.wallet

        WalletService.lock(
            wallet=wallet,
            amount=amount_coins,
        )

        amount_kes = Decimal(amount_coins) * settings.GENZ_COIN_RATE

        reference = cls.generate_reference("WTH")

        payment = MpesaTransaction.objects.create(
            user=user,
            reference=reference,
            external_reference=reference,
            phone_number=phone_number,
            amount_kes=amount_kes,
            coin_amount=amount_coins,
            transaction_type=(MpesaTransaction.TransactionType.WITHDRAWAL),
            status=MpesaTransaction.Status.PENDING,
        )

        payload = {
            "external_reference": reference,
            "amount": float(amount_kes),
            "phone_number": phone_number,

            "callback_url": "https://webhook.site/f14867a1-64e1-499f-a6b4-a261124667fb",

            "channel_id": settings.PAYHERO_CHANNEL_ID,

        }

        payment.raw_request = payload
        payment.save(update_fields=["raw_request"])

        try:

            response = requests.post(
                f"{settings.PAYHERO_BASE_URL}/withdraw",
                json=payload,
                headers=cls.get_auth_header(),
                timeout=30,
            )

            data = response.json()

            payment.raw_response = data

            if response.ok:
                payment.status = MpesaTransaction.Status.PROCESSING
            else:

                WalletService.unlock(
                    wallet=wallet,
                    amount=amount_coins,
                )

                payment.status = MpesaTransaction.Status.FAILED

            payment.save(
                update_fields=[
                    "status",
                    "raw_response",
                    "updated_at",
                ]
            )

            return payment

        except Exception as exc:

            WalletService.unlock(
                wallet=wallet,
                amount=amount_coins,
            )

            payment.status = MpesaTransaction.Status.FAILED

            payment.failure_reason = str(exc)

            payment.save(
                update_fields=[
                    "status",
                    "failure_reason",
                    "updated_at",
                ]
            )

            raise

    @classmethod
    @db_transaction.atomic
    def complete_deposit(
        cls,
        *,
        payment: MpesaTransaction,
        callback_data: dict,
    ):
        """
        Finalize successful deposit.
        """

        if payment.status == MpesaTransaction.Status.COMPLETED:
            return payment

        mpesa_wallet = SystemWalletService.get_mpesa_wallet()

        txn = TransactionService.create(
            initiated_by=payment.user,
            transaction_type=(Transaction.TransactionType.DEPOSIT),
            amount=payment.coin_amount,
            description="M-Pesa Deposit",
        )

        TransactionService.complete(
            transaction=txn,
            debit_wallet=mpesa_wallet,
            credit_wallet=payment.user.wallet,
        )

        WalletService.refresh_balance(payment.user.wallet)
        payment.transaction = cast(Transaction, txn)  # type: ignore

        payment.raw_callback = callback_data
        payment.status = MpesaTransaction.Status.COMPLETED
        payment.completed_at = timezone.now()

        payment.save()

        return payment

    @classmethod
    @db_transaction.atomic
    def complete_withdrawal(
        cls,
        *,
        payment: MpesaTransaction,
        callback_data: dict,
    ):
        """
        Finalize successful withdrawal.
        """

        if payment.status == MpesaTransaction.Status.COMPLETED:
            return payment

        mpesa_wallet = SystemWalletService.get_mpesa_wallet()

        txn = TransactionService.create(
            initiated_by=payment.user,
            transaction_type=(Transaction.TransactionType.WITHDRAWAL),
            amount=payment.coin_amount,
            description="M-Pesa Withdrawal",
        )

        TransactionService.complete(
            transaction=txn,
            debit_wallet=payment.user.wallet,
            credit_wallet=mpesa_wallet,
        )

        WalletService.consume_locked(
            wallet=payment.user.wallet,
            amount=payment.coin_amount,
        )

        WalletService.refresh_balance(payment.user.wallet)

        payment.transaction = txn  # type: ignore
        payment.raw_callback = callback_data
        payment.status = MpesaTransaction.Status.COMPLETED
        payment.completed_at = timezone.now()

        payment.save()

        return payment

    @classmethod
    @db_transaction.atomic
    def fail_payment(
        cls,
        *,
        payment: MpesaTransaction,
        callback_data: Optional[dict] = None,
        reason: str = "",
    ):
        """
        Mark payment failed.
        """

        if payment.transaction_type == MpesaTransaction.TransactionType.WITHDRAWAL:
            WalletService.unlock(
                wallet=payment.user.wallet,
                amount=payment.coin_amount,
            )

        payment.status = MpesaTransaction.Status.FAILED

        payment.failure_reason = reason

        if callback_data:
            payment.raw_callback = callback_data

        payment.save()

        return payment
