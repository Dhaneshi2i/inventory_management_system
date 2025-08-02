"""
Product catalog models for the Inventory Management System.
"""
import json
from typing import Dict, Any, Optional
from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from inventory_system.core.models import BaseModel


class Category(BaseModel):
    """
    Product category model for organizing products.
    """
    name = models.CharField(max_length=100, unique=True, help_text="Category name")
    description = models.TextField(blank=True, help_text="Category description")
    
    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
        ]

    def __str__(self) -> str:
        return self.name

    def clean(self) -> None:
        """Validate the category data."""
        if self.name:
            self.name = self.name.strip()
            if not self.name:
                raise ValidationError("Category name cannot be empty")


class Product(BaseModel):
    """
    Product model for the inventory management system.
    """
    name = models.CharField(max_length=200, help_text="Product name")
    sku = models.CharField(max_length=50, unique=True, help_text="Stock Keeping Unit")
    category = models.ForeignKey(
        Category, 
        on_delete=models.CASCADE, 
        related_name='products',
        help_text="Product category"
    )
    description = models.TextField(blank=True, help_text="Product description")
    unit_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Unit price in currency"
    )
    specifications = models.JSONField(default=dict, blank=True, help_text="Product specifications")
    
    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['sku']),
            models.Index(fields=['name']),
            models.Index(fields=['category']),
        ]

    def __str__(self) -> str:
        return f"{self.name} ({self.sku})"

    def clean(self) -> None:
        """Validate the product data."""
        if self.name:
            self.name = self.name.strip()
            if not self.name:
                raise ValidationError("Product name cannot be empty")
        
        if self.sku:
            self.sku = self.sku.strip().upper()
            if not self.sku:
                raise ValidationError("SKU cannot be empty")

    def get_specifications(self) -> Dict[str, Any]:
        """Get product specifications as a dictionary."""
        if isinstance(self.specifications, str):
            try:
                return json.loads(self.specifications)
            except json.JSONDecodeError:
                return {}
        return self.specifications or {}

    def set_specifications(self, specs: Dict[str, Any]) -> None:
        """Set product specifications from a dictionary."""
        self.specifications = specs

    @property
    def total_value(self) -> Optional[float]:
        """Calculate total inventory value for this product."""
        from inventory_system.apps.inventory.models import Inventory
        total_quantity = Inventory.objects.filter(
            product=self, 
            is_deleted=False
        ).aggregate(
            total=models.Sum('quantity')
        )['total'] or 0
        return float(total_quantity * self.unit_price)
