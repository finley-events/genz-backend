import logging

from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.deriv.models import (
    DerivConnection,
    DerivTradingAccount,
)
from apps.deriv.serializers.otp import OTPSerializer
from apps.deriv.services.otp_service import DerivOTPService

logger = logging.getLogger(__name__)


import logging

from django.shortcuts import get_object_or_404
from django.utils import timezone

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.deriv.models import (
    DerivConnection,
    DerivTradingAccount,
)
from apps.deriv.services.otp_service import DerivOTPService

logger = logging.getLogger(__name__)


class GenerateOTPView(APIView):
    """
    Generate a temporary authenticated WebSocket URL for a
    Deriv trading account.

    The frontend uses the returned URL to establish a direct
    WebSocket connection with Deriv.
    """

    authentication_classes = []
    permission_classes = []

    def post(self, request, account_id):

        logger.info("=" * 80)
        logger.info("OTP request received.")
        logger.info("Requested account: %s", account_id)

        account = get_object_or_404(
            DerivTradingAccount,
            account_id=account_id,
        )

        logger.info("Trading account found.")

        connection = account.connection

        logger.info("Connection ID: %s", connection.id)
        logger.info("Connected: %s", connection.is_connected)

        if not connection.is_connected:
            logger.warning("Connection is not active.")

            return Response(
                {
                    "success": False,
                    "message": "Deriv connection is not active.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if (
            connection.token_expires_at
            and connection.token_expires_at <= timezone.now()
        ):
            logger.warning("OAuth access token has expired.")

            return Response(
                {
                    "success": False,
                    "message": "Deriv access token has expired. Please reconnect.",
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )

        try:
            logger.info("Generating WebSocket OTP...")

            service = DerivOTPService(
                connection.access_token,
            )

            result = service.generate(
                account.account_id,
            )

            logger.info("OTP generated successfully.")
            logger.info("Returning authenticated WebSocket URL.")
            logger.info("=" * 80)

            return Response(
                {
                    "success": True,
                    "message": "WebSocket URL generated successfully.",
                    "data": result,
                },
                status=status.HTTP_200_OK,
            )

        except Exception:
            logger.exception("Failed to generate WebSocket OTP.")

            return Response(
                {
                    "success": False,
                    "message": "Unable to generate WebSocket URL.",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
