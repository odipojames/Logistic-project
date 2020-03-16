from django.shortcuts import render
from .models import Depot
from .serializers import DepotSerializer
from django.shortcuts import get_object_or_404
from utils.permissions import IsAdminOrCargoOwner, IsAdminOrReadOnly
from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from utils.renderers import JsnRenderer


# Create your views here.


class DepotList(generics.ListCreateAPIView):
    """creating depots"""

    permission_classes = [IsAuthenticated]
    permission_classes = (IsAdminOrCargoOwner,)
    serializer_class = DepotSerializer
    renderer_classes = (JsnRenderer,)

    def get_queryset(self):
        """overide queryset to return owner created depots and public depots only"""
        user = self.request.user
        if user.is_authenticated and str(user.role) == "superuser":
            return Depot.active_objects.all()
        return Depot.active_objects.get_depot(
            user=user
        ) | Depot.active_objects.get_public(is_public=True)

    def post(self, request, format=None):
        data = request.data.copy()
        data["user"] = request.user.pk
        if str(request.user.role) == "cargo-owner":
            # make the depot private when created by cargo owners
            data["is_public"] = False
        if str(request.user.role) == "superuser":
            # make all depots created by admin be public to all cargo owners
            data["is_public"] = True
        serializers = self.serializer_class(data=data)
        serializers.is_valid(raise_exception=True)
        serializers.save()
        response = {"depot": serializers.data, "message": "depot created succesfully"}
        return Response(response, status.HTTP_201_CREATED)


class DepotRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    """retrival,deleting and updating depots"""

    permission_classes = (IsAdminOrCargoOwner | IsAdminOrReadOnly,)
    serializer_class = DepotSerializer
    renderer_classes = (JsnRenderer,)

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated and str(user.role) == "superuser":
            return Depot.active_objects.all()
        return Depot.active_objects.get_depot(
            user=user
        ) | Depot.active_objects.get_public(is_public=True)

    def retrieve(self, request, pk):
        depot = self.get_object()
        serializer = self.serializer_class(depot)
        response = {"message": "depot retrieved", "depot details": serializer.data}
        return Response(response, status.HTTP_200_OK)

    # updates a single depot
    def put(self, request, pk):
        obj = get_object_or_404(self.get_queryset(), pk=self.kwargs["pk"])
        self.check_object_permissions(self.request, obj)
        data = request.data
        data.pop("user")
        serializer = self.serializer_class(obj, data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        response = {"depot": serializer.data, "message": "updated succesfully"}
        return Response(response)

    # soft deletes a depot
    def delete(self, request, pk):
        obj = get_object_or_404(self.get_queryset(), pk=self.kwargs["pk"])
        self.check_object_permissions(self.request, obj)
        obj.soft_delete(commit=True)
        response = {"message": "depot  deleted succesfully!"}
        return Response(response, status.HTTP_200_OK)
