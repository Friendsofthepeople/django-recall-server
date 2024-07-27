"""
Mixins that will be used for models with common characteristics.
"""

import uuid

from django.db import models


class TimeStampable(models.Model):
    """
    Base abstract timestamp model.

    This mixin is intended to be inherited by all models as it provides the
    characteristics for when a model is created/updated.
    """

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class OwnerlessAbstract(TimeStampable):
    """This mixin is to be inherited by all models."""

    tokenized_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True
        ordering = ("-updated_at", "-created_at")


class OwnerAbstract(OwnerlessAbstract):
    """This mixin is to be used by models that require a user to create/update them."""

    created_by = models.UUIDField(null=True, blank=True, editable=False)
    updated_by = models.UUIDField(null=True, blank=True)

    class Meta:
        abstract = True
