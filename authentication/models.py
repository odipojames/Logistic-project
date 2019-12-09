from django.db import models
from django.contrib.auth import get_user_model, password_validation
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from django.core.exceptions import ValidationError

from companies.models import Employer
from utils.models import AbstractBaseModel, ActiveObjectsQuerySet
from utils.validators import validate_international_phone_number
from utils.helpers import enforce_all_required_arguments_are_truthy

class UserManager(BaseUserManager):
    """
    Custom manager to handle the User model methods.
    """

    def create_user(self, full_name=None, email=None, password=None, phone=None, role=None, employer=None, **kwargs):
        REQUIRED_ARGS = ("full_name", "email", "password", "phone", "role", "employer")

        enforce_all_required_arguments_are_truthy({"full_name": full_name, "email": email, "password": password, "phone": phone, "role": role, "employer": employer}, REQUIRED_ARGS)

        # Create role first. If a role already exists, we don't create it again.
        role = Role.active_objects.get_or_create(title=role)[0]

        employer = Employer.objects.get_or_create(employer_code=employer)[0]

        # ensure that the passwords are strong enough.
        try:
            password_validation.validate_password(password)
        except ValidationError as exc:
            # return error accessible in the appropriate field, ie password
            raise ValidationError({"password": exc.messages}) from exc
        
        user = self.model(
            full_name=full_name,
            email=self.normalize_email(email),
            phone=phone,
            role=role,
            employer=employer,
            **kwargs
        )

        # ensure phone number and all fields are valid.
        user.clean()
        user.set_password(password)
        user.save()
        return user

    def create_superuser(
            self, full_name=None, email=None, password=None, phone=None, role="superuser", **kwargs):
        '''
        This is the method that creates superusers in the database.
        '''

        admin = self.create_user(full_name=full_name, email=email, password=password, role=role, phone=phone, is_superuser=True, is_staff=True, is_verified=True, is_active=True)

        return admin

class User(PermissionsMixin, AbstractBaseModel, AbstractBaseUser):
    """
    Custom user model to be used throughout the application.
    """

    full_name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    phone = models.CharField(unique=True, max_length=50)
    passport_number = models.CharField(unique=True, max_length=50, null=True, blank=True)
    drivers_license = models.CharField(unique=True, max_length=50, null=True, blank=True)
    date_joined = models.DateTimeField(auto_now=True)
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    # TODO: should this be nullable and blank?
    role = models.ForeignKey("Role", on_delete=models.CASCADE, related_name="users", to_field="title")

    employer = models.ForeignKey("companies.Employer", related_name="employees", to_field="employer_code", on_delete=models.SET_NULL, null=True, blank=True)

    REQUIRED_FIELDS = ['full_name', "phone"]
    USERNAME_FIELD = 'email'

    objects = UserManager()

    # this manager will now return a QuerySet of all instances that are not soft deleted.

    active_objects = ActiveObjectsQuerySet.as_manager()

    def __str__(self):

        return self.get_username()

    @property
    def get_email(self):

        return self.email

    @property
    def get_full_name(self):
        return self.full_name

    def clean(self):
        """
        We ensure that the phone number is of the proper format before we save it.
        """

        phone = self.phone

        if not validate_international_phone_number(phone):
            raise ValidationError({"phone": "Please enter a valid international phone number."})
        return super().clean()


class Role(AbstractBaseModel, models.Model):
    """
    Contains the Role that each user must have.
    """

    title = models.CharField(max_length=100, help_text="User's role within employer's organization.", unique=True)

    active_objects = ActiveObjectsQuerySet.as_manager()

    def __str__(self):
        return self.title
