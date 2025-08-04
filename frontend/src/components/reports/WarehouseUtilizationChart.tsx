import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

interface WarehouseUtilizationChartProps {
  warehouses: any[];
}

const WarehouseUtilizationChart: React.FC<WarehouseUtilizationChartProps> = ({
  warehouses: _warehouses,
}) => {
  // Mock data for warehouse utilization
  const data = [
    { name: 'Main Warehouse', capacity: 10000, used: 7500, utilization: 75 },
    { name: 'Secondary Warehouse', capacity: 5000, used: 2250, utilization: 45 },
    { name: 'North Warehouse', capacity: 8000, used: 6400, utilization: 80 },
    { name: 'South Warehouse', capacity: 6000, used: 1800, utilization: 30 },
  ];

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <h3 className="text-lg font-medium text-gray-900 mb-4">Warehouse Utilization</h3>
      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" />
            <YAxis />
            <Tooltip 
              formatter={(value, name) => [
                name === 'capacity' || name === 'used' ? `${value.toLocaleString()} sq ft` : `${value}%`,
                name === 'capacity' ? 'Capacity' : 
                name === 'used' ? 'Used Space' : 'Utilization %'
              ]}
            />
            <Legend />
            <Bar dataKey="capacity" fill="#E5E7EB" name="Capacity" />
            <Bar dataKey="used" fill="#3B82F6" name="Used Space" />
          </BarChart>
        </ResponsiveContainer>
      </div>
      <div className="mt-4 grid grid-cols-2 gap-4">
        {data.map((warehouse) => (
          <div key={warehouse.name} className="text-center">
            <div className="text-sm font-medium text-gray-900">{warehouse.name}</div>
            <div className="text-lg font-bold text-blue-600">{warehouse.utilization}%</div>
            <div className="text-xs text-gray-500">
              {warehouse.used.toLocaleString()} / {warehouse.capacity.toLocaleString()} sq ft
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default WarehouseUtilizationChart; 