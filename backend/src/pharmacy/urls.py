from django.urls import path

from .views import InventoryListView, PharmacyListView

urlpatterns = [
    path('', PharmacyListView.as_view()),
    path('<uuid:pharmacy_uuid>/mask-sold/', InventoryListView.as_view()),
]
