from django.shortcuts import render, get_object_or_404
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView

from utils.permissions import IsCargoOwner, IsShyperAdmin
from orders.serializers import OrderSerializer
from orders.models import Order
from companies.models import CargoOwnerCompany
from depots.models import Depot


class ListCreateOrder(ListCreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = (IsCargoOwner | IsShyperAdmin,)

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated and str(user.role) == "superuser":
            return Order.active_objects.all()
        if user.is_authenticated and str(user.role) == "cargo-owner":
            cargo_owner = CargoOwnerCompany.objects.get(company_director=user).pk
            return Order.active_objects.get_order(owner=cargo_owner)

    def post(self, request, format=None):
        user = self.request.user
        data = request.data.copy()
        cargo_owner = CargoOwnerCompany.objects.get(company_director=user).pk
        data["owner"] = cargo_owner
        context = {"request": request}
        serializer = self.serializer_class(data=data, context=context)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        response = {
            "order": dict(serializer.data),
            "message": "Orders successfully created",
        }
        return Response(response, status=status.HTTP_200_OK)


class RetrieveUpdateDeleteOrder(RetrieveUpdateDestroyAPIView):
    serializer_class = OrderSerializer
    permission_classes = (IsCargoOwner | IsShyperAdmin,)
    multiple_lookup_fields = ["tracking_id"]

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated and str(user.role) == "superuser":
            return Order.active_objects.all()
        if user.is_authenticated and str(user.role) == "cargo-owner":
            cargo_owner = CargoOwnerCompany.objects.get(company_director=user).pk
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
