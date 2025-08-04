import React from 'react';
import { StockAlert } from '@/types';
import LoadingSpinner from '../LoadingSpinner';

interface AlertListProps {
  alerts: StockAlert[];
  loading: boolean;
  onResolveAlert: (alertId: string, resolutionNotes: string) => void;
  filters: any;
}

const AlertList: React.FC<AlertListProps> = ({
  alerts,
  loading,
  onResolveAlert,
  filters,
}) => {
  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="p-6">
          <LoadingSpinner size="lg" />
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200">
      <div className="px-6 py-4 border-b border-gray-200">
        <h3 className="text-lg font-medium text-gray-900">Stock Alerts</h3>
      </div>
      <div className="p-6">
        <div className="text-center">
          <div className="text-gray-400 text-sm mb-2">Alert List</div>
          <div className="text-xs text-gray-500">
            List of stock alerts with filtering and resolution capabilities
          </div>
        </div>
      </div>
    </div>
  );
};

export default AlertList; 