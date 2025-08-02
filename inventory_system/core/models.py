"""
Core models for the Inventory Management System.
Contains base models and common functionality.
"""
import uuid
from typing import Optional
from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError


class TimeStampedModel(models.Model):
    """
    Abstract base model that provides self-updating created_at and updated_at fields.
    """
    created_at = models.DateTimeField(auto_now_add=True, help_text="Timestamp when the record was created")
    updated_at = models.DateTimeField(auto_now=True, help_text="Timestamp when the record was last updated")

    class Meta:
        abstract = True
        ordering = ['-created_at']


class SoftDeleteModel(models.Model):
    """
    Abstract base model that provides soft delete functionality.
    """
    is_deleted = models.BooleanField(default=False, help_text="Soft delete flag")
    deleted_at = models.DateTimeField(null=True, blank=True, help_text="Timestamp when the record was soft deleted")

    class Meta:
        abstract = True

    def soft_delete(self) -> None:
        """Soft delete the record by setting is_deleted to True and deleted_at to current time."""
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(update_fields=['is_deleted', 'deleted_at'])

    def restore(self) -> None:
        """Restore the soft deleted record."""
        self.is_deleted = False
        self.deleted_at = None
        self.save(update_fields=['is_deleted', 'deleted_at'])


class UUIDModel(models.Model):
    """
    Abstract base model that provides UUID primary key.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, help_text="Unique identifier")

    class Meta:
        abstract = True


class BaseModel(TimeStampedModel, SoftDeleteModel, UUIDModel):
    """
    Base model that combines timestamp, soft delete, and UUID functionality.
    """
    class Meta:
        abstract = True
