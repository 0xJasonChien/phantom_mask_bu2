from __future__ import annotations

import uuid
from contextlib import contextmanager
from typing import TYPE_CHECKING
from uuid import UUID

from django.db import models, transaction

if TYPE_CHECKING:
    from collections.abc import Generator

    from django.db.models.query import QuerySet


class BaseModel(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def __str__(self) -> str:
        return f' {self.__class__.__name__} - {self.uuid}'

    @classmethod
    @contextmanager
    def lock_query(
        cls: type[BaseModel],
        uuid_list: list[UUID],
        **kwargs: dict,  # for extra custom filters
    ) -> Generator[QuerySet[BaseModel], None, None]:
        try:
            with transaction.atomic():
                queryset = cls.objects.select_for_update().filter(
                    uuid__in=uuid_list,
                    **kwargs,
                )
                yield queryset
        except Exception as e:  # noqa: TRY203
            raise e  # noqa: TRY201

    @classmethod
    @contextmanager
    def lock_instance(
        cls: type[BaseModel],
        uuid: UUID,
    ) -> Generator[QuerySet[BaseModel], None, None]:
        try:
            with transaction.atomic():
                queryset = cls.objects.select_for_update().get(uuid=uuid)
                yield queryset
        except Exception as e:  # noqa: TRY203
            raise e  # noqa: TRY201
