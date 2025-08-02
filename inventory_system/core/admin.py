"""
Admin configuration for core models.
"""
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import TimeStampedModel, SoftDeleteModel, UUIDModel, BaseModel


# Note: Abstract models (TimeStampedModel, SoftDeleteModel, UUIDModel, BaseModel) 
# cannot be registered with Django admin as they are not concrete models.
# They are used as base classes for other models.


class BaseModelAdmin(admin.ModelAdmin):
    """Base admin class for models that inherit from BaseModel."""
    readonly_fields = ('id', 'created_at', 'updated_at', 'deleted_at')
    list_display = ('id', 'created_at', 'updated_at', 'is_deleted', 'deleted_at')
    list_filter = ('is_deleted', 'created_at', 'updated_at', 'deleted_at')
    date_hierarchy = 'created_at'
    actions = ['soft_delete_selected', 'restore_selected']

    def soft_delete_selected(self, request, queryset):
        """Soft delete selected objects."""
        count = 0
        for obj in queryset:
            if hasattr(obj, 'soft_delete'):
                obj.soft_delete()
                count += 1
        self.message_user(request, f'{count} objects were soft deleted.')
    soft_delete_selected.short_description = "Soft delete selected objects"

    def restore_selected(self, request, queryset):
        """Restore selected objects."""
        count = 0
        for obj in queryset:
            if hasattr(obj, 'restore'):
                obj.restore()
                count += 1
        self.message_user(request, f'{count} objects were restored.')
    restore_selected.short_description = "Restore selected objects"
