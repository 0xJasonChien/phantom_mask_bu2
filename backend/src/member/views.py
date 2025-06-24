from typing import Self

from django.db.models import F, QuerySet, Sum
from django.http import HttpRequest, HttpResponse
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED

from member.apps import MemberConfig

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

    @swagger_auto_schema(
        operation_id='新增購買紀錄',
        request_body=PurchaseHistoryCreateSerializer(many=True),
        responses={
            HTTP_201_CREATED: PurchaseHistoryCreateSerializer,
        },
        tags=(MemberConfig.name,),
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

    @swagger_auto_schema(
        operation_id='取得購買排行榜',
        responses={
            HTTP_200_OK: PurchaseRankingSerializer(many=True),
        },
        manual_parameters=[
            openapi.Parameter(
                'top',
                openapi.IN_QUERY,
                description='Get the top N buyers',
                type=openapi.TYPE_INTEGER,
            ),
        ],
        tags=(MemberConfig.name,),
    )
    def get(
        self: Self,
        request: HttpRequest,
        *args: tuple,
        **kwargs: dict,
    ) -> HttpResponse:
        return super().get(request, *args, **kwargs)
