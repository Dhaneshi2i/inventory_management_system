import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { 
  PlusIcon, 
  MagnifyingGlassIcon,
  BuildingOfficeIcon,
  UserIcon,
  PhoneIcon,
  EnvelopeIcon,
  GlobeAltIcon,
  ChartBarIcon,
  DocumentTextIcon
} from '@heroicons/react/24/outline';
import { toast } from 'react-hot-toast';
import { motion } from 'framer-motion';

import { apiService } from '@/services/api';
import { Supplier, PurchaseOrder } from '@/types';
import LoadingSpinner from '@/components/LoadingSpinner';
import Modal from '@/components/Modal';

// Components
import SupplierList from '@/components/suppliers/SupplierList';
import SupplierForm from '@/components/suppliers/SupplierForm';
import SupplierDetails from '@/components/suppliers/SupplierDetails';
import SupplierMetrics from '@/components/suppliers/SupplierMetrics';
import SupplierPerformanceChart from '@/components/suppliers/SupplierPerformanceChart';

const SuppliersPage: React.FC = () => {
  const queryClient = useQueryClient();
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedView, setSelectedView] = useState<'list' | 'performance'>('list');
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [isDetailsModalOpen, setIsDetailsModalOpen] = useState(false);
  const [selectedSupplier, setSelectedSupplier] = useState<Supplier | null>(null);
  const [filters, setFilters] = useState({
    is_active: true,
  });

  // Queries
  const { data: suppliers, isLoading: suppliersLoading, error: suppliersError } = useQuery({
    queryKey: ['suppliers', filters],
    queryFn: () => apiService.get<Supplier[]>('/suppliers/', { params: filters }),
    staleTime: 5 * 60 * 1000, // 5 minutes
    retry: 2,
  });

  const { data: purchaseOrders, isLoading: ordersLoading } = useQuery({
    queryKey: ['purchase-orders'],
    queryFn: () => apiService.get<PurchaseOrder[]>('/purchase-orders/'),
    staleTime: 2 * 60 * 1000, // 2 minutes
    retry: 2,
  });

  // Mutations
  const createSupplierMutation = useMutation({
    mutationFn: (data: any) => apiService.post('/suppliers/', data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['suppliers'] });
      toast.success('Supplier created successfully');
      setIsCreateModalOpen(false);
    },
    onError: (error: any) => {
      toast.error(error.detail || 'Failed to create supplier');
      console.error('Create supplier error:', error);
    },
  });

  const updateSupplierMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: any }) =>
      apiService.patch(`/suppliers/${id}/`, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['suppliers'] });
      toast.success('Supplier updated successfully');
      setIsDetailsModalOpen(false);
      setSelectedSupplier(null);
    },
    onError: (error: any) => {
      toast.error(error.detail || 'Failed to update supplier');
      console.error('Update supplier error:', error);
    },
  });

  const deleteSupplierMutation = useMutation({
    mutationFn: (id: string) => apiService.delete(`/suppliers/${id}/`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['suppliers'] });
      toast.success('Supplier deleted successfully');
    },
    onError: (error: any) => {
      toast.error(error.detail || 'Failed to delete supplier');
      console.error('Delete supplier error:', error);
    },
  });

  // Handlers
  const handleCreateSupplier = () => {
    setIsCreateModalOpen(true);
  };

  const handleViewSupplier = (supplier: Supplier) => {
    setSelectedSupplier(supplier);
    setIsDetailsModalOpen(true);
  };

  const handleCreateSupplierSubmit = (data: any) => {
    createSupplierMutation.mutate(data);
  };

  const handleUpdateSupplier = (data: any) => {
    if (selectedSupplier) {
      updateSupplierMutation.mutate({ id: selectedSupplier.id, data });
    }
  };

  const handleDeleteSupplier = (supplierId: string) => {
    if (window.confirm('Are you sure you want to delete this supplier?')) {
      deleteSupplierMutation.mutate(supplierId);
    }
  };

  if (suppliersLoading || ordersLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (suppliersError) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="text-red-500 text-lg font-medium mb-2">Error Loading Suppliers</div>
          <div className="text-gray-500 text-sm">
            {suppliersError.detail || 'Failed to load supplier data. Please try again.'}
          </div>
          <button
            onClick={() => queryClient.invalidateQueries({ queryKey: ['suppliers'] })}
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
          <h1 className="text-2xl font-bold text-gray-900">Suppliers</h1>
          <p className="mt-1 text-sm text-gray-500">
            Manage supplier relationships and performance
          </p>
        </div>
        <div className="mt-4 sm:mt-0 flex flex-wrap gap-2">
          <button
            onClick={() => setSelectedView('performance')}
            className={`inline-flex items-center px-3 py-2 border text-sm font-medium rounded-md ${
              selectedView === 'performance'
                ? 'border-blue-500 bg-blue-50 text-blue-700'
                : 'border-gray-300 bg-white text-gray-700 hover:bg-gray-50'
            }`}
          >
            <ChartBarIcon className="h-4 w-4 mr-2" />
            Performance
          </button>
          <button
            onClick={() => setSelectedView('list')}
            className={`inline-flex items-center px-3 py-2 border text-sm font-medium rounded-md ${
              selectedView === 'list'
                ? 'border-blue-500 bg-blue-50 text-blue-700'
                : 'border-gray-300 bg-white text-gray-700 hover:bg-gray-50'
            }`}
          >
            <DocumentTextIcon className="h-4 w-4 mr-2" />
            List
          </button>
          <button
            onClick={handleCreateSupplier}
            className="inline-flex items-center px-3 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
          >
            <PlusIcon className="h-4 w-4 mr-2" />
            Add Supplier
          </button>
        </div>
      </div>

      {/* Metrics */}
      <SupplierMetrics suppliers={suppliers?.results || []} />

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
                    placeholder="Search suppliers..."
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
                  <option value="all">All Suppliers</option>
                </select>
              </div>

              <div className="flex items-center space-x-2">
                <span className="text-sm text-gray-500">
                  {suppliers?.results?.length || 0} suppliers
                </span>
              </div>
            </div>
          </div>

          {/* Suppliers List */}
          <SupplierList
            suppliers={suppliers?.results || []}
            loading={suppliersLoading}
            onViewSupplier={handleViewSupplier}
            onDeleteSupplier={handleDeleteSupplier}
            searchTerm={searchTerm}
          />
        </div>
      )}

      {selectedView === 'performance' && (
        <div className="space-y-6">
          <SupplierPerformanceChart 
            suppliers={suppliers?.results || []}
            purchaseOrders={purchaseOrders?.results || []}
          />
        </div>
      )}

      {/* Modals */}
      <Modal
        isOpen={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
        title="Add Supplier"
        size="lg"
      >
        <SupplierForm
          onSubmit={handleCreateSupplierSubmit}
          loading={createSupplierMutation.isPending}
        />
      </Modal>

      <Modal
        isOpen={isDetailsModalOpen}
        onClose={() => {
          setIsDetailsModalOpen(false);
          setSelectedSupplier(null);
        }}
        title="Supplier Details"
        size="xl"
      >
        {selectedSupplier && (
          <SupplierDetails
            supplier={selectedSupplier}
            onUpdate={handleUpdateSupplier}
            onDelete={() => handleDeleteSupplier(selectedSupplier.id)}
            loading={updateSupplierMutation.isPending}
          />
        )}
      </Modal>
    </div>
  );
};

export default SuppliersPage; 