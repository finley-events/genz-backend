import logging
from django.utils import timezone

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.deriv.models import DerivConnection
from apps.deriv.serializers.connection import DerivConnectionSerializer

logger = logging.getLogger(__name__)


class ConnectionView(APIView):
    """
    Returns the current Deriv connection state.
    """

    authentication_classes = []
    permission_classes = []

    def get(self, request):

        logger.info("=" * 80)
        logger.info("Checking Deriv connection.")

        connection = (
            DerivConnection.objects.filter(
                is_connected=True,
                token_expires_at__gt=timezone.now(),
            )
            .order_by("-created_at")
            .first()
        )

        if connection is None:

            logger.info("No active Deriv connection found.")

            return Response(
                {
                    "success": True,
                    "connected": False,
                    "connection": None,
                },
                status=status.HTTP_200_OK,
            )

        serializer = DerivConnectionSerializer(connection)

        logger.info(
            "Active connection found: %s",
            connection.id,
        )

        return Response(
            {
                "success": True,
                "connected": True,
                "connection": serializer.data,
            },
            status=status.HTTP_200_OK,
        )
