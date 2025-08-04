import { apiService } from './api';
import {
  Category,
  Product,
  Warehouse,
  Inventory,
  StockMovement,
  Supplier,
  PurchaseOrder,
  PurchaseOrderItem,
  StockAlert,
  AlertRule,
  AlertNotification,
  Report,
  DashboardWidget,
  DashboardSummary,
  ApiResponse,
  CreateProductForm,
  CreateInventoryForm,
  CreatePurchaseOrderForm,
  InventoryFilters,
  ProductFilters,
  PurchaseOrderFilters,
} from '@/types';

// Categories
export const categoryService = {
  getAll: (params?: any) => apiService.get<ApiResponse<Category>>('/categories/', { params }),
  getById: (id: string) => apiService.get<Category>(`/categories/${id}/`),
  getProducts: (id: string, params?: any) => 
    apiService.get<ApiResponse<Product>>(`/categories/${id}/products/`, { params }),
  create: (data: Partial<Category>) => apiService.post<Category>('/categories/', data),
  update: (id: string, data: Partial<Category>) => apiService.put<Category>(`/categories/${id}/`, data),
  delete: (id: string) => apiService.delete(`/categories/${id}/`),
};

// Products
export const productService = {
  getAll: (params?: ProductFilters) => apiService.get<ApiResponse<Product>>('/products/', { params }),
  getById: (id: string) => apiService.get<Product>(`/products/${id}/`),
  create: (data: CreateProductForm) => apiService.post<Product>('/products/', data),
  update: (id: string, data: Partial<Product>) => apiService.put<Product>(`/products/${id}/`, data),
  delete: (id: string) => apiService.delete(`/products/${id}/`),
  export: (params?: any) => apiService.get('/products/export/', { params, responseType: 'blob' }),
};

// Warehouses
export const warehouseService = {
  getAll: (params?: any) => apiService.get<ApiResponse<Warehouse>>('/warehouses/', { params }),
  getById: (id: string) => apiService.get<Warehouse>(`/warehouses/${id}/`),
  create: (data: Partial<Warehouse>) => apiService.post<Warehouse>('/warehouses/', data),
  update: (id: string, data: Partial<Warehouse>) => apiService.put<Warehouse>(`/warehouses/${id}/`, data),
  delete: (id: string) => apiService.delete(`/warehouses/${id}/`),
};

// Inventory
export const inventoryService = {
  getAll: (params?: InventoryFilters) => apiService.get<ApiResponse<Inventory>>('/inventory/', { params }),
  getById: (id: string) => apiService.get<Inventory>(`/inventory/${id}/`),
  getLowStock: (params?: any) => apiService.get<ApiResponse<Inventory>>('/inventory/low_stock/', { params }),
  getOutOfStock: (params?: any) => apiService.get<ApiResponse<Inventory>>('/inventory/out_of_stock/', { params }),
  create: (data: CreateInventoryForm) => apiService.post<Inventory>('/inventory/', data),
  update: (id: string, data: Partial<Inventory>) => apiService.put<Inventory>(`/inventory/${id}/`, data),
  delete: (id: string) => apiService.delete(`/inventory/${id}/`),
  adjustQuantity: (id: string, data: { quantity: number; movement_type: string; notes?: string }) =>
    apiService.post(`/inventory/${id}/adjust_quantity/`, data),
  bulkUpdate: (data: { items: Array<{ id: string; quantity: number }> }) =>
    apiService.post('/inventory/bulk_update/', data),
  export: (params?: any) => apiService.get('/inventory/export/', { params, responseType: 'blob' }),
};

// Stock Movements
export const stockMovementService = {
  getAll: (params?: any) => apiService.get<ApiResponse<StockMovement>>('/stock-movements/', { params }),
  getById: (id: string) => apiService.get<StockMovement>(`/stock-movements/${id}/`),
  create: (data: Partial<StockMovement>) => apiService.post<StockMovement>('/stock-movements/', data),
  update: (id: string, data: Partial<StockMovement>) => 
    apiService.put<StockMovement>(`/stock-movements/${id}/`, data),
  delete: (id: string) => apiService.delete(`/stock-movements/${id}/`),
  export: (params?: any) => apiService.get('/stock-movements/export/', { params, responseType: 'blob' }),
};

// Suppliers
export const supplierService = {
  getAll: (params?: any) => apiService.get<ApiResponse<Supplier>>('/suppliers/', { params }),
  getById: (id: string) => apiService.get<Supplier>(`/suppliers/${id}/`),
  create: (data: Partial<Supplier>) => apiService.post<Supplier>('/suppliers/', data),
  update: (id: string, data: Partial<Supplier>) => apiService.put<Supplier>(`/suppliers/${id}/`, data),
  delete: (id: string) => apiService.delete(`/suppliers/${id}/`),
  getOrders: (id: string, params?: any) => 
    apiService.get<ApiResponse<PurchaseOrder>>(`/suppliers/${id}/orders/`, { params }),
};

// Purchase Orders
export const purchaseOrderService = {
  getAll: (params?: PurchaseOrderFilters) => 
    apiService.get<ApiResponse<PurchaseOrder>>('/purchase-orders/', { params }),
  getById: (id: string) => apiService.get<PurchaseOrder>(`/purchase-orders/${id}/`),
  getPending: (params?: any) => apiService.get<ApiResponse<PurchaseOrder>>('/purchase-orders/pending/', { params }),
  create: (data: CreatePurchaseOrderForm) => apiService.post<PurchaseOrder>('/purchase-orders/', data),
  update: (id: string, data: Partial<PurchaseOrder>) => 
    apiService.put<PurchaseOrder>(`/purchase-orders/${id}/`, data),
  delete: (id: string) => apiService.delete(`/purchase-orders/${id}/`),
  approve: (id: string, data?: { notes?: string }) => 
    apiService.post(`/purchase-orders/${id}/approve/`, data),
  receive: (id: string, data: { received_items: Array<{ item_id: string; received_quantity: number }> }) =>
    apiService.post(`/purchase-orders/${id}/receive/`, data),
  cancel: (id: string, data?: { notes?: string }) => 
    apiService.post(`/purchase-orders/${id}/cancel/`, data),
  export: (params?: any) => apiService.get('/purchase-orders/export/', { params, responseType: 'blob' }),
};

// Purchase Order Items
export const purchaseOrderItemService = {
  getAll: (params?: any) => apiService.get<ApiResponse<PurchaseOrderItem>>('/purchase-order-items/', { params }),
  getById: (id: string) => apiService.get<PurchaseOrderItem>(`/purchase-order-items/${id}/`),
  create: (data: Partial<PurchaseOrderItem>) => apiService.post<PurchaseOrderItem>('/purchase-order-items/', data),
  update: (id: string, data: Partial<PurchaseOrderItem>) => 
    apiService.put<PurchaseOrderItem>(`/purchase-order-items/${id}/`, data),
  delete: (id: string) => apiService.delete(`/purchase-order-items/${id}/`),
};

// Stock Alerts
export const stockAlertService = {
  getAll: (params?: any) => apiService.get<ApiResponse<StockAlert>>('/stock-alerts/', { params }),
  getById: (id: string) => apiService.get<StockAlert>(`/stock-alerts/${id}/`),
  getActive: (params?: any) => apiService.get<ApiResponse<StockAlert>>('/stock-alerts/active/', { params }),
  create: (data: Partial<StockAlert>) => apiService.post<StockAlert>('/stock-alerts/', data),
  update: (id: string, data: Partial<StockAlert>) => apiService.put<StockAlert>(`/stock-alerts/${id}/`, data),
  delete: (id: string) => apiService.delete(`/stock-alerts/${id}/`),
  resolve: (id: string, data: { resolution_notes?: string }) => 
    apiService.post(`/stock-alerts/${id}/resolve/`, data),
};

// Alert Rules
export const alertRuleService = {
  getAll: (params?: any) => apiService.get<ApiResponse<AlertRule>>('/alert-rules/', { params }),
  getById: (id: string) => apiService.get<AlertRule>(`/alert-rules/${id}/`),
  create: (data: Partial<AlertRule>) => apiService.post<AlertRule>('/alert-rules/', data),
  update: (id: string, data: Partial<AlertRule>) => apiService.put<AlertRule>(`/alert-rules/${id}/`, data),
  delete: (id: string) => apiService.delete(`/alert-rules/${id}/`),
};

// Alert Notifications
export const alertNotificationService = {
  getAll: (params?: any) => apiService.get<ApiResponse<AlertNotification>>('/alert-notifications/', { params }),
  getById: (id: string) => apiService.get<AlertNotification>(`/alert-notifications/${id}/`),
  create: (data: Partial<AlertNotification>) => apiService.post<AlertNotification>('/alert-notifications/', data),
  update: (id: string, data: Partial<AlertNotification>) => 
    apiService.put<AlertNotification>(`/alert-notifications/${id}/`, data),
  delete: (id: string) => apiService.delete(`/alert-notifications/${id}/`),
};

// Reports
export const reportService = {
  getAll: (params?: any) => apiService.get<ApiResponse<Report>>('/reports/', { params }),
  getById: (id: string) => apiService.get<Report>(`/reports/${id}/`),
  create: (data: Partial<Report>) => apiService.post<Report>('/reports/', data),
  update: (id: string, data: Partial<Report>) => apiService.put<Report>(`/reports/${id}/`, data),
  delete: (id: string) => apiService.delete(`/reports/${id}/`),
  generate: (reportType: string, params?: any) => 
    apiService.post(`/reports/generate/${reportType}/`, params),
  download: (id: string) => apiService.get(`/reports/${id}/download/`, { responseType: 'blob' }),
};

// Dashboard Widgets
export const dashboardWidgetService = {
  getAll: (params?: any) => apiService.get<ApiResponse<DashboardWidget>>('/dashboard-widgets/', { params }),
  getById: (id: string) => apiService.get<DashboardWidget>(`/dashboard-widgets/${id}/`),
  create: (data: Partial<DashboardWidget>) => apiService.post<DashboardWidget>('/dashboard-widgets/', data),
  update: (id: string, data: Partial<DashboardWidget>) => 
    apiService.put<DashboardWidget>(`/dashboard-widgets/${id}/`, data),
  delete: (id: string) => apiService.delete(`/dashboard-widgets/${id}/`),
};

// Dashboard
export const dashboardService = {
  getSummary: () => apiService.get<DashboardSummary>('/dashboard/summary/'),
  getLowStock: (params?: any) => apiService.get<ApiResponse<Inventory>>('/dashboard/low_stock/', { params }),
  getRecentMovements: (params?: any) => 
    apiService.get<ApiResponse<StockMovement>>('/dashboard/recent_movements/', { params }),
  getPendingOrders: (params?: any) => 
    apiService.get<ApiResponse<PurchaseOrder>>('/dashboard/pending_orders/', { params }),
};

// Export all services
export const apiEndpoints = {
  categories: categoryService,
  products: productService,
  warehouses: warehouseService,
  inventory: inventoryService,
  stockMovements: stockMovementService,
  suppliers: supplierService,
  purchaseOrders: purchaseOrderService,
  purchaseOrderItems: purchaseOrderItemService,
  stockAlerts: stockAlertService,
  alertRules: alertRuleService,
  alertNotifications: alertNotificationService,
  reports: reportService,
  dashboardWidgets: dashboardWidgetService,
  dashboard: dashboardService,
}; 