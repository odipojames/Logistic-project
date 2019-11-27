from django.db import models
from django.contrib.auth.models import User
import jwt
from django.contrib.auth.models import BaseUserManager, AbstractUser
from datetime import datetime, timedelta
from django.conf import settings


# Create your models here.

class UserManager(BaseUserManager):

    def create_user(self, last_name, first_name, username, email, company_name, role='EM', password=None):
        if first_name is None:
            raise TypError('first name is  required')
        if last_name is None:
            raise TypError('last name is  required')
        if email is None:
            raise TypError('email is  required')
        if company_name is None:
            raise TypError('company_name is  required')
        if password is None:
            raise TypError('passwad is  required')
        user = self.model(
            first_name=first_name,
            last_name=last_name,
            company_name=company_name,
            email=self.normalize_email(email),
            username=self.normalize_email(email)

        )
        user.set_password(password)
        user.role = role
        user.save()
        return user

    def create_superuser(
            self, first_name, last_name, email, password,company_name):
        '''
        create admin
        '''
        if first_name is None:
            raise TypeError('')

        if last_name is None:
            raise TypError('first name is  required')

        if email is None:
            raise TypeError('last name is  required')

        if company_name is None:
            raise TabError('your company name is required')

        if password is None:
            raise TypeError('passwad is  required')

        user = self.model(
            first_name=first_name, last_name=last_name,
            email=self.normalize_email(email), role='SA', company_name=company_name)
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.is_verified = True
        user.set_password(password)
        user.save()


class User(AbstractUser):

    USER_ROLES = (('EM', 'Employee'), ('SA', 'Shipper Admin'),
                  ('TR', 'Transporter'), ('CO', 'Cargo Owner'))
    username = models.CharField(
        max_length=200, blank=True, null=True, unique=True)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=200, choices=USER_ROLES, default='EM')
    company_name = models.CharField(max_length=200, unique=True)
    is_varified = models.BooleanField(default=False)

    REQUIRED_FIELDS = ['first_name', 'last_name','company_name']
    USERNAME_FIELD = 'email'
    objects = UserManager()

    def __str__(self):

        return self.email

    @property
    def get_email(self):

        return self.email

    @property
    def token(self):

        return self._generate_jwt_token()

    def _generate_jwt_token(self):

        token_expiry = datetime.now() + timedelta(hours=24)

        token = jwt.encode({
            'id': self.pk,
            'email': self.get_email,
            'exp': int(token_expiry.strftime('%s'))
        }, settings.SECRET_KEY, algorithm='HS256')

        return token.decode('utf-8')
