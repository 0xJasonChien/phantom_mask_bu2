from django.urls import path

from .views import PurchaseHistoryCreateView, PurchaseRankingListView

urlpatterns = [
    path('<uuid:uuid>/create-purchase-history/', PurchaseHistoryCreateView.as_view()),
    path('purchase-ranking/', PurchaseRankingListView.as_view()),
]
