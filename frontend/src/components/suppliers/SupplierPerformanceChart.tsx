import React from 'react';
import { Supplier } from '@/types';

interface SupplierPerformanceChartProps {
  suppliers: Supplier[];
}

const SupplierPerformanceChart: React.FC<SupplierPerformanceChartProps> = ({
  suppliers: _suppliers,
}) => {
  return (
    <div className="h-64 flex items-center justify-center">
      <div className="text-center">
        <div className="text-gray-400 text-sm mb-2">Supplier Performance Chart</div>
        <div className="text-xs text-gray-500">
          Chart showing supplier performance metrics and analytics
        </div>
      </div>
    </div>
  );
};

export default SupplierPerformanceChart; 