from __future__ import annotations

from typing import TYPE_CHECKING

from django.db import IntegrityError, models
from rest_framework.exceptions import ValidationError

from core.models import BaseModel

if TYPE_CHECKING:
    from django.db.models.query import QuerySet

    from .serializers import MultiplePurchaseHistoryCreateSerializer


class Member(BaseModel):
    name = models.CharField(max_length=50)
    cash_balance = models.FloatField(default=0.0)


class PurchaseHistory(BaseModel):
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    pharmacy = models.ForeignKey(
        'pharmacy.Pharmacy',
        null=True,
        on_delete=models.SET_NULL,
    )

    name = models.CharField(max_length=50)
    color = models.CharField(max_length=50)
    count_per_pack = models.PositiveIntegerField()

    amount = models.FloatField()
    quantity = models.PositiveIntegerField()
    purchase_date = models.DateTimeField()

    @classmethod
    def bulk_create_for_member(
        cls: PurchaseHistory,
        member: Member,
        serializer: MultiplePurchaseHistoryCreateSerializer,
    ) -> QuerySet:
        to_create_purchase_history = [
            cls(
                member=member,
                pharmacy_id=data['pharmacy_uuid'],
                name=history['name'],
                color=history['color'],
                count_per_pack=history['count_per_pack'],
                amount=history['amount'],
                quantity=history['quantity'],
                purchase_date=history['purchase_date'],
            )
            for data in serializer.validated_data
            for history in data['purchase_history']
        ]

        try:
            created_purchase_history_qs = cls.objects.bulk_create(
                to_create_purchase_history,
            )
        except IntegrityError as e:
            msg = {
                'detail': 'Violating unique constraint. One or more purchase history records could not be created.',
            }
            raise ValidationError(
                msg,
            ) from e
        else:
            return created_purchase_history_qs
