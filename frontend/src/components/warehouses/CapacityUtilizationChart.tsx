import React from 'react';
import { Warehouse } from '@/types';

interface CapacityUtilizationChartProps {
  warehouses: Warehouse[];
}

const CapacityUtilizationChart: React.FC<CapacityUtilizationChartProps> = ({
  warehouses: _warehouses,
}) => {
  return (
    <div className="h-64 flex items-center justify-center">
      <div className="text-center">
        <div className="text-gray-400 text-sm mb-2">Capacity Utilization Chart</div>
        <div className="text-xs text-gray-500">
          Chart showing warehouse capacity utilization across all warehouses
        </div>
      </div>
    </div>
  );
};

export default CapacityUtilizationChart; 