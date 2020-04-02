from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response

from .serializers import (
    TrucksCsvSerializer,
    TrailersCsvSerializer,
    TruckSerializer,
    TrailerSerializer,
)
from .models import Truck, Trailer
from companies.models import TransporterCompany, Company
from utils.renderers import JsnRenderer
from utils.permissions import (
    IsTransporterOrAdmin,
    IsAdminOrAssetOwner,
    IsTransporterEmployee,
)
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated


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


class TruckListCreateAPIView(generics.ListCreateAPIView):
    """ Transporter or admin can create trucks"""

    serializer_class = TruckSerializer
    renderer_classes = (JsnRenderer,)
    permission_classes = (IsAuthenticated, IsTransporterEmployee)

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Truck.objects.all()

        if user.is_superuser == False:
            company = user.employer
            transporter = TransporterCompany.objects.get(company=company).pk
            return Truck.active_objects.get_personal_assets(owned_by=transporter)

    def create(self, request):
        user = self.request.user
        data = request.data.copy()
        if request.user.is_superuser == False:
            owned_by = TransporterCompany.objects.get(company=request.user.employer).pk
            data["owned_by"] = owned_by
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        truck = serializer.data

        response = {"truck": dict(truck), "message": "Truck succesfully created"}

        return Response(response, status=status.HTTP_201_CREATED)

    def list(self, request):
        queryset = self.get_queryset()
        serialize = self.serializer_class(queryset, many=True)

        trucks = serialize.data
        if len(trucks) > 0:
            response = {"Message": "Trucks Retrieved Successfully", "Trucks": trucks}
        else:
            response = {"Message": "There are no Trucks for now"}
        return Response(response, status=status.HTTP_200_OK)


class TruckRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TruckSerializer
    renderer_classes = (JsnRenderer,)
    permission_classes = (IsAuthenticated, IsTransporterEmployee)

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Truck.objects.all()

        if user.is_superuser == False:
            company = user.employer
            transporter = TransporterCompany.objects.get(company=company).pk
            return Truck.active_objects.get_personal_assets(owned_by=transporter)

    def retrieve(self, request, pk):
        truck = self.get_object()
        serialize = self.serializer_class(truck)
        respose = {"Message": "Truck Successfully Retrieved", "Truck": serialize.data}

        return Response(respose, status=status.HTTP_200_OK)

    def update(self, request, **kwargs):
        """ Amend Truck """
        obj = self.get_object()
        self.check_object_permissions(request, obj)
        kwargs["partial"] = True
        data = request.data.copy()
        data.pop("is_deleted", None)
        data.pop("owned_by", None)
        serializer = self.serializer_class(obj, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        response = {"Truck": serializer.data, "Message": "Truck updated successfully"}
        return Response(response, status=status.HTTP_200_OK)

    def destroy(self, request, pk):
        """ Delete a truck """
        obj = self.get_object()
        self.check_object_permissions(request, obj)
        obj.soft_delete(commit=True)
        return Response(status.HTTP_204_NO_CONTENT)


class TrailerListCreateAPIView(generics.ListCreateAPIView):
    """ Transporter or admin can create trailers"""

    serializer_class = TrailerSerializer
    renderer_classes = (JsnRenderer,)
    permission_classes = (IsAuthenticated, IsTransporterEmployee)

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Trailer.objects.all()

        if user.is_superuser == False:
            company = user.employer
            transporter = TransporterCompany.objects.get(company=company).pk
            return Trailer.active_objects.get_personal_assets(owned_by=transporter)

    def create(self, request):
        data = request.data.copy()
        if request.user.is_superuser == False:
            owned_by = TransporterCompany.objects.get(company=request.user.employer).pk
            data["owned_by"] = owned_by
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        trailer = serializer.data

        response = {"trailer": dict(trailer), "message": "Trailer succesfully created"}

        return Response(response, status=status.HTTP_201_CREATED)

    def list(self, request):
        queryset = self.get_queryset()
        serialize = self.serializer_class(queryset, many=True)

        trailers = serialize.data
        if len(trailers) > 0:
            response = {
                "Message": "Trailers Retrieved Successfully",
                "Trailers": trailers,
            }
        else:
            response = {"Message": "There are no Trailers for now"}
        return Response(response, status=status.HTTP_200_OK)


class TrailerRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TrailerSerializer
    renderer_classes = (JsnRenderer,)
    permission_classes = (IsTransporterEmployee,)

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Trailer.objects.all()

        if user.is_superuser == False:
            company = user.employer
            transporter = TransporterCompany.objects.get(company=company).pk
            return Trailer.active_objects.get_personal_assets(owned_by=transporter)

    def retrieve(self, request, pk):
        trailer = self.get_object()
        self.check_object_permissions(request, trailer)
        serialize = self.serializer_class(trailer)
        respose = {
            "Message": "Trailer Successfully Retrieved",
            "Trailer": serialize.data,
        }

        return Response(respose, status=status.HTTP_200_OK)

    def update(self, request, **kwargs):
        """ Amend Trailer """
        trailer = self.get_object()
        self.check_object_permissions(request, trailer)
        data = request.data.copy()
        kwargs["partial"] = True
        data.pop("is_deleted", None)
        data.pop("owned_by", None)
        serializer = self.serializer_class(trailer, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        response = {
            "Trailer": serializer.data,
            "Message": "Trailer updated successfully",
        }
        return Response(response, status=status.HTTP_200_OK)

    def destroy(self, request, pk):
        """ Delete a trailer """
        obj = self.get_object()
        self.check_object_permissions(request, obj)
        obj.soft_delete(commit=True)
        return Response(status.HTTP_204_NO_CONTENT)
