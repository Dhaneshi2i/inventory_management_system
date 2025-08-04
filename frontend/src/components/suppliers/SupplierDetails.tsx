import React from 'react';
import { Supplier } from '@/types';

interface SupplierDetailsProps {
  supplier: Supplier;
  onEdit: (supplier: Supplier) => void;
}

const SupplierDetails: React.FC<SupplierDetailsProps> = ({
  supplier,
  onEdit,
}) => {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-medium text-gray-900">{supplier.name}</h3>
          <p className="text-sm text-gray-500">{supplier.address}</p>
        </div>
        <button
          onClick={() => onEdit(supplier)}
          className="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
        >
          Edit Supplier
        </button>
      </div>

      {/* Details Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-gray-50 rounded-lg p-4">
          <h4 className="text-sm font-medium text-gray-900 mb-3">Contact Information</h4>
          <dl className="space-y-2">
            <div>
              <dt className="text-sm font-medium text-gray-500">Contact Person</dt>
              <dd className="text-sm text-gray-900">{supplier.contact_person}</dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Email</dt>
              <dd className="text-sm text-gray-900">{supplier.email}</dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Phone</dt>
              <dd className="text-sm text-gray-900">{supplier.phone || 'Not provided'}</dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Website</dt>
              <dd className="text-sm text-gray-900">
                {supplier.website ? (
                  <a href={supplier.website} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:text-blue-800">
                    {supplier.website}
                  </a>
                ) : (
                  'Not provided'
                )}
              </dd>
            </div>
          </dl>
        </div>

        <div className="bg-gray-50 rounded-lg p-4">
          <h4 className="text-sm font-medium text-gray-900 mb-3">Business Information</h4>
          <dl className="space-y-2">
            <div>
              <dt className="text-sm font-medium text-gray-500">Tax ID</dt>
              <dd className="text-sm text-gray-900">{supplier.tax_id || 'Not provided'}</dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Payment Terms</dt>
              <dd className="text-sm text-gray-900">{supplier.payment_terms || 'Not specified'}</dd>
            </div>
          </dl>
        </div>

        <div className="bg-gray-50 rounded-lg p-4">
          <h4 className="text-sm font-medium text-gray-900 mb-3">Order Statistics</h4>
          <dl className="space-y-2">
            <div>
              <dt className="text-sm font-medium text-gray-500">Total Orders</dt>
              <dd className="text-sm text-gray-900">{supplier.total_orders}</dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Total Order Value</dt>
              <dd className="text-sm text-gray-900">{supplier.total_order_value}</dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Average Order Value</dt>
              <dd className="text-sm text-gray-900">{supplier.average_order_value}</dd>
            </div>
          </dl>
        </div>

        <div className="bg-gray-50 rounded-lg p-4">
          <h4 className="text-sm font-medium text-gray-900 mb-3">Status & History</h4>
          <dl className="space-y-2">
            <div>
              <dt className="text-sm font-medium text-gray-500">Status</dt>
              <dd>
                <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                  supplier.is_active
                    ? 'bg-green-100 text-green-800'
                    : 'bg-red-100 text-red-800'
                }`}>
                  {supplier.is_active ? 'Active' : 'Inactive'}
                </span>
              </dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Last Order</dt>
              <dd className="text-sm text-gray-900">
                {supplier.last_order_date ? new Date(supplier.last_order_date).toLocaleDateString() : 'Never'}
              </dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Created</dt>
              <dd className="text-sm text-gray-900">
                {new Date(supplier.created_at).toLocaleDateString()}
              </dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Last Updated</dt>
              <dd className="text-sm text-gray-900">
                {new Date(supplier.updated_at).toLocaleDateString()}
              </dd>
            </div>
          </dl>
        </div>
      </div>
    </div>
  );
};

export default SupplierDetails; 