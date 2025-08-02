"""
Stock alert models for monitoring inventory levels and notifications.
"""
from typing import Optional, Dict, Any
from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from inventory_system.core.models import BaseModel
from inventory_system.apps.products.models import Product
from inventory_system.apps.inventory.models import Warehouse, Inventory


class StockAlert(BaseModel):
    """
    Stock alert model for monitoring inventory levels and generating notifications.
    """
    ALERT_TYPES = [
        ('low_stock', 'Low Stock'),
        ('out_of_stock', 'Out of Stock'),
        ('overstock', 'Overstock'),
        ('expiring', 'Expiring Soon'),
        ('custom', 'Custom Alert'),
    ]
    
    SEVERITY_LEVELS = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE, 
        related_name='stock_alerts',
        help_text="Product"
    )
    warehouse = models.ForeignKey(
        Warehouse, 
        on_delete=models.CASCADE, 
        related_name='stock_alerts',
        help_text="Warehouse"
    )
    alert_type = models.CharField(
        max_length=20, 
        choices=ALERT_TYPES,
        help_text="Type of alert"
    )
    severity = models.CharField(
        max_length=20, 
        choices=SEVERITY_LEVELS,
        default='medium',
        help_text="Alert severity level"
    )
    message = models.TextField(help_text="Alert message")
    threshold_value = models.PositiveIntegerField(
        default=0,
        help_text="Threshold value that triggered the alert"
    )
    current_value = models.PositiveIntegerField(
        default=0,
        help_text="Current value when alert was triggered"
    )
    is_resolved = models.BooleanField(default=False, help_text="Whether alert is resolved")
    resolved_at = models.DateTimeField(blank=True, null=True, help_text="Resolution timestamp")
    resolved_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='resolved_alerts',
        help_text="User who resolved the alert"
    )
    resolution_notes = models.TextField(blank=True, help_text="Resolution notes")
    
    class Meta:
        verbose_name = "Stock Alert"
        verbose_name_plural = "Stock Alerts"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['product', 'warehouse']),
            models.Index(fields=['alert_type']),
            models.Index(fields=['severity']),
            models.Index(fields=['is_resolved']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self) -> str:
        return f"{self.product.name} - {self.get_alert_type_display()} at {self.warehouse.name}"

    def clean(self) -> None:
        """Validate alert data."""
        if not self.message:
            raise ValidationError("Alert message cannot be empty")

    @property
    def is_active(self) -> bool:
        """Check if alert is active (not resolved)."""
        return not self.is_resolved

    @property
    def duration(self) -> Optional[int]:
        """Calculate alert duration in hours."""
        if self.is_resolved and self.resolved_at:
            from django.utils import timezone
            duration = self.resolved_at - self.created_at
            return int(duration.total_seconds() / 3600)
        return None

    def resolve(self, user=None, notes: str = None) -> bool:
        """Resolve the alert."""
        if self.is_resolved:
            return False
        
        from django.utils import timezone
        self.is_resolved = True
        self.resolved_at = timezone.now()
        self.resolved_by = user
        self.resolution_notes = notes or ""
        self.save(update_fields=['is_resolved', 'resolved_at', 'resolved_by', 'resolution_notes'])
        return True

    def reactivate(self) -> bool:
        """Reactivate a resolved alert."""
        if not self.is_resolved:
            return False
        
        self.is_resolved = False
        self.resolved_at = None
        self.resolved_by = None
        self.resolution_notes = ""
        self.save(update_fields=['is_resolved', 'resolved_at', 'resolved_by', 'resolution_notes'])
        return True

    def get_alert_rule(self):
        """Get the alert rule that triggered this alert."""
        from .models import AlertRule
        
        return AlertRule.objects.filter(
            rule_type=self.alert_type,
            is_active=True,
            is_deleted=False
        ).filter(
            models.Q(product=self.product) | 
            models.Q(category=self.product.category) |
            models.Q(warehouse=self.warehouse) |
            (models.Q(product__isnull=True) & models.Q(category__isnull=True) & models.Q(warehouse__isnull=True))
        ).first()


class AlertRule(BaseModel):
    """
    Alert rule model for defining when alerts should be triggered.
    """
    RULE_TYPES = [
        ('low_stock', 'Low Stock'),
        ('out_of_stock', 'Out of Stock'),
        ('overstock', 'Overstock'),
        ('expiring', 'Expiring Soon'),
        ('custom', 'Custom Rule'),
    ]
    
    SEVERITY_LEVELS = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    name = models.CharField(max_length=100, help_text="Rule name")
    rule_type = models.CharField(
        max_length=20, 
        choices=RULE_TYPES,
        help_text="Type of rule"
    )
    severity = models.CharField(
        max_length=20, 
        choices=SEVERITY_LEVELS,
        default='medium',
        help_text="Alert severity level"
    )
    description = models.TextField(blank=True, help_text="Rule description")
    is_active = models.BooleanField(default=True, help_text="Whether rule is active")
    
    # Rule conditions
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='alert_rules',
        help_text="Specific product (leave blank for all products)"
    )
    category = models.ForeignKey(
        'products.Category',
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='alert_rules',
        help_text="Product category (leave blank for all categories)"
    )
    warehouse = models.ForeignKey(
        Warehouse, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='alert_rules',
        help_text="Specific warehouse (leave blank for all warehouses)"
    )
    
    # Threshold values
    min_threshold = models.PositiveIntegerField(
        default=0,
        help_text="Minimum threshold value"
    )
    max_threshold = models.PositiveIntegerField(
        default=0,
        help_text="Maximum threshold value"
    )
    
    # Notification settings
    email_notification = models.BooleanField(default=True, help_text="Send email notifications")
    dashboard_notification = models.BooleanField(default=True, help_text="Show dashboard notifications")
    auto_resolve = models.BooleanField(default=False, help_text="Auto-resolve when condition is no longer met")
    
    class Meta:
        verbose_name = "Alert Rule"
        verbose_name_plural = "Alert Rules"
        ordering = ['name']
        indexes = [
            models.Index(fields=['rule_type']),
            models.Index(fields=['severity']),
            models.Index(fields=['is_active']),
            models.Index(fields=['product']),
            models.Index(fields=['warehouse']),
        ]

    def __str__(self) -> str:
        return self.name

    def clean(self) -> None:
        """Validate rule data."""
        if self.name:
            self.name = self.name.strip()
            if not self.name:
                raise ValidationError("Rule name cannot be empty")
        
        if self.max_threshold > 0 and self.min_threshold > self.max_threshold:
            raise ValidationError("Minimum threshold cannot be greater than maximum threshold")

    def check_condition(self, inventory: Inventory) -> bool:
        """Check if the rule condition is met for a given inventory item."""
        if not self.is_active:
            return False
        
        # Check product filter
        if self.product and inventory.product != self.product:
            return False
        
        # Check category filter
        if self.category and inventory.product.category != self.category:
            return False
        
        # Check warehouse filter
        if self.warehouse and inventory.warehouse != self.warehouse:
            return False
        
        # Check threshold conditions based on rule type
        if self.rule_type == 'low_stock':
            return inventory.available_quantity <= self.min_threshold
        
        elif self.rule_type == 'out_of_stock':
            return inventory.available_quantity == 0
        
        elif self.rule_type == 'overstock':
            return inventory.quantity >= self.max_threshold
        
        elif self.rule_type == 'custom':
            # Custom logic can be implemented here
            return inventory.available_quantity <= self.min_threshold
        
        return False

    def create_alert(self, inventory: Inventory) -> Optional[StockAlert]:
        """Create an alert if the rule condition is met."""
        if not self.check_condition(inventory):
            return None
        
        # Check if there's already an active alert for this product/warehouse/rule
        existing_alert = StockAlert.objects.filter(
            product=inventory.product,
            warehouse=inventory.warehouse,
            alert_type=self.rule_type,
            is_resolved=False
        ).first()
        
        if existing_alert:
            return existing_alert
        
        # Create new alert
        message = self._generate_alert_message(inventory)
        
        alert = StockAlert.objects.create(
            product=inventory.product,
            warehouse=inventory.warehouse,
            alert_type=self.rule_type,
            severity=self.severity,
            message=message,
            threshold_value=self.min_threshold if self.rule_type in ['low_stock', 'custom'] else self.max_threshold,
            current_value=inventory.available_quantity
        )
        
        return alert

    def _generate_alert_message(self, inventory: Inventory) -> str:
        """Generate alert message based on rule type and inventory."""
        if self.rule_type == 'low_stock':
            return f"Low stock alert: {inventory.product.name} has {inventory.available_quantity} units available at {inventory.warehouse.name} (threshold: {self.min_threshold})"
        
        elif self.rule_type == 'out_of_stock':
            return f"Out of stock alert: {inventory.product.name} is out of stock at {inventory.warehouse.name}"
        
        elif self.rule_type == 'overstock':
            return f"Overstock alert: {inventory.product.name} has {inventory.quantity} units at {inventory.warehouse.name} (threshold: {self.max_threshold})"
        
        elif self.rule_type == 'custom':
            return f"Custom alert: {inventory.product.name} at {inventory.warehouse.name} - {self.description}"
        
        return f"Alert for {inventory.product.name} at {inventory.warehouse.name}"


class AlertNotification(BaseModel):
    """
    Alert notification model for tracking notification delivery.
    """
    NOTIFICATION_TYPES = [
        ('email', 'Email'),
        ('dashboard', 'Dashboard'),
        ('sms', 'SMS'),
        ('webhook', 'Webhook'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    alert = models.ForeignKey(
        StockAlert, 
        on_delete=models.CASCADE, 
        related_name='notifications',
        help_text="Related alert"
    )
    notification_type = models.CharField(
        max_length=20, 
        choices=NOTIFICATION_TYPES,
        help_text="Type of notification"
    )
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES,
        default='pending',
        help_text="Notification status"
    )
    recipient = models.CharField(max_length=200, help_text="Notification recipient")
    message = models.TextField(help_text="Notification message")
    sent_at = models.DateTimeField(blank=True, null=True, help_text="Sent timestamp")
    error_message = models.TextField(blank=True, help_text="Error message if failed")
    
    class Meta:
        verbose_name = "Alert Notification"
        verbose_name_plural = "Alert Notifications"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['alert']),
            models.Index(fields=['notification_type']),
            models.Index(fields=['status']),
            models.Index(fields=['sent_at']),
        ]

    def __str__(self) -> str:
        return f"{self.alert} - {self.get_notification_type_display()} ({self.status})"

    def mark_as_sent(self) -> None:
        """Mark notification as sent."""
        from django.utils import timezone
        self.status = 'sent'
        self.sent_at = timezone.now()
        self.save(update_fields=['status', 'sent_at'])

    def mark_as_failed(self, error_message: str = None) -> None:
        """Mark notification as failed."""
        self.status = 'failed'
        self.error_message = error_message or ""
        self.save(update_fields=['status', 'error_message'])
