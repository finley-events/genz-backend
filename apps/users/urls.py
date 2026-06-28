# users/urls.py

from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from .views import (
    ChangePasswordView,
    CurrentUserView,
    RegisterView,
    UpdateProfileView,
)

app_name = "users"

urlpatterns = [
    # Authentication
    path(
        "register/",
        RegisterView.as_view(),
        name="register",
    ),
    path(
        "login/",
        TokenObtainPairView.as_view(),
        name="login",
    ),
    path(
        "token/refresh/",
        TokenRefreshView.as_view(),
        name="token_refresh",
    ),
    # User profile
    path(
        "me/",
        CurrentUserView.as_view(),
        name="current_user",
    ),
    path(
        "me/update/",
        UpdateProfileView.as_view(),
        name="update_profile",
    ),
    # Password management
    path(
        "change-password/",
        ChangePasswordView.as_view(),
        name="change_password",
    ),
]
