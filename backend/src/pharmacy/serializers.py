from rest_framework import serializers

from pharmacy.models import Inventory, OpeningHour


class OpeningHourListSerializer(serializers.ModelSerializer):
    pharmacy_name = serializers.ReadOnlyField(source='pharmacy.name')
    pharmacy_cash_balance = serializers.ReadOnlyField(source='pharmacy.cash_balance')

    class Meta:
        model = OpeningHour
        fields = (
            'uuid',
            'pharmacy_name',
            'pharmacy_cash_balance',
            'weekday',
            'start_time',
            'end_time',
        )


class InventoryListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Inventory
        fields = ('uuid', 'name', 'color', 'count_per_pack')


class InventoryCountSerializer(serializers.Serializer):
    pharmacy_name = serializers.CharField(read_only=True, source='pharmacy.name')
    mask = serializers.CharField(read_only=True, source='mask.name')
    inventory_count = serializers.IntegerField(read_only=True, source='inventory_count')


class InventoryUpdateSerializer(serializers.Serializer):
    delta = serializers.IntegerField(
        required=True,
        help_text='The change in stock quantity (can be negative)',
    )
