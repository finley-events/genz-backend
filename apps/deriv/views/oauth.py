from datetime import timedelta

import requests

from django.conf import settings
from django.shortcuts import redirect
from django.utils import timezone

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.deriv.services.account_service import DerivAccountService
from apps.deriv.services.websocket_service import DerivWebSocketService

from ..models import DerivOAuthSession, DerivTradingAccount

from ..serializers.serializers import (
    AuthorizeSerializer,
    BuySerializer,
    CandleSerializer,
    DisconnectSerializer,
    HistorySerializer,
    ProposalSerializer,
    SellSerializer,
    TickSerializer,
)

from ..services.oauth_service import DerivOAuthService

from ..services.token_service import DerivTokenService

from django.db import transaction
from django.utils import timezone


from datetime import timedelta

from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.deriv.models import DerivOAuthSession
from apps.deriv.services.oauth_service import DerivOAuthService
import logging

logger = logging.getLogger(__name__)


class ConnectView(APIView):
    """
    Initiates the Deriv OAuth flow.

    Generates PKCE credentials, stores them temporarily,
    and returns the authorization URL.
    """

    authentication_classes = []
    permission_classes = []

    def get(self, request):
        logger.info("=" * 80)
        logger.info("Starting Deriv OAuth connection flow.")

        try:
            deleted, _ = DerivOAuthSession.objects.filter(
                expires_at__lt=timezone.now()
            ).delete()

            logger.info("Expired OAuth sessions deleted: %s", deleted)

            oauth_service = DerivOAuthService()

            logger.info("Generating PKCE credentials...")

            oauth_data = oauth_service.create_authorization()

            logger.info("OAuth data generated successfully.")
            logger.info("State: %s", oauth_data["state"])
            logger.info("Authorization URL: %s", oauth_data["authorization_url"])

            DerivOAuthSession.objects.create(
                state=oauth_data["state"],
                code_verifier=oauth_data["code_verifier"],
                expires_at=timezone.now() + timedelta(minutes=10),
                used=False,
            )

            logger.info("OAuth session stored successfully.")
            logger.info("=" * 80)

            return Response(
                {
                    "success": True,
                    "message": "Redirect user to the returned authorization URL.",
                    "authorization_url": oauth_data["authorization_url"],
                },
                status=status.HTTP_200_OK,
            )

        except Exception:
            logger.exception("Failed to start Deriv OAuth flow.")

            return Response(
                {
                    "success": False,
                    "message": "Unable to start the Deriv OAuth flow.",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class CallbackView(APIView):
    """
    Handles the OAuth callback from Deriv.
    """

    authentication_classes = []
    permission_classes = []

    def get(self, request):

        logger.info("=" * 80)
        logger.info("DERIV OAUTH CALLBACK RECEIVED")

        error = request.GET.get("error")

        if error:
            logger.error("Deriv OAuth returned an error: %s", error)

            return redirect(
                f"{settings.FRONTEND_URL}/auth/deriv?" f"success=false&error={error}"
            )

        code = request.GET.get("code")
        state = request.GET.get("state")

        logger.info(
            "Authorization code: %s",
            code[:15] + "..." if code else None,
        )
        logger.info("State: %s", state)

        if not code or not state:
            logger.error("Callback missing authorization code or state.")

            return redirect(
                f"{settings.FRONTEND_URL}/auth/deriv?"
                "success=false&error=invalid_callback"
            )

        try:
            oauth_session = DerivOAuthSession.objects.get(
                state=state,
                used=False,
            )

            logger.info("OAuth session located.")

        except DerivOAuthSession.DoesNotExist:

            logger.exception("OAuth session not found.")

            return redirect(
                f"{settings.FRONTEND_URL}/auth/deriv?"
                "success=false&error=invalid_state"
            )

        if oauth_session.is_expired:

            logger.warning("OAuth session expired.")

            oauth_session.delete()

            return redirect(
                f"{settings.FRONTEND_URL}/auth/deriv?"
                "success=false&error=session_expired"
            )

        try:

            logger.info("Exchanging authorization code...")

            token = DerivTokenService.exchange_code(
                code=code,
                code_verifier=oauth_session.code_verifier,
            )

            logger.info("OAuth token successfully received.")

            logger.info("Token type: %s", token.get("token_type"))
            logger.info("Scopes: %s", token.get("scope"))
            logger.info("Expires in: %s", token.get("expires_in"))

            access_token = token["access_token"]

            logger.info("Initializing DerivAccountService...")

            account_service = DerivAccountService(access_token)

            logger.info("Saving OAuth connection...")

            connection = account_service.save_connection(token)

            logger.info(
                "Connection saved successfully. Connection ID: %s",
                connection.id,
            )

            logger.info("Synchronizing trading accounts...")

            account_count = DerivTradingAccount.objects.filter(
                connection=connection,
            ).count()

            logger.info(
                "Synchronization complete. %s account(s) connected.",
                account_count,
            )

            oauth_session.used = True
            oauth_session.save(update_fields=["used"])

            logger.info("OAuth session marked as used.")

            logger.info("OAuth flow completed successfully.")

            logger.info("=" * 80)

            return redirect(f"{settings.FRONTEND_URL}/auth/deriv?" "success=true")

        except Exception:

            logger.exception("OAuth callback failed.")

            return redirect(
                f"{settings.FRONTEND_URL}/auth/deriv?"
                "success=false&error=authorization_failed"
            )


# class BaseDerivView(APIView):
#     """
#     Base class for Deriv API views.
#     """

#     service_class = DerivWebSocketService

#     def execute(self, callback):
#         service = self.service_class()

#         try:
#             service.connect()
#             result = callback(service)
#             return Response(result, status=status.HTTP_200_OK)

#         except Exception as exc:
#             return Response(
#                 {
#                     "success": False,
#                     "error": str(exc),
#                 },
#                 status=status.HTTP_400_BAD_REQUEST,
#             )

#         finally:
#             try:
#                 service.disconnect()
#             except Exception:
#                 pass


# class AuthorizeView(BaseDerivView):

#     def post(self, request):

#         serializer = AuthorizeSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)

#         token = serializer.validated_data["token"]

#         return self.execute(lambda service: service.authorize(token))


# class AccountView(BaseDerivView):

#     def post(self, request):

#         serializer = AuthorizeSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)

#         token = serializer.validated_data["token"]

#         def callback(service):
#             service.authorize(token)
#             return service.get_profile()

#         return self.execute(callback)


# class BalanceView(BaseDerivView):

#     def post(self, request):

#         serializer = AuthorizeSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)

#         token = serializer.validated_data["token"]

#         def callback(service):
#             service.authorize(token)
#             return service.get_balance()

#         return self.execute(callback)


# class ActiveSymbolsView(BaseDerivView):

#     def get(self, request):

#         return self.execute(lambda service: service.active_symbols())


# class TickView(BaseDerivView):

#     def post(self, request):

#         serializer = TickSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)

#         return self.execute(
#             lambda service: service.ticks(serializer.validated_data["symbol"])
#         )


# class CandleView(BaseDerivView):

#     def post(self, request):

#         serializer = CandleSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)

#         data = serializer.validated_data

#         return self.execute(
#             lambda service: service.candles(
#                 symbol=data["symbol"],
#                 granularity=data["granularity"],
#                 count=data["count"],
#             )
#         )


# class ProposalView(BaseDerivView):

#     def post(self, request):

#         serializer = ProposalSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)

#         return self.execute(lambda service: service.proposal(serializer.validated_data))


# class BuyView(BaseDerivView):

#     def post(self, request):

#         serializer = BuySerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)

#         data = serializer.validated_data

#         return self.execute(
#             lambda service: service.buy(
#                 proposal_id=data["proposal_id"],
#                 price=float(data["price"]),
#             )
#         )


# class SellView(BaseDerivView):

#     def post(self, request):

#         serializer = SellSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)

#         data = serializer.validated_data

#         return self.execute(
#             lambda service: service.sell(
#                 contract_id=data["contract_id"],
#                 price=float(data["price"]),
#             )
#         )


# class TradeHistoryView(BaseDerivView):

#     def post(self, request):

#         serializer = HistorySerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)

#         return self.execute(
#             lambda service: service.trade_history(serializer.validated_data["count"])  # type: ignore
#         )


# class DisconnectView(APIView):

#     def post(self, request):

#         serializer = DisconnectSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)

#         return Response(
#             {
#                 "success": True,
#                 "message": "Disconnected successfully.",
#             }
#         )
