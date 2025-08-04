import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { 
  PlusIcon, 
  MagnifyingGlassIcon,
  DocumentTextIcon,
  TruckIcon
} from '@heroicons/react/24/outline';
import { toast } from 'react-hot-toast';


import { apiService } from '@/services/api';
import { 
  PurchaseOrder, 
  Supplier, 
  Product,
  PurchaseOrderFilters,
  ApiResponse
} from '@/types';
import LoadingSpinner from '@/components/LoadingSpinner';
import Modal from '@/components/Modal';

// Components
import PurchaseOrderList from '@/components/purchase-orders/PurchaseOrderList';
import PurchaseOrderWizard from '@/components/purchase-orders/PurchaseOrderWizard';
import PurchaseOrderDetails from '@/components/purchase-orders/PurchaseOrderDetails';
import ReceivingInterface from '@/components/purchase-orders/ReceivingInterface';
import SupplierDirectory from '@/components/purchase-orders/SupplierDirectory';
import PurchaseOrderMetrics from '@/components/purchase-orders/PurchaseOrderMetrics';

const PurchaseOrdersPage: React.FC = () => {
  const queryClient = useQueryClient();
  const [filters, setFilters] = useState<PurchaseOrderFilters>({
    page: 1,
    page_size: 20,
    status: undefined,
    supplier_id: undefined,
    warehouse_id: undefined,
  });
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedView, setSelectedView] = useState<'orders' | 'suppliers' | 'create'>('orders');
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [isDetailsModalOpen, setIsDetailsModalOpen] = useState(false);
  const [isReceivingModalOpen, setIsReceivingModalOpen] = useState(false);
  const [selectedOrder, setSelectedOrder] = useState<PurchaseOrder | null>(null);

  // Queries
  const { data: purchaseOrders, isLoading: ordersLoading } = useQuery({
    queryKey: ['purchase-orders', filters],
    queryFn: () => apiService.get<ApiResponse<PurchaseOrder>>('/purchase-orders/', { params: filters }),
  });

  const { data: suppliers, isLoading: suppliersLoading } = useQuery({
    queryKey: ['suppliers'],
    queryFn: () => apiService.get<ApiResponse<Supplier>>('/suppliers/'),
  });

  const { data: products } = useQuery({
    queryKey: ['products'],
    queryFn: () => apiService.get<ApiResponse<Product>>('/products/'),
  });

  // Mutations
  const createPOMutation = useMutation({
    mutationFn: (data: any) => apiService.post('/purchase-orders/', data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['purchase-orders'] });
      toast.success('Purchase order created successfully');
      setIsCreateModalOpen(false);
    },
    onError: (error) => {
      toast.error('Failed to create purchase order');
      console.error('Create PO error:', error);
    },
  });

  const updatePOStatusMutation = useMutation({
    mutationFn: ({ id, status }: { id: string; status: string }) =>
      apiService.patch(`/purchase-orders/${id}/`, { status }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['purchase-orders'] });
      toast.success('Purchase order status updated');
    },
    onError: (error) => {
      toast.error('Failed to update purchase order status');
      console.error('Update PO status error:', error);
    },
  });

  const receiveItemsMutation = useMutation({
    mutationFn: (data: { po_id: string; items: Array<{ item_id: string; received_quantity: number }> }) =>
      apiService.post(`/purchase-orders/${data.po_id}/receive/`, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['purchase-orders'] });
      queryClient.invalidateQueries({ queryKey: ['inventory'] });
      toast.success('Items received successfully');
      setIsReceivingModalOpen(false);
      setSelectedOrder(null);
    },
    onError: (error) => {
      toast.error('Failed to receive items');
      console.error('Receive items error:', error);
    },
  });

  // Handlers
  const handleCreatePO = () => {
    setIsCreateModalOpen(true);
  };

  const handleViewOrder = (order: PurchaseOrder) => {
    setSelectedOrder(order);
    setIsDetailsModalOpen(true);
  };

  const handleReceiveOrder = (order: PurchaseOrder) => {
    setSelectedOrder(order);
    setIsReceivingModalOpen(true);
  };

  const handleStatusUpdate = (orderId: string, newStatus: string) => {
    updatePOStatusMutation.mutate({ id: orderId, status: newStatus });
  };

  const handleReceiveItems = (data: { po_id: string; items: Array<{ item_id: string; received_quantity: number }> }) => {
    receiveItemsMutation.mutate(data);
  };

  if (ordersLoading || suppliersLoading) {
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
          <h1 className="text-2xl font-bold text-gray-900">Purchase Orders</h1>
          <p className="mt-1 text-sm text-gray-500">
            Manage purchase orders, suppliers, and order fulfillment
          </p>
        </div>
        <div className="mt-4 sm:mt-0 flex flex-wrap gap-2">
          <button
            onClick={() => setSelectedView('suppliers')}
            className={`inline-flex items-center px-3 py-2 border text-sm font-medium rounded-md ${
              selectedView === 'suppliers'
                ? 'border-blue-500 bg-blue-50 text-blue-700'
                : 'border-gray-300 bg-white text-gray-700 hover:bg-gray-50'
            }`}
          >
            <DocumentTextIcon className="h-4 w-4 mr-2" />
            Suppliers
          </button>
          <button
            onClick={() => setSelectedView('orders')}
            className={`inline-flex items-center px-3 py-2 border text-sm font-medium rounded-md ${
              selectedView === 'orders'
                ? 'border-blue-500 bg-blue-50 text-blue-700'
                : 'border-gray-300 bg-white text-gray-700 hover:bg-gray-50'
            }`}
          >
            <TruckIcon className="h-4 w-4 mr-2" />
            Orders
          </button>
          <button
            onClick={handleCreatePO}
            className="inline-flex items-center px-3 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
          >
            <PlusIcon className="h-4 w-4 mr-2" />
            Create PO
          </button>
        </div>
      </div>

      {/* Metrics */}
      <PurchaseOrderMetrics purchaseOrders={purchaseOrders?.results || []} />

      {/* Main Content */}
      {selectedView === 'orders' && (
        <div className="space-y-6">
          {/* Filters and Search */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between space-y-3 sm:space-y-0">
              <div className="flex items-center space-x-4">
                <div className="relative">
                  <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                  <input
                    type="text"
                    placeholder="Search purchase orders..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-10 pr-4 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
                
                <select
                  value={filters.status || ''}
                  onChange={(e) => setFilters(prev => ({ ...prev, status: e.target.value || undefined }))}
                  className="px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="">All Status</option>
                  <option value="draft">Draft</option>
                  <option value="pending">Pending</option>
                  <option value="approved">Approved</option>
                  <option value="ordered">Ordered</option>
                  <option value="received">Received</option>
                  <option value="cancelled">Cancelled</option>
                </select>

                <select
                  value={filters.supplier_id || ''}
                  onChange={(e) => setFilters(prev => ({ ...prev, supplier_id: e.target.value || undefined }))}
                  className="px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="">All Suppliers</option>
                  {suppliers?.results?.map((supplier) => (
                    <option key={supplier.id} value={supplier.id}>
                      {supplier.name}
                    </option>
                  ))}
                </select>
              </div>

              <div className="flex items-center space-x-2">
                <span className="text-sm text-gray-500">
                  {purchaseOrders?.results?.length || 0} orders
                </span>
              </div>
            </div>
          </div>

          {/* Purchase Orders List */}
          <PurchaseOrderList
            purchaseOrders={purchaseOrders?.results || []}
            loading={ordersLoading}
            onViewOrder={handleViewOrder}
            onReceiveOrder={handleReceiveOrder}
            onStatusUpdate={handleStatusUpdate}
            searchTerm={searchTerm}
          />
        </div>
      )}

      {selectedView === 'suppliers' && (
        <SupplierDirectory
          suppliers={suppliers?.results || []}
          loading={suppliersLoading}
          purchaseOrders={purchaseOrders?.results || []}
        />
      )}

      {/* Modals */}
      <Modal
        isOpen={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
        title="Create Purchase Order"
        size="2xl"
      >
        <PurchaseOrderWizard
          suppliers={suppliers?.results || []}
          products={products?.results || []}
          onSubmit={(data) => createPOMutation.mutate(data)}
          loading={createPOMutation.isPending}
        />
      </Modal>

      <Modal
        isOpen={isDetailsModalOpen}
        onClose={() => {
          setIsDetailsModalOpen(false);
          setSelectedOrder(null);
        }}
        title="Purchase Order Details"
        size="xl"
      >
        {selectedOrder && (
          <PurchaseOrderDetails
            order={selectedOrder}
            onStatusUpdate={handleStatusUpdate}
            onReceiveOrder={handleReceiveOrder}
          />
        )}
      </Modal>

      <Modal
        isOpen={isReceivingModalOpen}
        onClose={() => {
          setIsReceivingModalOpen(false);
          setSelectedOrder(null);
        }}
        title="Receive Items"
        size="lg"
      >
        {selectedOrder && (
          <ReceivingInterface
            order={selectedOrder}
            onSubmit={handleReceiveItems}
            loading={receiveItemsMutation.isPending}
          />
        )}
      </Modal>
    </div>
  );
};

export default PurchaseOrdersPage; 