from django.db import models
from utils.models import AbstractBaseModel, ActiveObjectsQuerySet

from django.core.exceptions import ValidationError

from utils.models import AbstractBaseModel, ActiveObjectsQuerySet
from utils.helpers import enforce_all_required_arguments_are_truthy


class CargoTypeManager(models.Manager):
    """
    Manager to handle cargo type and commodity methods
    """

    def create_cargo_type(self, cargo_type=None, description=None):
        """
        method to create cargo type
        """

        REQUIRED_ARGS = ("cargo_type",)

        enforce_all_required_arguments_are_truthy(
            {"cargo_type": cargo_type, "description": description}, REQUIRED_ARGS
        )

        cargo_type = self.model(cargo_type=cargo_type, description=description)
        cargo_type.save()
        return cargo_type

    def create_commodity(
        self, name=None, description=None, created_by=None, cargo_type=None
    ):
        """
        method to create  and return commodity
        """
        REQUIRED_ARGS = ("name", "description", "created_by", "cargo_type")
        enforce_all_required_arguments_are_truthy(
            {
                "name": name,
                "description": description,
                "created_by": created_by,
                "cargo_type": cargo_type,
            },
            REQUIRED_ARGS,
        )
        commodity = self.model(
            name=name,
            description=description,
            cargo_type=cargo_type,
            created_by=created_by,
        )
        commodity.save()
        return commodity


class CargoType(AbstractBaseModel, models.Model):
    cargo_type = models.CharField(
        max_length=30,
        choices=[
            ("Container", "Container"),
            ("Bagged and Bulk", "Bagged and Bulk"),
            ("FMCG", "Fast-Moving Customer Goods"),
        ],
        unique=True,
    )
    description = models.CharField(max_length=200)

    objects = CargoTypeManager()
    active_objects = ActiveObjectsQuerySet.as_manager()

    def __str__(self):
        return self.cargo_type


class CommodityQuerySet(ActiveObjectsQuerySet):
    """Queryset to used by commodity model"""

    def get_commodity(self, created_by=None):
        """returns all commodities created by a spacific cargo owner"""
        return self._active().filter(created_by=created_by)


class Commodity(AbstractBaseModel, models.Model):
    name = models.CharField(max_length=200)
    cargo_type = models.ForeignKey(CargoType, on_delete=models.DO_NOTHING)
    description = models.TextField(max_length=200)
    created_by = models.ForeignKey(
        "companies.CargoOwnerCompany", on_delete=models.DO_NOTHING
    )

    objects = CargoTypeManager()
    active_objects = CommodityQuerySet.as_manager()

    def __str__(self):
        return self.name
