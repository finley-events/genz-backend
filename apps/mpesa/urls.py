from django.urls import path

from .views import (
    DepositView,
    WithdrawalView,
    PaymentHistoryView,
    PaymentDetailView,
    PayHeroWebhookView,
)

app_name = "mpesa"

urlpatterns = [
    path(
        "deposit/",
        DepositView.as_view(),
        name="deposit",
    ),
    path(
        "withdraw/",
        WithdrawalView.as_view(),
        name="withdraw",
    ),
    path(
        "webhook/",
        PayHeroWebhookView.as_view(),
        name="webhook",
    ),
    path(
        "history/",
        PaymentHistoryView.as_view(),
        name="history",
    ),
    path(
        "<str:reference>/",
        PaymentDetailView.as_view(),
        name="payment-detail",
    ),
]
