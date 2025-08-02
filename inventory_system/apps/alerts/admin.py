"""
Admin configuration for alert models.
"""
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.db.models import Sum, Count, Q
from django import forms
from .models import StockAlert, AlertRule, AlertNotification


@admin.register(StockAlert)
class StockAlertAdmin(admin.ModelAdmin):
    """Admin for StockAlert model."""
    list_display = ('product', 'warehouse', 'alert_type', 'severity', 'is_resolved', 'duration', 'created_at')
    list_filter = ('alert_type', 'severity', 'is_resolved', 'created_at', 'resolved_at')
    search_fields = ('product__name', 'product__sku', 'warehouse__name', 'message')
    readonly_fields = ('id', 'created_at', 'updated_at', 'duration', 'is_active')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Alert Information', {
            'fields': ('product', 'warehouse', 'alert_type', 'severity')
        }),
        ('Message & Values', {
            'fields': ('message', 'threshold_value', 'current_value')
        }),
        ('Status', {
            'fields': ('is_resolved', 'is_active', 'resolved_at', 'resolved_by', 'resolution_notes')
        }),
        ('Duration', {
            'fields': ('duration',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def duration(self, obj):
        """Display alert duration."""
        duration_hours = obj.duration
        if duration_hours is not None:
            if duration_hours < 24:
                return f"{duration_hours}h"
            else:
                days = duration_hours // 24
                hours = duration_hours % 24
                return f"{days}d {hours}h"
        return "-"
    duration.short_description = 'Duration'

    def is_active(self, obj):
        """Display active status."""
        if obj.is_active:
            return format_html('<span style="color: red;">● Active</span>')
        else:
            return format_html('<span style="color: green;">○ Resolved</span>')
    is_active.short_description = 'Status'

    def get_queryset(self, request):
        """Optimize queryset with related data."""
        return super().get_queryset(request).select_related('product', 'warehouse', 'resolved_by')

    actions = ['resolve_alerts', 'reactivate_alerts', 'export_alerts']

    def resolve_alerts(self, request, queryset):
        """Resolve selected alerts."""
        count = 0
        for alert in queryset.filter(is_resolved=False):
            if alert.resolve(request.user, "Resolved via admin action"):
                count += 1
        self.message_user(request, f'{count} alerts were resolved.')
    resolve_alerts.short_description = "Resolve selected alerts"

    def reactivate_alerts(self, request, queryset):
        """Reactivate selected alerts."""
        count = 0
        for alert in queryset.filter(is_resolved=True):
            if alert.reactivate():
                count += 1
        self.message_user(request, f'{count} alerts were reactivated.')
    reactivate_alerts.short_description = "Reactivate selected alerts"

    def export_alerts(self, request, queryset):
        """Export alerts data."""
        import csv
        from django.http import HttpResponse
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="stock_alerts.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Product', 'SKU', 'Warehouse', 'Alert Type', 'Severity', 'Message', 'Status', 'Created', 'Resolved'])
        
        for alert in queryset:
            writer.writerow([
                alert.product.name,
                alert.product.sku,
                alert.warehouse.name,
                alert.get_alert_type_display(),
                alert.get_severity_display(),
                alert.message,
                'Resolved' if alert.is_resolved else 'Active',
                alert.created_at.strftime('%Y-%m-%d %H:%M'),
                alert.resolved_at.strftime('%Y-%m-%d %H:%M') if alert.resolved_at else ''
            ])
        
        return response
    export_alerts.short_description = "Export alerts to CSV"


@admin.register(AlertRule)
class AlertRuleAdmin(admin.ModelAdmin):
    """Admin for AlertRule model."""
    list_display = ('name', 'rule_type', 'severity', 'is_active', 'product', 'category', 'warehouse', 'thresholds', 'created_at')
    list_filter = ('rule_type', 'severity', 'is_active', 'created_at')
    search_fields = ('name', 'description', 'product__name', 'warehouse__name')
    readonly_fields = ('id', 'created_at', 'updated_at')
    ordering = ('name',)
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'rule_type', 'severity', 'description')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Conditions', {
            'fields': ('product', 'category', 'warehouse'),
            'description': 'Leave blank to apply to all products/categories/warehouses'
        }),
        ('Thresholds', {
            'fields': ('min_threshold', 'max_threshold')
        }),
        ('Notifications', {
            'fields': ('email_notification', 'dashboard_notification', 'auto_resolve'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def thresholds(self, obj):
        """Display threshold values."""
        if obj.rule_type in ['low_stock', 'custom']:
            return f"Min: {obj.min_threshold}"
        elif obj.rule_type == 'overstock':
            return f"Max: {obj.max_threshold}"
        else:
            return f"Min: {obj.min_threshold}, Max: {obj.max_threshold}"
    thresholds.short_description = 'Thresholds'

    def get_queryset(self, request):
        """Optimize queryset with related data."""
        return super().get_queryset(request).select_related('product', 'category', 'warehouse')

    actions = ['activate_rules', 'deactivate_rules', 'test_rules']

    def activate_rules(self, request, queryset):
        """Activate selected rules."""
        count = queryset.update(is_active=True)
        self.message_user(request, f'{count} rules were activated.')
    activate_rules.short_description = "Activate selected rules"

    def deactivate_rules(self, request, queryset):
        """Deactivate selected rules."""
        count = queryset.update(is_active=False)
        self.message_user(request, f'{count} rules were deactivated.')
    deactivate_rules.short_description = "Deactivate selected rules"

    def test_rules(self, request, queryset):
        """Test selected rules."""
        from inventory_system.apps.inventory.models import Inventory
        
        count = 0
        for rule in queryset:
            if rule.is_active:
                # Test the rule against all relevant inventory items
                inventory_items = Inventory.objects.filter(is_deleted=False)
                
                if rule.product:
                    inventory_items = inventory_items.filter(product=rule.product)
                if rule.category:
                    inventory_items = inventory_items.filter(product__category=rule.category)
                if rule.warehouse:
                    inventory_items = inventory_items.filter(warehouse=rule.warehouse)
                
                for inventory in inventory_items:
                    if rule.check_condition(inventory):
                        alert = rule.create_alert(inventory)
                        if alert:
                            count += 1
        
        self.message_user(request, f'{count} alerts were created from testing the rules.')
    test_rules.short_description = "Test selected rules"


@admin.register(AlertNotification)
class AlertNotificationAdmin(admin.ModelAdmin):
    """Admin for AlertNotification model."""
    list_display = ('alert', 'notification_type', 'status', 'recipient', 'sent_at', 'created_at')
    list_filter = ('notification_type', 'status', 'sent_at', 'created_at')
    search_fields = ('alert__product__name', 'alert__warehouse__name', 'recipient', 'message')
    readonly_fields = ('id', 'created_at', 'updated_at', 'sent_at')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Notification Information', {
            'fields': ('alert', 'notification_type', 'status')
        }),
        ('Delivery', {
            'fields': ('recipient', 'message', 'sent_at', 'error_message')
        }),
        ('Metadata', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        """Optimize queryset with related data."""
        return super().get_queryset(request).select_related('alert', 'alert__product', 'alert__warehouse')

    actions = ['mark_as_sent', 'mark_as_failed', 'retry_notifications']

    def mark_as_sent(self, request, queryset):
        """Mark selected notifications as sent."""
        count = 0
        for notification in queryset.filter(status='pending'):
            notification.mark_as_sent()
            count += 1
        self.message_user(request, f'{count} notifications were marked as sent.')
    mark_as_sent.short_description = "Mark as sent"

    def mark_as_failed(self, request, queryset):
        """Mark selected notifications as failed."""
        count = 0
        for notification in queryset.filter(status='pending'):
            notification.mark_as_failed("Marked as failed via admin action")
            count += 1
        self.message_user(request, f'{count} notifications were marked as failed.')
    mark_as_failed.short_description = "Mark as failed"

    def retry_notifications(self, request, queryset):
        """Retry failed notifications."""
        count = 0
        for notification in queryset.filter(status='failed'):
            notification.status = 'pending'
            notification.error_message = ""
            notification.save(update_fields=['status', 'error_message'])
            count += 1
        self.message_user(request, f'{count} notifications were queued for retry.')
    retry_notifications.short_description = "Retry failed notifications"
