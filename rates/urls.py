from django.urls import path
from rates.views import ListRates, RetrieveUpdateDeleteRates

urlpatterns = [
    path("", ListRates.as_view(), name="create-rates"),
    path("<int:pk>/", RetrieveUpdateDeleteRates.as_view(), name="update_list"),
]
