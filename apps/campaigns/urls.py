from django.urls import path

from .views import (
    CampaignListView,
    CampaignDetailView,

    CreateCampaignView,
    PublishCampaignView,
    PauseCampaignView,
    ResumeCampaignView,
    CancelCampaignView,
    CompleteCampaignView,

    JoinCampaignView,
    SubmitTaskView,

    VerifySubmissionView,
    RejectSubmissionView,

    FundCampaignView,

    PayRewardView,
)

app_name = "campaigns"

urlpatterns = [
    # Campaign Discovery
    path(
        "",
        CampaignListView.as_view(),
        name="campaign-list",
    ),

    path(
        "<uuid:campaign_id>/",
        CampaignDetailView.as_view(),
        name="campaign-detail",
    ),

    # Campaign Management
    path(
        "create/",
        CreateCampaignView.as_view(),
        name="campaign-create",
    ),

    path(
        "<uuid:campaign_id>/publish/",
        PublishCampaignView.as_view(),
        name="campaign-publish",
    ),

    path(
        "<uuid:campaign_id>/pause/",
        PauseCampaignView.as_view(),
        name="campaign-pause",
    ),

    path(
        "<uuid:campaign_id>/resume/",
        ResumeCampaignView.as_view(),
        name="campaign-resume",
    ),

    path(
        "<uuid:campaign_id>/cancel/",
        CancelCampaignView.as_view(),
        name="campaign-cancel",
    ),

    path(
        "<uuid:campaign_id>/complete/",
        CompleteCampaignView.as_view(),
        name="campaign-complete",
    ),

    # Participation
    path(
        "join/",
        JoinCampaignView.as_view(),
        name="join-campaign",
    ),

    path(
        "submit/",
        SubmitTaskView.as_view(),
        name="submit-task",
    ),

    # Moderation
    path(
        "verify/",
        VerifySubmissionView.as_view(),
        name="verify-submission",
    ),

    path(
        "reject/",
        RejectSubmissionView.as_view(),
        name="reject-submission",
    ),

    # Funding
    path(
        "fund/",
        FundCampaignView.as_view(),
        name="fund-campaign",
    ),

    # Rewards
    path(
        "pay-reward/",
        PayRewardView.as_view(),
        name="pay-reward",
    ),
]
