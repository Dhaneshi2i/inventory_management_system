"""
Pytest configuration and fixtures for the Inventory Management System.
"""
import pytest
import os
import django
from django.conf import settings

# Set up Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'inventory_system.settings')
django.setup()


@pytest.fixture(scope="session")
def django_db_setup(django_db_setup, django_db_blocker):
    """Set up the database for the test session."""
    with django_db_blocker.unblock():
        from django.core.management import call_command
        call_command('migrate')


@pytest.fixture
def api_client():
    """Return an API client."""
    from rest_framework.test import APIClient
    return APIClient()


@pytest.fixture
def authenticated_client(api_client, user):
    """Return an authenticated API client."""
    from rest_framework_simplejwt.tokens import RefreshToken
    refresh = RefreshToken.for_user(user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return api_client


@pytest.fixture
def user():
    """Create a test user."""
    from django.contrib.auth.models import User
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )


@pytest.fixture
def admin_user():
    """Create an admin user."""
    from django.contrib.auth.models import User
    return User.objects.create_superuser(
        username='admin',
        email='admin@example.com',
        password='adminpass123'
    )


@pytest.fixture
def category():
    """Create a test category."""
    from inventory_system.apps.products.models import Category
    return Category.objects.create(
        name='Electronics',
        description='Electronic devices and accessories'
    )


@pytest.fixture
def product(category):
    """Create a test product."""
    from inventory_system.apps.products.models import Product
    from decimal import Decimal
    return Product.objects.create(
        name='Test Product',
        sku='TEST001',
        category=category,
        description='A test product',
        unit_price=Decimal('99.99'),
        specifications={'color': 'black', 'weight': '1kg'}
    )


@pytest.fixture
def warehouse():
    """Create a test warehouse."""
    from inventory_system.apps.inventory.models import Warehouse
    return Warehouse.objects.create(
        name='Main Warehouse',
        address='123 Main St, City, State 12345',
        capacity=10000,
        manager='John Doe',
        contact_email='warehouse@example.com',
        contact_phone='555-1234'
    )


@pytest.fixture
def inventory(product, warehouse):
    """Create a test inventory item."""
    from inventory_system.apps.inventory.models import Inventory
    return Inventory.objects.create(
        product=product,
        warehouse=warehouse,
        quantity=100,
        reserved_quantity=10,
        reorder_point=20,
        max_stock_level=500
    )


@pytest.fixture
def supplier():
    """Create a test supplier."""
    from inventory_system.apps.orders.models import Supplier
    return Supplier.objects.create(
        name='Test Supplier',
        contact_person='Jane Smith',
        email='supplier@example.com',
        phone='555-5678',
        address='456 Supplier St, City, State 12345'
    )


@pytest.fixture
def purchase_order(supplier, warehouse):
    """Create a test purchase order."""
    from inventory_system.apps.orders.models import PurchaseOrder
    return PurchaseOrder.objects.create(
        supplier=supplier,
        warehouse=warehouse,
        status='draft',
        order_date='2024-01-01',
        expected_date='2024-01-15',
        total_amount=999.99,
        notes='Test purchase order'
    )


@pytest.fixture
def purchase_order_item(purchase_order, product):
    """Create a test purchase order item."""
    from inventory_system.apps.orders.models import PurchaseOrderItem
    from decimal import Decimal
    return PurchaseOrderItem.objects.create(
        purchase_order=purchase_order,
        product=product,
        quantity_ordered=50,
        quantity_received=0,
        unit_price=Decimal('19.99'),
        total_price=Decimal('999.50')
    )


@pytest.fixture
def stock_movement(product, warehouse):
    """Create a test stock movement."""
    from inventory_system.apps.inventory.models import StockMovement
    return StockMovement.objects.create(
        product=product,
        warehouse=warehouse,
        movement_type='in',
        quantity=100,
        reference_type='purchase_order',
        notes='Initial stock'
    )


@pytest.fixture
def alert_rule(category):
    """Create a test alert rule."""
    from inventory_system.apps.alerts.models import AlertRule
    return AlertRule.objects.create(
        name='Low Stock Alert',
        rule_type='low_stock',
        severity='medium',
        description='Alert when stock is low',
        min_threshold=10,
        email_notification=True,
        dashboard_notification=True
    )


@pytest.fixture
def stock_alert(product, warehouse):
    """Create a test stock alert."""
    from inventory_system.apps.alerts.models import StockAlert
    return StockAlert.objects.create(
        product=product,
        warehouse=warehouse,
        alert_type='low_stock',
        severity='medium',
        message='Stock is running low',
        threshold_value=20,
        current_value=5
    )


@pytest.fixture
def alert_notification(stock_alert):
    """Create a test alert notification."""
    from inventory_system.apps.alerts.models import AlertNotification
    return AlertNotification.objects.create(
        alert=stock_alert,
        notification_type='email',
        status='pending',
        recipient='test@example.com',
        message='Stock alert notification'
    )


@pytest.fixture
def report(user):
    """Create a test report."""
    from inventory_system.apps.reports.models import Report
    return Report.objects.create(
        name='Test Report',
        report_type='inventory_valuation',
        description='A test report',
        format='json',
        data='{"test": "data"}',
        generated_by=user
    )


@pytest.fixture
def dashboard_widget():
    """Create a test dashboard widget."""
    from inventory_system.apps.reports.models import DashboardWidget
    return DashboardWidget.objects.create(
        name='Test Widget',
        widget_type='chart',
        title='Test Chart',
        description='A test widget',
        configuration='{"type": "bar"}',
        position=1,
        is_active=True
    )


@pytest.fixture
def mock_celery(mocker):
    """Mock Celery tasks."""
    mocker.patch('inventory_system.tasks.periodic.check_stock_levels.delay')
    mocker.patch('inventory_system.tasks.periodic.generate_daily_reports.delay')
    mocker.patch('inventory_system.tasks.notifications.send_alert_notifications.delay')
    return mocker


@pytest.fixture
def mock_email(mocker):
    """Mock email sending."""
    return mocker.patch('django.core.mail.send_mail')


@pytest.fixture
def mock_redis(mocker):
    """Mock Redis for Celery."""
    mocker.patch('redis.Redis')
    return mocker 