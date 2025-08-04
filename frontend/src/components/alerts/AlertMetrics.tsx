import React from 'react';
import { motion } from 'framer-motion';
import { 
  BellIcon, 
  ExclamationTriangleIcon,
  CheckCircleIcon,
  XCircleIcon
} from '@heroicons/react/24/outline';
import { StockAlert } from '@/types';

interface AlertMetricsProps {
  alerts: StockAlert[];
}

const AlertMetrics: React.FC<AlertMetricsProps> = ({ alerts }) => {
  const metrics = [
    {
      name: 'Total Alerts',
      value: alerts.length,
      icon: BellIcon,
      color: 'text-blue-600',
      bgColor: 'bg-blue-50',
    },
    {
      name: 'Active Alerts',
      value: alerts.filter(alert => !alert.is_resolved).length,
      icon: ExclamationTriangleIcon,
      color: 'text-yellow-600',
      bgColor: 'bg-yellow-50',
    },
    {
      name: 'Resolved Alerts',
      value: alerts.filter(alert => alert.is_resolved).length,
      icon: CheckCircleIcon,
      color: 'text-green-600',
      bgColor: 'bg-green-50',
    },
    {
      name: 'Critical Alerts',
      value: alerts.filter(alert => alert.severity === 'critical' && !alert.is_resolved).length,
      icon: XCircleIcon,
      color: 'text-red-600',
      bgColor: 'bg-red-50',
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

export default AlertMetrics; 