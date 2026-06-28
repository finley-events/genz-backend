# apps/referrals/urls.py

from django.urls import path

from .views import (
    ApplyReferralView,
    ReferralListView,
    ReferralRewardListView,
    ReferralStatsView,
)

app_name = "referrals"

urlpatterns = [
    # Apply a referral code
    path(
        "apply/",
        ApplyReferralView.as_view(),
        name="apply-referral",
    ),
    # List referrals made by the authenticated user
    path(
        "",
        ReferralListView.as_view(),
        name="referral-list",
    ),
    # Referral statistics/dashboard
    path(
        "stats/",
        ReferralStatsView.as_view(),
        name="referral-stats",
    ),
    # Referral reward history
    path(
        "rewards/",
        ReferralRewardListView.as_view(),
        name="referral-rewards",
    ),
]
