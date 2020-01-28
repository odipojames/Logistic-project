from django.contrib import admin
from .models import TransporterCompany,CargoOwnerCompany, PersonOfContact





admin.site.register(CargoOwnerCompany)
admin.site.register(TransporterCompany)
admin.site.register(PersonOfContact)
