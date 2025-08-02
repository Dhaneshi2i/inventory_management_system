"""
Management command to populate the database with sample data.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
import random

from inventory_system.apps.products.models import Category, Product
from inventory_system.apps.inventory.models import Warehouse, Inventory, StockMovement
from inventory_system.apps.orders.models import Supplier, PurchaseOrder, PurchaseOrderItem
from inventory_system.apps.alerts.models import StockAlert, AlertRule
from inventory_system.apps.reports.models import Report, DashboardWidget


class Command(BaseCommand):
    """Command to populate sample data."""
    help = 'Populate the database with sample data for testing and demonstration'

    def handle(self, *args, **options):
        """Execute the command."""
        self.stdout.write('Creating sample data...')
        
        # Create categories
        categories = self.create_categories()
        
        # Create products
        products = self.create_products(categories)
        
        # Create warehouses
        warehouses = self.create_warehouses()
        
        # Create inventory
        self.create_inventory(products, warehouses)
        
        # Create suppliers
        suppliers = self.create_suppliers()
        
        # Create purchase orders
        self.create_purchase_orders(suppliers, warehouses, products)
        
        # Create stock movements
        self.create_stock_movements(products, warehouses)
        
        # Create alert rules
        self.create_alert_rules(products, categories, warehouses)
        
        # Create sample alerts
        self.create_sample_alerts(products, warehouses)
        
        # Create reports
        self.create_reports()
        
        # Create dashboard widgets
        self.create_dashboard_widgets()
        
        self.stdout.write(
            self.style.SUCCESS('Successfully created sample data!')
        )

    def create_categories(self):
        """Create sample categories."""
        categories_data = [
            {'name': 'Electronics', 'description': 'Electronic devices and accessories'},
            {'name': 'Clothing', 'description': 'Apparel and fashion items'},
            {'name': 'Books', 'description': 'Books and publications'},
            {'name': 'Home & Garden', 'description': 'Home improvement and garden items'},
            {'name': 'Sports', 'description': 'Sports equipment and accessories'},
        ]
        
        categories = []
        for data in categories_data:
            category, created = Category.objects.get_or_create(
                name=data['name'],
                defaults={'description': data['description']}
            )
            categories.append(category)
            if created:
                self.stdout.write(f'Created category: {category.name}')
        
        return categories

    def create_products(self, categories):
        """Create sample products."""
        products_data = [
            # Electronics
            {'name': 'Laptop', 'sku': 'LAP001', 'category': categories[0], 'unit_price': 999.99, 'description': 'High-performance laptop'},
            {'name': 'Smartphone', 'sku': 'PHN001', 'category': categories[0], 'unit_price': 699.99, 'description': 'Latest smartphone model'},
            {'name': 'Headphones', 'sku': 'HP001', 'category': categories[0], 'unit_price': 199.99, 'description': 'Wireless noise-canceling headphones'},
            {'name': 'Tablet', 'sku': 'TAB001', 'category': categories[0], 'unit_price': 399.99, 'description': '10-inch tablet'},
            
            # Clothing
            {'name': 'T-Shirt', 'sku': 'TSH001', 'category': categories[1], 'unit_price': 19.99, 'description': 'Cotton t-shirt'},
            {'name': 'Jeans', 'sku': 'JNS001', 'category': categories[1], 'unit_price': 49.99, 'description': 'Blue denim jeans'},
            {'name': 'Sneakers', 'sku': 'SNK001', 'category': categories[1], 'unit_price': 79.99, 'description': 'Comfortable sneakers'},
            
            # Books
            {'name': 'Python Programming', 'sku': 'BOK001', 'category': categories[2], 'unit_price': 29.99, 'description': 'Learn Python programming'},
            {'name': 'Django Web Development', 'sku': 'BOK002', 'category': categories[2], 'unit_price': 34.99, 'description': 'Django framework guide'},
            
            # Home & Garden
            {'name': 'Garden Tool Set', 'sku': 'GAR001', 'category': categories[3], 'unit_price': 89.99, 'description': 'Complete garden tool set'},
            {'name': 'LED Light Bulb', 'sku': 'LED001', 'category': categories[3], 'unit_price': 9.99, 'description': 'Energy-efficient LED bulb'},
            
            # Sports
            {'name': 'Basketball', 'sku': 'SPT001', 'category': categories[4], 'unit_price': 24.99, 'description': 'Official size basketball'},
            {'name': 'Yoga Mat', 'sku': 'SPT002', 'category': categories[4], 'unit_price': 19.99, 'description': 'Non-slip yoga mat'},
        ]
        
        products = []
        for data in products_data:
            product, created = Product.objects.get_or_create(
                sku=data['sku'],
                defaults={
                    'name': data['name'],
                    'category': data['category'],
                    'unit_price': data['unit_price'],
                    'description': data['description']
                }
            )
            products.append(product)
            if created:
                self.stdout.write(f'Created product: {product.name} ({product.sku})')
        
        return products

    def create_warehouses(self):
        """Create sample warehouses."""
        warehouses_data = [
            {
                'name': 'Main Warehouse',
                'address': '123 Main St, City Center, 12345',
                'capacity': 10000,
                'manager': 'John Smith',
                'contact_email': 'john.smith@company.com',
                'contact_phone': '+1-555-0101'
            },
            {
                'name': 'East Coast Distribution',
                'address': '456 East Ave, East City, 67890',
                'capacity': 8000,
                'manager': 'Sarah Johnson',
                'contact_email': 'sarah.johnson@company.com',
                'contact_phone': '+1-555-0102'
            },
            {
                'name': 'West Coast Hub',
                'address': '789 West Blvd, West City, 11111',
                'capacity': 12000,
                'manager': 'Mike Davis',
                'contact_email': 'mike.davis@company.com',
                'contact_phone': '+1-555-0103'
            }
        ]
        
        warehouses = []
        for data in warehouses_data:
            warehouse, created = Warehouse.objects.get_or_create(
                name=data['name'],
                defaults=data
            )
            warehouses.append(warehouse)
            if created:
                self.stdout.write(f'Created warehouse: {warehouse.name}')
        
        return warehouses

    def create_inventory(self, products, warehouses):
        """Create sample inventory."""
        for product in products:
            for warehouse in warehouses:
                # Random quantity between 0 and 100
                quantity = random.randint(0, 100)
                reorder_point = random.randint(5, 20)
                max_stock_level = random.randint(50, 200)
                
                inventory, created = Inventory.objects.get_or_create(
                    product=product,
                    warehouse=warehouse,
                    defaults={
                        'quantity': quantity,
                        'reorder_point': reorder_point,
                        'max_stock_level': max_stock_level
                    }
                )
                
                if created:
                    self.stdout.write(f'Created inventory: {product.name} at {warehouse.name} ({quantity} units)')

    def create_suppliers(self):
        """Create sample suppliers."""
        suppliers_data = [
            {
                'name': 'Tech Supplies Inc.',
                'contact_person': 'Alice Brown',
                'email': 'alice@techsupplies.com',
                'phone': '+1-555-0201',
                'address': '100 Tech Street, Tech City, 22222',
                'website': 'https://techsupplies.com',
                'tax_id': 'TAX123456',
                'payment_terms': 'Net 30'
            },
            {
                'name': 'Fashion Wholesale Co.',
                'contact_person': 'Bob Wilson',
                'email': 'bob@fashionwholesale.com',
                'phone': '+1-555-0202',
                'address': '200 Fashion Ave, Fashion City, 33333',
                'website': 'https://fashionwholesale.com',
                'tax_id': 'TAX789012',
                'payment_terms': 'Net 45'
            },
            {
                'name': 'Book Publishers Ltd.',
                'contact_person': 'Carol Miller',
                'email': 'carol@bookpublishers.com',
                'phone': '+1-555-0203',
                'address': '300 Book Lane, Book City, 44444',
                'website': 'https://bookpublishers.com',
                'tax_id': 'TAX345678',
                'payment_terms': 'Net 30'
            }
        ]
        
        suppliers = []
        for data in suppliers_data:
            supplier, created = Supplier.objects.get_or_create(
                name=data['name'],
                defaults=data
            )
            suppliers.append(supplier)
            if created:
                self.stdout.write(f'Created supplier: {supplier.name}')
        
        return suppliers

    def create_purchase_orders(self, suppliers, warehouses, products):
        """Create sample purchase orders."""
        # Create a few purchase orders
        for i in range(5):
            supplier = random.choice(suppliers)
            warehouse = random.choice(warehouses)
            
            order = PurchaseOrder.objects.create(
                supplier=supplier,
                warehouse=warehouse,
                status=random.choice(['draft', 'pending', 'approved', 'ordered', 'received']),
                order_date=timezone.now().date() - timedelta(days=random.randint(1, 30)),
                expected_date=timezone.now().date() + timedelta(days=random.randint(1, 14)),
                notes=f'Sample purchase order #{i+1}'
            )
            
            # Add items to the order
            num_items = random.randint(1, 5)
            selected_products = random.sample(list(products), min(num_items, len(products)))
            
            for product in selected_products:
                quantity = random.randint(10, 100)
                unit_price = float(product.unit_price) * random.uniform(0.7, 0.9)  # Supplier price
                
                PurchaseOrderItem.objects.create(
                    purchase_order=order,
                    product=product,
                    quantity_ordered=quantity,
                    unit_price=unit_price,
                    notes=f'Sample order item for {product.name}'
                )
            
            self.stdout.write(f'Created purchase order: {order.order_number}')

    def create_stock_movements(self, products, warehouses):
        """Create sample stock movements."""
        movement_types = ['in', 'out', 'adjustment']
        
        for _ in range(20):
            product = random.choice(products)
            warehouse = random.choice(warehouses)
            movement_type = random.choice(movement_types)
            quantity = random.randint(1, 50)
            
            StockMovement.objects.create(
                product=product,
                warehouse=warehouse,
                movement_type=movement_type,
                quantity=quantity,
                reference_type='sample',
                reference_id=random.randint(1, 1000),
                notes=f'Sample {movement_type} movement for {product.name}'
            )

    def create_alert_rules(self, products, categories, warehouses):
        """Create sample alert rules."""
        # Low stock rule for all products
        AlertRule.objects.get_or_create(
            name='Global Low Stock Alert',
            defaults={
                'rule_type': 'low_stock',
                'severity': 'medium',
                'description': 'Alert when any product stock falls below reorder point',
                'min_threshold': 10,
                'is_active': True
            }
        )
        
        # Out of stock rule for electronics
        AlertRule.objects.get_or_create(
            name='Electronics Out of Stock',
            defaults={
                'rule_type': 'out_of_stock',
                'severity': 'high',
                'description': 'Alert when electronics products are out of stock',
                'category': categories[0],  # Electronics
                'is_active': True
            }
        )
        
        # Overstock rule for clothing
        AlertRule.objects.get_or_create(
            name='Clothing Overstock Alert',
            defaults={
                'rule_type': 'overstock',
                'severity': 'low',
                'description': 'Alert when clothing items are overstocked',
                'category': categories[1],  # Clothing
                'max_threshold': 200,
                'is_active': True
            }
        )
        
        self.stdout.write('Created alert rules')

    def create_sample_alerts(self, products, warehouses):
        """Create sample stock alerts."""
        # Create some low stock alerts
        low_stock_products = random.sample(list(products), min(3, len(products)))
        
        for product in low_stock_products:
            warehouse = random.choice(warehouses)
            
            StockAlert.objects.get_or_create(
                product=product,
                warehouse=warehouse,
                alert_type='low_stock',
                defaults={
                    'severity': 'medium',
                    'message': f'Low stock alert for {product.name} at {warehouse.name}',
                    'threshold_value': 10,
                    'current_value': random.randint(1, 9),
                    'is_resolved': False
                }
            )
        
        self.stdout.write('Created sample alerts')

    def create_reports(self):
        """Create sample reports."""
        report_types = ['inventory_summary', 'stock_movement', 'purchase_orders', 'supplier_analysis']
        
        for report_type in report_types:
            Report.objects.get_or_create(
                name=f'Sample {report_type.replace("_", " ").title()} Report',
                report_type=report_type,
                defaults={
                    'description': f'Sample {report_type} report for demonstration',
                    'format': 'json',
                    'is_scheduled': False
                }
            )
        
        self.stdout.write('Created sample reports')

    def create_dashboard_widgets(self):
        """Create sample dashboard widgets."""
        widgets_data = [
            {
                'name': 'Inventory Summary',
                'widget_type': 'metric',
                'title': 'Total Inventory Value',
                'description': 'Shows total inventory value across all warehouses',
                'data_source': 'inventory_summary',
                'position': 1
            },
            {
                'name': 'Low Stock Alerts',
                'widget_type': 'list',
                'title': 'Low Stock Items',
                'description': 'Shows products with low stock levels',
                'data_source': 'low_stock_alerts',
                'position': 2
            },
            {
                'name': 'Recent Movements',
                'widget_type': 'table',
                'title': 'Recent Stock Movements',
                'description': 'Shows recent inventory movements',
                'data_source': 'recent_movements',
                'position': 3
            },
            {
                'name': 'Pending Orders',
                'widget_type': 'list',
                'title': 'Pending Purchase Orders',
                'description': 'Shows pending purchase orders',
                'data_source': 'pending_orders',
                'position': 4
            }
        ]
        
        for data in widgets_data:
            DashboardWidget.objects.get_or_create(
                name=data['name'],
                defaults={
                    'widget_type': data['widget_type'],
                    'title': data['title'],
                    'description': data['description'],
                    'configuration': {'data_source': data['data_source']},
                    'position': data['position'],
                    'is_active': True,
                    'refresh_interval': 300
                }
            )
        
        self.stdout.write('Created dashboard widgets') 