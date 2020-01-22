from django.urls import path
from . import views

urlpatterns = [
    path('truck-csv-upload/', views.TruckCsvUploadView.as_view(), name='truck_csv_upload'),
    path('trailer-csv-upload/', views.TruckCsvUploadView.as_view(), name='trailer_csv_upload')
]
