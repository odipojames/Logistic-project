from django.db import models, IntegrityError
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from utils.models import AbstractBaseModel, ActiveObjectsQuerySet
from utils.helpers import enforce_all_required_arguments_are_truthy


class EmployerManager(models.Manager):
    """
    Manager method for the employer model.
    """
    pass

# TODO: should this be renamed to Company?
class Employer(AbstractBaseModel, models.Model):
    """
    This model will simply contain all employees of a company.
    """

    employer_code = models.CharField(max_length=100, unique=True)


    objects = EmployerManager()
    active_objects = ActiveObjectsQuerySet.as_manager()

    def __str__(self):
        return self.employer_code


class CargoOwnerManager(models.Manager):
    """
    The manager class for the CargoOwner model. Each instance must be tied to only one Employer.
    """

    def create_cargo_owner(self, company_name=None, company_admin=None, employer_code=None, company_location=None, **kwargs):
        """
        The method to actually create a Cargo Owner.
        """

        REQUIRED_ARGS = ("company_name", "company_admin", "employer_code", "company_location")

        enforce_all_required_arguments_are_truthy(
            {"company_name": company_name,
            "company_admin": company_admin,
            "employer_code": employer_code,
            "company_location": company_location},
            REQUIRED_ARGS)

        if not isinstance(company_admin, get_user_model()):
            raise ValidationError({"company_admin": "Provide a user instance for the admin."})

        # We either get or create a new employer if there is none.
        employer = Employer.objects.get_or_create(employer_code=employer_code)[0]
        
        company = self.model(company_name=company_name, company_admin=company_admin, employer_code=employer, company_location=company_location, **kwargs)

        company.save()
        return company

class CargoOwner(AbstractBaseModel, models.Model):
    """
    This model represents the entity that owns cargo to be transported on the platform.
    """

    company_name = models.CharField(max_length=100)
    company_admin = models.OneToOneField(get_user_model(), on_delete=models.CASCADE, related_name="cargo_company_admin")
    company_location = models.ForeignKey('locations.Location', on_delete=models.CASCADE, related_name="cargo_owners")
    employer_code = models.OneToOneField(Employer, to_field="employer_code", on_delete=models.CASCADE, related_name="cargo_company")

    objects = CargoOwnerManager()

    active_objects = ActiveObjectsQuerySet.as_manager()

    def __str__(self):
        return self.company_name


class TransporterManager(models.Manager):
    """
    Contains manager methods for the Transport class.
    """

    def create_transporter(self, company_name=None, company_admin=None, employer_code=None, company_location=None, **kwargs):
        """
        Create a transporter
        """

        if not isinstance(company_admin, get_user_model()):
            raise ValidationError({"company_admin": "Provide a user instance for the admin."})

        REQUIRED_ARGS = ("company_name", "company_admin", "employer_code", "copmany_location")

        enforce_all_required_arguments_are_truthy({"company_name": company_name, "company_admin": company_admin, "employer_code": employer_code, "company_location": company_location}, REQUIRED_ARGS)

        employer = Employer.objects.get_or_create(employer_code=employer_code)[0]

        transporter = self.model(company_admin=company_admin, company_name=company_name, employer_code=employer, company_location=company_location, **kwargs)

        transporter.save()
        return transporter


class Transporter(AbstractBaseModel, models.Model):
    """
    This model represents a Transporter.
    """

    company_name = models.CharField(max_length=100)
    company_admin = models.OneToOneField(get_user_model(), on_delete=models.CASCADE, related_name="transporter_company_admin")

    company_location = models.ForeignKey('locations.Location', on_delete=models.CASCADE, related_name="transporters")
    employer_code = models.OneToOneField(Employer, to_field="employer_code", on_delete=models.CASCADE, related_name="transporter_company")

    objects = TransporterManager()

    active_objects = ActiveObjectsQuerySet.as_manager()

    def __str__(self):
        return self.company_name
