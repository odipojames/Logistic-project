from django.shortcuts import render, get_object_or_404
from rest_framework import generics, status
from rest_framework.response import Response

from utils.permissions import IsAdminOrCargoOwner, IsAdminOrCargoOwnerRates
from rates.models import Rate
from rates.serializers import RateSerializer
from companies.models import CargoOwnerCompany, Company
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import JSONRenderer


class ListRates(generics.ListCreateAPIView):
    serializer_class = RateSerializer
    permission_classes = (IsAuthenticated, IsAdminOrCargoOwner)
    renderer_classes = (JSONRenderer,)

    def get_queryset(self):
        """
        override queryset to return only objects that are not
        partially deleted to cargo owner and all to admin
        """
        user = self.request.user
        company_instance = user.employer
        company = CargoOwnerCompany.active_objects.get(company=company_instance).pk
        if user.is_authenticated and str(user.role) == "superuser":
            return Rate.objects.all()
        return Rate.active_objects.get_rates(created_by=company)

    def create(self, request, *args, **kwargs):
        company = self.request.user.employer
        created_by = CargoOwnerCompany.active_objects.get(company=company).pk
        data = request.data.copy()
        data["created_by"] = created_by
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        response = {
            "rates": dict(serializer.data),
            "message": "Rates successfully created",
        }
        return Response(response, status=status.HTTP_201_CREATED)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        response = {
            "rates": serializer.data,
            "Message": "Successfully returned your rates",
        }
        return Response(response, status=status.HTTP_200_OK)


class RetrieveUpdateDeleteRates(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = RateSerializer
    permission_classes = (IsAuthenticated, IsAdminOrCargoOwnerRates)
    renderer_classes = (JSONRenderer,)

    def get_queryset(self):
        """
        override queryset to return only objects that are partially deleted to
        cargo owner and all to admin
        """
        user = self.request.user
        company = user.employer
        cargo_company = CargoOwnerCompany.active_objects.get(company=cargo_company)
        if user.is_authenticated and str(user.role) == "superuser":
            return Rate.objects.all()
        return Rate.active_objects.get_rates(created_by=cargo_company)

    # get a single rate and serialize it
    def retrieve(self, request, pk):
        rates = self.get_object()
        serializer = self.serializer_class(rates)
        response = {"Message": "rates returned successfully", "rates": serializer.data}
        return Response(response, status=status.HTTP_200_OK)

    # updating a single rate
    def put(self, request, pk):
        obj = get_object_or_404(self.get_queryset(), pk=self.kwargs["pk"])
        self.check_object_permissions(self.request, obj)
        data = request.data
        data.pop("created_by", None)
        serializer = self.serializer_class(obj, data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        response = {"Message": "updated successfully", "rate": serializer.data}
        return Response(response, status=status.HTTP_200_OK)

    # soft delete a rate
    def delete(self, request, pk):
        obj = get_object_or_404(self.get_queryset(), pk=self.kwargs["pk"])
        self.check_object_permissions(self.request, obj)
        obj.soft_delete(commit=True)
        response = {"Message": "The rate has been deleted successfully"}
        return Response(response, status=status.HTTP_200_OK)
