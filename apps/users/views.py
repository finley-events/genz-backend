# users/views.py
from typing import cast

from .models import User


from rest_framework import generics, permissions, status
from rest_framework.response import Response

from .models import Profile
from .serializers import (
    ChangePasswordSerializer,
    RegisterSerializer,
    UpdateProfileSerializer,
    UserSerializer,
)
from .services import UserService


class RegisterView(generics.CreateAPIView):
    """
    Register a new user.
    """

    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
        serializer.save()


class CurrentUserView(generics.RetrieveAPIView):
    """
    Retrieve the currently authenticated user.
    """

    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class UpdateProfileView(generics.UpdateAPIView):
    """
    Update the authenticated user's profile.
    """

    serializer_class = UpdateProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        user = cast(User, self.request.user)
        profile, _ = Profile.objects.get_or_create(user=user)
        return profile

    def perform_update(self, serializer):
        user = cast(User, self.request.user)

        UserService.update_profile(
            user=user,
            **serializer.validated_data,
        )


class ChangePasswordView(generics.GenericAPIView):
    """
    Change the authenticated user's password.
    """

    serializer_class = ChangePasswordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data,
            context={"request": request},
        )

        serializer.is_valid(raise_exception=True)

        UserService.change_password(
            user=request.user,
            old_password=serializer.validated_data["old_password"],
            new_password=serializer.validated_data["new_password"],
        )

        return Response(
            {"detail": "Password changed successfully."},
            status=status.HTTP_200_OK,
        )
