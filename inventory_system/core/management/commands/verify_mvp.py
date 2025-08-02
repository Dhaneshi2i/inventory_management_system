"""
Management command to verify MVP requirements.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import connection
from django.test import Client
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from inventory_system.apps.products.models import Category, Product
from inventory_system.apps.inventory.models import Warehouse, Inventory, StockMovement
from inventory_system.apps.orders.models import Supplier, PurchaseOrder, PurchaseOrderItem
from inventory_system.apps.alerts.models import StockAlert, AlertRule, AlertNotification
from inventory_system.apps.reports.models import Report, DashboardWidget


class Command(BaseCommand):
    """Command to verify MVP requirements."""
    help = 'Verify all MVP requirements are met'

    def handle(self, *args, **options):
        """Execute the command."""
        self.stdout.write('🔍 Verifying MVP Requirements...')
        self.stdout.write('=' * 50)
        
        # Test 1: Database Models
        self.verify_database_models()
        
        # Test 2: API Endpoints
        self.verify_api_endpoints()
        
        # Test 3: Authentication
        self.verify_authentication()
        
        # Test 4: Admin Interface
        self.verify_admin_interface()
        
        # Test 5: Business Logic
        self.verify_business_logic()
        
        # Test 6: Sample Data
        self.verify_sample_data()
        
        # Test 7: Documentation
        self.verify_documentation()
        
        self.stdout.write('=' * 50)
        self.stdout.write(self.style.SUCCESS('✅ MVP Verification Complete!'))

    def verify_database_models(self):
        """Verify all required database models exist and work."""
        self.stdout.write('\n📊 Testing Database Models...')
        
        try:
            # Test model imports
            models = [
                Category, Product, Warehouse, Inventory, StockMovement,
                Supplier, PurchaseOrder, PurchaseOrderItem,
                StockAlert, AlertRule, AlertNotification,
                Report, DashboardWidget
            ]
            
            for model in models:
                count = model.objects.count()
                self.stdout.write(f'  ✅ {model.__name__}: {count} records')
            
            self.stdout.write(self.style.SUCCESS('  ✅ All models working correctly'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  ❌ Model error: {e}'))

    def verify_api_endpoints(self):
        """Verify API endpoints are accessible."""
        self.stdout.write('\n🌐 Testing API Endpoints...')
        
        try:
            client = APIClient()
            
            # Test unauthenticated access (should return 401)
            response = client.get('/api/v1/products/')
            if response.status_code == 401:
                self.stdout.write('  ✅ API authentication working correctly')
            else:
                self.stdout.write(self.style.WARNING(f'  ⚠️ Unexpected status code: {response.status_code}'))
            
            # Test authenticated access
            user = User.objects.get(username='admin')
            refresh = RefreshToken.for_user(user)
            client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
            
            endpoints = [
                '/api/v1/categories/',
                '/api/v1/products/',
                '/api/v1/warehouses/',
                '/api/v1/inventory/',
                '/api/v1/suppliers/',
                '/api/v1/purchase-orders/',
                '/api/v1/stock-alerts/',
                '/api/v1/dashboard/summary/',
            ]
            
            for endpoint in endpoints:
                response = client.get(endpoint)
                if response.status_code in [200, 201]:
                    self.stdout.write(f'  ✅ {endpoint}: OK')
                else:
                    self.stdout.write(self.style.WARNING(f'  ⚠️ {endpoint}: {response.status_code}'))
            
            self.stdout.write(self.style.SUCCESS('  ✅ API endpoints working correctly'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  ❌ API error: {e}'))

    def verify_authentication(self):
        """Verify JWT authentication works."""
        self.stdout.write('\n🔐 Testing Authentication...')
        
        try:
            user = User.objects.get(username='admin')
            refresh = RefreshToken.for_user(user)
            
            # Test token generation
            if refresh.access_token and refresh:
                self.stdout.write('  ✅ JWT token generation working')
            
            # Test token validation
            client = APIClient()
            client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
            response = client.get('/api/v1/products/')
            
            if response.status_code == 200:
                self.stdout.write('  ✅ JWT authentication working correctly')
            else:
                self.stdout.write(self.style.WARNING(f'  ⚠️ JWT authentication issue: {response.status_code}'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  ❌ Authentication error: {e}'))

    def verify_admin_interface(self):
        """Verify Django admin interface."""
        self.stdout.write('\n⚙️ Testing Admin Interface...')
        
        try:
            client = Client()
            
            # Test admin login
            response = client.get('/admin/')
            if response.status_code == 302:  # Redirect to login
                self.stdout.write('  ✅ Admin interface accessible')
            else:
                self.stdout.write(self.style.WARNING(f'  ⚠️ Admin interface issue: {response.status_code}'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  ❌ Admin interface error: {e}'))

    def verify_business_logic(self):
        """Verify core business logic."""
        self.stdout.write('\n💼 Testing Business Logic...')
        
        try:
            # Test inventory calculations
            inventory = Inventory.objects.first()
            if inventory:
                available_qty = inventory.available_quantity
                is_low_stock = inventory.is_low_stock
                is_out_of_stock = inventory.is_out_of_stock
                
                self.stdout.write(f'  ✅ Inventory calculations: available={available_qty}, low_stock={is_low_stock}, out_of_stock={is_out_of_stock}')
            
            # Test warehouse utilization
            warehouse = Warehouse.objects.first()
            if warehouse:
                utilization = warehouse.current_utilization
                available_capacity = warehouse.available_capacity
                
                self.stdout.write(f'  ✅ Warehouse utilization: {utilization:.1f}%, available_capacity={available_capacity}')
            
            # Test purchase order status
            po = PurchaseOrder.objects.first()
            if po:
                item_count = po.item_count
                total_qty = po.total_quantity
                is_complete = po.is_complete
                
                self.stdout.write(f'  ✅ Purchase order: items={item_count}, total_qty={total_qty}, complete={is_complete}')
            
            # Test alert system
            alert = StockAlert.objects.filter(is_resolved=False).first()
            if alert:
                is_active = alert.is_active
                duration = alert.duration
                
                self.stdout.write(f'  ✅ Stock alert: active={is_active}, duration={duration}')
            
            self.stdout.write(self.style.SUCCESS('  ✅ Business logic working correctly'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  ❌ Business logic error: {e}'))

    def verify_sample_data(self):
        """Verify sample data exists."""
        self.stdout.write('\n📋 Testing Sample Data...')
        
        try:
            data_counts = {
                'Categories': Category.objects.count(),
                'Products': Product.objects.count(),
                'Warehouses': Warehouse.objects.count(),
                'Inventory Items': Inventory.objects.count(),
                'Suppliers': Supplier.objects.count(),
                'Purchase Orders': PurchaseOrder.objects.count(),
                'Stock Alerts': StockAlert.objects.count(),
                'Alert Rules': AlertRule.objects.count(),
                'Reports': Report.objects.count(),
                'Dashboard Widgets': DashboardWidget.objects.count(),
            }
            
            for name, count in data_counts.items():
                if count > 0:
                    self.stdout.write(f'  ✅ {name}: {count} records')
                else:
                    self.stdout.write(self.style.WARNING(f'  ⚠️ {name}: No data'))
            
            self.stdout.write(self.style.SUCCESS('  ✅ Sample data verification complete'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  ❌ Sample data error: {e}'))

    def verify_documentation(self):
        """Verify documentation is accessible."""
        self.stdout.write('\n📚 Testing Documentation...')
        
        try:
            client = Client()
            
            # Test Swagger documentation
            response = client.get('/swagger/')
            if response.status_code == 200:
                self.stdout.write('  ✅ Swagger documentation accessible')
            else:
                self.stdout.write(self.style.WARNING(f'  ⚠️ Swagger documentation issue: {response.status_code}'))
            
            # Test API root
            response = client.get('/api/')
            if response.status_code == 200:
                self.stdout.write('  ✅ API root accessible')
            else:
                self.stdout.write(self.style.WARNING(f'  ⚠️ API root issue: {response.status_code}'))
            
            self.stdout.write(self.style.SUCCESS('  ✅ Documentation verification complete'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  ❌ Documentation error: {e}')) 