import uuid

from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import HStoreField, ArrayField
from django.core.exceptions import ValidationError

from utils.models import AbstractBaseModel, ActiveObjectsQuerySet
from utils.helpers import enforce_all_required_arguments_are_truthy


class OrderManager(models.Manager):
    """
    Manager class for the Order model.
    """

    def create_order(self, **kwargs):
        """
        Method to actually create an order. Ensure all arguments in `REQUIRED_ARGS` are provided.
        """

        origin = kwargs.get("origin")
        destination = kwargs.get("destination")

        # We ensure that origin and destination are passed in either a tuple or list

        if origin and (not isinstance(origin, list) and not isinstance(origin, tuple)):
            raise ValidationError({"origin": "Could not save origin. Please pass a list or tuple containing one or more depot instances for origin."})

        if destination and (not isinstance(destination, list) and not isinstance(destination, tuple)):
            raise ValidationError({"destination": "Could not save destination. Please pass a list or tuple containing one or more depot instances for destination."})

        REQUIRED_ARGS = ("title", "description", "cargo_type", "cargo_tonnage", "loading_point_contact", "loading_point_contact_name",
                         "offloading_point_contact_name", "offloading_point_contact", "desired_rates", "desired_truck_type", "owner", "recepients", "origin", "destination")

        enforce_all_required_arguments_are_truthy(kwargs, REQUIRED_ARGS)

        # pop out depots because they can only be added once the model is saved.
        kwargs.pop("origin", None)
        kwargs.pop("destination", None)

        order = self.model(**kwargs)

        order.clean() # ensure the model is valid before saving
        order.save()

        if origin:
            order.origin.set(origin)

        if destination:
            order.destination.set(destination)
        return order


class Order(AbstractBaseModel, models.Model):
    """
    Class for modelling Order entities.
    """

    # this determines the maximum size of the array that holds recepients.
    MAX_RECEPIENT_COUNT = 5

    # TODO ensure these choices are correct.
    STATUS_CHOICES = [
        ("PD", "Pending"),
        ("AS", "Assigned"),
        ("AO", "Accepted")
    ]

    ORDER_TYPES = [
        ("SO-SD", "Single Origin To Single Destination"),
        ("SO-MD", "Single Origin To Many Destinations"),
        ("MO-MD", "Many Origins To Many Destinations"),
        ("MO-SD", "Many Origins To Single Destination"),
    ]

    title = models.CharField(max_length=50)
    description = models.CharField(max_length=1000)
    commodity = models.ForeignKey("cargo_types.Commodity", on_delete=models.CASCADE)
    cargo_tonnage = models.DecimalField(max_digits=12, decimal_places=4, blank=True, null=True)
    origin = models.ManyToManyField(
        "depots.Depot", blank=True, related_name="sent_orders")
    destination = models.ManyToManyField(
        "depots.Depot", blank=True, related_name="received_orders")
    loading_point_contact = models.ForeignKey("companies.PersonOfContact", on_delete=models.CASCADE, related_name='loading_orders')
    offloading_point_contact = models.ForeignKey("companies.PersonOfContact", on_delete=models.CASCADE, related_name='offloading_orders')
    status = models.CharField(
        max_length=2, choices=STATUS_CHOICES, default="PD")
    desired_rates = models.ForeignKey('rates.Rate', on_delete=models.CASCADE)
    recurring_order = models.BooleanField(default=False)
    order_type = models.CharField(
        max_length=5, choices=ORDER_TYPES, default="SO-SD")
    desired_truck_type = models.CharField(max_length=50)
    owner = models.ForeignKey('companies.CargoOwnerCompany', on_delete=models.CASCADE, related_name="orders")
    # TODO Must the recepients be registered on our application? If so, change this to ForeignKey
    recepients = ArrayField(models.CharField(
        blank=True, null=True, max_length=100), size=MAX_RECEPIENT_COUNT)
    assigned = models.BooleanField(default=False)
    # Added this just so we can track the order without using the auto-incrementing pk
    tracking_id = models.UUIDField(
        default=uuid.uuid4, blank=True, editable=False, unique=True, db_index=True)

    objects = OrderManager()
    active_objects = ActiveObjectsQuerySet.as_manager()

    def __str__(self):
        return f"{self.title} order by {self.owner}."

    def clean(self):
        RATE_CHOICES = ("per_tonne", "per_km_per_tonne", "per_truck_load")

        for key in RATE_CHOICES:
            if key not in self.desired_rates.keys():
                raise ValidationError({"desired_rates": f"{key} must be provided."})

        # if a key is passed that shouldn't be included, we remove it.
        for key in self.desired_rates.copy().keys():
            if key not in RATE_CHOICES:
                self.desired_rates.pop(key)

        return super().clean()


class CargoOwnerInvoiceManager(models.Manager):
    """
    Manager class for CargoOwnerInvoice model.
    """

    def create_cargo_owner_invoice(self, order=None, number_of_trips=None, description=None, charges=None):
        """
        Create an invoice for a cargo owner.
        """

        REQUIRED_ARGS = ("order", "number_of_trips", "description", "charges")

        enforce_all_required_arguments_are_truthy({"order": order, "number_of_trips": number_of_trips, "description": description, "charges": charges}, REQUIRED_ARGS)

        invoice = self.model(order=order, number_of_trips=number_of_trips, description=description, charges=charges)

        invoice.clean()
        invoice.save()

        return invoice

class CargoOwnerInvoice(AbstractBaseModel, models.Model):
    """
    This represents invoices sent to Cargo Owners.
    """

    order = models.ForeignKey(Order, to_field="tracking_id", on_delete=models.CASCADE)
    number_of_trips = models.IntegerField()
    description = models.CharField(max_length=1000)
    charges = HStoreField()

    objects = CargoOwnerInvoiceManager()
    active_objects = ActiveObjectsQuerySet.as_manager()

    def __str__(self):
        return f"Cargo Owner Invoice for {self.order}."


    def clean(self):
        """
        Ensure form is valid.
        """
        RATE_CHOICES = ("per_tonne", "per_km_per_tonne", "per_truck_load")

        for key in RATE_CHOICES:
            if key not in self.charges.keys():
                raise ValidationError({"charges": f"{key} must be provided."})

        # if a key is passed that shouldn't be included, we remove it.
        for key in self.charges.copy().keys():
            if key not in RATE_CHOICES:
                self.charges.pop(key)

        return super().clean()
