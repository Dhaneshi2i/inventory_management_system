import React, { useState } from 'react';
import { 
  MagnifyingGlassIcon, 
  ExclamationTriangleIcon,
  XCircleIcon,
  CheckCircleIcon,
  PencilIcon
} from '@heroicons/react/24/outline';
import { Inventory } from '@/types';
import LoadingSpinner from '../LoadingSpinner';
import DataTable from '../DataTable';

interface InventoryDashboardProps {
  inventory: Inventory[];
  loading: boolean;
  onStockAdjustment: (inventory: Inventory) => void;
}

const InventoryDashboard: React.FC<InventoryDashboardProps> = ({
  inventory,
  loading,
  onStockAdjustment,
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [showLowStock, setShowLowStock] = useState(false);
  const [showOutOfStock, setShowOutOfStock] = useState(false);

  // Filter inventory based on search and filters
  const filteredInventory = inventory.filter((item) => {
    const matchesSearch = searchTerm === '' || 
      item.product.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      item.product.sku.toLowerCase().includes(searchTerm.toLowerCase()) ||
      item.warehouse.name.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesLowStock = !showLowStock || item.is_low_stock;
    const matchesOutOfStock = !showOutOfStock || item.is_out_of_stock;
    
    return matchesSearch && matchesLowStock && matchesOutOfStock;
  });

  const getStockStatusColor = (status: string) => {
    switch (status) {
      case 'in_stock':
        return 'bg-green-100 text-green-800';
      case 'low_stock':
        return 'bg-yellow-100 text-yellow-800';
      case 'out_of_stock':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getStockStatusIcon = (status: string) => {
    switch (status) {
      case 'in_stock':
        return <CheckCircleIcon className="h-4 w-4" />;
      case 'low_stock':
        return <ExclamationTriangleIcon className="h-4 w-4" />;
      case 'out_of_stock':
        return <XCircleIcon className="h-4 w-4" />;
      default:
        return null;
    }
  };

  const columns = [
    {
      key: 'product',
      label: 'Product',
      render: (_value: any, item: Inventory) => (
        <div>
          <div className="font-medium text-gray-900">{item.product.name}</div>
          <div className="text-sm text-gray-500">SKU: {item.product.sku}</div>
        </div>
      ),
    },
    {
      key: 'warehouse',
      label: 'Warehouse',
      render: (_value: any, item: Inventory) => (
        <div className="text-sm text-gray-900">{item.warehouse.name}</div>
      ),
    },
    {
      key: 'quantity',
      label: 'Quantity',
      render: (_value: any, item: Inventory) => (
        <div className="text-right">
          <div className="font-medium text-gray-900">{item.quantity}</div>
          <div className="text-xs text-gray-500">
            Available: {item.available_quantity}
          </div>
        </div>
      ),
    },
    {
      key: 'stock_status',
      label: 'Status',
      render: (_value: any, item: Inventory) => (
        <div className="flex items-center">
          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStockStatusColor(item.stock_status)}`}>
            {getStockStatusIcon(item.stock_status)}
            <span className="ml-1 capitalize">{item.stock_status.replace('_', ' ')}</span>
          </span>
        </div>
      ),
    },
    {
      key: 'stock_value',
      label: 'Value',
      render: (_value: any, item: Inventory) => (
        <div className="text-right">
          <div className="font-medium text-gray-900">{item.stock_value}</div>
          <div className="text-xs text-gray-500">
            Reorder: {item.reorder_point}
          </div>
        </div>
      ),
    },
    {
      key: 'last_updated',
      label: 'Last Updated',
      render: (_value: any, item: Inventory) => (
        <div className="text-sm text-gray-500">
          {new Date(item.last_updated).toLocaleDateString()}
        </div>
      ),
    },
    {
      key: 'actions',
      label: 'Actions',
      render: (_value: any, item: Inventory) => (
        <div className="flex items-center space-x-2">
          <button
            onClick={() => onStockAdjustment(item)}
            className="inline-flex items-center px-2 py-1 border border-gray-300 shadow-sm text-xs font-medium rounded text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            <PencilIcon className="h-3 w-3 mr-1" />
            Adjust
          </button>
        </div>
      ),
    },
  ];

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
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between space-y-3 sm:space-y-0">
          <div>
            <h3 className="text-lg font-medium text-gray-900">Inventory Items</h3>
            <p className="text-sm text-gray-500">
              {filteredInventory.length} of {inventory.length} items
            </p>
          </div>
          
          <div className="flex items-center space-x-3">
            {/* Search */}
            <div className="relative">
              <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <input
                type="text"
                placeholder="Search products..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10 pr-4 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>

            {/* Filters */}
            <div className="flex items-center space-x-2">
              <button
                onClick={() => setShowLowStock(!showLowStock)}
                className={`inline-flex items-center px-3 py-2 border text-sm font-medium rounded-md ${
                  showLowStock
                    ? 'border-yellow-300 bg-yellow-50 text-yellow-700'
                    : 'border-gray-300 bg-white text-gray-700 hover:bg-gray-50'
                }`}
              >
                <ExclamationTriangleIcon className="h-4 w-4 mr-1" />
                Low Stock
              </button>
              
              <button
                onClick={() => setShowOutOfStock(!showOutOfStock)}
                className={`inline-flex items-center px-3 py-2 border text-sm font-medium rounded-md ${
                  showOutOfStock
                    ? 'border-red-300 bg-red-50 text-red-700'
                    : 'border-gray-300 bg-white text-gray-700 hover:bg-gray-50'
                }`}
              >
                <XCircleIcon className="h-4 w-4 mr-1" />
                Out of Stock
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Summary Stats */}
      <div className="px-6 py-3 bg-gray-50 border-b border-gray-200">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
          <div>
            <span className="text-gray-500">Total Items:</span>
            <span className="ml-2 font-medium">{inventory.length}</span>
          </div>
          <div>
            <span className="text-gray-500">Low Stock:</span>
            <span className="ml-2 font-medium text-yellow-600">
              {inventory.filter(item => item.is_low_stock).length}
            </span>
          </div>
          <div>
            <span className="text-gray-500">Out of Stock:</span>
            <span className="ml-2 font-medium text-red-600">
              {inventory.filter(item => item.is_out_of_stock).length}
            </span>
          </div>
          <div>
            <span className="text-gray-500">Total Value:</span>
            <span className="ml-2 font-medium">
              ${inventory.reduce((sum, item) => {
                const value = parseFloat(item.stock_value);
                return sum + (isNaN(value) ? 0 : value);
              }, 0).toLocaleString()}
            </span>
          </div>
        </div>
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <DataTable
          data={filteredInventory}
          columns={columns}
          loading={loading}
          emptyMessage="No inventory items found"
        />
      </div>
    </div>
  );
};

export default InventoryDashboard; 