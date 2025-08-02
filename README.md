# Inventory Management System

A comprehensive Django-based inventory management system for e-commerce businesses to track inventory across multiple warehouses.

## Features

### Core Modules
- **Product Management**: CRUD operations for products with categories and specifications
- **Inventory Tracking**: Real-time stock levels across multiple warehouses
- **Purchase Orders**: Create and manage supplier orders with status tracking
- **Stock Alerts**: Low inventory warnings and reorder notifications
- **Reporting Dashboard**: Inventory turnover, stock valuation, and trends

### Technical Features
- **RESTful API**: Complete API with Django REST Framework
- **JWT Authentication**: Secure token-based authentication
- **Swagger Documentation**: Auto-generated API documentation
- **Admin Interface**: Highly customized Django admin with computed fields and actions
- **Soft Delete**: Data preservation with soft delete functionality
- **Audit Trail**: Complete inventory movement history
- **Multi-warehouse Support**: Track inventory across multiple locations

## Technology Stack

### Backend
- **Django 4.2.7**: Core web framework
- **Django REST Framework 3.14.0**: API development
- **SQLite**: Database (with PostgreSQL migration path)
- **JWT Authentication**: Token-based security
- **Swagger/OpenAPI**: API documentation

### Development Tools
- **Python 3.12**: Programming language
- **Virtual Environment**: Isolated dependencies
- **Django Extensions**: Development utilities
- **Django Debug Toolbar**: Development debugging

## Project Structure

```
inventory_management_system/
├── inventory_system/
│   ├── apps/
│   │   ├── products/          # Product catalog management
│   │   ├── inventory/         # Stock tracking and locations
│   │   ├── orders/            # Purchase order management
│   │   ├── alerts/            # Stock alert system
│   │   └── reports/           # Reporting and analytics
│   ├── core/                  # Shared utilities and base models
│   ├── api/                   # DRF serializers and viewsets
│   ├── settings.py            # Django configuration
│   └── urls.py                # URL routing
├── manage.py                  # Django management script
├── requirements.txt           # Python dependencies
└── README.md                  # Project documentation
```

## Installation

### Prerequisites
- Python 3.12+
- pip (Python package installer)

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd inventory_management_system
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

6. **Populate sample data (optional)**
   ```bash
   python manage.py populate_sample_data
   ```

7. **Run development server**
   ```bash
   python manage.py runserver
   ```

## Usage

### Access Points

- **Django Admin**: http://localhost:8000/admin/
  - Username: `admin`
  - Password: `admin123`

- **API Documentation**: http://localhost:8000/swagger/
- **API Root**: http://localhost:8000/api/v1/
- **JWT Token**: http://localhost:8000/api/token/

### API Authentication

1. **Obtain JWT Token**
   ```bash
   curl -X POST http://localhost:8000/api/token/ \
     -H "Content-Type: application/json" \
     -d '{"username": "admin", "password": "admin123"}'
   ```

2. **Use Token in Requests**
   ```bash
   curl -X GET http://localhost:8000/api/v1/products/ \
     -H "Authorization: Bearer <your_token>"
   ```

## API Endpoints

### Products
- `GET /api/v1/products/` - List all products
- `POST /api/v1/products/` - Create new product
- `GET /api/v1/products/{id}/` - Get product details
- `PUT /api/v1/products/{id}/` - Update product
- `DELETE /api/v1/products/{id}/` - Delete product

### Inventory
- `GET /api/v1/inventory/` - List all inventory items
- `POST /api/v1/inventory/` - Create inventory item
- `GET /api/v1/inventory/{id}/` - Get inventory details
- `POST /api/v1/inventory/{id}/adjust_quantity/` - Adjust stock quantity

### Purchase Orders
- `GET /api/v1/purchase-orders/` - List all purchase orders
- `POST /api/v1/purchase-orders/` - Create new purchase order
- `POST /api/v1/purchase-orders/{id}/approve/` - Approve purchase order
- `POST /api/v1/purchase-orders/{id}/receive/` - Mark order as received

### Dashboard
- `GET /api/v1/dashboard/summary/` - Get dashboard summary
- `GET /api/v1/dashboard/low_stock/` - Get low stock items
- `GET /api/v1/dashboard/recent_movements/` - Get recent stock movements

## Database Models

### Core Models
- **Category**: Product categories
- **Product**: Product catalog with specifications
- **Warehouse**: Storage locations
- **Inventory**: Stock levels per product per warehouse
- **StockMovement**: Audit trail for all inventory changes

### Order Models
- **Supplier**: Vendor information
- **PurchaseOrder**: Order management
- **PurchaseOrderItem**: Order line items

### Alert Models
- **StockAlert**: Individual stock alerts
- **AlertRule**: Alert configuration rules
- **AlertNotification**: Alert delivery tracking

### Report Models
- **Report**: Generated reports and analytics
- **DashboardWidget**: Dashboard component configuration

## Admin Interface Features

### Custom Computed Fields
- Product total value across all warehouses
- Warehouse utilization percentage
- Stock status indicators (in stock, low stock, out of stock)
- Purchase order completion status

### Custom Actions
- Soft delete/restore objects
- Approve purchase orders
- Generate reports
- Export data to CSV
- Test alert rules

### Enhanced Filtering
- Advanced search capabilities
- Date range filtering
- Status-based filtering
- Category and warehouse filtering

## Development

### Running Tests
```bash
python manage.py test
```

### Code Quality
- Type hints throughout the codebase
- Comprehensive docstrings
- PEP 8 compliance
- Model validation

### Environment Variables
Create a `.env` file in the project root:
```env
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

## Sample Data

The system includes a management command to populate sample data:

```bash
python manage.py populate_sample_data
```

This creates:
- 5 product categories (Electronics, Clothing, Books, Home & Garden, Sports)
- 12 sample products across all categories
- 3 warehouses with different capacities
- Inventory items for all products across all warehouses
- 3 suppliers with contact information
- 5 sample purchase orders with various statuses
- Stock movements for audit trail
- Alert rules and sample alerts
- Dashboard widgets and reports

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Create an issue in the repository
- Contact: admin@inventorysystem.com

## Roadmap

### Phase 2: Frontend Development
- React-based user interface
- Real-time updates with WebSockets
- Advanced dashboard with charts
- Mobile-responsive design

### Phase 3: Advanced Features
- Barcode scanning integration
- Email notifications
- Advanced reporting with charts
- Multi-language support
- API rate limiting
- Background task processing with Celery 