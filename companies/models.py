from django.db import models, IntegrityError
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from utils.models import AbstractBaseModel, ActiveObjectsQuerySet
from utils.helpers import enforce_all_required_arguments_are_truthy
from authentication.models import User, UserManager
from utils.validators import validate_file_extension


class Company(models.Model):
    # busiss deatails
    business_name = models.CharField(max_length=20)
    business_type = models.CharField(max_length=200, choices=[(
        'single', 'single'), ('Corporate', 'Corporate'), ('others', 'others')])
    account_number = models.CharField(max_length=50)
    prefered_currency = models.CharField(max_length=200)
    logo = models.ImageField(upload_to='documents/')
    contact_details = models.CharField(max_length=300)
    location = models.CharField(
        max_length=200, help_text='Street, City, Country')
    company_director = models.OneToOneField(User, on_delete=models.CASCADE)
    # operations deatails
    operational_regions = models.CharField(max_length=30, choices=[(
        "locals", "locals"), ('transit', 'transit'), ('both', 'both')])
    is_active = models.BooleanField(default=False)
    # orthers
    person_of_contact = models.CharField(
        max_length=200, help_text='e.g Sales Person')
    # documents
    certificate_of_incorporation = models.FileField(
        upload_to="documents/", validators=[validate_file_extension])
    directors_id = models.FileField(
        upload_to="documents/", validators=[validate_file_extension])

    class Meta:
        abstract = True


class CargoOwnerCompany(AbstractBaseModel, Company):  # inherits from company model
    # operations deatails
    commodities = models.CharField(max_length=30, choices=[("Container", "Container"), (
        'Bagged and Bulk', 'Bagged and Bulk'), ('FMCG', 'Fast-Moving Customer Goods')])
    potential_monthly_tonnage = models.CharField(max_length=200)
    operational_hours = models.CharField(
        max_length=200, help_text='e.g Mon-Fri: 8-5, Mon-Sun 8-5 e.t.c')

    active_objects = ActiveObjectsQuerySet.as_manager()

    def __str__(self):

        return self.business_name


class TransporterCompany(AbstractBaseModel, Company):
    # operations deatails
    number_of_trucks = models.CharField(
        max_length=200, help_text='truck types + quantity')
    number_of_drivers = models.PositiveIntegerField()
    # documents
    truck_log_books = models.FileField(
        upload_to="documents/", validators=[validate_file_extension])
    goods_in_transit_insurance = models.FileField(
        upload_to="documents/", validators=[validate_file_extension])
    tax_compliance_certificate = models.FileField(
        upload_to="documents/", validators=[validate_file_extension])
    ntsa_inspection_certificates = models.FileField(
        upload_to="documents/", validators=[validate_file_extension])
    icdn_or_port_passes = models.FileField(
        upload_to="documents/", validators=[validate_file_extension], null=True, blank=True)
    cross_boarder_operation = models.FileField(
        upload_to="documents/", validators=[validate_file_extension])

    active_objects = ActiveObjectsQuerySet.as_manager()

    def __str__(self):
        return self.business_name

    class PersonOfContact(AbstractBaseModel):
        company = models.ForeignKey(TransporterCompany, related_name='company', on_delete=models.CASCADE)
        name = models.CharField(max_length=100)
        email = models.EmailField()
        phone = models.CharField(max_length=20)

        active_objects = ActiveObjectsQuerySet.as_manager()
