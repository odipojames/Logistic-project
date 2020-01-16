from django.db import models
from django.contrib.postgres.fields import HStoreField

from utils.models import AbstractBaseModel, ActiveObjectsQuerySet

from django.core.exceptions import ValidationError

from utils.helpers import enforce_all_required_arguments_are_truthy
from orders.models import Order
from decimal import Decimal

class RatesManager(models.Manager):
    """
    Manager to handle methods of the rates model.
    """

    def create_rates(self, type={}, prefered_currency=None):
        """
        Method to create and return Rate instances.
        """

        REQUIRED_ARGS = ("type", "prefered_currency")

        enforce_all_required_arguments_are_truthy(
            {"type": type, "prefered_currency": prefered_currency}, REQUIRED_ARGS)

        rates = self.model(type=type, prefered_currency=prefered_currency)
        rates.clean()
        rates.save()
        return rates


class Rate(AbstractBaseModel, models.Model):
    type = HStoreField()
    prefered_currency = models.CharField(
        max_length=20, choices=[('USD', 'USD'), ('KES', 'KES')])
    # Generic relations https://docs.djangoproject.com/en/2.2/ref/contrib/contenttypes/#id1

    
    objects = RatesManager()
    active_objects = ActiveObjectsQuerySet.as_manager()

    def clean(self):
        # TODO validate that the charges dictionary contains necessary keys, eg cost per distance, etc
        RATE_CHOICES = ("price_per_km", "price_per_kg", "price_per_truck")

        for key in RATE_CHOICES:
            if key in self.type.keys() is None:
                raise ValidationError({"charges": f"{key} must be provided."})

        for value in self.type.values():
            value = Decimal(value)
            if not isinstance(value, Decimal):
                raise ValidationError({"Rates should be decimal value"})
            
            

        # if a key is passed that shouldn't be included, we remove it.
        for key in self.type.copy().keys():
            if key not in RATE_CHOICES:
                self.type.pop(key)
        return super().clean()
