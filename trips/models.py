from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils.timezone import make_aware
from django.contrib.postgres.fields import HStoreField, ArrayField

from companies.models import TransporterCompany,CargoOwnerCompany
from utils.models import AbstractBaseModel, ActiveObjectsQuerySet
from utils.helpers import enforce_all_required_arguments_are_truthy
from utils.validators import validate_start_date_is_before_end_date


class TripManager(models.Manager):
    """
    Contains manager methods for the Trip model.
    """

    def create_trip(self, **kwargs):
        """
        Method to actually create a trip.
        """

        REQUIRED_ARGS = ("start_date", "order", "truck", "origin", "destination", "offloading_point_contact", "loading_point_contact", "description", "trip_number", "transporter")

        enforce_all_required_arguments_are_truthy(kwargs, REQUIRED_ARGS)
        trip = self.model(**kwargs)

        trip.clean()
        trip.save()

        return trip


class Trip(AbstractBaseModel, models.Model):
    """
    This is a model of a Trip entity.
    """

    STATUS_CHOICES = [
        ("P", "Pending"),
        ("S", "Started"),
        ("O", "Ongoing"),
        ("D", "Delivered"),
    ]

    start_date = models.DateTimeField()
    end_date = models.DateTimeField(null=True, blank=True)
    order = models.ForeignKey(
        "orders.Order", related_name="trips", on_delete=models.CASCADE)
    truck = models.ForeignKey(
        "assets.Truck", related_name="trips", on_delete=models.CASCADE)
    origin = models.ForeignKey(
        "depots.Depot", related_name="trip_origins", on_delete=models.CASCADE)
    destination = models.ForeignKey(
        "depots.Depot", related_name="trip_destinations", on_delete=models.CASCADE)
    status = models.CharField(
        max_length=1, choices=STATUS_CHOICES, default="P")
    description = models.CharField(max_length=1000)
    # Do we need a trip number? So as to identify each trip for an order?
    trip_number = models.IntegerField()
    transporter = models.ForeignKey(TransporterCompany, on_delete=models.CASCADE, related_name="trips")
    tracking_data = ArrayField(base_field=models.CharField(max_length=50), blank=True) 
    offloading_point_contact = models.ForeignKey("companies.PersonOfContact", on_delete=models.CASCADE, related_name='offloading_trips')
    loading_point_contact = models.ForeignKey("companies.PersonOfContact", on_delete=models.CASCADE, related_name='loading_trips')

    objects = TripManager()
    active_objects = ActiveObjectsQuerySet.as_manager()

    def __str__(self):
        return f"Trip no. {self.trip_number} for {self.order}."

    def clean(self):
        """
        Ensure that the model is valid.
        """
        if self.end_date:
            if not validate_start_date_is_before_end_date(self.start_date, self.end_date):
                raise ValidationError("Start date must come before the end date.")

        # The origin and destination must not be the same places
        if self.origin == self.destination:
            raise ValidationError({"destination": "The destination cannot be the same as the origin."})

        return super().clean()


class TripInvoiceManager(models.Manager):
    """
    Manager methods for the TripInvoice model.
    """

    def create_trip_invoice(self, trip=None, charges=None, description=None):
        """
        Create trip invoice.
        """

        REQUIRED_ARGS = ("trip", "charges", "description")

        enforce_all_required_arguments_are_truthy({"trip": trip, "charges": charges, "description": description}, REQUIRED_ARGS)

        trip_invoice = self.model(trip=trip, charges=charges, description=description)

        trip_invoice.clean()
        trip_invoice.save()
        return trip_invoice

class TripInvoice(AbstractBaseModel, models.Model):
    """
    Model for the invoices that are sent to Transporters.
    """

    trip = models.OneToOneField(Trip, on_delete=models.CASCADE, related_name="invoice")
    charges = HStoreField()
    description = models.CharField(max_length=1000)

    objects = TripInvoiceManager()
    active_objects = ActiveObjectsQuerySet.as_manager()

    def __str__(self):
        return f"Trip Invoice for {self.trip}."

    def clean(self):
        # TODO validate that the charges dictionary contains necessary keys, eg cost per distance, etc
        RATE_CHOICES = ("per_tonne", "per_km_per_tonne", "per_truck_load")

        for key in RATE_CHOICES:
            if key not in self.charges.keys():
                raise ValidationError({"charges": f"{key} must be provided."})

        # if a key is passed that shouldn't be included, we remove it.
        for key in self.charges.copy().keys():
            if key not in RATE_CHOICES:
                self.charges.pop(key)
        return super().clean()


class RatingsManager(models.Manager):
    """
    Manager class for the Ratings model.
    """

    def create_rating(self, reviewer=None, trip=None, body=None, points=None):
        """
        Create a review.
        """

        REQUIRED_ARGS = ("reviewer", "body", "points", "trip")

        enforce_all_required_arguments_are_truthy({"reviewer": reviewer, "trip": trip, "body": body, "points": points}, REQUIRED_ARGS)

        rating = self.model(reviewer=reviewer, trip=trip, body=body, points=points)

        rating.save()
        return rating


# should this be it's own app?
class Rating(AbstractBaseModel, models.Model):
    """
    Model for all ratings
    """

    # is the reviewer a User instance or a CargoOwner instance?
    reviewer = models.ForeignKey(CargoOwnerCompany, on_delete=models.CASCADE, related_name="ratings")
    body = models.CharField(max_length=1000)
    points = models.IntegerField()
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name="ratings")

    objects = RatingsManager()
    active_objects = ActiveObjectsQuerySet.as_manager()

    def __str__(self):
        return f"Review by {self.reviewer.company_name} for {self.trip}."
