from rest_framework import serializers
from companies.models import CargoOwnerCompany, TransporterCompany, PersonOfContact
from authentication.models import User, UserManager
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from authentication.serializers import TransporterRegistrationSerializer, CargoOwnerRegistrationSerializer


class CargoOwnerSerializer(serializers.ModelSerializer):
    '''create cargo owner company and its owner once'''
    company_director = CargoOwnerRegistrationSerializer()

    class Meta:
        model = CargoOwnerCompany
        fields = '__all__'

    def create(self, validated_data):
        user_data = validated_data.pop('company_director')
        user = User.objects.create_cargo_owner(
            **user_data)  # company_admin who is the onwer
        company = CargoOwnerCompany.active_objects.create(
            company_director=user, **validated_data)
        return company

    def update(self, instance, validated_data):
        company_director_data = validated_data.pop('company_director')

        if company_director_data:
            company_director = instance.company_director
            serializer = CargoOwnerRegistrationSerializer(
                data=company_director_data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.update(company_director, company_director_data)

        return super().update(instance, validated_data)


class TransporterSerializer(serializers.ModelSerializer):
    '''create transport company and its admin who is the dirctor in this case'''

    company_director = TransporterRegistrationSerializer()

    class Meta:
        model = TransporterCompany
        fields = '__all__'

    def create(self, validated_data):
        user_data = validated_data.pop('company_director')
        user = User.objects.create_transporter(
            **user_data)  # company_admin who is the onwer
        company = TransporterCompany.active_objects.create(
            company_director=user, **validated_data)
        return company

    def update(self, instance, validated_data):

        company_director_data = validated_data.pop('company_director')

        if company_director_data:
            company_director = instance.company_director
            serializer = TransporterRegistrationSerializer(
                data=company_director_data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.update(company_director, company_director_data)

        return super().update(instance, validated_data)


class PersonofContactSerializer(serializers.ModelSerializer):
    """
    Serializer for creating points of contact
    """
    class Meta:
        model = PersonOfContact
        fields = ['id', 'company', 'name', 'email', 'phone']

        def create(self, validated_data):
            return PersonOfContact.objects.create_person_of_contact(**validated_data)
