import React from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts';
import { Inventory } from '@/types';

interface StockAgingReportProps {
  inventory: Inventory[];
}

const StockAgingReport: React.FC<StockAgingReportProps> = ({
  inventory: _inventory,
}) => {
  // Mock data for stock aging analysis
  const data = [
    { name: '0-30 days', value: 45, color: '#10B981' },
    { name: '31-60 days', value: 25, color: '#F59E0B' },
    { name: '61-90 days', value: 15, color: '#EF4444' },
    { name: '90+ days', value: 15, color: '#8B5CF6' },
  ];

  const totalItems = data.reduce((sum, item) => sum + item.value, 0);

  return (
    <div className="h-64">
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            labelLine={false}
            label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
            outerRadius={80}
            fill="#8884d8"
            dataKey="value"
          >
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.color} />
            ))}
          </Pie>
          <Tooltip 
            formatter={(value, name) => [
              `${value} items`,
              name
            ]}
          />
          <Legend />
        </PieChart>
      </ResponsiveContainer>
      <div className="mt-4 text-center">
        <div className="text-sm text-gray-600">Total Items: {totalItems}</div>
        <div className="text-xs text-gray-500 mt-1">
          Aging analysis based on last movement date
        </div>
      </div>
    </div>
  );
};

export default StockAgingReport; 