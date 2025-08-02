"""
Reporting Service for analytics and reporting functionality.
"""
from django.db.models import Sum, F, Q, Avg, Count, Min, Max
from django.utils import timezone
from datetime import timedelta, date
from typing import List, Dict, Optional, Any
import json
import logging

from inventory_system.apps.inventory.models import Inventory, StockMovement, Warehouse
from inventory_system.apps.products.models import Product, Category
from inventory_system.apps.orders.models import PurchaseOrder, Supplier
from inventory_system.apps.alerts.models import StockAlert, AlertRule
from inventory_system.apps.reports.models import Report

logger = logging.getLogger(__name__)


class ReportingService:
    """Service for generating reports and analytics."""
    
    @staticmethod
    def generate_inventory_valuation_report(warehouse_id: Optional[str] = None) -> Dict:
        """Generate comprehensive inventory valuation report."""
        query = Inventory.objects.filter(is_deleted=False).select_related('product', 'warehouse')
        
        if warehouse_id:
            query = query.filter(warehouse_id=warehouse_id)
        
        # Total valuation
        total_valuation = query.aggregate(
            total=Sum(F('quantity') * F('product__unit_price'))
        )['total'] or 0
        
        # Category breakdown
        category_breakdown = query.values('product__category__name').annotate(
            total_quantity=Sum('quantity'),
            total_value=Sum(F('quantity') * F('product__unit_price')),
            product_count=Count('product', distinct=True)
        ).order_by('-total_value')
        
        # Warehouse breakdown
        warehouse_breakdown = query.values('warehouse__name').annotate(
            total_quantity=Sum('quantity'),
            total_value=Sum(F('quantity') * F('product__unit_price')),
            product_count=Count('product', distinct=True)
        ).order_by('-total_value')
        
        # Top products by value
        top_products = query.values('product__name', 'product__sku').annotate(
            total_quantity=Sum('quantity'),
            total_value=Sum(F('quantity') * F('product__unit_price'))
        ).order_by('-total_value')[:10]
        
        # Low stock items
        low_stock_items = query.filter(quantity__lte=F('reorder_point')).values(
            'product__name', 'product__sku', 'warehouse__name'
        ).annotate(
            current_quantity=Sum('quantity'),
            reorder_point=Sum('reorder_point'),
            value=Sum(F('quantity') * F('product__unit_price'))
        ).order_by('current_quantity')
        
        return {
            'report_date': timezone.now().date(),
            'total_valuation': float(total_valuation),
            'total_items': query.count(),
            'category_breakdown': list(category_breakdown),
            'warehouse_breakdown': list(warehouse_breakdown),
            'top_products': list(top_products),
            'low_stock_items': list(low_stock_items),
            'warehouse_filter': warehouse_id
        }
    
    @staticmethod
    def generate_turnover_analysis(days: int = 30) -> Dict:
        """Generate inventory turnover analysis."""
        start_date = timezone.now().date() - timedelta(days=days)
        
        # Get stock movements for the period
        movements = StockMovement.objects.filter(
            created_at__date__gte=start_date,
            is_deleted=False
        ).select_related('product', 'warehouse')
        
        # Calculate turnover by product
        product_turnover = movements.values('product__name', 'product__sku').annotate(
            total_in=Sum('quantity', filter=Q(movement_type='in')),
            total_out=Sum('quantity', filter=Q(movement_type='out')),
            net_movement=Sum('quantity')
        )
        
        # Get average inventory levels
        avg_inventory = Inventory.objects.filter(
            is_deleted=False
        ).values('product__name').annotate(
            avg_quantity=Avg('quantity')
        )
        
        # Calculate turnover rates
        turnover_data = []
        for product in product_turnover:
            product_name = product['product__name']
            
            # Find average inventory for this product
            avg_qty = next(
                (item['avg_quantity'] for item in avg_inventory if item['product__name'] == product_name),
                0
            )
            
            total_out = product['total_out'] or 0
            
            # Calculate turnover rate (annualized)
            if avg_qty > 0:
                daily_turnover = total_out / days
                annual_turnover = daily_turnover * 365
                turnover_rate = annual_turnover / avg_qty
            else:
                turnover_rate = 0
            
            turnover_data.append({
                'product_name': product_name,
                'product_sku': product['product__sku'],
                'total_in': product['total_in'] or 0,
                'total_out': total_out,
                'net_movement': product['net_movement'] or 0,
                'avg_inventory': avg_qty,
                'turnover_rate': round(turnover_rate, 2),
                'days_of_inventory': round(avg_qty / daily_turnover, 1) if daily_turnover > 0 else 0
            })
        
        # Sort by turnover rate
        turnover_data.sort(key=lambda x: x['turnover_rate'], reverse=True)
        
        return {
            'period_days': days,
            'start_date': start_date,
            'end_date': timezone.now().date(),
            'total_movements': movements.count(),
            'turnover_data': turnover_data,
            'fastest_turning': turnover_data[:5],
            'slowest_turning': turnover_data[-5:]
        }
    
    @staticmethod
    def generate_stock_aging_report() -> Dict:
        """Generate stock aging report."""
        # Get inventory items with their last movement date
        inventory_items = Inventory.objects.filter(
            is_deleted=False,
            quantity__gt=0
        ).select_related('product', 'warehouse')
        
        aging_data = []
        
        for item in inventory_items:
            # Get last movement date
            last_movement = StockMovement.objects.filter(
                product=item.product,
                warehouse=item.warehouse,
                is_deleted=False
            ).order_by('-created_at').first()
            
            if last_movement:
                days_since_movement = (timezone.now().date() - last_movement.created_at.date()).days
            else:
                days_since_movement = 999  # No movements recorded
            
            # Categorize by age
            if days_since_movement <= 30:
                age_category = '0-30 days'
            elif days_since_movement <= 60:
                age_category = '31-60 days'
            elif days_since_movement <= 90:
                age_category = '61-90 days'
            elif days_since_movement <= 180:
                age_category = '91-180 days'
            else:
                age_category = '180+ days'
            
            aging_data.append({
                'product_name': item.product.name,
                'product_sku': item.product.sku,
                'warehouse_name': item.warehouse.name,
                'quantity': item.quantity,
                'value': float(item.quantity * item.product.unit_price),
                'days_since_movement': days_since_movement,
                'age_category': age_category,
                'last_movement_date': last_movement.created_at.date() if last_movement else None
            })
        
        # Group by age category
        age_breakdown = {}
        for item in aging_data:
            category = item['age_category']
            if category not in age_breakdown:
                age_breakdown[category] = {
                    'count': 0,
                    'total_quantity': 0,
                    'total_value': 0,
                    'items': []
                }
            
            age_breakdown[category]['count'] += 1
            age_breakdown[category]['total_quantity'] += item['quantity']
            age_breakdown[category]['total_value'] += item['value']
            age_breakdown[category]['items'].append(item)
        
        return {
            'report_date': timezone.now().date(),
            'total_items': len(aging_data),
            'age_breakdown': age_breakdown,
            'oldest_items': sorted(aging_data, key=lambda x: x['days_since_movement'], reverse=True)[:10]
        }
    
    @staticmethod
    def generate_warehouse_utilization_report() -> Dict:
        """Generate warehouse utilization report."""
        warehouses = Warehouse.objects.filter(is_active=True, is_deleted=False)
        
        utilization_data = []
        
        for warehouse in warehouses:
            inventory_items = warehouse.inventory_items.filter(is_deleted=False)
            
            total_quantity = inventory_items.aggregate(total=Sum('quantity'))['total'] or 0
            total_value = inventory_items.aggregate(
                total=Sum(F('quantity') * F('product__unit_price'))
            )['total'] or 0
            
            utilization_percentage = (total_quantity / warehouse.capacity) * 100 if warehouse.capacity > 0 else 0
            available_capacity = max(0, warehouse.capacity - total_quantity)
            
            # Get top products by quantity
            top_products = inventory_items.values('product__name').annotate(
                quantity=Sum('quantity')
            ).order_by('-quantity')[:5]
            
            # Get low stock items
            low_stock_count = inventory_items.filter(quantity__lte=F('reorder_point')).count()
            out_of_stock_count = inventory_items.filter(quantity=0).count()
            
            utilization_data.append({
                'warehouse_id': warehouse.id,
                'warehouse_name': warehouse.name,
                'capacity': warehouse.capacity,
                'current_quantity': total_quantity,
                'current_value': float(total_value),
                'utilization_percentage': round(utilization_percentage, 2),
                'available_capacity': available_capacity,
                'low_stock_count': low_stock_count,
                'out_of_stock_count': out_of_stock_count,
                'top_products': list(top_products),
                'status': 'full' if utilization_percentage >= 90 else 'high' if utilization_percentage >= 75 else 'normal'
            })
        
        # Sort by utilization percentage
        utilization_data.sort(key=lambda x: x['utilization_percentage'], reverse=True)
        
        return {
            'report_date': timezone.now().date(),
            'total_warehouses': len(utilization_data),
            'utilization_data': utilization_data,
            'most_utilized': utilization_data[:3],
            'least_utilized': utilization_data[-3:]
        }
    
    @staticmethod
    def generate_supplier_performance_report(days: int = 90) -> Dict:
        """Generate supplier performance report."""
        start_date = timezone.now().date() - timedelta(days=days)
        
        suppliers = Supplier.objects.filter(is_active=True, is_deleted=False)
        
        performance_data = []
        
        for supplier in suppliers:
            orders = supplier.purchase_orders.filter(
                order_date__gte=start_date,
                is_deleted=False
            )
            
            total_orders = orders.count()
            total_value = orders.aggregate(total=Sum('total_amount'))['total'] or 0
            average_order_value = orders.aggregate(avg=Avg('total_amount'))['avg'] or 0
            
            # Calculate delivery performance
            received_orders = orders.filter(status='received')
            on_time_deliveries = 0
            late_deliveries = 0
            
            for order in received_orders:
                if order.received_date and order.expected_date:
                    if order.received_date <= order.expected_date:
                        on_time_deliveries += 1
                    else:
                        late_deliveries += 1
            
            total_deliveries = on_time_deliveries + late_deliveries
            on_time_percentage = (on_time_deliveries / total_deliveries * 100) if total_deliveries > 0 else 0
            
            # Get recent orders
            recent_orders = orders.order_by('-order_date')[:5]
            
            performance_data.append({
                'supplier_id': supplier.id,
                'supplier_name': supplier.name,
                'total_orders': total_orders,
                'total_value': float(total_value),
                'average_order_value': float(average_order_value),
                'on_time_deliveries': on_time_deliveries,
                'late_deliveries': late_deliveries,
                'on_time_percentage': round(on_time_percentage, 2),
                'recent_orders': [
                    {
                        'order_number': order.order_number,
                        'order_date': order.order_date,
                        'status': order.status,
                        'total_amount': float(order.total_amount)
                    }
                    for order in recent_orders
                ]
            })
        
        # Sort by total value
        performance_data.sort(key=lambda x: x['total_value'], reverse=True)
        
        return {
            'period_days': days,
            'start_date': start_date,
            'end_date': timezone.now().date(),
            'total_suppliers': len(performance_data),
            'performance_data': performance_data,
            'top_suppliers': performance_data[:5],
            'best_performers': sorted(performance_data, key=lambda x: x['on_time_percentage'], reverse=True)[:5]
        }
    
    @staticmethod
    def generate_alert_summary_report() -> Dict:
        """Generate alert summary report."""
        # Get active alerts
        active_alerts = StockAlert.objects.filter(
            is_resolved=False,
            is_deleted=False
        ).select_related('product', 'warehouse')
        
        # Get resolved alerts in last 30 days
        thirty_days_ago = timezone.now().date() - timedelta(days=30)
        resolved_alerts = StockAlert.objects.filter(
            is_resolved=True,
            resolved_at__date__gte=thirty_days_ago,
            is_deleted=False
        ).select_related('product', 'warehouse')
        
        # Alert type breakdown
        active_by_type = active_alerts.values('alert_type').annotate(
            count=Count('id')
        )
        
        # Severity breakdown
        active_by_severity = active_alerts.values('severity').annotate(
            count=Count('id')
        )
        
        # Warehouse breakdown
        active_by_warehouse = active_alerts.values('warehouse__name').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Resolution time analysis
        resolution_times = []
        for alert in resolved_alerts:
            if alert.resolved_at and alert.created_at:
                resolution_time = (alert.resolved_at.date() - alert.created_at.date()).days
                resolution_times.append(resolution_time)
        
        avg_resolution_time = sum(resolution_times) / len(resolution_times) if resolution_times else 0
        
        return {
            'report_date': timezone.now().date(),
            'active_alerts_count': active_alerts.count(),
            'resolved_alerts_count': resolved_alerts.count(),
            'active_by_type': list(active_by_type),
            'active_by_severity': list(active_by_severity),
            'active_by_warehouse': list(active_by_warehouse),
            'avg_resolution_time_days': round(avg_resolution_time, 1),
            'recent_alerts': list(active_alerts.order_by('-created_at')[:10].values(
                'product__name', 'warehouse__name', 'alert_type', 'severity', 'created_at'
            ))
        }
    
    @staticmethod
    def generate_trend_analysis(days: int = 90) -> Dict:
        """Generate trend analysis for inventory and orders."""
        start_date = timezone.now().date() - timedelta(days=days)
        
        # Daily inventory movements
        daily_movements = StockMovement.objects.filter(
            created_at__date__gte=start_date,
            is_deleted=False
        ).values('created_at__date').annotate(
            total_in=Sum('quantity', filter=Q(movement_type='in')),
            total_out=Sum('quantity', filter=Q(movement_type='out')),
            movement_count=Count('id')
        ).order_by('created_at__date')
        
        # Daily purchase orders
        daily_orders = PurchaseOrder.objects.filter(
            order_date__gte=start_date,
            is_deleted=False
        ).values('order_date').annotate(
            order_count=Count('id'),
            total_value=Sum('total_amount')
        ).order_by('order_date')
        
        # Monthly inventory valuation (estimated)
        monthly_valuation = []
        current_month = start_date.replace(day=1)
        
        while current_month <= timezone.now().date():
            month_end = (current_month.replace(day=1) + timedelta(days=32)).replace(day=1) - timedelta(days=1)
            
            # Get inventory at month end (approximation)
            valuation = Inventory.objects.filter(
                is_deleted=False
            ).aggregate(
                total=Sum(F('quantity') * F('product__unit_price'))
            )['total'] or 0
            
            monthly_valuation.append({
                'month': current_month.strftime('%Y-%m'),
                'valuation': float(valuation)
            })
            
            current_month = (current_month.replace(day=1) + timedelta(days=32)).replace(day=1)
        
        return {
            'period_days': days,
            'start_date': start_date,
            'end_date': timezone.now().date(),
            'daily_movements': list(daily_movements),
            'daily_orders': list(daily_orders),
            'monthly_valuation': monthly_valuation
        }
    
    @staticmethod
    def save_report(report_type: str, data: Dict, user) -> Report:
        """Save a generated report to the database."""
        report = Report.objects.create(
            name=f"{report_type.title()} Report - {timezone.now().strftime('%Y-%m-%d %H:%M')}",
            report_type=report_type,
            description=f"Automatically generated {report_type} report",
            format='json',
            data=json.dumps(data, default=str),
            generated_by=user,
            is_scheduled=False
        )
        
        logger.info(f"Report saved: {report.name} by {user.username}")
        return report
    
    @staticmethod
    def get_report_summary() -> Dict:
        """Get summary of all reports."""
        reports = Report.objects.filter(is_deleted=False).order_by('-created_at')
        
        # Group by type
        reports_by_type = {}
        for report in reports:
            report_type = report.report_type
            if report_type not in reports_by_type:
                reports_by_type[report_type] = []
            
            reports_by_type[report_type].append({
                'id': report.id,
                'name': report.name,
                'created_at': report.created_at,
                'generated_by': report.generated_by.username if report.generated_by else 'System'
            })
        
        return {
            'total_reports': reports.count(),
            'reports_by_type': reports_by_type,
            'recent_reports': list(reports[:10].values('id', 'name', 'report_type', 'created_at'))
        } 