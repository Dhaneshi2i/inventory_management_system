import React from 'react';
import { 
  CubeIcon, 
  CurrencyDollarIcon, 
  ExclamationTriangleIcon, 
  TruckIcon,
} from '@heroicons/react/24/outline';
import { 
  useDashboardSummary, 
  useDashboardLowStock, 
  useDashboardRecentMovements, 
  useDashboardPendingOrders 
} from '@/hooks/useApi';
import LoadingSpinner from '@/components/LoadingSpinner';

const DashboardPage: React.FC = () => {
  const { data: summary, isLoading: summaryLoading, error: summaryError } = useDashboardSummary();
  const { data: lowStock, isLoading: lowStockLoading } = useDashboardLowStock();
  const { data: recentMovements, isLoading: movementsLoading } = useDashboardRecentMovements();
  const { data: pendingOrders, isLoading: ordersLoading } = useDashboardPendingOrders();

  const stats = [
    {
      name: 'Total Products',
      value: summary?.total_products || 0,
      icon: CubeIcon,
      color: 'text-blue-600',
      bgColor: 'bg-blue-100',
    },
    {
      name: 'Total Inventory Value',
      value: `$${summary?.total_inventory_value || '0.00'}`,
      icon: CurrencyDollarIcon,
      color: 'text-green-600',
      bgColor: 'bg-green-100',
    },
    {
      name: 'Low Stock Items',
      value: summary?.low_stock_items || 0,
      icon: ExclamationTriangleIcon,
      color: 'text-yellow-600',
      bgColor: 'bg-yellow-100',
    },
    {
      name: 'Out of Stock Items',
      value: summary?.out_of_stock_items || 0,
      icon: ExclamationTriangleIcon,
      color: 'text-red-600',
      bgColor: 'bg-red-100',
    },
    {
      name: 'Active Alerts',
      value: summary?.active_alerts || 0,
      icon: ExclamationTriangleIcon,
      color: 'text-orange-600',
      bgColor: 'bg-orange-100',
    },
    {
      name: 'Pending Orders',
      value: summary?.pending_orders || 0,
      icon: TruckIcon,
      color: 'text-purple-600',
      bgColor: 'bg-purple-100',
    },
  ];

  if (summaryLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (summaryError) {
    return (
      <div className="text-center py-12">
        <p className="text-red-600">Failed to load dashboard data</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="mt-1 text-sm text-gray-500">
          Overview of your inventory management system
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
        {stats.map((stat) => (
          <div key={stat.name} className="dashboard-card">
            <div className="card-body">
              <div className="flex items-center">
                <div className={`flex-shrink-0 p-2 rounded-md ${stat.bgColor}`}>
                  <stat.icon className={`h-6 w-6 ${stat.color}`} />
                </div>
                <div className="ml-4">
                  <p className="dashboard-stat-label">{stat.name}</p>
                  <p className="dashboard-stat">{stat.value}</p>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Low Stock Items */}
        <div className="dashboard-card">
          <div className="card-header">
            <h3 className="text-lg font-medium text-gray-900">Low Stock Items</h3>
          </div>
          <div className="card-body">
            {lowStockLoading ? (
              <LoadingSpinner />
            ) : lowStock?.results && lowStock.results.length > 0 ? (
              <div className="space-y-3">
                {lowStock.results.slice(0, 5).map((item) => (
                  <div key={item.id} className="flex items-center justify-between p-3 bg-yellow-50 rounded-lg">
                    <div>
                      <p className="font-medium text-gray-900">{item.product.name}</p>
                      <p className="text-sm text-gray-500">{item.warehouse.name}</p>
                    </div>
                    <div className="text-right">
                      <p className="text-sm font-medium text-yellow-800">
                        {item.quantity} / {item.reorder_point}
                      </p>
                      <p className="text-xs text-gray-500">Reorder Point</p>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-500 text-center py-4">No low stock items</p>
            )}
          </div>
        </div>

        {/* Recent Movements */}
        <div className="dashboard-card">
          <div className="card-header">
            <h3 className="text-lg font-medium text-gray-900">Recent Stock Movements</h3>
          </div>
          <div className="card-body">
            {movementsLoading ? (
              <LoadingSpinner />
            ) : recentMovements?.results && recentMovements.results.length > 0 ? (
              <div className="space-y-3">
                {recentMovements.results.slice(0, 5).map((movement) => (
                  <div key={movement.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <div>
                      <p className="font-medium text-gray-900">{movement.product.name}</p>
                      <p className="text-sm text-gray-500">{movement.warehouse.name}</p>
                    </div>
                    <div className="text-right">
                      <p className={`text-sm font-medium ${
                        movement.movement_type === 'in' ? 'text-green-600' : 'text-red-600'
                      }`}>
                        {movement.movement_type === 'in' ? '+' : '-'}{movement.quantity}
                      </p>
                      <p className="text-xs text-gray-500 capitalize">{movement.movement_type}</p>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-500 text-center py-4">No recent movements</p>
            )}
          </div>
        </div>

        {/* Pending Orders */}
        <div className="dashboard-card">
          <div className="card-header">
            <h3 className="text-lg font-medium text-gray-900">Pending Purchase Orders</h3>
          </div>
          <div className="card-body">
            {ordersLoading ? (
              <LoadingSpinner />
            ) : pendingOrders?.results && pendingOrders.results.length > 0 ? (
              <div className="space-y-3">
                {pendingOrders.results.slice(0, 5).map((order) => (
                  <div key={order.id} className="flex items-center justify-between p-3 bg-blue-50 rounded-lg">
                    <div>
                      <p className="font-medium text-gray-900">{order.order_number}</p>
                      <p className="text-sm text-gray-500">{order.supplier.name}</p>
                    </div>
                    <div className="text-right">
                      <p className="text-sm font-medium text-blue-800">
                        ${order.total_amount}
                      </p>
                      <p className="text-xs text-gray-500">
                        {order.days_until_expected} days
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-500 text-center py-4">No pending orders</p>
            )}
          </div>
        </div>

        {/* Warehouse Utilization */}
        <div className="dashboard-card">
          <div className="card-header">
            <h3 className="text-lg font-medium text-gray-900">Warehouse Utilization</h3>
          </div>
          <div className="card-body">
            {summary?.warehouse_utilization && summary.warehouse_utilization.length > 0 ? (
              <div className="space-y-4">
                {summary.warehouse_utilization.map((warehouse, index) => (
                  <div key={index}>
                    <div className="flex justify-between text-sm mb-1">
                      <span className="font-medium">{warehouse.warehouse}</span>
                      <span className="text-gray-500">{warehouse.utilization}%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className={`h-2 rounded-full ${
                          warehouse.utilization > 80 ? 'bg-red-500' :
                          warehouse.utilization > 60 ? 'bg-yellow-500' : 'bg-green-500'
                        }`}
                        style={{ width: `${Math.min(warehouse.utilization, 100)}%` }}
                      />
                    </div>
                    <div className="flex justify-between text-xs text-gray-500 mt-1">
                      <span>{warehouse.used} used</span>
                      <span>{warehouse.capacity} total</span>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-500 text-center py-4">No warehouse data available</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default DashboardPage; 