from django.shortcuts import render, get_object_or_404
from rest_framework.response import Response
from utils.renderers import JsnRenderer
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.renderers import JSONRenderer
from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.parsers import MultiPartParser, FormParser

from utils.permissions import IsTransporterOrAdmin
from companies.models import TransporterCompany, PersonOfContact
from companies.serializers import TransporterSerializer, PersonofContactSerializer, CargoOwnerSerializer


class TransporterRegistrationAPIView(APIView):
    '''register transporter and its company once'''
    permission_classes = (AllowAny,)
    renderer_classes = (JsnRenderer, )
    serializer_class = TransporterSerializer
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        transporter = serializer.data

        response = {
            "transporter": dict(transporter),
            "message": "Transporter registration request sent, wait for your account to be varified"

        }

        return Response(response, status=status.HTTP_201_CREATED)


class CargoOwnerRegistrationAPIView(APIView):
    '''register cargo owner and its company once'''
    permission_classes = (AllowAny,)
    renderer_classes = (JsnRenderer, )
    serializer_class = CargoOwnerSerializer
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        cargoOwner = serializer.data

        response = {
            "transporter": dict(cargoOwner),
            "message": "cargo owner registration request sent, wait for your account to be varified"

        }

        return Response(response, status=status.HTTP_201_CREATED)

class CreatePersonOfContact(generics.ListCreateAPIView):
    serializer_class = PersonofContactSerializer
    permission_classes = (IsTransporterOrAdmin,)

    def get_queryset(self):
        """
        Override queryset to return objects that are not partially 
        deleted to the transporter and all to admin
        """
        user = self.request.user
        transporter = TransporterCompany.active_objects.get(company_director=user).pk
        if user.is_authenticated and str(user.role) == 'superuser':
            return PersonOfContact.objects.all()
        return PersonOfContact.active_objects.get_person_of_contact(company=transporter)
    
    def create(self, request, *args, **kwargs):
        company = TransporterCompany.active_objects.get(company_director=request.user).pk
        data = request.data.copy()
        data['company'] = company
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        response = {
            'Person of Contact' : dict(serializer.data),
            "message" : "Person of Contact has been created successfully",
        }
        return Response(response, status=status.HTTP_201_CREATED)
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        response = {
            "Persons of contact" : serializer.data,
            "Message" : "Successfully returned your persons of contact"
        }
        return Response(response, status=status.HTTP_200_OK)
        
class PersonOfContactRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PersonofContactSerializer
    permission_classes = (IsTransporterOrAdmin,)

    def get_queryset(self):
        """
        Override queryset to return objects that are not partially 
        deleted to the transporter and all to admin
        """
        user = self.request.user
        transporter = TransporterCompany.active_objects.get(company_director=user).pk
        if user.is_authenticated and str(user.role) == 'superuser':
            return PersonOfContact.objects.all()
        return PersonOfContact.active_objects.get_person_of_contact(company=transporter)

    # getting a single person of contact
    def retrieve(self, request, pk):
        person_of_contact = self.get_object()
        serializer = self.serializer_class(person_of_contact)
        response = {
            "Message" : "Persons of contact returned successfully",
            "Persons of Conact" : serializer.data,
        }
        return Response(response, status=status.HTTP_200_OK)

    # updating a single person of contact
    def put(self, request, pk):
        obj = get_object_or_404(self.get_queryset(), pk=self.kwargs['pk'])
        self.check_object_permissions(self.request, obj)
        data = request.data
        data.pop('company', None)
        serializer = self.serializer_class(obj, data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        response = {
            "Message" : "Person of contact updated successfully",
            "Person of Conact" : serializer.data
        }
        return Response(response, status=status.HTTP_200_OK)

    # self delete a person of contact
    def delete(self, request, pk):
        obj = get_object_or_404(self.get_queryset(), pk=self.kwargs['pk'])
        self.check_object_permissions(self.request, obj)
        obj.soft_delete(commit=True)
        response = {"Message" : "Person of contact has been successfully deleted"}
        return Response(response, status=status.HTTP_200_OK)