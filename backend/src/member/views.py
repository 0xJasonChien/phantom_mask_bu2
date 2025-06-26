from typing import ClassVar, Self

from django.db.models import F, QuerySet, Sum
from django.http import HttpRequest, HttpResponse
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED

from .models import Member, PurchaseHistory
from .serializers import (
    PurchaseHistoryCreateSerializer,
    PurchaseHistoryListSerializer,
    PurchaseRankingSerializer,
)


class PurchaseHistoryCreateView(CreateAPIView):
    serializer_class = PurchaseHistoryCreateSerializer
    queryset = Member.objects.all()

    def create(
        self: Self,
        request: HttpRequest,
        *args: tuple,
        **kwargs: dict,
    ) -> HttpResponse:
        member = Member.objects.get(uuid=self.kwargs['uuid'])
        serializer = self.get_serializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)

        created_purchase_history = PurchaseHistory.bulk_create_for_member(
            member,
            serializer,
        )
        response_serializer = PurchaseHistoryListSerializer(
            created_purchase_history,
            many=True,
        )

        return Response(
            response_serializer.data,
            status=HTTP_201_CREATED,
        )

    @extend_schema(
        operation_id='新增購買紀錄',
        request=PurchaseHistoryCreateSerializer(many=True),
        responses={
            HTTP_201_CREATED: PurchaseHistoryListSerializer(many=True),
        },
    )
    def post(
        self: Self,
        request: HttpRequest,
        *args: tuple,
        **kwargs: dict,
    ) -> HttpResponse:
        return super().post(request, *args, **kwargs)


class PurchaseRankingListView(ListAPIView):
    queryset = PurchaseHistory.objects.all()
    serializer_class = PurchaseRankingSerializer
    filterset_fields: ClassVar = {
        'purchase_date': ['gte', 'lte', 'gt', 'lt', 'exact'],
    }

    def get_queryset(self: Self) -> QuerySet:
        top = self.request.query_params.get('top')
        queryset = (
            super()
            .get_queryset()
            .select_related('member')
            .values('member__uuid', 'member__name')
            .annotate(
                accumulated_amount=Sum('amount'),
                cash_balance=F('member__cash_balance'),
            )
            .order_by('-accumulated_amount')
        )

        if top:
            return queryset[: int(top)]
        return queryset

    @extend_schema(
        operation_id='取得購買排行榜',
        parameters=[
            OpenApiParameter(
                name='top',
                type=int,
                location=OpenApiParameter.QUERY,
                description='Get the top N buyers',
                required=False,
            ),
        ],
    )
    def get(
        self: Self,
        request: HttpRequest,
        *args: tuple,
        **kwargs: dict,
    ) -> HttpResponse:
        return super().get(request, *args, **kwargs)
