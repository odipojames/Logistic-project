from django.shortcuts import render, get_object_or_404
from rest_framework.response import Response
from utils.renderers import JsnRenderer
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.renderers import JSONRenderer
from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.generics import (
    RetrieveUpdateAPIView,
    ListAPIView,
    RetrieveUpdateDestroyAPIView,
)
from rest_framework.parsers import MultiPartParser, FormParser
from utils.permissions import (
    IsTransporterOrAdmin,
    IsShyperAdmin,
    IsAdminOrCompanyOwner,
    IsCargoOwner,
    IsComponyAdminOrDirectorOrStaffReadOnly,
    IsShyperEmployee,
)
from companies.models import (
    TransporterCompany,
    PersonOfContact,
    CargoOwnerCompany,
    TransporterCompany,
    Company,
)
from companies.serializers import (
    TransporterSerializer,
    PersonofContactSerializer,
    CargoOwnerSerializer,
    EmployeeSerializer,
    MainCompanySerializer,
)
from authentication.models import User, Role
from django.core.mail import send_mail
from logisticts.settings import EMAIL_HOST_USER
from django.contrib.auth.base_user import BaseUserManager
from drf_yasg.utils import swagger_auto_schema
from utils.helpers import send_sms


class TransporterCompanyListAPIView(generics.ListCreateAPIView):
    """register transporter and its company once"""

    queryset = TransporterCompany.objects.all()
    serializer_class = TransporterSerializer
    renderer_classes = (JsnRenderer,)

    def list(self, request):
        permission_classes = (IsShyperAdmin,)
        queryset = self.get_queryset()
        serialize = self.serializer_class(queryset, many=True)

        companies = serialize.data
        if len(companies) > 0:
            response = {
                "Message": "Companies Retrieved Successfully",
                "Companies": companies,
            }
        else:
            response = {"Message": "There are no companies for now"}
        return Response(response, status=status.HTTP_200_OK)


class CargoOwnerCompanyListAPIView(generics.ListCreateAPIView):
    """register cargo owner and its company once"""

    queryset = CargoOwnerCompany.objects.all()
    serializer_class = CargoOwnerSerializer
    renderer_classes = (JsnRenderer,)

    def list(self, request):
        permission_classes = (IsShyperAdmin,)
        queryset = self.get_queryset()
        serialize_companies = self.serializer_class(queryset, many=True)

        companies = serialize_companies.data
        if len(companies) > 0:
            response = {
                "Message": "Companies Retrieved Successfully",
                "Companies": companies,
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
    renderer_classes = (JsnRenderer,)
    permission_classes = (IsAdminOrCompanyOwner,)

    def get_queryset(self):

        return CargoOwnerCompany.active_objects.all_objects()

    def retrieve(self, request, pk):
        obj = self.get_object()
        serialized_company = self.serializer_class(obj)
        respose = {
            "Message": "Company Successfully Retrieved",
            "Company": serialized_company.data,
        }

        return Response(respose, status=status.HTTP_200_OK)

    def update(self, request, **kwargs):
        """ Update an existing company """
        obj = self.get_object()
        self.check_object_permissions(request, obj)
        kwargs["partial"] = True
        data_to_update = request.data
        company = data_to_update.get("company", None)
        if company:
            company.pop("company_director")
        serializer = self.serializer_class(obj, data=data_to_update, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        response = {
            "Company": serializer.data,
            "Message": "Company updated successfully",
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

        response = {"message": "Company deleted successfully"}

        return Response(response, status=status.HTTP_200_OK)


class TransporterCompanyRetrieveUpdateDestroy(RetrieveUpdateDestroyAPIView):
    """
    Handle retrieving, updating or deletion of transporter companies
    Only the Transporter can crud its company
    """

    serializer_class = TransporterSerializer
    renderer_classes = (JsnRenderer,)
    permission_classes = [IsAuthenticated]
    permission_classes = (IsAdminOrCompanyOwner,)

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated and str(user.role) == "superuser":
            return TransporterCompany.objects.all()
        return TransporterCompany.active_objects.all_objects()

    def retrieve(self, request, pk):
        company = self.get_object()
        serialize = self.serializer_class(company)
        respose = {
            "Message": "Company Successfully Retrieved",
            "Company": serialize.data,
        }

        return Response(respose, status=status.HTTP_200_OK)

    def update(self, request, **kwargs):
        """ Update an existing company """
        obj = self.get_object()
        self.check_object_permissions(request, obj)
        kwargs["partial"] = True
        data_to_update = request.data
        company = data_to_update.get("company", None)
        if company:
            company.pop("company_director", None)
        serializer = self.serializer_class(obj, data=data_to_update, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        response = {
            "Company": serializer.data,
            "Message": "Company updated successfully",
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

        response = {"message": "Company deleted successfully"}

        return Response(response, status=status.HTTP_200_OK)


class PendingCompaniesListAPIView(generics.ListAPIView):
    permission_classes = (IsAuthenticated, IsShyperEmployee)
    serializer_class = MainCompanySerializer
    renderer_classes = (JSONRenderer, JsnRenderer)

    def get_queryset(self):

        return Company.objects.filter(onboarding_status__in=("under_review",))

        def list(self, request, *args, **kwargs):
            queryset = self.get_queryset()
            serializer = self.serializer_class(queryset)
            response = {
                "pennding_companies": serializer.data,
                "message": "pending companies succesfully retrieved",
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
        if user.is_authenticated and str(user.role) == "superuser":
            return PersonOfContact.objects.all()
        if user.is_superuser == False:
            company = user.employer
            cargo_owner = CargoOwnerCompany.active_objects.get(company=company).pk
            return PersonOfContact.active_objects.get_person_of_contact(
                company=cargo_owner
            )

    def create(self, request, *args, **kwargs):
        user = self.request.user
        data = request.data.copy()
        if user.is_superuser == False:
            company = user.employer
            cargo_owner = CargoOwnerCompany.active_objects.get(company=company).pk
            data["company"] = cargo_owner
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        response = {
            "Person of Contact": dict(serializer.data),
            "message": "Person of Contact has been created successfully",
        }
        return Response(response, status=status.HTTP_201_CREATED)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        response = {
            "Persons of contact": serializer.data,
            "Message": "Successfully returned your persons of contact",
        }
        return Response(response, status=status.HTTP_200_OK)


class PersonOfContactRetrieveUpdateDestroyAPIView(
    generics.RetrieveUpdateDestroyAPIView
):
    serializer_class = PersonofContactSerializer
    permission_classes = (IsCargoOwner | IsShyperAdmin, IsAuthenticated)

    def get_parsers(self):
        if getattr(self, "swagger_fake_view", False):
            return []

        return super().get_parsers()

    def get_queryset(self):
        """
        Override queryset to return objects that are not partially
        deleted to the transporter and all to admin
        """
        user = self.request.user
        if user.is_authenticated and str(user.role) == "superuser":
            return PersonOfContact.objects.all()
        if user.is_superuser == False:
            company = user.employer
            cargo_owner = CargoOwnerCompany.active_objects.get(company=company).pk
            return PersonOfContact.active_objects.get_person_of_contact(
                company=cargo_owner
            )

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
        obj = get_object_or_404(self.get_queryset(), pk=self.kwargs["pk"])
        self.check_object_permissions(self.request, obj)
        data = request.data
        data.pop("company", None)
        serializer = self.serializer_class(obj, data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        response = {
            "Message": "Person of contact updated successfully",
            "Person of Conact": serializer.data,
        }
        return Response(response, status=status.HTTP_200_OK)

    # self delete a person of contact
    def delete(self, request, pk):
        obj = get_object_or_404(self.get_queryset(), pk=self.kwargs["pk"])
        self.check_object_permissions(self.request, obj)
        obj.soft_delete(commit=True)
        response = {"Message": "Person of contact has been successfully deleted"}
        return Response(response, status=status.HTTP_200_OK)


class EmployeeListCreateAPIView(generics.ListCreateAPIView):
    """create company employer"""

    serializer_class = EmployeeSerializer
    renderer_classes = (JsnRenderer,)
    permission_classes = (IsAuthenticated, IsComponyAdminOrDirectorOrStaffReadOnly)

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser == False:
            company = user.employer
            return company.employees.filter(is_deleted=False)

        if user.is_superuser:
            companies = []
            for c in Company.objects.all():
                companies.append(c)
                for company in companies:
                    return company.employees.all()

    def post(self, request, format=None):
        user = self.request.user
        data = request.data.copy()
        if user.is_superuser == False:
            company = user.employer
            data["employer"] = company.pk
        password = BaseUserManager().make_random_password(
            10
        )  # generate random password for the user
        data["password"] = password
        email = data["email"]
        phone = data["phone"]
        if data["employer"]:
            company = Company.objects.get(id=data["employer"])
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        subject = f"{company} new employee"
        message = f"Your  account for {company} has been created  . Login credentials are \nYour email is : {email} \n password: {password}"
        from_email = EMAIL_HOST_USER
        recipient_list = [email]

        # sends authentication credentials to employee's email
        send_mail(subject, message, from_email, recipient_list, fail_silently=False)
        # sms notifications
        send_sms(
            message=f"Your  account for {company} has been created . Login credentials are \n Your email is : {email} \n password: {password}",
            recipients=[phone],
        )
        response = {
            "message": "employee added succesfully",
            "employee": serializer.data,
        }
        return Response(response, status.HTTP_201_CREATED)


class EmployeeRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    """singl employes retrival updates and destroy"""

    serializer_class = EmployeeSerializer
    renderer_classes = (JsnRenderer,)
    permission_classes = (IsAuthenticated, IsComponyAdminOrDirectorOrStaffReadOnly)

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser == False:
            company = user.employer
            return company.employees.filter(is_deleted=False)

        if user.is_superuser:
            companies = []
            for c in Company.objects.all():
                companies.append(c)
                for company in companies:
                    return company.employees.all()

    def retrieve(self, request, pk):
        employee = self.get_object()
        serializer = self.serializer_class(employee)
        response = {
            "message": "employee succesfully retrieved ",
            "employee": serializer.data,
        }
        return Response(response, status.HTTP_200_OK)

    @swagger_auto_schema(auto_schema=None)
    def update(self, request, **kwargs):
        obj = get_object_or_404(self.get_queryset(), pk=self.kwargs["pk"])
        self.check_object_permissions(self.request, obj)
        kwargs["partial"] = True
        data = request.data
        data.pop("employer", None)
        data.pop("password", None)
        serializer = self.serializer_class(obj, data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        # suspending employee
        suspend = data.get("suspend")
        if suspend:
            if suspend.lower() == "true":
                obj.is_active = False
                send_mail(
                    subject="Shyper Account suspension",
                    message="your account has been suspended",
                    from_email=EMAIL_HOST_USER,
                    recipient_list=[obj.email],
                    fail_silently=False,
                )
                send_sms(
                    message="your shypper account has been suspended",
                    recipients=[obj.phone],
                )
            if suspend.lower() == "false":
                obj.is_active = True
                send_mail(
                    subject="Shyper Account reactivation",
                    message="your account suspension has been uplifted",
                    from_email=EMAIL_HOST_USER,
                    recipient_list=[obj.email],
                    fail_silently=False,
                )
                send_sms(
                    message="your shypper account has been reactivated",
                    recipients=[obj.phone],
                )
            obj.save()
        response = {
            "message": "employee data succesfully updated",
            "employee": serializer.data,
        }
        return Response(response, status.HTTP_200_OK)

    def destroy(self, request, pk):
        obj = self.get_object()
        obj.is_active = False
        obj.soft_delete(commit=True)
        return Response(status.HTTP_204_NO_CONTENT)
