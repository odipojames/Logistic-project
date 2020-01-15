from django.db import models
from django.core.exceptions import ValidationError

from utils.models import AbstractBaseModel, ActiveObjectsQuerySet
from utils.helpers import enforce_all_required_arguments_are_truthy
from utils.validators import validate_file_extension

# Create your models here.


class AssetManager(models.Manager):
    """
    manager to handele asset methods
    """

    def create_truck(self, name=None, owned_by=None, type=None, reg_no=None):
        """
        method that creates and return truck
        """
        REQUIRED_ARGS = ('name', 'owned_by', 'reg_no', 'type')
        enforce_all_required_arguments_are_truthy(
            {'name': name,  'reg_no': reg_no, 'owned_by': owned_by, 'type': type}, REQUIRED_ARGS)
        truck = self.model(name=name, type=type, owned_by=owned_by,reg_no=reg_no)
        truck.save()
        return truck

    def create_trailer(self, name=None, owned_by=None, type=None, reg_no=None):
        """
        method that creates and returns trailer
        """
        REQUIRED_ARGS = ('name','owned_by', 'reg_no', 'type')
        enforce_all_required_arguments_are_truthy({'name': name, 'type': type, 'owned_by': owned_by,'reg_no':reg_no},REQUIRED_ARGS)
        trailer = self.model(name=name, type=type, owned_by=owned_by,reg_no=reg_no)
        trailer.save()
        return trailer


class Asset(models.Model):
    """
    model that holds trucks/trailers data
    """
    name = models.CharField(max_length=200)
    owned_by = models.ForeignKey(
        'companies.TransporterCompany', on_delete=models.CASCADE)

    reg_no = models.CharField(max_length=20)
    tracking = models.BooleanField(default=False)

    class Meta:
        abstract = True


class Truck(AbstractBaseModel, Asset, models.Model):
    """
    model to hold truck information
    """
    type = models.CharField(
        max_length=200, choices=[('flatbed', 'flatbed'), ('double diff', 'double diff'), ('skeleton', 'skeleton')])
    truck_log_books = models.FileField(
    upload_to="documents/", validators=[validate_file_extension])

    objects = AssetManager()
    active_objects = ActiveObjectsQuerySet.as_manager()

    def __str__(self):
        return self.reg_no


class Trailer(AbstractBaseModel, Asset, models.Model):
    """
    model to hold trailer  information
    """
    type = models.CharField(
        max_length=200, choices=[('flatbed', 'flatbed'), ('enclosed', 'enclosed'), ('refregirated', 'refregirated'), ('lowboy', 'lowboy')])

    objects = AssetManager()
    active_objects = ActiveObjectsQuerySet.as_manager()

    def __str__(self):
        return self.reg_no
