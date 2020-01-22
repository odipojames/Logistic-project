from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response

from .serializers import TrucksCsvSerializer, TrailersCsvSerializer
from .models import Truck, Trailer
from utils.permissions import IsTransporterOrAdmin

class TruckCsvUploadView(generics.CreateAPIView):
    serializer_class = TrucksCsvSerializer
    queryset = Truck.objects.all()
    permission_classes = (IsTransporterOrAdmin,)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        response_args = serializer.save()
        return Response(*response_args)


class TrailerCsvUploadView(generics.CreateAPIView):
    serializer_class = TrailersCsvSerializer
    queryset = Trailer.objects.all()
    permission_classes = (IsTransporterOrAdmin,)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        response_args = serializer.save()
        return Response(*response_args)
