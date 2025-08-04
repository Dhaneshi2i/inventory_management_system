import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Inventory } from '@/types';

interface TopProductsChartProps {
  inventory: Inventory[];
}

const TopProductsChart: React.FC<TopProductsChartProps> = ({
  inventory: _inventory,
}) => {
  // Mock data for top products by value (adjusted for better visualization)
  const data = [
    { name: 'Laptop', value: 500, quantity: 100, category: 'Electronics' },
    { name: 'Smartphone', value: 350, quantity: 200, category: 'Electronics' },
    { name: 'Tablet', value: 200, quantity: 150, category: 'Electronics' },
    { name: 'Headphones', value: 150, quantity: 300, category: 'Electronics' },
    { name: 'Jeans', value: 125, quantity: 500, category: 'Clothing' },
    { name: 'Sneakers', value: 100, quantity: 250, category: 'Clothing' },
  ];

  return (
    <div className="h-64">
      <div className="text-center mb-2">
        <h4 className="text-sm font-medium text-gray-900">Top Products by Value</h4>
        <p className="text-xs text-gray-500">Values in thousands ($K)</p>
      </div>
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} layout="horizontal">
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis type="number" />
          <YAxis type="category" dataKey="name" width={80} />
          <Tooltip 
            formatter={(value, name) => [
              name === 'value' ? `$${(Number(value) * 1000).toLocaleString()}` : value,
              name === 'value' ? 'Total Value (K)' : 'Quantity'
            ]}
            labelFormatter={(label) => `Product: ${label}`}
          />
          <Bar dataKey="value" fill="#10B981" name="Total Value" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};

export default TopProductsChart; 