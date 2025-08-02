"""
Management command to test alert notifications.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from inventory_system.apps.alerts.services import AlertNotificationService
from inventory_system.apps.alerts.models import StockAlert, AlertRule
from inventory_system.apps.inventory.models import Inventory
from inventory_system.apps.products.models import Product


class Command(BaseCommand):
    """Command to test alert notifications."""
    help = 'Test the alert notification system'

    def handle(self, *args, **options):
        """Execute the command."""
        self.stdout.write('Testing alert notification system...')
        
        # Get a sample alert
        alert = StockAlert.objects.filter(is_resolved=False).first()
        
        if not alert:
            self.stdout.write('No active alerts found. Creating a test alert...')
            
            # Create a test alert
            product = Product.objects.first()
            if not product:
                self.stdout.write(self.style.ERROR('No products found. Please run populate_sample_data first.'))
                return
            
            inventory = Inventory.objects.filter(product=product).first()
            if not inventory:
                self.stdout.write(self.style.ERROR('No inventory found. Please run populate_sample_data first.'))
                return
            
            alert = StockAlert.objects.create(
                product=product,
                warehouse=inventory.warehouse,
                alert_type='low_stock',
                severity='medium',
                message=f'Test low stock alert for {product.name}',
                threshold_value=10,
                current_value=5
            )
        
        # Test email notification
        self.stdout.write('Testing email notification...')
        recipients = ['test@example.com']
        success = AlertNotificationService.send_email_notification(alert, recipients)
        
        if success:
            self.stdout.write(self.style.SUCCESS('Email notification sent successfully!'))
        else:
            self.stdout.write(self.style.ERROR('Email notification failed!'))
        
        # Test dashboard notification
        self.stdout.write('Testing dashboard notification...')
        success = AlertNotificationService.send_dashboard_notification(alert)
        
        if success:
            self.stdout.write(self.style.SUCCESS('Dashboard notification created successfully!'))
        else:
            self.stdout.write(self.style.ERROR('Dashboard notification failed!'))
        
        # Test alert rule checking
        self.stdout.write('Testing alert rule checking...')
        created_alerts = AlertNotificationService.check_and_create_alerts()
        
        if created_alerts:
            self.stdout.write(self.style.SUCCESS(f'Created {len(created_alerts)} new alerts!'))
            for alert in created_alerts:
                self.stdout.write(f'  - {alert.product.name} at {alert.warehouse.name}: {alert.alert_type}')
        else:
            self.stdout.write('No new alerts were created.')
        
        self.stdout.write(self.style.SUCCESS('Alert notification test completed!')) 