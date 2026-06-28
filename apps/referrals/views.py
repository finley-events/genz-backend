# apps/referrals/views.py

from typing import cast

from rest_framework import generics, permissions, status
from rest_framework.request import Request
from rest_framework.response import Response

from decimal import Decimal

from django.db.models import Sum
from rest_framework.views import APIView

from apps.users.models import User

from .models import Referral, ReferralReward
from .serializers import (
    ApplyReferralSerializer,
    ReferralRewardSerializer,
    ReferralSerializer,
)
from .services import ReferralService


class ApplyReferralView(generics.GenericAPIView):
    """
    Apply a referral code for the authenticated user.
    """

    serializer_class = ApplyReferralSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request: Request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = cast(User, request.user)

        referral = ReferralService.create_referral(
            referred_user=user,
            referral_code=serializer.validated_data["referral_code"],
        )

        return Response(
            ReferralSerializer(referral).data,
            status=status.HTTP_201_CREATED,
        )


class ReferralListView(generics.ListAPIView):
    """
    List referrals made by the authenticated user.
    """

    serializer_class = ReferralSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = cast(User, self.request.user)

        return (
            Referral.objects.filter(referrer=user)
            .select_related("referrer", "referred_user")
            .order_by("-created_at")
        )


class ReferralRewardListView(generics.ListAPIView):
    """
    List rewards earned by the authenticated user's referrals.
    """

    serializer_class = ReferralRewardSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = cast(User, self.request.user)

        return (
            ReferralReward.objects.filter(
                referral__referrer=user,
            )
            .select_related(
                "referral",
                "transaction",
            )
            .order_by("-created_at")
        )


class ReferralStatsView(APIView):
    """
    Return referral statistics for the authenticated user.
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request: Request, *args, **kwargs):
        user = cast(User, request.user)

        referrals = Referral.objects.filter(referrer=user)

        total_referrals = referrals.count()

        pending_referrals = referrals.filter(
            status=Referral.Status.PENDING,
        ).count()

        qualified_referrals = referrals.filter(
            status=Referral.Status.QUALIFIED,
        ).count()

        rewarded_referrals = referrals.filter(
            status=Referral.Status.REWARDED,
        ).count()

        total_rewards = ReferralReward.objects.filter(
            referral__referrer=user,
            status=ReferralReward.Status.COMPLETED,
        ).aggregate(total=Sum("amount"),)["total"] or Decimal("0")

        referral_code = getattr(
            getattr(user, "profile", None),
            "referral_code",
            None,
        )

        return Response(
            {
                "referral_code": referral_code,
                "total_referrals": total_referrals,
                "pending_referrals": pending_referrals,
                "qualified_referrals": qualified_referrals,
                "rewarded_referrals": rewarded_referrals,
                "total_rewards": total_rewards,
            }
        )
