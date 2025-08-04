import React from 'react';
import { AlertNotification } from '@/types';
import LoadingSpinner from '../LoadingSpinner';

interface NotificationCenterProps {
  notifications: AlertNotification[];
  loading: boolean;
}

const NotificationCenter: React.FC<NotificationCenterProps> = ({
  notifications: _notifications,
  loading,
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
        <h3 className="text-lg font-medium text-gray-900">Notification Center</h3>
      </div>
      <div className="p-6">
        <div className="text-center">
          <div className="text-gray-400 text-sm mb-2">Notification Center</div>
          <div className="text-xs text-gray-500">
            View and manage alert notifications and delivery status
          </div>
        </div>
      </div>
    </div>
  );
};

export default NotificationCenter; 