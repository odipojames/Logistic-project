from django.contrib import admin


from .models import Employer, CargoOwner, Transporter

admin.site.register(Employer)
admin.site.register(CargoOwner)
admin.site.register(Transporter)
