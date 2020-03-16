from django.contrib import admin
from .models import CargoType, Commodity

# Register your models here.
admin.site.register(CargoType)
admin.site.register(Commodity)
