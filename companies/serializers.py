from rest_framework import serializers
from companies.models import (
    CargoOwnerCompany,
    TransporterCompany,
    PersonOfContact,
    Company,
)
from authentication.models import User, UserManager, Role
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from authentication.serializers import (
    TransporterRegistrationSerializer,
    CargoOwnerRegistrationSerializer,
)
from django.contrib.auth.base_user import BaseUserManager
from utils.validators import validate_international_phone_number
from django.core import exceptions
import django.contrib.auth.password_validation as validators
from utils.helpers import get_errored_integrity_field
from django.db.utils import IntegrityError
from authentication.serializers import CompanyDirectorSerializer
from rest_framework.validators import ValidationError


class CompanySerializer(serializers.ModelSerializer):
    """creating company dirctor for cargo owners """

    company_director = CargoOwnerRegistrationSerializer()
    CAT_CHOICES = (("cargo_owner", "cargo_owner"),)
    category = serializers.ChoiceField(choices=CAT_CHOICES, default="cargo_owner")
    business_phone_no = serializers.CharField(
        max_length=15, validators=[validate_international_phone_number]
    )

    class Meta:
        model = Company
        fields = "__all__"


class CompanyTSerializer(serializers.ModelSerializer):
    """creating company  director for transporters"""

    company_director = TransporterRegistrationSerializer()
    CAT_CHOICES = (("transporter", "transporter"),)
    category = serializers.ChoiceField(choices=CAT_CHOICES, default="transporter")
    business_phone_no = serializers.CharField(
        max_length=15, validators=[validate_international_phone_number]
    )

    class Meta:
        model = Company
        fields = "__all__"


class CargoOwnerSerializer(serializers.ModelSerializer):
    """create cargo owner company and its owner once"""

    company = CompanySerializer(read_only=False)

    class Meta:
        model = CargoOwnerCompany
        fields = "__all__"

    def create(self, validated_data):
        company_data = validated_data.pop("company")  # get company instance
        user_data = company_data.pop("company_director")
        try:
            user = User.objects.create_cargo_owner(**user_data)
        except IntegrityError as exc:
            errored_field = get_errored_integrity_field(exc)
            if errored_field:
                raise serializers.ValidationError(
                    {
                        errored_field: f"A company user is already registered with this {errored_field}."
                    }
                ) from exc
        except ValidationError as exc:
            raise serializers.ValidationError(exc.args[0]) from exc
        company = Company.objects.create(
            company_director=user, **company_data
        )  # create company
        cargo_company = CargoOwnerCompany.active_objects.create(
            company=company, **validated_data
        )  # create cargo owner company
        director = cargo_company.company.company_director
        # make director be employee of its company
        director.employer = cargo_company.company
        director.save()
        return cargo_company


class CargoOwnerUpdateSerializer(serializers.ModelSerializer):
    """serializer for retrival and updating cargo owner companies """

    company = CompanySerializer(read_only=False)

    class Meta:
        model = CargoOwnerCompany
        fields = "__all__"

    def get_fields(self):
        fields = super(CargoOwnerUpdateSerializer, self).get_fields()
        try:  # Handle unique fields on company serializer
            if self.instance and self.instance.company:
                fields["company"].instance = self.instance.company
        except Company.DoesNotExist:
            pass
        return fields

    def update(self, instance, validated_data):
        company_data = validated_data.pop("company", None)
        if company_data:
            company_data.pop("company_director", None)  # remove director
            company_data.pop("category", None)
            company = instance.company
            serializer = CargoOwnerSerializer(data=company_data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.update(company, company_data)

        return super().update(instance, validated_data)


class TransporterSerializer(serializers.ModelSerializer):
    """create transport company and its admin who is the dirctor in this case"""

    company = CompanyTSerializer(read_only=False)

    class Meta:
        model = TransporterCompany
        fields = "__all__"

    def create(self, validated_data):
        company_data = validated_data.pop("company")  # get company instance
        user_data = company_data.pop("company_director")
        try:
            user = User.objects.create_transporter(
                **user_data
            )  # create the company director
        except IntegrityError as exc:
            errored_field = get_errored_integrity_field(exc)
            if errored_field:
                raise serializers.ValidationError(
                    {
                        "company": {
                            "company_director": {
                                errored_field: f"A company user is already registered with this {errored_field}."
                            }
                        }
                    }
                ) from exc
        except ValidationError as exc:
            raise serializers.ValidationError(exc.args[0]) from exc
        company = Company.objects.create(
            company_director=user, **company_data
        )  # create company
        transport_company = TransporterCompany.active_objects.create(
            company=company, **validated_data
        )  # create transporter owner company
        director = transport_company.company.company_director
        director.employer = transport_company.company
        director.save()
        return transport_company


class TransporterUpdateSerializer(serializers.ModelSerializer):
    """transport company retrival and update"""

    company = CompanyTSerializer(read_only=False)

    class Meta:
        model = TransporterCompany
        fields = "__all__"

    def get_fields(self):
        fields = super(TransporterUpdateSerializer, self).get_fields()
        try:  # Handle unique fields on company serializer
            if self.instance and self.instance.company:
                fields["company"].instance = self.instance.company
        except Company.DoesNotExist:
            pass
        return fields

    def update(self, instance, validated_data):

        company_data = validated_data.pop("company", None)
        if company_data:
            company_data.pop("company_director", None)
            company_data.pop("category", None)
            company = instance.company
            serializer = TransporterRegistrationSerializer(
                data=company_data, partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.update(company, company_data)

        return super().update(instance, validated_data)


class PersonofContactSerializer(serializers.ModelSerializer):
    """
    Serializer for creating points of contact
    """

    class Meta:
        model = PersonOfContact
        fields = ["id", "company", "name", "email", "phone"]

    def create(self, validated_data):
        return PersonOfContact.objects.create_person_of_contact(**validated_data)


class RoleSerializer(serializers.ModelSerializer):
    role_choice = (
        ("transporter-director", "transporter-director"),
        ("cargo-owner-director", "cargo-owner-director"),
        ("driver", "driver"),
        ("admin", "admin"),
        ("staff", "staff"),
    )
    title = serializers.ChoiceField(choices=role_choice, default="staff")

    class Meta:
        model = Role
        fields = ["title"]


class MainCompanySerializer(serializers.ModelSerializer):
    """company serializer"""

    company_director = CompanyDirectorSerializer()

    class Meta:
        model = Company
        fields = "__all__"


class EmployeeSerializer(serializers.ModelSerializer):
    """serializer for creating employees"""

    role_choice = (
        ("admin", "admin"),
        ("staff", "staff"),
        ("transporter-director", "transporter-director"),
        ("cargo-owner-director", "cargo-owner-director"),
    )  ## TODO: disble director choices on front end
    role = serializers.ChoiceField(choices=role_choice, default="staff")
    is_verified = serializers.BooleanField(default=True)
    full_name = serializers.CharField()
    phone = serializers.CharField(validators=[validate_international_phone_number])
    password = serializers.CharField(
        max_length=124,
        min_length=4,
        write_only=True,
        error_messages={
            "min_length": "Password should be {min_length} characters and above"
        },
    )

    class Meta:
        model = User
        fields = [
            "id",
            "full_name",
            "email",
            "password",
            "phone",
            "is_verified",
            "role",
            "employer",
        ]
        extra_kwargs = {
            "id": {"read_only": True},
            "password": {"read_only": True},
            "is_verified": {"read_only": True},
        }

    def validate(self, data):
        if not validate_international_phone_number(data.get("phone")):
            raise serializers.ValidationError(
                {"phone": "Please enter a valid international phone number"}
            )
        if (
            data.get("role") == "cargo-owner-director"
            or data.get("role") == "transporter-director"
        ):
            raise serializers.ValidationError({"role": "Please provide a valid choice"})
        validated_data = super().validate(data)

        role = data.get("role", None)

        if role:
            role_instance = Role.active_objects.get_or_create(title=role)[0]
            validated_data["role"] = role_instance
        return validated_data

    def create(self, validated_data):
        employee = User.objects.create_user(**validated_data)
        return employee

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response["employer"] = MainCompanySerializer(instance.employer).data
        return response
