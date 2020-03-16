from django.contrib import admin
from .models import (
    TransporterCompany,
    CargoOwnerCompany,
    PersonOfContact,
    Company,
    Shypper,
)


admin.site.register(CargoOwnerCompany)
admin.site.register(TransporterCompany)
admin.site.register(PersonOfContact)
admin.site.register(Shypper)
admin.site.register(Company)
