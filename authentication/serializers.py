from rest_framework import serializers, exceptions
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate, get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer

from authentication.models import User, Profile
from utils.validators import validate_international_phone_number
from utils.helpers import get_errored_integrity_field, blacklist_user_outstanding_tokens


class RegistrationSerializer(serializers.Serializer):
    """
    Serializer for handling user registration
    """

    email = serializers.EmailField()
    phone = serializers.CharField(max_length=15, validators=[
                                  validate_international_phone_number])
    full_name = serializers.CharField(max_length=100)
    role = serializers.CharField()
    password = serializers.CharField(
        max_length=124, min_length=8, write_only=True)
    confirmed_password = serializers.CharField(
        max_length=124, min_length=8, write_only=True)

    def validate(self, data):
        """validate data before it gets saved"""
        confirmed_password = data.get("confirmed_password")

        try:
            validate_password(data['password'])
        except ValidationError as e:
            raise serializers.ValidationError({
                "password": e.messages
            }) from e

        if not self.do_passwords_match(data['password'], confirmed_password):
            raise serializers.ValidationError({
                "password": "passwords don't match"
            })

        return data

    def create(self, validated_data):
        validated_data.pop("confirmed_password")

        try:
            user = User.objects.create_user(**validated_data)
            return user
        except IntegrityError as exc:
            errored_field = get_errored_integrity_field(exc)
            if errored_field:
                raise serializers.ValidationError(
                    {errored_field: f"A user is already registered with this {errored_field}."}) from exc
        except ValidationError as exc:
            raise serializers.ValidationError(exc.args[0]) from exc

    @staticmethod
    def do_passwords_match(password1, password2):

        return password1 == password2


class LoginSerializer(TokenObtainPairSerializer):
    """
    We rely on the backend provided by simple jwt for more robust authentication.
    """

    @classmethod
    def get_token(cls, user):
        """
        Override this method to ensure that the email address is encoded within the JWT token.
        """
        token = super().get_token(user)

        token["email"] = user.email

        return token

    def validate(self, data):

        email = data.get("email")
        password = data.get("password")

        user = authenticate(username=email, password=password)

        if not user:
            raise exceptions.AuthenticationFailed(
                detail="Wrong email or password", code="authentication_failed")

        if user.is_verified == False:
            raise exceptions.AuthenticationFailed(
                detail="your account has not been verified please contact Shipper", code="unverified_account")

        if user:

            token = LoginSerializer.get_token(user)
            return {"refresh": str(token), "access": str(token.access_token)}


class UserUpdateSerializer(serializers.ModelSerializer):
    """Handles serialization and deserialization of User objects."""

    password = serializers.CharField(
        max_length=124,
        min_length=8,
        write_only=True
    )

    class Meta:
        model = User
        exclude = ["is_verified", "date_joined", "is_staff", "is_active", "groups",
                   "user_permissions", "is_deleted", "created_at", "updated_at", "last_login", "is_superuser"]
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

            # if a user changes their password, we blacklist all their outstanding refresh tokens.

            blacklist_user_outstanding_tokens(instance)

        # After everything has been updated we must explicitly save

        instance.save()

        return instance


class TransporterRegistrationSerializer(serializers.ModelSerializer):
    '''register transporter as a user'''
    full_name = serializers.CharField()
    phone = serializers.CharField(max_length=15, validators=[
                                  validate_international_phone_number])
    role = serializers.CharField(default="transporter-director")
    password = serializers.CharField(
        max_length=124, min_length=4, write_only=True,
        error_messages={
            "min_length": "Password should be {min_length} characters and above"
        }
    )

    class Meta:
        model = User
        fields = ["email", "full_name", 'phone',
                  "password", "role", ]

    def create(self, validated_data):

        return User.objects.create_transporter(**validated_data)


class CargoOwnerRegistrationSerializer(serializers.ModelSerializer):
    '''register cargo owner as a user'''
    full_name = serializers.CharField()
    phone = serializers.CharField(max_length=15, validators=[
                                  validate_international_phone_number])
    role = serializers.CharField(default="cargo-owner-director")
    password = serializers.CharField(
        max_length=124, min_length=8, write_only=True,
        error_messages={
            "min_length": "Password should be {min_length} characters and above"
        }
    )

    class Meta:
        model = User
        fields = ["email", "full_name", 'phone',
                  "password", "role", ]

    def create(self, validated_data):

        return User.objects.create_cargo_owner(**validated_data)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "full_name", "email",
                  "phone", "role", "employer"]


class ProfileSerializer(serializers.ModelSerializer):
    """user profile serializer"""
    date_of_birth = serializers.DateField(input_formats=['%d-%m-%Y', ])
    user = UserSerializer(read_only=True)

    class Meta:
        model = Profile
        fields = '__all__'

    def validate(self, data):

        if not validate_international_phone_number(data.get('person_contact_phone')):
            raise serializers.ValidationError(
                {'person_contact_phone': 'Please enter a valid international phone number'})
        validated_data = super().validate(data)

        return validated_data


class CustomTokenSerializer(serializers.Serializer):
    """custome tokenVerification"""
    token = serializers.CharField()
