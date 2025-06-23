from django.urls import path

from .views import (
    InventoryBulkCreateView,
    InventoryBulkUpdateView,
    InventoryCountView,
    InventoryListView,
    InventoryPerPharmacyListView,
    InventoryQuantityUpdateView,
    PharmacyListView,
)

urlpatterns = [
    path('', PharmacyListView.as_view()),
    path('<uuid:uuid>/inventory/', InventoryPerPharmacyListView.as_view()),
    path(
        '<uuid:uuid>/inventory/bulk-create/',
        InventoryBulkCreateView.as_view(),
    ),
    path('<uuid:uuid>/inventory/bulk-update/', InventoryBulkUpdateView.as_view()),
    path('inventory/', InventoryListView.as_view()),
    path('inventory/count/', InventoryCountView.as_view()),
    path(
        'inventory/<uuid:uuid>/update-quantity/',
        InventoryQuantityUpdateView.as_view(),
    ),
]
