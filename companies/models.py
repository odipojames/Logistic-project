from django.db import models, IntegrityError
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from utils.models import AbstractBaseModel, ActiveObjectsQuerySet
from utils.helpers import enforce_all_required_arguments_are_truthy
from authentication.models import User, UserManager
from utils.validators import validate_file_extension, validate_international_phone_number
from cargo_types.models import Commodity

class PersonOfContactManager(models.Manager):
    """
    Points of Contact manager for cargo owner to creating
    people to contact
    """
    def create_person_of_contact(self, company=None, name=None, email=None, phone=None):
        REQUIRED_ARGS = ('company','name', 'phone')
        enforce_all_required_arguments_are_truthy({'company' : company, 'name' : name, 'email' : email, 'phone' : phone}, REQUIRED_ARGS)
        person_of_contact = self.model(company=company, name=name, email=email, phone=phone)
        person_of_contact.save()
        return person_of_contact

class PersonOfContactQuerySet(ActiveObjectsQuerySet):
    """Queryset to be used by PersonOfContact model"""
    def get_person_of_contact(self, company=None):
        """returns person of contact a specific cargo owner"""
        return self._active().filter(company=company)

class Company(models.Model):
    # business details
    business_name = models.CharField(max_length=20,unique=True)
    business_type = models.CharField(max_length=200, choices=[(
        'single', 'single'), ('Corporate', 'Corporate'), ('others', 'others')])
    account_number = models.CharField(max_length=50,unique=True)
    prefered_currency = models.CharField(max_length=200)
    logo = models.ImageField(upload_to='documents/')
    business_phone_no = models.CharField(max_length=20, validators=[validate_international_phone_number],unique=True)
    business_email = models.EmailField(unique=True)
    postal_code = models.CharField(max_length=50, null=True)
    location = models.CharField(
        max_length=200, help_text='Street, City, Country')
    company_director = models.OneToOneField(User, on_delete=models.CASCADE)
    # operations deatails
    operational_regions = models.CharField(max_length=30, choices=[(
        "locals", "locals"), ('transit', 'transit'), ('both', 'both')])
    is_active = models.BooleanField(default=False)
    # documents
    certificate_of_incorporation = models.FileField(
        upload_to="documents/", validators=[validate_file_extension])
    directors_id = models.FileField(
        upload_to="documents/", validators=[validate_file_extension])


    objects = models.Manager()
    class Meta:
        abstract = True


class CargoOwnerCompany(AbstractBaseModel, Company):  # inherits from company model
    # operations deatails
    potential_monthly_tonnage = models.CharField(max_length=200)
    operational_hours = models.CharField(
        max_length=200, help_text='e.g Mon-Fri: 8-5, Mon-Sun 8-5 e.t.c')
    employees = models.ForeignKey(User,on_delete=models.CASCADE,null=True,blank=True,related_name='employer_cargo')

    active_objects = ActiveObjectsQuerySet.as_manager()

    def __str__(self):

        return self.business_name


class TransporterCompany(AbstractBaseModel, Company):
    # operations deatails
    number_of_trucks = models.CharField(
        max_length=200, help_text='truck types + quantity')
    number_of_drivers = models.PositiveIntegerField()
    # documents
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
    employees = models.ForeignKey(User,on_delete=models.CASCADE,null=True,blank=True,related_name='employer_transporter')

    active_objects = ActiveObjectsQuerySet.as_manager()

    def __str__(self):
        return self.business_name


class PersonOfContact(AbstractBaseModel):
    company = models.ForeignKey('companies.CargoOwnerCompany', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, validators=[validate_international_phone_number], unique=True)

    objects = PersonOfContactManager()
    active_objects = PersonOfContactQuerySet.as_manager()

    def __str__(self):
        return self.phone


class Shypper(AbstractBaseModel,Company) :
    employees = models.ForeignKey(User,on_delete=models.CASCADE,null=True,blank=True,related_name='employer_shypper')

    active_objects = ActiveObjectsQuerySet.as_manager()

    def str__(self):
        return self.business_name
