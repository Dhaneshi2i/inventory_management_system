// Base types
export interface BaseEntity {
  id: string;
  created_at: string;
  updated_at: string;
}

// User types
export interface User {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  is_active: boolean;
  date_joined: string;
}

// Authentication types
export interface LoginCredentials {
  username: string;
  password: string;
}

export interface AuthTokens {
  access: string;
  refresh: string;
}

export interface AuthResponse {
  access: string;
  refresh: string;
}

// Category types
export interface Category extends BaseEntity {
  name: string;
  description: string;
  product_count: number;
  total_value: string;
}

// Product types
export interface Product extends BaseEntity {
  name: string;
  sku: string;
  category: Category;
  description: string;
  unit_price: string;
  specifications: Record<string, any>;
  total_value: string;
  stock_status: 'in_stock' | 'low_stock' | 'out_of_stock';
}

// Warehouse types
export interface Warehouse extends BaseEntity {
  name: string;
  address: string;
  capacity: number;
  manager: string;
  contact_email: string;
  contact_phone: string;
  is_active: boolean;
  current_utilization: string;
  available_capacity: number;
  inventory_count: number;
  total_inventory_value: string;
}

// Inventory types
export interface Inventory extends BaseEntity {
  product: {
    id: string;
    name: string;
    sku: string;
  };
  warehouse: {
    id: string;
    name: string;
  };
  quantity: number;
  reserved_quantity: number;
  reorder_point: number;
  max_stock_level: number;
  available_quantity: number;
  is_low_stock: boolean;
  is_out_of_stock: boolean;
  stock_value: string;
  stock_status: 'in_stock' | 'low_stock' | 'out_of_stock';
  last_updated: string;
}

// Stock Movement types
export interface StockMovement extends BaseEntity {
  product: {
    id: string;
    name: string;
    sku: string;
  };
  warehouse: {
    id: string;
    name: string;
  };
  movement_type: 'in' | 'out' | 'transfer' | 'adjustment';
  quantity: number;
  reference_type: string | null;
  reference_id: number | null;
  notes: string;
  movement_value: string;
}

// Supplier types
export interface Supplier extends BaseEntity {
  name: string;
  contact_person: string;
  email: string;
  phone: string;
  address: string;
  website: string;
  tax_id: string;
  payment_terms: string;
  is_active: boolean;
  total_orders: number;
  total_order_value: string;
  average_order_value: string;
  last_order_date: string;
}

// Purchase Order types
export interface PurchaseOrder extends BaseEntity {
  order_number: string;
  supplier: {
    id: string;
    name: string;
  };
  warehouse: {
    id: string;
    name: string;
  };
  status: 'draft' | 'pending' | 'approved' | 'ordered' | 'received' | 'cancelled';
  order_date: string;
  expected_date: string;
  received_date: string | null;
  total_amount: string;
  notes: string;
  approved_by: User | null;
  approved_at: string | null;
  item_count: number;
  total_quantity: number;
  received_quantity: number;
  is_complete: boolean;
  completion_percentage: string;
  days_until_expected: number;
}

// Purchase Order Item types
export interface PurchaseOrderItem extends BaseEntity {
  purchase_order: {
    id: string;
    order_number: string;
  };
  product: {
    id: string;
    name: string;
    sku: string;
  };
  quantity: number;
  unit_price: string;
  total_price: string;
  received_quantity: number;
  remaining_quantity: number;
  is_complete: boolean;
  completion_percentage: string;
}

// Stock Alert types
export interface StockAlert extends BaseEntity {
  product: {
    id: string;
    name: string;
    sku: string;
  };
  warehouse: {
    id: string;
    name: string;
  };
  alert_type: 'low_stock' | 'out_of_stock' | 'overstock';
  severity: 'low' | 'medium' | 'high' | 'critical';
  message: string;
  threshold_value: number;
  current_value: number;
  is_resolved: boolean;
  resolved_at: string | null;
  resolved_by: User | null;
  resolution_notes: string | null;
  is_active: boolean;
  duration: number | null;
  severity_color: string;
}

// Alert Rule types
export interface AlertRule extends BaseEntity {
  name: string;
  description: string;
  alert_type: 'low_stock' | 'out_of_stock' | 'overstock';
  severity: 'low' | 'medium' | 'high' | 'critical';
  threshold_value: number;
  is_active: boolean;
  notification_channels: string[];
  created_by: User;
}

// Alert Notification types
export interface AlertNotification extends BaseEntity {
  alert: StockAlert;
  notification_type: 'email' | 'dashboard' | 'sms';
  recipient: string;
  subject: string;
  message: string;
  is_sent: boolean;
  sent_at: string | null;
  error_message: string | null;
}

// Report types
export interface Report extends BaseEntity {
  name: string;
  report_type: string;
  description: string;
  format: 'json' | 'csv' | 'pdf' | 'excel';
  data: Record<string, any>;
  generated_by: User;
  is_scheduled: boolean;
  file_path: string | null;
}

// Dashboard Widget types
export interface DashboardWidget extends BaseEntity {
  name: string;
  widget_type: 'chart' | 'metric' | 'table' | 'list';
  title: string;
  description: string;
  configuration: Record<string, any>;
  position: number;
  is_active: boolean;
  refresh_interval: number;
}

// Dashboard Summary types
export interface DashboardSummary {
  total_products: number;
  total_inventory_value: string;
  low_stock_items: number;
  out_of_stock_items: number;
  total_warehouses: number;
  active_alerts: number;
  pending_orders: number;
  recent_movements: Array<{
    id: string;
    product: { id: string; name: string; sku: string };
    warehouse: { id: string; name: string };
    movement_type: string;
    quantity: number;
    created_at: string;
  }>;
  warehouse_utilization: Array<{
    warehouse: string;
    utilization: number;
    capacity: number;
    used: number;
  }>;
  top_products: Array<{
    product: string;
    total_value: string;
    quantity: number;
  }>;
  alert_summary: {
    low_stock: number;
    out_of_stock: number;
    critical: number;
  };
}

// API Response types
export interface ApiResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export interface ApiError {
  detail?: string;
  error?: string;
  details?: Record<string, string[]>;
}

// Form types
export interface CreateProductForm {
  name: string;
  sku: string;
  category_id: string;
  description: string;
  unit_price: string;
  specifications: Record<string, any>;
}

export interface CreateInventoryForm {
  product_id: string;
  warehouse_id: string;
  quantity: number;
  reorder_point: number;
  max_stock_level: number;
}

export interface CreatePurchaseOrderForm {
  supplier_id: string;
  warehouse_id: string;
  expected_date: string;
  notes: string;
  items: Array<{
    product_id: string;
    quantity: number;
    unit_price: string;
  }>;
}

// Filter and Search types
export interface PaginationParams {
  page?: number;
  page_size?: number;
}

export interface SearchParams extends PaginationParams {
  search?: string;
  ordering?: string;
}

export interface InventoryFilters extends SearchParams {
  warehouse_id?: string;
  product_id?: string;
  is_low_stock?: boolean;
  is_out_of_stock?: boolean;
}

export interface ProductFilters extends SearchParams {
  category_id?: string;
  stock_status?: string;
}

export interface PurchaseOrderFilters extends SearchParams {
  supplier_id?: string;
  warehouse_id?: string;
  status?: string;
  date_from?: string;
  date_to?: string;
}

// UI Component types
export interface TableColumn<T> {
  key: keyof T | string;
  label: string;
  sortable?: boolean;
  render?: (value: any, item: T) => React.ReactNode;
  width?: string;
}

export interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  children: React.ReactNode;
  size?: 'sm' | 'md' | 'lg' | 'xl' | '2xl';
}

export interface ToastProps {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  title: string;
  message?: string;
  duration?: number;
}

// Chart types
export interface ChartData {
  name: string;
  value: number;
  color?: string;
}

export interface ChartConfig {
  type: 'bar' | 'line' | 'pie' | 'area';
  data: ChartData[];
  height?: number;
  width?: number;
} 