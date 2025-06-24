from __future__ import annotations

from typing import TYPE_CHECKING, Self

from django.db import IntegrityError, models
from rest_framework.exceptions import ValidationError

from core.config.env_config import settings
from core.models import BaseModel
from pharmacy.enums import WeekDay

if TYPE_CHECKING:
    from django.db.models.query import QuerySet

    from pharmacy.serializers import (
        InventoryBulkCreateSerializer,
        InventoryBulkUpdateSerializer,
    )


class Pharmacy(BaseModel):
    name = models.CharField(max_length=50)
    cash_balance = models.FloatField(default=0.0)


class OpeningHour(BaseModel):
    pharmacy = models.ForeignKey(Pharmacy, on_delete=models.CASCADE)
    weekday = models.CharField(choices=WeekDay.choices, max_length=4)
    start_time = models.TimeField()

    end_time = models.TimeField()


class Inventory(BaseModel):
    pharmacy = models.ForeignKey(Pharmacy, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    color = models.CharField(max_length=50)

    count_per_pack = models.PositiveIntegerField()
    price = models.FloatField()
    stock_quantity = models.PositiveIntegerField()

    @classmethod
    def bulk_create_for_pharmacy(
        cls: Inventory,
        pharmacy: Pharmacy,
        serializer: InventoryBulkCreateSerializer,
    ) -> QuerySet:
        to_create_inventory = [
            cls(
                pharmacy=pharmacy,
                name=item['name'],
                color=item['color'],
                count_per_pack=item['count_per_pack'],
                price=item['price'],
                stock_quantity=item['stock_quantity'],
            )
            for item in serializer.validated_data
        ]
        try:
            created_inventories = cls.objects.bulk_create(
                to_create_inventory,
                batch_size=settings.BATCH_SIZE,
            )
        except IntegrityError as e:
            msg = {
                'detail': 'Duplicate inventory entries detected. item must be unique by name, color, and count_per_pack for a pharmacy.',
            }
            raise ValidationError(msg) from e

        return created_inventories

    @classmethod
    def bulk_update_for_pharmacy(
        cls: Inventory,
        pharmacy: Pharmacy,
        serializer: InventoryBulkUpdateSerializer,
    ) -> QuerySet:
        inventory_qs = cls.objects.filter(pharmacy=pharmacy)
        inventory_uuid_mapping = {str(item.uuid): item for item in inventory_qs}

        to_update_inventory = []
        for item in serializer.validated_data:
            inventory = inventory_uuid_mapping.get(item['uuid'])
            if inventory is None:
                msg = {
                    'detail': f'Inventory with uuid {item["uuid"]} for Pharmacy {pharmacy.uuid} does not exist.',
                }
                raise ValidationError(
                    msg,
                )

            inventory.__dict__.update(item)
            to_update_inventory.append(inventory)

        try:
            cls.objects.bulk_update(
                to_update_inventory,
                fields=['name', 'color', 'count_per_pack'],
                batch_size=settings.BATCH_SIZE,
            )
        except IntegrityError as e:
            msg = {
                'detail': 'Duplicate inventory entries detected. item must be unique by name, color, and count_per_pack for a pharmacy.',
            }
            raise ValidationError(msg) from e

        return to_update_inventory

    def create_snapshot(self: Self) -> InventorySnapshot:
        return InventorySnapshot.objects.create(
            pharmacy=self.pharmacy,
            inventory=self,
            pharmacy_name=self.pharmacy.name,
            inventory_name=self.name,
            color=self.color,
            count_per_pack=self.count_per_pack,
            price=self.price,
        )

    class Meta:
        unique_together = ('pharmacy', 'name', 'color', 'count_per_pack')


class InventorySnapshot(BaseModel):
    pharmacy = models.ForeignKey(Pharmacy, on_delete=models.SET_NULL, null=True)
    inventory = models.ForeignKey(Inventory, on_delete=models.SET_NULL, null=True)

    pharmacy_name = models.CharField(max_length=50)
    inventory_name = models.CharField(max_length=50)
    color = models.CharField(max_length=50)

    count_per_pack = models.PositiveIntegerField()
    price = models.FloatField()
