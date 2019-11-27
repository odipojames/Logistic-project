from django.shortcuts import render
from rest_framework.response import Response
from utils.renderers import JsnRenderer
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.renderers import JSONRenderer
from rest_framework import generics
from .models import *
from .serializer import *
from rest_framework.decorators import api_view
from rest_framework.generics import RetrieveUpdateAPIView
# Create your views here.


class RegistrationAPIView(generics.GenericAPIView):
    permission_classes = (AllowAny,)
    renderer_classes = (JsnRenderer, )
    serializer_class = RegistrationSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        user = serializer.data

        response = {
            "user": dict(user),
            "message": "Account created successfully,confirm from your email"

        }

        return Response(response, status=status.HTTP_201_CREATED)


class LoginAPIView(generics.GenericAPIView):

    permission_classes = (AllowAny,)
    renderer_classes = (JsnRenderer, )
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.data

        response = {
            "user": dict(user),
            "message": "logged in successfully"
        }

        return Response(response, status=status.HTTP_200_OK)


class UserUpdateAPIView(generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)
    renderer_classes = (JsnRenderer,)
    serializer_class = UserUpdateSerializer

    def retrieve(self, request, *args, **kwargs):
        # serialize to handle turning our `User` object into something that
        # can be JSONified and sent to the client.
        serializer = self.serializer_class(request.user)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        serializer_data = request.data.get('user', {})

        # Here is that serialize, validate, save pattern we talked about
        # before.
        serializer = self.serializer_class(
            request.user, data=serializer_data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)
