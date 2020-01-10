from django.db import models
from django.contrib.postgres.fields import HStoreField

from utils.models import AbstractBaseModel, ActiveObjectsQuerySet

from django.core.exceptions import ValidationError

from utils.models import AbstractBaseModel, ActiveObjectsQuerySet
from utils.helpers import enforce_all_required_arguments_are_truthy


class RatesManager(models.Manager):
    """
    Manager to handle methods of the rates model.
    """

    def create_rates(self, type=None, prefered_currency=None):
        """
        Method to create and return Rate instances.
        """

        REQUIRED_ARGS = ("type", "prefered_currency")

        enforce_all_required_arguments_are_truthy(
            {"type": type, "prefered_currency": prefered_currency}, REQUIRED_ARGS)

        rates = self.model(type=type, prefered_currency=prefered_currency)

        rates.save()
        return rates


class Rate(AbstractBaseModel, models.Model):
    type = HStoreField()
    prefered_currency = models.CharField(
        max_length=20, choices=[('USD', 'USD'), ('KES', 'KES')])

    objects = RatesManager()
    active_objects = ActiveObjectsQuerySet.as_manager()
