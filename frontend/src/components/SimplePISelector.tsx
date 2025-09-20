import React from 'react';
import { ProgramIncrementResponse, PIStatus } from '../types/wsjf';

interface SimplePISelectorProps {
  pis: ProgramIncrementResponse[];
  selectedPI: ProgramIncrementResponse | null;
  onPISelect: (pi: ProgramIncrementResponse | null) => void;
  loading?: boolean;
}

export const SimplePISelector: React.FC<SimplePISelectorProps> = ({
  pis,
  selectedPI,
  onPISelect,
  loading = false,
}) => {
  const getStatusColor = (status: PIStatus) => {
    switch (status) {
      case PIStatus.PLANNING:
        return 'bg-blue-100 text-blue-800';
      case PIStatus.ACTIVE:
        return 'bg-green-100 text-green-800';
      case PIStatus.COMPLETED:
        return 'bg-gray-100 text-gray-800';
      case PIStatus.CANCELLED:
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString();
  };

  if (loading) {
    return (
      <div className="mb-6">
        <div className="animate-pulse">
          <div className="h-4 bg-gray-200 rounded w-1/4 mb-2"></div>
          <div className="h-10 bg-gray-200 rounded"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="mb-6">
      <label htmlFor="pi-select" className="block text-sm font-medium text-gray-700 mb-2">
        Program Increment
      </label>
      <div className="flex flex-col space-y-2">
        <select
          id="pi-select"
          value={selectedPI?.id || ''}
          onChange={(e) => {
            const pi = e.target.value ? pis.find(p => p.id === e.target.value) : null;
            onPISelect(pi || null);
          }}
          className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
        >
          <option value="">Select a Program Increment</option>
          {pis.map((pi) => (
            <option key={pi.id} value={pi.id}>
              {pi.name} - {pi.status} ({pi.item_count} items)
            </option>
          ))}
        </select>

        {selectedPI && (
          <div className="mt-3 p-3 bg-gray-50 border border-gray-200 rounded-md">
            <div className="flex justify-between items-start mb-2">
              <h3 className="font-medium text-gray-900">{selectedPI.name}</h3>
              <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(selectedPI.status)}`}>
                {selectedPI.status}
              </span>
            </div>
            {selectedPI.description && (
              <p className="text-gray-600 text-sm mb-2">{selectedPI.description}</p>
            )}
            <div className="flex justify-between items-center text-sm text-gray-500">
              <span>{formatDate(selectedPI.start_date)} - {formatDate(selectedPI.end_date)}</span>
              <span>{selectedPI.item_count} items</span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};