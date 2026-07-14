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

from .models import DerivAccount, DerivOAuthSession

from .serializers import (
    AuthorizeSerializer,
    BuySerializer,
    CandleSerializer,
    DisconnectSerializer,
    HistorySerializer,
    ProposalSerializer,
    SellSerializer,
    TickSerializer,
)

from .services.oauth_service import DerivOAuthService

from .services.token_service import DerivTokenService

from django.db import transaction
from django.utils import timezone


class ConnectView(APIView):
    """
    Initiates the Deriv OAuth flow.

    Generates PKCE credentials, stores them temporarily,
    and returns the authorization URL.
    """

    authentication_classes = []
    permission_classes = []

    def get(self, request):
        try:
            # Remove expired OAuth sessions
            DerivOAuthSession.objects.filter(expires_at__lt=timezone.now()).delete()

            oauth_service = DerivOAuthService()

            oauth = oauth_service.create_authorization()

            DerivOAuthSession.objects.create(
                state=oauth["state"],
                code_verifier=oauth["code_verifier"],
                expires_at=timezone.now() + timedelta(minutes=10),
            )

            return Response(
                {
                    "success": True,
                    "message": "Redirect user to the returned authorization URL.",
                    "authorization_url": oauth["authorization_url"],
                },
                status=status.HTTP_200_OK,
            )

        except Exception as exc:
            return Response(
                {
                    "success": False,
                    "message": "Unable to start the Deriv OAuth flow.",
                    "error": str(exc),
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

        error = request.GET.get("error")

        if error:
            return redirect(
                f"{settings.FRONTEND_URL}/auth/deriv?" f"success=false&error={error}"
            )

        code = request.GET.get("code")
        state = request.GET.get("state")

        if not code or not state:
            return redirect(
                f"{settings.FRONTEND_URL}/auth/deriv?"
                "success=false&error=invalid_callback"
            )

        try:

            oauth_session = DerivOAuthSession.objects.get(
                state=state,
                used=False,
            )

        except DerivOAuthSession.DoesNotExist:

            return redirect(
                f"{settings.FRONTEND_URL}/auth/deriv?"
                "success=false&error=invalid_state"
            )

        if oauth_session.is_expired:

            oauth_session.delete()

            return redirect(
                f"{settings.FRONTEND_URL}/auth/deriv?"
                "success=false&error=session_expired"
            )

        try:

            token = DerivTokenService.exchange_code(
                code=code,
                code_verifier=oauth_session.code_verifier,
            )

            access_token = token["access_token"]
            expires_in = token.get("expires_in", 3600)

            account_service = DerivAccountService(access_token)

            account_data = account_service.get_primary_account()

            account_service.save_account(
                account_data=account_data,
                access_token=access_token,
                expires_in=expires_in,
            )

            oauth_session.used = True
            oauth_session.save(update_fields=["used"])

            return redirect(f"{settings.FRONTEND_URL}/auth/deriv?" "success=true")

        except Exception:

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
