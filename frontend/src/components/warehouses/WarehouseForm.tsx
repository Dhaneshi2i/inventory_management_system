import React from 'react';
import { useForm } from 'react-hook-form';
import { Warehouse } from '@/types';

interface WarehouseFormProps {
  warehouse?: Warehouse;
  onSubmit: (data: any) => void;
  loading: boolean;
}

const WarehouseForm: React.FC<WarehouseFormProps> = ({
  warehouse,
  onSubmit,
  loading,
}) => {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm({
    defaultValues: warehouse || {
      name: '',
      address: '',
      manager: '',
      contact_email: '',
      contact_phone: '',
      capacity: 0,
      is_active: true,
    },
  });

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <label className="block text-sm font-medium text-gray-700">
            Warehouse Name *
          </label>
          <input
            type="text"
            {...register('name', { required: 'Warehouse name is required' })}
            className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
          />
          {errors.name && (
            <p className="mt-1 text-sm text-red-600">{errors.name.message}</p>
          )}
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700">
            Manager *
          </label>
          <input
            type="text"
            {...register('manager', { required: 'Manager name is required' })}
            className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
          />
          {errors.manager && (
            <p className="mt-1 text-sm text-red-600">{errors.manager.message}</p>
          )}
        </div>

        <div className="md:col-span-2">
          <label className="block text-sm font-medium text-gray-700">
            Address *
          </label>
          <input
            type="text"
            {...register('address', { required: 'Address is required' })}
            className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
          />
          {errors.address && (
            <p className="mt-1 text-sm text-red-600">{errors.address.message}</p>
          )}
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700">
            Contact Email *
          </label>
          <input
            type="email"
            {...register('contact_email', { 
              required: 'Email is required',
              pattern: {
                value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                message: 'Invalid email address'
              }
            })}
            className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
          />
          {errors.contact_email && (
            <p className="mt-1 text-sm text-red-600">{errors.contact_email.message}</p>
          )}
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700">
            Contact Phone
          </label>
          <input
            type="tel"
            {...register('contact_phone')}
            className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700">
            Capacity *
          </label>
          <input
            type="number"
            {...register('capacity', { 
              required: 'Capacity is required',
              min: { value: 1, message: 'Capacity must be at least 1' }
            })}
            className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
          />
          {errors.capacity && (
            <p className="mt-1 text-sm text-red-600">{errors.capacity.message}</p>
          )}
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700">
            Status
          </label>
          <select
            {...register('is_active')}
            className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="true">Active</option>
            <option value="false">Inactive</option>
          </select>
        </div>
      </div>

      <div className="flex justify-end space-x-3">
        <button
          type="submit"
          disabled={loading}
          className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
        >
          {loading ? 'Saving...' : warehouse ? 'Update Warehouse' : 'Create Warehouse'}
        </button>
      </div>
    </form>
  );
};

export default WarehouseForm; 