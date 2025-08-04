# Inventory Management System - Frontend

A modern React frontend for the Inventory Management System, built with TypeScript, Tailwind CSS, and React Query.

## 🚀 Features

- **Modern React Architecture**: Built with React 18, TypeScript, and functional components
- **Responsive Design**: Mobile-first design with Tailwind CSS
- **State Management**: React Query for server state management
- **Authentication**: JWT-based authentication with automatic token refresh
- **Real-time Updates**: Auto-refreshing dashboard with live data
- **Type Safety**: Full TypeScript support with comprehensive type definitions
- **Modern UI**: Clean, professional interface with smooth animations
- **Error Handling**: Comprehensive error handling and user feedback
- **Loading States**: Skeleton loading and spinner components
- **Form Validation**: React Hook Form with Zod validation

## 🛠️ Tech Stack

- **React 18** - UI library
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **React Query** - Server state management
- **React Router** - Navigation
- **React Hook Form** - Form handling
- **Axios** - HTTP client
- **Heroicons** - Icons
- **React Hot Toast** - Notifications
- **Framer Motion** - Animations
- **Recharts** - Charts and graphs

## 📁 Project Structure

```
frontend/
├── public/
│   ├── index.html
│   └── favicon.ico
├── src/
│   ├── components/          # Reusable UI components
│   │   ├── Layout.tsx       # Main layout with sidebar
│   │   └── LoadingSpinner.tsx
│   ├── contexts/            # React contexts
│   │   └── AuthContext.tsx  # Authentication context
│   ├── hooks/               # Custom React hooks
│   │   └── useApi.ts        # API hooks with React Query
│   ├── pages/               # Page components
│   │   ├── DashboardPage.tsx
│   │   ├── LoginPage.tsx
│   │   ├── ProductsPage.tsx
│   │   ├── InventoryPage.tsx
│   │   ├── WarehousesPage.tsx
│   │   ├── SuppliersPage.tsx
│   │   ├── PurchaseOrdersPage.tsx
│   │   ├── StockAlertsPage.tsx
│   │   └── ReportsPage.tsx
│   ├── services/            # API services
│   │   ├── api.ts           # Axios configuration
│   │   └── endpoints.ts     # API endpoint definitions
│   ├── types/               # TypeScript type definitions
│   │   └── index.ts         # All type definitions
│   ├── utils/               # Utility functions
│   ├── App.tsx              # Main app component
│   ├── index.tsx            # Entry point
│   └── index.css            # Global styles
├── package.json
├── tailwind.config.js
├── tsconfig.json
└── README.md
```

## 🚀 Getting Started

### Prerequisites

- Node.js 16+ 
- npm or yarn
- Backend API running (see backend README)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd inventory_management_system/frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   # or
   yarn install
   ```

3. **Set up environment variables**
   Create a `.env` file in the frontend directory:
   ```env
   REACT_APP_API_BASE_URL=http://localhost:8000/api/v1
   REACT_APP_AUTH_URL=http://localhost:8000/api/token
   REACT_APP_REFRESH_URL=http://localhost:8000/api/token/refresh
   REACT_APP_APP_NAME=Inventory Management System
   REACT_APP_VERSION=1.0.0
   ```

4. **Start the development server**
   ```bash
   npm start
   # or
   yarn start
   ```

5. **Open your browser**
   Navigate to `http://localhost:3000`

### Login Credentials

Use the demo credentials to log in:
- **Username**: `admin`
- **Password**: `admin123`

## 📱 Available Scripts

- `npm start` - Start development server
- `npm build` - Build for production
- `npm test` - Run tests
- `npm run lint` - Run ESLint
- `npm run lint:fix` - Fix ESLint errors
- `npm run format` - Format code with Prettier

## 🎨 UI Components

### Core Components

- **Layout**: Main application layout with sidebar navigation
- **LoadingSpinner**: Reusable loading spinner with different sizes
- **Modal**: Reusable modal component
- **Table**: Data table with sorting and filtering
- **Form**: Form components with validation

### Styling

The application uses Tailwind CSS with custom components:

- **Buttons**: `.btn`, `.btn-primary`, `.btn-secondary`, etc.
- **Cards**: `.card`, `.card-header`, `.card-body`
- **Forms**: `.input`, `.form-group`, `.form-label`
- **Tables**: `.table`, `.table-header`, `.table-body`
- **Badges**: `.badge`, `.badge-success`, `.badge-warning`

## 🔐 Authentication

The application uses JWT authentication with automatic token refresh:

- **Login**: Username/password authentication
- **Token Storage**: Access and refresh tokens stored in localStorage
- **Auto Refresh**: Automatic token refresh on 401 errors
- **Protected Routes**: All routes except login require authentication
- **Logout**: Clears tokens and redirects to login

## 📊 API Integration

### API Services

- **Categories**: Product category management
- **Products**: Product catalog management
- **Warehouses**: Warehouse management
- **Inventory**: Stock level tracking
- **Suppliers**: Supplier management
- **Purchase Orders**: Order management
- **Stock Alerts**: Alert monitoring
- **Dashboard**: Summary and analytics

### React Query Hooks

All API calls use React Query for:
- **Caching**: Automatic data caching
- **Background Updates**: Automatic data refetching
- **Optimistic Updates**: Immediate UI updates
- **Error Handling**: Centralized error handling
- **Loading States**: Automatic loading state management

## 🎯 Key Features

### Dashboard
- **Real-time Stats**: Live inventory statistics
- **Low Stock Alerts**: Items below reorder point
- **Recent Movements**: Latest stock movements
- **Pending Orders**: Orders awaiting approval
- **Warehouse Utilization**: Capacity usage charts

### Navigation
- **Responsive Sidebar**: Collapsible navigation
- **Active States**: Visual feedback for current page
- **Mobile Support**: Touch-friendly mobile navigation

### Data Management
- **CRUD Operations**: Create, read, update, delete
- **Bulk Operations**: Multi-select actions
- **Search & Filter**: Advanced filtering capabilities
- **Export**: Data export functionality

## 🔧 Configuration

### Tailwind CSS
Custom theme configuration in `tailwind.config.js`:
- Custom color palette
- Custom animations
- Responsive breakpoints
- Component utilities

### TypeScript
Strict TypeScript configuration with:
- Path mapping for clean imports
- Strict type checking
- ESLint integration
- Prettier formatting

## 🚀 Deployment

### Build for Production

```bash
npm run build
```

### Environment Variables for Production

```env
REACT_APP_API_BASE_URL=https://your-api-domain.com/api/v1
REACT_APP_AUTH_URL=https://your-api-domain.com/api/token
REACT_APP_REFRESH_URL=https://your-api-domain.com/api/token/refresh
```

### Deployment Options

- **Netlify**: Drag and drop the `build` folder
- **Vercel**: Connect your GitHub repository
- **AWS S3**: Upload build files to S3 bucket
- **Docker**: Use the provided Dockerfile

## 🧪 Testing

### Running Tests

```bash
npm test
```

### Test Structure

- **Unit Tests**: Component and utility tests
- **Integration Tests**: API integration tests
- **E2E Tests**: End-to-end user flow tests

## 📈 Performance

### Optimization Features

- **Code Splitting**: Automatic route-based code splitting
- **Lazy Loading**: Component lazy loading
- **Caching**: React Query caching strategy
- **Bundle Analysis**: Webpack bundle analyzer
- **Image Optimization**: Optimized image loading

### Performance Monitoring

- **Lighthouse**: Performance auditing
- **Bundle Size**: Monitor bundle size
- **Loading Times**: Track page load times

## 🔒 Security

### Security Features

- **HTTPS Only**: Production HTTPS enforcement
- **CSP Headers**: Content Security Policy
- **XSS Protection**: Cross-site scripting protection
- **CSRF Protection**: Cross-site request forgery protection
- **Input Validation**: Client-side validation

## 🤝 Contributing

### Development Workflow

1. **Fork the repository**
2. **Create a feature branch**
3. **Make your changes**
4. **Add tests**
5. **Run linting and tests**
6. **Submit a pull request**

### Code Standards

- **TypeScript**: Strict type checking
- **ESLint**: Code quality rules
- **Prettier**: Code formatting
- **Conventional Commits**: Commit message format

## 📚 API Documentation

For detailed API documentation, see the [API_ENDPOINTS_REFERENCE.md](../API_ENDPOINTS_REFERENCE.md) file.

## 🆘 Support

### Common Issues

1. **CORS Errors**: Ensure backend CORS is configured
2. **Authentication Issues**: Check token validity and refresh
3. **API Connection**: Verify backend is running and accessible

### Getting Help

- **Documentation**: Check this README and API docs
- **Issues**: Create an issue on GitHub
- **Discussions**: Use GitHub Discussions

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **React Team**: For the amazing React library
- **Tailwind CSS**: For the utility-first CSS framework
- **React Query**: For excellent server state management
- **Heroicons**: For beautiful icons
- **Community**: For all the open-source contributions 