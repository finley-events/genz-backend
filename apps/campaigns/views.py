from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from typing import cast, Any

from apps.campaigns.services.campaign_service import CampaignService

from .models import (
    Campaign,
    CampaignParticipation,
    CampaignSubmission,
    CampaignReward,
    CampaignTask,
)

from .serializers import (
    CreateCampaignSerializer,
    JoinCampaignSerializer,
    SubmitTaskSerializer,
    VerifySubmissionSerializer,
    RejectSubmissionSerializer,
    FundCampaignSerializer,
    RewardPayoutSerializer,
    CampaignSerializer,
    CampaignParticipationSerializer,
    CampaignSubmissionSerializer,
    CampaignRewardSerializer,
)

from .services.participation_service import (
    ParticipationService,
)

from .services.campain_reward import (
    CampaignRewardService,
)

from .services.funding_service import (
    CampaignFundingService,
)


class JoinCampaignView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        serializer = JoinCampaignSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        serializer.is_valid(raise_exception=True)

        data = cast(dict, serializer.validated_data)

        campaign = get_object_or_404(
            Campaign,
            pk=data["campaign_id"],
        )

        participation = ParticipationService.join_campaign(
            campaign=campaign,
            user=request.user,
        )

        return Response(
            CampaignParticipationSerializer(participation).data,
            status=status.HTTP_201_CREATED,
        )


class SubmitTaskView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        serializer = SubmitTaskSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        data = cast(
            dict[str, Any],
            serializer.validated_data,
        )

        participation = get_object_or_404(
            CampaignParticipation,
            user=request.user,
            campaign_id=data["campaign_id"],
        )

        task = get_object_or_404(
            CampaignTask,
            pk=data["task_id"],
        )

        submission = ParticipationService.submit_task(
            participation=participation,
            task=task,
            proof_url=serializer.validated_data.get("proof_url"),  # type: ignore
            proof_image=serializer.validated_data.get("proof_image"),  # type: ignore
            notes=serializer.validated_data.get(  # type: ignore
                "notes",
                "",
            ),
        )

        return Response(
            CampaignSubmissionSerializer(submission).data,
            status=status.HTTP_201_CREATED,
        )


class VerifySubmissionView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        if not request.user.is_staff:
            return Response(
                {"detail": "Only staff can verify submissions."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = VerifySubmissionSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        data = cast(
            dict[str, Any],
            serializer.validated_data,
        )

        submission = get_object_or_404(
            CampaignSubmission,
            pk=data["submission_id"],
        )

        submission = ParticipationService.verify_submission(
            submission=submission,
            verified_by=request.user,
        )

        return Response(CampaignSubmissionSerializer(submission).data)


class RejectSubmissionView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        if not request.user.is_staff:
            return Response(
                {"detail": "Only staff can reject submissions."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = RejectSubmissionSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        data = cast(
            dict[str, Any],
            serializer.validated_data,
        )

        submission = get_object_or_404(
            CampaignSubmission,
            pk=data["submission_id"],
        )

        submission = ParticipationService.reject_submission(
            submission=submission,
            verified_by=request.user,
        )

        return Response(CampaignSubmissionSerializer(submission).data)


class FundCampaignView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        serializer = FundCampaignSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        data = cast(
            dict[str, Any],
            serializer.validated_data,
        )

        campaign = get_object_or_404(
            Campaign,
            pk=data["campaign_id"],
            sponsor=request.user,
        )
        data = cast(
            dict[str, Any],
            serializer.validated_data,
        )

        funding = CampaignFundingService.fund_campaign(
            campaign=campaign,
            sponsor=request.user,
            amount=data["amount"],
            notes=data.get(
                "notes",
                "",
            ),
        )

        return Response(
            {
                "message": "Campaign funded successfully.",
                "funding_id": str(funding.id),
            },
            status=status.HTTP_201_CREATED,
        )


class PayRewardView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        if not request.user.is_staff:
            return Response(
                {"detail": "Only staff can pay rewards."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = RewardPayoutSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        data = cast(
            dict[str, Any],
            serializer.validated_data,
        )

        participation = get_object_or_404(
            CampaignParticipation,
            pk=data["participation_id"],
        )

        reward = CampaignRewardService.create_reward(
            participation=participation,
        )

        reward = CampaignRewardService.pay_reward(
            reward=reward,
        )

        return Response(CampaignRewardSerializer(reward).data)


class CampaignListView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        campaigns = Campaign.objects.filter(
            status=Campaign.Status.ACTIVE,
        )

        serializer = CampaignSerializer(
            campaigns,
            many=True,
        )

        return Response(serializer.data)


class CampaignDetailView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, campaign_id):

        campaign = get_object_or_404(
            Campaign,
            pk=campaign_id,
        )

        serializer = CampaignSerializer(campaign)

        return Response(serializer.data)


class CreateCampaignView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        serializer = CreateCampaignSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        serializer.is_valid(
            raise_exception=True,
        )

        data = cast(
            dict[str, Any],
            serializer.validated_data,
        )

        campaign = CampaignService.create_campaign(
            sponsor=request.user,
            **data,
        )

        return Response(
            CampaignSerializer(campaign).data,
            status=status.HTTP_201_CREATED,
        )


class PublishCampaignView(APIView):

    permission_classes = [IsAuthenticated]

    def post(
        self,
        request,
        campaign_id,
    ):

        campaign = get_object_or_404(
            Campaign,
            pk=campaign_id,
            sponsor=request.user,
        )

        campaign = CampaignService.publish_campaign(
            campaign=campaign, user=request.user
        )

        return Response(CampaignSerializer(campaign).data)


class PauseCampaignView(APIView):

    permission_classes = [IsAuthenticated]

    def post(
        self,
        request,
        campaign_id,
    ):

        campaign = get_object_or_404(
            Campaign,
            pk=campaign_id,
            sponsor=request.user,
        )

        campaign = CampaignService.pause_campaign(campaign=campaign, user=request.user)

        return Response(CampaignSerializer(campaign).data)


class CompleteCampaignView(APIView):

    permission_classes = [IsAuthenticated]

    def post(
        self,
        request,
        campaign_id,
    ):

        campaign = get_object_or_404(
            Campaign,
            pk=campaign_id,
            sponsor=request.user,
        )

        campaign = CampaignService.complete_campaign(
            campaign=campaign,
        )

        return Response(CampaignSerializer(campaign).data)


class CancelCampaignView(APIView):

    permission_classes = [IsAuthenticated]

    def post(
        self,
        request,
        campaign_id,
    ):

        campaign = get_object_or_404(
            Campaign,
            pk=campaign_id,
            sponsor=request.user,
        )

        campaign = CampaignService.cancel_campaign(campaign=campaign, user=request.user)

        return Response(CampaignSerializer(campaign).data)


class ResumeCampaignView(APIView):

    permission_classes = [IsAuthenticated]

    def post(
        self,
        request,
        campaign_id,
    ):

        campaign = get_object_or_404(
            Campaign,
            pk=campaign_id,
            sponsor=request.user,
        )

        campaign = CampaignService.resume_campaign(campaign=campaign, user=request.user)

        return Response(CampaignSerializer(campaign).data)
