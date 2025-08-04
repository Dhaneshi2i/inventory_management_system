import React from 'react';
import { motion } from 'framer-motion';
import { 
  EyeIcon,
  PencilIcon,
  TrashIcon,
  BuildingOfficeIcon
} from '@heroicons/react/24/outline';
import { Warehouse } from '@/types';
import LoadingSpinner from '../LoadingSpinner';

interface WarehouseListProps {
  warehouses: Warehouse[];
  loading: boolean;
  onViewWarehouse: (warehouse: Warehouse) => void;
  onEditWarehouse: (warehouse: Warehouse) => void;
  onDeleteWarehouse: (warehouseId: string) => void;
  searchTerm: string;
}

const WarehouseList: React.FC<WarehouseListProps> = ({
  warehouses,
  loading,
  onViewWarehouse,
  onEditWarehouse,
  onDeleteWarehouse,
  searchTerm,
}) => {
  const filteredWarehouses = warehouses.filter((warehouse) => {
    const matchesSearch = searchTerm === '' || 
      warehouse.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      warehouse.address.toLowerCase().includes(searchTerm.toLowerCase()) ||
      warehouse.manager.toLowerCase().includes(searchTerm.toLowerCase());
    
    return matchesSearch;
  });

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="p-6">
          <LoadingSpinner size="lg" />
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200">
      {/* Header */}
      <div className="px-6 py-4 border-b border-gray-200">
        <h3 className="text-lg font-medium text-gray-900">Warehouses</h3>
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Warehouse
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Manager
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Capacity
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Utilization
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Inventory Value
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Status
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {filteredWarehouses.length === 0 ? (
              <tr>
                <td colSpan={7} className="px-6 py-12 text-center">
                  <BuildingOfficeIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <h4 className="text-lg font-medium text-gray-900 mb-2">No Warehouses</h4>
                  <p className="text-sm text-gray-500">
                    {searchTerm ? 'No warehouses match your search criteria.' : 'No warehouses found.'}
                  </p>
                </td>
              </tr>
            ) : (
              filteredWarehouses.map((warehouse, index) => (
                <motion.tr
                  key={warehouse.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.3, delay: index * 0.05 }}
                  className="hover:bg-gray-50"
                >
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-gray-900">{warehouse.name}</div>
                    <div className="text-sm text-gray-500">{warehouse.address}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900">{warehouse.manager}</div>
                    <div className="text-sm text-gray-500">{warehouse.contact_email}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900">{warehouse.capacity.toLocaleString()}</div>
                    <div className="text-sm text-gray-500">
                      {warehouse.available_capacity.toLocaleString()} available
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900">{warehouse.current_utilization}</div>
                    <div className="text-sm text-gray-500">{warehouse.inventory_count} items</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-gray-900">{warehouse.total_inventory_value}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                      warehouse.is_active
                        ? 'bg-green-100 text-green-800'
                        : 'bg-red-100 text-red-800'
                    }`}>
                      {warehouse.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <div className="flex items-center space-x-2">
                      <button
                        onClick={() => onViewWarehouse(warehouse)}
                        className="text-blue-600 hover:text-blue-900"
                      >
                        <EyeIcon className="h-4 w-4" />
                      </button>
                      <button
                        onClick={() => onEditWarehouse(warehouse)}
                        className="text-green-600 hover:text-green-900"
                      >
                        <PencilIcon className="h-4 w-4" />
                      </button>
                      <button
                        onClick={() => onDeleteWarehouse(warehouse.id)}
                        className="text-red-600 hover:text-red-900"
                      >
                        <TrashIcon className="h-4 w-4" />
                      </button>
                    </div>
                  </td>
                </motion.tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default WarehouseList; 