import React, { useState } from 'react';
import { useForm } from 'react-hook-form';

import { 
  ExclamationTriangleIcon,
  CheckCircleIcon,
  XCircleIcon,
  InformationCircleIcon
} from '@heroicons/react/24/outline';
import { Inventory } from '@/types';

interface StockAdjustmentFormProps {
  inventory: Inventory;
  onSubmit: (data: { inventory_id: string; quantity: number; notes: string }) => void;
  loading: boolean;
}

interface FormData {
  adjustment_type: 'add' | 'subtract' | 'set';
  quantity: number;
  notes: string;
}

const StockAdjustmentForm: React.FC<StockAdjustmentFormProps> = ({
  inventory,
  onSubmit,
  loading,
}) => {
  const [adjustmentType, setAdjustmentType] = useState<'add' | 'subtract' | 'set'>('add');
  
  const {
    register,
    handleSubmit,
    watch,
    formState: { errors, isValid },
    reset,
  } = useForm<FormData>({
    defaultValues: {
      adjustment_type: 'add',
      quantity: 0,
      notes: '',
    },
    mode: 'onChange',
  });

  const watchedQuantity = watch('quantity');


  const calculateNewQuantity = () => {
    const quantity = watchedQuantity || 0;
    switch (adjustmentType) {
      case 'add':
        return inventory.quantity + quantity;
      case 'subtract':
        return inventory.quantity - quantity;
      case 'set':
        return quantity;
      default:
        return inventory.quantity;
    }
  };

  const newQuantity = calculateNewQuantity();
  const isNegative = newQuantity < 0;
  const isLowStock = newQuantity <= inventory.reorder_point;
  const isOverMax = newQuantity > inventory.max_stock_level;

  const handleFormSubmit = (data: FormData) => {
    const finalQuantity = calculateNewQuantity();
    
    if (finalQuantity < 0) {
      return; // Don't submit if negative
    }

    onSubmit({
      inventory_id: inventory.id,
      quantity: finalQuantity,
      notes: data.notes,
    });
  };

  const getStatusIcon = () => {
    if (isNegative) {
      return <XCircleIcon className="h-5 w-5 text-red-500" />;
    } else if (isLowStock) {
      return <ExclamationTriangleIcon className="h-5 w-5 text-yellow-500" />;
    } else if (isOverMax) {
      return <InformationCircleIcon className="h-5 w-5 text-blue-500" />;
    } else {
      return <CheckCircleIcon className="h-5 w-5 text-green-500" />;
    }
  };

  const getStatusMessage = () => {
    if (isNegative) {
      return 'Quantity cannot be negative';
    } else if (isLowStock) {
      return 'Stock will be below reorder point';
    } else if (isOverMax) {
      return 'Stock will exceed maximum level';
    } else {
      return 'Stock level is optimal';
    }
  };

  const getStatusColor = () => {
    if (isNegative) {
      return 'text-red-600 bg-red-50 border-red-200';
    } else if (isLowStock) {
      return 'text-yellow-600 bg-yellow-50 border-yellow-200';
    } else if (isOverMax) {
      return 'text-blue-600 bg-blue-50 border-blue-200';
    } else {
      return 'text-green-600 bg-green-50 border-green-200';
    }
  };

  return (
    <div className="space-y-6">
      {/* Product Information */}
      <div className="bg-gray-50 rounded-lg p-4">
        <h4 className="font-medium text-gray-900 mb-2">Product Information</h4>
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <span className="text-gray-500">Product:</span>
            <span className="ml-2 font-medium">{inventory.product.name}</span>
          </div>
          <div>
            <span className="text-gray-500">SKU:</span>
            <span className="ml-2 font-medium">{inventory.product.sku}</span>
          </div>
          <div>
            <span className="text-gray-500">Warehouse:</span>
            <span className="ml-2 font-medium">{inventory.warehouse.name}</span>
          </div>
          <div>
            <span className="text-gray-500">Current Stock:</span>
            <span className="ml-2 font-medium">{inventory.quantity}</span>
          </div>
        </div>
      </div>

      {/* Adjustment Form */}
      <form onSubmit={handleSubmit(handleFormSubmit)} className="space-y-4">
        {/* Adjustment Type */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Adjustment Type
          </label>
          <div className="grid grid-cols-3 gap-3">
            {[
              { value: 'add', label: 'Add Stock', color: 'bg-green-50 border-green-200 text-green-700' },
              { value: 'subtract', label: 'Remove Stock', color: 'bg-red-50 border-red-200 text-red-700' },
              { value: 'set', label: 'Set Stock', color: 'bg-blue-50 border-blue-200 text-blue-700' },
            ].map((type) => (
              <button
                key={type.value}
                type="button"
                onClick={() => setAdjustmentType(type.value as any)}
                className={`p-3 border-2 rounded-lg text-sm font-medium transition-colors ${
                  adjustmentType === type.value
                    ? type.color
                    : 'border-gray-200 bg-white text-gray-700 hover:bg-gray-50'
                }`}
              >
                {type.label}
              </button>
            ))}
          </div>
        </div>

        {/* Quantity Input */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            {adjustmentType === 'add' && 'Quantity to Add'}
            {adjustmentType === 'subtract' && 'Quantity to Remove'}
            {adjustmentType === 'set' && 'New Stock Level'}
          </label>
          <input
            type="number"
            min="0"
            step="1"
            {...register('quantity', {
              required: 'Quantity is required',
              min: { value: 0, message: 'Quantity must be positive' },
              validate: (value) => {
                if (adjustmentType === 'subtract' && value > inventory.quantity) {
                  return 'Cannot remove more than current stock';
                }
                return true;
              },
            })}
            className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${
              errors.quantity ? 'border-red-300' : 'border-gray-300'
            }`}
            placeholder="Enter quantity"
          />
          {errors.quantity && (
            <p className="mt-1 text-sm text-red-600">{errors.quantity.message}</p>
          )}
        </div>

        {/* Notes */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Notes (Optional)
          </label>
          <textarea
            {...register('notes')}
            rows={3}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Reason for adjustment, reference numbers, etc."
          />
        </div>

        {/* Preview */}
        <div className="bg-gray-50 rounded-lg p-4">
          <h4 className="font-medium text-gray-900 mb-3">Adjustment Preview</h4>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span className="text-gray-500">Current Stock:</span>
              <span className="ml-2 font-medium">{inventory.quantity}</span>
            </div>
            <div>
              <span className="text-gray-500">New Stock:</span>
              <span className={`ml-2 font-medium ${isNegative ? 'text-red-600' : ''}`}>
                {newQuantity}
              </span>
            </div>
            <div>
              <span className="text-gray-500">Reorder Point:</span>
              <span className="ml-2 font-medium">{inventory.reorder_point}</span>
            </div>
            <div>
              <span className="text-gray-500">Max Level:</span>
              <span className="ml-2 font-medium">{inventory.max_stock_level}</span>
            </div>
          </div>
        </div>

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
            disabled={loading || !isValid || isNegative}
            className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Adjusting...' : 'Adjust Stock'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default StockAdjustmentForm; 