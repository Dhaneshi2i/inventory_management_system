import React from 'react';
import { PurchaseOrder } from '@/types';

interface PurchaseOrderDetailsProps {
  order: PurchaseOrder;
  onStatusUpdate: (orderId: string, status: string) => void;
  onReceiveOrder: (order: PurchaseOrder) => void;
}

const PurchaseOrderDetails: React.FC<PurchaseOrderDetailsProps> = ({
  order,
  onStatusUpdate,
  onReceiveOrder,
}) => {
  return (
    <div className="p-6">
      <div className="text-center">
        <h3 className="text-lg font-medium text-gray-900 mb-2">Purchase Order Details</h3>
        <p className="text-sm text-gray-500 mb-6">
          Detailed view of purchase order {order.order_number} - Coming soon!
        </p>
        <div className="bg-gray-50 rounded-lg p-4">
          <p className="text-sm text-gray-600">
            This will include order items, status history, and approval workflow.
          </p>
        </div>
      </div>
    </div>
  );
};

export default PurchaseOrderDetails; 