from authentication.models import User
from companies.models import TransporterCompany
from rest_framework import serializers
from .models import Driver
from django.core.mail import send_mail
from logisticts.settings import EMAIL_HOST_USER
from utils.helpers import random_password
from rest_framework.fields import CurrentUserDefault
from django.db import transaction


class DriverRegistrationSerializer(serializers.ModelSerializer):

    role = serializers.CharField(default="driver")

    class Meta:
        model = User
        fields = ["id", "full_name", "email", "role", "phone"]


class DriverSerializer(serializers.ModelSerializer):
    """Handles serialization and deserialization of Driver objects."""

    user = DriverRegistrationSerializer()

    class Meta:
        model = Driver
        fields = ["id", "driver_license", "id_number", "user", "company"]

    def create(self, validated_data):
        user_data = validated_data.pop("user")
        password = random_password(10)
        user_data["password"] = password

        user = User.objects.create_driver(**user_data)
        driver = Driver.active_objects.create(user=user, **validated_data)
        email = user_data["email"]

        subject = "Account Created"
        message = f"Your driver account has been created by Shipper. Login with these credentials. Your email is : {email} and password: {password}."
        from_email = EMAIL_HOST_USER
        recipient_list = [email]
        # sends authentication credentials to the driver
        send_mail(subject, message, from_email, recipient_list, fail_silently=False)

        return driver

    def update(self, instance, validated_data):
        """
        Override this method so that driver information is properly updated.
        """

        driver_user_data = validated_data.pop("user", None)

        # if driver data needs to be updated, it is update at this
        # stage. Because it is nested, we have to manually update
        # it.
        if driver_user_data:

            request = self.context.get("request")
            driver_id = request.resolver_match.kwargs.get("id")
            # get the user instance we want to update
            user_instance = Driver.active_objects.get(pk=driver_id).user
            driver_serializer = DriverRegistrationSerializer(
                data=driver_user_data, partial=True
            )
            driver_serializer.is_valid(raise_exception=True)
            # update user instance
            driver_serializer.update(user_instance, driver_user_data)

        # now proceed to update the driver instance
        return super().update(instance, validated_data)
