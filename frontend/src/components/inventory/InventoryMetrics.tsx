import React from 'react';
import { motion } from 'framer-motion';
import { 
  CubeIcon, 
  ExclamationTriangleIcon, 
  XCircleIcon, 
  CurrencyDollarIcon,
  BuildingOfficeIcon,
  BellAlertIcon,
  ClockIcon
} from '@heroicons/react/24/outline';
import { DashboardSummary } from '@/types';
import { LoadingSpinner } from '@/components/LoadingSpinner';

interface InventoryMetricsProps {
  data?: DashboardSummary;
  loading: boolean;
}

const InventoryMetrics: React.FC<InventoryMetricsProps> = ({ data, loading }) => {
  if (loading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {[...Array(4)].map((_, i) => (
          <div key={i} className="bg-white rounded-lg shadow p-6 animate-pulse">
            <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
            <div className="h-8 bg-gray-200 rounded w-1/2"></div>
          </div>
        ))}
      </div>
    );
  }

  if (!data) return null;

  const metrics = [
    {
      name: 'Total Products',
      value: data.total_products.toLocaleString(),
      icon: CubeIcon,
      color: 'text-blue-600',
      bgColor: 'bg-blue-50',
      change: '+2.5%',
      changeType: 'positive' as const,
    },
    {
      name: 'Inventory Value',
      value: data.total_inventory_value,
      icon: CurrencyDollarIcon,
      color: 'text-green-600',
      bgColor: 'bg-green-50',
      change: '+8.1%',
      changeType: 'positive' as const,
    },
    {
      name: 'Low Stock Items',
      value: data.low_stock_items.toString(),
      icon: ExclamationTriangleIcon,
      color: 'text-yellow-600',
      bgColor: 'bg-yellow-50',
      change: '-12.3%',
      changeType: 'negative' as const,
    },
    {
      name: 'Out of Stock',
      value: data.out_of_stock_items.toString(),
      icon: XCircleIcon,
      color: 'text-red-600',
      bgColor: 'bg-red-50',
      change: '-5.2%',
      changeType: 'negative' as const,
    },
    {
      name: 'Active Warehouses',
      value: data.total_warehouses.toString(),
      icon: BuildingOfficeIcon,
      color: 'text-purple-600',
      bgColor: 'bg-purple-50',
      change: '+0%',
      changeType: 'neutral' as const,
    },
    {
      name: 'Active Alerts',
      value: data.active_alerts.toString(),
      icon: BellAlertIcon,
      color: 'text-orange-600',
      bgColor: 'bg-orange-50',
      change: '+3.1%',
      changeType: 'positive' as const,
    },
    {
      name: 'Pending Orders',
      value: data.pending_orders.toString(),
      icon: ClockIcon,
      color: 'text-indigo-600',
      bgColor: 'bg-indigo-50',
      change: '-15.7%',
      changeType: 'negative' as const,
    },
    {
      name: 'Recent Movements',
      value: data.recent_movements.length.toString(),
      icon: CubeIcon,
      color: 'text-gray-600',
      bgColor: 'bg-gray-50',
      change: '+22.4%',
      changeType: 'positive' as const,
    },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      {metrics.map((metric, index) => (
        <motion.div
          key={metric.name}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3, delay: index * 0.1 }}
          className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow"
        >
          <div className="flex items-center justify-between">
            <div className="flex-1">
              <div className="flex items-center">
                <div className={`p-2 rounded-lg ${metric.bgColor}`}>
                  <metric.icon className={`h-6 w-6 ${metric.color}`} />
                </div>
                <div className="ml-3">
                  <p className="text-sm font-medium text-gray-600">{metric.name}</p>
                  <p className="text-2xl font-bold text-gray-900">{metric.value}</p>
                </div>
              </div>
            </div>
            <div className="text-right">
              <span
                className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                  metric.changeType === 'positive'
                    ? 'bg-green-100 text-green-800'
                    : metric.changeType === 'negative'
                    ? 'bg-red-100 text-red-800'
                    : 'bg-gray-100 text-gray-800'
                }`}
              >
                {metric.change}
              </span>
            </div>
          </div>
        </motion.div>
      ))}
    </div>
  );
};

export default InventoryMetrics; 