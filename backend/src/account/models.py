from django.contrib.auth.models import AbstractUser
from django.db import models

from core.models import BaseModel


class User(BaseModel, AbstractUser):
    email = models.EmailField(unique=True, verbose_name=('email address'))
    username = models.CharField(max_length=50, verbose_name='使用者名稱')

    last_name, first_name = None, None  # remove default first and last name fields
    REQUIRED_FIELDS = ('username',)
    USERNAME_FIELD = 'email'  # Use email as the primary identifier for login
