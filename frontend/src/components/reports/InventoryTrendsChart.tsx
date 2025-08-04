import React from 'react';
import { Inventory } from '@/types';

interface InventoryTrendsChartProps {
  inventory: Inventory[];
  dateRange: string;
}

const InventoryTrendsChart: React.FC<InventoryTrendsChartProps> = ({
  inventory,
  dateRange,
}) => {
  return (
    <div className="h-64 flex items-center justify-center">
      <div className="text-center">
        <div className="text-gray-400 text-sm mb-2">Inventory Trends Chart</div>
        <div className="text-xs text-gray-500">
          Chart showing inventory trends over {dateRange} days
        </div>
      </div>
    </div>
  );
};

export default InventoryTrendsChart; 