from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import MpesaTransaction, MpesaWebhookLog
from .serializers import (
    DepositSerializer,
    WithdrawalSerializer,
    MpesaTransactionSerializer,
)
from .services import MpesaService


class DepositView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = DepositSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        payment = MpesaService.initiate_deposit(
            user=request.user,
            phone_number=serializer.validated_data["phone_number"],  # type: ignore
            amount_kes=serializer.validated_data["amount"],  # type: ignore
        )

        return Response(
            {
                "reference": payment.reference,
                "status": payment.status,
                "message": "STK Push initiated",
            },
            status=status.HTTP_201_CREATED,
        )


class WithdrawalView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = WithdrawalSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        payment = MpesaService.initiate_withdrawal(
            user=request.user,
            phone_number=serializer.validated_data["phone_number"],  # type: ignore
            amount_coins=serializer.validated_data["amount"],  # type: ignore
        )

        return Response(
            {
                "reference": payment.reference,
                "status": payment.status,
                "message": "Withdrawal initiated",
            },
            status=status.HTTP_201_CREATED,
        )


class PaymentHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        payments = MpesaTransaction.objects.filter(user=request.user).order_by(
            "-created_at"
        )

        serializer = MpesaTransactionSerializer(
            payments,
            many=True,
        )

        return Response(serializer.data)


class PaymentDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, reference):
        payment = get_object_or_404(
            MpesaTransaction,
            user=request.user,
            reference=reference,
        )

        serializer = MpesaTransactionSerializer(payment)

        return Response(serializer.data)


class PayHeroWebhookView(APIView):
    """
    Receives callbacks from PayHero.
    """

    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):

        callback_data = request.data

        log = MpesaWebhookLog.objects.create(
            payload=callback_data,
        )

        try:

            external_reference = callback_data.get(
                "external_reference"
            ) or callback_data.get("ExternalReference")

            if not external_reference:

                log.processing_error = "Missing external reference"

                log.save(update_fields=["processing_error"])

                return Response(
                    {"detail": "Reference missing"},
                    status=400,
                )

            payment = MpesaTransaction.objects.get(
                external_reference=external_reference
            )

            log.mpesa_transaction = payment  # type: ignore

            status_value = (
                callback_data.get("status") or callback_data.get("Status") or ""
            ).lower()

            transaction_type = payment.transaction_type

            if status_value in [
                "success",
                "successful",
                "completed",
            ]:

                if transaction_type == MpesaTransaction.TransactionType.DEPOSIT:

                    MpesaService.complete_deposit(
                        payment=payment,
                        callback_data=callback_data,
                    )

                else:

                    MpesaService.complete_withdrawal(
                        payment=payment,
                        callback_data=callback_data,
                    )

            else:

                MpesaService.fail_payment(
                    payment=payment,
                    callback_data=callback_data,
                    reason="Payment failed",
                )

            log.processed = True
            log.save(
                update_fields=[
                    "processed",
                    "mpesa_transaction",
                ]
            )

            return Response({"detail": "OK"})

        except Exception as exc:

            log.processing_error = str(exc)

            log.save(update_fields=["processing_error"])

            return Response(
                {"detail": str(exc)},
                status=500,
            )
