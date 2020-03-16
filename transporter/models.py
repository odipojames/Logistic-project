from django.db import models, IntegrityError
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from utils.models import AbstractBaseModel, ActiveObjectsQuerySet
from utils.helpers import enforce_all_required_arguments_are_truthy
from authentication.models import User, UserManager
from utils.validators import validate_file_extension
from companies.models import TransporterCompany


class DriverQuerySet(ActiveObjectsQuerySet):
    """Queryset that will be used by the driver model"""

    def for_transporter(self, company=None):
        """This query set returns all the driver that
        belongs to a particular transporter"""
        return self._active().filter(company=company)


class Driver(AbstractBaseModel, models.Model):
    id_number = models.CharField(max_length=20, unique=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    company = models.ForeignKey(
        TransporterCompany, on_delete=models.CASCADE, related_name="drivers"
    )
    driver_license = models.CharField(max_length=20, unique=True)

    active_objects = DriverQuerySet.as_manager()

    def __str__(self):
        return self.user.full_name
