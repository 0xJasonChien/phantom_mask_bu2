from django.db import models


class WeekDay(models.TextChoices):
    MONDAY = 'Mon', 'Monday'
    TUESDAY = 'Tue', 'Tuesday'
    WEDNESDAY = 'Wed', 'Wednesday'
    THURSDAY = 'Thur', 'Thursday'
    FRIDAY = 'Fri', 'Friday'
    SATURDAY = 'Sat', 'Saturday'
    SUNDAY = 'Sun', 'Sunday'
