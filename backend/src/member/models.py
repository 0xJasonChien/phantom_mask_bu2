from django.db import models

from core.models import BaseModel


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
    mask_name = models.ForeignKey('pharmacy.Mask', null=True, on_delete=models.SET_NULL)
    amount = models.FloatField()
    quantity = models.PositiveIntegerField()
    purchase_date = models.DateTimeField()
