"""
Admin configuration for product models.
"""
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.db.models import Sum, Count
from .models import Category, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Admin for Category model."""
    list_display = ('name', 'description', 'product_count', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('name', 'description')
    readonly_fields = ('id', 'created_at', 'updated_at')
    ordering = ('name',)
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description')
        }),
        ('Metadata', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def product_count(self, obj):
        """Display product count for category."""
        count = obj.products.filter(is_deleted=False).count()
        return count
    product_count.short_description = 'Products'
    product_count.admin_order_field = 'products__count'

    def get_queryset(self, request):
        """Annotate queryset with product count."""
        return super().get_queryset(request).annotate(
            product_count=Count('products', filter=models.Q(products__is_deleted=False))
        )


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Admin for Product model."""
    list_display = ('name', 'sku', 'category', 'unit_price', 'total_value', 'stock_status', 'created_at')
    list_filter = ('category', 'created_at', 'updated_at')
    search_fields = ('name', 'sku', 'description')
    readonly_fields = ('id', 'created_at', 'updated_at', 'total_value')
    ordering = ('name',)
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'sku', 'category', 'description')
        }),
        ('Pricing', {
            'fields': ('unit_price', 'total_value')
        }),
        ('Specifications', {
            'fields': ('specifications',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def total_value(self, obj):
        """Display total inventory value."""
        value = obj.total_value
        if value:
            return format_html('<span style="color: green;">${:.2f}</span>', value)
        return '$0.00'
    total_value.short_description = 'Total Value'
    total_value.admin_order_field = 'unit_price'

    def stock_status(self, obj):
        """Display stock status with color coding."""
        from inventory_system.apps.inventory.models import Inventory
        
        inventory_items = Inventory.objects.filter(
            product=obj, 
            is_deleted=False
        )
        
        total_quantity = inventory_items.aggregate(
            total=Sum('quantity')
        )['total'] or 0
        
        low_stock_count = inventory_items.filter(
            quantity__lte=models.F('reorder_point')
        ).count()
        
        out_of_stock_count = inventory_items.filter(quantity=0).count()
        
        if out_of_stock_count > 0:
            return format_html('<span style="color: red;">Out of Stock</span>')
        elif low_stock_count > 0:
            return format_html('<span style="color: orange;">Low Stock</span>')
        elif total_quantity > 0:
            return format_html('<span style="color: green;">In Stock ({})</span>', total_quantity)
        else:
            return format_html('<span style="color: gray;">No Stock</span>')
    
    stock_status.short_description = 'Stock Status'

    def get_queryset(self, request):
        """Optimize queryset with related data."""
        return super().get_queryset(request).select_related('category')

    actions = ['export_products', 'update_prices']

    def export_products(self, request, queryset):
        """Export selected products."""
        import csv
        from django.http import HttpResponse
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="products.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['SKU', 'Name', 'Category', 'Unit Price', 'Description'])
        
        for product in queryset:
            writer.writerow([
                product.sku,
                product.name,
                product.category.name,
                product.unit_price,
                product.description
            ])
        
        return response
    export_products.short_description = "Export selected products to CSV"

    def update_prices(self, request, queryset):
        """Update product prices."""
        # This is a placeholder action - you can implement price update logic here
        count = queryset.count()
        self.message_user(request, f'{count} products selected for price update.')
    update_prices.short_description = "Update prices for selected products"
