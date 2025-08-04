"""
Enhanced ViewSets for the Inventory Management System API.
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum, Count, Q, F
from django.utils import timezone
from django.http import HttpResponse
from django.db import transaction
from datetime import timedelta
import csv
import json
import logging
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample

from .serializers_v2 import (
    CategorySerializer, ProductSerializer, WarehouseSerializer, InventorySerializer,
    StockMovementSerializer, SupplierSerializer, PurchaseOrderSerializer,
    PurchaseOrderItemSerializer, StockAlertSerializer, AlertRuleSerializer,
    AlertNotificationSerializer, ReportSerializer, DashboardWidgetSerializer,
    DashboardSummarySerializer, BulkInventoryUpdateSerializer, ExportSerializer
)
from inventory_system.apps.products.models import Category, Product
from inventory_system.apps.inventory.models import Warehouse, Inventory, StockMovement
from inventory_system.apps.orders.models import Supplier, PurchaseOrder, PurchaseOrderItem
from inventory_system.apps.alerts.models import StockAlert, AlertRule, AlertNotification
from inventory_system.apps.reports.models import Report, DashboardWidget

logger = logging.getLogger(__name__)


@extend_schema(tags=['products'])
class CategoryViewSet(viewsets.ModelViewSet):
    """Enhanced ViewSet for Category model."""
    queryset = Category.objects.filter(is_deleted=False)
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at', 'product_count', 'total_value']
    ordering = ['name']

    @extend_schema(
        summary="Get products in category",
        description="Retrieve all products belonging to a specific category"
    )
    @action(detail=True, methods=['get'])
    def products(self, request, pk=None):
        """Get products in a category."""
        category = self.get_object()
        products = Product.objects.filter(category=category, is_deleted=False)
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="Export category data",
        description="Export category data in various formats"
    )
    @action(detail=False, methods=['post'])
    def export(self, request):
        """Export category data."""
        serializer = ExportSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        format_type = serializer.validated_data['format']
        categories = self.filter_queryset(self.get_queryset())
        
        if format_type == 'csv':
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="categories.csv"'
            
            writer = csv.writer(response)
            writer.writerow(['ID', 'Name', 'Description', 'Product Count', 'Total Value', 'Created At'])
            
            for category in categories:
                writer.writerow([
                    category.id, category.name, category.description,
                    category.products.filter(is_deleted=False).count(),
                    category.get_total_value(), category.created_at
                ])
            
            return response
        
        elif format_type == 'json':
            data = CategorySerializer(categories, many=True).data
            return Response(data)
        
        return Response({'error': 'Unsupported format'}, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(tags=['products'])
class ProductViewSet(viewsets.ModelViewSet):
    """Enhanced ViewSet for Product model."""
    queryset = Product.objects.filter(is_deleted=False).select_related('category')
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'unit_price']
    search_fields = ['name', 'sku', 'description']
    ordering_fields = ['name', 'sku', 'unit_price', 'created_at']
    ordering = ['name']
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    @extend_schema(
        summary="Get product inventory",
        description="Retrieve inventory information for a specific product across all warehouses"
    )
    @action(detail=True, methods=['get'])
    def inventory(self, request, pk=None):
        """Get inventory for a product."""
        product = self.get_object()
        inventory = Inventory.objects.filter(product=product, is_deleted=False).select_related('warehouse')
        serializer = InventorySerializer(inventory, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="Get product movements",
        description="Retrieve stock movement history for a specific product"
    )
    @action(detail=True, methods=['get'])
    def movements(self, request, pk=None):
        """Get stock movements for a product."""
        product = self.get_object()
        movements = StockMovement.objects.filter(
            product=product, is_deleted=False
        ).select_related('warehouse').order_by('-created_at')[:50]
        serializer = StockMovementSerializer(movements, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="Bulk update products",
        description="Update multiple products at once"
    )
    @action(detail=False, methods=['post'])
    def bulk_update(self, request):
        """Bulk update products."""
        updates = request.data.get('updates', [])
        updated_count = 0
        
        with transaction.atomic():
            for update in updates:
                product_id = update.get('id')
                if product_id:
                    try:
                        product = Product.objects.get(id=product_id, is_deleted=False)
                        serializer = ProductSerializer(product, data=update, partial=True)
                        if serializer.is_valid():
                            serializer.save()
                            updated_count += 1
                    except Product.DoesNotExist:
                        continue
        
        return Response({
            'message': f'Successfully updated {updated_count} products',
            'updated_count': updated_count
        })

    @extend_schema(
        summary="Export products",
        description="Export product data in various formats"
    )
    @action(detail=False, methods=['post'])
    def export(self, request):
        """Export product data."""
        serializer = ExportSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        format_type = serializer.validated_data['format']
        products = self.filter_queryset(self.get_queryset())
        
        if format_type == 'csv':
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="products.csv"'
            
            writer = csv.writer(response)
            writer.writerow(['ID', 'Name', 'SKU', 'Category', 'Unit Price', 'Stock Status', 'Created At'])
            
            for product in products:
                writer.writerow([
                    product.id, product.name, product.sku, product.category.name,
                    product.unit_price, product.get_stock_status(), product.created_at
                ])
            
            return response
        
        elif format_type == 'json':
            data = ProductSerializer(products, many=True).data
            return Response(data)
        
        return Response({'error': 'Unsupported format'}, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(tags=['inventory'])
class WarehouseViewSet(viewsets.ModelViewSet):
    """Enhanced ViewSet for Warehouse model."""
    queryset = Warehouse.objects.filter(is_deleted=False)
    serializer_class = WarehouseSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active']
    search_fields = ['name', 'manager', 'address']
    ordering_fields = ['name', 'capacity', 'created_at']
    ordering = ['name']

    @extend_schema(
        summary="Get warehouse inventory",
        description="Retrieve all inventory items in a specific warehouse"
    )
    @action(detail=True, methods=['get'])
    def inventory(self, request, pk=None):
        """Get inventory for a warehouse."""
        warehouse = self.get_object()
        inventory = warehouse.inventory_items.filter(is_deleted=False).select_related('product', 'product__category')
        serializer = InventorySerializer(inventory, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="Get warehouse movements",
        description="Retrieve stock movement history for a specific warehouse"
    )
    @action(detail=True, methods=['get'])
    def movements(self, request, pk=None):
        """Get stock movements for a warehouse."""
        warehouse = self.get_object()
        movements = warehouse.stock_movements.filter(
            is_deleted=False
        ).select_related('product').order_by('-created_at')[:50]
        serializer = StockMovementSerializer(movements, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="Get warehouse summary",
        description="Get comprehensive summary of warehouse operations"
    )
    @action(detail=True, methods=['get'])
    def summary(self, request, pk=None):
        """Get warehouse summary."""
        warehouse = self.get_object()
        
        # Get inventory statistics
        inventory_stats = warehouse.inventory_items.filter(is_deleted=False).aggregate(
            total_items=Count('id'),
            total_quantity=Sum('quantity'),
            total_value=Sum(F('quantity') * F('product__unit_price')),
            low_stock_items=Count('id', filter=Q(quantity__lte=F('reorder_point'))),
            out_of_stock_items=Count('id', filter=Q(quantity=0))
        )
        
        # Get recent movements
        recent_movements = warehouse.stock_movements.filter(
            is_deleted=False
        ).select_related('product').order_by('-created_at')[:10]
        
        data = {
            'warehouse': WarehouseSerializer(warehouse).data,
            'inventory_stats': inventory_stats,
            'recent_movements': StockMovementSerializer(recent_movements, many=True).data,
            'utilization': warehouse.current_utilization,
            'available_capacity': warehouse.available_capacity
        }
        
        return Response(data)


@extend_schema(tags=['inventory'])
class InventoryViewSet(viewsets.ModelViewSet):
    """Enhanced ViewSet for Inventory model."""
    queryset = Inventory.objects.filter(is_deleted=False).select_related('product', 'warehouse', 'product__category')
    serializer_class = InventorySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['warehouse', 'product__category']
    search_fields = ['product__name', 'product__sku', 'warehouse__name']
    ordering_fields = ['quantity', 'last_updated', 'created_at']
    ordering = ['-last_updated']

    @extend_schema(
        summary="Get low stock items",
        description="Retrieve inventory items that are below reorder point"
    )
    @action(detail=False, methods=['get'])
    def low_stock(self, request):
        """Get low stock items."""
        low_stock = self.queryset.filter(quantity__lte=F('reorder_point'))
        serializer = self.get_serializer(low_stock, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="Get out of stock items",
        description="Retrieve inventory items that are completely out of stock"
    )
    @action(detail=False, methods=['get'])
    def out_of_stock(self, request):
        """Get out of stock items."""
        out_of_stock = self.queryset.filter(quantity=0)
        serializer = self.get_serializer(out_of_stock, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="Adjust inventory quantity",
        description="Adjust the quantity of an inventory item and create movement record"
    )
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

    @extend_schema(
        summary="Bulk update inventory",
        description="Update multiple inventory items at once"
    )
    @action(detail=False, methods=['post'])
    def bulk_update(self, request):
        """Bulk update inventory."""
        serializer = BulkInventoryUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        updates = serializer.validated_data['updates']
        updated_count = 0
        
        with transaction.atomic():
            for update in updates:
                inventory_id = update['inventory_id']
                quantity = update['quantity']
                
                try:
                    inventory = Inventory.objects.get(id=inventory_id, is_deleted=False)
                    old_quantity = inventory.quantity
                    inventory.quantity = quantity
                    inventory.save()
                    
                    # Create movement record
                    movement_type = update.get('movement_type', 'adjustment')
                    notes = update.get('notes', 'Bulk update')
                    
                    StockMovement.objects.create(
                        product=inventory.product,
                        warehouse=inventory.warehouse,
                        movement_type=movement_type,
                        quantity=quantity - old_quantity,
                        reference_type='bulk_update',
                        notes=notes
                    )
                    
                    updated_count += 1
                except Inventory.DoesNotExist:
                    continue
        
        return Response({
            'message': f'Successfully updated {updated_count} inventory items',
            'updated_count': updated_count
        })

    @extend_schema(
        summary="Transfer inventory",
        description="Transfer inventory between warehouses"
    )
    @action(detail=True, methods=['post'])
    def transfer(self, request, pk=None):
        """Transfer inventory to another warehouse."""
        inventory = self.get_object()
        target_warehouse_id = request.data.get('target_warehouse_id')
        quantity = request.data.get('quantity', 0)
        notes = request.data.get('notes', '')
        
        if not target_warehouse_id or quantity <= 0:
            return Response(
                {'error': 'Invalid transfer parameters'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            target_warehouse = Warehouse.objects.get(id=target_warehouse_id, is_deleted=False)
        except Warehouse.DoesNotExist:
            return Response(
                {'error': 'Target warehouse not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        if quantity > inventory.quantity:
            return Response(
                {'error': 'Insufficient quantity for transfer'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        with transaction.atomic():
            # Reduce quantity from source
            inventory.quantity -= quantity
            inventory.save()
            
            # Add quantity to target
            target_inventory, created = Inventory.objects.get_or_create(
                product=inventory.product,
                warehouse=target_warehouse,
                defaults={'quantity': quantity}
            )
            
            if not created:
                target_inventory.quantity += quantity
                target_inventory.save()
            
            # Create movement records
            StockMovement.objects.create(
                product=inventory.product,
                warehouse=inventory.warehouse,
                movement_type='out',
                quantity=quantity,
                reference_type='transfer',
                notes=f"Transfer to {target_warehouse.name}: {notes}"
            )
            
            StockMovement.objects.create(
                product=inventory.product,
                warehouse=target_warehouse,
                movement_type='in',
                quantity=quantity,
                reference_type='transfer',
                notes=f"Transfer from {inventory.warehouse.name}: {notes}"
            )
        
        return Response({
            'message': f'Successfully transferred {quantity} units to {target_warehouse.name}',
            'source_inventory': InventorySerializer(inventory).data,
            'target_inventory': InventorySerializer(target_inventory).data
        })


@extend_schema(tags=['inventory'])
class StockMovementViewSet(viewsets.ModelViewSet):
    """Enhanced ViewSet for StockMovement model."""
    queryset = StockMovement.objects.filter(is_deleted=False).select_related('product', 'warehouse')
    serializer_class = StockMovementSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['movement_type', 'warehouse', 'product__category']
    search_fields = ['product__name', 'product__sku', 'warehouse__name', 'notes']
    ordering_fields = ['quantity', 'created_at']
    ordering = ['-created_at']

    @extend_schema(
        summary="Create stock movement",
        description="Create a stock movement and update inventory accordingly"
    )
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

    @extend_schema(
        summary="Get movement summary",
        description="Get summary of stock movements by type and date range"
    )
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get movement summary."""
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        queryset = self.get_queryset()
        
        if start_date:
            queryset = queryset.filter(created_at__date__gte=start_date)
        if end_date:
            queryset = queryset.filter(created_at__date__lte=end_date)
        
        summary = queryset.values('movement_type').annotate(
            count=Count('id'),
            total_quantity=Sum('quantity'),
            total_value=Sum(F('quantity') * F('product__unit_price'))
        )
        
        return Response(summary)


@extend_schema(tags=['orders'])
class SupplierViewSet(viewsets.ModelViewSet):
    """Enhanced ViewSet for Supplier model."""
    queryset = Supplier.objects.filter(is_deleted=False)
    serializer_class = SupplierSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active']
    search_fields = ['name', 'contact_person', 'email', 'phone']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']

    @extend_schema(
        summary="Get supplier orders",
        description="Retrieve all purchase orders from a specific supplier"
    )
    @action(detail=True, methods=['get'])
    def orders(self, request, pk=None):
        """Get orders from a supplier."""
        supplier = self.get_object()
        orders = PurchaseOrder.objects.filter(
            supplier=supplier, is_deleted=False
        ).select_related('warehouse').order_by('-created_at')
        serializer = PurchaseOrderSerializer(orders, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="Get supplier performance",
        description="Get performance metrics for a supplier"
    )
    @action(detail=True, methods=['get'])
    def performance(self, request, pk=None):
        """Get supplier performance metrics."""
        supplier = self.get_object()
        
        # Get order statistics
        orders = supplier.purchase_orders.filter(is_deleted=False)
        
        performance_data = {
            'total_orders': orders.count(),
            'total_value': float(orders.aggregate(total=Sum('total_amount'))['total'] or 0),
            'average_order_value': float(orders.aggregate(avg=Sum('total_amount'))['avg'] or 0) / max(orders.count(), 1),
            'on_time_deliveries': orders.filter(status='received').count(),
            'pending_orders': orders.filter(status__in=['draft', 'pending', 'approved']).count(),
            'last_order_date': orders.order_by('-order_date').first().order_date if orders.exists() else None
        }
        
        return Response(performance_data)


@extend_schema(tags=['orders'])
class PurchaseOrderViewSet(viewsets.ModelViewSet):
    """Enhanced ViewSet for PurchaseOrder model."""
    queryset = PurchaseOrder.objects.filter(is_deleted=False).select_related('supplier', 'warehouse')
    serializer_class = PurchaseOrderSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'supplier', 'warehouse']
    search_fields = ['order_number', 'supplier__name', 'warehouse__name', 'notes']
    ordering_fields = ['order_date', 'expected_date', 'total_amount', 'created_at']
    ordering = ['-created_at']

    @extend_schema(
        summary="Approve purchase order",
        description="Approve a purchase order and update its status"
    )
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve purchase order."""
        order = self.get_object()
        
        if order.approve(request.user):
            serializer = self.get_serializer(order)
            return Response(serializer.data)
        else:
            return Response(
                {'error': 'Order cannot be approved'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

    @extend_schema(
        summary="Mark order as ordered",
        description="Mark a purchase order as ordered with supplier"
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
                {'error': 'Order cannot be marked as ordered'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

    @extend_schema(
        summary="Receive order",
        description="Mark a purchase order as received and update inventory"
    )
    @action(detail=True, methods=['post'])
    def receive(self, request, pk=None):
        """Receive order and update inventory."""
        order = self.get_object()
        received_date = request.data.get('received_date')
        
        with transaction.atomic():
            if order.receive_order(received_date):
                # Update inventory for each item
                for item in order.items.filter(is_deleted=False):
                    if item.quantity_received > 0:
                        inventory, created = Inventory.objects.get_or_create(
                            product=item.product,
                            warehouse=order.warehouse,
                            defaults={'quantity': 0}
                        )
                        
                        inventory.quantity += item.quantity_received
                        inventory.save()
                        
                        # Create movement record
                        StockMovement.objects.create(
                            product=item.product,
                            warehouse=order.warehouse,
                            movement_type='in',
                            quantity=item.quantity_received,
                            reference_type='purchase_order',
                            reference_id=order.id,
                            notes=f"Received from PO {order.order_number}"
                        )
                
                serializer = self.get_serializer(order)
                return Response(serializer.data)
            else:
                return Response(
                    {'error': 'Order cannot be received'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

    @extend_schema(
        summary="Cancel order",
        description="Cancel a purchase order"
    )
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel order."""
        order = self.get_object()
        
        if order.cancel_order():
            serializer = self.get_serializer(order)
            return Response(serializer.data)
        else:
            return Response(
                {'error': 'Order cannot be cancelled'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

    @extend_schema(
        summary="Get pending orders",
        description="Retrieve all pending purchase orders"
    )
    @action(detail=False, methods=['get'])
    def pending(self, request):
        """Get pending orders."""
        pending_orders = self.queryset.filter(
            status__in=['draft', 'pending', 'approved']
        ).order_by('-created_at')
        serializer = self.get_serializer(pending_orders, many=True)
        return Response(serializer.data)


@extend_schema(tags=['orders'])
class PurchaseOrderItemViewSet(viewsets.ModelViewSet):
    """Enhanced ViewSet for PurchaseOrderItem model."""
    queryset = PurchaseOrderItem.objects.filter(is_deleted=False).select_related('purchase_order', 'product')
    serializer_class = PurchaseOrderItemSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['purchase_order__status', 'product__category']
    search_fields = ['product__name', 'product__sku', 'purchase_order__order_number']
    ordering_fields = ['quantity_ordered', 'quantity_received', 'created_at']
    ordering = ['-created_at']

    @extend_schema(
        summary="Receive item quantity",
        description="Receive a specific quantity for a purchase order item"
    )
    @action(detail=True, methods=['post'])
    def receive_quantity(self, request, pk=None):
        """Receive quantity for an item."""
        item = self.get_object()
        quantity = request.data.get('quantity', 0)
        
        if quantity <= 0:
            return Response(
                {'error': 'Quantity must be greater than zero'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if item.quantity_received + quantity > item.quantity_ordered:
            return Response(
                {'error': 'Cannot receive more than ordered quantity'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        with transaction.atomic():
            item.quantity_received += quantity
            item.save()
            
            # Update inventory
            inventory, created = Inventory.objects.get_or_create(
                product=item.product,
                warehouse=item.purchase_order.warehouse,
                defaults={'quantity': 0}
            )
            
            inventory.quantity += quantity
            inventory.save()
            
            # Create movement record
            StockMovement.objects.create(
                product=item.product,
                warehouse=item.purchase_order.warehouse,
                movement_type='in',
                quantity=quantity,
                reference_type='purchase_order_item',
                reference_id=item.id,
                notes=f"Received {quantity} units for PO {item.purchase_order.order_number}"
            )
        
        serializer = self.get_serializer(item)
        return Response(serializer.data)


@extend_schema(tags=['alerts'])
class StockAlertViewSet(viewsets.ModelViewSet):
    """Enhanced ViewSet for StockAlert model."""
    queryset = StockAlert.objects.filter(is_deleted=False).select_related('product', 'warehouse')
    serializer_class = StockAlertSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['alert_type', 'severity', 'is_resolved', 'warehouse']
    search_fields = ['product__name', 'product__sku', 'warehouse__name', 'message']
    ordering_fields = ['severity', 'created_at', 'resolved_at']
    ordering = ['-created_at']

    @extend_schema(
        summary="Resolve alert",
        description="Resolve a stock alert"
    )
    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        """Resolve alert."""
        alert = self.get_object()
        resolution_notes = request.data.get('resolution_notes', '')
        
        if alert.resolve(request.user, resolution_notes):
            serializer = self.get_serializer(alert)
            return Response(serializer.data)
        else:
            return Response(
                {'error': 'Alert cannot be resolved'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

    @extend_schema(
        summary="Reactivate alert",
        description="Reactivate a resolved alert"
    )
    @action(detail=True, methods=['post'])
    def reactivate(self, request, pk=None):
        """Reactivate alert."""
        alert = self.get_object()
        
        if alert.reactivate():
            serializer = self.get_serializer(alert)
            return Response(serializer.data)
        else:
            return Response(
                {'error': 'Alert cannot be reactivated'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

    @extend_schema(
        summary="Get active alerts",
        description="Retrieve all active (unresolved) alerts"
    )
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get active alerts."""
        active_alerts = self.queryset.filter(is_resolved=False)
        serializer = self.get_serializer(active_alerts, many=True)
        return Response(serializer.data)


@extend_schema(tags=['alerts'])
class AlertRuleViewSet(viewsets.ModelViewSet):
    """Enhanced ViewSet for AlertRule model."""
    queryset = AlertRule.objects.filter(is_deleted=False).select_related('product', 'category', 'warehouse')
    serializer_class = AlertRuleSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['rule_type', 'severity', 'is_active']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']

    @extend_schema(
        summary="Test alert rule",
        description="Test an alert rule to see what alerts it would generate"
    )
    @action(detail=True, methods=['post'])
    def test(self, request, pk=None):
        """Test alert rule."""
        rule = self.get_object()
        
        from inventory_system.apps.alerts.services import AlertNotificationService
        created_alerts = AlertNotificationService.check_and_create_alerts()
        
        return Response({
            'message': f'Rule test completed. Created {len(created_alerts)} alerts.',
            'created_alerts': StockAlertSerializer(created_alerts, many=True).data
        })


@extend_schema(tags=['alerts'])
class AlertNotificationViewSet(viewsets.ModelViewSet):
    """Enhanced ViewSet for AlertNotification model."""
    queryset = AlertNotification.objects.filter(is_deleted=False).select_related('alert')
    serializer_class = AlertNotificationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['notification_type', 'status']
    search_fields = ['recipient', 'message']
    ordering_fields = ['status', 'sent_at', 'created_at']
    ordering = ['-created_at']


@extend_schema(tags=['reports'])
class ReportViewSet(viewsets.ModelViewSet):
    """Enhanced ViewSet for Report model."""
    queryset = Report.objects.filter(is_deleted=False).select_related('generated_by')
    serializer_class = ReportSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['report_type', 'format', 'is_scheduled']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['-created_at']

    @extend_schema(
        summary="Generate report",
        description="Generate a new report with specified parameters"
    )
    @action(detail=True, methods=['post'])
    def generate(self, request, pk=None):
        """Generate report."""
        report = self.get_object()
        parameters = request.data.get('parameters', {})
        
        # This would typically call a report generation service
        # For now, we'll just update the report
        report.parameters = parameters
        report.generated_by = request.user
        report.save()
        
        serializer = self.get_serializer(report)
        return Response(serializer.data)


@extend_schema(tags=['reports'])
class DashboardWidgetViewSet(viewsets.ModelViewSet):
    """Enhanced ViewSet for DashboardWidget model."""
    queryset = DashboardWidget.objects.filter(is_deleted=False)
    serializer_class = DashboardWidgetSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['widget_type', 'is_active']
    search_fields = ['name', 'title', 'description']
    ordering_fields = ['position', 'name', 'created_at']
    ordering = ['position', 'name']

    @extend_schema(
        summary="Get widget data",
        description="Get data for a specific dashboard widget"
    )
    @action(detail=True, methods=['get'])
    def data(self, request, pk=None):
        """Get widget data."""
        widget = self.get_object()
        
        # This would typically call a service to get widget-specific data
        # For now, we'll return a basic structure
        data = {
            'widget_id': widget.id,
            'widget_type': widget.widget_type,
            'title': widget.title,
            'data': {}  # Widget-specific data would go here
        }
        
        return Response(data)


@extend_schema(tags=['dashboard'])
class DashboardViewSet(viewsets.ViewSet):
    """Enhanced ViewSet for Dashboard data."""
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Get dashboard summary",
        description="Get comprehensive dashboard summary with all key metrics"
    )
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
        
        # Get top products by value
        top_products = Inventory.objects.filter(
            is_deleted=False
        ).values('product__name').annotate(
            total_value=Sum(F('quantity') * F('product__unit_price'))
        ).order_by('-total_value')[:5]
        
        # Get alert summary
        alert_summary = StockAlert.objects.filter(
            is_deleted=False
        ).values('alert_type').annotate(
            count=Count('id')
        )
        
        data = {
            'total_products': total_products,
            'total_inventory_value': total_inventory_value,
            'low_stock_items': low_stock_items,
            'out_of_stock_items': out_of_stock_items,
            'total_warehouses': total_warehouses,
            'active_alerts': active_alerts,
            'pending_orders': pending_orders,
            'recent_movements': StockMovementSerializer(recent_movements, many=True).data,
            'warehouse_utilization': warehouse_utilization,
            'top_products': list(top_products),
            'alert_summary': {item['alert_type']: item['count'] for item in alert_summary}
        }
        
        serializer = DashboardSummarySerializer(data)
        return Response(serializer.data)

    @extend_schema(
        summary="Get low stock items",
        description="Get items that are below reorder point"
    )
    @action(detail=False, methods=['get'])
    def low_stock(self, request):
        """Get low stock items for dashboard."""
        low_stock = Inventory.objects.filter(
            is_deleted=False,
            quantity__lte=F('reorder_point')
        ).select_related('product', 'warehouse')[:20]
        
        serializer = InventorySerializer(low_stock, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="Get recent movements",
        description="Get recent stock movements for dashboard"
    )
    @action(detail=False, methods=['get'])
    def recent_movements(self, request):
        """Get recent movements for dashboard."""
        recent_movements = StockMovement.objects.filter(
            is_deleted=False
        ).select_related('product', 'warehouse').order_by('-created_at')[:20]
        
        serializer = StockMovementSerializer(recent_movements, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="Get pending orders",
        description="Get pending purchase orders for dashboard"
    )
    @action(detail=False, methods=['get'])
    def pending_orders(self, request):
        """Get pending orders for dashboard."""
        pending_orders = PurchaseOrder.objects.filter(
            status__in=['draft', 'pending', 'approved'],
            is_deleted=False
        ).select_related('supplier', 'warehouse').order_by('-created_at')[:20]
        
        serializer = PurchaseOrderSerializer(pending_orders, many=True)
        return Response(serializer.data) 