import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  ArrowUpIcon,
  ArrowDownIcon,
  ArrowRightIcon,
  ClockIcon,
  MagnifyingGlassIcon
} from '@heroicons/react/24/outline';
import { StockMovement } from '@/types';

interface StockMovementHistoryProps {
  movements: StockMovement[];
  loading: boolean;
  warehouseId: string;
}

const StockMovementHistory: React.FC<StockMovementHistoryProps> = ({ 
  movements, 
  loading, 
    warehouseId: _warehouseId
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [filterType, setFilterType] = useState<string>('all');
  
  const filteredMovements = movements.filter((movement) => {
    const matchesSearch = searchTerm === '' || 
      movement.product.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      movement.product.sku.toLowerCase().includes(searchTerm.toLowerCase()) ||
      movement.warehouse.name.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesType = filterType === 'all' || movement.movement_type === filterType;
    
    return matchesSearch && matchesType;
  });

  const getMovementIcon = (type: string) => {
    switch (type) {
      case 'in':
        return <ArrowUpIcon className="h-4 w-4 text-green-500" />;
      case 'out':
        return <ArrowDownIcon className="h-4 w-4 text-red-500" />;
      case 'transfer':
        return <ArrowRightIcon className="h-4 w-4 text-blue-500" />;
      case 'adjustment':
        return <ClockIcon className="h-4 w-4 text-yellow-500" />;
      default:
        return <ClockIcon className="h-4 w-4 text-gray-500" />;
    }
  };

  const getMovementColor = (type: string) => {
    switch (type) {
      case 'in':
        return 'bg-green-50 border-green-200';
      case 'out':
        return 'bg-red-50 border-red-200';
      case 'transfer':
        return 'bg-blue-50 border-blue-200';
      case 'adjustment':
        return 'bg-yellow-50 border-yellow-200';
      default:
        return 'bg-gray-50 border-gray-200';
    }
  };

  const getMovementTextColor = (type: string) => {
    switch (type) {
      case 'in':
        return 'text-green-700';
      case 'out':
        return 'text-red-700';
      case 'transfer':
        return 'text-blue-700';
      case 'adjustment':
        return 'text-yellow-700';
      default:
        return 'text-gray-700';
    }
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="p-6">
          <div className="animate-pulse">
            <div className="h-4 bg-gray-200 rounded w-1/3 mb-4"></div>
            <div className="space-y-3">
              {[...Array(5)].map((_, i) => (
                <div key={i} className="h-16 bg-gray-200 rounded"></div>
              ))}
            </div>
          </div>
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
            <h3 className="text-lg font-medium text-gray-900">Stock Movement History</h3>
            <p className="text-sm text-gray-500">
              {filteredMovements.length} of {movements.length} movements
            </p>
          </div>
          
          <div className="flex items-center space-x-3">
            {/* Search */}
            <div className="relative">
              <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <input
                type="text"
                placeholder="Search movements..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10 pr-4 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>

            {/* Filter */}
            <select
              value={filterType}
              onChange={(e) => setFilterType(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="all">All Types</option>
              <option value="in">Stock In</option>
              <option value="out">Stock Out</option>
              <option value="transfer">Transfer</option>
              <option value="adjustment">Adjustment</option>
            </select>
          </div>
        </div>
      </div>

      {/* Movements List */}
      <div className="divide-y divide-gray-200">
        {filteredMovements.length === 0 ? (
          <div className="p-6 text-center">
            <ClockIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h4 className="text-lg font-medium text-gray-900 mb-2">No Movements</h4>
            <p className="text-sm text-gray-500">
              {searchTerm || filterType !== 'all' 
                ? 'No movements match your filters.' 
                : 'No stock movements recorded yet.'}
            </p>
          </div>
        ) : (
          filteredMovements.slice(0, 10).map((movement, index) => (
            <motion.div
              key={movement.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3, delay: index * 0.05 }}
              className={`p-4 ${getMovementColor(movement.movement_type)}`}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className="flex-shrink-0">
                    {getMovementIcon(movement.movement_type)}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center space-x-2">
                      <p className="text-sm font-medium text-gray-900 truncate">
                        {movement.product.name}
                      </p>
                      <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${getMovementTextColor(movement.movement_type)}`}>
                        {movement.movement_type.toUpperCase()}
                      </span>
                    </div>
                    <div className="mt-1 flex items-center space-x-4 text-xs text-gray-500">
                      <span>SKU: {movement.product.sku}</span>
                      <span>Warehouse: {movement.warehouse.name}</span>
                      {movement.reference_type && (
                        <span>Ref: {movement.reference_type} #{movement.reference_id}</span>
                      )}
                    </div>
                    {movement.notes && (
                      <p className="mt-1 text-xs text-gray-600 italic">
                        "{movement.notes}"
                      </p>
                    )}
                  </div>
                </div>
                
                <div className="flex items-center space-x-4">
                  <div className="text-right">
                    <div className={`text-sm font-medium ${getMovementTextColor(movement.movement_type)}`}>
                      {movement.movement_type === 'out' ? '-' : '+'}{movement.quantity}
                    </div>
                    <div className="text-xs text-gray-500">
                      {movement.movement_value}
                    </div>
                  </div>
                  <div className="text-right text-xs text-gray-500">
                    <div>{new Date(movement.created_at).toLocaleDateString()}</div>
                    <div>{new Date(movement.created_at).toLocaleTimeString()}</div>
                  </div>
                </div>
              </div>
            </motion.div>
          ))
        )}
      </div>

      {/* Footer */}
      {filteredMovements.length > 10 && (
        <div className="px-6 py-3 bg-gray-50 border-t border-gray-200">
          <div className="flex items-center justify-between">
            <p className="text-sm text-gray-500">
              Showing 10 of {filteredMovements.length} movements
            </p>
            <button className="text-sm text-blue-600 hover:text-blue-800 font-medium">
              View All Movements
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default StockMovementHistory; 