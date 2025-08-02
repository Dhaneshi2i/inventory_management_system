"""
Purchase order management models for supplier orders and tracking.
"""
from typing import Optional, Dict, Any
from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db.models import Sum
from inventory_system.core.models import BaseModel
from inventory_system.apps.products.models import Product
from inventory_system.apps.inventory.models import Warehouse


class Supplier(BaseModel):
    """
    Supplier model for vendor information.
    """
    name = models.CharField(max_length=200, help_text="Supplier name")
    contact_person = models.CharField(max_length=100, help_text="Contact person name")
    email = models.EmailField(help_text="Contact email")
    phone = models.CharField(max_length=20, help_text="Contact phone")
    address = models.TextField(help_text="Supplier address")
    website = models.URLField(blank=True, help_text="Supplier website")
    tax_id = models.CharField(max_length=50, blank=True, help_text="Tax identification number")
    payment_terms = models.CharField(max_length=100, blank=True, help_text="Payment terms")
    is_active = models.BooleanField(default=True, help_text="Whether supplier is active")
    
    class Meta:
        verbose_name = "Supplier"
        verbose_name_plural = "Suppliers"
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['is_active']),
            models.Index(fields=['email']),
        ]

    def __str__(self) -> str:
        return self.name

    def clean(self) -> None:
        """Validate supplier data."""
        if self.name:
            self.name = self.name.strip()
            if not self.name:
                raise ValidationError("Supplier name cannot be empty")
        
        if self.contact_person:
            self.contact_person = self.contact_person.strip()
            if not self.contact_person:
                raise ValidationError("Contact person cannot be empty")

    @property
    def total_orders(self) -> int:
        """Get total number of orders from this supplier."""
        return self.purchase_orders.filter(is_deleted=False).count()

    @property
    def total_order_value(self) -> float:
        """Get total value of all orders from this supplier."""
        total = self.purchase_orders.filter(
            is_deleted=False
        ).aggregate(
            total=Sum('total_amount')
        )['total'] or 0
        return float(total)


class PurchaseOrder(BaseModel):
    """
    Purchase order model for managing supplier orders.
    """
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('ordered', 'Ordered'),
        ('received', 'Received'),
        ('cancelled', 'Cancelled'),
    ]
    
    order_number = models.CharField(
        max_length=50, 
        unique=True, 
        help_text="Unique order number"
    )
    supplier = models.ForeignKey(
        Supplier, 
        on_delete=models.CASCADE, 
        related_name='purchase_orders',
        help_text="Supplier"
    )
    warehouse = models.ForeignKey(
        Warehouse, 
        on_delete=models.CASCADE, 
        related_name='purchase_orders',
        help_text="Destination warehouse"
    )
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES,
        default='draft',
        help_text="Order status"
    )
    order_date = models.DateField(help_text="Order date")
    expected_date = models.DateField(help_text="Expected delivery date")
    received_date = models.DateField(blank=True, null=True, help_text="Actual received date")
    total_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Total order amount"
    )
    notes = models.TextField(blank=True, help_text="Order notes")
    approved_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_orders',
        help_text="User who approved the order"
    )
    approved_at = models.DateTimeField(blank=True, null=True, help_text="Approval timestamp")
    
    class Meta:
        verbose_name = "Purchase Order"
        verbose_name_plural = "Purchase Orders"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['order_number']),
            models.Index(fields=['status']),
            models.Index(fields=['order_date']),
            models.Index(fields=['supplier']),
            models.Index(fields=['warehouse']),
        ]

    def __str__(self) -> str:
        return f"PO-{self.order_number} - {self.supplier.name}"

    def clean(self) -> None:
        """Validate purchase order data."""
        if self.order_number:
            self.order_number = self.order_number.strip().upper()
            if not self.order_number:
                raise ValidationError("Order number cannot be empty")
        
        if self.expected_date and self.order_date and self.expected_date < self.order_date:
            raise ValidationError("Expected date cannot be before order date")
        
        if self.received_date and self.expected_date and self.received_date < self.order_date:
            raise ValidationError("Received date cannot be before order date")

    def save(self, *args, **kwargs):
        """Override save to auto-generate order number if not provided."""
        if not self.order_number:
            # Generate order number: PO-YYYYMMDD-XXXX
            from django.utils import timezone
            today = timezone.now().strftime('%Y%m%d')
            last_order = PurchaseOrder.objects.filter(
                order_number__startswith=f'PO-{today}'
            ).order_by('-order_number').first()
            
            if last_order:
                last_number = int(last_order.order_number.split('-')[-1])
                new_number = last_number + 1
            else:
                new_number = 1
            
            self.order_number = f"PO-{today}-{new_number:04d}"
        
        super().save(*args, **kwargs)

    @property
    def item_count(self) -> int:
        """Get total number of items in the order."""
        return self.items.filter(is_deleted=False).count()

    @property
    def total_quantity(self) -> int:
        """Get total quantity of all items."""
        total = self.items.filter(
            is_deleted=False
        ).aggregate(
            total=Sum('quantity_ordered')
        )['total'] or 0
        return total

    @property
    def received_quantity(self) -> int:
        """Get total received quantity."""
        total = self.items.filter(
            is_deleted=False
        ).aggregate(
            total=Sum('quantity_received')
        )['total'] or 0
        return total

    @property
    def is_complete(self) -> bool:
        """Check if all items have been received."""
        if self.status != 'received':
            return False
        
        items = self.items.filter(is_deleted=False)
        if not items.exists():
            return False
        
        return all(item.quantity_received >= item.quantity_ordered for item in items)

    def approve(self, user) -> bool:
        """Approve the purchase order."""
        if self.status not in ['draft', 'pending']:
            return False
        
        self.status = 'approved'
        self.approved_by = user
        self.approved_at = timezone.now()
        self.save(update_fields=['status', 'approved_by', 'approved_at'])
        return True

    def mark_as_ordered(self) -> bool:
        """Mark order as ordered."""
        if self.status != 'approved':
            return False
        
        self.status = 'ordered'
        self.save(update_fields=['status'])
        return True

    def receive_order(self, received_date=None) -> bool:
        """Mark order as received."""
        if self.status not in ['ordered', 'approved']:
            return False
        
        self.status = 'received'
        self.received_date = received_date or timezone.now().date()
        self.save(update_fields=['status', 'received_date'])
        return True

    def cancel_order(self) -> bool:
        """Cancel the order."""
        if self.status in ['received', 'cancelled']:
            return False
        
        self.status = 'cancelled'
        self.save(update_fields=['status'])
        return True

    def calculate_total(self) -> float:
        """Calculate total order amount."""
        total = self.items.filter(
            is_deleted=False
        ).aggregate(
            total=Sum('total_price')
        )['total'] or 0
        return float(total)

    def update_total(self) -> None:
        """Update the total amount."""
        self.total_amount = self.calculate_total()
        self.save(update_fields=['total_amount'])


class PurchaseOrderItem(BaseModel):
    """
    Purchase order item model for individual products in an order.
    """
    purchase_order = models.ForeignKey(
        PurchaseOrder, 
        on_delete=models.CASCADE, 
        related_name='items',
        help_text="Purchase order"
    )
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE, 
        related_name='purchase_order_items',
        help_text="Product"
    )
    quantity_ordered = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        help_text="Quantity ordered"
    )
    quantity_received = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Quantity received"
    )
    unit_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Unit price"
    )
    total_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Total price for this item"
    )
    notes = models.TextField(blank=True, help_text="Item notes")
    
    class Meta:
        verbose_name = "Purchase Order Item"
        verbose_name_plural = "Purchase Order Items"
        ordering = ['purchase_order', 'product__name']
        indexes = [
            models.Index(fields=['purchase_order', 'product']),
            models.Index(fields=['quantity_ordered']),
            models.Index(fields=['quantity_received']),
        ]

    def __str__(self) -> str:
        return f"{self.purchase_order.order_number} - {self.product.name} ({self.quantity_ordered})"

    def clean(self) -> None:
        """Validate order item data."""
        if self.quantity_received > self.quantity_ordered:
            raise ValidationError("Received quantity cannot exceed ordered quantity")

    def save(self, *args, **kwargs):
        """Override save to calculate total price."""
        self.total_price = self.quantity_ordered * self.unit_price
        super().save(*args, **kwargs)
        
        # Update order total
        self.purchase_order.update_total()

    @property
    def remaining_quantity(self) -> int:
        """Calculate remaining quantity to be received."""
        return max(0, self.quantity_ordered - self.quantity_received)

    @property
    def is_complete(self) -> bool:
        """Check if item has been fully received."""
        return self.quantity_received >= self.quantity_ordered

    def receive_quantity(self, quantity: int) -> bool:
        """Receive quantity for this item."""
        if quantity <= 0:
            return False
        
        if self.quantity_received + quantity > self.quantity_ordered:
            return False
        
        self.quantity_received += quantity
        self.save(update_fields=['quantity_received'])
        
        # Update inventory
        from inventory_system.apps.inventory.models import Inventory
        inventory, created = Inventory.objects.get_or_create(
            product=self.product,
            warehouse=self.purchase_order.warehouse,
            defaults={'quantity': 0}
        )
        
        inventory.adjust_quantity(
            quantity,
            'in',
            'purchase_order',
            self.purchase_order.id,
            f"Received from PO-{self.purchase_order.order_number}"
        )
        
        return True
