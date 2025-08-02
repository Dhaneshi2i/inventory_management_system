"""
Notification background tasks for the inventory system.
"""
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
import logging

from inventory_system.apps.alerts.models import StockAlert, AlertNotification
from inventory_system.apps.alerts.services import AlertNotificationService

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def send_alert_notifications(self):
    """Send pending alert notifications."""
    try:
        logger.info("Starting alert notification sending...")
        
        # Get pending notifications
        pending_notifications = AlertNotification.objects.filter(
            status='pending',
            is_deleted=False
        ).select_related('alert', 'alert__product', 'alert__warehouse')
        
        notifications_sent = 0
        notifications_failed = 0
        
        for notification in pending_notifications:
            try:
                if notification.notification_type == 'email':
                    success = send_email_notification(notification)
                elif notification.notification_type == 'dashboard':
                    success = create_dashboard_notification(notification)
                else:
                    logger.warning(f"Unknown notification type: {notification.notification_type}")
                    continue
                
                if success:
                    notification.status = 'sent'
                    notification.sent_at = timezone.now()
                    notification.save()
                    notifications_sent += 1
                else:
                    notification.status = 'failed'
                    notification.error_message = 'Failed to send notification'
                    notification.save()
                    notifications_failed += 1
                    
            except Exception as e:
                logger.error(f"Error sending notification {notification.id}: {e}")
                notification.status = 'failed'
                notification.error_message = str(e)
                notification.save()
                notifications_failed += 1
        
        logger.info(f"Notification sending completed. Sent: {notifications_sent}, Failed: {notifications_failed}")
        return f"Sent {notifications_sent} notifications, {notifications_failed} failed"
        
    except Exception as exc:
        logger.error(f"Error in send_alert_notifications: {exc}")
        raise self.retry(exc=exc, countdown=120)


@shared_task(bind=True, max_retries=3)
def send_bulk_email_notifications(self, alert_ids, recipients):
    """Send bulk email notifications for multiple alerts."""
    try:
        logger.info(f"Starting bulk email notifications for {len(alert_ids)} alerts...")
        
        alerts = StockAlert.objects.filter(
            id__in=alert_ids,
            is_deleted=False
        ).select_related('product', 'warehouse')
        
        if not alerts.exists():
            logger.warning("No alerts found for bulk notification")
            return "No alerts found"
        
        # Create email content
        subject = f"Stock Alert Summary - {timezone.now().strftime('%Y-%m-%d')}"
        
        # Build email body
        email_body = "Stock Alert Summary\n\n"
        email_body += f"Generated on: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        for alert in alerts:
            email_body += f"Alert: {alert.alert_type.replace('_', ' ').title()}\n"
            email_body += f"Product: {alert.product.name} ({alert.product.sku})\n"
            email_body += f"Warehouse: {alert.warehouse.name}\n"
            email_body += f"Severity: {alert.severity.title()}\n"
            email_body += f"Message: {alert.message}\n"
            email_body += f"Current Stock: {alert.current_value}\n"
            email_body += f"Threshold: {alert.threshold_value}\n"
            email_body += "-" * 50 + "\n\n"
        
        # Send email
        send_mail(
            subject=subject,
            message=email_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipients,
            fail_silently=False,
        )
        
        logger.info(f"Bulk email notifications sent to {len(recipients)} recipients")
        return f"Sent bulk notifications to {len(recipients)} recipients"
        
    except Exception as exc:
        logger.error(f"Error in send_bulk_email_notifications: {exc}")
        raise self.retry(exc=exc, countdown=300)


@shared_task(bind=True, max_retries=3)
def send_daily_alert_summary(self, recipients):
    """Send daily alert summary email."""
    try:
        logger.info("Starting daily alert summary...")
        
        # Get alerts from the last 24 hours
        yesterday = timezone.now().date() - timezone.timedelta(days=1)
        
        new_alerts = StockAlert.objects.filter(
            created_at__date=yesterday,
            is_deleted=False
        ).select_related('product', 'warehouse')
        
        resolved_alerts = StockAlert.objects.filter(
            resolved_at__date=yesterday,
            is_resolved=True,
            is_deleted=False
        ).select_related('product', 'warehouse')
        
        # Get active alerts count
        active_alerts = StockAlert.objects.filter(
            is_resolved=False,
            is_deleted=False
        ).count()
        
        # Create email content
        subject = f"Daily Alert Summary - {yesterday.strftime('%Y-%m-%d')}"
        
        email_body = f"Daily Alert Summary for {yesterday.strftime('%Y-%m-%d')}\n\n"
        email_body += f"Generated on: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        email_body += f"Active Alerts: {active_alerts}\n"
        email_body += f"New Alerts Today: {new_alerts.count()}\n"
        email_body += f"Resolved Alerts Today: {resolved_alerts.count()}\n\n"
        
        if new_alerts.exists():
            email_body += "NEW ALERTS:\n"
            email_body += "=" * 50 + "\n"
            for alert in new_alerts:
                email_body += f"• {alert.alert_type.replace('_', ' ').title()}: {alert.product.name} at {alert.warehouse.name}\n"
                email_body += f"  Severity: {alert.severity.title()}, Stock: {alert.current_value}\n\n"
        
        if resolved_alerts.exists():
            email_body += "RESOLVED ALERTS:\n"
            email_body += "=" * 50 + "\n"
            for alert in resolved_alerts:
                email_body += f"• {alert.alert_type.replace('_', ' ').title()}: {alert.product.name} at {alert.warehouse.name}\n"
                email_body += f"  Resolved by: {alert.resolved_by.username if alert.resolved_by else 'System'}\n\n"
        
        # Send email
        send_mail(
            subject=subject,
            message=email_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipients,
            fail_silently=False,
        )
        
        logger.info(f"Daily alert summary sent to {len(recipients)} recipients")
        return f"Sent daily summary to {len(recipients)} recipients"
        
    except Exception as exc:
        logger.error(f"Error in send_daily_alert_summary: {exc}")
        raise self.retry(exc=exc, countdown=300)


@shared_task(bind=True, max_retries=3)
def send_weekly_report_notifications(self, recipients):
    """Send weekly report notifications."""
    try:
        logger.info("Starting weekly report notifications...")
        
        from inventory_system.services.reporting_service import ReportingService
        
        # Generate weekly reports
        reports = []
        
        # Inventory valuation
        valuation_data = ReportingService.generate_inventory_valuation_report()
        reports.append(('Inventory Valuation', valuation_data))
        
        # Warehouse utilization
        utilization_data = ReportingService.generate_warehouse_utilization_report()
        reports.append(('Warehouse Utilization', utilization_data))
        
        # Alert summary
        alert_data = ReportingService.generate_alert_summary_report()
        reports.append(('Alert Summary', alert_data))
        
        # Create email content
        subject = f"Weekly Inventory Report - {timezone.now().strftime('%Y-%m-%d')}"
        
        email_body = f"Weekly Inventory Management Report\n\n"
        email_body += f"Generated on: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        for report_name, data in reports:
            email_body += f"{report_name.upper()}:\n"
            email_body += "=" * 50 + "\n"
            
            if report_name == 'Inventory Valuation':
                email_body += f"Total Valuation: ${data['total_valuation']:,.2f}\n"
                email_body += f"Total Items: {data['total_items']}\n"
                email_body += f"Low Stock Items: {len(data['low_stock_items'])}\n\n"
            
            elif report_name == 'Warehouse Utilization':
                email_body += f"Total Warehouses: {data['total_warehouses']}\n"
                for warehouse in data['utilization_data'][:3]:  # Top 3
                    email_body += f"• {warehouse['warehouse_name']}: {warehouse['utilization_percentage']}% utilized\n"
                email_body += "\n"
            
            elif report_name == 'Alert Summary':
                email_body += f"Active Alerts: {data['active_alerts_count']}\n"
                email_body += f"Resolved This Week: {data['resolved_alerts_count']}\n"
                email_body += f"Avg Resolution Time: {data['avg_resolution_time_days']} days\n\n"
        
        # Send email
        send_mail(
            subject=subject,
            message=email_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipients,
            fail_silently=False,
        )
        
        logger.info(f"Weekly report notifications sent to {len(recipients)} recipients")
        return f"Sent weekly reports to {len(recipients)} recipients"
        
    except Exception as exc:
        logger.error(f"Error in send_weekly_report_notifications: {exc}")
        raise self.retry(exc=exc, countdown=300)


def send_email_notification(notification):
    """Send individual email notification."""
    try:
        alert = notification.alert
        
        subject = f"Stock Alert: {alert.alert_type.replace('_', ' ').title()}"
        
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
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[notification.recipient],
            fail_silently=False,
        )
        
        return True
        
    except Exception as e:
        logger.error(f"Error sending email notification: {e}")
        return False


def create_dashboard_notification(notification):
    """Create dashboard notification."""
    try:
        # Dashboard notifications are typically handled by the frontend
        # This function would update the notification status
        notification.status = 'sent'
        notification.sent_at = timezone.now()
        notification.save()
        return True
        
    except Exception as e:
        logger.error(f"Error creating dashboard notification: {e}")
        return False 