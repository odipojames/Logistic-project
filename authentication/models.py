from django.db import models
from django.contrib.auth import get_user_model, password_validation
from django.contrib.auth.models import (
    BaseUserManager,
    AbstractBaseUser,
    PermissionsMixin,
)
from django.core.exceptions import ValidationError
from utils.models import AbstractBaseModel, ActiveObjectsQuerySet
from utils.validators import validate_international_phone_number
from utils.helpers import enforce_all_required_arguments_are_truthy
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserManager(BaseUserManager):
    """
    Custom manager to handle the User model methods.
    """

    def create_user(
        self, full_name=None, email=None, password=None, phone=None, role=None, **kwargs
    ):
        REQUIRED_ARGS = ("full_name", "email", "password", "phone")

        enforce_all_required_arguments_are_truthy(
            {
                "full_name": full_name,
                "email": email,
                "password": password,
                "phone": phone,
            },
            REQUIRED_ARGS,
        )

        # Create role first. If a role already exists, we don't create it again.
        role = Role.active_objects.get_or_create(title=role)[0]

        # employer = Employer.objects.get_or_create(employer_code=employer)[0]

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
            **kwargs
        )

        # ensure phone number and all fields are valid.
        user.clean()
        user.set_password(password)
        user.save()
        return user

    def create_superuser(
        self, full_name=None, email=None, password=None, phone=None, role=None, **kwargs
    ):
        """
        This is the method that creates superusers in the database.
        """

        admin = self.create_user(
            full_name=full_name,
            email=email,
            password=password,
            role="superuser",
            phone=phone,
            is_superuser=True,
            is_staff=True,
            is_verified=True,
            is_active=True,
        )

        return admin

    def create_transporter(
        self,
        full_name=None,
        email=None,
        password=None,
        phone=None,
        role="transporter-director",
        **kwargs
    ):
        """
        This  creates transporter company director/admin
        """

        transporter = self.create_user(
            full_name=full_name,
            email=email,
            password=password,
            role=role,
            phone=phone,
            is_superuser=False,
            is_staff=False,
            is_verified=False,
            is_active=True,
        )

        return transporter

    def create_cargo_owner(
        self,
        full_name=None,
        email=None,
        password=None,
        phone=None,
        role="cargo-owner-director",
        **kwargs
    ):
        """
        This  creates cargoOwner company director/admin
        """

        cargoOwner = self.create_user(
            full_name=full_name,
            email=email,
            password=password,
            role=role,
            phone=phone,
            is_superuser=False,
            is_staff=False,
            is_verified=False,
            is_active=True,
        )

        return cargoOwner

    def create_driver(
        self,
        full_name=None,
        email=None,
        phone=None,
        is_verified=True,
        password=None,
        role=None,
        **kwargs
    ):
        """
        This is the to create the driver
        """

        driver = self.create_user(
            full_name=full_name,
            email=email,
            is_verified=is_verified,
            role="driver",
            password=password,
            phone=phone,
            is_superuser=False,
            is_active=True,
        )

        driver.is_verified = True
        return driver


class User(PermissionsMixin, AbstractBaseModel, AbstractBaseUser):
    """
    Custom user model to be used throughout the application.
    """

    full_name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    phone = models.CharField(unique=True, max_length=50)
    date_joined = models.DateTimeField(auto_now=True)
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    employer = models.ForeignKey(
        "companies.Company",
        on_delete=models.CASCADE,
        related_name="employees",
        null=True,
        blank=True,
    )
    role = models.ForeignKey(
        "Role", on_delete=models.CASCADE, related_name="users", to_field="title"
    )
    REQUIRED_FIELDS = ["full_name", "phone"]
    USERNAME_FIELD = "email"

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
            raise ValidationError(
                {"phone": "Please enter a valid international phone number."}
            )
        return super().clean()


class Role(AbstractBaseModel, models.Model):
    """
    Contains the Role that each user must have.
    """

    role_choice = (
        ("transporter-director", "transporter-director"),
        ("cargo-owner-director", "cargo-owner-director"),
        ("driver", "driver"),
        ("admin", "admin"),
        ("staff", "staff"),
        ("superuser", "superuser"),
    )
    title = models.CharField(
        max_length=100,
        choices=role_choice,
        help_text="User's role within employer's organization.",
        unique=True,
    )

    active_objects = ActiveObjectsQuerySet.as_manager()

    def __str__(self):
        return self.title


class Profile(models.Model):
    """create user profiles"""

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="user_profile"
    )
    profile_picture = models.ImageField(
        upload_to="documents/profile/", null=True, blank=True
    )
    id_or_passport = models.CharField(max_length=20, blank=True, null=True)
    date_of_birth = models.DateField(null=True, blank=True)
    person_contact_name = models.CharField(max_length=50, blank=True, null=True)
    person_contact_phone = models.CharField(max_length=50, null=True, blank=True)

    @receiver(post_save, sender=User)
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            Profile.objects.create(user=instance)

    @receiver(post_save, sender=User)
    def save_user_profile(sender, instance, **kwargs):
        instance.user_profile.save()

    def __str__(self):
        return self.user.full_name
