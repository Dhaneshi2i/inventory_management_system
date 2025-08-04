import React, { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { 
  PlusIcon, 
  ArrowPathIcon, 
  ExclamationTriangleIcon,
  ChartBarIcon,
  CubeIcon,
  TruckIcon,
  DocumentArrowDownIcon,
  PrinterIcon,
  QrCodeIcon
} from '@heroicons/react/24/outline';
import { toast } from 'react-hot-toast';
import { motion } from 'framer-motion';

// import { api } from '@/services/api';
import { 
  Inventory, 
  Warehouse, 
  StockMovement, 
  DashboardSummary,
  InventoryFilters 
} from '@/types';
import LoadingSpinner from '@/components/LoadingSpinner';
import Modal from '@/components/Modal';
import DataTable from '@/components/DataTable';
import ConfirmationDialog from '@/components/ConfirmationDialog';

// Components
import InventoryDashboard from '@/components/inventory/InventoryDashboard';
import StockAdjustmentForm from '@/components/inventory/StockAdjustmentForm';
import StockTransferForm from '@/components/inventory/StockTransferForm';
import InventoryChart from '@/components/inventory/InventoryChart';
import StockMovementHistory from '@/components/inventory/StockMovementHistory';
import WarehouseSelector from '@/components/inventory/WarehouseSelector';
import LowStockAlerts from '@/components/inventory/LowStockAlerts';
import InventoryMetrics from '@/components/inventory/InventoryMetrics';
import api, { apiService } from '@/services/api';

const InventoryPage: React.FC = () => {
  const queryClient = useQueryClient();
  const [selectedWarehouse, setSelectedWarehouse] = useState<string>('all');
  const [filters, setFilters] = useState<InventoryFilters>({
    page: 1,
    page_size: 20,
    warehouse_id: undefined,
    is_low_stock: false,
    is_out_of_stock: false,
  });
  const [isAdjustmentModalOpen, setIsAdjustmentModalOpen] = useState(false);
  const [isTransferModalOpen, setIsTransferModalOpen] = useState(false);
  const [selectedInventory, setSelectedInventory] = useState<Inventory | null>(null);
  const [autoRefresh, setAutoRefresh] = useState(true);

  // Queries
  const { data: dashboardData, isLoading: dashboardLoading } = useQuery({
    queryKey: ['dashboard-summary'],
    queryFn: () => apiService.get<DashboardSummary>('/dashboard/summary/'),
    refetchInterval: autoRefresh ? 30000 : false, // 30 seconds
  });
  const { data: warehouses, isLoading: warehousesLoading } = useQuery({
    queryKey: ['warehouses'],
    queryFn: () => apiService.get<Warehouse[]>('/warehouses/'),
  });

  const { data: inventoryData, isLoading: inventoryLoading } = useQuery({
    queryKey: ['inventory', filters],
    queryFn: () => apiService.get<Inventory[]>('/inventory/', { params: filters }),
  });

  const { data: stockMovements, isLoading: movementsLoading } = useQuery({
    queryKey: ['stock-movements', selectedWarehouse],
    queryFn: () => apiService.get<StockMovement[]>('/stock-movements/', {
      params: { warehouse_id: selectedWarehouse === 'all' ? undefined : selectedWarehouse }
    }),
    enabled: !!selectedWarehouse,
  });
  // Mutations
  const adjustStockMutation = useMutation({
    mutationFn: (data: { inventory_id: string; quantity: number; notes: string }) =>
      api.post('/inventory/adjust/', data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['inventory'] });
      queryClient.invalidateQueries({ queryKey: ['dashboard-summary'] });
      queryClient.invalidateQueries({ queryKey: ['stock-movements'] });
      toast.success('Stock adjusted successfully');
      setIsAdjustmentModalOpen(false);
      setSelectedInventory(null);
    },
    onError: (error) => {
      toast.error('Failed to adjust stock');
      console.error('Stock adjustment error:', error);
    },
  });

  const transferStockMutation = useMutation({
    mutationFn: (data: { 
      from_warehouse_id: string; 
      to_warehouse_id: string; 
      product_id: string; 
      quantity: number; 
      notes: string 
    }) => api.post('/inventory/transfer/', data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['inventory'] });
      queryClient.invalidateQueries({ queryKey: ['dashboard-summary'] });
      queryClient.invalidateQueries({ queryKey: ['stock-movements'] });
      toast.success('Stock transferred successfully');
      setIsTransferModalOpen(false);
    },
    onError: (error) => {
      toast.error('Failed to transfer stock');
      console.error('Stock transfer error:', error);
    },
  });

  // Effects
  useEffect(() => {
    setFilters(prev => ({
      ...prev,
      warehouse_id: selectedWarehouse === 'all' ? undefined : selectedWarehouse,
    }));
  }, [selectedWarehouse]);

  // Handlers
  const handleStockAdjustment = (inventory: Inventory) => {
    setSelectedInventory(inventory);
    setIsAdjustmentModalOpen(true);
  };

  const handleStockTransfer = () => {
    setIsTransferModalOpen(true);
  };

  const handleExportInventory = async () => {
    try {
      const response = await api.get('/inventory/export/', {
        params: filters,
        responseType: 'blob',
      });
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `inventory-${new Date().toISOString().split('T')[0]}.csv`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      
      toast.success('Inventory exported successfully');
    } catch (error) {
      toast.error('Failed to export inventory');
      console.error('Export error:', error);
    }
  };

  const handlePrintLabels = () => {
    // Simulate barcode label printing
    toast.success('Printing labels...');
  };

  const handleBarcodeScan = () => {
    // Simulate barcode scanning
    toast.info('Barcode scanner activated. Please scan a product.');
  };

  if (dashboardLoading || warehousesLoading) {
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
          <h1 className="text-2xl font-bold text-gray-900">Inventory Management</h1>
          <p className="mt-1 text-sm text-gray-500">
            Manage stock levels, track movements, and monitor warehouse performance
          </p>
        </div>
        <div className="mt-4 sm:mt-0 flex flex-wrap gap-2">
          <button
            onClick={() => setAutoRefresh(!autoRefresh)}
            className={`inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md ${
              autoRefresh 
                ? 'bg-green-100 text-green-800 hover:bg-green-200' 
                : 'bg-gray-100 text-gray-800 hover:bg-gray-200'
            }`}
          >
            <ArrowPathIcon className={`h-4 w-4 mr-2 ${autoRefresh ? 'animate-spin' : ''}`} />
            {autoRefresh ? 'Auto-refresh ON' : 'Auto-refresh OFF'}
          </button>
          <button
            onClick={handleBarcodeScan}
            className="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
          >
            <QrCodeIcon className="h-4 w-4 mr-2" />
            Scan Barcode
          </button>
          <button
            onClick={handlePrintLabels}
            className="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
          >
            <PrinterIcon className="h-4 w-4 mr-2" />
            Print Labels
          </button>
          <button
            onClick={handleExportInventory}
            className="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
          >
            <DocumentArrowDownIcon className="h-4 w-4 mr-2" />
            Export
          </button>
          <button
            onClick={handleStockTransfer}
            className="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
          >
            <TruckIcon className="h-4 w-4 mr-2" />
            Transfer Stock
          </button>
        </div>
      </div>:

      {/* Warehouse Selector */}
      <WarehouseSelector
        warehouses={warehouses || []}
        selectedWarehouse={selectedWarehouse}
        onWarehouseChange={setSelectedWarehouse}
        loading={warehousesLoading}
      />

      {/* Dashboard Metrics */}
      <InventoryMetrics data={dashboardData} loading={dashboardLoading} />

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column - Inventory List */}
        <div className="lg:col-span-2 space-y-6">
          {/* Inventory Dashboard */}
          <InventoryDashboard
            inventory={inventoryData?.results || []}
            loading={inventoryLoading}
            onStockAdjustment={handleStockAdjustment}
            filters={filters}
            onFiltersChange={setFilters}
          />

          {/* Stock Movement History */}
          <StockMovementHistory
            movements={stockMovements || []}
            loading={movementsLoading}
            warehouseId={selectedWarehouse}
          />
        </div>

        {/* Right Column - Charts and Alerts */}
        <div className="space-y-6">
          {/* Low Stock Alerts */}
          <LowStockAlerts
            inventory={inventoryData?.results || []}
            loading={inventoryLoading}
          />

          {/* Inventory Charts */}
          <InventoryChart
            inventory={inventoryData?.results || []}
            warehouses={warehouses || []}
            loading={inventoryLoading}
          />
        </div>
      </div>

      {/* Modals */}
      <Modal
        isOpen={isAdjustmentModalOpen}
        onClose={() => {
          setIsAdjustmentModalOpen(false);
          setSelectedInventory(null);
        }}
        title="Adjust Stock Level"
        size="md"
      >
        {selectedInventory && (
          <StockAdjustmentForm
            inventory={selectedInventory}
            onSubmit={(data) => adjustStockMutation.mutate(data)}
            loading={adjustStockMutation.isPending}
          />
        )}
      </Modal>

      <Modal
        isOpen={isTransferModalOpen}
        onClose={() => setIsTransferModalOpen(false)}
        title="Transfer Stock Between Warehouses"
        size="lg"
      >
        <StockTransferForm
          warehouses={warehouses}
          inventory={inventoryData?.results || []}
          onSubmit={(data) => transferStockMutation.mutate(data)}
          loading={transferStockMutation.isPending}
        />
      </Modal>
    </div>
  );
};

export default InventoryPage; 