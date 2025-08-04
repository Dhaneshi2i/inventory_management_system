import React from 'react';
import { Inventory, Warehouse } from '@/types';

interface ReorderRecommendationsProps {
  inventory: Inventory[];
  warehouses: Warehouse[];
}

const ReorderRecommendations: React.FC<ReorderRecommendationsProps> = ({
  inventory: _inventory,
  warehouses: _warehouses,
}) => {
  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200">
      <div className="px-6 py-4 border-b border-gray-200">
        <h3 className="text-lg font-medium text-gray-900">Reorder Recommendations</h3>
      </div>
      <div className="p-6">
        <div className="text-center">
          <div className="text-gray-400 text-sm mb-2">Reorder Recommendations</div>
          <div className="text-xs text-gray-500">
            AI-powered recommendations for inventory reordering
          </div>
        </div>
      </div>
    </div>
  );
};

export default ReorderRecommendations; 