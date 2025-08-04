import React from 'react';
import { Inventory } from '@/types';

interface TopProductsChartProps {
  inventory: Inventory[];
}

const TopProductsChart: React.FC<TopProductsChartProps> = ({
  inventory: _inventory,
}) => {
  return (
    <div className="h-64 flex items-center justify-center">
      <div className="text-center">
        <div className="text-gray-400 text-sm mb-2">Top Products Chart</div>
        <div className="text-xs text-gray-500">
          Chart showing top products by inventory value
        </div>
      </div>
    </div>
  );
};

export default TopProductsChart; 