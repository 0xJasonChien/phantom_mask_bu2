from typing import ClassVar, Self

from django.db.models import Sum
from django.db.models.query import QuerySet
from django.http import HttpRequest, HttpResponse
from drf_yasg.utils import swagger_auto_schema
from rest_framework.generics import ListAPIView
from rest_framework.status import HTTP_200_OK

from pharmacy.models import Inventory, OpeningHour
from pharmacy.serializers import (
    InventoryCountSerializer,
    InventoryListSerializer,
    OpeningHourListSerializer,
)


class PharmacyListView(ListAPIView):
    queryset = OpeningHour.objects.select_related('pharmacy').all()
    serializer_class = OpeningHourListSerializer
    filterset_fields: ClassVar = {
        'weekday': ['in'],
        'start_time': ['gte', 'exact'],
        'end_time': ['lte', 'exact'],
    }

    @swagger_auto_schema(
        operation_id='取得藥局列表',
        responses={
            HTTP_200_OK: OpeningHourListSerializer(many=True),
        },
    )
    def get(
        self: Self,
        request: HttpRequest,
        *args: tuple,
        **kwargs: dict,
    ) -> HttpResponse:
        return self.list(request, *args, **kwargs)


class InventoryListView(ListAPIView):
    queryset = Inventory.objects.select_related('pharmacy').all()
    serializer_class = InventoryListSerializer
    filterset_fields: ClassVar = {
        'weekday': ['in'],
        'start_time': ['gte', 'exact'],
        'end_time': ['lte', 'exact'],
    }
    lookup_field = 'pharmacy__uuid'

    @swagger_auto_schema(
        operation_id='取得口罩販售藥局列表',
        responses={
            HTTP_200_OK: InventoryListSerializer(many=True),
        },
    )
    def get(
        self: Self,
        request: HttpRequest,
        *args: tuple,
        **kwargs: dict,
    ) -> HttpResponse:
        return self.list(request, *args, **kwargs)


class InventoryCountView(ListAPIView):
    queryset = Inventory.objects.select_related('pharmacy').all()
    serializer_class = InventoryCountSerializer
    filterset_fields: ClassVar = {
        'price': ['gte', 'lte', 'gt', 'lt', 'exact'],
    }

    def get_queryset(self: Self) -> QuerySet:
        return (
            super()
            .get_queryset()
            .values('pharmacy')
            .annotate(
                inventory_count=Sum('stock_quantity'),
            )
        )

    @swagger_auto_schema(
        operation_id='取得藥局庫存數量',
        responses={
            HTTP_200_OK: InventoryCountSerializer(many=True),
        },
    )
    def get(
        self: Self,
        request: HttpRequest,
        *args: tuple,
        **kwargs: dict,
    ) -> HttpResponse:
        return self.list(request, *args, **kwargs)
