"""
Serializers for Inventory Management System API.
"""
from rest_framework import serializers
from django.db.models import Sum, F
from inventory_system.apps.products.models import Category, Product
from inventory_system.apps.inventory.models import Warehouse, Inventory, StockMovement
from inventory_system.apps.orders.models import Supplier, PurchaseOrder, PurchaseOrderItem
from inventory_system.apps.alerts.models import StockAlert, AlertRule, AlertNotification
from inventory_system.apps.reports.models import Report, DashboardWidget


# Product Serializers
class CategorySerializer(serializers.ModelSerializer):
    """Serializer for Category model."""
    product_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = [
            'id', 'name', 'description', 'product_count', 
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_product_count(self, obj):
        """Get product count for category."""
        return obj.products.filter(is_deleted=False).count()


class ProductSerializer(serializers.ModelSerializer):
    """Serializer for Product model."""
    category = CategorySerializer(read_only=True)
    category_id = serializers.UUIDField(write_only=True)
    total_value = serializers.SerializerMethodField()
    stock_status = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'sku', 'category', 'category_id', 'description',
            'unit_price', 'specifications', 'total_value', 'stock_status',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'total_value', 'stock_status']
    
    def get_total_value(self, obj):
        """Get total inventory value."""
        return obj.total_value
    
    def get_stock_status(self, obj):
        """Get stock status."""
        from inventory_system.apps.inventory.models import Inventory
        
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


# Inventory Serializers
class WarehouseSerializer(serializers.ModelSerializer):
    """Serializer for Warehouse model."""
    current_utilization = serializers.SerializerMethodField()
    available_capacity = serializers.SerializerMethodField()
    inventory_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Warehouse
        fields = [
            'id', 'name', 'address', 'capacity', 'manager', 'contact_email',
            'contact_phone', 'is_active', 'current_utilization', 'available_capacity',
            'inventory_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'current_utilization', 'available_capacity', 'inventory_count']
    
    def get_current_utilization(self, obj):
        """Get current utilization percentage."""
        return obj.current_utilization
    
    def get_available_capacity(self, obj):
        """Get available capacity."""
        return obj.available_capacity
    
    def get_inventory_count(self, obj):
        """Get inventory item count."""
        return obj.inventory_items.filter(is_deleted=False).count()


class InventorySerializer(serializers.ModelSerializer):
    """Serializer for Inventory model."""
    product = ProductSerializer(read_only=True)
    product_id = serializers.UUIDField(write_only=True)
    warehouse = WarehouseSerializer(read_only=True)
    warehouse_id = serializers.UUIDField(write_only=True)
    available_quantity = serializers.SerializerMethodField()
    is_low_stock = serializers.SerializerMethodField()
    is_out_of_stock = serializers.SerializerMethodField()
    stock_value = serializers.SerializerMethodField()
    
    class Meta:
        model = Inventory
        fields = [
            'id', 'product', 'product_id', 'warehouse', 'warehouse_id',
            'quantity', 'reserved_quantity', 'available_quantity', 'reorder_point',
            'max_stock_level', 'is_low_stock', 'is_out_of_stock', 'stock_value',
            'last_updated', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at', 'available_quantity', 
            'is_low_stock', 'is_out_of_stock', 'stock_value', 'last_updated'
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


class StockMovementSerializer(serializers.ModelSerializer):
    """Serializer for StockMovement model."""
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


# Order Serializers
class SupplierSerializer(serializers.ModelSerializer):
    """Serializer for Supplier model."""
    total_orders = serializers.SerializerMethodField()
    total_order_value = serializers.SerializerMethodField()
    
    class Meta:
        model = Supplier
        fields = [
            'id', 'name', 'contact_person', 'email', 'phone', 'address',
            'website', 'tax_id', 'payment_terms', 'is_active', 'total_orders',
            'total_order_value', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'total_orders', 'total_order_value']
    
    def get_total_orders(self, obj):
        """Get total orders count."""
        return obj.total_orders
    
    def get_total_order_value(self, obj):
        """Get total order value."""
        return obj.total_order_value


class PurchaseOrderItemSerializer(serializers.ModelSerializer):
    """Serializer for PurchaseOrderItem model."""
    product = ProductSerializer(read_only=True)
    remaining_quantity = serializers.SerializerMethodField()
    is_complete = serializers.SerializerMethodField()
    
    class Meta:
        model = PurchaseOrderItem
        fields = [
            'id', 'purchase_order', 'product', 'quantity_ordered', 'quantity_received',
            'unit_price', 'total_price', 'remaining_quantity', 'is_complete', 'notes',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at', 'total_price', 
            'remaining_quantity', 'is_complete'
        ]
    
    def get_remaining_quantity(self, obj):
        """Get remaining quantity."""
        return obj.remaining_quantity
    
    def get_is_complete(self, obj):
        """Get completion status."""
        return obj.is_complete


class PurchaseOrderSerializer(serializers.ModelSerializer):
    """Serializer for PurchaseOrder model."""
    supplier = SupplierSerializer(read_only=True)
    warehouse = WarehouseSerializer(read_only=True)
    items = PurchaseOrderItemSerializer(many=True, read_only=True)
    item_count = serializers.SerializerMethodField()
    total_quantity = serializers.SerializerMethodField()
    received_quantity = serializers.SerializerMethodField()
    is_complete = serializers.SerializerMethodField()
    
    class Meta:
        model = PurchaseOrder
        fields = [
            'id', 'order_number', 'supplier', 'warehouse', 'status', 'order_date',
            'expected_date', 'received_date', 'total_amount', 'notes', 'approved_by',
            'approved_at', 'item_count', 'total_quantity', 'received_quantity',
            'is_complete', 'items', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at', 'order_number', 'total_amount',
            'item_count', 'total_quantity', 'received_quantity', 'is_complete',
            'approved_by', 'approved_at'
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
        """Get completion status."""
        return obj.is_complete


# Alert Serializers
class StockAlertSerializer(serializers.ModelSerializer):
    """Serializer for StockAlert model."""
    product = ProductSerializer(read_only=True)
    warehouse = WarehouseSerializer(read_only=True)
    is_active = serializers.SerializerMethodField()
    duration = serializers.SerializerMethodField()
    
    class Meta:
        model = StockAlert
        fields = [
            'id', 'product', 'warehouse', 'alert_type', 'severity', 'message',
            'threshold_value', 'current_value', 'is_resolved', 'is_active',
            'resolved_at', 'resolved_by', 'resolution_notes', 'duration',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at', 'is_active', 'duration',
            'resolved_at', 'resolved_by'
        ]
    
    def get_is_active(self, obj):
        """Get active status."""
        return obj.is_active
    
    def get_duration(self, obj):
        """Get duration in hours."""
        return obj.duration


class AlertRuleSerializer(serializers.ModelSerializer):
    """Serializer for AlertRule model."""
    product = ProductSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    warehouse = WarehouseSerializer(read_only=True)
    
    class Meta:
        model = AlertRule
        fields = [
            'id', 'name', 'rule_type', 'severity', 'description', 'is_active',
            'product', 'category', 'warehouse', 'min_threshold', 'max_threshold',
            'email_notification', 'dashboard_notification', 'auto_resolve',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class AlertNotificationSerializer(serializers.ModelSerializer):
    """Serializer for AlertNotification model."""
    alert = StockAlertSerializer(read_only=True)
    
    class Meta:
        model = AlertNotification
        fields = [
            'id', 'alert', 'notification_type', 'status', 'recipient',
            'message', 'sent_at', 'error_message', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'sent_at']


# Report Serializers
class ReportSerializer(serializers.ModelSerializer):
    """Serializer for Report model."""
    generated_by = serializers.StringRelatedField()
    
    class Meta:
        model = Report
        fields = [
            'id', 'name', 'report_type', 'description', 'format', 'parameters',
            'data', 'file_path', 'generated_by', 'is_scheduled', 'schedule_frequency',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at', 'data', 'file_path', 'generated_by'
        ]


class DashboardWidgetSerializer(serializers.ModelSerializer):
    """Serializer for DashboardWidget model."""
    
    class Meta:
        model = DashboardWidget
        fields = [
            'id', 'name', 'widget_type', 'title', 'description', 'configuration',
            'position', 'is_active', 'refresh_interval', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


# Dashboard Serializer
class DashboardSummarySerializer(serializers.Serializer):
    """Serializer for dashboard summary data."""
    total_products = serializers.IntegerField()
    total_inventory_value = serializers.DecimalField(max_digits=15, decimal_places=2)
    low_stock_items = serializers.IntegerField()
    out_of_stock_items = serializers.IntegerField()
    total_warehouses = serializers.IntegerField()
    active_alerts = serializers.IntegerField()
    pending_orders = serializers.IntegerField()
    recent_movements = serializers.ListField()
    warehouse_utilization = serializers.ListField() 