"""
Views for Inventory Management System API.
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum, Count, Q, F
from django.utils import timezone
from datetime import timedelta

from .serializers import (
    # Products
    CategorySerializer, ProductSerializer,
    
    # Inventory
    WarehouseSerializer, InventorySerializer, StockMovementSerializer,
    
    # Orders
    SupplierSerializer, PurchaseOrderSerializer, PurchaseOrderItemSerializer,
    
    # Alerts
    StockAlertSerializer, AlertRuleSerializer, AlertNotificationSerializer,
    
    # Reports
    ReportSerializer, DashboardWidgetSerializer, DashboardSummarySerializer,
)

from inventory_system.apps.products.models import Category, Product
from inventory_system.apps.inventory.models import Warehouse, Inventory, StockMovement
from inventory_system.apps.orders.models import Supplier, PurchaseOrder, PurchaseOrderItem
from inventory_system.apps.alerts.models import StockAlert, AlertRule, AlertNotification
from inventory_system.apps.reports.models import Report, DashboardWidget


# Product Viewsets
class CategoryViewSet(viewsets.ModelViewSet):
    """ViewSet for Category model."""
    queryset = Category.objects.filter(is_deleted=False)
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']

    @action(detail=True, methods=['get'])
    def products(self, request, pk=None):
        """Get products in a category."""
        category = self.get_object()
        products = Product.objects.filter(category=category, is_deleted=False)
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)


class ProductViewSet(viewsets.ModelViewSet):
    """ViewSet for Product model."""
    queryset = Product.objects.filter(is_deleted=False).select_related('category')
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'unit_price']
    search_fields = ['name', 'sku', 'description']
    ordering_fields = ['name', 'sku', 'unit_price', 'created_at']
    ordering = ['name']

    @action(detail=True, methods=['get'])
    def inventory(self, request, pk=None):
        """Get inventory for a product."""
        product = self.get_object()
        inventory = Inventory.objects.filter(product=product, is_deleted=False).select_related('warehouse')
        serializer = InventorySerializer(inventory, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def movements(self, request, pk=None):
        """Get stock movements for a product."""
        product = self.get_object()
        movements = StockMovement.objects.filter(product=product, is_deleted=False).select_related('warehouse')
        serializer = StockMovementSerializer(movements, many=True)
        return Response(serializer.data)


# Inventory Viewsets
class WarehouseViewSet(viewsets.ModelViewSet):
    """ViewSet for Warehouse model."""
    queryset = Warehouse.objects.filter(is_deleted=False)
    serializer_class = WarehouseSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active']
    search_fields = ['name', 'manager', 'address']
    ordering_fields = ['name', 'capacity', 'created_at']
    ordering = ['name']

    @action(detail=True, methods=['get'])
    def inventory(self, request, pk=None):
        """Get inventory in a warehouse."""
        warehouse = self.get_object()
        inventory = Inventory.objects.filter(warehouse=warehouse, is_deleted=False).select_related('product')
        serializer = InventorySerializer(inventory, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def movements(self, request, pk=None):
        """Get stock movements in a warehouse."""
        warehouse = self.get_object()
        movements = StockMovement.objects.filter(warehouse=warehouse, is_deleted=False).select_related('product')
        serializer = StockMovementSerializer(movements, many=True)
        return Response(serializer.data)


class InventoryViewSet(viewsets.ModelViewSet):
    """ViewSet for Inventory model."""
    queryset = Inventory.objects.filter(is_deleted=False).select_related('product', 'warehouse', 'product__category')
    serializer_class = InventorySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['warehouse', 'product__category']
    search_fields = ['product__name', 'product__sku', 'warehouse__name']
    ordering_fields = ['quantity', 'last_updated', 'created_at']
    ordering = ['-last_updated']

    @action(detail=False, methods=['get'])
    def low_stock(self, request):
        """Get low stock items."""
        low_stock = self.queryset.filter(quantity__lte=F('reorder_point'))
        serializer = self.get_serializer(low_stock, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def out_of_stock(self, request):
        """Get out of stock items."""
        out_of_stock = self.queryset.filter(quantity=0)
        serializer = self.get_serializer(out_of_stock, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def adjust_quantity(self, request, pk=None):
        """Adjust inventory quantity."""
        inventory = self.get_object()
        amount = request.data.get('amount', 0)
        movement_type = request.data.get('movement_type', 'adjustment')
        notes = request.data.get('notes', '')
        
        if inventory.adjust_quantity(amount, movement_type, notes=notes):
            serializer = self.get_serializer(inventory)
            return Response(serializer.data)
        else:
            return Response(
                {'error': 'Invalid quantity adjustment'}, 
                status=status.HTTP_400_BAD_REQUEST
            )


class StockMovementViewSet(viewsets.ModelViewSet):
    """ViewSet for StockMovement model."""
    queryset = StockMovement.objects.filter(is_deleted=False).select_related('product', 'warehouse')
    serializer_class = StockMovementSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['movement_type', 'warehouse', 'product__category']
    search_fields = ['product__name', 'product__sku', 'warehouse__name', 'notes']
    ordering_fields = ['quantity', 'created_at']
    ordering = ['-created_at']

    def create(self, request, *args, **kwargs):
        """Create stock movement and update inventory."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Get inventory item
        product_id = serializer.validated_data['product'].id
        warehouse_id = serializer.validated_data['warehouse'].id
        
        try:
            inventory = Inventory.objects.get(
                product_id=product_id, 
                warehouse_id=warehouse_id,
                is_deleted=False
            )
        except Inventory.DoesNotExist:
            return Response(
                {'error': 'Inventory item not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Adjust inventory
        amount = serializer.validated_data['quantity']
        movement_type = serializer.validated_data['movement_type']
        notes = serializer.validated_data.get('notes', '')
        
        if inventory.adjust_quantity(amount, movement_type, notes=notes):
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(
                {'error': 'Invalid quantity adjustment'}, 
                status=status.HTTP_400_BAD_REQUEST
            )


# Order Viewsets
class SupplierViewSet(viewsets.ModelViewSet):
    """ViewSet for Supplier model."""
    queryset = Supplier.objects.filter(is_deleted=False)
    serializer_class = SupplierSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active']
    search_fields = ['name', 'contact_person', 'email', 'phone']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']

    @action(detail=True, methods=['get'])
    def orders(self, request, pk=None):
        """Get orders from a supplier."""
        supplier = self.get_object()
        orders = PurchaseOrder.objects.filter(supplier=supplier, is_deleted=False).select_related('warehouse')
        serializer = PurchaseOrderSerializer(orders, many=True)
        return Response(serializer.data)


class PurchaseOrderViewSet(viewsets.ModelViewSet):
    """ViewSet for PurchaseOrder model."""
    queryset = PurchaseOrder.objects.filter(is_deleted=False).select_related('supplier', 'warehouse')
    serializer_class = PurchaseOrderSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'supplier', 'warehouse']
    search_fields = ['order_number', 'supplier__name', 'warehouse__name', 'notes']
    ordering_fields = ['order_date', 'expected_date', 'total_amount', 'created_at']
    ordering = ['-created_at']

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve a purchase order."""
        order = self.get_object()
        if order.approve(request.user):
            serializer = self.get_serializer(order)
            return Response(serializer.data)
        else:
            return Response(
                {'error': 'Cannot approve this order'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'])
    def mark_ordered(self, request, pk=None):
        """Mark order as ordered."""
        order = self.get_object()
        if order.mark_as_ordered():
            serializer = self.get_serializer(order)
            return Response(serializer.data)
        else:
            return Response(
                {'error': 'Cannot mark as ordered'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'])
    def receive(self, request, pk=None):
        """Receive an order."""
        order = self.get_object()
        received_date = request.data.get('received_date')
        if order.receive_order(received_date):
            serializer = self.get_serializer(order)
            return Response(serializer.data)
        else:
            return Response(
                {'error': 'Cannot receive this order'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel an order."""
        order = self.get_object()
        if order.cancel_order():
            serializer = self.get_serializer(order)
            return Response(serializer.data)
        else:
            return Response(
                {'error': 'Cannot cancel this order'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['get'])
    def pending(self, request):
        """Get pending orders."""
        pending_orders = self.queryset.filter(status__in=['draft', 'pending', 'approved'])
        serializer = self.get_serializer(pending_orders, many=True)
        return Response(serializer.data)


class PurchaseOrderItemViewSet(viewsets.ModelViewSet):
    """ViewSet for PurchaseOrderItem model."""
    queryset = PurchaseOrderItem.objects.filter(is_deleted=False).select_related('purchase_order', 'product')
    serializer_class = PurchaseOrderItemSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['purchase_order__status', 'product__category']
    search_fields = ['product__name', 'product__sku', 'purchase_order__order_number']
    ordering_fields = ['quantity_ordered', 'quantity_received', 'created_at']
    ordering = ['-created_at']

    @action(detail=True, methods=['post'])
    def receive_quantity(self, request, pk=None):
        """Receive quantity for an item."""
        item = self.get_object()
        quantity = request.data.get('quantity', 0)
        
        if item.receive_quantity(quantity):
            serializer = self.get_serializer(item)
            return Response(serializer.data)
        else:
            return Response(
                {'error': 'Invalid quantity'}, 
                status=status.HTTP_400_BAD_REQUEST
            )


# Alert Viewsets
class StockAlertViewSet(viewsets.ModelViewSet):
    """ViewSet for StockAlert model."""
    queryset = StockAlert.objects.filter(is_deleted=False).select_related('product', 'warehouse')
    serializer_class = StockAlertSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['alert_type', 'severity', 'is_resolved', 'warehouse']
    search_fields = ['product__name', 'product__sku', 'warehouse__name', 'message']
    ordering_fields = ['severity', 'created_at', 'resolved_at']
    ordering = ['-created_at']

    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        """Resolve an alert."""
        alert = self.get_object()
        notes = request.data.get('notes', '')
        
        if alert.resolve(request.user, notes):
            serializer = self.get_serializer(alert)
            return Response(serializer.data)
        else:
            return Response(
                {'error': 'Cannot resolve this alert'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'])
    def reactivate(self, request, pk=None):
        """Reactivate an alert."""
        alert = self.get_object()
        if alert.reactivate():
            serializer = self.get_serializer(alert)
            return Response(serializer.data)
        else:
            return Response(
                {'error': 'Cannot reactivate this alert'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get active alerts."""
        active_alerts = self.queryset.filter(is_resolved=False)
        serializer = self.get_serializer(active_alerts, many=True)
        return Response(serializer.data)


class AlertRuleViewSet(viewsets.ModelViewSet):
    """ViewSet for AlertRule model."""
    queryset = AlertRule.objects.filter(is_deleted=False).select_related('product', 'category', 'warehouse')
    serializer_class = AlertRuleSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['rule_type', 'severity', 'is_active']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']

    @action(detail=True, methods=['post'])
    def test(self, request, pk=None):
        """Test an alert rule."""
        rule = self.get_object()
        from inventory_system.apps.inventory.models import Inventory
        
        count = 0
        inventory_items = Inventory.objects.filter(is_deleted=False)
        
        if rule.product:
            inventory_items = inventory_items.filter(product=rule.product)
        if rule.category:
            inventory_items = inventory_items.filter(product__category=rule.category)
        if rule.warehouse:
            inventory_items = inventory_items.filter(warehouse=rule.warehouse)
        
        for inventory in inventory_items:
            if rule.check_condition(inventory):
                alert = rule.create_alert(inventory)
                if alert:
                    count += 1
        
        return Response({'alerts_created': count})


class AlertNotificationViewSet(viewsets.ModelViewSet):
    """ViewSet for AlertNotification model."""
    queryset = AlertNotification.objects.filter(is_deleted=False).select_related('alert')
    serializer_class = AlertNotificationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['notification_type', 'status']
    search_fields = ['recipient', 'message']
    ordering_fields = ['status', 'sent_at', 'created_at']
    ordering = ['-created_at']


# Report Viewsets
class ReportViewSet(viewsets.ModelViewSet):
    """ViewSet for Report model."""
    queryset = Report.objects.filter(is_deleted=False).select_related('generated_by')
    serializer_class = ReportSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['report_type', 'format', 'is_scheduled']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['-created_at']

    @action(detail=True, methods=['post'])
    def generate(self, request, pk=None):
        """Generate a report."""
        report = self.get_object()
        try:
            report.data = report.generate_data()
            report.generated_by = request.user
            report.save(update_fields=['data', 'generated_by'])
            serializer = self.get_serializer(report)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class DashboardWidgetViewSet(viewsets.ModelViewSet):
    """ViewSet for DashboardWidget model."""
    queryset = DashboardWidget.objects.filter(is_deleted=False)
    serializer_class = DashboardWidgetSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['widget_type', 'is_active']
    search_fields = ['name', 'title', 'description']
    ordering_fields = ['position', 'name', 'created_at']
    ordering = ['position', 'name']

    @action(detail=True, methods=['get'])
    def data(self, request, pk=None):
        """Get widget data."""
        widget = self.get_object()
        try:
            data = widget.get_data()
            return Response(data)
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# Dashboard ViewSet
class DashboardViewSet(viewsets.ViewSet):
    """ViewSet for Dashboard data."""
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get dashboard summary."""
        # Get basic counts
        total_products = Product.objects.filter(is_deleted=False).count()
        total_warehouses = Warehouse.objects.filter(is_active=True, is_deleted=False).count()
        active_alerts = StockAlert.objects.filter(is_resolved=False, is_deleted=False).count()
        pending_orders = PurchaseOrder.objects.filter(
            status__in=['draft', 'pending', 'approved'],
            is_deleted=False
        ).count()
        
        # Get inventory value
        total_inventory_value = Inventory.objects.filter(
            is_deleted=False
        ).aggregate(
            total=Sum(F('quantity') * F('product__unit_price'))
        )['total'] or 0
        
        # Get low stock and out of stock counts
        low_stock_items = Inventory.objects.filter(
            is_deleted=False,
            quantity__lte=F('reorder_point')
        ).count()
        
        out_of_stock_items = Inventory.objects.filter(
            is_deleted=False,
            quantity=0
        ).count()
        
        # Get recent movements
        recent_movements = StockMovement.objects.filter(
            is_deleted=False
        ).select_related('product', 'warehouse').order_by('-created_at')[:10]
        
        # Get warehouse utilization
        warehouses = Warehouse.objects.filter(is_active=True, is_deleted=False)
        warehouse_utilization = []
        for warehouse in warehouses:
            warehouse_utilization.append({
                'name': warehouse.name,
                'utilization': warehouse.current_utilization,
                'capacity': warehouse.capacity,
                'current_stock': warehouse.inventory_items.filter(is_deleted=False).aggregate(
                    total=Sum('quantity')
                )['total'] or 0
            })
        
        data = {
            'total_products': total_products,
            'total_inventory_value': total_inventory_value,
            'low_stock_items': low_stock_items,
            'out_of_stock_items': out_of_stock_items,
            'total_warehouses': total_warehouses,
            'active_alerts': active_alerts,
            'pending_orders': pending_orders,
            'recent_movements': StockMovementSerializer(recent_movements, many=True).data,
            'warehouse_utilization': warehouse_utilization
        }
        
        serializer = DashboardSummarySerializer(data)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def low_stock(self, request):
        """Get low stock items for dashboard."""
        low_stock = Inventory.objects.filter(
            is_deleted=False,
            quantity__lte=F('reorder_point')
        ).select_related('product', 'warehouse')[:20]
        
        serializer = InventorySerializer(low_stock, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def recent_movements(self, request):
        """Get recent stock movements for dashboard."""
        movements = StockMovement.objects.filter(
            is_deleted=False
        ).select_related('product', 'warehouse').order_by('-created_at')[:20]
        
        serializer = StockMovementSerializer(movements, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def pending_orders(self, request):
        """Get pending orders for dashboard."""
        orders = PurchaseOrder.objects.filter(
            status__in=['draft', 'pending', 'approved'],
            is_deleted=False
        ).select_related('supplier', 'warehouse').order_by('-created_at')[:20]
        
        serializer = PurchaseOrderSerializer(orders, many=True)
        return Response(serializer.data) 