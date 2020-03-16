from django.urls import path
from orders.views import ListCreateOrder, RetrieveUpdateDeleteOrder

urlpatterns = [
    path("orders/", ListCreateOrder.as_view(), name="create-list-orders"),
    path(
        "orders/<str:tracking_id>/",
        RetrieveUpdateDeleteOrder.as_view(),
        name="order-detail",
    ),
]
