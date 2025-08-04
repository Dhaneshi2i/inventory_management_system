import React from 'react';
import { Warehouse } from '@/types';

interface WarehouseDetailsProps {
  warehouse: Warehouse;
  onEdit: (warehouse: Warehouse) => void;
}

const WarehouseDetails: React.FC<WarehouseDetailsProps> = ({
  warehouse,
  onEdit,
}) => {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-medium text-gray-900">{warehouse.name}</h3>
          <p className="text-sm text-gray-500">{warehouse.address}</p>
        </div>
        <button
          onClick={() => onEdit(warehouse)}
          className="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
        >
          Edit Warehouse
        </button>
      </div>

      {/* Details Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-gray-50 rounded-lg p-4">
          <h4 className="text-sm font-medium text-gray-900 mb-3">Contact Information</h4>
          <dl className="space-y-2">
            <div>
              <dt className="text-sm font-medium text-gray-500">Manager</dt>
              <dd className="text-sm text-gray-900">{warehouse.manager}</dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Email</dt>
              <dd className="text-sm text-gray-900">{warehouse.contact_email}</dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Phone</dt>
              <dd className="text-sm text-gray-900">{warehouse.contact_phone || 'Not provided'}</dd>
            </div>
          </dl>
        </div>

        <div className="bg-gray-50 rounded-lg p-4">
          <h4 className="text-sm font-medium text-gray-900 mb-3">Capacity & Utilization</h4>
          <dl className="space-y-2">
            <div>
              <dt className="text-sm font-medium text-gray-500">Total Capacity</dt>
              <dd className="text-sm text-gray-900">{warehouse.capacity.toLocaleString()}</dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Available Capacity</dt>
              <dd className="text-sm text-gray-900">{warehouse.available_capacity.toLocaleString()}</dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Current Utilization</dt>
              <dd className="text-sm text-gray-900">{warehouse.current_utilization}</dd>
            </div>
          </dl>
        </div>

        <div className="bg-gray-50 rounded-lg p-4">
          <h4 className="text-sm font-medium text-gray-900 mb-3">Inventory Summary</h4>
          <dl className="space-y-2">
            <div>
              <dt className="text-sm font-medium text-gray-500">Total Items</dt>
              <dd className="text-sm text-gray-900">{warehouse.inventory_count}</dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Total Value</dt>
              <dd className="text-sm text-gray-900">{warehouse.total_inventory_value}</dd>
            </div>
          </dl>
        </div>

        <div className="bg-gray-50 rounded-lg p-4">
          <h4 className="text-sm font-medium text-gray-900 mb-3">Status</h4>
          <dl className="space-y-2">
            <div>
              <dt className="text-sm font-medium text-gray-500">Status</dt>
              <dd>
                <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                  warehouse.is_active
                    ? 'bg-green-100 text-green-800'
                    : 'bg-red-100 text-red-800'
                }`}>
                  {warehouse.is_active ? 'Active' : 'Inactive'}
                </span>
              </dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Created</dt>
              <dd className="text-sm text-gray-900">
                {new Date(warehouse.created_at).toLocaleDateString()}
              </dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Last Updated</dt>
              <dd className="text-sm text-gray-900">
                {new Date(warehouse.updated_at).toLocaleDateString()}
              </dd>
            </div>
          </dl>
        </div>
      </div>
    </div>
  );
};

export default WarehouseDetails; 