from rest_framework import serializers

from pharmacy.models import Inventory, OpeningHour, Pharmacy


class PharmacySerializer(serializers.ModelSerializer):
    class Meta:
        model = Pharmacy
        fields = ('name', 'cash_balance')


class OpeningHourListSerializer(serializers.ModelSerializer):
    uuid = serializers.CharField(source='pharmacy.uuid')
    pharmacy_name = serializers.CharField(source='pharmacy.name')
    pharmacy_cash_balance = serializers.FloatField(source='pharmacy.cash_balance')

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


class InventoryPerPharmacyListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Inventory
        fields = ('uuid', 'name', 'color', 'count_per_pack', 'price', 'stock_quantity')
        read_only_fields = ('uuid',)


class InventoryCountSerializer(serializers.ModelSerializer):
    uuid = serializers.CharField(source='pharmacy__uuid')
    pharmacy_name = serializers.CharField(source='pharmacy__name')
    inventory_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Inventory
        fields = ('uuid', 'pharmacy_name', 'inventory_count')


class InventoryUpdateSerializer(serializers.Serializer):
    delta = serializers.IntegerField(
        required=True,
        write_only=True,
        help_text='The change in stock quantity (can be negative)',
    )
    uuid = serializers.CharField(read_only=True)
    name = serializers.CharField(read_only=True)
    stock_quantity = serializers.IntegerField(read_only=True)


class InventoryBulkUpdateSerializer(serializers.ModelSerializer):
    uuid = serializers.CharField()

    class Meta:
        model = Inventory
        fields = ('uuid', 'name', 'color', 'count_per_pack', 'price', 'stock_quantity')


class InventoryBulkCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Inventory
        fields = ('uuid', 'name', 'color', 'count_per_pack', 'price', 'stock_quantity')
        read_only_fields = ('uuid',)


class InventoryListSerializer(serializers.ModelSerializer):
    pharmacy_uuid = serializers.CharField(source='pharmacy.uuid')
    pharmacy_name = serializers.CharField(source='pharmacy.name')
    inventory_uuid = serializers.CharField(source='uuid')
    inventory_name = serializers.CharField(source='name')

    class Meta:
        model = Inventory
        fields = (
            'pharmacy_uuid',
            'pharmacy_name',
            'inventory_uuid',
            'inventory_name',
            'color',
            'count_per_pack',
            'price',
            'stock_quantity',
        )
