import React from 'react';
import { Supplier, Product } from '@/types';

interface PurchaseOrderWizardProps {
  suppliers: Supplier[];
  products: Product[];
  onSubmit: (data: any) => void;
  loading: boolean;
}

const PurchaseOrderWizard: React.FC<PurchaseOrderWizardProps> = ({
  suppliers,
  products,
  onSubmit,
  loading,
}) => {
  return (
    <div className="p-6">
      <div className="text-center">
        <h3 className="text-lg font-medium text-gray-900 mb-2">Purchase Order Wizard</h3>
        <p className="text-sm text-gray-500 mb-6">
          Multi-step form for creating purchase orders - Coming soon!
        </p>
        <div className="bg-gray-50 rounded-lg p-4">
          <p className="text-sm text-gray-600">
            This will include supplier selection, line item management, and order approval workflow.
          </p>
        </div>
      </div>
    </div>
  );
};

export default PurchaseOrderWizard; 