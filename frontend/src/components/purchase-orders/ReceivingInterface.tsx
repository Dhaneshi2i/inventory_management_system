import React from 'react';
import { PurchaseOrder } from '@/types';

interface ReceivingInterfaceProps {
  order: PurchaseOrder;
  onSubmit: (data: { po_id: string; items: Array<{ item_id: string; received_quantity: number }> }) => void;
  loading: boolean;
}

const ReceivingInterface: React.FC<ReceivingInterfaceProps> = ({
  order,
  onSubmit,
  loading,
}) => {
  return (
    <div className="p-6">
      <div className="text-center">
        <h3 className="text-lg font-medium text-gray-900 mb-2">Receiving Interface</h3>
        <p className="text-sm text-gray-500 mb-6">
          Receive items for order {order.order_number} - Coming soon!
        </p>
        <div className="bg-gray-50 rounded-lg p-4">
          <p className="text-sm text-gray-600">
            This will include partial receipts, quality checks, and inventory updates.
          </p>
        </div>
      </div>
    </div>
  );
};

export default ReceivingInterface; 