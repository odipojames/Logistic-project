from django.shortcuts import render, get_object_or_404
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView

from utils.permissions import IsCargoOwner, IsShyperAdmin
from orders.serializers import OrderSerializer
from orders.models import Order
from companies.models import CargoOwnerCompany
from depots.models import Depot
from cargo_types.models import Commodity
import math


class ListCreateOrder(ListCreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = (IsCargoOwner | IsShyperAdmin,)

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated and str(user.role) == "superuser":
            return Order.active_objects.all()
        if user.is_authenticated and str(user.role) != "superuser":
            company = user.employer
            cargo_owner = CargoOwnerCompany.objects.get(company=company).pk
            return Order.active_objects.get_order(owner=cargo_owner)

    def post(self, request, format=None):
        user = self.request.user
        data = request.data.copy()
        if user.is_superuser == False:
            company = user.employer
            cargo_owner = CargoOwnerCompany.objects.get(company=company).pk
            data["owner"] = cargo_owner
        context = {"request": request}
        if data["commodity"]:
            commodity = Commodity.objects.get(id=data["commodity"])
            cargo_type = commodity.cargo_type
            if str(cargo_type).lower() != "container":
                data["number_of_containers"] = math.ceil(
                    int(data["cargo_tonnage"]) / 28
                )
        serializer = self.serializer_class(data=data, context=context)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        response = {
            "order": dict(serializer.data),
            "message": "Orders successfully created",
        }
        return Response(response, status=status.HTTP_201_CREATED)


class RetrieveUpdateDeleteOrder(RetrieveUpdateDestroyAPIView):
    serializer_class = OrderSerializer
    permission_classes = (IsCargoOwner | IsShyperAdmin,)
    multiple_lookup_fields = ["tracking_id"]

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated and str(user.role) == "superuser":
            return Order.active_objects.all()
        if (
            user.is_authenticated
            and str(user.role) == "cargo-owner-director"
            or str(user.role) == "admin"
        ):
            company = user.employer
            cargo_owner = CargoOwnerCompany.objects.get(company=company).pk
            return Order.active_objects.get_order(owner=cargo_owner)

    def get_object(self):
        queryset = self.get_queryset()
        filter = {}
        for field in self.multiple_lookup_fields:
            filter[field] = self.kwargs[field]

        obj = get_object_or_404(queryset, **filter)
        self.check_object_permissions(self.request, obj)
        return obj

    def retrieve(self, request, tracking_id):
        order = self.get_object()
        serializer = self.serializer_class(order)
        response = {
            "Order": serializer.data,
            "Message": "Order details returned successfully",
        }
        return Response(response, status.HTTP_200_OK)

    def put(self, request, tracking_id):
        obj = self.get_object()
        data = request.data
        data.pop("owner", None)
        serializer = self.serializer_class(obj, data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        response = {
            "Order": serializer.data,
            "Message": "Order has been updated successfully",
        }
        return Response(response, status.HTTP_200_OK)

    def delete(self, request, tracking_id):
        obj = self.get_object()
        obj.soft_delete(commit=True)
        response = {"Message": "Order has been deleted successfully"}
        return Response(response, status.HTTP_200_OK)
