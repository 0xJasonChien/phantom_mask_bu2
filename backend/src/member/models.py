from __future__ import annotations

from typing import TYPE_CHECKING

from django.db import models
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from core.config.env_config import settings
from core.models import BaseModel
from pharmacy.models import Inventory, InventorySnapshot, Pharmacy

if TYPE_CHECKING:

    from .serializers import PurchaseHistoryCreateSerializer


class Member(BaseModel):
    name = models.CharField(max_length=50)
    cash_balance = models.FloatField(default=0.0)


class PurchaseHistory(BaseModel):
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    inventory = models.ForeignKey(InventorySnapshot, on_delete=models.PROTECT)
    amount = models.FloatField()

    quantity = models.PositiveIntegerField()
    purchase_date = models.DateTimeField()

    @classmethod
    def bulk_create_for_member(
        cls: PurchaseHistory,
        member: Member,
        serializer: PurchaseHistoryCreateSerializer,
    ) -> list[PurchaseHistory]:
        created_inventory_list = []
        to_purchase_inventory_uuid_list = [
            str(data['inventory_uuid']) for data in serializer.validated_data
        ]
        to_purchase_pharmacy_uuid = (
            Inventory.objects.filter(
                uuid__in=to_purchase_inventory_uuid_list,
            )
            .values_list(
                'pharmacy',
                flat=True,
            )
            .distinct()
        )

        with (
            Inventory.lock_query(
                uuid_list=to_purchase_inventory_uuid_list,
            ) as locked_inventory_qs,
            Pharmacy.lock_query(
                uuid_list=to_purchase_pharmacy_uuid,
            ) as locked_pharmacy_qs,
        ):
            inventory_mapping = {
                str(inventory.uuid): inventory for inventory in locked_inventory_qs
            }
            pharmacy_mapping = {
                str(pharmacy.uuid): pharmacy for pharmacy in locked_pharmacy_qs
            }

            for data in serializer.validated_data:
                inventory = inventory_mapping[str(data['inventory_uuid'])]
                pharmacy = pharmacy_mapping[str(inventory.pharmacy.uuid)]
                if inventory.stock_quantity < data['quantity']:
                    msg = {
                        'detail': f'Inventory: {inventory.uuid}/{inventory.name} is out of stock.',
                    }
                    raise ValidationError(msg)

                # construct purchase history
                inventory_snapshot = inventory.create_snapshot()
                amount = data['quantity'] * inventory_snapshot.price
                if amount > member.cash_balance:
                    msg = {
                        'detail': f'Member cash balance:{member.cash_balance} is not enough.',
                    }
                    raise ValidationError(msg)

                purchase_history = cls.objects.create(
                    member=member,
                    inventory=inventory_snapshot,
                    amount=amount,
                    quantity=data['quantity'],
                    purchase_date=timezone.now(),
                )
                created_inventory_list.append(purchase_history)

                # update stock quantity
                inventory.stock_quantity -= data['quantity']
                member.cash_balance -= amount
                pharmacy.cash_balance += amount

            # bulk update for inventory, pharmacy, member
            Inventory.objects.bulk_update(
                list(inventory_mapping.values()),
                fields=['stock_quantity'],
                batch_size=settings.BATCH_SIZE,
            )
            Pharmacy.objects.bulk_update(
                list(pharmacy_mapping.values()),
                fields=['cash_balance'],
                batch_size=settings.BATCH_SIZE,
            )
            member.save()

        return created_inventory_list
