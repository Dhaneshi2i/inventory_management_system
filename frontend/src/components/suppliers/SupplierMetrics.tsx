import React from 'react';
import { motion } from 'framer-motion';
import { 
  BuildingOfficeIcon, 
  CurrencyDollarIcon,
  DocumentTextIcon,
  ChartBarIcon
} from '@heroicons/react/24/outline';
import { Supplier } from '@/types';

interface SupplierMetricsProps {
  suppliers: Supplier[];
}

const SupplierMetrics: React.FC<SupplierMetricsProps> = ({ suppliers }) => {
  const metrics = [
    {
      name: 'Total Suppliers',
      value: suppliers.length,
      icon: BuildingOfficeIcon,
      color: 'text-blue-600',
      bgColor: 'bg-blue-50',
    },
    {
      name: 'Active Suppliers',
      value: suppliers.filter(s => s.is_active).length,
      icon: DocumentTextIcon,
      color: 'text-green-600',
      bgColor: 'bg-green-50',
    },
    {
      name: 'Total Orders',
      value: suppliers.reduce((sum, s) => sum + s.total_orders, 0),
      icon: ChartBarIcon,
      color: 'text-purple-600',
      bgColor: 'bg-purple-50',
    },
    {
      name: 'Total Value',
      value: `$${suppliers.reduce((sum, s) => {
        const value = parseFloat(s.total_order_value);
        return sum + (isNaN(value) ? 0 : value);
      }, 0).toLocaleString()}`,
      icon: CurrencyDollarIcon,
      color: 'text-green-600',
      bgColor: 'bg-green-50',
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
          className="bg-white rounded-lg shadow-sm border border-gray-200 p-6"
        >
          <div className="flex items-center">
            <div className={`p-2 rounded-lg ${metric.bgColor}`}>
              <metric.icon className={`h-6 w-6 ${metric.color}`} />
            </div>
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-600">{metric.name}</p>
              <p className="text-2xl font-bold text-gray-900">{metric.value}</p>
            </div>
          </div>
        </motion.div>
      ))}
    </div>
  );
};

export default SupplierMetrics; 