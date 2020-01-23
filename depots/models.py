from django.db import models
from django.contrib.postgres.fields import HStoreField
from django.contrib.auth import get_user_model

from django.core.exceptions import ValidationError

from utils.models import AbstractBaseModel, ActiveObjectsQuerySet
from utils.helpers import enforce_all_required_arguments_are_truthy


class DepotManager(models.Manager):
    """
    Manager to handle methods of the Depot model.
    """

    def create_depot(self, city=None, address=None, street=None, state=None, coordinates=None, user=None,is_public=None):
        """
        Method to create and return depot instances.
        """

        REQUIRED_ARGS = ("coordinates", "user")

        enforce_all_required_arguments_are_truthy({"coordinates": coordinates, "user": user}, REQUIRED_ARGS)

        if not isinstance(user, get_user_model()):
            raise ValidationError({"user": "Provide a valid user instance for user."})


        depot = self.model(city=city, address=address, street=street, state=state, coordinates=coordinates, user=user,is_public=is_public)

        depot.clean()
        depot.save()
        return depot

class DepotQuerySet(ActiveObjectsQuerySet):
    """queryset to handle depot model"""
    def get_depot(self,user=None):
        """return only depots created by a particular cargo owner and all public ones"""
        return self._active().filter(user=user)
    def get_public(self,is_public=None):
        """return public depots"""
        return self._active().filter(is_public=True)

class Depot(AbstractBaseModel, models.Model):
    """
    This defines the data about a specific depot.
    """

    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name="Depots")
    city = models.CharField(max_length=50, null=True, blank=True)
    address = models.CharField(max_length=50, null=True, blank=True)
    street = models.CharField(max_length=50, null=True, blank=True)
    state = models.CharField(max_length=50, null=True, blank=True)
    coordinates = HStoreField()
    is_public = models.BooleanField(default=True)

    objects = DepotManager()

    active_objects = DepotQuerySet.as_manager()

    def __str__(self):
        return f"{self.coordinates} in {self.city}."

    def clean(self):
        """
        Ensure that coordinates are stored in proper format.
        """

        coordinate_keys = ("lattitude", "longitude")

        for key in coordinate_keys:
            if key not in self.coordinates.keys():
                raise ValidationError({key: f"{key} is required."})
            elif not self.coordinates[key]:
                raise ValidationError({key: f"{key} cannot be empty."})

        # remove any unnecessary keys being passed here
        self.coordinates = {"lattitude": self.coordinates.get("lattitude"),
        "longitude": self.coordinates.get("longitude")}

        return super().clean()
