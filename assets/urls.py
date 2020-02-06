from django.urls import path
from . import views

urlpatterns = [
    path('truck-csv-upload/', views.TruckCsvUploadView.as_view(),
         name='truck_csv_upload'),
    path('trailer-csv-upload/', views.TruckCsvUploadView.as_view(),
         name='trailer_csv_upload'),
    path('truck/', views.TruckListCreateAPIView.as_view(), name='trucks'),
    path('truck/<int:pk>/',
         views.TruckRetrieveUpdateDestroyAPIView.as_view(), name='truck'),
    path('trailer/', views.TrailerListCreateAPIView.as_view(), name='trailers'),
    path('trailer/<int:pk>/', views.TrailerRetrieveUpdateDestroyAPIView.as_view(),
         name='trailers')
]
