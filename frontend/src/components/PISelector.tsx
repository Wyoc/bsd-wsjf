import React, { useState, useEffect } from 'react';
import { ProgramIncrementResponse, PIStatus } from '../types/wsjf';
import { apiClient } from '../api/client';

interface PISelectorProps {
  selectedPI: ProgramIncrementResponse | null;
  onPISelect: (pi: ProgramIncrementResponse | null) => void;
  onCreatePI: () => void;
}

export const PISelector: React.FC<PISelectorProps> = ({
  selectedPI,
  onPISelect,
  onCreatePI,
}) => {
  const [pis, setPIs] = useState<ProgramIncrementResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadPIs();
  }, []);

  const loadPIs = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await apiClient.getPIs();
      setPIs(data);
    } catch (err: any) {
      setError(err.detail || 'Failed to load Program Increments');
    } finally {
      setLoading(false);
    }
  };

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
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="animate-pulse">
          <div className="h-4 bg-gray-200 rounded w-1/4 mb-4"></div>
          <div className="h-10 bg-gray-200 rounded"></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="text-red-600 mb-4">{error}</div>
        <button
          onClick={loadPIs}
          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
        >
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-lg font-semibold text-gray-800">Program Increment</h2>
        <button
          onClick={onCreatePI}
          className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 text-sm"
        >
          Create PI
        </button>
      </div>

      {pis.length === 0 ? (
        <div className="text-center py-8 text-gray-500">
          <p className="mb-4">No Program Increments found.</p>
          <button
            onClick={onCreatePI}
            className="px-6 py-3 bg-blue-600 text-white rounded-md hover:bg-blue-700"
          >
            Create Your First PI
          </button>
        </div>
      ) : (
        <div className="space-y-4">
          <div className="mb-4">
            <select
              value={selectedPI?.id || ''}
              onChange={(e) => {
                const pi = e.target.value ? pis.find(p => p.id === e.target.value) : null;
                onPISelect(pi || null);
              }}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Select a Program Increment</option>
              {pis.map((pi) => (
                <option key={pi.id} value={pi.id}>
                  {pi.name} ({pi.item_count} items)
                </option>
              ))}
            </select>
          </div>

          {selectedPI && (
            <div className="border border-gray-200 rounded-md p-4 bg-gray-50">
              <div className="flex justify-between items-start mb-2">
                <h3 className="font-medium text-gray-800">{selectedPI.name}</h3>
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(selectedPI.status)}`}>
                  {selectedPI.status}
                </span>
              </div>
              {selectedPI.description && (
                <p className="text-gray-600 text-sm mb-2">{selectedPI.description}</p>
              )}
              <div className="flex justify-between text-sm text-gray-500">
                <span>{formatDate(selectedPI.start_date)} - {formatDate(selectedPI.end_date)}</span>
                <span>{selectedPI.item_count} items</span>
              </div>
            </div>
          )}

          {pis.length > 0 && (
            <div className="mt-6">
              <h3 className="text-md font-medium text-gray-700 mb-3">All Program Increments</h3>
              <div className="grid gap-3">
                {pis.map((pi) => (
                  <div
                    key={pi.id}
                    className={`border rounded-md p-3 cursor-pointer transition-colors ${
                      selectedPI?.id === pi.id 
                        ? 'border-blue-500 bg-blue-50' 
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                    onClick={() => onPISelect(pi)}
                  >
                    <div className="flex justify-between items-start">
                      <div className="flex-1">
                        <h4 className="font-medium text-gray-800">{pi.name}</h4>
                        {pi.description && (
                          <p className="text-gray-600 text-sm mt-1">{pi.description}</p>
                        )}
                        <div className="flex justify-between items-center mt-2">
                          <span className="text-xs text-gray-500">
                            {formatDate(pi.start_date)} - {formatDate(pi.end_date)}
                          </span>
                          <span className="text-xs text-gray-500">{pi.item_count} items</span>
                        </div>
                      </div>
                      <span className={`ml-3 px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(pi.status)}`}>
                        {pi.status}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};