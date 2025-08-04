import React from 'react';
import { Inventory } from '@/types';

interface InventoryTurnoverChartProps {
  inventory: Inventory[];
  dateRange: string;
}

const InventoryTurnoverChart: React.FC<InventoryTurnoverChartProps> = ({
  inventory,
  dateRange,
}) => {
  return (
    <div className="h-64 flex items-center justify-center">
      <div className="text-center">
        <div className="text-gray-400 text-sm mb-2">Inventory Turnover Chart</div>
        <div className="text-xs text-gray-500">
          Chart showing inventory turnover analysis over {dateRange} days
        </div>
      </div>
    </div>
  );
};

export default InventoryTurnoverChart; 