from rest_framework import serializers
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from django.shortcuts import render
from authentication.models import User
from django.contrib.auth import authenticate


class RegistrationSerializer(serializers.ModelSerializer):

    first_name = serializers.CharField()
    last_name = serializers.CharField()
    username = serializers.CharField()
    company_name = serializers.CharField()
    role = serializers.ChoiceField(
        choices=[('EM', 'Employee'), ('AD,Shipper Admin'), ('TR', 'Transporter'), ('CO', 'Cargo Owner')
                 ]
    )
    password = serializers.CharField(
        max_length=12, min_length=4, write_only=True,
        error_messages={
            "min_length": "Password should be {min_length} characters and above"
        }
    )
    confirmed_password = serializers.CharField(
        max_length=124,
        min_length=4,
        write_only=True,
        error_messages={
            "min_length": "Password should be at least {min_length} characters"
        }
    )

    class Meta:
        model = User
        fields = ["email", "first_name", "last_name", 'company_name', 'username',
                  "password", "confirmed_password", "role"]

    def validate(self, data):
        """validate data before it gets saved"""
        confirmed_password = data.get("confirmed_password")

        try:
            validate_password(data['password'])
        except ValidationError as e:
            raise serializers.ValidationError({
                "password": str(e).replace(
                    "["", "").replace(""]", ""
                )
            })

        if not self.do_passwords_match(data['password'], confirmed_password):
            raise serializers.ValidationError({
                "password": "passwords don't match"
            })

        return data

    def create(self, validated_data):

        del validated_data["confirmed_password"]
        return User.objects.create_user(**validated_data)

    @staticmethod
    def do_passwords_match(password1, password2):

        return password1 == password2


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(
        write_only=True, max_length=124, min_length=4)
    token = serializers.CharField(max_length=200, read_only=True)

    def validate(self, data):
        email = data.get('email', None)
        password = data.get('password', None)
        user = authenticate(username=email, password=password)

        if user is None:
            raise serializers.ValidationError({
                "invalid": "wrong password or email"
            })

        return {
            'email': user.email,
            'username': user.username,
            'token': user.token,
            'is_active': user.is_active
        }


class UserUpdateSerializer(serializers.ModelSerializer):
    """Handles serialization and deserialization of User objects."""

    # Passwords must be at least 8 characters, but no more than 128
    # characters. These values are the default provided by Django. We could

    password = serializers.CharField(
        max_length=124,
        min_length=4,
        write_only=True
    )

    class Meta:
        model = User
        fields = ["email", "first_name", "last_name",
                  'company_name', 'username', "role"]
        # The `read_only_fields` option is an alternative for explicitly
        # specifying the field with `read_only=True` like we did for password

    def update(self, instance, validated_data):
        """Performs an update on a User."""

        # we need to remove the password field from the
        # `validated_data` dictionary before iterating over it.
        password = validated_data.pop('password', None)

        for (key, value) in validated_data.items():
            # For the keys remaining in `validated_data`, we will set them on
            # the current `User` instance one at a time.
            setattr(instance, key, value)

        if password is not None:
            # `.set_password()`  handles all
            # of the security stuff that we shouldn't be concerned with.
            instance.set_password(password)

        # After everything has been updated we must explicitly save

        instance.save()

        return instance
