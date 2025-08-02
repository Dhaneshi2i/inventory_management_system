"""
Periodic background tasks for the inventory system.
"""
from celery import shared_task
from django.utils import timezone
from datetime import timedelta
import logging

from inventory_system.apps.alerts.services import AlertNotificationService
from inventory_system.services.reporting_service import ReportingService
from inventory_system.apps.alerts.models import StockAlert
from inventory_system.apps.reports.models import Report

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def check_stock_levels(self):
    """Check stock levels and generate alerts."""
    try:
        logger.info("Starting stock level check...")
        
        # Check and create alerts
        created_alerts = AlertNotificationService.check_and_create_alerts()
        
        logger.info(f"Stock level check completed. Created {len(created_alerts)} alerts.")
        return f"Created {len(created_alerts)} alerts"
        
    except Exception as exc:
        logger.error(f"Error in check_stock_levels: {exc}")
        raise self.retry(exc=exc, countdown=60)


@shared_task(bind=True, max_retries=3)
def generate_daily_reports(self):
    """Generate daily reports."""
    try:
        logger.info("Starting daily report generation...")
        
        # Generate various reports
        reports_created = []
        
        # Inventory valuation report
        valuation_data = ReportingService.generate_inventory_valuation_report()
        report = ReportingService.save_report('inventory_valuation', valuation_data, None)
        reports_created.append(report.name)
        
        # Warehouse utilization report
        utilization_data = ReportingService.generate_warehouse_utilization_report()
        report = ReportingService.save_report('warehouse_utilization', utilization_data, None)
        reports_created.append(report.name)
        
        # Alert summary report
        alert_data = ReportingService.generate_alert_summary_report()
        report = ReportingService.save_report('alert_summary', alert_data, None)
        reports_created.append(report.name)
        
        logger.info(f"Daily reports generated: {', '.join(reports_created)}")
        return f"Generated {len(reports_created)} reports"
        
    except Exception as exc:
        logger.error(f"Error in generate_daily_reports: {exc}")
        raise self.retry(exc=exc, countdown=300)


@shared_task(bind=True, max_retries=3)
def cleanup_old_data(self):
    """Clean up old data to maintain performance."""
    try:
        logger.info("Starting data cleanup...")
        
        # Clean up old stock movements (keep last 2 years)
        two_years_ago = timezone.now() - timedelta(days=730)
        old_movements = StockMovement.objects.filter(
            created_at__lt=two_years_ago,
            is_deleted=False
        )
        old_movements_count = old_movements.count()
        old_movements.update(is_deleted=True)
        
        # Clean up old resolved alerts (keep last 1 year)
        one_year_ago = timezone.now() - timedelta(days=365)
        old_alerts = StockAlert.objects.filter(
            is_resolved=True,
            resolved_at__lt=one_year_ago,
            is_deleted=False
        )
        old_alerts_count = old_alerts.count()
        old_alerts.update(is_deleted=True)
        
        # Clean up old reports (keep last 6 months)
        six_months_ago = timezone.now() - timedelta(days=180)
        old_reports = Report.objects.filter(
            created_at__lt=six_months_ago,
            is_deleted=False
        )
        old_reports_count = old_reports.count()
        old_reports.update(is_deleted=True)
        
        logger.info(f"Data cleanup completed. Deleted: {old_movements_count} movements, {old_alerts_count} alerts, {old_reports_count} reports")
        return f"Cleaned up {old_movements_count + old_alerts_count + old_reports_count} records"
        
    except Exception as exc:
        logger.error(f"Error in cleanup_old_data: {exc}")
        raise self.retry(exc=exc, countdown=600)


@shared_task(bind=True, max_retries=3)
def send_alert_notifications(self):
    """Send pending alert notifications."""
    try:
        logger.info("Starting alert notification sending...")
        
        # Get active alerts that need notifications
        active_alerts = StockAlert.objects.filter(
            is_resolved=False,
            is_deleted=False
        ).select_related('product', 'warehouse')
        
        notifications_sent = 0
        
        for alert in active_alerts:
            try:
                # Process notifications for this alert
                AlertNotificationService.process_alert_notifications(alert)
                notifications_sent += 1
            except Exception as e:
                logger.error(f"Error processing notifications for alert {alert.id}: {e}")
                continue
        
        logger.info(f"Alert notifications completed. Processed {notifications_sent} alerts")
        return f"Processed {notifications_sent} alert notifications"
        
    except Exception as exc:
        logger.error(f"Error in send_alert_notifications: {exc}")
        raise self.retry(exc=exc, countdown=120)


@shared_task(bind=True, max_retries=3)
def generate_weekly_reports(self):
    """Generate weekly reports."""
    try:
        logger.info("Starting weekly report generation...")
        
        # Generate weekly reports
        reports_created = []
        
        # Turnover analysis
        turnover_data = ReportingService.generate_turnover_analysis(days=7)
        report = ReportingService.save_report('weekly_turnover', turnover_data, None)
        reports_created.append(report.name)
        
        # Supplier performance
        supplier_data = ReportingService.generate_supplier_performance_report(days=7)
        report = ReportingService.save_report('weekly_supplier_performance', supplier_data, None)
        reports_created.append(report.name)
        
        # Trend analysis
        trend_data = ReportingService.generate_trend_analysis(days=7)
        report = ReportingService.save_report('weekly_trends', trend_data, None)
        reports_created.append(report.name)
        
        logger.info(f"Weekly reports generated: {', '.join(reports_created)}")
        return f"Generated {len(reports_created)} weekly reports"
        
    except Exception as exc:
        logger.error(f"Error in generate_weekly_reports: {exc}")
        raise self.retry(exc=exc, countdown=300)


@shared_task(bind=True, max_retries=3)
def generate_monthly_reports(self):
    """Generate monthly reports."""
    try:
        logger.info("Starting monthly report generation...")
        
        # Generate monthly reports
        reports_created = []
        
        # Stock aging report
        aging_data = ReportingService.generate_stock_aging_report()
        report = ReportingService.save_report('monthly_stock_aging', aging_data, None)
        reports_created.append(report.name)
        
        # Comprehensive inventory valuation
        valuation_data = ReportingService.generate_inventory_valuation_report()
        report = ReportingService.save_report('monthly_inventory_valuation', valuation_data, None)
        reports_created.append(report.name)
        
        # Monthly trend analysis
        trend_data = ReportingService.generate_trend_analysis(days=30)
        report = ReportingService.save_report('monthly_trends', trend_data, None)
        reports_created.append(report.name)
        
        logger.info(f"Monthly reports generated: {', '.join(reports_created)}")
        return f"Generated {len(reports_created)} monthly reports"
        
    except Exception as exc:
        logger.error(f"Error in generate_monthly_reports: {exc}")
        raise self.retry(exc=exc, countdown=300) 