import React from 'react';
import { motion } from 'framer-motion';
import { 
  ExclamationTriangleIcon,
  XCircleIcon,
  BellAlertIcon,
  ArrowRightIcon,
  CheckCircleIcon
} from '@heroicons/react/24/outline';
import { Inventory } from '@/types';

interface LowStockAlertsProps {
  inventory: Inventory[];
  loading: boolean;
}

const LowStockAlerts: React.FC<LowStockAlertsProps> = ({ inventory, loading }) => {
  const lowStockItems = inventory.filter((item: Inventory) => item.is_low_stock && !item.is_out_of_stock);
  const outOfStockItems = inventory.filter((item: Inventory) => item.is_out_of_stock);

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="animate-pulse">
          <div className="h-4 bg-gray-200 rounded w-1/3 mb-4"></div>
          <div className="space-y-3">
            {[...Array(3)].map((_, i) => (
              <div key={i} className="h-16 bg-gray-200 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  const totalAlerts = lowStockItems.length + outOfStockItems.length;

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200">
      {/* Header */}
      <div className="px-6 py-4 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <div className="flex items-center">
            <BellAlertIcon className="h-5 w-5 text-red-500 mr-2" />
            <h3 className="text-lg font-medium text-gray-900">Stock Alerts</h3>
          </div>
          {totalAlerts > 0 && (
            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
              {totalAlerts} alert{totalAlerts !== 1 ? 's' : ''}
            </span>
          )}
        </div>
      </div>

      {/* Alerts Content */}
      <div className="p-6">
        {totalAlerts === 0 ? (
          <div className="text-center py-8">
            <CheckCircleIcon className="h-12 w-12 text-green-500 mx-auto mb-4" />
            <h4 className="text-lg font-medium text-gray-900 mb-2">All Good!</h4>
            <p className="text-sm text-gray-500">No stock alerts at the moment.</p>
          </div>
        ) : (
          <div className="space-y-4">
            {/* Out of Stock Items */}
            {outOfStockItems.length > 0 && (
              <div>
                <h4 className="text-sm font-medium text-red-700 mb-3 flex items-center">
                  <XCircleIcon className="h-4 w-4 mr-1" />
                  Out of Stock ({outOfStockItems.length})
                </h4>
                <div className="space-y-2">
                  {outOfStockItems.slice(0, 3).map((item: Inventory, index: number) => (
                    <motion.div
                      key={item.id}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ duration: 0.3, delay: index * 0.1 }}
                      className="bg-red-50 border border-red-200 rounded-lg p-3"
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex-1">
                          <div className="font-medium text-red-900 text-sm">
                            {item.product.name}
                          </div>
                          <div className="text-xs text-red-600">
                            SKU: {item.product.sku} • {item.warehouse.name}
                          </div>
                        </div>
                        <div className="text-right">
                          <div className="text-sm font-medium text-red-900">0</div>
                          <div className="text-xs text-red-600">in stock</div>
                        </div>
                      </div>
                    </motion.div>
                  ))}
                  {outOfStockItems.length > 3 && (
                    <div className="text-center">
                      <button className="text-sm text-red-600 hover:text-red-800 font-medium">
                        View {outOfStockItems.length - 3} more
                      </button>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Low Stock Items */}
            {lowStockItems.length > 0 && (
              <div>
                <h4 className="text-sm font-medium text-yellow-700 mb-3 flex items-center">
                  <ExclamationTriangleIcon className="h-4 w-4 mr-1" />
                  Low Stock ({lowStockItems.length})
                </h4>
                <div className="space-y-2">
                  {lowStockItems.slice(0, 3).map((item: Inventory, index: number) => (
                    <motion.div
                      key={item.id}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ duration: 0.3, delay: index * 0.1 }}
                      className="bg-yellow-50 border border-yellow-200 rounded-lg p-3"
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex-1">
                          <div className="font-medium text-yellow-900 text-sm">
                            {item.product.name}
                          </div>
                          <div className="text-xs text-yellow-600">
                            SKU: {item.product.sku} • {item.warehouse.name}
                          </div>
                        </div>
                        <div className="text-right">
                          <div className="text-sm font-medium text-yellow-900">
                            {item.quantity}
                          </div>
                          <div className="text-xs text-yellow-600">
                            reorder: {item.reorder_point}
                          </div>
                        </div>
                      </div>
                      <div className="mt-2">
                        <div className="flex items-center justify-between text-xs">
                          <span className="text-yellow-600">Stock Level</span>
                          <span className="text-yellow-600">
                            {Math.round((item.quantity / item.max_stock_level) * 100)}%
                          </span>
                        </div>
                        <div className="mt-1 bg-yellow-200 rounded-full h-1">
                          <div
                            className="bg-yellow-500 h-1 rounded-full"
                            style={{
                              width: `${Math.min((item.quantity / item.max_stock_level) * 100, 100)}%`
                            }}
                          />
                        </div>
                      </div>
                    </motion.div>
                  ))}
                  {lowStockItems.length > 3 && (
                    <div className="text-center">
                      <button className="text-sm text-yellow-600 hover:text-yellow-800 font-medium">
                        View {lowStockItems.length - 3} more
                      </button>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Quick Actions */}
            <div className="pt-4 border-t border-gray-200">
              <div className="grid grid-cols-2 gap-2">
                <button className="inline-flex items-center justify-center px-3 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500">
                  <ArrowRightIcon className="h-4 w-4 mr-1" />
                  Create PO
                </button>
                <button className="inline-flex items-center justify-center px-3 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500">
                  View All
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default LowStockAlerts; 