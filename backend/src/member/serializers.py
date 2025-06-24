from rest_framework import serializers

from pharmacy.models import InventorySnapshot
from pharmacy.serializers import PharmacySerializer


class PurchaseHistoryCreateSerializer(serializers.Serializer):
    inventory_uuid = serializers.UUIDField(write_only=True)
    quantity = serializers.IntegerField(help_text='購買數量')


class InventorySnapshotSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventorySnapshot
        fields = (
            'inventory_name',
            'pharmacy_name',
            'color',
            'count_per_pack',
            'price',
        )


class PurchaseHistoryListSerializer(serializers.Serializer):
    uuid = serializers.UUIDField(read_only=True)
    pharmacy = PharmacySerializer(read_only=True)
    inventory = InventorySnapshotSerializer(read_only=True)
    quantity = serializers.IntegerField(help_text='購買數量')
    purchase_date = serializers.DateTimeField(read_only=True)


class PurchaseRankingSerializer(serializers.Serializer):
    member__uuid = serializers.UUIDField(help_text='會員 uuid')
    member__name = serializers.CharField(help_text='會員姓名')
    accumulated_amount = serializers.FloatField(help_text='統計消費金額')
    cash_balance = serializers.FloatField(help_text='會員現金餘額')
