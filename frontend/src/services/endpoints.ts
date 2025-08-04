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

// API Endpoints configuration
export const apiEndpoints = {
  // Categories
  categories: {
    getAll: (params?: any) => apiService.get<ApiResponse<Category>>('/api/v1/categories/', { params }),
    getById: (id: string) => apiService.get<Category>(`/api/v1/api/v1/categories/${id}/`),
    create: (data: Partial<Category>) => apiService.post<Category>('/api/v1/categories/', data),
    update: (id: string, data: Partial<Category>) => apiService.patch<Category>(`/api/v1/categories/${id}/`, data),
    delete: (id: string) => apiService.delete(`/api/v1/categories/${id}/`),
    getProducts: (id: string, params?: any) => apiService.get<ApiResponse<Product>>(`/api/v1/categories/${id}/products/`, { params }),
  },

  // Products
  products: {
    getAll: (params?: ProductFilters) => apiService.get<ApiResponse<Product>>('/api/v1/products/', { params }),
    getById: (id: string) => apiService.get<Product>(`/api/v1/products/${id}/`),
    create: (data: CreateProductForm) => apiService.post<Product>('/api/v1/products/', data),
    update: (id: string, data: Partial<Product>) => apiService.patch<Product>(`/api/v1/products/${id}/`, data),
    delete: (id: string) => apiService.delete(`/api/v1/products/${id}/`),
    getInventory: (id: string, params?: any) => apiService.get<ApiResponse<Inventory>>(`/api/v1/products/${id}/inventory/`, { params }),
  },

  // Warehouses
  warehouses: {
    getAll: (params?: any) => apiService.get<ApiResponse<Warehouse>>('/api/v1/warehouses/', { params }),
    getById: (id: string) => apiService.get<Warehouse>(`/api/v1/warehouses/${id}/`),
    create: (data: Partial<Warehouse>) => apiService.post<Warehouse>('/api/v1/warehouses/', data),
    update: (id: string, data: Partial<Warehouse>) => apiService.patch<Warehouse>(`/api/v1/warehouses/${id}/`, data),
    delete: (id: string) => apiService.delete(`/api/v1/warehouses/${id}/`),
    getInventory: (id: string, params?: any) => apiService.get<ApiResponse<Inventory>>(`/api/v1/warehouses/${id}/inventory/`, { params }),
    getUtilization: (id: string) => apiService.get<any>(`/api/v1/warehouses/${id}/utilization/`),
  },

  // Inventory
  inventory: {
    getAll: (params?: InventoryFilters) => apiService.get<ApiResponse<Inventory>>('/api/v1/inventory/', { params }),
    getById: (id: string) => apiService.get<Inventory>(`/api/v1/inventory/${id}/`),
    create: (data: CreateInventoryForm) => apiService.post<Inventory>('/api/v1/inventory/', data),
    update: (id: string, data: Partial<Inventory>) => apiService.patch<Inventory>(`/api/v1/inventory/${id}/`, data),
    delete: (id: string) => apiService.delete(`/api/v1/inventory/${id}/`),
    adjust: (id: string, data: { quantity: number; notes?: string }) => apiService.post(`/api/v1/inventory/${id}/adjust/`, data),
    transfer: (data: { from_warehouse_id: string; to_warehouse_id: string; product_id: string; quantity: number; notes?: string }) => 
      apiService.post('/api/v1/inventory/transfer/', data),
    getLowStock: (params?: any) => apiService.get<ApiResponse<Inventory>>('/api/v1/inventory/low-stock/', { params }),
    getOutOfStock: (params?: any) => apiService.get<ApiResponse<Inventory>>('/api/v1/inventory/out-of-stock/', { params }),
  },

  // Stock Movements
  stockMovements: {
    getAll: (params?: any) => apiService.get<ApiResponse<StockMovement>>('/api/v1/stock-movements/', { params }),
    getById: (id: string) => apiService.get<StockMovement>(`/api/v1/stock-movements/${id}/`),
    create: (data: Partial<StockMovement>) => apiService.post<StockMovement>('/api/v1/stock-movements/', data),
    getByProduct: (productId: string, params?: any) => apiService.get<ApiResponse<StockMovement>>(`/api/v1/stock-movements/?product_id=${productId}`, { params }),
    getByWarehouse: (warehouseId: string, params?: any) => apiService.get<ApiResponse<StockMovement>>(`/api/v1/stock-movements/?warehouse_id=${warehouseId}`, { params }),
  },

  // Suppliers
  suppliers: {
    getAll: (params?: any) => apiService.get<ApiResponse<Supplier>>('/api/v1/suppliers/', { params }),
    getById: (id: string) => apiService.get<Supplier>(`/api/v1/suppliers/${id}/`),
    create: (data: Partial<Supplier>) => apiService.post<Supplier>('/api/v1/suppliers/', data),
    update: (id: string, data: Partial<Supplier>) => apiService.patch<Supplier>(`/api/v1/suppliers/${id}/`, data),
    delete: (id: string) => apiService.delete(`/api/v1/suppliers/${id}/`),
    getOrders: (id: string, params?: any) => apiService.get<ApiResponse<PurchaseOrder>>(`/api/v1/suppliers/${id}/orders/`, { params }),
    getPerformance: (id: string) => apiService.get<any>(`/api/v1/suppliers/${id}/performance/`),
  },

  // Purchase Orders
  purchaseOrders: {
    getAll: (params?: PurchaseOrderFilters) => apiService.get<ApiResponse<PurchaseOrder>>('/api/v1/purchase-orders/', { params }),
    getById: (id: string) => apiService.get<PurchaseOrder>(`/api/v1/purchase-orders/${id}/`),
    create: (data: CreatePurchaseOrderForm) => apiService.post<PurchaseOrder>('/api/v1/purchase-orders/', data),
    update: (id: string, data: Partial<PurchaseOrder>) => apiService.patch<PurchaseOrder>(`/api/v1/purchase-orders/${id}/`, data),
    delete: (id: string) => apiService.delete(`/api/v1/purchase-orders/${id}/`),
    approve: (id: string, data?: { notes?: string }) => apiService.post(`/api/v1/purchase-orders/${id}/approve/`, data),
    receive: (id: string, data: { items: Array<{ item_id: string; received_quantity: number }> }) => 
      apiService.post(`/api/v1/purchase-orders/${id}/receive/`, data),
    getPending: (params?: any) => apiService.get<ApiResponse<PurchaseOrder>>('/api/v1/purchase-orders/pending/', { params }),
    getBySupplier: (supplierId: string, params?: any) => apiService.get<ApiResponse<PurchaseOrder>>(`/api/v1/purchase-orders/?supplier_id=${supplierId}`, { params }),
  },

  // Purchase Order Items
  purchaseOrderItems: {
    getAll: (params?: any) => apiService.get<ApiResponse<PurchaseOrderItem>>('/api/v1/purchase-order-items/', { params }),
    getById: (id: string) => apiService.get<PurchaseOrderItem>(`/api/v1/purchase-order-items/${id}/`),
    create: (data: Partial<PurchaseOrderItem>) => apiService.post<PurchaseOrderItem>('/api/v1/purchase-order-items/', data),
    update: (id: string, data: Partial<PurchaseOrderItem>) => apiService.patch<PurchaseOrderItem>(`/api/v1/purchase-order-items/${id}/`, data),
    delete: (id: string) => apiService.delete(`/api/v1/purchase-order-items/${id}/`),
    getByOrder: (orderId: string, params?: any) => apiService.get<ApiResponse<PurchaseOrderItem>>(`/api/v1/purchase-order-items/?purchase_order_id=${orderId}`, { params }),
  },

  // Stock Alerts
  stockAlerts: {
    getAll: (params?: any) => apiService.get<ApiResponse<StockAlert>>('/api/v1/stock-alerts/', { params }),
    getById: (id: string) => apiService.get<StockAlert>(`/api/v1/stock-alerts/${id}/`),
    create: (data: Partial<StockAlert>) => apiService.post<StockAlert>('/api/v1/stock-alerts/', data),
    update: (id: string, data: Partial<StockAlert>) => apiService.patch<StockAlert>(`/api/v1/stock-alerts/${id}/`, data),
    delete: (id: string) => apiService.delete(`/api/v1/stock-alerts/${id}/`),
    resolve: (id: string, data?: { resolution_notes?: string }) => apiService.post(`/api/v1/stock-alerts/${id}/resolve/`, data),
    getActive: (params?: any) => apiService.get<ApiResponse<StockAlert>>('/api/v1/stock-alerts/active/', { params }),
  },

  // Alert Rules
  alertRules: {
    getAll: (params?: any) => apiService.get<ApiResponse<AlertRule>>('/api/v1/alert-rules/', { params }),
    getById: (id: string) => apiService.get<AlertRule>(`/api/v1/alert-rules/${id}/`),
    create: (data: Partial<AlertRule>) => apiService.post<AlertRule>('/api/v1/alert-rules/', data),
    update: (id: string, data: Partial<AlertRule>) => apiService.patch<AlertRule>(`/api/v1/alert-rules/${id}/`, data),
    delete: (id: string) => apiService.delete(`/api/v1/alert-rules/${id}/`),
  },

  // Alert Notifications
  alertNotifications: {
    getAll: (params?: any) => apiService.get<ApiResponse<AlertNotification>>('/api/v1/alert-notifications/', { params }),
    getById: (id: string) => apiService.get<AlertNotification>(`/api/v1/alert-notifications/${id}/`),
    create: (data: Partial<AlertNotification>) => apiService.post<AlertNotification>('/api/v1/alert-notifications/', data),
    update: (id: string, data: Partial<AlertNotification>) => apiService.patch<AlertNotification>(`/api/v1/alert-notifications/${id}/`, data),
    delete: (id: string) => apiService.delete(`/api/v1/alert-notifications/${id}/`),
    getByAlert: (alertId: string, params?: any) => apiService.get<ApiResponse<AlertNotification>>(`/api/v1/alert-notifications/?alert_id=${alertId}`, { params }),
  },

  // Reports
  reports: {
    getAll: (params?: any) => apiService.get<ApiResponse<Report>>('/api/v1/reports/', { params }),
    getById: (id: string) => apiService.get<Report>(`/api/v1/reports/${id}/`),
    create: (data: Partial<Report>) => apiService.post<Report>('/api/v1/reports/', data),
    update: (id: string, data: Partial<Report>) => apiService.patch<Report>(`/api/v1/reports/${id}/`, data),
    delete: (id: string) => apiService.delete(`/api/v1/reports/${id}/`),
    generate: (type: string, params?: any) => apiService.post<Report>(`/api/v1/reports/generate/${type}/`, params),
    download: (id: string, format: string) => apiService.get(`/api/v1/reports/${id}/download/${format}/`),
  },

  // Dashboard Widgets
  dashboardWidgets: {
    getAll: (params?: any) => apiService.get<ApiResponse<DashboardWidget>>('/api/v1/dashboard-widgets/', { params }),
    getById: (id: string) => apiService.get<DashboardWidget>(`/api/v1/dashboard-widgets/${id}/`),
    create: (data: Partial<DashboardWidget>) => apiService.post<DashboardWidget>('/api/v1/dashboard-widgets/', data),
    update: (id: string, data: Partial<DashboardWidget>) => apiService.patch<DashboardWidget>(`/api/v1/dashboard-widgets/${id}/`, data),
    delete: (id: string) => apiService.delete(`/api/v1/dashboard-widgets/${id}/`),
  },

  // Dashboard
  dashboard: {
    getSummary: () => apiService.get<DashboardSummary>('/api/v1/dashboard/summary/'),
    getLowStock: (params?: any) => apiService.get<ApiResponse<Inventory>>('/api/v1/dashboard/low-stock/', { params }),
    getRecentMovements: (params?: any) => apiService.get<ApiResponse<StockMovement>>('/api/v1/dashboard/recent-movements/', { params }),
    getPendingOrders: (params?: any) => apiService.get<ApiResponse<PurchaseOrder>>('/api/v1/dashboard/pending-orders/', { params }),
    getMetrics: () => apiService.get<any>('/api/v1/dashboard/metrics/'),
    getCharts: (type: string, params?: any) => apiService.get<any>(`/api/v1/dashboard/charts/${type}/`, { params }),
  },
}; 