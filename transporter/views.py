from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from utils.permissions import IsTransporterOrAdmin
from companies.models import TransporterCompany
from .models import Driver
from .serializers import DriverSerializer


    
class DriverListCreateView(generics.ListCreateAPIView):
    serializer_class = DriverSerializer
    permission_classes = (IsTransporterOrAdmin,)

    def get_queryset(self):
        """ return different results depending on who is making a request """
        user = self.request.user
        
        if str(user.role) == "superuser":
            return Driver.active_objects.all()

        if str(user.role) == "transporter":
            transporter = TransporterCompany.active_objects.get(company_director=self.request.user).pk
        
            return Driver.active_objects.for_transporter(company=transporter) 
           
    def create(self, request, **kwargs):
        transporter = TransporterCompany.active_objects.get(company_director=request.user).pk
        
        data = request.data.copy()
        data['company'] = transporter
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        email = serializer.data.get('user').get('email')

        response = {
            "transporter": dict(serializer.data),
            "message": f'Driver succesfully created. Login credentials have been sent to {email}'

        }

        return Response(response, status=status.HTTP_201_CREATED)


class DriverDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    This class defines the views for retreiving, updating and destroying a single driver.
    """

    serializer_class = DriverSerializer
    permission_classes = (IsTransporterOrAdmin,)
    lookup_field = 'id'

    def get_queryset(self):
        """
        Superusers can view all drivers. Transporters can only view their drivers.
        """

        user = self.request.user

        if user.is_superuser:
            return Driver.active_objects.all()
        if str(user.role) == 'transporter':
            company = TransporterCompany.active_objects.get(company_director=user).pk
            return Driver.active_objects.for_transporter(company=company)

    def update(self, request, **kwargs):
        kwargs['partial'] = True
        response = super().update(request, **kwargs)

        # logic for suspending driver.
        suspend = request.data.get('suspend')

        if suspend and suspend.lower() == 'true': 
            obj = self.get_object()
            self.check_object_permissions(request, obj)
            obj.user.is_active = False
            obj.user.save()

        message = "Driver succesfully updated."

        payload = response.data.copy()
        payload['message'] = message

        return Response(payload, status=status.HTTP_200_OK)

    def destroy(self, request, **kwargs):
        """
        Overide the destroy method so that we soft-delete users.
        """

        obj = self.get_object()
        self.check_object_permissions(request, obj)

        # soft delete both the driver instance and the user instance
        obj.soft_delete(commit=True)
        obj.user.is_active = False
        obj.user.soft_delete(commit=True)

        return Response(status=status.HTTP_204_NO_CONTENT)
