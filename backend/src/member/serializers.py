from rest_framework import serializers

from member.models import PurchaseHistory
from pharmacy.serializers import PharmacySerializer


class MultiplePurchaseHistoryCreateSerializer(serializers.Serializer):

    class NestedPurchaseHistoryCreateSerializer(serializers.ModelSerializer):
        class Meta:
            model = PurchaseHistory
            fields = (
                'name',
                'color',
                'count_per_pack',
                'amount',
                'quantity',
                'purchase_date',
            )

    pharmacy_uuid = serializers.UUIDField(write_only=True)
    purchase_history = NestedPurchaseHistoryCreateSerializer(
        many=True,
        help_text='購買紀錄',
    )


class PurchaseHistoryListSerializer(serializers.ModelSerializer):
    pharmacy = PharmacySerializer(read_only=True)

    class Meta:
        model = PurchaseHistory
        fields = (
            'pharmacy',
            'uuid',
            'name',
            'color',
            'count_per_pack',
            'amount',
            'quantity',
            'purchase_date',
        )


class PurchaseRankingSerializer(serializers.Serializer):
    member__uuid = serializers.UUIDField(help_text='會員 uuid')
    member__name = serializers.CharField(help_text='會員姓名')
    accumulated_amount = serializers.FloatField(help_text='統計消費金額')
