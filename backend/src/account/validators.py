from __future__ import annotations

from typing import TYPE_CHECKING, Self

from captcha.models import CaptchaStore
from django.utils import timezone
from rest_framework.exceptions import AuthenticationFailed

if TYPE_CHECKING:
    from collections import OrderedDict


class CaptchaValidator:
    def __call__(self: Self, value: OrderedDict) -> None:
        captcha = value['captcha']
        captcha_hash_key = value['captcha_hash_key']

        try:
            captcha_store = CaptchaStore.objects.get(hashkey=captcha_hash_key)
        except CaptchaStore.DoesNotExist as exc:
            msg = {'detail': f'Invalid Captcha Hash Key: {captcha_hash_key}'}
            raise AuthenticationFailed(msg) from exc

        if captcha_store.expiration < timezone.localtime():
            msg = {'detail': f'Invalid Captcha Hash Key: {captcha_hash_key}'}
            raise AuthenticationFailed(msg)

        if captcha.lower() != captcha_store.response:
            msg = {'detail': f'Invalid Captcha: {captcha}'}
            raise AuthenticationFailed(msg)

        CaptchaStore.remove_expired()
