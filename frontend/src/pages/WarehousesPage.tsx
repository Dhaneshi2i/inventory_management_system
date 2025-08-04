import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { 
  PlusIcon, 
  MagnifyingGlassIcon,
  ChartBarIcon,
  BuildingOfficeIcon
} from '@heroicons/react/24/outline';
import { toast } from 'react-hot-toast';

import { apiService } from '@/services/api';
import { Warehouse, Inventory, ApiResponse } from '@/types';
import LoadingSpinner from '@/components/LoadingSpinner';
import Modal from '@/components/Modal';

// Components
import WarehouseList from '@/components/warehouses/WarehouseList';
import WarehouseForm from '@/components/warehouses/WarehouseForm';
import WarehouseDetails from '@/components/warehouses/WarehouseDetails';
import WarehouseMetrics from '@/components/warehouses/WarehouseMetrics';
import CapacityUtilizationChart from '@/components/warehouses/CapacityUtilizationChart';

const WarehousesPage: React.FC = () => {
  const queryClient = useQueryClient();
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedView, setSelectedView] = useState<'list' | 'analytics'>('list');
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [isDetailsModalOpen, setIsDetailsModalOpen] = useState(false);
  const [selectedWarehouse, setSelectedWarehouse] = useState<Warehouse | null>(null);
  const [filters, setFilters] = useState({
    is_active: true,
  });

  // Queries
  const { data: warehouses, isLoading: warehousesLoading, error: warehousesError } = useQuery({
    queryKey: ['warehouses', filters],
    queryFn: () => apiService.get<ApiResponse<Warehouse>>('/warehouses/', { params: filters }),
    staleTime: 5 * 60 * 1000, // 5 minutes
    retry: 2,
  });

  const { isLoading: inventoryLoading } = useQuery({
    queryKey: ['inventory'],
    queryFn: () => apiService.get<ApiResponse<Inventory>>('/inventory/'),
    staleTime: 2 * 60 * 1000, // 2 minutes
    retry: 2,
  });

  // Mutations
  const createWarehouseMutation = useMutation({
    mutationFn: (data: any) => apiService.post('/warehouses/', data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['warehouses'] });
      toast.success('Warehouse created successfully');
      setIsCreateModalOpen(false);
    },
    onError: (error: any) => {
      toast.error(error.detail || 'Failed to create warehouse');
      console.error('Create warehouse error:', error);
    },
  });

  const updateWarehouseMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: any }) =>
      apiService.patch(`/warehouses/${id}/`, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['warehouses'] });
      toast.success('Warehouse updated successfully');
      setIsDetailsModalOpen(false);
      setSelectedWarehouse(null);
    },
    onError: (error: any) => {
      toast.error(error.detail || 'Failed to update warehouse');
      console.error('Update warehouse error:', error);
    },
  });

  const deleteWarehouseMutation = useMutation({
    mutationFn: (id: string) => apiService.delete(`/warehouses/${id}/`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['warehouses'] });
      toast.success('Warehouse deleted successfully');
    },
    onError: (error: any) => {
      toast.error(error.detail || 'Failed to delete warehouse');
      console.error('Delete warehouse error:', error);
    },
  });

  // Handlers
  const handleCreateWarehouse = () => {
    setIsCreateModalOpen(true);
  };

  const handleViewWarehouse = (warehouse: Warehouse) => {
    setSelectedWarehouse(warehouse);
    setIsDetailsModalOpen(true);
  };

  const handleCreateWarehouseSubmit = (data: any) => {
    createWarehouseMutation.mutate(data);
  };

  const handleUpdateWarehouse = (data: any) => {
    if (selectedWarehouse) {
      updateWarehouseMutation.mutate({ id: selectedWarehouse.id, data });
    }
  };

  const handleDeleteWarehouse = (warehouseId: string) => {
    if (window.confirm('Are you sure you want to delete this warehouse?')) {
      deleteWarehouseMutation.mutate(warehouseId);
    }
  };

  if (warehousesLoading || inventoryLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (warehousesError) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="text-red-500 text-lg font-medium mb-2">Error Loading Warehouses</div>
          <div className="text-gray-500 text-sm">
            {(warehousesError as any)?.detail || 'Failed to load warehouse data. Please try again.'}
          </div>
          <button
            onClick={() => queryClient.invalidateQueries({ queryKey: ['warehouses'] })}
            className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Warehouses</h1>
          <p className="mt-1 text-sm text-gray-500">
            Manage warehouse locations, capacity, and performance
          </p>
        </div>
        <div className="mt-4 sm:mt-0 flex flex-wrap gap-2">
          <button
            onClick={() => setSelectedView('analytics')}
            className={`inline-flex items-center px-3 py-2 border text-sm font-medium rounded-md ${
              selectedView === 'analytics'
                ? 'border-blue-500 bg-blue-50 text-blue-700'
                : 'border-gray-300 bg-white text-gray-700 hover:bg-gray-50'
            }`}
          >
            <ChartBarIcon className="h-4 w-4 mr-2" />
            Analytics
          </button>
          <button
            onClick={() => setSelectedView('list')}
            className={`inline-flex items-center px-3 py-2 border text-sm font-medium rounded-md ${
              selectedView === 'list'
                ? 'border-blue-500 bg-blue-50 text-blue-700'
                : 'border-gray-300 bg-white text-gray-700 hover:bg-gray-50'
            }`}
          >
            <BuildingOfficeIcon className="h-4 w-4 mr-2" />
            List
          </button>
          <button
            onClick={handleCreateWarehouse}
            className="inline-flex items-center px-3 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
          >
            <PlusIcon className="h-4 w-4 mr-2" />
            Add Warehouse
          </button>
        </div>
      </div>

      {/* Metrics */}
      <WarehouseMetrics warehouses={warehouses?.results || []} />

      {/* Main Content */}
      {selectedView === 'list' && (
        <div className="space-y-6">
          {/* Filters and Search */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between space-y-3 sm:space-y-0">
              <div className="flex items-center space-x-4">
                <div className="relative">
                  <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                  <input
                    type="text"
                    placeholder="Search warehouses..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-10 pr-4 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
                
                <select
                  value={filters.is_active ? 'active' : 'all'}
                  onChange={(e) => setFilters(prev => ({ 
                    ...prev, 
                    is_active: e.target.value === 'active' 
                  }))}
                  className="px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="active">Active Only</option>
                  <option value="all">All Warehouses</option>
                </select>
              </div>

              <div className="flex items-center space-x-2">
                <span className="text-sm text-gray-500">
                  {warehouses?.results?.length || 0} warehouses
                </span>
              </div>
            </div>
          </div>

          {/* Warehouses List */}
          <WarehouseList
            warehouses={warehouses?.results || []}
            loading={warehousesLoading}
            onViewWarehouse={handleViewWarehouse}
            onEditWarehouse={handleViewWarehouse}
            onDeleteWarehouse={handleDeleteWarehouse}
            searchTerm={searchTerm}
          />
        </div>
      )}

      {selectedView === 'analytics' && (
        <div className="space-y-6">
          <CapacityUtilizationChart 
            warehouses={warehouses?.results || []}
          />
        </div>
      )}

      {/* Modals */}
      <Modal
        isOpen={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
        title="Add Warehouse"
        size="lg"
      >
        <WarehouseForm
          onSubmit={handleCreateWarehouseSubmit}
          loading={createWarehouseMutation.isPending}
        />
      </Modal>

      <Modal
        isOpen={isDetailsModalOpen}
        onClose={() => {
          setIsDetailsModalOpen(false);
          setSelectedWarehouse(null);
        }}
        title="Warehouse Details"
        size="xl"
      >
        {selectedWarehouse && (
          <WarehouseDetails
            warehouse={selectedWarehouse}
            onEdit={handleUpdateWarehouse}
          />
        )}
      </Modal>
    </div>
  );
};

export default WarehousesPage; 