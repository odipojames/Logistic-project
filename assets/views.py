from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response

from .serializers import TrucksCsvSerializer, TrailersCsvSerializer, TruckSerializer, TrailerSerializer
from .models import Truck, Trailer
from companies.models import TransporterCompany, Company
from utils.renderers import JsnRenderer
from utils.permissions import IsTransporterOrAdmin, IsAdminOrAssetOwner
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
    renderer_classes = (JsnRenderer, )
    permission_classes = (IsAuthenticated, IsTransporterOrAdmin,)

    def get_queryset(self):

        user = self.request.user
        if str(user.role) == "transporter-director":
            company = Company.objects.get(company_director=user)
            transporter = TransporterCompany.active_objects.get(
                company=company).pk
            return Truck.active_objects.filter(owned_by=transporter)

        if str(user.role) == "admin" or str(user.role) == "staff":
            company = user.employer
            transporter = TransporterCompany.active_objects.get(
                company=company).pk
            return Truck.active_objects.filter(owned_by=transporter)

        if user.is_superuser:
            return Truck.objects.all()

    def create(self, request):
        user = self.request.user
        if str(user.role) == "transporter-director":
            company = Company.objects.get(company_director=user)
        if str(user.role) == "admin":
            company = user.employer
        owned_by = TransporterCompany.active_objects.get(
            company=company).pk

        data = request.data.copy()
        data['owned_by'] = owned_by
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        truck = serializer.data

        response = {
            "truck": dict(truck),
            "message": "Truck succesfully created"

        }

        return Response(response, status=status.HTTP_201_CREATED)

    def list(self, request):
        queryset = self.get_queryset()
        serialize = self.serializer_class(
            queryset, many=True)

        trucks = serialize.data
        if len(trucks) > 0:
            response = {
                "Message": "Trucks Retrieved Successfully",
                "Trucks": trucks
            }
        else:
            response = {"Message": "There are no Trucks for now"}
        return Response(response, status=status.HTTP_200_OK)


class TruckRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TruckSerializer
    renderer_classes = (JsnRenderer, )
    permission_classes = (IsAuthenticated, IsAdminOrAssetOwner,)

    def get_queryset(self):
        user = self.request.user

        user = self.request.user
        if str(user.role) == "transporter-director":
            company = Company.objects.get(company_director=user)
            transporter = TransporterCompany.active_objects.get(
                company=company).pk
            return Truck.active_objects.filter(owned_by=transporter)

        if str(user.role) == "admin" or str(user.role) == "staff":
            company = user.employer
            transporter = TransporterCompany.active_objects.get(
                company=company).pk
            return Truck.active_objects.filter(owned_by=transporter)

        if user.is_superuser:
            return Truck.objects.all()

    def retrieve(self, request, pk):
        truck = self.get_object()
        serialize = self.serializer_class(truck,)
        respose = {
            "Message": "Truck Successfully Retrieved",
            "Truck": serialize.data
        }

        return Response(respose, status=status.HTTP_200_OK)

    def update(self, request, **kwargs):
        """ Amend Truck """
        obj = self.get_object()
        self.check_object_permissions(request, obj)
        kwargs['partial'] = True
        data = request.data.copy()
        data.pop("is_deleted", None)
        data.pop("owned_by", None)
        serializer = self.serializer_class(
            obj, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        response = {
            "Truck": serializer.data,
            "Message": "Truck updated successfully"
        }
        return Response(response, status=status.HTTP_200_OK)

    def destroy(self, request, pk):
        """ Delete a truck """
        truck = self.get_object()
        self.check_object_permissions(request, truck)
        truck.soft_delete(commit=True)

        response = {
            "message": "Truck deleted successfully"
        }

        return Response(response, status=status.HTTP_200_OK)


class TrailerListCreateAPIView(generics.ListCreateAPIView):
    ''' Transporter or admin can create trailers'''
    serializer_class = TrailerSerializer
    renderer_classes = (JsnRenderer, )
    permission_classes = (IsTransporterOrAdmin,)

    def get_queryset(self):
        user = self.request.user
        if str(user.role) == "transporter-director":
            company = Company.objects.get(company_director=user)
        if str(user.role) == "admin" or str(user.role) == "staff":
            company = user.employer
        transporter = TransporterCompany.active_objects.get(
            company=company).pk

        if user.role == "superuser":
            return Trailer.objects.all()
        return Trailer.active_objects.get(owned_by=transporter)

    def create(self, request):
        owned_by = TransporterCompany.active_objects.get(
            company_director=request.user).pk

        data = request.data.copy()
        data['owned_by'] = owned_by
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        trailer = serializer.data

        response = {
            "trailer": dict(trailer),
            "message": "Trailer succesfully created"

        }

        return Response(response, status=status.HTTP_201_CREATED)

    def list(self, request):
        queryset = self.get_queryset()
        serialize = self.serializer_class(
            queryset, many=True)

        trailers = serialize.data
        if len(trailers) > 0:
            response = {
                "Message": "Trailers Retrieved Successfully",
                "Trailers": trailers
            }
        else:
            response = {"Message": "There are no Trailers for now"}
        return Response(response, status=status.HTTP_200_OK)


class TrailerRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TrailerSerializer
    renderer_classes = (JsnRenderer, )
    permission_classes = (IsAdminOrAssetOwner,)

    def get_queryset(self):
        user = self.request.user
        if str(user.role) == "transporter-director":
            company = Company.objects.get(company_director=user)
        if str(user.role) == "admin" or str(user.role) == "staff":
            company = user.employer
        transporter = TransporterCompany.active_objects.get(
            company=company).pk

        if user.role == "superuser":
            return Trailer.objects.all()
        return Trailer.active_objects.get(owned_by=transporter)

    def retrieve(self, request, pk):
        trailer = self.get_object()
        self.check_object_permissions(request, trailer)
        serialize = self.serializer_class(trailer)
        respose = {
            "Message": "Trailer Successfully Retrieved",
            "Trailer": serialize.data
        }

        return Response(respose, status=status.HTTP_200_OK)

    def update(self, request, pk):
        """ Amend Trailer """
        trailer = self.get_object()
        self.check_object_permissions(request, trailer)
        data = request.data.copy()
        data.pop("is_deleted", None)
        data.pop("owned_by", None)
        serializer = self.serializer_class(
            trailer, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        response = {
            "Trailer": serializer.data,
            "Message": "Trailer updated successfully"
        }
        return Response(response, status=status.HTTP_200_OK)

    def destroy(self, request, pk):
        """ Delete a trailer """
        trailer = self.get_object()
        self.check_object_permissions(request, trailer)
        trailer.soft_delete(commit=True)

        response = {
            "message": "Trailer deleted successfully"
        }

        return Response(response, status=status.HTTP_200_OK)
