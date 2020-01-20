from django.urls import path
from .views import CargoTypeList,CargoTypeRetrieveUpdateDestroy,CommodityList,CommodityRetrieveUpdateDestroy


urlpatterns = [
    path('cargo_type/',CargoTypeList.as_view(),name='cargo_type'),
    path('cargo_type/<int:pk>',CargoTypeRetrieveUpdateDestroy.as_view(),name='cargo_type_detail'),
    path('commodity/',CommodityList.as_view(),name='commodities'),
    path('commodity/<int:pk>',CommodityRetrieveUpdateDestroy.as_view(),name='commodity'),

]
