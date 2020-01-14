from rest_framework import generics, status
from companies.models import TransporterCompany
from .models import Driver
from .serializers import DriverSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from utils.permissions import IsTransporterOrAdmin

    
class DriverListCreateView(generics.ListCreateAPIView):
    serializer_class = DriverSerializer
    permission_classes = (IsTransporterOrAdmin,)

    def get_queryset(self,):
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
            "message": f'Driver succesfully craeted. Login credentials have been sent to {email}'

        }

        return Response(response, status=status.HTTP_201_CREATED)

        