import React from 'react';
import { Inventory } from '@/types';

interface StockAgingReportProps {
  inventory: Inventory[];
}

const StockAgingReport: React.FC<StockAgingReportProps> = ({
  inventory: _inventory,
}) => {
  return (
    <div className="h-64 flex items-center justify-center">
      <div className="text-center">
        <div className="text-gray-400 text-sm mb-2">Stock Aging Report</div>
        <div className="text-xs text-gray-500">
          Report showing inventory aging analysis
        </div>
      </div>
    </div>
  );
};

export default StockAgingReport; 