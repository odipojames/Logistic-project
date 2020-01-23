from django.urls import path
from . views import DepotList,DepotRetrieveUpdateDestroy


urlpatterns = [
    path('depot/',DepotList.as_view(),name='DepotList'),
    path('depot/<int:pk>',DepotRetrieveUpdateDestroy.as_view(),name='depot_details'),


]
