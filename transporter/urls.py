from django.urls import path
from .views import DriverListCreateView, DriverDetailView
from transporter import views

urlpatterns = [
    path('drivers/', DriverListCreateView.as_view(), name="drivercreate_list"),
    path('drivers/<int:id>', DriverDetailView.as_view(), name="driver-detail"),                                           
]