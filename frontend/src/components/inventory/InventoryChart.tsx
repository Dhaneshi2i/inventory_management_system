import React from 'react';
import { motion } from 'framer-motion';
import { 
  ChartBarIcon
} from '@heroicons/react/24/outline';
import { Inventory, Warehouse } from '@/types';

interface InventoryChartProps {
  inventory: Inventory[];
  warehouses: Warehouse[];
  loading: boolean;
}

const InventoryChart: React.FC<InventoryChartProps> = ({ 
  inventory, 
  warehouses, 
  loading 
}) => {
  // Calculate chart data
  const stockByWarehouse = warehouses?.map(warehouse => {
    const warehouseInventory = inventory.filter(item => item.warehouse.id === warehouse.id);
    const totalQuantity = warehouseInventory.reduce((sum, item) => sum + item.quantity, 0);
    const totalValue = warehouseInventory.reduce((sum, item) => {
      const value = parseFloat(item.stock_value);
      return sum + (isNaN(value) ? 0 : value);
    }, 0);
    
    return {
      name: warehouse.name,
      quantity: totalQuantity,
      value: totalValue,
      utilization: warehouse.current_utilization,
      capacity: warehouse.capacity,
    };
  });

  const stockByStatus = [
    {
      name: 'In Stock',
      value: inventory.filter(item => item.stock_status === 'in_stock').length,
      color: 'bg-green-500',
    },
    {
      name: 'Low Stock',
      value: inventory.filter(item => item.stock_status === 'low_stock').length,
      color: 'bg-yellow-500',
    },
    {
      name: 'Out of Stock',
      value: inventory.filter(item => item.stock_status === 'out_of_stock').length,
      color: 'bg-red-500',
    },
  ];

  const topProducts = inventory
    .sort((a, b) => {
      const valueA = parseFloat(a.stock_value);
      const valueB = parseFloat(b.stock_value);
      return valueB - valueA;
    })
    .slice(0, 5);

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="animate-pulse">
          <div className="h-4 bg-gray-200 rounded w-1/3 mb-4"></div>
          <div className="space-y-3">
            {[...Array(3)].map((_, i) => (
              <div key={i} className="h-20 bg-gray-200 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200">
      {/* Header */}
      <div className="px-6 py-4 border-b border-gray-200">
        <div className="flex items-center">
          <ChartBarIcon className="h-5 w-5 text-blue-500 mr-2" />
          <h3 className="text-lg font-medium text-gray-900">Inventory Analytics</h3>
        </div>
      </div>

      <div className="p-6 space-y-6">
        {/* Stock Status Distribution */}
        <div>
          <h4 className="text-sm font-medium text-gray-900 mb-3">Stock Status Distribution</h4>
          <div className="space-y-2">
            {stockByStatus.map((status, index) => (
              <motion.div
                key={status.name}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.3, delay: index * 0.1 }}
                className="flex items-center justify-between"
              >
                <div className="flex items-center">
                  <div className={`w-3 h-3 rounded-full ${status.color} mr-2`} />
                  <span className="text-sm text-gray-600">{status.name}</span>
                </div>
                <span className="text-sm font-medium text-gray-900">{status.value}</span>
              </motion.div>
            ))}
          </div>
        </div>

        {/* Warehouse Utilization */}
        <div>
          <h4 className="text-sm font-medium text-gray-900 mb-3">Warehouse Utilization</h4>
          <div className="space-y-3">
            {stockByWarehouse.map((warehouse, index) => (
              <motion.div
                key={warehouse.name}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3, delay: index * 0.1 }}
                className="space-y-1"
              >
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-600 truncate">{warehouse.name}</span>
                  <span className="text-gray-900 font-medium">
                    {warehouse.quantity} items
                  </span>
                </div>
                <div className="bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-blue-500 h-2 rounded-full transition-all duration-300"
                    style={{
                      width: `${Math.min((warehouse.quantity / warehouse.capacity) * 100, 100)}%`
                    }}
                  />
                </div>
                <div className="flex justify-between text-xs text-gray-500">
                  <span>Capacity: {warehouse.capacity}</span>
                  <span>Utilization: {Math.round((warehouse.quantity / warehouse.capacity) * 100)}%</span>
                </div>
              </motion.div>
            ))}
          </div>
        </div>

        {/* Top Products by Value */}
        <div>
          <h4 className="text-sm font-medium text-gray-900 mb-3">Top Products by Value</h4>
          <div className="space-y-2">
            {topProducts.map((product, index) => (
              <motion.div
                key={product.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.3, delay: index * 0.1 }}
                className="flex items-center justify-between p-2 bg-gray-50 rounded"
              >
                <div className="flex-1 min-w-0">
                  <div className="text-sm font-medium text-gray-900 truncate">
                    {product.product.name}
                  </div>
                  <div className="text-xs text-gray-500">
                    SKU: {product.product.sku} • {product.warehouse.name}
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-sm font-medium text-gray-900">
                    {product.stock_value}
                  </div>
                  <div className="text-xs text-gray-500">
                    {product.quantity} units
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-2 gap-4 pt-4 border-t border-gray-200">
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-600">
              {inventory.length}
            </div>
            <div className="text-xs text-gray-500">Total Items</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-green-600">
              ${inventory.reduce((sum, item) => {
                const value = parseFloat(item.stock_value);
                return sum + (isNaN(value) ? 0 : value);
              }, 0).toLocaleString()}
            </div>
            <div className="text-xs text-gray-500">Total Value</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default InventoryChart; 