"""
Factory classes for test data generation using factory_boy.
"""
import factory
from factory.django import DjangoModelFactory
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

from inventory_system.apps.products.models import Category, Product
from inventory_system.apps.inventory.models import Warehouse, Inventory, StockMovement
from inventory_system.apps.orders.models import Supplier, PurchaseOrder, PurchaseOrderItem
from inventory_system.apps.alerts.models import StockAlert, AlertRule, AlertNotification
from inventory_system.apps.reports.models import Report, DashboardWidget


class UserFactory(DjangoModelFactory):
    """Factory for User model."""
    class Meta:
        model = User
    
    username = factory.Sequence(lambda n: f'user{n}')
    email = factory.LazyAttribute(lambda obj: f'{obj.username}@example.com')
    password = factory.PostGenerationMethodCall('set_password', 'testpass123')
    is_active = True


class CategoryFactory(DjangoModelFactory):
    """Factory for Category model."""
    class Meta:
        model = Category
    
    name = factory.Sequence(lambda n: f'Category {n}')
    description = factory.LazyAttribute(lambda obj: f'Description for {obj.name}')


class ProductFactory(DjangoModelFactory):
    """Factory for Product model."""
    class Meta:
        model = Product
    
    name = factory.Sequence(lambda n: f'Product {n}')
    sku = factory.Sequence(lambda n: f'SKU{n:06d}')
    category = factory.SubFactory(CategoryFactory)
    description = factory.LazyAttribute(lambda obj: f'Description for {obj.name}')
    unit_price = factory.Faker('pydecimal', left_digits=3, right_digits=2, positive=True)
    specifications = factory.Dict({
        'color': factory.Faker('color_name'),
        'weight': factory.Faker('pydecimal', left_digits=2, right_digits=2, positive=True),
        'dimensions': factory.Faker('pydecimal', left_digits=2, right_digits=1, positive=True)
    })


class WarehouseFactory(DjangoModelFactory):
    """Factory for Warehouse model."""
    class Meta:
        model = Warehouse
    
    name = factory.Sequence(lambda n: f'Warehouse {n}')
    address = factory.Faker('address')
    capacity = factory.Faker('random_int', min=1000, max=50000)
    manager = factory.Faker('name')
    contact_email = factory.LazyAttribute(lambda obj: f'{obj.name.lower().replace(" ", "")}@example.com')
    contact_phone = factory.Faker('phone_number')
    is_active = True


class InventoryFactory(DjangoModelFactory):
    """Factory for Inventory model."""
    class Meta:
        model = Inventory
    
    product = factory.SubFactory(ProductFactory)
    warehouse = factory.SubFactory(WarehouseFactory)
    quantity = factory.Faker('random_int', min=0, max=1000)
    reserved_quantity = factory.Faker('random_int', min=0, max=100)
    reorder_point = factory.Faker('random_int', min=10, max=50)
    max_stock_level = factory.Faker('random_int', min=200, max=2000)


class SupplierFactory(DjangoModelFactory):
    """Factory for Supplier model."""
    class Meta:
        model = Supplier
    
    name = factory.Sequence(lambda n: f'Supplier {n}')
    contact_person = factory.Faker('name')
    email = factory.LazyAttribute(lambda obj: f'{obj.name.lower().replace(" ", "")}@example.com')
    phone = factory.Faker('phone_number')
    address = factory.Faker('address')
    website = factory.Faker('url')
    tax_id = factory.Faker('random_number', digits=9)
    payment_terms = factory.Iterator(['Net 30', 'Net 60', 'Net 90'])
    is_active = True


class PurchaseOrderFactory(DjangoModelFactory):
    """Factory for PurchaseOrder model."""
    class Meta:
        model = PurchaseOrder
    
    supplier = factory.SubFactory(SupplierFactory)
    warehouse = factory.SubFactory(WarehouseFactory)
    status = factory.Iterator(['draft', 'pending', 'approved', 'ordered', 'received', 'cancelled'])
    order_date = factory.LazyFunction(lambda: timezone.now().date())
    expected_date = factory.LazyFunction(lambda: timezone.now().date() + timedelta(days=14))
    total_amount = factory.Faker('pydecimal', left_digits=4, right_digits=2, positive=True)
    notes = factory.Faker('text', max_nb_chars=200)


class PurchaseOrderItemFactory(DjangoModelFactory):
    """Factory for PurchaseOrderItem model."""
    class Meta:
        model = PurchaseOrderItem
    
    purchase_order = factory.SubFactory(PurchaseOrderFactory)
    product = factory.SubFactory(ProductFactory)
    quantity_ordered = factory.Faker('random_int', min=10, max=100)
    quantity_received = factory.Faker('random_int', min=0, max=50)
    unit_price = factory.Faker('pydecimal', left_digits=3, right_digits=2, positive=True)
    total_price = factory.LazyAttribute(lambda obj: obj.quantity_ordered * obj.unit_price)
    notes = factory.Faker('text', max_nb_chars=100)


class StockMovementFactory(DjangoModelFactory):
    """Factory for StockMovement model."""
    class Meta:
        model = StockMovement
    
    product = factory.SubFactory(ProductFactory)
    warehouse = factory.SubFactory(WarehouseFactory)
    movement_type = factory.Iterator(['in', 'out', 'transfer', 'adjustment'])
    quantity = factory.Faker('random_int', min=1, max=100)
    reference_type = factory.Iterator(['purchase_order', 'sale', 'adjustment', 'transfer'])
    reference_id = factory.Faker('random_int', min=1, max=1000)
    notes = factory.Faker('text', max_nb_chars=150)


class AlertRuleFactory(DjangoModelFactory):
    """Factory for AlertRule model."""
    class Meta:
        model = AlertRule
    
    name = factory.Sequence(lambda n: f'Alert Rule {n}')
    rule_type = factory.Iterator(['low_stock', 'out_of_stock', 'overstock'])
    severity = factory.Iterator(['low', 'medium', 'high', 'critical'])
    description = factory.Faker('text', max_nb_chars=200)
    min_threshold = factory.Faker('random_int', min=5, max=50)
    max_threshold = factory.Faker('random_int', min=100, max=500)
    email_notification = True
    dashboard_notification = True
    auto_resolve = False
    is_active = True


class StockAlertFactory(DjangoModelFactory):
    """Factory for StockAlert model."""
    class Meta:
        model = StockAlert
    
    product = factory.SubFactory(ProductFactory)
    warehouse = factory.SubFactory(WarehouseFactory)
    alert_type = factory.Iterator(['low_stock', 'out_of_stock', 'overstock'])
    severity = factory.Iterator(['low', 'medium', 'high', 'critical'])
    message = factory.Faker('text', max_nb_chars=150)
    threshold_value = factory.Faker('random_int', min=10, max=100)
    current_value = factory.Faker('random_int', min=0, max=50)
    is_resolved = False


class AlertNotificationFactory(DjangoModelFactory):
    """Factory for AlertNotification model."""
    class Meta:
        model = AlertNotification
    
    alert = factory.SubFactory(StockAlertFactory)
    notification_type = factory.Iterator(['email', 'dashboard', 'sms'])
    status = factory.Iterator(['pending', 'sent', 'failed'])
    recipient = factory.Faker('email')
    message = factory.Faker('text', max_nb_chars=200)


class ReportFactory(DjangoModelFactory):
    """Factory for Report model."""
    class Meta:
        model = Report
    
    name = factory.Sequence(lambda n: f'Report {n}')
    report_type = factory.Iterator(['inventory_valuation', 'turnover_analysis', 'stock_aging'])
    description = factory.Faker('text', max_nb_chars=200)
    format = factory.Iterator(['json', 'csv', 'xlsx'])
    data = factory.Dict({
        'total_items': factory.Faker('random_int', min=100, max=1000),
        'total_value': factory.Faker('pydecimal', left_digits=6, right_digits=2, positive=True)
    })
    generated_by = factory.SubFactory(UserFactory)
    is_scheduled = False


class DashboardWidgetFactory(DjangoModelFactory):
    """Factory for DashboardWidget model."""
    class Meta:
        model = DashboardWidget
    
    name = factory.Sequence(lambda n: f'Widget {n}')
    widget_type = factory.Iterator(['chart', 'table', 'metric', 'gauge'])
    title = factory.LazyAttribute(lambda obj: f'{obj.name} Title')
    description = factory.Faker('text', max_nb_chars=150)
    configuration = factory.Dict({
        'type': factory.LazyAttribute(lambda obj: obj.widget_type),
        'data_source': 'inventory',
        'refresh_interval': 300
    })
    position = factory.Sequence(lambda n: n)
    is_active = True
    refresh_interval = factory.Faker('random_int', min=60, max=3600)


# Specialized factories for specific test scenarios
class LowStockInventoryFactory(InventoryFactory):
    """Factory for inventory items with low stock."""
    quantity = factory.Faker('random_int', min=0, max=10)
    reorder_point = factory.Faker('random_int', min=15, max=25)


class OutOfStockInventoryFactory(InventoryFactory):
    """Factory for inventory items that are out of stock."""
    quantity = 0
    reserved_quantity = 0


class HighValueProductFactory(ProductFactory):
    """Factory for high-value products."""
    unit_price = factory.Faker('pydecimal', left_digits=4, right_digits=2, positive=True, min_value=1000)


class LargeWarehouseFactory(WarehouseFactory):
    """Factory for large warehouses."""
    capacity = factory.Faker('random_int', min=50000, max=200000)


class PendingPurchaseOrderFactory(PurchaseOrderFactory):
    """Factory for pending purchase orders."""
    status = 'pending'
    expected_date = factory.LazyFunction(lambda: timezone.now().date() + timedelta(days=7))


class ReceivedPurchaseOrderFactory(PurchaseOrderFactory):
    """Factory for received purchase orders."""
    status = 'received'
    received_date = factory.LazyFunction(lambda: timezone.now().date())


class CriticalStockAlertFactory(StockAlertFactory):
    """Factory for critical stock alerts."""
    severity = 'critical'
    alert_type = 'out_of_stock'
    current_value = 0


class ResolvedStockAlertFactory(StockAlertFactory):
    """Factory for resolved stock alerts."""
    is_resolved = True
    resolved_at = factory.LazyFunction(lambda: timezone.now())
    resolved_by = factory.SubFactory(UserFactory)
    resolution_notes = factory.Faker('text', max_nb_chars=200) 