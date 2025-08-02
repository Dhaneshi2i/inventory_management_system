"""
Unit tests for models with edge cases and validation.
"""
import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.utils import timezone
from decimal import Decimal

from inventory_system.apps.products.models import Category, Product
from inventory_system.apps.inventory.models import Warehouse, Inventory, StockMovement
from inventory_system.apps.orders.models import Supplier, PurchaseOrder, PurchaseOrderItem
from inventory_system.apps.alerts.models import StockAlert, AlertRule, AlertNotification
from inventory_system.apps.reports.models import Report, DashboardWidget
from tests.factories.factories import (
    CategoryFactory, ProductFactory, WarehouseFactory, InventoryFactory,
    SupplierFactory, PurchaseOrderFactory, PurchaseOrderItemFactory,
    StockMovementFactory, AlertRuleFactory, StockAlertFactory,
    AlertNotificationFactory, ReportFactory, DashboardWidgetFactory,
    UserFactory
)


@pytest.mark.django_db
@pytest.mark.model
class TestCategoryModel:
    """Test Category model."""
    
    def test_category_creation(self):
        """Test basic category creation."""
        category = CategoryFactory()
        assert category.name is not None
        assert category.description is not None
        assert not category.is_deleted
    
    def test_category_str_representation(self):
        """Test string representation."""
        category = CategoryFactory(name="Electronics")
        assert str(category) == "Electronics"
    
    def test_category_soft_delete(self):
        """Test soft delete functionality."""
        category = CategoryFactory()
        category.soft_delete()
        assert category.is_deleted
        assert category.deleted_at is not None
    
    def test_category_restore(self):
        """Test restore functionality."""
        category = CategoryFactory()
        category.soft_delete()
        category.restore()
        assert not category.is_deleted
        assert category.deleted_at is None
    
    def test_category_name_validation(self):
        """Test category name validation."""
        # Test empty name
        with pytest.raises(ValidationError):
            category = CategoryFactory(name="")
            category.full_clean()
        
        # Test very long name
        with pytest.raises(ValidationError):
            category = CategoryFactory(name="a" * 101)
            category.full_clean()
    
    def test_category_unique_name(self):
        """Test category name uniqueness."""
        CategoryFactory(name="Electronics")
        with pytest.raises(IntegrityError):
            CategoryFactory(name="Electronics")


@pytest.mark.django_db
@pytest.mark.model
class TestProductModel:
    """Test Product model."""
    
    def test_product_creation(self):
        """Test basic product creation."""
        product = ProductFactory()
        assert product.name is not None
        assert product.sku is not None
        assert product.category is not None
        assert product.unit_price > 0
    
    def test_product_str_representation(self):
        """Test string representation."""
        product = ProductFactory(name="Test Product", sku="TEST001")
        assert str(product) == "Test Product (TEST001)"
    
    def test_product_sku_validation(self):
        """Test SKU validation."""
        # Test empty SKU
        with pytest.raises(ValidationError):
            product = ProductFactory(sku="")
            product.full_clean()
        
        # Test very long SKU
        with pytest.raises(ValidationError):
            product = ProductFactory(sku="a" * 51)
            product.full_clean()
    
    def test_product_unit_price_validation(self):
        """Test unit price validation."""
        # Test negative price
        with pytest.raises(ValidationError):
            product = ProductFactory(unit_price=Decimal('-10.00'))
            product.full_clean()
        
        # Test zero price
        with pytest.raises(ValidationError):
            product = ProductFactory(unit_price=Decimal('0.00'))
            product.full_clean()
    
    def test_product_sku_uniqueness(self):
        """Test SKU uniqueness."""
        ProductFactory(sku="TEST001")
        with pytest.raises(IntegrityError):
            ProductFactory(sku="TEST001")
    
    def test_product_specifications_json(self):
        """Test specifications JSON field."""
        specs = {
            'color': 'red',
            'weight': '1.5kg',
            'dimensions': {'length': 10, 'width': 5, 'height': 2}
        }
        product = ProductFactory(specifications=specs)
        assert product.specifications == specs
    
    def test_product_stock_status(self):
        """Test stock status calculation."""
        product = ProductFactory()
        
        # No inventory
        assert product.get_stock_status() == 'no_stock'
        
        # Create inventory with stock
        inventory = InventoryFactory(product=product, quantity=100)
        assert product.get_stock_status() == 'in_stock'
        
        # Low stock
        inventory.quantity = 5
        inventory.reorder_point = 10
        inventory.save()
        assert product.get_stock_status() == 'low_stock'
        
        # Out of stock
        inventory.quantity = 0
        inventory.save()
        assert product.get_stock_status() == 'out_of_stock'


@pytest.mark.django_db
@pytest.mark.model
class TestWarehouseModel:
    """Test Warehouse model."""
    
    def test_warehouse_creation(self):
        """Test basic warehouse creation."""
        warehouse = WarehouseFactory()
        assert warehouse.name is not None
        assert warehouse.address is not None
        assert warehouse.capacity > 0
    
    def test_warehouse_str_representation(self):
        """Test string representation."""
        warehouse = WarehouseFactory(name="Main Warehouse")
        assert str(warehouse) == "Main Warehouse"
    
    def test_warehouse_capacity_validation(self):
        """Test capacity validation."""
        # Test negative capacity
        with pytest.raises(ValidationError):
            warehouse = WarehouseFactory(capacity=-1000)
            warehouse.full_clean()
        
        # Test zero capacity
        with pytest.raises(ValidationError):
            warehouse = WarehouseFactory(capacity=0)
            warehouse.full_clean()
    
    def test_warehouse_utilization_calculation(self):
        """Test utilization calculation."""
        warehouse = WarehouseFactory(capacity=1000)
        
        # No inventory
        assert warehouse.current_utilization == 0
        assert warehouse.available_capacity == 1000
        
        # Add inventory
        inventory = InventoryFactory(warehouse=warehouse, quantity=500)
        assert warehouse.current_utilization == 50.0
        assert warehouse.available_capacity == 500
    
    def test_warehouse_email_validation(self):
        """Test email validation."""
        # Test invalid email format
        with pytest.raises(ValidationError):
            warehouse = WarehouseFactory(contact_email="invalid-email")
            warehouse.full_clean()


@pytest.mark.django_db
@pytest.mark.model
class TestInventoryModel:
    """Test Inventory model."""
    
    def test_inventory_creation(self):
        """Test basic inventory creation."""
        inventory = InventoryFactory()
        assert inventory.product is not None
        assert inventory.warehouse is not None
        assert inventory.quantity >= 0
    
    def test_inventory_str_representation(self):
        """Test string representation."""
        product = ProductFactory(name="Test Product")
        warehouse = WarehouseFactory(name="Test Warehouse")
        inventory = InventoryFactory(product=product, warehouse=warehouse, quantity=100)
        assert str(inventory) == "Test Product at Test Warehouse: 100"
    
    def test_inventory_quantity_validation(self):
        """Test quantity validation."""
        # Test negative quantity
        with pytest.raises(ValidationError):
            inventory = InventoryFactory(quantity=-10)
            inventory.full_clean()
    
    def test_inventory_reserved_quantity_validation(self):
        """Test reserved quantity validation."""
        inventory = InventoryFactory(quantity=100, reserved_quantity=50)
        
        # Test reserved quantity exceeding available quantity
        with pytest.raises(ValidationError):
            inventory.reserved_quantity = 150
            inventory.full_clean()
    
    def test_inventory_available_quantity(self):
        """Test available quantity calculation."""
        inventory = InventoryFactory(quantity=100, reserved_quantity=30)
        assert inventory.available_quantity == 70
    
    def test_inventory_stock_status(self):
        """Test stock status indicators."""
        inventory = InventoryFactory(quantity=100, reorder_point=20)
        
        # In stock
        assert not inventory.is_low_stock
        assert not inventory.is_out_of_stock
        
        # Low stock
        inventory.quantity = 15
        inventory.save()
        assert inventory.is_low_stock
        assert not inventory.is_out_of_stock
        
        # Out of stock
        inventory.quantity = 0
        inventory.save()
        assert inventory.is_out_of_stock
    
    def test_inventory_stock_value(self):
        """Test stock value calculation."""
        product = ProductFactory(unit_price=Decimal('25.00'))
        inventory = InventoryFactory(product=product, quantity=10)
        assert inventory.stock_value == Decimal('250.00')
    
    def test_inventory_unique_constraint(self):
        """Test unique product-warehouse constraint."""
        product = ProductFactory()
        warehouse = WarehouseFactory()
        
        InventoryFactory(product=product, warehouse=warehouse)
        
        # Should not allow duplicate product-warehouse combination
        with pytest.raises(IntegrityError):
            InventoryFactory(product=product, warehouse=warehouse)


@pytest.mark.django_db
@pytest.mark.model
class TestStockMovementModel:
    """Test StockMovement model."""
    
    def test_stock_movement_creation(self):
        """Test basic stock movement creation."""
        movement = StockMovementFactory()
        assert movement.product is not None
        assert movement.warehouse is not None
        assert movement.quantity > 0
        assert movement.movement_type in ['in', 'out', 'transfer', 'adjustment']
    
    def test_stock_movement_str_representation(self):
        """Test string representation."""
        product = ProductFactory(name="Test Product")
        movement = StockMovementFactory(
            product=product,
            movement_type='in',
            quantity=50
        )
        assert str(movement) == "Test Product: IN 50 units"
    
    def test_stock_movement_quantity_validation(self):
        """Test quantity validation."""
        # Test zero quantity
        with pytest.raises(ValidationError):
            movement = StockMovementFactory(quantity=0)
            movement.full_clean()
        
        # Test negative quantity
        with pytest.raises(ValidationError):
            movement = StockMovementFactory(quantity=-10)
            movement.full_clean()
    
    def test_stock_movement_value_calculation(self):
        """Test movement value calculation."""
        product = ProductFactory(unit_price=Decimal('15.00'))
        movement = StockMovementFactory(product=product, quantity=20)
        assert movement.movement_value == Decimal('300.00')


@pytest.mark.django_db
@pytest.mark.model
class TestSupplierModel:
    """Test Supplier model."""
    
    def test_supplier_creation(self):
        """Test basic supplier creation."""
        supplier = SupplierFactory()
        assert supplier.name is not None
        assert supplier.contact_person is not None
    
    def test_supplier_str_representation(self):
        """Test string representation."""
        supplier = SupplierFactory(name="Test Supplier")
        assert str(supplier) == "Test Supplier"
    
    def test_supplier_email_validation(self):
        """Test email validation."""
        # Test invalid email format
        with pytest.raises(ValidationError):
            supplier = SupplierFactory(email="invalid-email")
            supplier.full_clean()
    
    def test_supplier_performance_metrics(self):
        """Test supplier performance calculations."""
        supplier = SupplierFactory()
        
        # No orders
        assert supplier.total_orders == 0
        assert supplier.total_order_value == Decimal('0.00')
        
        # Add orders
        order1 = PurchaseOrderFactory(supplier=supplier, total_amount=Decimal('1000.00'))
        order2 = PurchaseOrderFactory(supplier=supplier, total_amount=Decimal('2000.00'))
        
        assert supplier.total_orders == 2
        assert supplier.total_order_value == Decimal('3000.00')


@pytest.mark.django_db
@pytest.mark.model
class TestPurchaseOrderModel:
    """Test PurchaseOrder model."""
    
    def test_purchase_order_creation(self):
        """Test basic purchase order creation."""
        order = PurchaseOrderFactory()
        assert order.supplier is not None
        assert order.warehouse is not None
        assert order.status in ['draft', 'pending', 'approved', 'ordered', 'received', 'cancelled']
    
    def test_purchase_order_str_representation(self):
        """Test string representation."""
        order = PurchaseOrderFactory(order_number="PO-2024-001")
        assert str(order) == "PO-2024-001"
    
    def test_purchase_order_auto_number_generation(self):
        """Test automatic order number generation."""
        order = PurchaseOrderFactory(order_number="")
        order.save()
        assert order.order_number is not None
        assert order.order_number.startswith("PO-")
    
    def test_purchase_order_status_workflow(self):
        """Test status workflow."""
        order = PurchaseOrderFactory(status='draft')
        
        # Test approve
        user = UserFactory()
        assert order.approve(user)
        assert order.status == 'approved'
        assert order.approved_by == user
        
        # Test mark as ordered
        assert order.mark_as_ordered()
        assert order.status == 'ordered'
        
        # Test receive
        assert order.receive_order()
        assert order.status == 'received'
        
        # Test cancel
        order = PurchaseOrderFactory(status='draft')
        assert order.cancel_order()
        assert order.status == 'cancelled'
    
    def test_purchase_order_validation(self):
        """Test purchase order validation."""
        # Test expected date in past
        with pytest.raises(ValidationError):
            order = PurchaseOrderFactory(expected_date=timezone.now().date() - timezone.timedelta(days=1))
            order.full_clean()
    
    def test_purchase_order_calculations(self):
        """Test purchase order calculations."""
        order = PurchaseOrderFactory()
        
        # Add items
        item1 = PurchaseOrderItemFactory(
            purchase_order=order,
            quantity_ordered=10,
            unit_price=Decimal('25.00')
        )
        item2 = PurchaseOrderItemFactory(
            purchase_order=order,
            quantity_ordered=5,
            unit_price=Decimal('50.00')
        )
        
        assert order.item_count == 2
        assert order.total_quantity == 15
        assert order.received_quantity == 0
        assert not order.is_complete


@pytest.mark.django_db
@pytest.mark.model
class TestPurchaseOrderItemModel:
    """Test PurchaseOrderItem model."""
    
    def test_purchase_order_item_creation(self):
        """Test basic purchase order item creation."""
        item = PurchaseOrderItemFactory()
        assert item.purchase_order is not None
        assert item.product is not None
        assert item.quantity_ordered > 0
        assert item.unit_price > 0
    
    def test_purchase_order_item_str_representation(self):
        """Test string representation."""
        product = ProductFactory(name="Test Product")
        item = PurchaseOrderItemFactory(product=product, quantity_ordered=50)
        assert str(item) == "Test Product: 50 ordered, 0 received"
    
    def test_purchase_order_item_validation(self):
        """Test purchase order item validation."""
        # Test negative quantities
        with pytest.raises(ValidationError):
            item = PurchaseOrderItemFactory(quantity_ordered=-10)
            item.full_clean()
        
        with pytest.raises(ValidationError):
            item = PurchaseOrderItemFactory(quantity_received=-5)
            item.full_clean()
    
    def test_purchase_order_item_calculations(self):
        """Test purchase order item calculations."""
        item = PurchaseOrderItemFactory(
            quantity_ordered=100,
            quantity_received=60,
            unit_price=Decimal('25.00')
        )
        
        assert item.remaining_quantity == 40
        assert item.is_complete is False
        assert item.completion_percentage == 60.0
        
        # Complete the order
        item.quantity_received = 100
        item.save()
        assert item.is_complete is True
        assert item.completion_percentage == 100.0


@pytest.mark.django_db
@pytest.mark.model
class TestStockAlertModel:
    """Test StockAlert model."""
    
    def test_stock_alert_creation(self):
        """Test basic stock alert creation."""
        alert = StockAlertFactory()
        assert alert.product is not None
        assert alert.warehouse is not None
        assert alert.alert_type in ['low_stock', 'out_of_stock', 'overstock']
        assert alert.severity in ['low', 'medium', 'high', 'critical']
    
    def test_stock_alert_str_representation(self):
        """Test string representation."""
        product = ProductFactory(name="Test Product")
        alert = StockAlertFactory(product=product, alert_type='low_stock')
        assert str(alert) == "Low Stock Alert: Test Product"
    
    def test_stock_alert_resolution(self):
        """Test alert resolution."""
        alert = StockAlertFactory()
        user = UserFactory()
        
        assert not alert.is_resolved
        assert alert.is_active
        
        # Resolve alert
        assert alert.resolve(user, "Stock replenished")
        assert alert.is_resolved
        assert not alert.is_active
        assert alert.resolved_by == user
        assert alert.resolution_notes == "Stock replenished"
        
        # Reactivate alert
        assert alert.reactivate()
        assert not alert.is_resolved
        assert alert.is_active
    
    def test_stock_alert_duration_calculation(self):
        """Test alert duration calculation."""
        alert = StockAlertFactory()
        
        # Alert just created
        assert alert.duration == 0
        
        # Simulate time passing
        alert.created_at = timezone.now() - timezone.timedelta(hours=5)
        alert.save()
        assert alert.duration == 5


@pytest.mark.django_db
@pytest.mark.model
class TestAlertRuleModel:
    """Test AlertRule model."""
    
    def test_alert_rule_creation(self):
        """Test basic alert rule creation."""
        rule = AlertRuleFactory()
        assert rule.name is not None
        assert rule.rule_type in ['low_stock', 'out_of_stock', 'overstock']
        assert rule.severity in ['low', 'medium', 'high', 'critical']
    
    def test_alert_rule_str_representation(self):
        """Test string representation."""
        rule = AlertRuleFactory(name="Low Stock Rule")
        assert str(rule) == "Low Stock Rule"
    
    def test_alert_rule_validation(self):
        """Test alert rule validation."""
        # Test invalid thresholds
        with pytest.raises(ValidationError):
            rule = AlertRuleFactory(min_threshold=100, max_threshold=50)
            rule.full_clean()


@pytest.mark.django_db
@pytest.mark.model
class TestAlertNotificationModel:
    """Test AlertNotification model."""
    
    def test_alert_notification_creation(self):
        """Test basic alert notification creation."""
        notification = AlertNotificationFactory()
        assert notification.alert is not None
        assert notification.notification_type in ['email', 'dashboard', 'sms']
        assert notification.status in ['pending', 'sent', 'failed']
    
    def test_alert_notification_str_representation(self):
        """Test string representation."""
        notification = AlertNotificationFactory(recipient="test@example.com")
        assert str(notification) == "test@example.com - pending"


@pytest.mark.django_db
@pytest.mark.model
class TestReportModel:
    """Test Report model."""
    
    def test_report_creation(self):
        """Test basic report creation."""
        report = ReportFactory()
        assert report.name is not None
        assert report.report_type in ['inventory_valuation', 'turnover_analysis', 'stock_aging']
        assert report.format in ['json', 'csv', 'xlsx']
    
    def test_report_str_representation(self):
        """Test string representation."""
        report = ReportFactory(name="Test Report")
        assert str(report) == "Test Report"


@pytest.mark.django_db
@pytest.mark.model
class TestDashboardWidgetModel:
    """Test DashboardWidget model."""
    
    def test_dashboard_widget_creation(self):
        """Test basic dashboard widget creation."""
        widget = DashboardWidgetFactory()
        assert widget.name is not None
        assert widget.widget_type in ['chart', 'table', 'metric', 'gauge']
        assert widget.is_active
    
    def test_dashboard_widget_str_representation(self):
        """Test string representation."""
        widget = DashboardWidgetFactory(name="Test Widget")
        assert str(widget) == "Test Widget" 