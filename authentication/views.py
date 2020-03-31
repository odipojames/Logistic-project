from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from django.shortcuts import get_object_or_404

from authentication.serializers import (
    LoginSerializer,
    RegistrationSerializer,
    UserUpdateSerializer,
    ProfileSerializer,
)
from utils.renderers import JsnRenderer
from authentication.models import Profile
from utils.permissions import IsOwnerOrAdmin
from companies.models import Company, CargoOwnerCompany, TransporterCompany


class RegistrationAPIView(generics.CreateAPIView):
    renderer_classes = (JsnRenderer,)
    serializer_class = RegistrationSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)

        payload = response.data.copy()
        payload[
            "message"
        ] = "Account created successfully. Please confirm from your email."

        return Response(payload, status=status.HTTP_201_CREATED)


class LoginAPIView(TokenObtainPairView):

    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)

        response.data["message"] = "Logged in successfully. Welcome to Shipper."
        payload = {"data": response.data}

        return Response(payload, status=status.HTTP_200_OK)


class UserUpdateAPIView(generics.RetrieveUpdateAPIView):
    permission_classes = (IsAuthenticated,)
    renderer_classes = (JsnRenderer,)
    serializer_class = UserUpdateSerializer

    def retrieve(self, request, *args, **kwargs):
        # serialize to handle turning our `User` object into something that
        # can be JSONified and sent to the client.
        serializer = self.serializer_class(request.user)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        data = request.data.copy()
        data.pop("password", None)
        data.pop("role", None)
        serializer = self.serializer_class(request.user, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """
    Method to log out users.
    """

    refresh_token = request.data.get("refresh")

    if not refresh_token:
        return Response({"refresh": "You must provide a refresh token."})

    try:
        refresh_token_instance = RefreshToken(refresh_token)
        refresh_token_instance.blacklist()

        next_url = (
            request.query_params.get("next") if request.query_params.get("next") else ""
        )

        response = {
            "data": {
                "message": "You have been succesfully logged out",
                "next_url": next_url,
            }
        }

        return Response(response, status=status.HTTP_200_OK)

    except TokenError:
        return Response(
            {"detail": "You are already logged out."},
            status=status.HTTP_400_BAD_REQUEST,
        )


class GetProfileAPIView(generics.ListAPIView):
    """Get the profile of the user who is currently logged in"""

    renderer_classes = (JsnRenderer,)
    serializer_class = ProfileSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """
        Only return the profile of the currently logged in User
        """
        user = self.request.user

        try:
            # some users might not have a profile, either because signal did not fire
            # or they existed before signal profile was fired.
            profile = Profile.objects.get(user=user)
        except Profile.DoesNotExist:
            profile = Profile.objects.create(user=user)

        return Profile.objects.filter(user=user)


class ProfileRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateAPIView):
    """user profile update api """

    renderer_classes = (JsnRenderer,)
    serializer_class = ProfileSerializer
    permission_classes = (IsAuthenticated, IsOwnerOrAdmin)

    def get_queryset(self):
        user = self.request.user

        if user.is_superuser:
            return Profile.objects.all()

        if (
            str(user.role) == "transporter-director"
            or str(user.role) == "cargo-owner-director"
        ):
            company = Company.objects.get(company_director=user)
            return Profile.objects.filter(user__employer=company)

        if str(user.role) == "admin" or str(user.role) == "staff":
            company = user.employer
            return Profile.objects.filter(user__employer=company)

    def retrieve(self, request, pk):
        profile = self.get_object()
        serializer = self.serializer_class(profile)
        response = {
            "message": "profile retrieved succesfully",
            "profile": serializer.data,
        }
        return Response(response, status.HTTP_200_OK)

    def update(self, request, **kwargs):

        obj = get_object_or_404(self.get_queryset(), pk=self.kwargs["pk"])
        self.check_object_permissions(self.request, obj)
        kwargs["partial"] = True
        data = request.data
        data.pop("user")
        serializer = self.serializer_class(obj, data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        response = {
            "message": "profile info succesfully updated",
            "profile": serializer.data,
        }
        return Response(response, status.HTTP_200_OK)
