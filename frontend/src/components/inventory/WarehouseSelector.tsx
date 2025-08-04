import React from 'react';
import { motion } from 'framer-motion';
import { BuildingOfficeIcon, ChevronDownIcon } from '@heroicons/react/24/outline';
import { Warehouse } from '@/types';
import { LoadingSpinner } from '@/components/LoadingSpinner';

interface WarehouseSelectorProps {
  warehouses: Warehouse[];
  selectedWarehouse: string;
  onWarehouseChange: (warehouseId: string) => void;
  loading: boolean;
}

const WarehouseSelector: React.FC<WarehouseSelectorProps> = ({
  warehouses,
  selectedWarehouse,
  onWarehouseChange,
  loading,
}) => {
  const selectedWarehouseData = warehouses?.data?.results?.find(w => w.id === selectedWarehouse);

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
        <div className="animate-pulse">
          <div className="h-4 bg-gray-200 rounded w-1/4 mb-2"></div>
          <div className="h-10 bg-gray-200 rounded"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <div className="flex items-center">
            <BuildingOfficeIcon className="h-5 w-5 text-gray-400 mr-2" />
            <span className="text-sm font-medium text-gray-700">Warehouse:</span>
          </div>
          
          <div className="relative">
            <select
              value={selectedWarehouse}
              onChange={(e) => onWarehouseChange(e.target.value)}
              className="appearance-none bg-white border border-gray-300 rounded-md px-3 py-2 pr-8 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="all">All Warehouses</option>
              {warehouses?.data?.results?.map((warehouse) => (
                <option key={warehouse.id} value={warehouse.id}>
                  {warehouse.name}
                </option>
              ))}
            </select>
            <ChevronDownIcon className="absolute right-2 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400 pointer-events-none" />
          </div>
        </div>

        {selectedWarehouseData && selectedWarehouse !== 'all' && (
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            className="flex items-center space-x-4 text-sm text-gray-600"
          >
            <div className="flex items-center space-x-2">
              <span>Capacity:</span>
              <span className="font-medium">
                {selectedWarehouseData.current_utilization} / {selectedWarehouseData.capacity}
              </span>
            </div>
            <div className="flex items-center space-x-2">
              <span>Items:</span>
              <span className="font-medium">{selectedWarehouseData.inventory_count}</span>
            </div>
            <div className="flex items-center space-x-2">
              <span>Value:</span>
              <span className="font-medium">{selectedWarehouseData.total_inventory_value}</span>
            </div>
          </motion.div>
        )}
      </div>

      {/* Warehouse Cards for Quick Selection */}
      {warehouses.length > 0 && (
        <div className="mt-4 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
          <motion.button
            onClick={() => onWarehouseChange('all')}
            className={`p-3 rounded-lg border-2 text-left transition-all ${
              selectedWarehouse === 'all'
                ? 'border-blue-500 bg-blue-50'
                : 'border-gray-200 bg-gray-50 hover:border-gray-300 hover:bg-gray-100'
            }`}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            <div className="flex items-center justify-between">
              <div>
                <h3 className="font-medium text-gray-900">All Warehouses</h3>
                <p className="text-sm text-gray-500">
                  {warehouses.length} warehouse{warehouses.length !== 1 ? 's' : ''}
                </p>
              </div>
              <BuildingOfficeIcon className="h-5 w-5 text-gray-400" />
            </div>
          </motion.button>

          {warehouses?.data?.results?.slice(0, 3).map((warehouse) => (
            <motion.button
              key={warehouse.id}
              onClick={() => onWarehouseChange(warehouse.id)}
              className={`p-3 rounded-lg border-2 text-left transition-all ${
                selectedWarehouse === warehouse.id
                  ? 'border-blue-500 bg-blue-50'
                  : 'border-gray-200 bg-gray-50 hover:border-gray-300 hover:bg-gray-100'
              }`}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="font-medium text-gray-900 truncate">{warehouse.name}</h3>
                  <p className="text-sm text-gray-500">
                    {warehouse.inventory_count} items
                  </p>
                </div>
                <div className="text-right">
                  <div className="text-xs text-gray-500">Utilization</div>
                  <div className="text-sm font-medium text-gray-900">
                    {warehouse.current_utilization}
                  </div>
                </div>
              </div>
            </motion.button>
          ))}
        </div>
      )}
    </div>
  );
};

export default WarehouseSelector; 