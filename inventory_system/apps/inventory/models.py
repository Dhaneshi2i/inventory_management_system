"""
Inventory management models for tracking stock levels and movements.
"""
from typing import Optional, Dict, Any
from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db.models import Sum, Q
from inventory_system.core.models import BaseModel
from inventory_system.apps.products.models import Product


class Warehouse(BaseModel):
    """
    Warehouse model for storing location information.
    """
    name = models.CharField(max_length=100, help_text="Warehouse name")
    address = models.TextField(help_text="Warehouse address")
    capacity = models.PositiveIntegerField(help_text="Warehouse capacity in units")
    manager = models.CharField(max_length=100, help_text="Warehouse manager name")
    contact_email = models.EmailField(blank=True, help_text="Contact email")
    contact_phone = models.CharField(max_length=20, blank=True, help_text="Contact phone")
    is_active = models.BooleanField(default=True, help_text="Whether warehouse is active")
    
    class Meta:
        verbose_name = "Warehouse"
        verbose_name_plural = "Warehouses"
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self) -> str:
        return self.name

    def clean(self) -> None:
        """Validate warehouse data."""
        if self.name:
            self.name = self.name.strip()
            if not self.name:
                raise ValidationError("Warehouse name cannot be empty")
        
        if self.capacity <= 0:
            raise ValidationError("Capacity must be greater than 0")

    @property
    def current_utilization(self) -> float:
        """Calculate current warehouse utilization percentage."""
        total_stock = Inventory.objects.filter(
            warehouse=self, 
            is_deleted=False
        ).aggregate(
            total=Sum('quantity')
        )['total'] or 0
        return (total_stock / self.capacity) * 100 if self.capacity > 0 else 0

    @property
    def available_capacity(self) -> int:
        """Calculate available capacity."""
        total_stock = Inventory.objects.filter(
            warehouse=self, 
            is_deleted=False
        ).aggregate(
            total=Sum('quantity')
        )['total'] or 0
        return max(0, self.capacity - total_stock)


class Inventory(BaseModel):
    """
    Inventory model for tracking stock levels per product per warehouse.
    """
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE, 
        related_name='inventory_items',
        help_text="Product"
    )
    warehouse = models.ForeignKey(
        Warehouse, 
        on_delete=models.CASCADE, 
        related_name='inventory_items',
        help_text="Warehouse"
    )
    quantity = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Current stock quantity"
    )
    reserved_quantity = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Reserved quantity for pending orders"
    )
    reorder_point = models.PositiveIntegerField(
        default=0,
        help_text="Reorder point threshold"
    )
    max_stock_level = models.PositiveIntegerField(
        default=0,
        help_text="Maximum stock level"
    )
    last_updated = models.DateTimeField(auto_now=True, help_text="Last update timestamp")
    
    class Meta:
        verbose_name = "Inventory"
        verbose_name_plural = "Inventory"
        unique_together = ['product', 'warehouse']
        ordering = ['product__name', 'warehouse__name']
        indexes = [
            models.Index(fields=['product', 'warehouse']),
            models.Index(fields=['quantity']),
            models.Index(fields=['reorder_point']),
        ]

    def __str__(self) -> str:
        return f"{self.product.name} - {self.warehouse.name} ({self.quantity})"

    def clean(self) -> None:
        """Validate inventory data."""
        if self.quantity < 0:
            raise ValidationError("Quantity cannot be negative")
        
        if self.reserved_quantity > self.quantity:
            raise ValidationError("Reserved quantity cannot exceed available quantity")
        
        if self.max_stock_level > 0 and self.quantity > self.max_stock_level:
            raise ValidationError("Quantity cannot exceed maximum stock level")

    @property
    def available_quantity(self) -> int:
        """Calculate available quantity (total - reserved)."""
        return max(0, self.quantity - self.reserved_quantity)

    @property
    def is_low_stock(self) -> bool:
        """Check if stock is below reorder point."""
        return self.available_quantity <= self.reorder_point

    @property
    def is_out_of_stock(self) -> bool:
        """Check if product is out of stock."""
        return self.available_quantity == 0

    @property
    def stock_value(self) -> float:
        """Calculate total stock value."""
        return float(self.quantity * self.product.unit_price)

    def reserve_quantity(self, amount: int) -> bool:
        """Reserve quantity for pending orders."""
        if amount <= 0:
            return False
        
        if self.available_quantity >= amount:
            self.reserved_quantity += amount
            self.save(update_fields=['reserved_quantity', 'last_updated'])
            return True
        return False

    def release_reserved_quantity(self, amount: int) -> bool:
        """Release reserved quantity."""
        if amount <= 0:
            return False
        
        if self.reserved_quantity >= amount:
            self.reserved_quantity -= amount
            self.save(update_fields=['reserved_quantity', 'last_updated'])
            return True
        return False

    def adjust_quantity(self, amount: int, movement_type: str, reference_type: str = None, reference_id: int = None, notes: str = None) -> bool:
        """Adjust inventory quantity and create movement record."""
        if amount == 0:
            return False
        
        # Calculate new quantity based on movement type
        if movement_type == 'in':
            new_quantity = self.quantity + amount
        elif movement_type == 'out':
            if self.available_quantity < amount:
                return False
            new_quantity = self.quantity - amount
        elif movement_type == 'adjustment':
            new_quantity = amount
        else:
            return False
        
        if new_quantity < 0:
            return False
        
        # Update inventory
        old_quantity = self.quantity
        self.quantity = new_quantity
        self.save(update_fields=['quantity', 'last_updated'])
        
        # Create movement record
        StockMovement.objects.create(
            product=self.product,
            warehouse=self.warehouse,
            movement_type=movement_type,
            quantity=abs(amount),
            reference_type=reference_type,
            reference_id=reference_id,
            notes=notes or f"Quantity adjusted from {old_quantity} to {new_quantity}"
        )
        
        return True


class StockMovement(BaseModel):
    """
    Stock movement model for tracking all inventory changes.
    """
    MOVEMENT_TYPES = [
        ('in', 'Stock In'),
        ('out', 'Stock Out'),
        ('transfer', 'Transfer'),
        ('adjustment', 'Adjustment'),
    ]
    
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE, 
        related_name='stock_movements',
        help_text="Product"
    )
    warehouse = models.ForeignKey(
        Warehouse, 
        on_delete=models.CASCADE, 
        related_name='stock_movements',
        help_text="Warehouse"
    )
    movement_type = models.CharField(
        max_length=20, 
        choices=MOVEMENT_TYPES,
        help_text="Type of movement"
    )
    quantity = models.PositiveIntegerField(help_text="Quantity moved")
    reference_type = models.CharField(
        max_length=50, 
        blank=True, 
        null=True,
        help_text="Reference type (e.g., purchase_order, sale, adjustment)"
    )
    reference_id = models.PositiveIntegerField(
        blank=True, 
        null=True,
        help_text="Reference ID"
    )
    notes = models.TextField(blank=True, help_text="Movement notes")
    
    class Meta:
        verbose_name = "Stock Movement"
        verbose_name_plural = "Stock Movements"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['product', 'warehouse']),
            models.Index(fields=['movement_type']),
            models.Index(fields=['created_at']),
            models.Index(fields=['reference_type', 'reference_id']),
        ]

    def __str__(self) -> str:
        return f"{self.product.name} - {self.get_movement_type_display()} ({self.quantity}) at {self.warehouse.name}"

    def clean(self) -> None:
        """Validate movement data."""
        if self.quantity <= 0:
            raise ValidationError("Quantity must be greater than 0")

    @property
    def movement_value(self) -> float:
        """Calculate movement value."""
        return float(self.quantity * self.product.unit_price)
