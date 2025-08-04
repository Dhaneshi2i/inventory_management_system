import React from 'react';
import { Supplier, PurchaseOrder } from '@/types';

interface SupplierDirectoryProps {
  suppliers: Supplier[];
  loading: boolean;
  purchaseOrders: PurchaseOrder[];
}

const SupplierDirectory: React.FC<SupplierDirectoryProps> = ({
  suppliers,
  loading,
  purchaseOrders,
}) => {
  return (
    <div className="space-y-6">
      <div className="text-center">
        <h3 className="text-lg font-medium text-gray-900 mb-2">Supplier Directory</h3>
        <p className="text-sm text-gray-500 mb-6">
          Manage suppliers and view performance metrics - Coming soon!
        </p>
        <div className="bg-gray-50 rounded-lg p-4">
          <p className="text-sm text-gray-600">
            This will include supplier profiles, performance metrics, and order history.
          </p>
        </div>
      </div>
    </div>
  );
};

export default SupplierDirectory; 