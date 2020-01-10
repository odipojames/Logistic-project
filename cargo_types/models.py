from django.db import models
from utils.models import AbstractBaseModel, ActiveObjectsQuerySet

from django.core.exceptions import ValidationError

from utils.models import AbstractBaseModel, ActiveObjectsQuerySet
from utils.helpers import enforce_all_required_arguments_are_truthy


class CargoTypeManager(models.Manager):
    '''
    Manager to handle cargo type methods
    '''

    def create_cargo_type(self, name=None, description=None):
        '''
        method to create cargo type
        '''

        REQUIRED_ARGS = ('name', 'description')

        enforce_all_required_arguments_are_truthy(
            {"name": name, "description": description}, REQUIRED_ARGS)

        cargo_type = self.model(name=name, description=description)
        cargo_type.save()
        return cargo_type


class CargoType(AbstractBaseModel, models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()

    objects = CargoTypeManager()
    active_objects = ActiveObjectsQuerySet.as_manager()

    def __str__(self):
        return self.name
