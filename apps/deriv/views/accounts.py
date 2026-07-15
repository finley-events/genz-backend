import logging

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.deriv.models import (
    DerivConnection,
    DerivTradingAccount,
)
from apps.deriv.serializers.account import (
    DerivTradingAccountSerializer,
)

logger = logging.getLogger(__name__)


class AccountsView(APIView):
    """
    Returns every trading account belonging to the
    current active Deriv connection.
    """

    authentication_classes = []
    permission_classes = []

    def get(self, request):
        logger.info("=" * 80)
        logger.info("Fetching trading accounts.")

        connection = (
            DerivConnection.objects.filter(
                is_connected=True,
            )
            .order_by("-created_at")
            .first()
        )

        if connection is None:
            return Response(
                {
                    "success": True,
                    "data": [],
                },
                status=status.HTTP_200_OK,
            )

        accounts = DerivTradingAccount.objects.filter(connection=connection).order_by(
            "account_type", "account_id"
        )

        serializer = DerivTradingAccountSerializer(
            accounts,
            many=True,
        )

        logger.info(
            "%s trading account(s) returned.",
            accounts.count(),
        )

        return Response(
            {
                "success": True,
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )
