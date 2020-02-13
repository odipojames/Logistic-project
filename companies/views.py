from django.shortcuts import render, get_object_or_404
from rest_framework.response import Response
from utils.renderers import JsnRenderer
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.renderers import JSONRenderer
from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.generics import RetrieveUpdateAPIView, ListAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.parsers import MultiPartParser, FormParser
from utils.permissions import IsTransporterOrAdmin, IsShyperAdmin, IsAdminOrCompanyOwner, IsCargoOwner, IsComponyAdminOrDirector
from companies.models import TransporterCompany, PersonOfContact, CargoOwnerCompany, TransporterCompany, Company
from companies.serializers import TransporterSerializer, PersonofContactSerializer, CargoOwnerSerializer, EmployeeSerializer
from authentication.models import User, Role
from django.core.mail import send_mail
from logisticts.settings import EMAIL_HOST_USER
from django.contrib.auth.base_user import BaseUserManager
from django.forms.models import model_to_dict


class TransporterCompanyListAPIView(generics.ListCreateAPIView):
    """register transporter and its company once"""
    queryset = TransporterCompany.objects.all()
    serializer_class = TransporterSerializer
    renderer_classes = (JsnRenderer, )

    def list(self, request):
        permission_classes = (IsShyperAdmin, )
        queryset = self.get_queryset()
        serialize = self.serializer_class(
            queryset, many=True)

        companies = serialize.data
        if len(companies) > 0:
            response = {
                "Message": "Companies Retrieved Successfully",
                "Companies": companies
            }
        else:
            response = {"Message": "There are no companies for now"}
        return Response(response, status=status.HTTP_200_OK)


class CargoOwnerCompanyListAPIView(generics.ListCreateAPIView):
    """register cargo owner and its company once"""
    queryset = CargoOwnerCompany.objects.all()
    serializer_class = CargoOwnerSerializer
    renderer_classes = (JsnRenderer, )

    def list(self, request):
        permission_classes = (IsShyperAdmin, )
        queryset = self.get_queryset()
        serialize_companies = self.serializer_class(
            queryset, many=True)

        companies = serialize_companies.data
        if len(companies) > 0:
            response = {
                "Message": "Companies Retrieved Successfully",
                "Companies": companies
            }
        else:
            response = {"Message": "There are no companies for now"}
        return Response(response, status=status.HTTP_200_OK)


class CargoOwnerCompanyRetrieveUpdateDestroy(RetrieveUpdateDestroyAPIView):
    """
    Handle retrieving, updating or deletion of cargo owner companies
    Only the Cargo Owner can crud its company
    """
    serializer_class = CargoOwnerSerializer
    renderer_classes = (JsnRenderer, )
    permission_classes = (IsAdminOrCompanyOwner, )

    def get_queryset(self):

        return CargoOwnerCompany.active_objects.all_objects()

    def retrieve(self, request, pk):
        company = self.get_object()
        self.check_object_permissions(request, company)
        serialized_company = self.serializer_class(company)
        respose = {
            "Message": "Company Successfully Retrieved",
            "Company": serialized_company.data
        }

        return Response(respose, status=status.HTTP_200_OK)

    def update(self, request, pk):
        """ Update an existing company """
        company = self.get_object()
        self.check_object_permissions(request, company)
        data_to_update = request.data
        serializer = self.serializer_class(
            company, data=data_to_update, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        response = {
            "Company": serializer.data,
            "Message": "Company updated successfully"
        }
        return Response(response, status=status.HTTP_200_OK)

    def destroy(self, request, pk):
        """ Delete the company with the corresponding company director """
        company = self.get_object()
        self.check_object_permissions(request, company)
        company.is_active = False
        company.soft_delete(commit=True)
        company.company_director.is_active = False
        company.company_director.soft_delete(commit=True)

        response = {
            "message": "Company deleted successfully"
        }

        return Response(response, status=status.HTTP_200_OK)


class TransporterCompanyRetrieveUpdateDestroy(RetrieveUpdateDestroyAPIView):
    """
    Handle retrieving, updating or deletion of transporter companies
    Only the Transporter can crud its company
    """
    serializer_class = TransporterSerializer
    renderer_classes = (JsnRenderer, )
    permission_classes = [IsAuthenticated]
    permission_classes = (IsAdminOrCompanyOwner, )

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated and str(user.role) == "superuser":
            return TransporterCompany.objects.all()
        return TransporterCompany.active_objects.all_objects()

    def retrieve(self, request, pk):
        company = self.get_object()
        self.check_object_permissions(request, company)
        serialize = self.serializer_class(company)
        respose = {
            "Message": "Company Successfully Retrieved",
            "Company": serialize.data
        }

        return Response(respose, status=status.HTTP_200_OK)

    def update(self, request, pk):
        """ Update an existing company """
        company = self.get_object()
        self.check_object_permissions(request, company)
        data_to_update = request.data
        serializer = self.serializer_class(
            company, data=data_to_update, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        response = {
            "Company": serializer.data,
            "Message": "Company updated successfully"
        }
        return Response(response, status=status.HTTP_200_OK)

    def destroy(self, request, pk):
        """ Delete the company with the corresponding company director """
        company = self.get_object()
        self.check_object_permissions(request, company)
        company.is_active = False
        company.soft_delete(commit=True)
        company.company_director.is_active = False
        company.company_director.soft_delete(commit=True)

        response = {
            "message": "Company deleted successfully"
        }

        return Response(response, status=status.HTTP_200_OK)


class CreatePersonOfContact(generics.ListCreateAPIView):
    serializer_class = PersonofContactSerializer
    permission_classes = (IsCargoOwner | IsShyperAdmin, IsAuthenticated)

    def get_queryset(self):
        """
        Override queryset to return objects that are not partially
        deleted to the transporter and all to admin
        """
        user = self.request.user
        cargo_owner = CargoOwnerCompany.active_objects.get(
            company_director=user).pk
        if user.is_authenticated and str(user.role) == 'superuser':
            return PersonOfContact.objects.all()
        return PersonOfContact.active_objects.get_person_of_contact(company=cargo_owner)

    def create(self, request, *args, **kwargs):
        company = CargoOwnerCompany.active_objects.get(
            company_director=request.user).pk
        data = request.data.copy()
        data['company'] = company
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        response = {
            'Person of Contact': dict(serializer.data),
            "message": "Person of Contact has been created successfully",
        }
        return Response(response, status=status.HTTP_201_CREATED)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        response = {
            "Persons of contact": serializer.data,
            "Message": "Successfully returned your persons of contact"
        }
        return Response(response, status=status.HTTP_200_OK)


class PersonOfContactRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PersonofContactSerializer
    permission_classes = (IsCargoOwner | IsShyperAdmin, IsAuthenticated)

    def get_parsers(self):
        if getattr(self, 'swagger_fake_view', False):
            return []

        return super().get_parsers()

    def get_queryset(self):
        """
        Override queryset to return objects that are not partially
        deleted to the transporter and all to admin
        """
        user = self.request.user
        company = Company.active_objects.get(company_director=user)
        cargo_owner = CargoOwnerCompany.active_objects.get(company=company).pk
        if user.is_authenticated and str(user.role) == 'superuser':
            return PersonOfContact.objects.all()
        return PersonOfContact.active_objects.get_person_of_contact(company=cargo_owner)

    # getting a single person of contact
    def retrieve(self, request, pk):
        person_of_contact = self.get_object()
        serializer = self.serializer_class(person_of_contact)
        response = {
            "Message": "Persons of contact returned successfully",
            "Persons of Conact": serializer.data,
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
            "Message": "Person of contact updated successfully",
            "Person of Conact": serializer.data
        }
        return Response(response, status=status.HTTP_200_OK)

    # self delete a person of contact
    def delete(self, request, pk):
        obj = get_object_or_404(self.get_queryset(), pk=self.kwargs['pk'])
        self.check_object_permissions(self.request, obj)
        obj.soft_delete(commit=True)
        response = {
            "Message": "Person of contact has been successfully deleted"}
        return Response(response, status=status.HTTP_200_OK)


class EmployeeListCreateAPIView(generics.ListCreateAPIView):
    """create company employer"""
    serializer_class = EmployeeSerializer
    renderer_classes = (JsnRenderer, )
    permission_classes = (IsAuthenticated, IsComponyAdminOrDirector)

    def get_queryset(self):
        user = self.request.user
        if str(user.role) == 'transporter-director' or str(user.role) == 'cargo-owner-director':
            company = Company.objects.get(company_director=user)
            return company.employees.filter(is_deleted=False)
        if str(user.role)=='admin':
            company = user.employer
            return company.employees.filter(is_deleted=False)

        if str(user.role) == 'superuser':
            for c in Company.objects.all():
                return c.employees.all()

    def post(self, request, format=None):
        user = self.request.user
        if str(user.role) =="admin":
            company = user.employer
        else:
            company = Company.objects.get(company_director=user)
        data = request.data.copy()
        data['employer'] = company.pk
        password = BaseUserManager().make_random_password(
            10)  # generate random password for the user
        data['password'] = password
        email = data['email']
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        subject = f"{company} new employee"
        message = f"Your  account has been created by {company}. Login credentials are \n Your email is : {email} \n password: {password}"
        from_email = EMAIL_HOST_USER
        recipient_list = [email]

        # sends authentication credentials to employee's email
        send_mail(subject, message, from_email,
                  recipient_list, fail_silently=False)
        response = {
            "message": "employee added succesfully",
            "employee": serializer.data

        }
        return Response(response, status.HTTP_201_CREATED)


class EmployeeRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    """singl employes retrival updates and destroy"""
    serializer_class = EmployeeSerializer
    renderer_classes = (JsnRenderer, )
    permission_classes = (IsAuthenticated, IsComponyAdminOrDirector)

    def get_queryset(self):
        user = self.request.user
        if str(user.role) == 'transporter-director' or str(user.role) == 'cargo-owner-director':
            company = Company.objects.get(company_director=user)
            return company.employees.filter(is_deleted=False)

        if str(user.role)=='admin':
            company = user.employer
            return company.employees.filter(is_deleted=False)

        if str(user.role) == 'superuser':
            for c in Company.objects.all():
                return c.employees.all()


    def retrieve(self, request, pk):
        employee = self.get_object()
        serializer = self.serializer_class(employee,)
        response = {
            "message": "employee succesfully retrieved ",
            "employee": serializer.data
        }
        return Response(response, status.HTTP_200_OK)

    def update(self, request, **kwargs):
        obj = get_object_or_404(self.get_queryset(), pk=self.kwargs["pk"])
        self.check_object_permissions(self.request, obj)
        kwargs['partial'] = True
        data = request.data
        data.pop('employer',None)
        data.pop('password',None)
        data.pop('role',None)  # TODO: update role
        #role_instance = Role.active_objects.get_or_create(title=role)[0]
        #data['role'] = role_instance
        serializer = self.serializer_class(
            obj, data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        response = {
            "message": "employee data succesfully updated",
            "employee": serializer.data

        }
        return Response(response, status.HTTP_200_OK)

    def destroy(self, request, pk):
        obj = self.get_object()
        obj.is_active = False
        obj.soft_delete(commit=True)
        return Response(status.HTTP_204_NO_CONTENT)
