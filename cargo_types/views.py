from companies.models import CargoOwnerCompany
from django.shortcuts import get_object_or_404
from utils.permissions import IsAdminOrCargoOwner, IsAdminOrReadOnly
from .models import CargoType, Commodity
from rest_framework.exceptions import NotFound
from django.http import Http404
from django.shortcuts import render
from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from utils.renderers import JsnRenderer
from .serializers import CargoTypeSerializer, CommoditySerializer


# Create your views here.


class CargoTypeList(generics.ListCreateAPIView):
    """
    view to handle cargo type CRUD
    """

    renderer_classes = (JsnRenderer,)
    serializer_class = CargoTypeSerializer
    permission_classes = (IsAuthenticated, IsAdminOrReadOnly)

    def get_queryset(self):
        """
        overide query set return only unsoft deleted objects to cargo owner and all to Admin
        """
        user = self.request.user
        if user.is_authenticated and str(user.role) == "superuser":
            return CargoType.active_objects.all()
        return CargoType.active_objects.all_objects()

    def post(self, request, format=None):
        serializers = self.serializer_class(data=request.data)
        serializers.is_valid(raise_exception=True)
        serializers.save()
        response = {
            "cargo types": serializers.data,
            "message": "cargo type created succesfully",
        }
        return Response(response, status=status.HTTP_201_CREATED)


class CargoTypeRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    """
    class that retrieves update and destroys cargo types
    """

    renderer_classes = (JsnRenderer,)
    serializer_class = CargoTypeSerializer
    permission_classes = (IsAuthenticated, IsAdminOrReadOnly)

    def get_queryset(self):
        """
        overide query set return only unsoft deleted objects to cargo owner and all to Admin
        """
        user = self.request.user
        if user.is_authenticated and str(user.role) == "superuser":
            return CargoType.objects.all()
        return CargoType.active_objects.all_objects()

    # get the details of a particular item
    def retrieve(self, request, pk):

        type = self.get_object()
        serializer = self.serializer_class(type)
        response = {
            "Message": "cargo type details returned successfully",
            "Cargo-Type_details": serializer.data,
        }

        return Response(response, status=status.HTTP_200_OK)

    # updating particular cargo type
    def put(self, request, pk, format=None):

        obj = get_object_or_404(self.get_queryset(), pk=self.kwargs["pk"])
        self.check_object_permissions(self.request, obj)
        serializer = self.serializer_class(obj, request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        response = {"cargo type": serializer.data, "message": "updated succesfully"}
        return Response(response)

    def delete(self, request, pk):

        obj = get_object_or_404(self.get_queryset(), pk=self.kwargs["pk"])
        self.check_object_permissions(self.request, obj)

        obj.soft_delete(commit=True)
        response = {"message": "cargo type deleted succesfully!"}
        return Response(response, status.HTTP_200_OK)


class CommodityList(generics.ListCreateAPIView):
    """
    view to handle Commodity CRUD
    """

    renderer_classes = (JsnRenderer,)
    serializer_class = CommoditySerializer
    permission_classes = (IsAuthenticated, IsAdminOrCargoOwner)

    def get_queryset(self):
        """
        overide query set return only unsoft deleted objects to cargo owner and all to Admin
        """
        user = self.request.user
        if user.is_authenticated and str(user.role) == "superuser":
            return Commodity.objects.all()

        if user.is_superuser == False:
            company_instance = user.employer
            company = CargoOwnerCompany.active_objects.get(company=company_instance).pk

            return Commodity.active_objects.get_commodity(created_by=company)

    def post(self, request, format=None):
        company = request.user.employer
        cargo_owner = CargoOwnerCompany.active_objects.get(company=company).pk
        data = request.data.copy()
        data["created_by"] = cargo_owner
        serializers = self.serializer_class(data=data)
        serializers.is_valid(raise_exception=True)
        serializers.save()
        response = {
            "commodities": serializers.data,
            "message": "commodity created succesfully",
        }
        return Response(response, status=status.HTTP_201_CREATED)


class CommodityRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    """
    class that retrieves,updates and destroys commodity
    """

    renderer_classes = (JsnRenderer,)
    serializer_class = CommoditySerializer
    permission_classes = (IsAuthenticated, IsAdminOrCargoOwner)

    def get_queryset(self):
        """
        overide query set return only unsoft deleted objects to cargo owner and all to Admin
        """
        user = self.request.user
        company = CargoOwnerCompany.active_objects.get(company_director=user).pk
        if user.is_authenticated and str(user.role) == "superuser":
            return Commodity.objects.all()
        return Commodity.active_objects.get_commodity(created_by=company)

    # get the details of a particular commodity
    def retrieve(self, request, pk):

        commodity = self.get_object()
        serializer = self.serializer_class(commodity)
        response = {
            "Message": "commodity details returned successfully",
            "commodity_details": serializer.data,
        }

        return Response(response, status=status.HTTP_200_OK)

    # updates a single commodity
    def put(self, request, pk):
        obj = get_object_or_404(self.get_queryset(), pk=self.kwargs["pk"])
        self.check_object_permissions(self.request, obj)
        serializer = self.serializer_class(obj, request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        response = {"commodity": serializer.data, "message": "updated succesfully"}
        return Response(response)

    # soft deletes a commodity
    def delete(self, request, pk):
        obj = get_object_or_404(self.get_queryset(), pk=self.kwargs["pk"])
        self.check_object_permissions(self.request, obj)
        obj.soft_delete(commit=True)
        response = {"message": "commodity  deleted succesfully!"}
        return Response(response, status.HTTP_200_OK)
