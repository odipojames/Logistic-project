from django.db import models
from utils.models import AbstractBaseModel, ActiveObjectsQuerySet

from django.core.exceptions import ValidationError

from utils.helpers import enforce_all_required_arguments_are_truthy
from orders.models import Order
from decimal import Decimal


class RatesManager(models.Manager):
    """
    Manager to handle methods of the rates model.
    """

    def create_rates(
        self,
        price_per_kg=Decimal(0),
        price_per_km=Decimal(0),
        price_per_truck=Decimal(0),
        preferred_currency=None,
        created_by=None,
    ):
        """
        Method to create and return Rate instances.
        """

        REQUIRED_ARGS = ("preferred_currency", "created_by")

        enforce_all_required_arguments_are_truthy(
            {"preferred_currency": preferred_currency, "created_by": created_by},
            REQUIRED_ARGS,
        )

        rates = self.model(
            price_per_kg=price_per_kg,
            price_per_km=price_per_km,
            price_per_truck=price_per_truck,
            preferred_currency=preferred_currency,
            created_by=created_by,
        )
        rates.save()
        return rates


class RatesQuerySet(ActiveObjectsQuerySet):
    """ Queryset to be used by rates model"""

    def get_rates(self, created_by=None):
        """ returns all rates created by a specifi cargo owner"""
        return self._active().filter(created_by=created_by)


class Rate(AbstractBaseModel, models.Model):
    price_per_kg = models.DecimalField(
        decimal_places=4, max_digits=12, blank=True, default=Decimal(0)
    )
    price_per_km = models.DecimalField(
        decimal_places=4, max_digits=12, blank=True, default=Decimal(0)
    )
    price_per_truck = models.DecimalField(
        decimal_places=4, max_digits=12, blank=True, default=Decimal(0)
    )
    preferred_currency = models.CharField(
        max_length=20, choices=[("USD", "USD"), ("KES", "KES")]
    )
    created_by = models.ForeignKey(
        "companies.CargoOwnerCompany", on_delete=models.CASCADE, related_name="rates"
    )

    objects = RatesManager()
    active_objects = RatesQuerySet.as_manager()
