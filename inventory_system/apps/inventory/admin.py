"""
Admin configuration for inventory models.
"""
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.db.models import Sum, Count, Q
from django import forms
from .models import Warehouse, Inventory, StockMovement


class InventoryInline(admin.TabularInline):
    """Inline admin for Inventory items in Warehouse."""
    model = Inventory
    extra = 0
    readonly_fields = ('available_quantity', 'is_low_stock', 'is_out_of_stock', 'stock_value')
    fields = ('product', 'quantity', 'reserved_quantity', 'available_quantity', 'reorder_point', 'max_stock_level', 'is_low_stock', 'is_out_of_stock', 'stock_value')


@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    """Admin for Warehouse model."""
    list_display = ('name', 'manager', 'capacity', 'current_utilization', 'available_capacity', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'manager', 'address')
    readonly_fields = ('id', 'created_at', 'updated_at', 'current_utilization', 'available_capacity')
    ordering = ('name',)
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'manager', 'address')
        }),
        ('Contact Information', {
            'fields': ('contact_email', 'contact_phone'),
            'classes': ('collapse',)
        }),
        ('Capacity', {
            'fields': ('capacity', 'current_utilization', 'available_capacity')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Metadata', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [InventoryInline]

    def current_utilization(self, obj):
        """Display current utilization with color coding."""
        utilization = obj.current_utilization
        if utilization >= 90:
            color = 'red'
        elif utilization >= 75:
            color = 'orange'
        else:
            color = 'green'
        return format_html('<span style="color: {};">{:.1f}%</span>', color, utilization)
    current_utilization.short_description = 'Utilization'

    def available_capacity(self, obj):
        """Display available capacity."""
        capacity = obj.available_capacity
        return format_html('<span style="color: blue;">{}</span>', capacity)
    available_capacity.short_description = 'Available Capacity'


@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    """Admin for Inventory model."""
    list_display = ('product', 'warehouse', 'quantity', 'reserved_quantity', 'available_quantity', 'stock_status', 'stock_value', 'last_updated')
    list_filter = ('warehouse', 'product__category', 'last_updated')
    search_fields = ('product__name', 'product__sku', 'warehouse__name')
    readonly_fields = ('id', 'created_at', 'updated_at', 'available_quantity', 'is_low_stock', 'is_out_of_stock', 'stock_value', 'last_updated')
    ordering = ('product__name', 'warehouse__name')
    
    fieldsets = (
        ('Product & Warehouse', {
            'fields': ('product', 'warehouse')
        }),
        ('Stock Levels', {
            'fields': ('quantity', 'reserved_quantity', 'available_quantity')
        }),
        ('Thresholds', {
            'fields': ('reorder_point', 'max_stock_level')
        }),
        ('Status', {
            'fields': ('is_low_stock', 'is_out_of_stock', 'stock_value')
        }),
        ('Metadata', {
            'fields': ('id', 'created_at', 'updated_at', 'last_updated'),
            'classes': ('collapse',)
        }),
    )

    def stock_status(self, obj):
        """Display stock status with color coding."""
        if obj.is_out_of_stock:
            return format_html('<span style="color: red;">Out of Stock</span>')
        elif obj.is_low_stock:
            return format_html('<span style="color: orange;">Low Stock</span>')
        else:
            return format_html('<span style="color: green;">In Stock</span>')
    stock_status.short_description = 'Status'

    # def stock_value(self, obj):
    #     """Display stock value."""
    #     value = obj.stock_value
    #     return format_html('<span style="color: green;">${:.2f}</span>', value)
    def stock_value(self, obj):
        """Display stock value."""
        try:
            value = float(obj.stock_value) if obj.stock_value else 0
            return format_html('<span style="color: green;">${:.2f}</span>', value)
        except (ValueError, TypeError):
            return format_html('<span style="color: gray;">N/A</span>')


    def get_queryset(self, request):
        """Optimize queryset with related data."""
        return super().get_queryset(request).select_related('product', 'warehouse', 'product__category')

    actions = ['adjust_quantities', 'export_inventory', 'set_reorder_points']

    def adjust_quantities(self, request, queryset):
        """Adjust quantities for selected inventory items."""
        # This is a placeholder action - you can implement quantity adjustment logic here
        count = queryset.count()
        self.message_user(request, f'{count} inventory items selected for quantity adjustment.')
    adjust_quantities.short_description = "Adjust quantities for selected items"

    def export_inventory(self, request, queryset):
        """Export inventory data."""
        import csv
        from django.http import HttpResponse
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="inventory.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Product', 'SKU', 'Warehouse', 'Quantity', 'Reserved', 'Available', 'Reorder Point', 'Value'])
        
        for item in queryset:
            writer.writerow([
                item.product.name,
                item.product.sku,
                item.warehouse.name,
                item.quantity,
                item.reserved_quantity,
                item.available_quantity,
                item.reorder_point,
                item.stock_value
            ])
        
        return response
    export_inventory.short_description = "Export inventory to CSV"

    def set_reorder_points(self, request, queryset):
        """Set reorder points for selected items."""
        # This is a placeholder action - you can implement reorder point logic here
        count = queryset.count()
        self.message_user(request, f'{count} inventory items selected for reorder point update.')
    set_reorder_points.short_description = "Set reorder points for selected items"


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    """Admin for StockMovement model."""
    list_display = ('product', 'warehouse', 'movement_type', 'quantity', 'movement_value', 'reference_info', 'created_at')
    list_filter = ('movement_type', 'warehouse', 'created_at')
    search_fields = ('product__name', 'product__sku', 'warehouse__name', 'notes')
    readonly_fields = ('id', 'created_at', 'updated_at', 'movement_value')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Movement Details', {
            'fields': ('product', 'warehouse', 'movement_type', 'quantity')
        }),
        ('Reference Information', {
            'fields': ('reference_type', 'reference_id', 'notes'),
            'classes': ('collapse',)
        }),
        ('Value', {
            'fields': ('movement_value',)
        }),
        ('Metadata', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def movement_value(self, obj):
        """Display movement value."""
        value = obj.movement_value
        return format_html('<span style="color: green;">${:.2f}</span>', value)
    movement_value.short_description = 'Value'

    def reference_info(self, obj):
        """Display reference information."""
        if obj.reference_type and obj.reference_id:
            return f"{obj.reference_type.title()} #{obj.reference_id}"
        return "-"
    reference_info.short_description = 'Reference'

    def get_queryset(self, request):
        """Optimize queryset with related data."""
        return super().get_queryset(request).select_related('product', 'warehouse')

    actions = ['export_movements']

    def export_movements(self, request, queryset):
        """Export stock movements."""
        import csv
        from django.http import HttpResponse
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="stock_movements.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Date', 'Product', 'SKU', 'Warehouse', 'Type', 'Quantity', 'Value', 'Reference', 'Notes'])
        
        for movement in queryset:
            writer.writerow([
                movement.created_at.strftime('%Y-%m-%d %H:%M'),
                movement.product.name,
                movement.product.sku,
                movement.warehouse.name,
                movement.get_movement_type_display(),
                movement.quantity,
                movement.movement_value,
                movement.reference_info(),
                movement.notes
            ])
        
        return response
    export_movements.short_description = "Export movements to CSV"
