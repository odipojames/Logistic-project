from django.contrib import admin

from .models import Trip, TripInvoice, Event

# Register your models here.
admin.site.register(Trip)
admin.site.register(TripInvoice)
admin.site.register(Event)
