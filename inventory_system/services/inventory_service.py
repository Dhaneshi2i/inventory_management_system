"""
Inventory Service for core business logic.
"""
from django.db import transaction
from django.db.models import Sum, F, Q
from django.utils import timezone
from typing import List, Dict, Optional, Tuple
import logging

from inventory_system.apps.inventory.models import Inventory, StockMovement, Warehouse
from inventory_system.apps.products.models import Product
from inventory_system.apps.alerts.models import StockAlert, AlertRule

logger = logging.getLogger(__name__)


class InventoryService:
    """Service for inventory management operations."""
    
    @staticmethod
    def get_stock_levels(product: Product, warehouse: Optional[Warehouse] = None) -> Dict:
        """Get comprehensive stock levels for a product."""
        query = Inventory.objects.filter(product=product, is_deleted=False)
        
        if warehouse:
            query = query.filter(warehouse=warehouse)
        
        inventory_items = query.select_related('warehouse')
        
        total_quantity = sum(item.quantity for item in inventory_items)
        total_reserved = sum(item.reserved_quantity for item in inventory_items)
        total_available = sum(item.available_quantity for item in inventory_items)
        
        low_stock_locations = [
            item.warehouse.name for item in inventory_items 
            if item.is_low_stock
        ]
        
        out_of_stock_locations = [
            item.warehouse.name for item in inventory_items 
            if item.is_out_of_stock
        ]
        
        return {
            'product_id': product.id,
            'product_name': product.name,
            'total_quantity': total_quantity,
            'total_reserved': total_reserved,
            'total_available': total_available,
            'low_stock_locations': low_stock_locations,
            'out_of_stock_locations': out_of_stock_locations,
            'warehouse_breakdown': [
                {
                    'warehouse': item.warehouse.name,
                    'quantity': item.quantity,
                    'reserved': item.reserved_quantity,
                    'available': item.available_quantity,
                    'is_low_stock': item.is_low_stock,
                    'is_out_of_stock': item.is_out_of_stock
                }
                for item in inventory_items
            ]
        }
    
    @staticmethod
    def adjust_stock(
        product: Product, 
        warehouse: Warehouse, 
        quantity: int, 
        movement_type: str,
        reference_type: str = None,
        reference_id: int = None,
        notes: str = ""
    ) -> Tuple[bool, str]:
        """Adjust stock levels and create movement record."""
        try:
            with transaction.atomic():
                # Get or create inventory item
                inventory, created = Inventory.objects.get_or_create(
                    product=product,
                    warehouse=warehouse,
                    defaults={
                        'quantity': 0,
                        'reserved_quantity': 0,
                        'reorder_point': 10,
                        'max_stock_level': 1000
                    }
                )
                
                # Validate adjustment
                if movement_type in ['out', 'transfer_out'] and quantity > inventory.available_quantity:
                    return False, f"Insufficient stock. Available: {inventory.available_quantity}, Requested: {quantity}"
                
                # Update inventory
                old_quantity = inventory.quantity
                inventory.quantity += quantity
                inventory.save()
                
                # Create movement record
                StockMovement.objects.create(
                    product=product,
                    warehouse=warehouse,
                    movement_type=movement_type,
                    quantity=quantity,
                    reference_type=reference_type,
                    reference_id=reference_id,
                    notes=notes
                )
                
                logger.info(
                    f"Stock adjusted: {product.name} at {warehouse.name} "
                    f"({old_quantity} -> {inventory.quantity}) "
                    f"Type: {movement_type}, Notes: {notes}"
                )
                
                return True, f"Stock adjusted successfully. New quantity: {inventory.quantity}"
                
        except Exception as e:
            logger.error(f"Error adjusting stock: {e}")
            return False, f"Error adjusting stock: {str(e)}"
    
    @staticmethod
    def transfer_stock(
        product: Product,
        source_warehouse: Warehouse,
        target_warehouse: Warehouse,
        quantity: int,
        notes: str = ""
    ) -> Tuple[bool, str]:
        """Transfer stock between warehouses."""
        try:
            with transaction.atomic():
                # Check source inventory
                source_inventory = Inventory.objects.get(
                    product=product,
                    warehouse=source_warehouse,
                    is_deleted=False
                )
                
                if source_inventory.available_quantity < quantity:
                    return False, f"Insufficient stock at source. Available: {source_inventory.available_quantity}"
                
                # Transfer out from source
                success, message = InventoryService.adjust_stock(
                    product=product,
                    warehouse=source_warehouse,
                    quantity=-quantity,
                    movement_type='transfer_out',
                    reference_type='transfer',
                    notes=f"Transfer to {target_warehouse.name}: {notes}"
                )
                
                if not success:
                    return False, message
                
                # Transfer in to target
                success, message = InventoryService.adjust_stock(
                    product=product,
                    warehouse=target_warehouse,
                    quantity=quantity,
                    movement_type='transfer_in',
                    reference_type='transfer',
                    notes=f"Transfer from {source_warehouse.name}: {notes}"
                )
                
                if not success:
                    # Rollback source adjustment
                    InventoryService.adjust_stock(
                        product=product,
                        warehouse=source_warehouse,
                        quantity=quantity,
                        movement_type='adjustment',
                        reference_type='rollback',
                        notes="Rollback due to target transfer failure"
                    )
                    return False, message
                
                return True, f"Successfully transferred {quantity} units from {source_warehouse.name} to {target_warehouse.name}"
                
        except Inventory.DoesNotExist:
            return False, f"No inventory found for {product.name} at {source_warehouse.name}"
        except Exception as e:
            logger.error(f"Error transferring stock: {e}")
            return False, f"Error transferring stock: {str(e)}"
    
    @staticmethod
    def reserve_stock(
        product: Product,
        warehouse: Warehouse,
        quantity: int
    ) -> Tuple[bool, str]:
        """Reserve stock for future use."""
        try:
            with transaction.atomic():
                inventory = Inventory.objects.get(
                    product=product,
                    warehouse=warehouse,
                    is_deleted=False
                )
                
                if inventory.available_quantity < quantity:
                    return False, f"Insufficient available stock. Available: {inventory.available_quantity}"
                
                inventory.reserved_quantity += quantity
                inventory.save()
                
                logger.info(
                    f"Stock reserved: {product.name} at {warehouse.name} "
                    f"Reserved: {inventory.reserved_quantity}"
                )
                
                return True, f"Successfully reserved {quantity} units"
                
        except Inventory.DoesNotExist:
            return False, f"No inventory found for {product.name} at {warehouse.name}"
        except Exception as e:
            logger.error(f"Error reserving stock: {e}")
            return False, f"Error reserving stock: {str(e)}"
    
    @staticmethod
    def release_reserved_stock(
        product: Product,
        warehouse: Warehouse,
        quantity: int
    ) -> Tuple[bool, str]:
        """Release reserved stock."""
        try:
            with transaction.atomic():
                inventory = Inventory.objects.get(
                    product=product,
                    warehouse=warehouse,
                    is_deleted=False
                )
                
                if inventory.reserved_quantity < quantity:
                    return False, f"Insufficient reserved stock. Reserved: {inventory.reserved_quantity}"
                
                inventory.reserved_quantity -= quantity
                inventory.save()
                
                logger.info(
                    f"Reserved stock released: {product.name} at {warehouse.name} "
                    f"Reserved: {inventory.reserved_quantity}"
                )
                
                return True, f"Successfully released {quantity} reserved units"
                
        except Inventory.DoesNotExist:
            return False, f"No inventory found for {product.name} at {warehouse.name}"
        except Exception as e:
            logger.error(f"Error releasing reserved stock: {e}")
            return False, f"Error releasing reserved stock: {str(e)}"
    
    @staticmethod
    def check_reorder_points() -> List[Dict]:
        """Check all inventory items for reorder point violations."""
        low_stock_items = Inventory.objects.filter(
            is_deleted=False,
            quantity__lte=F('reorder_point')
        ).select_related('product', 'warehouse', 'product__category')
        
        reorder_suggestions = []
        
        for item in low_stock_items:
            # Calculate suggested reorder quantity
            suggested_quantity = max(
                item.max_stock_level - item.quantity,
                item.reorder_point * 2  # At least double the reorder point
            )
            
            reorder_suggestions.append({
                'product_id': item.product.id,
                'product_name': item.product.name,
                'product_sku': item.product.sku,
                'category': item.product.category.name,
                'warehouse_id': item.warehouse.id,
                'warehouse_name': item.warehouse.name,
                'current_quantity': item.quantity,
                'reorder_point': item.reorder_point,
                'max_stock_level': item.max_stock_level,
                'suggested_quantity': suggested_quantity,
                'urgency': 'critical' if item.quantity == 0 else 'high' if item.quantity <= item.reorder_point // 2 else 'medium'
            })
        
        return reorder_suggestions
    
    @staticmethod
    def get_warehouse_utilization(warehouse: Warehouse) -> Dict:
        """Get detailed warehouse utilization metrics."""
        inventory_items = warehouse.inventory_items.filter(is_deleted=False)
        
        total_quantity = inventory_items.aggregate(total=Sum('quantity'))['total'] or 0
        total_reserved = inventory_items.aggregate(total=Sum('reserved_quantity'))['total'] or 0
        total_available = total_quantity - total_reserved
        
        utilization_percentage = (total_quantity / warehouse.capacity) * 100 if warehouse.capacity > 0 else 0
        available_capacity = max(0, warehouse.capacity - total_quantity)
        
        # Get top products by quantity
        top_products = inventory_items.values('product__name').annotate(
            total_quantity=Sum('quantity')
        ).order_by('-total_quantity')[:5]
        
        # Get low stock items
        low_stock_count = inventory_items.filter(quantity__lte=F('reorder_point')).count()
        out_of_stock_count = inventory_items.filter(quantity=0).count()
        
        return {
            'warehouse_id': warehouse.id,
            'warehouse_name': warehouse.name,
            'capacity': warehouse.capacity,
            'total_quantity': total_quantity,
            'total_reserved': total_reserved,
            'total_available': total_available,
            'utilization_percentage': round(utilization_percentage, 2),
            'available_capacity': available_capacity,
            'low_stock_count': low_stock_count,
            'out_of_stock_count': out_of_stock_count,
            'top_products': list(top_products),
            'status': 'full' if utilization_percentage >= 90 else 'high' if utilization_percentage >= 75 else 'normal'
        }
    
    @staticmethod
    def get_product_valuation(product: Product) -> Dict:
        """Get product valuation across all warehouses."""
        inventory_items = Inventory.objects.filter(
            product=product,
            is_deleted=False
        ).select_related('warehouse')
        
        total_quantity = sum(item.quantity for item in inventory_items)
        total_value = sum(item.quantity * product.unit_price for item in inventory_items)
        
        warehouse_breakdown = []
        for item in inventory_items:
            warehouse_breakdown.append({
                'warehouse_id': item.warehouse.id,
                'warehouse_name': item.warehouse.name,
                'quantity': item.quantity,
                'value': item.quantity * product.unit_price
            })
        
        return {
            'product_id': product.id,
            'product_name': product.name,
            'product_sku': product.sku,
            'unit_price': product.unit_price,
            'total_quantity': total_quantity,
            'total_value': total_value,
            'warehouse_breakdown': warehouse_breakdown
        }
    
    @staticmethod
    def bulk_adjust_stock(adjustments: List[Dict]) -> Tuple[int, List[str]]:
        """Bulk adjust stock levels."""
        success_count = 0
        errors = []
        
        for adjustment in adjustments:
            try:
                product_id = adjustment.get('product_id')
                warehouse_id = adjustment.get('warehouse_id')
                quantity = adjustment.get('quantity', 0)
                movement_type = adjustment.get('movement_type', 'adjustment')
                notes = adjustment.get('notes', 'Bulk adjustment')
                
                if not all([product_id, warehouse_id]):
                    errors.append("Missing product_id or warehouse_id")
                    continue
                
                product = Product.objects.get(id=product_id, is_deleted=False)
                warehouse = Warehouse.objects.get(id=warehouse_id, is_deleted=False)
                
                success, message = InventoryService.adjust_stock(
                    product=product,
                    warehouse=warehouse,
                    quantity=quantity,
                    movement_type=movement_type,
                    notes=notes
                )
                
                if success:
                    success_count += 1
                else:
                    errors.append(f"Product {product.name}: {message}")
                    
            except (Product.DoesNotExist, Warehouse.DoesNotExist) as e:
                errors.append(f"Invalid product or warehouse: {str(e)}")
            except Exception as e:
                errors.append(f"Unexpected error: {str(e)}")
        
        return success_count, errors 