import React from 'react';
import { Warehouse } from '@/types';

interface WarehouseUtilizationChartProps {
  warehouses: Warehouse[];
}

const WarehouseUtilizationChart: React.FC<WarehouseUtilizationChartProps> = ({
  warehouses,
}) => {
  return (
    <div className="h-64 flex items-center justify-center">
      <div className="text-center">
        <div className="text-gray-400 text-sm mb-2">Warehouse Utilization Chart</div>
        <div className="text-xs text-gray-500">
          Chart showing capacity utilization across warehouses
        </div>
      </div>
    </div>
  );
};

export default WarehouseUtilizationChart; 