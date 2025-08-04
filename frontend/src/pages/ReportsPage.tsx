import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { 
  ChartBarIcon,
  DocumentArrowDownIcon,
  CalendarIcon,
  FunnelIcon,
  PrinterIcon,
  EyeIcon
} from '@heroicons/react/24/outline';


import { apiService } from '@/services/api';
import { DashboardSummary, Inventory, Warehouse, ApiResponse } from '@/types';
import LoadingSpinner from '@/components/LoadingSpinner';

// Components
import InventoryTrendsChart from '@/components/reports/InventoryTrendsChart';
import WarehouseUtilizationChart from '@/components/reports/WarehouseUtilizationChart';
import TopProductsChart from '@/components/reports/TopProductsChart';
import StockAgingReport from '@/components/reports/StockAgingReport';
import InventoryTurnoverChart from '@/components/reports/InventoryTurnoverChart';
import ReorderRecommendations from '@/components/reports/ReorderRecommendations';

const ReportsPage: React.FC = () => {
  const [dateRange, setDateRange] = useState('30');
  const [selectedWarehouse, setSelectedWarehouse] = useState('all');
  const [reportType, setReportType] = useState('overview');

  // Queries
  const { data: dashboardData, isLoading: dashboardLoading } = useQuery({
    queryKey: ['dashboard-summary'],
    queryFn: () => apiService.get<DashboardSummary>('/api/v1/dashboard/summary/'),
  });

  const { data: inventory, isLoading: inventoryLoading } = useQuery({
    queryKey: ['inventory'],
    queryFn: () => apiService.get<ApiResponse<Inventory>>('/api/v1/inventory/'),
  });

  const { data: warehouses, isLoading: warehousesLoading } = useQuery({
    queryKey: ['warehouses'],
    queryFn: () => apiService.get<ApiResponse<Warehouse>>('/api/v1/warehouses/'),
  });

  const handleExportReport = (type: string) => {
    // Simulate report export
    console.log(`Exporting ${type} report...`);
  };

  const handlePrintReport = () => {
    window.print();
  };

  if (dashboardLoading || inventoryLoading || warehousesLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Reports & Analytics</h1>
          <p className="mt-1 text-sm text-gray-500">
            Generate insights and track inventory performance
          </p>
        </div>
        <div className="mt-4 sm:mt-0 flex flex-wrap gap-2">
          <button
            onClick={handlePrintReport}
            className="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
          >
            <PrinterIcon className="h-4 w-4 mr-2" />
            Print
          </button>
          <button
            onClick={() => handleExportReport('inventory')}
            className="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
          >
            <DocumentArrowDownIcon className="h-4 w-4 mr-2" />
            Export
          </button>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between space-y-3 sm:space-y-0">
          <div className="flex items-center space-x-4">
            <div className="flex items-center">
              <CalendarIcon className="h-4 w-4 text-gray-400 mr-2" />
              <span className="text-sm font-medium text-gray-700">Date Range:</span>
            </div>
            <select
              value={dateRange}
              onChange={(e) => setDateRange(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="7">Last 7 days</option>
              <option value="30">Last 30 days</option>
              <option value="90">Last 90 days</option>
              <option value="365">Last year</option>
            </select>

            <div className="flex items-center">
              <FunnelIcon className="h-4 w-4 text-gray-400 mr-2" />
              <span className="text-sm font-medium text-gray-700">Warehouse:</span>
            </div>
            <select
              value={selectedWarehouse}
              onChange={(e) => setSelectedWarehouse(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="all">All Warehouses</option>
              {warehouses?.results?.map((warehouse) => (
                <option key={warehouse.id} value={warehouse.id}>
                  {warehouse.name}
                </option>
              ))}
            </select>
          </div>

          <div className="flex items-center space-x-2">
            <button
              onClick={() => setReportType('overview')}
              className={`px-3 py-2 text-sm font-medium rounded-md ${
                reportType === 'overview'
                  ? 'bg-blue-100 text-blue-700'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              Overview
            </button>
            <button
              onClick={() => setReportType('analytics')}
              className={`px-3 py-2 text-sm font-medium rounded-md ${
                reportType === 'analytics'
                  ? 'bg-blue-100 text-blue-700'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              Analytics
            </button>
            <button
              onClick={() => setReportType('recommendations')}
              className={`px-3 py-2 text-sm font-medium rounded-md ${
                reportType === 'recommendations'
                  ? 'bg-blue-100 text-blue-700'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              Recommendations
            </button>
          </div>
        </div>
      </div>

      {/* Report Content */}
      {reportType === 'overview' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Inventory Trends */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200">
            <div className="px-6 py-4 border-b border-gray-200">
              <h3 className="text-lg font-medium text-gray-900">Inventory Trends</h3>
            </div>
            <div className="p-6">
              <InventoryTrendsChart 
                inventory={inventory?.results || []}
              />
            </div>
          </div>

          {/* Warehouse Utilization */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200">
            <div className="px-6 py-4 border-b border-gray-200">
              <h3 className="text-lg font-medium text-gray-900">Warehouse Utilization</h3>
            </div>
            <div className="p-6">
              <WarehouseUtilizationChart 
                warehouses={warehouses?.results || []}
              />
            </div>
          </div>

          {/* Top Products */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200">
            <div className="px-6 py-4 border-b border-gray-200">
              <h3 className="text-lg font-medium text-gray-900">Top Products by Value</h3>
            </div>
            <div className="p-6">
              <TopProductsChart 
                inventory={inventory?.results || []}
              />
            </div>
          </div>

          {/* Stock Aging */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200">
            <div className="px-6 py-4 border-b border-gray-200">
              <h3 className="text-lg font-medium text-gray-900">Stock Aging Report</h3>
            </div>
            <div className="p-6">
              <StockAgingReport 
                inventory={inventory?.results || []}
              />
            </div>
          </div>
        </div>
      )}

      {reportType === 'analytics' && (
        <div className="space-y-6">
          {/* Inventory Turnover */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200">
            <div className="px-6 py-4 border-b border-gray-200">
              <h3 className="text-lg font-medium text-gray-900">Inventory Turnover Analysis</h3>
            </div>
            <div className="p-6">
              <InventoryTurnoverChart 
                inventory={inventory?.results || []}
                dateRange={dateRange}
              />
            </div>
          </div>

          {/* Key Metrics */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <div className="flex items-center">
                <ChartBarIcon className="h-8 w-8 text-blue-500" />
                <div className="ml-3">
                  <p className="text-sm font-medium text-gray-500">Total Inventory Value</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {dashboardData?.total_inventory_value || '$0'}
                  </p>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <div className="flex items-center">
                <EyeIcon className="h-8 w-8 text-green-500" />
                <div className="ml-3">
                  <p className="text-sm font-medium text-gray-500">Low Stock Items</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {dashboardData?.low_stock_items || 0}
                  </p>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <div className="flex items-center">
                <ChartBarIcon className="h-8 w-8 text-purple-500" />
                <div className="ml-3">
                  <p className="text-sm font-medium text-gray-500">Total Products</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {dashboardData?.total_products || 0}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {reportType === 'recommendations' && (
        <div className="space-y-6">
          <ReorderRecommendations 
            inventory={inventory?.results || []}
            warehouses={warehouses?.results || []}
          />
        </div>
      )}
    </div>
  );
};

export default ReportsPage; 