from django.urls import path
from .views import DriverListCreateView
from transporter import views

urlpatterns = [
    path('drivers/', DriverListCreateView.as_view(), name="drivercreate_list")                                             
]