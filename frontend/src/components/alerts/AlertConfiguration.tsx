import React from 'react';

interface AlertConfigurationProps {
  onSubmit: (data: any) => void;
  loading: boolean;
}

const AlertConfiguration: React.FC<AlertConfigurationProps> = ({
  onSubmit: _onSubmit,
  loading: _loading,
}) => {
  return (
    <div className="p-6">
      <div className="text-center">
        <h3 className="text-lg font-medium text-gray-900 mb-2">Alert Configuration</h3>
        <p className="text-sm text-gray-500 mb-6">
          Configure alert rules and notification settings - Coming soon!
        </p>
        <div className="bg-gray-50 rounded-lg p-4">
          <p className="text-sm text-gray-600">
            This will include threshold settings, notification channels, and rule creation.
          </p>
        </div>
      </div>
    </div>
  );
};

export default AlertConfiguration; 