from django.shortcuts import render
from rest_framework.response import Response
from utils.renderers import JsnRenderer
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.renderers import JSONRenderer
from rest_framework import generics
from .models import *
from .serializers import *
from rest_framework.decorators import api_view
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.parsers import MultiPartParser, FormParser

# Create your views here.


class TransporterRegistrationAPIView(APIView):
    '''register transporter and its company once'''
    permission_classes = (AllowAny,)
    renderer_classes = (JsnRenderer, )
    serializer_class = TransporterSerializer
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        transporter = serializer.data

        response = {
            "transporter": dict(transporter),
            "message": "Transporter registration request sent, wait for your account to be varified"

        }

        return Response(response, status=status.HTTP_201_CREATED)


class CargoOwnerRegistrationAPIView(APIView):
    '''register cargo owner and its company once'''
    permission_classes = (AllowAny,)
    renderer_classes = (JsnRenderer, )
    serializer_class = CargoOwnerSerializer
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        cargoOwner = serializer.data

        response = {
            "transporter": dict(cargoOwner),
            "message": "cargo owner registration request sent, wait for your account to be varified"

        }

        return Response(response, status=status.HTTP_201_CREATED)
