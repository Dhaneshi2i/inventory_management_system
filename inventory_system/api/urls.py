"""
API URL configuration for Inventory Management System.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views_v2 import (
    # Products
    CategoryViewSet,
    ProductViewSet,
    
    # Inventory
    WarehouseViewSet,
    InventoryViewSet,
    StockMovementViewSet,
    
    # Orders
    SupplierViewSet,
    PurchaseOrderViewSet,
    PurchaseOrderItemViewSet,
    
    # Alerts
    StockAlertViewSet,
    AlertRuleViewSet,
    AlertNotificationViewSet,
    
    # Reports
    ReportViewSet,
    DashboardWidgetViewSet,
    
    # Dashboard
    DashboardViewSet,
)

# Create router and register viewsets
router = DefaultRouter()

# Products
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'products', ProductViewSet, basename='product')

# Inventory
router.register(r'warehouses', WarehouseViewSet, basename='warehouse')
router.register(r'inventory', InventoryViewSet, basename='inventory')
router.register(r'stock-movements', StockMovementViewSet, basename='stock-movement')

# Orders
router.register(r'suppliers', SupplierViewSet, basename='supplier')
router.register(r'purchase-orders', PurchaseOrderViewSet, basename='purchase-order')
router.register(r'purchase-order-items', PurchaseOrderItemViewSet, basename='purchase-order-item')

# Alerts
router.register(r'stock-alerts', StockAlertViewSet, basename='stock-alert')
router.register(r'alert-rules', AlertRuleViewSet, basename='alert-rule')
router.register(r'alert-notifications', AlertNotificationViewSet, basename='alert-notification')

# Reports
router.register(r'reports', ReportViewSet, basename='report')
router.register(r'dashboard-widgets', DashboardWidgetViewSet, basename='dashboard-widget')

# Dashboard
router.register(r'dashboard', DashboardViewSet, basename='dashboard')

urlpatterns = [
    # Include router URLs
    path('', include(router.urls)),
    
    # Additional custom endpoints
    path('dashboard/summary/', DashboardViewSet.as_view({'get': 'summary'}), name='dashboard-summary'),
    path('dashboard/low-stock/', DashboardViewSet.as_view({'get': 'low_stock'}), name='dashboard-low-stock'),
    path('dashboard/recent-movements/', DashboardViewSet.as_view({'get': 'recent_movements'}), name='dashboard-recent-movements'),
    path('dashboard/pending-orders/', DashboardViewSet.as_view({'get': 'pending_orders'}), name='dashboard-pending-orders'),
    
    # API authentication
    path('auth/', include('rest_framework.urls')),
] 