from django.contrib import admin

from .models import Driver
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
# Register your models here.

admin.site.register(Driver)
