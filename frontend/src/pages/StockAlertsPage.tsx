import React, { useState } from 'react';
import { 
  BellIcon,
  CogIcon,
  EyeIcon,
  PlusIcon
} from '@heroicons/react/24/outline';
import { toast } from 'react-hot-toast';

import { 
  useStockAlerts, 
  useResolveStockAlert,
  useAlertRules,
  useAlertNotifications,
  useCreateAlertRule
} from '@/hooks/useApi';
import LoadingSpinner from '@/components/LoadingSpinner';
import Modal from '@/components/Modal';

// Components
import AlertList from '@/components/alerts/AlertList';
import AlertConfiguration from '@/components/alerts/AlertConfiguration';
import NotificationCenter from '@/components/alerts/NotificationCenter';
import AlertMetrics from '@/components/alerts/AlertMetrics';

const StockAlertsPage: React.FC = () => {
  const [selectedView, setSelectedView] = useState<'alerts' | 'rules' | 'notifications'>('alerts');
  const [isConfigModalOpen, setIsConfigModalOpen] = useState(false);

  const [filters, setFilters] = useState({
    alert_type: '',
    severity: '',
    is_resolved: false,
  });

  // Queries
  const { data: alerts, isLoading: alertsLoading } = useStockAlerts(filters);

  const { isLoading: rulesLoading } = useAlertRules();

  const { data: notifications, isLoading: notificationsLoading } = useAlertNotifications();

  // Mutations
  const resolveAlertMutation = useResolveStockAlert({
    onSuccess: () => {
      toast.success('Alert resolved successfully');
    },
  });

  const createAlertRuleMutation = useCreateAlertRule({
    onSuccess: () => {
      setIsConfigModalOpen(false);
    },
  });

  const handleResolveAlert = (alertId: string, resolutionNotes: string) => {
    resolveAlertMutation.mutate({ id: alertId, resolution_notes: resolutionNotes });
  };

  const handleCreateRule = (data: any) => {
    createAlertRuleMutation.mutate(data);
  };

  if (alertsLoading || rulesLoading || notificationsLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Alert Management</h1>
          <p className="mt-1 text-sm text-gray-500">
            Monitor and manage stock alerts and notifications
          </p>
        </div>
        <div className="mt-4 sm:mt-0 flex flex-wrap gap-2">
          <button
            onClick={() => setSelectedView('alerts')}
            className={`inline-flex items-center px-3 py-2 border text-sm font-medium rounded-md ${
              selectedView === 'alerts'
                ? 'border-blue-500 bg-blue-50 text-blue-700'
                : 'border-gray-300 bg-white text-gray-700 hover:bg-gray-50'
            }`}
          >
            <BellIcon className="h-4 w-4 mr-2" />
            Alerts
          </button>
          <button
            onClick={() => setSelectedView('rules')}
            className={`inline-flex items-center px-3 py-2 border text-sm font-medium rounded-md ${
              selectedView === 'rules'
                ? 'border-blue-500 bg-blue-50 text-blue-700'
                : 'border-gray-300 bg-white text-gray-700 hover:bg-gray-50'
            }`}
          >
            <CogIcon className="h-4 w-4 mr-2" />
            Rules
          </button>
          <button
            onClick={() => setSelectedView('notifications')}
            className={`inline-flex items-center px-3 py-2 border text-sm font-medium rounded-md ${
              selectedView === 'notifications'
                ? 'border-blue-500 bg-blue-50 text-blue-700'
                : 'border-gray-300 bg-white text-gray-700 hover:bg-gray-50'
            }`}
          >
            <EyeIcon className="h-4 w-4 mr-2" />
            Notifications
          </button>
          <button
            onClick={() => setIsConfigModalOpen(true)}
            className="inline-flex items-center px-3 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
          >
            <PlusIcon className="h-4 w-4 mr-2" />
            Create Rule
          </button>
        </div>
      </div>

      {/* Metrics */}
      <AlertMetrics alerts={alerts?.results || []} />

      {/* Main Content */}
      {selectedView === 'alerts' && (
        <div className="space-y-6">
          {/* Filters */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
            <div className="flex flex-col sm:flex-row sm:items-center space-y-3 sm:space-y-0 sm:space-x-4">
              <select
                value={filters.alert_type}
                onChange={(e) => setFilters(prev => ({ ...prev, alert_type: e.target.value }))}
                className="px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="">All Alert Types</option>
                <option value="low_stock">Low Stock</option>
                <option value="out_of_stock">Out of Stock</option>
                <option value="overstock">Overstock</option>
              </select>

              <select
                value={filters.severity}
                onChange={(e) => setFilters(prev => ({ ...prev, severity: e.target.value }))}
                className="px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="">All Severities</option>
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
                <option value="critical">Critical</option>
              </select>

              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={filters.is_resolved}
                  onChange={(e) => setFilters(prev => ({ ...prev, is_resolved: e.target.checked }))}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <span className="ml-2 text-sm text-gray-700">Show Resolved</span>
              </label>
            </div>
          </div>

          {/* Alerts List */}
          <AlertList
            alerts={alerts?.results || []}
            loading={alertsLoading}
            onResolveAlert={handleResolveAlert}
            filters={filters}
          />
        </div>
      )}

      {selectedView === 'rules' && (
        <div className="space-y-6">
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Alert Rules</h3>
            <div className="text-center">
              <CogIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <h4 className="text-lg font-medium text-gray-900 mb-2">Alert Configuration</h4>
              <p className="text-sm text-gray-500 mb-6">
                Configure alert rules and notification preferences - Coming soon!
              </p>
              <div className="bg-gray-50 rounded-lg p-4">
                <p className="text-sm text-gray-600">
                  This will include rule creation, threshold settings, and notification channel configuration.
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      {selectedView === 'notifications' && (
        <div className="space-y-6">
          <NotificationCenter
            notifications={notifications?.results || []}
            loading={notificationsLoading}
          />
        </div>
      )}

      {/* Modals */}
      <Modal
        isOpen={isConfigModalOpen}
        onClose={() => setIsConfigModalOpen(false)}
        title="Create Alert Rule"
        size="lg"
      >
        <AlertConfiguration
          onSubmit={handleCreateRule}
          loading={createAlertRuleMutation.isPending}
        />
      </Modal>
    </div>
  );
};

export default StockAlertsPage; 