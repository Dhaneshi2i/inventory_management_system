"""
Purchase Order Service for core business logic.
"""
from django.db import transaction
from django.db.models import Sum, F, Q, Avg, Count
from django.utils import timezone
from typing import List, Dict, Optional, Tuple
import logging

from inventory_system.apps.orders.models import PurchaseOrder, PurchaseOrderItem, Supplier
from inventory_system.apps.inventory.models import Inventory, StockMovement
from inventory_system.apps.products.models import Product
from inventory_system.apps.inventory.services import InventoryService

logger = logging.getLogger(__name__)


class PurchaseOrderService:
    """Service for purchase order management operations."""
    
    @staticmethod
    def create_purchase_order(
        supplier: Supplier,
        warehouse: 'Warehouse',
        items: List[Dict],
        order_date: Optional[timezone.date] = None,
        expected_date: Optional[timezone.date] = None,
        notes: str = ""
    ) -> Tuple[bool, str, Optional[PurchaseOrder]]:
        """Create a new purchase order with items."""
        try:
            with transaction.atomic():
                # Create purchase order
                order = PurchaseOrder.objects.create(
                    supplier=supplier,
                    warehouse=warehouse,
                    order_date=order_date or timezone.now().date(),
                    expected_date=expected_date,
                    notes=notes
                )
                
                # Create order items
                total_amount = 0
                for item_data in items:
                    product_id = item_data.get('product_id')
                    quantity = item_data.get('quantity', 0)
                    unit_price = item_data.get('unit_price', 0)
                    item_notes = item_data.get('notes', '')
                    
                    if not product_id or quantity <= 0 or unit_price <= 0:
                        continue
                    
                    try:
                        product = Product.objects.get(id=product_id, is_deleted=False)
                    except Product.DoesNotExist:
                        continue
                    
                    total_price = quantity * unit_price
                    total_amount += total_price
                    
                    PurchaseOrderItem.objects.create(
                        purchase_order=order,
                        product=product,
                        quantity_ordered=quantity,
                        unit_price=unit_price,
                        total_price=total_price,
                        notes=item_notes
                    )
                
                # Update order total
                order.total_amount = total_amount
                order.save()
                
                logger.info(
                    f"Purchase order created: {order.order_number} "
                    f"Supplier: {supplier.name}, Total: ${total_amount}"
                )
                
                return True, f"Purchase order created successfully: {order.order_number}", order
                
        except Exception as e:
            logger.error(f"Error creating purchase order: {e}")
            return False, f"Error creating purchase order: {str(e)}", None
    
    @staticmethod
    def approve_purchase_order(order: PurchaseOrder, user) -> Tuple[bool, str]:
        """Approve a purchase order."""
        try:
            if order.status not in ['draft', 'pending']:
                return False, "Order cannot be approved in current status"
            
            order.status = 'approved'
            order.approved_by = user
            order.approved_at = timezone.now()
            order.save()
            
            logger.info(f"Purchase order approved: {order.order_number} by {user.username}")
            
            return True, f"Purchase order {order.order_number} approved successfully"
            
        except Exception as e:
            logger.error(f"Error approving purchase order: {e}")
            return False, f"Error approving purchase order: {str(e)}"
    
    @staticmethod
    def mark_as_ordered(order: PurchaseOrder) -> Tuple[bool, str]:
        """Mark purchase order as ordered with supplier."""
        try:
            if order.status != 'approved':
                return False, "Order must be approved before marking as ordered"
            
            order.status = 'ordered'
            order.save()
            
            logger.info(f"Purchase order marked as ordered: {order.order_number}")
            
            return True, f"Purchase order {order.order_number} marked as ordered"
            
        except Exception as e:
            logger.error(f"Error marking order as ordered: {e}")
            return False, f"Error marking order as ordered: {str(e)}"
    
    @staticmethod
    def receive_purchase_order(
        order: PurchaseOrder,
        received_items: List[Dict],
        received_date: Optional[timezone.date] = None
    ) -> Tuple[bool, str]:
        """Receive items from a purchase order and update inventory."""
        try:
            with transaction.atomic():
                if order.status not in ['ordered', 'approved']:
                    return False, "Order cannot be received in current status"
                
                # Update received quantities
                for item_data in received_items:
                    item_id = item_data.get('item_id')
                    quantity_received = item_data.get('quantity_received', 0)
                    
                    if not item_id or quantity_received <= 0:
                        continue
                    
                    try:
                        item = PurchaseOrderItem.objects.get(
                            id=item_id,
                            purchase_order=order,
                            is_deleted=False
                        )
                    except PurchaseOrderItem.DoesNotExist:
                        continue
                    
                    # Update received quantity
                    item.quantity_received += quantity_received
                    item.save()
                    
                    # Update inventory
                    success, message = InventoryService.adjust_stock(
                        product=item.product,
                        warehouse=order.warehouse,
                        quantity=quantity_received,
                        movement_type='in',
                        reference_type='purchase_order',
                        reference_id=order.id,
                        notes=f"Received from PO {order.order_number}"
                    )
                    
                    if not success:
                        logger.warning(f"Failed to update inventory for item {item.id}: {message}")
                
                # Check if all items are received
                all_received = all(
                    item.quantity_received >= item.quantity_ordered
                    for item in order.items.filter(is_deleted=False)
                )
                
                if all_received:
                    order.status = 'received'
                    order.received_date = received_date or timezone.now().date()
                    order.save()
                    
                    logger.info(f"Purchase order fully received: {order.order_number}")
                    return True, f"Purchase order {order.order_number} fully received"
                else:
                    logger.info(f"Purchase order partially received: {order.order_number}")
                    return True, f"Purchase order {order.order_number} partially received"
                
        except Exception as e:
            logger.error(f"Error receiving purchase order: {e}")
            return False, f"Error receiving purchase order: {str(e)}"
    
    @staticmethod
    def cancel_purchase_order(order: PurchaseOrder) -> Tuple[bool, str]:
        """Cancel a purchase order."""
        try:
            if order.status in ['received', 'cancelled']:
                return False, "Order cannot be cancelled in current status"
            
            order.status = 'cancelled'
            order.save()
            
            logger.info(f"Purchase order cancelled: {order.order_number}")
            
            return True, f"Purchase order {order.order_number} cancelled successfully"
            
        except Exception as e:
            logger.error(f"Error cancelling purchase order: {e}")
            return False, f"Error cancelling purchase order: {str(e)}"
    
    @staticmethod
    def get_supplier_performance(supplier: Supplier, days: int = 30) -> Dict:
        """Get supplier performance metrics."""
        start_date = timezone.now().date() - timezone.timedelta(days=days)
        
        orders = supplier.purchase_orders.filter(
            order_date__gte=start_date,
            is_deleted=False
        )
        
        total_orders = orders.count()
        total_value = orders.aggregate(total=Sum('total_amount'))['total'] or 0
        average_order_value = orders.aggregate(avg=Avg('total_amount'))['avg'] or 0
        
        # Calculate on-time deliveries
        on_time_deliveries = 0
        late_deliveries = 0
        
        for order in orders.filter(status='received'):
            if order.received_date and order.expected_date:
                if order.received_date <= order.expected_date:
                    on_time_deliveries += 1
                else:
                    late_deliveries += 1
        
        total_deliveries = on_time_deliveries + late_deliveries
        on_time_percentage = (on_time_deliveries / total_deliveries * 100) if total_deliveries > 0 else 0
        
        # Get recent orders
        recent_orders = orders.order_by('-order_date')[:5]
        
        return {
            'supplier_id': supplier.id,
            'supplier_name': supplier.name,
            'period_days': days,
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
        }
    
    @staticmethod
    def get_pending_orders(warehouse: Optional['Warehouse'] = None) -> List[Dict]:
        """Get pending purchase orders."""
        query = PurchaseOrder.objects.filter(
            status__in=['draft', 'pending', 'approved'],
            is_deleted=False
        ).select_related('supplier', 'warehouse')
        
        if warehouse:
            query = query.filter(warehouse=warehouse)
        
        pending_orders = []
        
        for order in query.order_by('-created_at'):
            # Calculate completion percentage
            total_ordered = sum(item.quantity_ordered for item in order.items.filter(is_deleted=False))
            total_received = sum(item.quantity_received for item in order.items.filter(is_deleted=False))
            completion_percentage = (total_received / total_ordered * 100) if total_ordered > 0 else 0
            
            # Calculate days until expected
            days_until_expected = None
            if order.expected_date:
                delta = order.expected_date - timezone.now().date()
                days_until_expected = delta.days
            
            pending_orders.append({
                'order_id': order.id,
                'order_number': order.order_number,
                'supplier_name': order.supplier.name,
                'warehouse_name': order.warehouse.name,
                'status': order.status,
                'order_date': order.order_date,
                'expected_date': order.expected_date,
                'total_amount': float(order.total_amount),
                'completion_percentage': round(completion_percentage, 2),
                'days_until_expected': days_until_expected,
                'item_count': order.items.filter(is_deleted=False).count()
            })
        
        return pending_orders
    
    @staticmethod
    def generate_reorder_suggestions() -> List[Dict]:
        """Generate reorder suggestions based on low stock levels."""
        from inventory_system.apps.inventory.services import InventoryService
        
        reorder_suggestions = InventoryService.check_reorder_points()
        
        # Group by supplier (assuming products have preferred suppliers)
        supplier_suggestions = {}
        
        for suggestion in reorder_suggestions:
            # For now, we'll use a simple logic to assign suppliers
            # In a real system, products would have preferred suppliers
            product_id = suggestion['product_id']
            
            # Get the most recent supplier for this product
            recent_order = PurchaseOrderItem.objects.filter(
                product_id=product_id,
                purchase_order__is_deleted=False
            ).select_related('purchase_order__supplier').order_by('-purchase_order__order_date').first()
            
            supplier_id = recent_order.purchase_order.supplier.id if recent_order else None
            supplier_name = recent_order.purchase_order.supplier.name if recent_order else "Unknown"
            
            if supplier_id not in supplier_suggestions:
                supplier_suggestions[supplier_id] = {
                    'supplier_id': supplier_id,
                    'supplier_name': supplier_name,
                    'items': []
                }
            
            supplier_suggestions[supplier_id]['items'].append(suggestion)
        
        return list(supplier_suggestions.values())
    
    @staticmethod
    def get_order_summary(days: int = 30) -> Dict:
        """Get purchase order summary for a period."""
        start_date = timezone.now().date() - timezone.timedelta(days=days)
        
        orders = PurchaseOrder.objects.filter(
            order_date__gte=start_date,
            is_deleted=False
        )
        
        total_orders = orders.count()
        total_value = orders.aggregate(total=Sum('total_amount'))['total'] or 0
        
        # Status breakdown
        status_breakdown = orders.values('status').annotate(
            count=Count('id'),
            total_value=Sum('total_amount')
        )
        
        # Supplier breakdown
        supplier_breakdown = orders.values('supplier__name').annotate(
            count=Count('id'),
            total_value=Sum('total_amount')
        ).order_by('-total_value')
        
        # Warehouse breakdown
        warehouse_breakdown = orders.values('warehouse__name').annotate(
            count=Count('id'),
            total_value=Sum('total_amount')
        ).order_by('-total_value')
        
        return {
            'period_days': days,
            'total_orders': total_orders,
            'total_value': float(total_value),
            'status_breakdown': list(status_breakdown),
            'supplier_breakdown': list(supplier_breakdown),
            'warehouse_breakdown': list(warehouse_breakdown)
        } 