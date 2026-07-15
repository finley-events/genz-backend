from django.urls import path
from apps.deriv.views.accounts import AccountsView
from apps.deriv.views.connection import ConnectionView
from apps.deriv.views.otp import GenerateOTPView

from .views.oauth import (
    CallbackView,
    ConnectView,
)

app_name = "deriv"

urlpatterns = [
    # Authentication
    path(
        "connect/",
        ConnectView.as_view(),
        name="connect",
    ),
    path(
        "callback/",
        CallbackView.as_view(),
        name="callback",
    ),
    path(
        "accounts/",
        AccountsView.as_view(),
        name="deriv-accounts",
    ),
    path(
        "accounts/<str:account_id>/otp/",
        GenerateOTPView.as_view(),
        name="deriv-generate-otp",
    ),
    path(
        "connection/",
        ConnectionView.as_view(),
        name="deriv-connection",
    ),
    #     path(
    #         "authorize/",
    #         AuthorizeView.as_view(),
    #         name="authorize",
    #     ),
    #     path(
    #         "disconnect/",
    #         DisconnectView.as_view(),
    #         name="disconnect",
    #     ),
    #     # Account
    #     path(
    #         "account/",
    #         AccountView.as_view(),
    #         name="account",
    #     ),
    #     path(
    #         "balance/",
    #         BalanceView.as_view(),
    #         name="balance",
    #     ),
    #     # Market Data
    #     path(
    #         "symbols/",
    #         ActiveSymbolsView.as_view(),
    #         name="symbols",
    #     ),
    #     path(
    #         "ticks/",
    #         TickView.as_view(),
    #         name="ticks",
    #     ),
    #     path(
    #         "candles/",
    #         CandleView.as_view(),
    #         name="candles",
    #     ),
    #     # Trading
    #     path(
    #         "proposal/",
    #         ProposalView.as_view(),
    #         name="proposal",
    #     ),
    #     path(
    #         "buy/",
    #         BuyView.as_view(),
    #         name="buy",
    #     ),
    #     path(
    #         "sell/",
    #         SellView.as_view(),
    #         name="sell",
    #     ),
    #     path(
    #         "history/",
    #         TradeHistoryView.as_view(),
    #         name="history",
    #     ),
    #
]
