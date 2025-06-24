from typing import ClassVar, Self

from django.db.models import Sum
from django.db.models.query import QuerySet
from django.http import HttpRequest, HttpResponse
from drf_spectacular.utils import extend_schema
from rest_framework.generics import CreateAPIView, ListAPIView, UpdateAPIView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED

from core.filters import FullTextSearchFilter
from pharmacy.apps import PharmacyConfig
from pharmacy.models import Inventory, OpeningHour, Pharmacy
from pharmacy.serializers import (
    InventoryBulkCreateSerializer,
    InventoryBulkUpdateSerializer,
    InventoryCountSerializer,
    InventoryListSerializer,
    InventoryPerPharmacyListSerializer,
    InventoryUpdateSerializer,
    OpeningHourListSerializer,
)


class PharmacyListView(ListAPIView):
    """
    List pharmacies, optionally filtered by specific time and/or day of the week.
    """

    queryset = OpeningHour.objects.select_related('pharmacy').all()
    serializer_class = OpeningHourListSerializer
    filterset_fields: ClassVar = {
        'weekday': ['exact'],
        'start_time': ['gte', 'exact'],
        'end_time': ['lte', 'exact'],
    }

    @extend_schema(
        operation_id='取得藥局列表',
        tags=(PharmacyConfig.name,),
    )
    def get(
        self: Self,
        request: HttpRequest,
        *args: tuple,
        **kwargs: dict,
    ) -> HttpResponse:
        return super().get(request, *args, **kwargs)


class InventoryPerPharmacyListView(ListAPIView):
    """
    List all masks sold by a given pharmacy with an option to sort by name or price.
    """

    queryset = Inventory.objects.all()
    serializer_class = InventoryPerPharmacyListSerializer
    filterset_fields: ClassVar = {
        'name': ['in', 'exact'],
        'price': ['gte', 'lte', 'gt', 'lt', 'exact'],
    }

    def get_queryset(self: Self) -> QuerySet:
        return super().get_queryset().filter(pharmacy_id=self.kwargs['uuid'])

    @extend_schema(
        operation_id='取得藥局販售的口罩列表',
        responses={
            HTTP_200_OK: InventoryPerPharmacyListSerializer(many=True),
        },
    )
    def get(
        self: Self,
        request: HttpRequest,
        *args: tuple,
        **kwargs: dict,
    ) -> HttpResponse:
        return super().get(request, *args, **kwargs)


class InventoryCountView(ListAPIView):
    """
    List all pharmacies that offer a number of mask products within a given price range, where the count is above, below, or between given thresholds.
    """

    queryset = Inventory.objects.select_related('pharmacy').all()
    serializer_class = InventoryCountSerializer
    filterset_fields: ClassVar = {
        'price': ['gte', 'lte', 'gt', 'lt', 'exact'],
    }

    def get_queryset(self: Self) -> QuerySet:
        return (
            super()
            .get_queryset()
            .values('pharmacy__uuid', 'pharmacy__name')
            .annotate(
                inventory_count=Sum('stock_quantity'),
            )
        )

    @extend_schema(
        operation_id='取得所有藥局庫存統計',
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
        return super().get(request, *args, **kwargs)


class InventoryQuantityUpdateView(UpdateAPIView):
    """
    Update the stock quantity of an existing mask product by increasing or decreasing it.
    """

    queryset = Inventory.objects.all()
    serializer_class = InventoryUpdateSerializer
    lookup_field = 'uuid'

    def perform_update(self: Self, serializer: InventoryUpdateSerializer) -> None:
        inventory = self.get_object()
        inventory.stock_quantity += serializer.validated_data['delta']
        inventory.save()

    @extend_schema(
        operation_id='Delta 更新藥局庫存數量',
        responses={
            HTTP_200_OK: InventoryCountSerializer(many=True),
        },
    )
    def put(
        self: Self,
        request: HttpRequest,
        *args: tuple,
        **kwargs: dict,
    ) -> HttpResponse:
        return super().put(request, *args, **kwargs)

    @extend_schema(exclude=True)
    def patch(
        self: Self,
        request: HttpRequest,
        *args: tuple,
        **kwargs: dict,
    ) -> HttpResponse:
        return super().patch(request, *args, **kwargs)


class InventoryBulkUpdateView(UpdateAPIView):
    """
    Update multiple mask products for a pharmacy at once, including name, price, and stock quantity.
    """

    queryset = Pharmacy.objects.all()
    serializer_class = InventoryBulkUpdateSerializer
    lookup_field = 'uuid'

    def update(
        self: Self,
        request: HttpRequest,
        *args: tuple,
        **kwargs: dict,
    ) -> HttpResponse:
        pharmacy = self.get_object()
        serializer = self.get_serializer(
            data=request.data,
            many=True,
            partial=False,
        )
        serializer.is_valid(raise_exception=True)

        updated_inventories = Inventory.bulk_update_for_pharmacy(pharmacy, serializer)
        response_serializer = self.get_serializer(
            updated_inventories,
            many=True,
        )
        return Response(response_serializer.data)

    @extend_schema(exclude=True)
    def patch(
        self: Self,
        request: HttpRequest,
        *args: tuple,
        **kwargs: dict,
    ) -> HttpResponse:
        return super().put(request, *args, **kwargs)

    @extend_schema(
        operation_id='批次更新藥局庫存數量',
        request=InventoryBulkUpdateSerializer(many=True),
        responses={
            HTTP_200_OK: InventoryBulkUpdateSerializer(many=True),
        },
    )
    def put(
        self: Self,
        request: HttpRequest,
        *args: tuple,
        **kwargs: dict,
    ) -> HttpResponse:
        return super().put(request, *args, **kwargs)


class InventoryBulkCreateView(CreateAPIView):
    """
    Create multiple mask products for a pharmacy at once, including name, price, and stock quantity.
    """

    queryset = Pharmacy.objects.all()
    serializer_class = InventoryBulkCreateSerializer

    def create(
        self,
        request: HttpRequest,
        *args: tuple,
        **kwargs: dict,
    ) -> HttpResponse:
        pharmacy = Pharmacy.objects.get(uuid=self.kwargs['uuid'])
        serializer = self.get_serializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)

        created_inventories = Inventory.bulk_create_for_pharmacy(pharmacy, serializer)

        response_serializer = self.get_serializer(created_inventories, many=True)
        headers = self.get_success_headers(response_serializer.data)
        return Response(
            response_serializer.data,
            status=HTTP_201_CREATED,
            headers=headers,
        )

    @extend_schema(
        operation_id='批次新增藥局庫存數量',
        request=InventoryBulkCreateSerializer(many=True),
        responses={
            HTTP_200_OK: InventoryBulkCreateSerializer(many=True),
        },
    )
    def post(
        self: Self,
        request: HttpRequest,
        *args: tuple,
        **kwargs: dict,
    ) -> HttpResponse:
        return super().post(request, *args, **kwargs)


class InventoryListView(ListAPIView):
    """
    Search for pharmacies or masks by name and rank the results by relevance to the search term.
    """

    queryset = Inventory.objects.select_related('pharmacy').all()
    serializer_class = InventoryListSerializer
    search_fields = ('name', 'pharmacy__name')
    filter_backends = (FullTextSearchFilter,)

    @extend_schema(
        operation_id='取得庫存列表',
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
        return super().get(request, *args, **kwargs)
