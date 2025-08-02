"""
Reports and analytics models for inventory management system.
"""
from typing import Optional, Dict, Any
from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db.models import Sum, Avg, Count
from inventory_system.core.models import BaseModel
from inventory_system.apps.products.models import Product, Category
from inventory_system.apps.inventory.models import Warehouse, Inventory, StockMovement
from inventory_system.apps.orders.models import PurchaseOrder, Supplier


class Report(BaseModel):
    """
    Report model for storing generated reports and analytics.
    """
    REPORT_TYPES = [
        ('inventory_summary', 'Inventory Summary'),
        ('stock_movement', 'Stock Movement'),
        ('purchase_orders', 'Purchase Orders'),
        ('supplier_analysis', 'Supplier Analysis'),
        ('warehouse_utilization', 'Warehouse Utilization'),
        ('product_performance', 'Product Performance'),
        ('custom', 'Custom Report'),
    ]
    
    FORMAT_CHOICES = [
        ('json', 'JSON'),
        ('csv', 'CSV'),
        ('pdf', 'PDF'),
        ('excel', 'Excel'),
    ]
    
    name = models.CharField(max_length=200, help_text="Report name")
    report_type = models.CharField(
        max_length=50, 
        choices=REPORT_TYPES,
        help_text="Type of report"
    )
    description = models.TextField(blank=True, help_text="Report description")
    format = models.CharField(
        max_length=10, 
        choices=FORMAT_CHOICES,
        default='json',
        help_text="Report format"
    )
    parameters = models.JSONField(default=dict, blank=True, help_text="Report parameters")
    data = models.JSONField(default=dict, blank=True, help_text="Report data")
    file_path = models.CharField(max_length=500, blank=True, help_text="File path if exported")
    generated_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='generated_reports',
        help_text="User who generated the report"
    )
    is_scheduled = models.BooleanField(default=False, help_text="Whether report is scheduled")
    schedule_frequency = models.CharField(
        max_length=20, 
        blank=True,
        help_text="Schedule frequency (daily, weekly, monthly)"
    )
    
    class Meta:
        verbose_name = "Report"
        verbose_name_plural = "Reports"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['report_type']),
            models.Index(fields=['format']),
            models.Index(fields=['is_scheduled']),
            models.Index(fields=['generated_by']),
        ]

    def __str__(self) -> str:
        return self.name

    def clean(self) -> None:
        """Validate report data."""
        if self.name:
            self.name = self.name.strip()
            if not self.name:
                raise ValidationError("Report name cannot be empty")

    def generate_data(self) -> Dict[str, Any]:
        """Generate report data based on type."""
        if self.report_type == 'inventory_summary':
            return self._generate_inventory_summary()
        elif self.report_type == 'stock_movement':
            return self._generate_stock_movement_report()
        elif self.report_type == 'purchase_orders':
            return self._generate_purchase_orders_report()
        elif self.report_type == 'supplier_analysis':
            return self._generate_supplier_analysis()
        elif self.report_type == 'warehouse_utilization':
            return self._generate_warehouse_utilization()
        elif self.report_type == 'product_performance':
            return self._generate_product_performance()
        else:
            return {}

    def _generate_inventory_summary(self) -> Dict[str, Any]:
        """Generate inventory summary report."""
        from django.db.models import Sum, Count
        
        # Total products
        total_products = Product.objects.filter(is_deleted=False).count()
        
        # Total inventory value
        total_value = Inventory.objects.filter(
            is_deleted=False
        ).aggregate(
            total=Sum(F('quantity') * F('product__unit_price'))
        )['total'] or 0
        
        # Low stock items
        low_stock_items = Inventory.objects.filter(
            is_deleted=False,
            quantity__lte=models.F('reorder_point')
        ).count()
        
        # Out of stock items
        out_of_stock_items = Inventory.objects.filter(
            is_deleted=False,
            quantity=0
        ).count()
        
        # Warehouse utilization
        warehouse_data = []
        for warehouse in Warehouse.objects.filter(is_active=True, is_deleted=False):
            warehouse_data.append({
                'name': warehouse.name,
                'capacity': warehouse.capacity,
                'current_stock': warehouse.inventory_items.filter(is_deleted=False).aggregate(
                    total=models.Sum('quantity')
                )['total'] or 0,
                'utilization_percentage': warehouse.current_utilization
            })
        
        return {
            'total_products': total_products,
            'total_inventory_value': float(total_value),
            'low_stock_items': low_stock_items,
            'out_of_stock_items': out_of_stock_items,
            'warehouse_utilization': warehouse_data,
            'generated_at': self.created_at.isoformat()
        }

    def _generate_stock_movement_report(self) -> Dict[str, Any]:
        """Generate stock movement report."""
        from django.utils import timezone
        from datetime import timedelta
        
        # Get date range from parameters or default to last 30 days
        days = self.parameters.get('days', 30)
        start_date = timezone.now() - timedelta(days=days)
        
        movements = StockMovement.objects.filter(
            created_at__gte=start_date,
            is_deleted=False
        ).select_related('product', 'warehouse')
        
        movement_summary = movements.values('movement_type').annotate(
            count=Count('id'),
            total_quantity=Sum('quantity')
        )
        
        recent_movements = movements.order_by('-created_at')[:50]
        
        return {
            'period_days': days,
            'start_date': start_date.isoformat(),
            'end_date': timezone.now().isoformat(),
            'total_movements': movements.count(),
            'movement_summary': list(movement_summary),
            'recent_movements': [
                {
                    'product': movement.product.name,
                    'warehouse': movement.warehouse.name,
                    'type': movement.get_movement_type_display(),
                    'quantity': movement.quantity,
                    'date': movement.created_at.isoformat()
                }
                for movement in recent_movements
            ]
        }

    def _generate_purchase_orders_report(self) -> Dict[str, Any]:
        """Generate purchase orders report."""
        from django.utils import timezone
        from datetime import timedelta
        
        # Get date range from parameters or default to last 30 days
        days = self.parameters.get('days', 30)
        start_date = timezone.now() - timedelta(days=days)
        
        orders = PurchaseOrder.objects.filter(
            created_at__gte=start_date,
            is_deleted=False
        ).select_related('supplier', 'warehouse')
        
        status_summary = orders.values('status').annotate(
            count=Count('id'),
            total_amount=Sum('total_amount')
        )
        
        supplier_summary = orders.values('supplier__name').annotate(
            count=Count('id'),
            total_amount=Sum('total_amount')
        )
        
        return {
            'period_days': days,
            'total_orders': orders.count(),
            'total_amount': float(orders.aggregate(total=Sum('total_amount'))['total'] or 0),
            'status_summary': list(status_summary),
            'supplier_summary': list(supplier_summary),
            'recent_orders': [
                {
                    'order_number': order.order_number,
                    'supplier': order.supplier.name,
                    'warehouse': order.warehouse.name,
                    'status': order.get_status_display(),
                    'total_amount': float(order.total_amount),
                    'order_date': order.order_date.isoformat()
                }
                for order in orders.order_by('-created_at')[:20]
            ]
        }

    def _generate_supplier_analysis(self) -> Dict[str, Any]:
        """Generate supplier analysis report."""
        suppliers = Supplier.objects.filter(is_active=True, is_deleted=False)
        
        supplier_data = []
        for supplier in suppliers:
            orders = supplier.purchase_orders.filter(is_deleted=False)
            supplier_data.append({
                'name': supplier.name,
                'total_orders': orders.count(),
                'total_amount': float(orders.aggregate(total=Sum('total_amount'))['total'] or 0),
                'avg_order_value': float(orders.aggregate(avg=Avg('total_amount'))['avg'] or 0),
                'last_order_date': orders.order_by('-created_at').first().created_at.isoformat() if orders.exists() else None
            })
        
        return {
            'total_suppliers': suppliers.count(),
            'supplier_data': supplier_data,
            'top_suppliers_by_value': sorted(supplier_data, key=lambda x: x['total_amount'], reverse=True)[:10]
        }

    def _generate_warehouse_utilization(self) -> Dict[str, Any]:
        """Generate warehouse utilization report."""
        warehouses = Warehouse.objects.filter(is_active=True, is_deleted=False)
        
        warehouse_data = []
        for warehouse in warehouses:
            inventory_items = warehouse.inventory_items.filter(is_deleted=False)
            total_stock = inventory_items.aggregate(total=Sum('quantity'))['total'] or 0
            total_value = inventory_items.aggregate(
                total=Sum(F('quantity') * F('product__unit_price'))
            )['total'] or 0
            
            warehouse_data.append({
                'name': warehouse.name,
                'capacity': warehouse.capacity,
                'current_stock': total_stock,
                'utilization_percentage': (total_stock / warehouse.capacity * 100) if warehouse.capacity > 0 else 0,
                'total_value': float(total_value),
                'product_count': inventory_items.values('product').distinct().count()
            })
        
        return {
            'total_warehouses': warehouses.count(),
            'warehouse_data': warehouse_data,
            'average_utilization': sum(w['utilization_percentage'] for w in warehouse_data) / len(warehouse_data) if warehouse_data else 0
        }

    def _generate_product_performance(self) -> Dict[str, Any]:
        """Generate product performance report."""
        from django.utils import timezone
        from datetime import timedelta
        
        days = self.parameters.get('days', 30)
        start_date = timezone.now() - timedelta(days=days)
        
        # Get products with their movement data
        products = Product.objects.filter(is_deleted=False)
        
        product_data = []
        for product in products:
            # Get stock movements for this product
            movements = StockMovement.objects.filter(
                product=product,
                created_at__gte=start_date,
                is_deleted=False
            )
            
            # Calculate movement metrics
            stock_in = movements.filter(movement_type='in').aggregate(total=Sum('quantity'))['total'] or 0
            stock_out = movements.filter(movement_type='out').aggregate(total=Sum('quantity'))['total'] or 0
            
            # Get current inventory
            current_stock = product.inventory_items.filter(is_deleted=False).aggregate(
                total=Sum('quantity')
            )['total'] or 0
            
            product_data.append({
                'name': product.name,
                'sku': product.sku,
                'category': product.category.name,
                'current_stock': current_stock,
                'stock_in': stock_in,
                'stock_out': stock_out,
                'turnover_rate': (stock_out / current_stock) if current_stock > 0 else 0,
                'total_value': float(current_stock * product.unit_price)
            })
        
        return {
            'period_days': days,
            'total_products': len(product_data),
            'product_data': product_data,
            'top_products_by_turnover': sorted(product_data, key=lambda x: x['turnover_rate'], reverse=True)[:20],
            'top_products_by_value': sorted(product_data, key=lambda x: x['total_value'], reverse=True)[:20]
        }


class DashboardWidget(BaseModel):
    """
    Dashboard widget model for customizable dashboard components.
    """
    WIDGET_TYPES = [
        ('chart', 'Chart'),
        ('metric', 'Metric'),
        ('table', 'Table'),
        ('list', 'List'),
    ]
    
    name = models.CharField(max_length=100, help_text="Widget name")
    widget_type = models.CharField(
        max_length=20, 
        choices=WIDGET_TYPES,
        help_text="Type of widget"
    )
    title = models.CharField(max_length=200, help_text="Widget title")
    description = models.TextField(blank=True, help_text="Widget description")
    configuration = models.JSONField(default=dict, blank=True, help_text="Widget configuration")
    position = models.PositiveIntegerField(default=0, help_text="Widget position on dashboard")
    is_active = models.BooleanField(default=True, help_text="Whether widget is active")
    refresh_interval = models.PositiveIntegerField(
        default=300, 
        help_text="Refresh interval in seconds"
    )
    
    class Meta:
        verbose_name = "Dashboard Widget"
        verbose_name_plural = "Dashboard Widgets"
        ordering = ['position', 'name']
        indexes = [
            models.Index(fields=['widget_type']),
            models.Index(fields=['is_active']),
            models.Index(fields=['position']),
        ]

    def __str__(self) -> str:
        return self.name

    def clean(self) -> None:
        """Validate widget data."""
        if self.name:
            self.name = self.name.strip()
            if not self.name:
                raise ValidationError("Widget name cannot be empty")

    def get_data(self) -> Dict[str, Any]:
        """Get widget data based on configuration."""
        data_source = self.configuration.get('data_source', '')
        
        if data_source == 'inventory_summary':
            return self._get_inventory_summary_data()
        elif data_source == 'recent_movements':
            return self._get_recent_movements_data()
        elif data_source == 'low_stock_alerts':
            return self._get_low_stock_alerts_data()
        elif data_source == 'pending_orders':
            return self._get_pending_orders_data()
        else:
            return {}

    def _get_inventory_summary_data(self) -> Dict[str, Any]:
        """Get inventory summary data for widget."""
        total_products = Product.objects.filter(is_deleted=False).count()
        total_value = Inventory.objects.filter(
            is_deleted=False
        ).aggregate(
            total=Sum(F('quantity') * F('product__unit_price'))
        )['total'] or 0
        
        return {
            'total_products': total_products,
            'total_value': float(total_value),
            'low_stock_count': Inventory.objects.filter(
                is_deleted=False,
                quantity__lte=models.F('reorder_point')
            ).count()
        }

    def _get_recent_movements_data(self) -> Dict[str, Any]:
        """Get recent stock movements data for widget."""
        movements = StockMovement.objects.filter(
            is_deleted=False
        ).select_related('product', 'warehouse').order_by('-created_at')[:10]
        
        return {
            'movements': [
                {
                    'product': movement.product.name,
                    'warehouse': movement.warehouse.name,
                    'type': movement.get_movement_type_display(),
                    'quantity': movement.quantity,
                    'date': movement.created_at.strftime('%Y-%m-%d %H:%M')
                }
                for movement in movements
            ]
        }

    def _get_low_stock_alerts_data(self) -> Dict[str, Any]:
        """Get low stock alerts data for widget."""
        low_stock_items = Inventory.objects.filter(
            is_deleted=False,
            quantity__lte=models.F('reorder_point')
        ).select_related('product', 'warehouse')[:10]
        
        return {
            'alerts': [
                {
                    'product': item.product.name,
                    'warehouse': item.warehouse.name,
                    'current_stock': item.quantity,
                    'reorder_point': item.reorder_point
                }
                for item in low_stock_items
            ]
        }

    def _get_pending_orders_data(self) -> Dict[str, Any]:
        """Get pending orders data for widget."""
        pending_orders = PurchaseOrder.objects.filter(
            status__in=['draft', 'pending', 'approved'],
            is_deleted=False
        ).select_related('supplier', 'warehouse').order_by('-created_at')[:10]
        
        return {
            'orders': [
                {
                    'order_number': order.order_number,
                    'supplier': order.supplier.name,
                    'warehouse': order.warehouse.name,
                    'status': order.get_status_display(),
                    'total_amount': float(order.total_amount),
                    'order_date': order.order_date.strftime('%Y-%m-%d')
                }
                for order in pending_orders
            ]
        }
