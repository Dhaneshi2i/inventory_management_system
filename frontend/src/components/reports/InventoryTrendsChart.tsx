import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

interface InventoryTrendsChartProps {
  inventory: any[];
}

const InventoryTrendsChart: React.FC<InventoryTrendsChartProps> = ({
  inventory: _inventory,
}) => {
  // Mock data for inventory trends over time (normalized for better visualization)
  const data = [
    { month: 'Jan', total_value: 125, total_items: 450, low_stock: 12 },
    { month: 'Feb', total_value: 138, total_items: 480, low_stock: 8 },
    { month: 'Mar', total_value: 142, total_items: 520, low_stock: 15 },
    { month: 'Apr', total_value: 135, total_items: 490, low_stock: 10 },
    { month: 'May', total_value: 148, total_items: 540, low_stock: 6 },
    { month: 'Jun', total_value: 155, total_items: 580, low_stock: 9 },
  ];

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <h3 className="text-lg font-medium text-gray-900 mb-4">Inventory Trends</h3>
      <div className="text-center mb-2">
        <p className="text-xs text-gray-500">Values in thousands ($K)</p>
      </div>
      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="month" />
            <YAxis />
            <Tooltip 
              formatter={(value, name) => [
                name === 'total_value' ? `$${(Number(value) * 1000).toLocaleString()}` : value,
                name === 'total_value' ? 'Total Value (K)' : 
                name === 'total_items' ? 'Total Items' : 'Low Stock Items'
              ]}
            />
            <Legend />
            <Line 
              type="monotone" 
              dataKey="total_value" 
              stroke="#3B82F6" 
              strokeWidth={2}
              name="Total Value"
            />
            <Line 
              type="monotone" 
              dataKey="total_items" 
              stroke="#10B981" 
              strokeWidth={2}
              name="Total Items"
            />
            <Line 
              type="monotone" 
              dataKey="low_stock" 
              stroke="#EF4444" 
              strokeWidth={2}
              name="Low Stock Items"
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export default InventoryTrendsChart; 