from django.db import models
from authentication.models import User
from datetime import date
import datetime

# Create your models here.


class ResetPasswordToken(models.Model):
    userId = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    status = models.CharField(max_length=200, null=True)
    token = models.CharField(max_length=2000, null=True)
    date = models.DateField(("Date"), null=True)


class Company(models.Model):
    company_type = models.CharField(max_length=200, null=True)
    companyName = models.CharField(max_length=200, null=True)
    location = models.CharField(max_length=200, null=True)

    def __str__(self):
        return self.companyName


class Employee(models.Model):
    name = models.ForeignKey(User, on_delete=models.CASCADE, null=True,)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    KRAPIN = models.CharField(max_length=200, null=True)
    POCName = models.CharField(max_length=200, null=True)
    POCnumber = models.CharField(max_length=200, null=True)

    def __str__(self):
        return self.name


class CargoType(models.Model):
    name = models.CharField(max_length=200, null=True)
    description = models.TextField()

    def __str__(self):
        return self.name


class Truck(models.Model):
    name = models.CharField(max_length=200, null=True)
    type = models.CharField(max_length=200, null=True)
    plate = models.CharField(max_length=200, null=True)

    def __str__(self):
        return self.plate
