import { useQuery, useMutation, useQueryClient, UseQueryOptions, UseMutationOptions } from '@tanstack/react-query';
import { toast } from 'react-hot-toast';
import { handleApiError } from '@/services/api';
import { apiEndpoints } from '@/services/endpoints';
import {
  Category,
  Product,
  Warehouse,
  Inventory,
  StockMovement,
  Supplier,
  PurchaseOrder,
  StockAlert,
  AlertRule,
  AlertNotification,
  DashboardSummary,
  ApiResponse,
  CreateProductForm,
  CreateInventoryForm,
  CreatePurchaseOrderForm,
  InventoryFilters,
  ProductFilters,
  PurchaseOrderFilters,
} from '@/types';

// Generic error handler
const handleError = (error: any) => {
  const apiError = handleApiError(error);
  toast.error(apiError.detail || 'An error occurred');
  return apiError;
};

// Categories
export const useCategories = (params?: any, options?: UseQueryOptions<ApiResponse<Category>>) => {
  return useQuery({
    queryKey: ['categories', params],
    queryFn: () => apiEndpoints.categories.getAll(params),
    ...options,
  });
};

export const useCategory = (id: string, options?: UseQueryOptions<Category>) => {
  return useQuery({
    queryKey: ['categories', id],
    queryFn: () => apiEndpoints.categories.getById(id),
    enabled: !!id,
    ...options,
  });
};

export const useCategoryProducts = (id: string, params?: any, options?: UseQueryOptions<ApiResponse<Product>>) => {
  return useQuery({
    queryKey: ['categories', id, 'products', params],
    queryFn: () => apiEndpoints.categories.getProducts(id, params),
    enabled: !!id,
    ...options,
  });
};

export const useCreateCategory = (options?: UseMutationOptions<Category, any, Partial<Category>>) => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (data: Partial<Category>) => apiEndpoints.categories.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['categories'] });
      toast.success('Category created successfully');
    },
    onError: handleError,
    ...options,
  });
};

export const useUpdateCategory = (options?: UseMutationOptions<Category, any, { id: string; data: Partial<Category> }>) => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<Category> }) => 
      apiEndpoints.categories.update(id, data),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: ['categories'] });
      queryClient.invalidateQueries({ queryKey: ['categories', id] });
      toast.success('Category updated successfully');
    },
    onError: handleError,
    ...options,
  });
};

export const useDeleteCategory = (options?: UseMutationOptions<void, any, string>) => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (id: string) => {
      await apiEndpoints.categories.delete(id);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['categories'] });
      toast.success('Category deleted successfully');
    },
    onError: handleError,
    ...options,
  });
};

// Products
export const useProducts = (params?: ProductFilters, options?: UseQueryOptions<ApiResponse<Product>>) => {
  return useQuery({
    queryKey: ['products', params],
    queryFn: () => apiEndpoints.products.getAll(params),
    ...options,
  });
};

export const useProduct = (id: string, options?: UseQueryOptions<Product>) => {
  return useQuery({
    queryKey: ['products', id],
    queryFn: () => apiEndpoints.products.getById(id),
    enabled: !!id,
    ...options,
  });
};

export const useCreateProduct = (options?: UseMutationOptions<Product, any, CreateProductForm>) => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (data: CreateProductForm) => apiEndpoints.products.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['products'] });
      toast.success('Product created successfully');
    },
    onError: handleError,
    ...options,
  });
};

export const useUpdateProduct = (options?: UseMutationOptions<Product, any, { id: string; data: Partial<Product> }>) => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<Product> }) => 
      apiEndpoints.products.update(id, data),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: ['products'] });
      queryClient.invalidateQueries({ queryKey: ['products', id] });
      toast.success('Product updated successfully');
    },
    onError: handleError,
    ...options,
  });
};

export const useDeleteProduct = (options?: UseMutationOptions<void, any, string>) => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (id: string) => {
      await apiEndpoints.products.delete(id);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['products'] });
      toast.success('Product deleted successfully');
    },
    onError: handleError,
    ...options,
  });
};

// Warehouses
export const useWarehouses = (params?: any, options?: UseQueryOptions<ApiResponse<Warehouse>>) => {
  return useQuery({
    queryKey: ['warehouses', params],
    queryFn: () => apiEndpoints.warehouses.getAll(params),
    ...options,
  });
};

export const useWarehouse = (id: string, options?: UseQueryOptions<Warehouse>) => {
  return useQuery({
    queryKey: ['warehouses', id],
    queryFn: () => apiEndpoints.warehouses.getById(id),
    enabled: !!id,
    ...options,
  });
};

export const useCreateWarehouse = (options?: UseMutationOptions<Warehouse, any, Partial<Warehouse>>) => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (data: Partial<Warehouse>) => apiEndpoints.warehouses.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['warehouses'] });
      toast.success('Warehouse created successfully');
    },
    onError: handleError,
    ...options,
  });
};

export const useUpdateWarehouse = (options?: UseMutationOptions<Warehouse, any, { id: string; data: Partial<Warehouse> }>) => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<Warehouse> }) => 
      apiEndpoints.warehouses.update(id, data),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: ['warehouses'] });
      queryClient.invalidateQueries({ queryKey: ['warehouses', id] });
      toast.success('Warehouse updated successfully');
    },
    onError: handleError,
    ...options,
  });
};

export const useDeleteWarehouse = (options?: UseMutationOptions<void, any, string>) => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (id: string) => {
      await apiEndpoints.warehouses.delete(id);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['warehouses'] });
      toast.success('Warehouse deleted successfully');
    },
    onError: handleError,
    ...options,
  });
};

// Inventory
export const useInventory = (params?: InventoryFilters, options?: UseQueryOptions<ApiResponse<Inventory>>) => {
  return useQuery({
    queryKey: ['inventory', params],
    queryFn: () => apiEndpoints.inventory.getAll(params),
    ...options,
  });
};

export const useInventoryItem = (id: string, options?: UseQueryOptions<Inventory>) => {
  return useQuery({
    queryKey: ['inventory', id],
    queryFn: () => apiEndpoints.inventory.getById(id),
    enabled: !!id,
    ...options,
  });
};

export const useLowStockInventory = (params?: any, options?: UseQueryOptions<ApiResponse<Inventory>>) => {
  return useQuery({
    queryKey: ['inventory', 'low-stock', params],
    queryFn: () => apiEndpoints.inventory.getLowStock(params),
    ...options,
  });
};

export const useOutOfStockInventory = (params?: any, options?: UseQueryOptions<ApiResponse<Inventory>>) => {
  return useQuery({
    queryKey: ['inventory', 'out-of-stock', params],
    queryFn: () => apiEndpoints.inventory.getOutOfStock(params),
    ...options,
  });
};

export const useCreateInventory = (options?: UseMutationOptions<Inventory, any, CreateInventoryForm>) => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (data: CreateInventoryForm) => apiEndpoints.inventory.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['inventory'] });
      toast.success('Inventory item created successfully');
    },
    onError: handleError,
    ...options,
  });
};

export const useUpdateInventory = (options?: UseMutationOptions<Inventory, any, { id: string; data: Partial<Inventory> }>) => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<Inventory> }) => 
      apiEndpoints.inventory.update(id, data),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: ['inventory'] });
      queryClient.invalidateQueries({ queryKey: ['inventory', id] });
      toast.success('Inventory item updated successfully');
    },
    onError: handleError,
    ...options,
  });
};

export const useAdjustInventoryQuantity = (options?: UseMutationOptions<any, any, { id: string; quantity: number; movement_type: string; notes?: string }>) => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ id, quantity, movement_type: _movement_type, notes }: { id: string; quantity: number; movement_type: string; notes?: string }) => 
      apiEndpoints.inventory.adjust(id, { quantity, notes }),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: ['inventory'] });
      queryClient.invalidateQueries({ queryKey: ['inventory', id] });
      queryClient.invalidateQueries({ queryKey: ['stock-movements'] });
      toast.success('Inventory quantity adjusted successfully');
    },
    onError: handleError,
    ...options,
  });
};

// Stock Movements
export const useStockMovements = (params?: any, options?: UseQueryOptions<ApiResponse<StockMovement>>) => {
  return useQuery({
    queryKey: ['stock-movements', params],
    queryFn: () => apiEndpoints.stockMovements.getAll(params),
    ...options,
  });
};

// Suppliers
export const useSuppliers = (params?: any, options?: UseQueryOptions<ApiResponse<Supplier>>) => {
  return useQuery({
    queryKey: ['suppliers', params],
    queryFn: () => apiEndpoints.suppliers.getAll(params),
    ...options,
  });
};

export const useSupplier = (id: string, options?: UseQueryOptions<Supplier>) => {
  return useQuery({
    queryKey: ['suppliers', id],
    queryFn: () => apiEndpoints.suppliers.getById(id),
    enabled: !!id,
    ...options,
  });
};

export const useCreateSupplier = (options?: UseMutationOptions<Supplier, any, Partial<Supplier>>) => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (data: Partial<Supplier>) => apiEndpoints.suppliers.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['suppliers'] });
      toast.success('Supplier created successfully');
    },
    onError: handleError,
    ...options,
  });
};

export const useUpdateSupplier = (options?: UseMutationOptions<Supplier, any, { id: string; data: Partial<Supplier> }>) => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<Supplier> }) => 
      apiEndpoints.suppliers.update(id, data),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: ['suppliers'] });
      queryClient.invalidateQueries({ queryKey: ['suppliers', id] });
      toast.success('Supplier updated successfully');
    },
    onError: handleError,
    ...options,
  });
};

export const useDeleteSupplier = (options?: UseMutationOptions<void, any, string>) => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (id: string) => {
      await apiEndpoints.suppliers.delete(id);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['suppliers'] });
      toast.success('Supplier deleted successfully');
    },
    onError: handleError,
    ...options,
  });
};

// Purchase Orders
export const usePurchaseOrders = (params?: PurchaseOrderFilters, options?: UseQueryOptions<ApiResponse<PurchaseOrder>>) => {
  return useQuery({
    queryKey: ['purchase-orders', params],
    queryFn: () => apiEndpoints.purchaseOrders.getAll(params),
    ...options,
  });
};

export const usePurchaseOrder = (id: string, options?: UseQueryOptions<PurchaseOrder>) => {
  return useQuery({
    queryKey: ['purchase-orders', id],
    queryFn: () => apiEndpoints.purchaseOrders.getById(id),
    enabled: !!id,
    ...options,
  });
};

export const usePendingPurchaseOrders = (params?: any, options?: UseQueryOptions<ApiResponse<PurchaseOrder>>) => {
  return useQuery({
    queryKey: ['purchase-orders', 'pending', params],
    queryFn: () => apiEndpoints.purchaseOrders.getPending(params),
    ...options,
  });
};

export const useCreatePurchaseOrder = (options?: UseMutationOptions<PurchaseOrder, any, CreatePurchaseOrderForm>) => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (data: CreatePurchaseOrderForm) => apiEndpoints.purchaseOrders.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['purchase-orders'] });
      toast.success('Purchase order created successfully');
    },
    onError: handleError,
    ...options,
  });
};

export const useApprovePurchaseOrder = (options?: UseMutationOptions<any, any, { id: string; notes?: string }>) => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ id, notes }: { id: string; notes?: string }) => 
      apiEndpoints.purchaseOrders.approve(id, { notes }),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: ['purchase-orders'] });
      queryClient.invalidateQueries({ queryKey: ['purchase-orders', id] });
      toast.success('Purchase order approved successfully');
    },
    onError: handleError,
    ...options,
  });
};

// Stock Alerts
export const useStockAlerts = (params?: any, options?: UseQueryOptions<ApiResponse<StockAlert>>) => {
  return useQuery({
    queryKey: ['stock-alerts', params],
    queryFn: () => apiEndpoints.stockAlerts.getAll(params),
    ...options,
  });
};

export const useActiveStockAlerts = (params?: any, options?: UseQueryOptions<ApiResponse<StockAlert>>) => {
  return useQuery({
    queryKey: ['stock-alerts', 'active', params],
    queryFn: () => apiEndpoints.stockAlerts.getActive(params),
    ...options,
  });
};

export const useResolveStockAlert = (options?: UseMutationOptions<any, any, { id: string; resolution_notes?: string }>) => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ id, resolution_notes }: { id: string; resolution_notes?: string }) => 
      apiEndpoints.stockAlerts.resolve(id, { resolution_notes }),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: ['stock-alerts'] });
      queryClient.invalidateQueries({ queryKey: ['stock-alerts', id] });
      toast.success('Stock alert resolved successfully');
    },
    onError: handleError,
    ...options,
  });
};

// Alert Rules
export const useAlertRules = (params?: any, options?: UseQueryOptions<ApiResponse<AlertRule>>) => {
  return useQuery({
    queryKey: ['alert-rules', params],
    queryFn: () => apiEndpoints.alertRules.getAll(params),
    ...options,
  });
};

export const useCreateAlertRule = (options?: UseMutationOptions<AlertRule, any, Partial<AlertRule>>) => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (data: Partial<AlertRule>) => apiEndpoints.alertRules.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['alert-rules'] });
      toast.success('Alert rule created successfully');
    },
    onError: handleError,
    ...options,
  });
};

// Alert Notifications
export const useAlertNotifications = (params?: any, options?: UseQueryOptions<ApiResponse<AlertNotification>>) => {
  return useQuery({
    queryKey: ['alert-notifications', params],
    queryFn: () => apiEndpoints.alertNotifications.getAll(params),
    ...options,
  });
};

// Dashboard
export const useDashboardSummary = (options?: UseQueryOptions<DashboardSummary>) => {
  return useQuery({
    queryKey: ['dashboard', 'summary'],
    queryFn: () => apiEndpoints.dashboard.getSummary(),
    refetchInterval: 30000, // Refetch every 30 seconds
    ...options,
  });
};

export const useDashboardLowStock = (params?: any, options?: UseQueryOptions<ApiResponse<Inventory>>) => {
  return useQuery({
    queryKey: ['dashboard', 'low-stock', params],
    queryFn: () => apiEndpoints.dashboard.getLowStock(params),
    refetchInterval: 60000, // Refetch every minute
    ...options,
  });
};

export const useDashboardRecentMovements = (params?: any, options?: UseQueryOptions<ApiResponse<StockMovement>>) => {
  return useQuery({
    queryKey: ['dashboard', 'recent-movements', params],
    queryFn: () => apiEndpoints.dashboard.getRecentMovements(params),
    refetchInterval: 30000, // Refetch every 30 seconds
    ...options,
  });
};

export const useDashboardPendingOrders = (params?: any, options?: UseQueryOptions<ApiResponse<PurchaseOrder>>) => {
  return useQuery({
    queryKey: ['dashboard', 'pending-orders', params],
    queryFn: () => apiEndpoints.dashboard.getPendingOrders(params),
    refetchInterval: 60000, // Refetch every minute
    ...options,
  });
}; 