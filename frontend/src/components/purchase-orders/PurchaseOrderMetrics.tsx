import React from 'react';
import { motion } from 'framer-motion';
import { 
  DocumentTextIcon, 
  ClockIcon, 
  CheckCircleIcon,
  CurrencyDollarIcon,
  TruckIcon
} from '@heroicons/react/24/outline';
import { PurchaseOrder } from '@/types';

interface PurchaseOrderMetricsProps {
  purchaseOrders: PurchaseOrder[];
}

const PurchaseOrderMetrics: React.FC<PurchaseOrderMetricsProps> = ({ purchaseOrders }) => {
  const metrics = [
    {
      name: 'Total Orders',
      value: purchaseOrders.length,
      icon: DocumentTextIcon,
      color: 'text-blue-600',
      bgColor: 'bg-blue-50',
      change: '+12.5%',
      changeType: 'positive' as const,
    },
    {
      name: 'Pending Approval',
      value: purchaseOrders.filter(po => po.status === 'pending').length,
      icon: ClockIcon,
      color: 'text-yellow-600',
      bgColor: 'bg-yellow-50',
      change: '+5.2%',
      changeType: 'positive' as const,
    },
    {
      name: 'Approved Orders',
      value: purchaseOrders.filter(po => po.status === 'approved').length,
      icon: CheckCircleIcon,
      color: 'text-green-600',
      bgColor: 'bg-green-50',
      change: '+8.1%',
      changeType: 'positive' as const,
    },
    {
      name: 'In Transit',
      value: purchaseOrders.filter(po => po.status === 'ordered').length,
      icon: TruckIcon,
      color: 'text-purple-600',
      bgColor: 'bg-purple-50',
      change: '+15.3%',
      changeType: 'positive' as const,
    },
    {
      name: 'Total Value',
      value: `$${purchaseOrders.reduce((sum, po) => {
        const value = parseFloat(po.total_amount.replace('$', '').replace(',', ''));
        return sum + (isNaN(value) ? 0 : value);
      }, 0).toLocaleString()}`,
      icon: CurrencyDollarIcon,
      color: 'text-green-600',
      bgColor: 'bg-green-50',
      change: '+18.7%',
      changeType: 'positive' as const,
    },
    {
      name: 'Completion Rate',
      value: `${Math.round((purchaseOrders.filter(po => po.status === 'received').length / purchaseOrders.length) * 100)}%`,
      icon: CheckCircleIcon,
      color: 'text-indigo-600',
      bgColor: 'bg-indigo-50',
      change: '+2.1%',
      changeType: 'positive' as const,
    },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
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

export default PurchaseOrderMetrics; 