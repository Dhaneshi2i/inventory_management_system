import React from 'react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Inventory } from '@/types';

interface InventoryTurnoverChartProps {
  inventory: Inventory[];
  dateRange?: string;
}

const InventoryTurnoverChart: React.FC<InventoryTurnoverChartProps> = ({
  inventory: _inventory,
  dateRange: _dateRange = '30',
}) => {
  // Mock data for inventory turnover
  const data = [
    { week: 'Week 1', turnover: 2.5, sales: 125000, purchases: 100000 },
    { week: 'Week 2', turnover: 3.2, sales: 160000, purchases: 120000 },
    { week: 'Week 3', turnover: 2.8, sales: 140000, purchases: 110000 },
    { week: 'Week 4', turnover: 3.5, sales: 175000, purchases: 130000 },
  ];

  return (
    <div className="h-64">
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="week" />
          <YAxis />
          <Tooltip 
            formatter={(value, name) => [
              name === 'turnover' ? value : `$${value.toLocaleString()}`,
              name === 'turnover' ? 'Turnover Rate' : 
              name === 'sales' ? 'Sales' : 'Purchases'
            ]}
          />
          <Area 
            type="monotone" 
            dataKey="turnover" 
            stackId="1"
            stroke="#3B82F6" 
            fill="#3B82F6" 
            fillOpacity={0.6}
            name="Turnover Rate"
          />
          <Area 
            type="monotone" 
            dataKey="sales" 
            stackId="2"
            stroke="#10B981" 
            fill="#10B981" 
            fillOpacity={0.6}
            name="Sales"
          />
          <Area 
            type="monotone" 
            dataKey="purchases" 
            stackId="3"
            stroke="#F59E0B" 
            fill="#F59E0B" 
            fillOpacity={0.6}
            name="Purchases"
          />
        </AreaChart>
      </ResponsiveContainer>
      <div className="mt-2 text-center">
        <div className="text-sm text-gray-600">
          Average Turnover Rate: {(data.reduce((sum, item) => sum + item.turnover, 0) / data.length).toFixed(1)}
        </div>
      </div>
    </div>
  );
};

export default InventoryTurnoverChart; 