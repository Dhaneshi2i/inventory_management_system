"""
Alert notification services.
"""
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils import timezone
from typing import List, Optional

from .models import StockAlert, AlertNotification


class AlertNotificationService:
    """Service for handling alert notifications."""
    
    @staticmethod
    def send_email_notification(alert: StockAlert, recipients: List[str]) -> bool:
        """Send email notification for a stock alert."""
        try:
            subject = f"Stock Alert: {alert.alert_type.replace('_', ' ').title()}"
            
            context = {
                'alert': alert,
                'product': alert.product,
                'warehouse': alert.warehouse,
                'timestamp': timezone.now(),
            }
            
            # Simple text email for now
            message = f"""
Stock Alert Notification

Alert Type: {alert.alert_type.replace('_', ' ').title()}
Severity: {alert.severity.title()}

Product: {alert.product.name} ({alert.product.sku})
Warehouse: {alert.warehouse.name}
Current Stock: {alert.current_value}
Threshold: {alert.threshold_value}

Message: {alert.message}

This alert was triggered on {alert.created_at.strftime('%Y-%m-%d %H:%M:%S')}.

Please take appropriate action to resolve this stock issue.
            """.strip()
            
            # Send email
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=recipients,
                fail_silently=False,
            )
            
            # Create notification record
            for recipient in recipients:
                AlertNotification.objects.create(
                    alert=alert,
                    notification_type='email',
                    status='sent',
                    recipient=recipient,
                    message=message,
                    sent_at=timezone.now()
                )
            
            return True
            
        except Exception as e:
            # Log the error and create failed notification record
            for recipient in recipients:
                AlertNotification.objects.create(
                    alert=alert,
                    notification_type='email',
                    status='failed',
                    recipient=recipient,
                    message=str(e),
                    error_message=str(e)
                )
            return False
    
    @staticmethod
    def send_dashboard_notification(alert: StockAlert) -> bool:
        """Create dashboard notification for a stock alert."""
        try:
            AlertNotification.objects.create(
                alert=alert,
                notification_type='dashboard',
                status='sent',
                recipient='dashboard',
                message=alert.message,
                sent_at=timezone.now()
            )
            return True
        except Exception as e:
            return False
    
    @staticmethod
    def process_alert_notifications(alert: StockAlert) -> None:
        """Process all notifications for a stock alert."""
        # Get alert rule to determine notification preferences
        alert_rule = alert.get_alert_rule()
        
        if not alert_rule:
            return
        
        # Send email notifications if enabled
        if alert_rule.email_notification:
            # Get recipients (in a real system, this would come from user preferences)
            recipients = ['admin@inventorysystem.com']  # Default recipient
            AlertNotificationService.send_email_notification(alert, recipients)
        
        # Send dashboard notification if enabled
        if alert_rule.dashboard_notification:
            AlertNotificationService.send_dashboard_notification(alert)
    
    @staticmethod
    def check_and_create_alerts() -> List[StockAlert]:
        """Check all alert rules and create alerts where conditions are met."""
        from .models import AlertRule
        from inventory_system.apps.inventory.models import Inventory
        
        created_alerts = []
        
        # Get all active alert rules
        alert_rules = AlertRule.objects.filter(is_active=True, is_deleted=False)
        
        for rule in alert_rules:
            # Get inventory items that match the rule criteria
            inventory_query = Inventory.objects.filter(is_deleted=False)
            
            if rule.product:
                inventory_query = inventory_query.filter(product=rule.product)
            
            if rule.category:
                inventory_query = inventory_query.filter(product__category=rule.category)
            
            if rule.warehouse:
                inventory_query = inventory_query.filter(warehouse=rule.warehouse)
            
            # Check each inventory item against the rule
            for inventory in inventory_query:
                should_alert = False
                alert_type = None
                message = ""
                
                # Check low stock
                if rule.rule_type == 'low_stock' and inventory.quantity <= rule.min_threshold:
                    should_alert = True
                    alert_type = 'low_stock'
                    message = f"Low stock alert: {inventory.product.name} has {inventory.quantity} units (threshold: {rule.min_threshold})"
                
                # Check out of stock
                elif rule.rule_type == 'out_of_stock' and inventory.quantity == 0:
                    should_alert = True
                    alert_type = 'out_of_stock'
                    message = f"Out of stock alert: {inventory.product.name} has 0 units"
                
                # Check overstock
                elif rule.rule_type == 'overstock' and inventory.quantity >= rule.max_threshold:
                    should_alert = True
                    alert_type = 'overstock'
                    message = f"Overstock alert: {inventory.product.name} has {inventory.quantity} units (threshold: {rule.max_threshold})"
                
                if should_alert:
                    # Check if alert already exists and is not resolved
                    existing_alert = StockAlert.objects.filter(
                        product=inventory.product,
                        warehouse=inventory.warehouse,
                        alert_type=alert_type,
                        is_resolved=False,
                        is_deleted=False
                    ).first()
                    
                    if not existing_alert:
                        # Create new alert
                        alert = StockAlert.objects.create(
                            product=inventory.product,
                            warehouse=inventory.warehouse,
                            alert_type=alert_type,
                            severity=rule.severity,
                            message=message,
                            threshold_value=rule.min_threshold if rule.rule_type == 'low_stock' else rule.max_threshold,
                            current_value=inventory.quantity
                        )
                        created_alerts.append(alert)
                        
                        # Process notifications
                        AlertNotificationService.process_alert_notifications(alert)
        
        return created_alerts 