"""
Admin configuration for order models.
"""
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.db.models import Sum, Count, Q
from django import forms
from .models import Supplier, PurchaseOrder, PurchaseOrderItem


class PurchaseOrderItemInline(admin.TabularInline):
    """Inline admin for PurchaseOrderItem in PurchaseOrder."""
    model = PurchaseOrderItem
    extra = 1
    readonly_fields = ('total_price', 'remaining_quantity', 'is_complete')
    fields = ('product', 'quantity_ordered', 'quantity_received', 'unit_price', 'total_price', 'remaining_quantity', 'is_complete', 'notes')


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    """Admin for Supplier model."""
    list_display = ('name', 'contact_person', 'email', 'phone', 'total_orders', 'total_order_value', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'contact_person', 'email', 'phone')
    readonly_fields = ('id', 'created_at', 'updated_at', 'total_orders', 'total_order_value')
    ordering = ('name',)
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'contact_person')
        }),
        ('Contact Information', {
            'fields': ('email', 'phone', 'address', 'website')
        }),
        ('Business Information', {
            'fields': ('tax_id', 'payment_terms'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Statistics', {
            'fields': ('total_orders', 'total_order_value'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def total_orders(self, obj):
        """Display total orders count."""
        count = obj.total_orders
        return format_html('<span style="color: blue;">{}</span>', count)
    total_orders.short_description = 'Total Orders'

    def total_order_value(self, obj):
        """Display total order value."""
        value = obj.total_order_value
        return format_html('<span style="color: green;">${:.2f}</span>', value)
    total_order_value.short_description = 'Total Value'

    actions = ['export_suppliers', 'deactivate_suppliers']

    def export_suppliers(self, request, queryset):
        """Export suppliers data."""
        import csv
        from django.http import HttpResponse
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="suppliers.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Name', 'Contact Person', 'Email', 'Phone', 'Address', 'Website', 'Tax ID', 'Payment Terms'])
        
        for supplier in queryset:
            writer.writerow([
                supplier.name,
                supplier.contact_person,
                supplier.email,
                supplier.phone,
                supplier.address,
                supplier.website,
                supplier.tax_id,
                supplier.payment_terms
            ])
        
        return response
    export_suppliers.short_description = "Export suppliers to CSV"

    def deactivate_suppliers(self, request, queryset):
        """Deactivate selected suppliers."""
        count = queryset.update(is_active=False)
        self.message_user(request, f'{count} suppliers were deactivated.')
    deactivate_suppliers.short_description = "Deactivate selected suppliers"


@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    """Admin for PurchaseOrder model."""
    list_display = ('order_number', 'supplier', 'warehouse', 'status', 'order_date', 'expected_date', 'total_amount', 'item_count', 'is_complete', 'created_at')
    list_filter = ('status', 'supplier', 'warehouse', 'order_date', 'expected_date', 'created_at')
    search_fields = ('order_number', 'supplier__name', 'warehouse__name', 'notes')
    readonly_fields = ('id', 'created_at', 'updated_at', 'total_amount', 'item_count', 'total_quantity', 'received_quantity', 'is_complete', 'approved_by', 'approved_at')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Order Information', {
            'fields': ('order_number', 'supplier', 'warehouse', 'status')
        }),
        ('Dates', {
            'fields': ('order_date', 'expected_date', 'received_date')
        }),
        ('Financial', {
            'fields': ('total_amount',)
        }),
        ('Approval', {
            'fields': ('approved_by', 'approved_at'),
            'classes': ('collapse',)
        }),
        ('Notes', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        ('Statistics', {
            'fields': ('item_count', 'total_quantity', 'received_quantity', 'is_complete'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [PurchaseOrderItemInline]

    def item_count(self, obj):
        """Display item count."""
        count = obj.item_count
        return format_html('<span style="color: blue;">{}</span>', count)
    item_count.short_description = 'Items'

    def is_complete(self, obj):
        """Display completion status."""
        if obj.is_complete:
            return format_html('<span style="color: green;">✓ Complete</span>')
        else:
            return format_html('<span style="color: orange;">○ Pending</span>')
    is_complete.short_description = 'Complete'

    def get_queryset(self, request):
        """Optimize queryset with related data."""
        return super().get_queryset(request).select_related('supplier', 'warehouse', 'approved_by')

    actions = ['approve_orders', 'mark_as_ordered', 'receive_orders', 'cancel_orders', 'export_orders']

    def approve_orders(self, request, queryset):
        """Approve selected orders."""
        count = 0
        for order in queryset:
            if order.approve(request.user):
                count += 1
        self.message_user(request, f'{count} orders were approved.')
    approve_orders.short_description = "Approve selected orders"

    def mark_as_ordered(self, request, queryset):
        """Mark selected orders as ordered."""
        count = 0
        for order in queryset:
            if order.mark_as_ordered():
                count += 1
        self.message_user(request, f'{count} orders were marked as ordered.')
    mark_as_ordered.short_description = "Mark as ordered"

    def receive_orders(self, request, queryset):
        """Mark selected orders as received."""
        count = 0
        for order in queryset:
            if order.receive_order():
                count += 1
        self.message_user(request, f'{count} orders were marked as received.')
    receive_orders.short_description = "Mark as received"

    def cancel_orders(self, request, queryset):
        """Cancel selected orders."""
        count = 0
        for order in queryset:
            if order.cancel_order():
                count += 1
        self.message_user(request, f'{count} orders were cancelled.')
    cancel_orders.short_description = "Cancel selected orders"

    def export_orders(self, request, queryset):
        """Export purchase orders."""
        import csv
        from django.http import HttpResponse
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="purchase_orders.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Order Number', 'Supplier', 'Warehouse', 'Status', 'Order Date', 'Expected Date', 'Total Amount', 'Items'])
        
        for order in queryset:
            writer.writerow([
                order.order_number,
                order.supplier.name,
                order.warehouse.name,
                order.get_status_display(),
                order.order_date,
                order.expected_date,
                order.total_amount,
                order.item_count
            ])
        
        return response
    export_orders.short_description = "Export orders to CSV"


@admin.register(PurchaseOrderItem)
class PurchaseOrderItemAdmin(admin.ModelAdmin):
    """Admin for PurchaseOrderItem model."""
    list_display = ('purchase_order', 'product', 'quantity_ordered', 'quantity_received', 'remaining_quantity', 'unit_price', 'total_price', 'is_complete')
    list_filter = ('purchase_order__status', 'product__category', 'created_at')
    search_fields = ('purchase_order__order_number', 'product__name', 'product__sku')
    readonly_fields = ('id', 'created_at', 'updated_at', 'total_price', 'remaining_quantity', 'is_complete')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Order Information', {
            'fields': ('purchase_order', 'product')
        }),
        ('Quantities', {
            'fields': ('quantity_ordered', 'quantity_received', 'remaining_quantity')
        }),
        ('Pricing', {
            'fields': ('unit_price', 'total_price')
        }),
        ('Status', {
            'fields': ('is_complete',)
        }),
        ('Notes', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def remaining_quantity(self, obj):
        """Display remaining quantity."""
        remaining = obj.remaining_quantity
        if remaining > 0:
            return format_html('<span style="color: orange;">{}</span>', remaining)
        else:
            return format_html('<span style="color: green;">0</span>')
    remaining_quantity.short_description = 'Remaining'

    def is_complete(self, obj):
        """Display completion status."""
        if obj.is_complete:
            return format_html('<span style="color: green;">✓ Complete</span>')
        else:
            return format_html('<span style="color: orange;">○ Pending</span>')
    is_complete.short_description = 'Complete'

    def get_queryset(self, request):
        """Optimize queryset with related data."""
        return super().get_queryset(request).select_related('purchase_order', 'product', 'purchase_order__supplier', 'purchase_order__warehouse')

    actions = ['receive_quantities']

    def receive_quantities(self, request, queryset):
        """Receive quantities for selected items."""
        # This is a placeholder action - you can implement quantity receiving logic here
        count = queryset.count()
        self.message_user(request, f'{count} items selected for quantity receiving.')
    receive_quantities.short_description = "Receive quantities for selected items"
