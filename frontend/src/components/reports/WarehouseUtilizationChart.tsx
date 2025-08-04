import React from 'react';

interface WarehouseUtilizationChartProps {
  warehouses: any[];
}

const WarehouseUtilizationChart: React.FC<WarehouseUtilizationChartProps> = ({
  warehouses: _warehouses,
}) => {
  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <h3 className="text-lg font-medium text-gray-900 mb-4">Warehouse Utilization</h3>
      <div className="text-center text-gray-500">
        <p>Chart component coming soon...</p>
      </div>
    </div>
  );
};

export default WarehouseUtilizationChart; 