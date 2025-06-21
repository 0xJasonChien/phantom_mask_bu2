from django.db import models

from core.models import BaseModel
from pharmacy.enums import WeekDay


class Pharmacy(BaseModel):
    name = models.CharField(max_length=50)
    cash_balance = models.FloatField(default=0.0)


class OpeningHour(BaseModel):
    pharmacy = models.ForeignKey(Pharmacy, on_delete=models.CASCADE)
    weekday = models.CharField(choices=WeekDay.choices, max_length=4)
    start_time = models.TimeField()
    end_time = models.TimeField()


class Mask(BaseModel):
    name = models.CharField(max_length=50)
    color = models.CharField(max_length=50)
    count_per_pack = models.PositiveIntegerField()

    class Meta:
        unique_together = ('name', 'color', 'count_per_pack')


class Inventory(BaseModel):
    pharmacy = models.ForeignKey(Pharmacy, on_delete=models.CASCADE)
    mask_name = models.ForeignKey(Mask, on_delete=models.PROTECT)
    price = models.FloatField()
    stock_quantity = models.PositiveIntegerField()

    class Meta:
        unique_together = ('pharmacy', 'mask_name')
