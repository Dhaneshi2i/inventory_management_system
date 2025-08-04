import React from 'react';
import { motion } from 'framer-motion';
import { 
  BuildingOfficeIcon, 
  CubeIcon,
  CurrencyDollarIcon,
  ChartBarIcon
} from '@heroicons/react/24/outline';
import { Warehouse } from '@/types';

interface WarehouseMetricsProps {
  warehouses: Warehouse[];
}

const WarehouseMetrics: React.FC<WarehouseMetricsProps> = ({ warehouses }) => {
  const metrics = [
    {
      name: 'Total Warehouses',
      value: warehouses.length,
      icon: BuildingOfficeIcon,
      color: 'text-blue-600',
      bgColor: 'bg-blue-50',
    },
    {
      name: 'Active Warehouses',
      value: warehouses.filter(w => w.is_active).length,
      icon: CubeIcon,
      color: 'text-green-600',
      bgColor: 'bg-green-50',
    },
    {
      name: 'Total Capacity',
      value: warehouses.reduce((sum, w) => sum + w.capacity, 0).toLocaleString(),
      icon: ChartBarIcon,
      color: 'text-purple-600',
      bgColor: 'bg-purple-50',
    },
    {
      name: 'Total Value',
      value: `$${warehouses.reduce((sum, w) => {
        const value = parseFloat(w.total_inventory_value);
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

export default WarehouseMetrics; 