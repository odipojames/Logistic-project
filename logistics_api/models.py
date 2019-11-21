from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import date
import datetime

# Create your models here.

class Role(models.Model):
    role_choices = (('admin','admin'),('employee','employee'),('transporter','transporter'),('cargo owner','cargo owner'))
    name = models.CharField(max_length=200,choices=role_choices,null=True)

    def __str__(self):
        return self.name


class User(AbstractUser):
    firstName = models.CharField(max_length=300, null=True)
    lastName = models.CharField(max_length=300,null=True)
    username = models.CharField(max_length=300,unique=True)
    email = models.EmailField(null=True)
    password = models.CharField(max_length=200,null=True)
    password2 = models.CharField(max_length=200,null=True)
    phoneNumber =models.CharField(max_length=15,null=True)
    active = models.BooleanField(null=True)
    varified = models.BooleanField(null=True)
    role = models.ForeignKey(Role,on_delete=models.CASCADE ,null=True)
    def __str__(self):
        return self.username


class ResetPasswordToken(models.Model):
    userId = models.ForeignKey(User,null=True,on_delete=models.CASCADE)
    status = models.CharField(max_length=200,null=True)
    token = models.CharField(max_length=2000,null=True)
    date  = models.DateField(("Date"),null=True)


class Company(models.Model):
    company_type = models.CharField(max_length=200,null=True)
    companyName = models.CharField(max_length=200,null=True)
    location = models.CharField(max_length=200,null=True)

    def __str__(self):
        return self.companyName


class Employee(models.Model):
    name = models.ForeignKey(User,on_delete=models.CASCADE,null=True)
    company = models.ForeignKey(Company,on_delete=models.CASCADE)
    KRAPIN = models.CharField(max_length =200,null=True)
    POCName = models.CharField(max_length =200,null=True)
    POCnumber = models.CharField(max_length =200,null=True)
    role = models.ForeignKey(Role,on_delete=models.CASCADE,null=True)


    def __str__(self):
        return self.name


class CargoType(models.Model):
    name = models.CharField(max_length=200,null=True)
    description = models.TextField()

    def __str__(self):
        return self.name


class Truck(models.Model):
    name = models.CharField(max_length=200,null=True)
    type = models.CharField(max_length=200,null=True)
    plate = models.CharField(max_length=200,null=True)

    def __str__(self):
        return self.plate
