# Inventory Management System - API Endpoints Reference

## 🔐 Authentication

### Get JWT Token
```http
POST /api/token/
Content-Type: application/json

{
  "username": "admin",
  "password": "admin123"
}
```

**Response:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### Refresh Token
```http
POST /api/token/refresh/
Content-Type: application/json

{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Response:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

---

## 📦 Products

### Get Categories
```http
GET /api/v1/categories/
Authorization: Bearer <token>
```

**Response:**
```json
{
  "count": 5,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": "1a68bd8d-6502-48de-b900-3695d9f22bf2",
      "name": "Electronics",
      "description": "Electronic devices and accessories",
      "product_count": 3,
      "total_value": "2999.97",
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    },
    {
      "id": "2b79ce9e-7613-59ef-c011-4706ea033cf3",
      "name": "Clothing",
      "description": "Apparel and fashion items",
      "product_count": 2,
      "total_value": "199.98",
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

### Get Category Details
```http
GET /api/v1/categories/{id}/
Authorization: Bearer <token>
```

**Response:**
```json
{
  "id": "1a68bd8d-6502-48de-b900-3695d9f22bf2",
  "name": "Electronics",
  "description": "Electronic devices and accessories",
  "product_count": 3,
  "total_value": "2999.97",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

### Get Products in Category
```http
GET /api/v1/categories/{id}/products/
Authorization: Bearer <token>
```

**Response:**
```json
{
  "count": 3,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": "565f6152-78c4-435f-98a6-d92691e37ff2",
      "name": "Laptop",
      "sku": "LAP001",
      "category": {
        "id": "1a68bd8d-6502-48de-b900-3695d9f22bf2",
        "name": "Electronics"
      },
      "description": "High-performance laptop",
      "unit_price": "999.99",
      "total_value": "99999.00",
      "stock_status": "in_stock",
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

### Get Products
```http
GET /api/v1/products/
Authorization: Bearer <token>
```

**Response:**
```json
{
  "count": 13,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": "565f6152-78c4-435f-98a6-d92691e37ff2",
      "name": "Laptop",
      "sku": "LAP001",
      "category": {
        "id": "1a68bd8d-6502-48de-b900-3695d9f22bf2",
        "name": "Electronics"
      },
      "description": "High-performance laptop",
      "unit_price": "999.99",
      "specifications": {
        "color": "black",
        "weight": "2.5kg",
        "dimensions": "15.6"
      },
      "total_value": "99999.00",
      "stock_status": "in_stock",
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

### Get Product Details
```http
GET /api/v1/products/{id}/
Authorization: Bearer <token>
```

**Response:**
```json
{
  "id": "565f6152-78c4-435f-98a6-d92691e37ff2",
  "name": "Laptop",
  "sku": "LAP001",
  "category": {
    "id": "1a68bd8d-6502-48de-b900-3695d9f22bf2",
    "name": "Electronics"
  },
  "description": "High-performance laptop",
  "unit_price": "999.99",
  "specifications": {
    "color": "black",
    "weight": "2.5kg",
    "dimensions": "15.6"
  },
  "total_value": "99999.00",
  "stock_status": "in_stock",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

---

## 🏢 Warehouses

### Get Warehouses
```http
GET /api/v1/warehouses/
Authorization: Bearer <token>
```

**Response:**
```json
{
  "count": 3,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": "3c8ad0f0-8724-6af0-d122-5817fb144d04",
      "name": "Main Warehouse",
      "address": "123 Main St, City, State 12345",
      "capacity": 10000,
      "manager": "John Doe",
      "contact_email": "warehouse@example.com",
      "contact_phone": "555-1234",
      "is_active": true,
      "current_utilization": "7.8",
      "available_capacity": 7377,
      "inventory_count": 13,
      "total_inventory_value": "2999.97",
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

### Get Warehouse Details
```http
GET /api/v1/warehouses/{id}/
Authorization: Bearer <token>
```

**Response:**
```json
{
  "id": "3c8ad0f0-8724-6af0-d122-5817fb144d04",
  "name": "Main Warehouse",
  "address": "123 Main St, City, State 12345",
  "capacity": 10000,
  "manager": "John Doe",
  "contact_email": "warehouse@example.com",
  "contact_phone": "555-1234",
  "is_active": true,
  "current_utilization": "7.8",
  "available_capacity": 7377,
  "inventory_count": 13,
  "total_inventory_value": "2999.97",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

---

## 📦 Inventory

### Get Inventory
```http
GET /api/v1/inventory/
Authorization: Bearer <token>
```

**Response:**
```json
{
  "count": 39,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": "4d9be1g1-9835-7bg1-e233-6928gc255e15",
      "product": {
        "id": "565f6152-78c4-435f-98a6-d92691e37ff2",
        "name": "Laptop",
        "sku": "LAP001"
      },
      "warehouse": {
        "id": "3c8ad0f0-8724-6af0-d122-5817fb144d04",
        "name": "Main Warehouse"
      },
      "quantity": 100,
      "reserved_quantity": 10,
      "reorder_point": 20,
      "max_stock_level": 500,
      "available_quantity": 90,
      "is_low_stock": false,
      "is_out_of_stock": false,
      "stock_value": "99999.00",
      "stock_status": "in_stock",
      "last_updated": "2024-01-01T00:00:00Z",
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

### Get Low Stock Items
```http
GET /api/v1/inventory/low_stock/
Authorization: Bearer <token>
```

**Response:**
```json
{
  "count": 5,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": "4d9be1g1-9835-7bg1-e233-6928gc255e15",
      "product": {
        "id": "565f6152-78c4-435f-98a6-d92691e37ff2",
        "name": "Laptop",
        "sku": "LAP001"
      },
      "warehouse": {
        "id": "3c8ad0f0-8724-6af0-d122-5817fb144d04",
        "name": "Main Warehouse"
      },
      "quantity": 15,
      "reserved_quantity": 5,
      "reorder_point": 20,
      "max_stock_level": 500,
      "available_quantity": 10,
      "is_low_stock": true,
      "is_out_of_stock": false,
      "stock_value": "14999.85",
      "stock_status": "low_stock",
      "last_updated": "2024-01-01T00:00:00Z",
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

### Get Out of Stock Items
```http
GET /api/v1/inventory/out_of_stock/
Authorization: Bearer <token>
```

**Response:**
```json
{
  "count": 2,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": "5eacf2h2-0946-8ch2-f344-7039hd366f26",
      "product": {
        "id": "676g7263-89d5-546g-09a7-e03702e48ff3",
        "name": "Smartphone",
        "sku": "PHN001"
      },
      "warehouse": {
        "id": "3c8ad0f0-8724-6af0-d122-5817fb144d04",
        "name": "Main Warehouse"
      },
      "quantity": 0,
      "reserved_quantity": 0,
      "reorder_point": 10,
      "max_stock_level": 200,
      "available_quantity": 0,
      "is_low_stock": false,
      "is_out_of_stock": true,
      "stock_value": "0.00",
      "stock_status": "out_of_stock",
      "last_updated": "2024-01-01T00:00:00Z",
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

---

## 📊 Stock Movements

### Get Stock Movements
```http
GET /api/v1/stock-movements/
Authorization: Bearer <token>
```

**Response:**
```json
{
  "count": 20,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": "6fbdg3i3-1057-9di3-g455-8140ie477g37",
      "product": {
        "id": "565f6152-78c4-435f-98a6-d92691e37ff2",
        "name": "Laptop",
        "sku": "LAP001"
      },
      "warehouse": {
        "id": "3c8ad0f0-8724-6af0-d122-5817fb144d04",
        "name": "Main Warehouse"
      },
      "movement_type": "in",
      "quantity": 100,
      "reference_type": "purchase_order",
      "reference_id": 1,
      "notes": "Initial stock",
      "movement_value": "99999.00",
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

---

## 🏪 Suppliers

### Get Suppliers
```http
GET /api/v1/suppliers/
Authorization: Bearer <token>
```

**Response:**
```json
{
  "count": 3,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": "7gceh4j4-1168-aej4-h566-9251jf588h48",
      "name": "Tech Supplies Inc",
      "contact_person": "Jane Smith",
      "email": "supplier@example.com",
      "phone": "555-5678",
      "address": "456 Supplier St, City, State 12345",
      "website": "https://techsupplies.com",
      "tax_id": "123456789",
      "payment_terms": "Net 30",
      "is_active": true,
      "total_orders": 5,
      "total_order_value": "4999.95",
      "average_order_value": "999.99",
      "last_order_date": "2024-01-15",
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

---

## 📋 Purchase Orders

### Get Purchase Orders
```http
GET /api/v1/purchase-orders/
Authorization: Bearer <token>
```

**Response:**
```json
{
  "count": 5,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": "8hdfi5k5-1279-bfk5-i677-0362kg699i59",
      "order_number": "PO-2024-001",
      "supplier": {
        "id": "7gceh4j4-1168-aej4-h566-9251jf588h48",
        "name": "Tech Supplies Inc"
      },
      "warehouse": {
        "id": "3c8ad0f0-8724-6af0-d122-5817fb144d04",
        "name": "Main Warehouse"
      },
      "status": "pending",
      "order_date": "2024-01-01",
      "expected_date": "2024-01-15",
      "received_date": null,
      "total_amount": "999.99",
      "notes": "Initial order",
      "approved_by": null,
      "approved_at": null,
      "item_count": 3,
      "total_quantity": 186,
      "received_quantity": 0,
      "is_complete": false,
      "completion_percentage": "0.0",
      "days_until_expected": 14,
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

### Get Pending Orders
```http
GET /api/v1/purchase-orders/pending/
Authorization: Bearer <token>
```

**Response:**
```json
{
  "count": 2,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": "8hdfi5k5-1279-bfk5-i677-0362kg699i59",
      "order_number": "PO-2024-001",
      "supplier": {
        "id": "7gceh4j4-1168-aej4-h566-9251jf588h48",
        "name": "Tech Supplies Inc"
      },
      "warehouse": {
        "id": "3c8ad0f0-8724-6af0-d122-5817fb144d04",
        "name": "Main Warehouse"
      },
      "status": "pending",
      "order_date": "2024-01-01",
      "expected_date": "2024-01-15",
      "total_amount": "999.99",
      "item_count": 3,
      "total_quantity": 186,
      "received_quantity": 0,
      "is_complete": false,
      "completion_percentage": "0.0",
      "days_until_expected": 14
    }
  ]
}
```

---

## 🚨 Stock Alerts

### Get Stock Alerts
```http
GET /api/v1/stock-alerts/
Authorization: Bearer <token>
```

**Response:**
```json
{
  "count": 7,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": "9iegj6l6-1380-cgl6-j788-1473lh700j60",
      "product": {
        "id": "565f6152-78c4-435f-98a6-d92691e37ff2",
        "name": "Laptop",
        "sku": "LAP001"
      },
      "warehouse": {
        "id": "3c8ad0f0-8724-6af0-d122-5817fb144d04",
        "name": "Main Warehouse"
      },
      "alert_type": "low_stock",
      "severity": "medium",
      "message": "Stock is running low",
      "threshold_value": 20,
      "current_value": 15,
      "is_resolved": false,
      "resolved_at": null,
      "resolved_by": null,
      "resolution_notes": null,
      "is_active": true,
      "duration": 5,
      "severity_color": "orange",
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

### Get Active Alerts
```http
GET /api/v1/stock-alerts/active/
Authorization: Bearer <token>
```

**Response:**
```json
{
  "count": 5,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": "9iegj6l6-1380-cgl6-j788-1473lh700j60",
      "product": {
        "id": "565f6152-78c4-435f-98a6-d92691e37ff2",
        "name": "Laptop",
        "sku": "LAP001"
      },
      "warehouse": {
        "id": "3c8ad0f0-8724-6af0-d122-5817fb144d04",
        "name": "Main Warehouse"
      },
      "alert_type": "low_stock",
      "severity": "medium",
      "message": "Stock is running low",
      "threshold_value": 20,
      "current_value": 15,
      "is_resolved": false,
      "is_active": true,
      "duration": 5,
      "severity_color": "orange"
    }
  ]
}
```

---

## 📊 Dashboard

### Get Dashboard Summary
```http
GET /api/v1/dashboard/summary/
Authorization: Bearer <token>
```

**Response:**
```json
{
  "total_products": 13,
  "total_inventory_value": "2999.97",
  "low_stock_items": 5,
  "out_of_stock_items": 2,
  "total_warehouses": 3,
  "active_alerts": 5,
  "pending_orders": 2,
  "recent_movements": [
    {
      "id": "6fbdg3i3-1057-9di3-g455-8140ie477g37",
      "product": {
        "id": "565f6152-78c4-435f-98a6-d92691e37ff2",
        "name": "Laptop",
        "sku": "LAP001"
      },
      "warehouse": {
        "id": "3c8ad0f0-8724-6af0-d122-5817fb144d04",
        "name": "Main Warehouse"
      },
      "movement_type": "in",
      "quantity": 100,
      "created_at": "2024-01-01T00:00:00Z"
    }
  ],
  "warehouse_utilization": [
    {
      "warehouse": "Main Warehouse",
      "utilization": 7.8,
      "capacity": 10000,
      "used": 777
    }
  ],
  "top_products": [
    {
      "product": "Laptop",
      "total_value": "99999.00",
      "quantity": 100
    }
  ],
  "alert_summary": {
    "low_stock": 3,
    "out_of_stock": 2,
    "critical": 1
  }
}
```

### Get Low Stock Items for Dashboard
```http
GET /api/v1/dashboard/low_stock/
Authorization: Bearer <token>
```

**Response:**
```json
{
  "count": 5,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": "4d9be1g1-9835-7bg1-e233-6928gc255e15",
      "product": {
        "id": "565f6152-78c4-435f-98a6-d92691e37ff2",
        "name": "Laptop",
        "sku": "LAP001"
      },
      "warehouse": {
        "id": "3c8ad0f0-8724-6af0-d122-5817fb144d04",
        "name": "Main Warehouse"
      },
      "quantity": 15,
      "reorder_point": 20,
      "stock_value": "14999.85",
      "days_until_stockout": 3
    }
  ]
}
```

### Get Recent Movements for Dashboard
```http
GET /api/v1/dashboard/recent_movements/
Authorization: Bearer <token>
```

**Response:**
```json
{
  "count": 10,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": "6fbdg3i3-1057-9di3-g455-8140ie477g37",
      "product": {
        "id": "565f6152-78c4-435f-98a6-d92691e37ff2",
        "name": "Laptop",
        "sku": "LAP001"
      },
      "warehouse": {
        "id": "3c8ad0f0-8724-6af0-d122-5817fb144d04",
        "name": "Main Warehouse"
      },
      "movement_type": "in",
      "quantity": 100,
      "movement_value": "99999.00",
      "created_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

### Get Pending Orders for Dashboard
```http
GET /api/v1/dashboard/pending_orders/
Authorization: Bearer <token>
```

**Response:**
```json
{
  "count": 2,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": "8hdfi5k5-1279-bfk5-i677-0362kg699i59",
      "order_number": "PO-2024-001",
      "supplier": {
        "id": "7gceh4j4-1168-aej4-h566-9251jf588h48",
        "name": "Tech Supplies Inc"
      },
      "warehouse": {
        "id": "3c8ad0f0-8724-6af0-d122-5817fb144d04",
        "name": "Main Warehouse"
      },
      "status": "pending",
      "expected_date": "2024-01-15",
      "total_amount": "999.99",
      "item_count": 3,
      "days_until_expected": 14
    }
  ]
}
```

---

## 📈 Reports

### Get Reports
```http
GET /api/v1/reports/
Authorization: Bearer <token>
```

**Response:**
```json
{
  "count": 4,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": "ajfhk7m7-1491-dhm7-k899-2584mi811k71",
      "name": "Inventory Valuation Report",
      "report_type": "inventory_valuation",
      "description": "Current inventory value across all warehouses",
      "format": "json",
      "data": {
        "total_items": 39,
        "total_value": "2999.97",
        "warehouses": [
          {
            "name": "Main Warehouse",
            "value": "2999.97",
            "items": 13
          }
        ]
      },
      "generated_by": {
        "id": 1,
        "username": "admin"
      },
      "is_scheduled": false,
      "file_path": null,
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

---

## 🎛️ Dashboard Widgets

### Get Dashboard Widgets
```http
GET /api/v1/dashboard-widgets/
Authorization: Bearer <token>
```

**Response:**
```json
{
  "count": 4,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": "bkghl8n8-1502-ein8-l900-3695nj922l82",
      "name": "Inventory Overview",
      "widget_type": "chart",
      "title": "Inventory Overview",
      "description": "Shows inventory levels across warehouses",
      "configuration": {
        "type": "bar",
        "data_source": "inventory",
        "refresh_interval": 300
      },
      "position": 1,
      "is_active": true,
      "refresh_interval": 300,
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

---

## 🔧 Common Operations

### Create New Product
```http
POST /api/v1/products/
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "New Product",
  "sku": "NEW001",
  "category_id": "1a68bd8d-6502-48de-b900-3695d9f22bf2",
  "description": "A new product",
  "unit_price": "99.99",
  "specifications": {
    "color": "blue",
    "weight": "1kg"
  }
}
```

### Update Inventory Quantity
```http
POST /api/v1/inventory/{id}/adjust_quantity/
Authorization: Bearer <token>
Content-Type: application/json

{
  "quantity": 50,
  "movement_type": "in",
  "notes": "Stock adjustment"
}
```

### Approve Purchase Order
```http
POST /api/v1/purchase-orders/{id}/approve/
Authorization: Bearer <token>
Content-Type: application/json

{
  "notes": "Approved for ordering"
}
```

### Resolve Stock Alert
```http
POST /api/v1/stock-alerts/{id}/resolve/
Authorization: Bearer <token>
Content-Type: application/json

{
  "resolution_notes": "Stock replenished"
}
```

---

## 📝 Error Responses

### 400 Bad Request
```json
{
  "error": "Validation failed",
  "details": {
    "name": ["This field is required."],
    "unit_price": ["A valid number is required."]
  }
}
```

### 401 Unauthorized
```json
{
  "detail": "Authentication credentials were not provided."
}
```

### 403 Forbidden
```json
{
  "detail": "You do not have permission to perform this action."
}
```

### 404 Not Found
```json
{
  "detail": "Not found."
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error."
}
```

---

## 🔗 Base URL Configuration

For development:
```
Base URL: http://localhost:8000
API Base: http://localhost:8000/api/v1
Auth URL: http://localhost:8000/api/token
```

For production:
```
Base URL: https://your-domain.com
API Base: https://your-domain.com/api/v1
Auth URL: https://your-domain.com/api/token
```

---

## 📋 Environment Variables

```env
# Frontend Environment Variables
REACT_APP_API_BASE_URL=http://localhost:8000/api/v1
REACT_APP_AUTH_URL=http://localhost:8000/api/token
REACT_APP_REFRESH_URL=http://localhost:8000/api/token/refresh
REACT_APP_APP_NAME=Inventory Management System
REACT_APP_VERSION=1.0.0
``` 