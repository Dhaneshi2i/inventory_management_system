"""
Unit tests for serializers with all fields and validations.
"""
import pytest
from decimal import Decimal
from django.core.exceptions import ValidationError
from rest_framework.exceptions import ValidationError as DRFValidationError

from inventory_system.api.serializers_v2 import (
    CategorySerializer, ProductSerializer, WarehouseSerializer, InventorySerializer,
    StockMovementSerializer, SupplierSerializer, PurchaseOrderSerializer,
    PurchaseOrderItemSerializer, StockAlertSerializer, AlertRuleSerializer,
    AlertNotificationSerializer, ReportSerializer, DashboardWidgetSerializer,
    DashboardSummarySerializer, BulkInventoryUpdateSerializer, ExportSerializer
)
from tests.factories.factories import (
    CategoryFactory, ProductFactory, WarehouseFactory, InventoryFactory,
    SupplierFactory, PurchaseOrderFactory, PurchaseOrderItemFactory,
    StockMovementFactory, AlertRuleFactory, StockAlertFactory,
    AlertNotificationFactory, ReportFactory, DashboardWidgetFactory,
    UserFactory
)


@pytest.mark.django_db
@pytest.mark.serializer
class TestCategorySerializer:
    """Test CategorySerializer."""
    
    def test_category_serializer_valid_data(self):
        """Test serializer with valid data."""
        category = CategoryFactory()
        serializer = CategorySerializer(category)
        data = serializer.data
        
        assert data['id'] == str(category.id)
        assert data['name'] == category.name
        assert data['description'] == category.description
        assert 'product_count' in data
        assert 'total_value' in data
        assert 'created_at' in data
        assert 'updated_at' in data
    
    def test_category_serializer_create(self):
        """Test serializer create method."""
        data = {
            'name': 'New Category',
            'description': 'A new category'
        }
        serializer = CategorySerializer(data=data)
        assert serializer.is_valid()
        
        category = serializer.save()
        assert category.name == 'New Category'
        assert category.description == 'A new category'
    
    def test_category_serializer_update(self):
        """Test serializer update method."""
        category = CategoryFactory()
        data = {
            'name': 'Updated Category',
            'description': 'Updated description'
        }
        serializer = CategorySerializer(category, data=data, partial=True)
        assert serializer.is_valid()
        
        updated_category = serializer.save()
        assert updated_category.name == 'Updated Category'
        assert updated_category.description == 'Updated description'
    
    def test_category_serializer_validation(self):
        """Test serializer validation."""
        # Test empty name
        data = {'name': '', 'description': 'Test'}
        serializer = CategorySerializer(data=data)
        assert not serializer.is_valid()
        assert 'name' in serializer.errors
        
        # Test very long name
        data = {'name': 'a' * 101, 'description': 'Test'}
        serializer = CategorySerializer(data=data)
        assert not serializer.is_valid()
        assert 'name' in serializer.errors
    
    def test_category_serializer_product_count(self):
        """Test product count calculation."""
        category = CategoryFactory()
        ProductFactory(category=category)
        ProductFactory(category=category)
        
        serializer = CategorySerializer(category)
        assert serializer.data['product_count'] == 2


@pytest.mark.django_db
@pytest.mark.serializer
class TestProductSerializer:
    """Test ProductSerializer."""
    
    def test_product_serializer_valid_data(self):
        """Test serializer with valid data."""
        product = ProductFactory()
        serializer = ProductSerializer(product)
        data = serializer.data
        
        assert data['id'] == str(product.id)
        assert data['name'] == product.name
        assert data['sku'] == product.sku
        assert data['category']['id'] == str(product.category.id)
        assert data['description'] == product.description
        assert data['unit_price'] == str(product.unit_price)
        assert 'total_value' in data
        assert 'stock_status' in data
        assert 'created_at' in data
        assert 'updated_at' in data
    
    def test_product_serializer_create(self):
        """Test serializer create method."""
        category = CategoryFactory()
        data = {
            'name': 'New Product',
            'sku': 'NEW001',
            'category_id': str(category.id),
            'description': 'A new product',
            'unit_price': '99.99'
        }
        serializer = ProductSerializer(data=data)
        assert serializer.is_valid()
        
        product = serializer.save()
        assert product.name == 'New Product'
        assert product.sku == 'NEW001'
        assert product.category == category
        assert product.unit_price == Decimal('99.99')
    
    def test_product_serializer_update(self):
        """Test serializer update method."""
        product = ProductFactory()
        data = {
            'name': 'Updated Product',
            'unit_price': '149.99'
        }
        serializer = ProductSerializer(product, data=data, partial=True)
        assert serializer.is_valid()
        
        updated_product = serializer.save()
        assert updated_product.name == 'Updated Product'
        assert updated_product.unit_price == Decimal('149.99')
    
    def test_product_serializer_validation(self):
        """Test serializer validation."""
        # Test invalid SKU
        data = {'name': 'Test', 'sku': '', 'unit_price': '99.99'}
        serializer = ProductSerializer(data=data)
        assert not serializer.is_valid()
        assert 'sku' in serializer.errors
        
        # Test invalid unit price
        data = {'name': 'Test', 'sku': 'TEST001', 'unit_price': '-10.00'}
        serializer = ProductSerializer(data=data)
        assert not serializer.is_valid()
        assert 'unit_price' in serializer.errors
        
        # Test duplicate SKU
        existing_product = ProductFactory(sku='TEST001')
        data = {'name': 'Test', 'sku': 'TEST001', 'unit_price': '99.99'}
        serializer = ProductSerializer(data=data)
        assert not serializer.is_valid()
        assert 'sku' in serializer.errors
    
    def test_product_serializer_stock_status(self):
        """Test stock status calculation."""
        product = ProductFactory()
        
        # No inventory
        serializer = ProductSerializer(product)
        assert serializer.data['stock_status'] == 'no_stock'
        
        # Add inventory
        InventoryFactory(product=product, quantity=100)
        serializer = ProductSerializer(product)
        assert serializer.data['stock_status'] == 'in_stock'


@pytest.mark.django_db
@pytest.mark.serializer
class TestWarehouseSerializer:
    """Test WarehouseSerializer."""
    
    def test_warehouse_serializer_valid_data(self):
        """Test serializer with valid data."""
        warehouse = WarehouseFactory()
        serializer = WarehouseSerializer(warehouse)
        data = serializer.data
        
        assert data['id'] == str(warehouse.id)
        assert data['name'] == warehouse.name
        assert data['address'] == warehouse.address
        assert data['capacity'] == warehouse.capacity
        assert data['manager'] == warehouse.manager
        assert 'current_utilization' in data
        assert 'available_capacity' in data
        assert 'inventory_count' in data
        assert 'total_inventory_value' in data
    
    def test_warehouse_serializer_create(self):
        """Test serializer create method."""
        data = {
            'name': 'New Warehouse',
            'address': '123 New St, City, State 12345',
            'capacity': 5000,
            'manager': 'John Manager',
            'contact_email': 'warehouse@example.com'
        }
        serializer = WarehouseSerializer(data=data)
        assert serializer.is_valid()
        
        warehouse = serializer.save()
        assert warehouse.name == 'New Warehouse'
        assert warehouse.capacity == 5000
        assert warehouse.manager == 'John Manager'
    
    def test_warehouse_serializer_validation(self):
        """Test serializer validation."""
        # Test invalid capacity
        data = {
            'name': 'Test Warehouse',
            'address': 'Test Address',
            'capacity': -1000
        }
        serializer = WarehouseSerializer(data=data)
        assert not serializer.is_valid()
        assert 'capacity' in serializer.errors


@pytest.mark.django_db
@pytest.mark.serializer
class TestInventorySerializer:
    """Test InventorySerializer."""
    
    def test_inventory_serializer_valid_data(self):
        """Test serializer with valid data."""
        inventory = InventoryFactory()
        serializer = InventorySerializer(inventory)
        data = serializer.data
        
        assert data['id'] == str(inventory.id)
        assert data['product']['id'] == str(inventory.product.id)
        assert data['warehouse']['id'] == str(inventory.warehouse.id)
        assert data['quantity'] == inventory.quantity
        assert data['reserved_quantity'] == inventory.reserved_quantity
        assert 'available_quantity' in data
        assert 'is_low_stock' in data
        assert 'is_out_of_stock' in data
        assert 'stock_value' in data
        assert 'stock_status' in data
    
    def test_inventory_serializer_create(self):
        """Test serializer create method."""
        product = ProductFactory()
        warehouse = WarehouseFactory()
        data = {
            'product_id': str(product.id),
            'warehouse_id': str(warehouse.id),
            'quantity': 100,
            'reserved_quantity': 10,
            'reorder_point': 20,
            'max_stock_level': 500
        }
        serializer = InventorySerializer(data=data)
        assert serializer.is_valid()
        
        inventory = serializer.save()
        assert inventory.product == product
        assert inventory.warehouse == warehouse
        assert inventory.quantity == 100
        assert inventory.reserved_quantity == 10
    
    def test_inventory_serializer_validation(self):
        """Test serializer validation."""
        product = ProductFactory()
        warehouse = WarehouseFactory()
        
        # Test negative quantity
        data = {
            'product_id': str(product.id),
            'warehouse_id': str(warehouse.id),
            'quantity': -10
        }
        serializer = InventorySerializer(data=data)
        assert not serializer.is_valid()
        assert 'quantity' in serializer.errors
        
        # Test reserved quantity exceeding available quantity
        data = {
            'product_id': str(product.id),
            'warehouse_id': str(warehouse.id),
            'quantity': 50,
            'reserved_quantity': 60
        }
        serializer = InventorySerializer(data=data)
        assert not serializer.is_valid()
        assert 'non_field_errors' in serializer.errors


@pytest.mark.django_db
@pytest.mark.serializer
class TestStockMovementSerializer:
    """Test StockMovementSerializer."""
    
    def test_stock_movement_serializer_valid_data(self):
        """Test serializer with valid data."""
        movement = StockMovementFactory()
        serializer = StockMovementSerializer(movement)
        data = serializer.data
        
        assert data['id'] == str(movement.id)
        assert data['product']['id'] == str(movement.product.id)
        assert data['warehouse']['id'] == str(movement.warehouse.id)
        assert data['movement_type'] == movement.movement_type
        assert data['quantity'] == movement.quantity
        assert data['reference_type'] == movement.reference_type
        assert data['notes'] == movement.notes
        assert 'movement_value' in data
        assert 'created_at' in data
    
    def test_stock_movement_serializer_create(self):
        """Test serializer create method."""
        product = ProductFactory()
        warehouse = WarehouseFactory()
        data = {
            'product': product.id,
            'warehouse': warehouse.id,
            'movement_type': 'in',
            'quantity': 50,
            'reference_type': 'purchase_order',
            'notes': 'Test movement'
        }
        serializer = StockMovementSerializer(data=data)
        assert serializer.is_valid()
        
        movement = serializer.save()
        assert movement.product == product
        assert movement.warehouse == warehouse
        assert movement.movement_type == 'in'
        assert movement.quantity == 50
    
    def test_stock_movement_serializer_validation(self):
        """Test serializer validation."""
        product = ProductFactory()
        warehouse = WarehouseFactory()
        
        # Test zero quantity
        data = {
            'product': product.id,
            'warehouse': warehouse.id,
            'movement_type': 'in',
            'quantity': 0
        }
        serializer = StockMovementSerializer(data=data)
        assert not serializer.is_valid()
        assert 'quantity' in serializer.errors


@pytest.mark.django_db
@pytest.mark.serializer
class TestSupplierSerializer:
    """Test SupplierSerializer."""
    
    def test_supplier_serializer_valid_data(self):
        """Test serializer with valid data."""
        supplier = SupplierFactory()
        serializer = SupplierSerializer(supplier)
        data = serializer.data
        
        assert data['id'] == str(supplier.id)
        assert data['name'] == supplier.name
        assert data['contact_person'] == supplier.contact_person
        assert data['email'] == supplier.email
        assert data['phone'] == supplier.phone
        assert data['address'] == supplier.address
        assert 'total_orders' in data
        assert 'total_order_value' in data
        assert 'average_order_value' in data
        assert 'last_order_date' in data
    
    def test_supplier_serializer_create(self):
        """Test serializer create method."""
        data = {
            'name': 'New Supplier',
            'contact_person': 'Jane Doe',
            'email': 'supplier@example.com',
            'phone': '555-1234',
            'address': '123 Supplier St'
        }
        serializer = SupplierSerializer(data=data)
        assert serializer.is_valid()
        
        supplier = serializer.save()
        assert supplier.name == 'New Supplier'
        assert supplier.contact_person == 'Jane Doe'
        assert supplier.email == 'supplier@example.com'
    
    def test_supplier_serializer_validation(self):
        """Test serializer validation."""
        # Test invalid email
        data = {
            'name': 'Test Supplier',
            'contact_person': 'John Doe',
            'email': 'invalid-email'
        }
        serializer = SupplierSerializer(data=data)
        assert not serializer.is_valid()
        assert 'email' in serializer.errors


@pytest.mark.django_db
@pytest.mark.serializer
class TestPurchaseOrderSerializer:
    """Test PurchaseOrderSerializer."""
    
    def test_purchase_order_serializer_valid_data(self):
        """Test serializer with valid data."""
        order = PurchaseOrderFactory()
        serializer = PurchaseOrderSerializer(order)
        data = serializer.data
        
        assert data['id'] == str(order.id)
        assert data['order_number'] == order.order_number
        assert data['supplier']['id'] == str(order.supplier.id)
        assert data['warehouse']['id'] == str(order.warehouse.id)
        assert data['status'] == order.status
        assert data['order_date'] == order.order_date.isoformat()
        assert 'item_count' in data
        assert 'total_quantity' in data
        assert 'received_quantity' in data
        assert 'is_complete' in data
        assert 'completion_percentage' in data
        assert 'days_until_expected' in data
    
    def test_purchase_order_serializer_create(self):
        """Test serializer create method."""
        supplier = SupplierFactory()
        warehouse = WarehouseFactory()
        data = {
            'supplier': supplier.id,
            'warehouse': warehouse.id,
            'status': 'draft',
            'order_date': '2024-01-01',
            'expected_date': '2024-01-15',
            'notes': 'Test order'
        }
        serializer = PurchaseOrderSerializer(data=data)
        assert serializer.is_valid()
        
        order = serializer.save()
        assert order.supplier == supplier
        assert order.warehouse == warehouse
        assert order.status == 'draft'
    
    def test_purchase_order_serializer_validation(self):
        """Test serializer validation."""
        supplier = SupplierFactory()
        warehouse = WarehouseFactory()
        
        # Test expected date in past
        data = {
            'supplier': supplier.id,
            'warehouse': warehouse.id,
            'expected_date': '2020-01-01'
        }
        serializer = PurchaseOrderSerializer(data=data)
        assert not serializer.is_valid()
        assert 'expected_date' in serializer.errors


@pytest.mark.django_db
@pytest.mark.serializer
class TestPurchaseOrderItemSerializer:
    """Test PurchaseOrderItemSerializer."""
    
    def test_purchase_order_item_serializer_valid_data(self):
        """Test serializer with valid data."""
        item = PurchaseOrderItemFactory()
        serializer = PurchaseOrderItemSerializer(item)
        data = serializer.data
        
        assert data['id'] == str(item.id)
        assert data['purchase_order'] == item.purchase_order.id
        assert data['product']['id'] == str(item.product.id)
        assert data['quantity_ordered'] == item.quantity_ordered
        assert data['quantity_received'] == item.quantity_received
        assert data['unit_price'] == str(item.unit_price)
        assert data['total_price'] == str(item.total_price)
        assert 'remaining_quantity' in data
        assert 'is_complete' in data
        assert 'completion_percentage' in data
    
    def test_purchase_order_item_serializer_create(self):
        """Test serializer create method."""
        order = PurchaseOrderFactory()
        product = ProductFactory()
        data = {
            'purchase_order': order.id,
            'product': product.id,
            'quantity_ordered': 50,
            'unit_price': '25.00',
            'notes': 'Test item'
        }
        serializer = PurchaseOrderItemSerializer(data=data)
        assert serializer.is_valid()
        
        item = serializer.save()
        assert item.purchase_order == order
        assert item.product == product
        assert item.quantity_ordered == 50
        assert item.unit_price == Decimal('25.00')
    
    def test_purchase_order_item_serializer_validation(self):
        """Test serializer validation."""
        order = PurchaseOrderFactory()
        product = ProductFactory()
        
        # Test negative quantity
        data = {
            'purchase_order': order.id,
            'product': product.id,
            'quantity_ordered': -10,
            'unit_price': '25.00'
        }
        serializer = PurchaseOrderItemSerializer(data=data)
        assert not serializer.is_valid()
        assert 'quantity_ordered' in serializer.errors


@pytest.mark.django_db
@pytest.mark.serializer
class TestStockAlertSerializer:
    """Test StockAlertSerializer."""
    
    def test_stock_alert_serializer_valid_data(self):
        """Test serializer with valid data."""
        alert = StockAlertFactory()
        serializer = StockAlertSerializer(alert)
        data = serializer.data
        
        assert data['id'] == str(alert.id)
        assert data['product']['id'] == str(alert.product.id)
        assert data['warehouse']['id'] == str(alert.warehouse.id)
        assert data['alert_type'] == alert.alert_type
        assert data['severity'] == alert.severity
        assert data['message'] == alert.message
        assert data['threshold_value'] == alert.threshold_value
        assert data['current_value'] == alert.current_value
        assert data['is_resolved'] == alert.is_resolved
        assert 'is_active' in data
        assert 'duration' in data
        assert 'severity_color' in data
    
    def test_stock_alert_serializer_create(self):
        """Test serializer create method."""
        product = ProductFactory()
        warehouse = WarehouseFactory()
        data = {
            'product': product.id,
            'warehouse': warehouse.id,
            'alert_type': 'low_stock',
            'severity': 'medium',
            'message': 'Stock is running low',
            'threshold_value': 20,
            'current_value': 5
        }
        serializer = StockAlertSerializer(data=data)
        assert serializer.is_valid()
        
        alert = serializer.save()
        assert alert.product == product
        assert alert.warehouse == warehouse
        assert alert.alert_type == 'low_stock'
        assert alert.severity == 'medium'


@pytest.mark.django_db
@pytest.mark.serializer
class TestAlertRuleSerializer:
    """Test AlertRuleSerializer."""
    
    def test_alert_rule_serializer_valid_data(self):
        """Test serializer with valid data."""
        rule = AlertRuleFactory()
        serializer = AlertRuleSerializer(rule)
        data = serializer.data
        
        assert data['id'] == str(rule.id)
        assert data['name'] == rule.name
        assert data['rule_type'] == rule.rule_type
        assert data['severity'] == rule.severity
        assert data['description'] == rule.description
        assert data['min_threshold'] == rule.min_threshold
        assert data['max_threshold'] == rule.max_threshold
        assert data['email_notification'] == rule.email_notification
        assert data['dashboard_notification'] == rule.dashboard_notification
        assert 'alert_count' in data
    
    def test_alert_rule_serializer_create(self):
        """Test serializer create method."""
        data = {
            'name': 'New Alert Rule',
            'rule_type': 'low_stock',
            'severity': 'medium',
            'description': 'Alert when stock is low',
            'min_threshold': 10,
            'email_notification': True,
            'dashboard_notification': True
        }
        serializer = AlertRuleSerializer(data=data)
        assert serializer.is_valid()
        
        rule = serializer.save()
        assert rule.name == 'New Alert Rule'
        assert rule.rule_type == 'low_stock'
        assert rule.severity == 'medium'


@pytest.mark.django_db
@pytest.mark.serializer
class TestAlertNotificationSerializer:
    """Test AlertNotificationSerializer."""
    
    def test_alert_notification_serializer_valid_data(self):
        """Test serializer with valid data."""
        notification = AlertNotificationFactory()
        serializer = AlertNotificationSerializer(notification)
        data = serializer.data
        
        assert data['id'] == str(notification.id)
        assert data['alert']['id'] == str(notification.alert.id)
        assert data['notification_type'] == notification.notification_type
        assert data['status'] == notification.status
        assert data['recipient'] == notification.recipient
        assert data['message'] == notification.message
        assert 'sent_at' in data
        assert 'created_at' in data
        assert 'updated_at' in data


@pytest.mark.django_db
@pytest.mark.serializer
class TestReportSerializer:
    """Test ReportSerializer."""
    
    def test_report_serializer_valid_data(self):
        """Test serializer with valid data."""
        report = ReportFactory()
        serializer = ReportSerializer(report)
        data = serializer.data
        
        assert data['id'] == str(report.id)
        assert data['name'] == report.name
        assert data['report_type'] == report.report_type
        assert data['description'] == report.description
        assert data['format'] == report.format
        assert data['data'] == report.data
        assert 'generated_by' in data
        assert 'file_path' in data
        assert 'created_at' in data
        assert 'updated_at' in data


@pytest.mark.django_db
@pytest.mark.serializer
class TestDashboardWidgetSerializer:
    """Test DashboardWidgetSerializer."""
    
    def test_dashboard_widget_serializer_valid_data(self):
        """Test serializer with valid data."""
        widget = DashboardWidgetFactory()
        serializer = DashboardWidgetSerializer(widget)
        data = serializer.data
        
        assert data['id'] == str(widget.id)
        assert data['name'] == widget.name
        assert data['widget_type'] == widget.widget_type
        assert data['title'] == widget.title
        assert data['description'] == widget.description
        assert data['configuration'] == widget.configuration
        assert data['position'] == widget.position
        assert data['is_active'] == widget.is_active
        assert data['refresh_interval'] == widget.refresh_interval


@pytest.mark.django_db
@pytest.mark.serializer
class TestDashboardSummarySerializer:
    """Test DashboardSummarySerializer."""
    
    def test_dashboard_summary_serializer_valid_data(self):
        """Test serializer with valid data."""
        data = {
            'total_products': 100,
            'total_inventory_value': Decimal('50000.00'),
            'low_stock_items': 10,
            'out_of_stock_items': 5,
            'total_warehouses': 3,
            'active_alerts': 8,
            'pending_orders': 15,
            'recent_movements': [],
            'warehouse_utilization': [],
            'top_products': [],
            'alert_summary': {}
        }
        serializer = DashboardSummarySerializer(data=data)
        assert serializer.is_valid()
        
        validated_data = serializer.validated_data
        assert validated_data['total_products'] == 100
        assert validated_data['total_inventory_value'] == Decimal('50000.00')
        assert validated_data['low_stock_items'] == 10


@pytest.mark.django_db
@pytest.mark.serializer
class TestBulkInventoryUpdateSerializer:
    """Test BulkInventoryUpdateSerializer."""
    
    def test_bulk_inventory_update_serializer_valid_data(self):
        """Test serializer with valid data."""
        data = {
            'updates': [
                {'inventory_id': '123e4567-e89b-12d3-a456-426614174000', 'quantity': 100},
                {'inventory_id': '123e4567-e89b-12d3-a456-426614174001', 'quantity': 200}
            ]
        }
        serializer = BulkInventoryUpdateSerializer(data=data)
        assert serializer.is_valid()
    
    def test_bulk_inventory_update_serializer_validation(self):
        """Test serializer validation."""
        # Test missing inventory_id
        data = {
            'updates': [
                {'quantity': 100}
            ]
        }
        serializer = BulkInventoryUpdateSerializer(data=data)
        assert not serializer.is_valid()
        assert 'updates' in serializer.errors
        
        # Test missing quantity
        data = {
            'updates': [
                {'inventory_id': '123e4567-e89b-12d3-a456-426614174000'}
            ]
        }
        serializer = BulkInventoryUpdateSerializer(data=data)
        assert not serializer.is_valid()
        assert 'updates' in serializer.errors
        
        # Test negative quantity
        data = {
            'updates': [
                {'inventory_id': '123e4567-e89b-12d3-a456-426614174000', 'quantity': -10}
            ]
        }
        serializer = BulkInventoryUpdateSerializer(data=data)
        assert not serializer.is_valid()
        assert 'updates' in serializer.errors


@pytest.mark.django_db
@pytest.mark.serializer
class TestExportSerializer:
    """Test ExportSerializer."""
    
    def test_export_serializer_valid_data(self):
        """Test serializer with valid data."""
        data = {
            'format': 'csv',
            'filters': {'category': 'electronics'},
            'fields': ['name', 'sku', 'unit_price'],
            'date_range': {'start': '2024-01-01', 'end': '2024-12-31'}
        }
        serializer = ExportSerializer(data=data)
        assert serializer.is_valid()
    
    def test_export_serializer_validation(self):
        """Test serializer validation."""
        # Test invalid format
        data = {
            'format': 'invalid_format'
        }
        serializer = ExportSerializer(data=data)
        assert not serializer.is_valid()
        assert 'format' in serializer.errors 