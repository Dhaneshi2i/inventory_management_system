import React, { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { motion } from 'framer-motion';
import { 
  TruckIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
  InformationCircleIcon
} from '@heroicons/react/24/outline';
import { Warehouse, Inventory } from '@/types';

interface StockTransferFormProps {
  warehouses: Warehouse[];
  inventory: Inventory[];
  onSubmit: (data: { 
    from_warehouse_id: string; 
    to_warehouse_id: string; 
    product_id: string; 
    quantity: number; 
    notes: string 
  }) => void;
  loading: boolean;
}

interface FormData {
  from_warehouse_id: string;
  to_warehouse_id: string;
  product_id: string;
  quantity: number;
  notes: string;
}

const StockTransferForm: React.FC<StockTransferFormProps> = ({
  warehouses,
  inventory,
  onSubmit,
  loading,
}) => {
  const [selectedProduct, setSelectedProduct] = useState<Inventory | null>(null);
  const [availableQuantity, setAvailableQuantity] = useState(0);
  
  const {
    register,
    handleSubmit,
    watch,
    setValue,
    formState: { errors, isValid },
    reset,
  } = useForm<FormData>({
    defaultValues: {
      from_warehouse_id: '',
      to_warehouse_id: '',
      product_id: '',
      quantity: 0,
      notes: '',
    },
    mode: 'onChange',
  });

  const watchedFromWarehouse = watch('from_warehouse_id');
  const watchedToWarehouse = watch('to_warehouse_id');
  const watchedProduct = watch('product_id');
  const watchedQuantity = watch('quantity');

  // Filter available products based on selected warehouse
  const availableProducts = inventory.filter(
    item => item.warehouse.id === watchedFromWarehouse && item.quantity > 0
  );

  // Update available quantity when product changes
  useEffect(() => {
    if (watchedProduct) {
      const product = inventory.find(item => item.id === watchedProduct);
      if (product) {
        setSelectedProduct(product);
        setAvailableQuantity(product.available_quantity);
        setValue('quantity', 0);
      }
    } else {
      setSelectedProduct(null);
      setAvailableQuantity(0);
    }
  }, [watchedProduct, inventory, setValue]);

  const handleFormSubmit = (data: FormData) => {
    if (data.quantity > availableQuantity) {
      return; // Don't submit if quantity exceeds available
    }

    onSubmit(data);
  };

  const isQuantityValid = watchedQuantity <= availableQuantity && watchedQuantity > 0;
  const isTransferValid = watchedFromWarehouse && watchedProduct && isQuantityValid;

  const getStatusIcon = () => {
    if (!watchedFromWarehouse || !watchedProduct) {
      return <InformationCircleIcon className="h-5 w-5 text-blue-500" />;
    } else if (!isQuantityValid) {
      return <ExclamationTriangleIcon className="h-5 w-5 text-yellow-500" />;
    } else {
      return <CheckCircleIcon className="h-5 w-5 text-green-500" />;
    }
  };

  const getStatusMessage = () => {
    if (!watchedFromWarehouse) {
      return 'Please select source warehouse';
    } else if (!watchedProduct) {
      return 'Please select a product to transfer';
    } else if (watchedQuantity > availableQuantity) {
      return 'Quantity exceeds available stock';
    } else if (watchedQuantity <= 0) {
      return 'Please enter a valid quantity';
    } else {
      return 'Transfer is ready';
    }
  };

  const getStatusColor = () => {
    if (!watchedFromWarehouse || !watchedProduct) {
      return 'text-blue-600 bg-blue-50 border-blue-200';
    } else if (!isQuantityValid) {
      return 'text-yellow-600 bg-yellow-50 border-yellow-200';
    } else {
      return 'text-green-600 bg-green-50 border-green-200';
    }
  };

  return (
    <div className="space-y-6">
      <form onSubmit={handleSubmit(handleFormSubmit)} className="space-y-4">
        {/* Source Warehouse */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Source Warehouse *
          </label>
          <select
            {...register('from_warehouse_id', { required: 'Source warehouse is required' })}
            className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${
              errors.from_warehouse_id ? 'border-red-300' : 'border-gray-300'
            }`}
          >
            <option value="">Select source warehouse</option>
            {warehouses.map((warehouse) => (
              <option key={warehouse.id} value={warehouse.id}>
                {warehouse.name} ({warehouse.inventory_count} items)
              </option>
            ))}
          </select>
          {errors.from_warehouse_id && (
            <p className="mt-1 text-sm text-red-600">{errors.from_warehouse_id.message}</p>
          )}
        </div>

        {/* Destination Warehouse */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Destination Warehouse *
          </label>
          <select
            {...register('to_warehouse_id', { 
              required: 'Destination warehouse is required',
              validate: (value) => value !== watchedFromWarehouse || 'Source and destination must be different'
            })}
            className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${
              errors.to_warehouse_id ? 'border-red-300' : 'border-gray-300'
            }`}
          >
            <option value="">Select destination warehouse</option>
            {warehouses
              .filter(warehouse => warehouse.id !== watchedFromWarehouse)
              .map((warehouse) => (
                <option key={warehouse.id} value={warehouse.id}>
                  {warehouse.name} (Capacity: {warehouse.available_capacity})
                </option>
              ))}
          </select>
          {errors.to_warehouse_id && (
            <p className="mt-1 text-sm text-red-600">{errors.to_warehouse_id.message}</p>
          )}
        </div>

        {/* Product Selection */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Product to Transfer *
          </label>
          <select
            {...register('product_id', { required: 'Product is required' })}
            className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${
              errors.product_id ? 'border-red-300' : 'border-gray-300'
            }`}
            disabled={!watchedFromWarehouse}
          >
            <option value="">Select a product</option>
            {availableProducts.map((item) => (
              <option key={item.id} value={item.id}>
                {item.product.name} (SKU: {item.product.sku}) - Available: {item.available_quantity}
              </option>
            ))}
          </select>
          {errors.product_id && (
            <p className="mt-1 text-sm text-red-600">{errors.product_id.message}</p>
          )}
        </div>

        {/* Product Details */}
        {selectedProduct && (
          <div className="bg-gray-50 rounded-lg p-4">
            <h4 className="font-medium text-gray-900 mb-2">Product Details</h4>
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <span className="text-gray-500">Product:</span>
                <span className="ml-2 font-medium">{selectedProduct.product.name}</span>
              </div>
              <div>
                <span className="text-gray-500">SKU:</span>
                <span className="ml-2 font-medium">{selectedProduct.product.sku}</span>
              </div>
              <div>
                <span className="text-gray-500">Current Stock:</span>
                <span className="ml-2 font-medium">{selectedProduct.quantity}</span>
              </div>
              <div>
                <span className="text-gray-500">Available:</span>
                <span className="ml-2 font-medium">{selectedProduct.available_quantity}</span>
              </div>
            </div>
          </div>
        )}

        {/* Quantity */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Transfer Quantity *
          </label>
          <input
            type="number"
            min="1"
            max={availableQuantity}
            step="1"
            {...register('quantity', {
              required: 'Quantity is required',
              min: { value: 1, message: 'Quantity must be at least 1' },
              max: { value: availableQuantity, message: `Cannot transfer more than ${availableQuantity}` },
            })}
            className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${
              errors.quantity ? 'border-red-300' : 'border-gray-300'
            }`}
            placeholder={`Enter quantity (max: ${availableQuantity})`}
            disabled={!selectedProduct}
          />
          {errors.quantity && (
            <p className="mt-1 text-sm text-red-600">{errors.quantity.message}</p>
          )}
          {selectedProduct && (
            <p className="mt-1 text-sm text-gray-500">
              Available for transfer: {availableQuantity} units
            </p>
          )}
        </div>

        {/* Notes */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Transfer Notes (Optional)
          </label>
          <textarea
            {...register('notes')}
            rows={3}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Reason for transfer, reference numbers, etc."
          />
        </div>

        {/* Transfer Preview */}
        {watchedFromWarehouse && watchedProduct && (
          <div className="bg-blue-50 rounded-lg p-4">
            <h4 className="font-medium text-gray-900 mb-3 flex items-center">
              <TruckIcon className="h-5 w-5 mr-2 text-blue-500" />
              Transfer Preview
            </h4>
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <span className="text-gray-500">From:</span>
                <span className="ml-2 font-medium">
                  {warehouses.find(w => w.id === watchedFromWarehouse)?.name}
                </span>
              </div>
              <div>
                <span className="text-gray-500">To:</span>
                <span className="ml-2 font-medium">
                  {warehouses.find(w => w.id === watchedToWarehouse)?.name}
                </span>
              </div>
              <div>
                <span className="text-gray-500">Product:</span>
                <span className="ml-2 font-medium">{selectedProduct?.product.name}</span>
              </div>
              <div>
                <span className="text-gray-500">Quantity:</span>
                <span className="ml-2 font-medium">{watchedQuantity || 0}</span>
              </div>
            </div>
          </div>
        )}

        {/* Status Indicator */}
        <div className={`flex items-center p-3 border rounded-lg ${getStatusColor()}`}>
          {getStatusIcon()}
          <span className="ml-2 text-sm font-medium">{getStatusMessage()}</span>
        </div>

        {/* Action Buttons */}
        <div className="flex justify-end space-x-3 pt-4">
          <button
            type="button"
            onClick={() => reset()}
            className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            disabled={loading}
          >
            Reset
          </button>
          <button
            type="submit"
            disabled={loading || !isTransferValid}
            className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Transferring...' : 'Transfer Stock'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default StockTransferForm; 