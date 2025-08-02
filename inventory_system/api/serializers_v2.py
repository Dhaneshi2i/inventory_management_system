"""
Enhanced serializers for the Inventory Management System API.
"""
from rest_framework import serializers
from django.db.models import Sum, F, Q
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
import logging

from inventory_system.apps.products.models import Category, Product
from inventory_system.apps.inventory.models import Warehouse, Inventory, StockMovement
from inventory_system.apps.orders.models import Supplier, PurchaseOrder, PurchaseOrderItem
from inventory_system.apps.alerts.models import StockAlert, AlertRule, AlertNotification
from inventory_system.apps.reports.models import Report, DashboardWidget

logger = logging.getLogger(__name__)


class CategorySerializer(serializers.ModelSerializer):
    """Enhanced serializer for Category model."""
    product_count = serializers.SerializerMethodField()
    total_value = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = [
            'id', 'name', 'description', 'product_count', 'total_value',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'product_count', 'total_value']
    
    def get_product_count(self, obj):
        """Get count of active products in category."""
        return obj.products.filter(is_deleted=False).count()
    
    def get_total_value(self, obj):
        """Get total inventory value for products in this category."""
        total = Inventory.objects.filter(
            product__category=obj,
            product__is_deleted=False,
            is_deleted=False
        ).aggregate(
            total=Sum(F('quantity') * F('product__unit_price'))
        )['total'] or 0
        return float(total)
    
    def validate_name(self, value):
        """Validate category name."""
        if len(value.strip()) < 2:
            raise ValidationError("Category name must be at least 2 characters long.")
        return value.strip()


class ProductSerializer(serializers.ModelSerializer):
    """Enhanced serializer for Product model."""
    category = CategorySerializer(read_only=True)
    category_id = serializers.UUIDField(write_only=True)
    total_value = serializers.SerializerMethodField()
    stock_status = serializers.SerializerMethodField()
    image = serializers.ImageField(required=False, allow_null=True)
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'sku', 'category', 'category_id', 'description',
            'unit_price', 'specifications', 'image', 'total_value', 'stock_status',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'total_value', 'stock_status']
    
    def get_total_value(self, obj):
        """Get total inventory value across all warehouses."""
        inventory_items = Inventory.objects.filter(product=obj, is_deleted=False)
        total_quantity = inventory_items.aggregate(total=Sum('quantity'))['total'] or 0
        low_stock_count = inventory_items.filter(quantity__lte=F('reorder_point')).count()
        out_of_stock_count = inventory_items.filter(quantity=0).count()
        
        if out_of_stock_count > 0:
            return 'out_of_stock'
        elif low_stock_count > 0:
            return 'low_stock'
        elif total_quantity > 0:
            return 'in_stock'
        else:
            return 'no_stock'
    
    def get_stock_status(self, obj):
        """Get stock status across all warehouses."""
        inventory_items = Inventory.objects.filter(product=obj, is_deleted=False)
        total_quantity = inventory_items.aggregate(total=Sum('quantity'))['total'] or 0
        low_stock_count = inventory_items.filter(quantity__lte=F('reorder_point')).count()
        out_of_stock_count = inventory_items.filter(quantity=0).count()
        
        if out_of_stock_count > 0:
            return 'out_of_stock'
        elif low_stock_count > 0:
            return 'low_stock'
        elif total_quantity > 0:
            return 'in_stock'
        else:
            return 'no_stock'
    
    def validate_sku(self, value):
        """Validate SKU uniqueness."""
        if self.instance and self.instance.sku == value:
            return value
        
        if Product.objects.filter(sku=value, is_deleted=False).exists():
            raise ValidationError("SKU must be unique.")
        return value.upper()
    
    def validate_unit_price(self, value):
        """Validate unit price."""
        if value <= 0:
            raise ValidationError("Unit price must be greater than zero.")
        return value


class WarehouseSerializer(serializers.ModelSerializer):
    """Enhanced serializer for Warehouse model."""
    current_utilization = serializers.SerializerMethodField()
    available_capacity = serializers.SerializerMethodField()
    inventory_count = serializers.SerializerMethodField()
    total_inventory_value = serializers.SerializerMethodField()
    
    class Meta:
        model = Warehouse
        fields = [
            'id', 'name', 'address', 'capacity', 'manager', 'contact_email',
            'contact_phone', 'is_active', 'current_utilization', 'available_capacity',
            'inventory_count', 'total_inventory_value', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at', 'current_utilization', 
            'available_capacity', 'inventory_count', 'total_inventory_value'
        ]
    
    def get_current_utilization(self, obj):
        """Get current utilization percentage."""
        return obj.current_utilization
    
    def get_available_capacity(self, obj):
        """Get available capacity."""
        return obj.available_capacity
    
    def get_inventory_count(self, obj):
        """Get inventory item count."""
        return obj.inventory_items.filter(is_deleted=False).count()
    
    def get_total_inventory_value(self, obj):
        """Get total inventory value in this warehouse."""
        total = obj.inventory_items.filter(is_deleted=False).aggregate(
            total=Sum(F('quantity') * F('product__unit_price'))
        )['total'] or 0
        return float(total)
    
    def validate_capacity(self, value):
        """Validate warehouse capacity."""
        if value <= 0:
            raise ValidationError("Capacity must be greater than zero.")
        return value


class InventorySerializer(serializers.ModelSerializer):
    """Enhanced serializer for Inventory model."""
    product = ProductSerializer(read_only=True)
    product_id = serializers.UUIDField(write_only=True)
    warehouse = WarehouseSerializer(read_only=True)
    warehouse_id = serializers.UUIDField(write_only=True)
    available_quantity = serializers.SerializerMethodField()
    is_low_stock = serializers.SerializerMethodField()
    is_out_of_stock = serializers.SerializerMethodField()
    stock_value = serializers.SerializerMethodField()
    stock_status = serializers.SerializerMethodField()
    
    class Meta:
        model = Inventory
        fields = [
            'id', 'product', 'product_id', 'warehouse', 'warehouse_id',
            'quantity', 'reserved_quantity', 'available_quantity', 'reorder_point',
            'max_stock_level', 'is_low_stock', 'is_out_of_stock', 'stock_value',
            'stock_status', 'last_updated', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at', 'available_quantity', 
            'is_low_stock', 'is_out_of_stock', 'stock_value', 'last_updated', 'stock_status'
        ]
    
    def get_available_quantity(self, obj):
        """Get available quantity."""
        return obj.available_quantity
    
    def get_is_low_stock(self, obj):
        """Get low stock status."""
        return obj.is_low_stock
    
    def get_is_out_of_stock(self, obj):
        """Get out of stock status."""
        return obj.is_out_of_stock
    
    def get_stock_value(self, obj):
        """Get stock value."""
        return obj.stock_value
    
    def get_stock_status(self, obj):
        """Get stock status."""
        if obj.quantity == 0:
            return 'out_of_stock'
        elif obj.quantity <= obj.reorder_point:
            return 'low_stock'
        else:
            return 'in_stock'
    
    def validate(self, data):
        """Validate inventory data."""
        if 'quantity' in data and data['quantity'] < 0:
            raise ValidationError("Quantity cannot be negative.")
        
        if 'reserved_quantity' in data and 'quantity' in data:
            if data['reserved_quantity'] > data['quantity']:
                raise ValidationError("Reserved quantity cannot exceed available quantity.")
        
        if 'max_stock_level' in data and 'quantity' in data:
            if data['max_stock_level'] > 0 and data['quantity'] > data['max_stock_level']:
                raise ValidationError("Quantity cannot exceed maximum stock level.")
        
        return data


class StockMovementSerializer(serializers.ModelSerializer):
    """Enhanced serializer for StockMovement model."""
    product = ProductSerializer(read_only=True)
    warehouse = WarehouseSerializer(read_only=True)
    movement_value = serializers.SerializerMethodField()
    
    class Meta:
        model = StockMovement
        fields = [
            'id', 'product', 'warehouse', 'movement_type', 'quantity',
            'reference_type', 'reference_id', 'notes', 'movement_value',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'movement_value']
    
    def get_movement_value(self, obj):
        """Get movement value."""
        return obj.movement_value
    
    def validate_quantity(self, value):
        """Validate movement quantity."""
        if value <= 0:
            raise ValidationError("Movement quantity must be greater than zero.")
        return value


class SupplierSerializer(serializers.ModelSerializer):
    """Enhanced serializer for Supplier model."""
    total_orders = serializers.SerializerMethodField()
    total_order_value = serializers.SerializerMethodField()
    average_order_value = serializers.SerializerMethodField()
    last_order_date = serializers.SerializerMethodField()
    
    class Meta:
        model = Supplier
        fields = [
            'id', 'name', 'contact_person', 'email', 'phone', 'address',
            'website', 'tax_id', 'payment_terms', 'is_active', 'total_orders',
            'total_order_value', 'average_order_value', 'last_order_date',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at', 'total_orders', 
            'total_order_value', 'average_order_value', 'last_order_date'
        ]
    
    def get_total_orders(self, obj):
        """Get total number of orders."""
        return obj.total_orders
    
    def get_total_order_value(self, obj):
        """Get total order value."""
        return obj.total_order_value
    
    def get_average_order_value(self, obj):
        """Get average order value."""
        orders = obj.purchase_orders.filter(is_deleted=False)
        if orders.exists():
            return float(orders.aggregate(avg=Sum('total_amount'))['avg'] or 0) / orders.count()
        return 0.0
    
    def get_last_order_date(self, obj):
        """Get last order date."""
        last_order = obj.purchase_orders.filter(is_deleted=False).order_by('-order_date').first()
        return last_order.order_date if last_order else None
    
    def validate_email(self, value):
        """Validate email format."""
        if value and '@' not in value:
            raise ValidationError("Invalid email format.")
        return value.lower()


class PurchaseOrderItemSerializer(serializers.ModelSerializer):
    """Enhanced serializer for PurchaseOrderItem model."""
    product = ProductSerializer(read_only=True)
    remaining_quantity = serializers.SerializerMethodField()
    is_complete = serializers.SerializerMethodField()
    completion_percentage = serializers.SerializerMethodField()
    
    class Meta:
        model = PurchaseOrderItem
        fields = [
            'id', 'purchase_order', 'product', 'quantity_ordered', 'quantity_received',
            'unit_price', 'total_price', 'remaining_quantity', 'is_complete',
            'completion_percentage', 'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at', 'remaining_quantity', 
            'is_complete', 'completion_percentage'
        ]
    
    def get_remaining_quantity(self, obj):
        """Get remaining quantity to receive."""
        return obj.remaining_quantity
    
    def get_is_complete(self, obj):
        """Check if item is complete."""
        return obj.is_complete
    
    def get_completion_percentage(self, obj):
        """Get completion percentage."""
        if obj.quantity_ordered == 0:
            return 0
        return (obj.quantity_received / obj.quantity_ordered) * 100
    
    def validate_quantity_ordered(self, value):
        """Validate ordered quantity."""
        if value <= 0:
            raise ValidationError("Ordered quantity must be greater than zero.")
        return value
    
    def validate_quantity_received(self, value):
        """Validate received quantity."""
        if value < 0:
            raise ValidationError("Received quantity cannot be negative.")
        return value


class PurchaseOrderSerializer(serializers.ModelSerializer):
    """Enhanced serializer for PurchaseOrder model."""
    supplier = SupplierSerializer(read_only=True)
    warehouse = WarehouseSerializer(read_only=True)
    items = PurchaseOrderItemSerializer(many=True, read_only=True)
    item_count = serializers.SerializerMethodField()
    total_quantity = serializers.SerializerMethodField()
    received_quantity = serializers.SerializerMethodField()
    is_complete = serializers.SerializerMethodField()
    completion_percentage = serializers.SerializerMethodField()
    days_until_expected = serializers.SerializerMethodField()
    
    class Meta:
        model = PurchaseOrder
        fields = [
            'id', 'order_number', 'supplier', 'warehouse', 'status', 'order_date',
            'expected_date', 'received_date', 'total_amount', 'notes', 'approved_by',
            'approved_at', 'item_count', 'total_quantity', 'received_quantity',
            'is_complete', 'completion_percentage', 'days_until_expected', 'items',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'order_number', 'created_at', 'updated_at', 'item_count',
            'total_quantity', 'received_quantity', 'is_complete', 'completion_percentage',
            'days_until_expected'
        ]
    
    def get_item_count(self, obj):
        """Get item count."""
        return obj.item_count
    
    def get_total_quantity(self, obj):
        """Get total quantity."""
        return obj.total_quantity
    
    def get_received_quantity(self, obj):
        """Get received quantity."""
        return obj.received_quantity
    
    def get_is_complete(self, obj):
        """Check if order is complete."""
        return obj.is_complete
    
    def get_completion_percentage(self, obj):
        """Get completion percentage."""
        if obj.total_quantity == 0:
            return 0
        return (obj.received_quantity / obj.total_quantity) * 100
    
    def get_days_until_expected(self, obj):
        """Get days until expected delivery."""
        if obj.expected_date:
            delta = obj.expected_date - timezone.now().date()
            return delta.days
        return None
    
    def validate_expected_date(self, value):
        """Validate expected date."""
        if value and value < timezone.now().date():
            raise ValidationError("Expected date cannot be in the past.")
        return value


class StockAlertSerializer(serializers.ModelSerializer):
    """Enhanced serializer for StockAlert model."""
    product = ProductSerializer(read_only=True)
    warehouse = WarehouseSerializer(read_only=True)
    is_active = serializers.SerializerMethodField()
    duration = serializers.SerializerMethodField()
    severity_color = serializers.SerializerMethodField()
    
    class Meta:
        model = StockAlert
        fields = [
            'id', 'product', 'warehouse', 'alert_type', 'severity', 'message',
            'threshold_value', 'current_value', 'is_resolved', 'is_active',
            'resolved_at', 'resolved_by', 'resolution_notes', 'duration',
            'severity_color', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at', 'is_active', 'duration', 'severity_color'
        ]
    
    def get_is_active(self, obj):
        """Check if alert is active."""
        return obj.is_active
    
    def get_duration(self, obj):
        """Get alert duration in hours."""
        return obj.duration
    
    def get_severity_color(self, obj):
        """Get severity color for UI."""
        colors = {
            'low': 'blue',
            'medium': 'yellow',
            'high': 'orange',
            'critical': 'red'
        }
        return colors.get(obj.severity, 'gray')


class AlertRuleSerializer(serializers.ModelSerializer):
    """Enhanced serializer for AlertRule model."""
    product = ProductSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    warehouse = WarehouseSerializer(read_only=True)
    alert_count = serializers.SerializerMethodField()
    
    class Meta:
        model = AlertRule
        fields = [
            'id', 'name', 'rule_type', 'severity', 'description', 'is_active',
            'product', 'category', 'warehouse', 'min_threshold', 'max_threshold',
            'email_notification', 'dashboard_notification', 'auto_resolve',
            'alert_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'alert_count']
    
    def get_alert_count(self, obj):
        """Get count of alerts generated by this rule."""
        return StockAlert.objects.filter(
            alert_type=obj.rule_type,
            is_resolved=False,
            is_deleted=False
        ).count()


class AlertNotificationSerializer(serializers.ModelSerializer):
    """Enhanced serializer for AlertNotification model."""
    alert = StockAlertSerializer(read_only=True)
    
    class Meta:
        model = AlertNotification
        fields = [
            'id', 'alert', 'notification_type', 'status', 'recipient',
            'message', 'sent_at', 'error_message', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'sent_at']


class ReportSerializer(serializers.ModelSerializer):
    """Enhanced serializer for Report model."""
    generated_by = serializers.StringRelatedField()
    
    class Meta:
        model = Report
        fields = [
            'id', 'name', 'report_type', 'description', 'format', 'parameters',
            'data', 'file_path', 'generated_by', 'is_scheduled', 'schedule_frequency',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at', 'generated_by', 'file_path'
        ]


class DashboardWidgetSerializer(serializers.ModelSerializer):
    """Enhanced serializer for DashboardWidget model."""
    
    class Meta:
        model = DashboardWidget
        fields = [
            'id', 'name', 'widget_type', 'title', 'description', 'configuration',
            'position', 'is_active', 'refresh_interval', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class DashboardSummarySerializer(serializers.Serializer):
    """Enhanced serializer for dashboard summary data."""
    total_products = serializers.IntegerField()
    total_inventory_value = serializers.DecimalField(max_digits=15, decimal_places=2)
    low_stock_items = serializers.IntegerField()
    out_of_stock_items = serializers.IntegerField()
    total_warehouses = serializers.IntegerField()
    active_alerts = serializers.IntegerField()
    pending_orders = serializers.IntegerField()
    recent_movements = serializers.ListField()
    warehouse_utilization = serializers.ListField()
    top_products = serializers.ListField()
    alert_summary = serializers.DictField()


class BulkInventoryUpdateSerializer(serializers.Serializer):
    """Serializer for bulk inventory updates."""
    updates = serializers.ListField(
        child=serializers.DictField(),
        min_length=1,
        max_length=100
    )
    
    def validate_updates(self, value):
        """Validate bulk update data."""
        for update in value:
            if 'inventory_id' not in update:
                raise ValidationError("Each update must include inventory_id.")
            if 'quantity' not in update:
                raise ValidationError("Each update must include quantity.")
            if update['quantity'] < 0:
                raise ValidationError("Quantity cannot be negative.")
        return value


class ExportSerializer(serializers.Serializer):
    """Serializer for export requests."""
    format = serializers.ChoiceField(choices=['csv', 'json', 'xlsx'])
    filters = serializers.DictField(required=False)
    fields = serializers.ListField(child=serializers.CharField(), required=False)
    date_range = serializers.DictField(required=False) 