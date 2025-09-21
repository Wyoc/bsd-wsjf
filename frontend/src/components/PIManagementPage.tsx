import React, { useState, useEffect } from 'react';
import { Plus, Calendar, BarChart3 } from 'lucide-react';
import { ProgramIncrementResponse, PIStatus } from '../types/wsjf';
import { PIForm } from './PIForm';
import { apiClient } from '../api/client';
import toast from 'react-hot-toast';

interface PIManagementPageProps {
  onPICreated: () => void;
}

export const PIManagementPage: React.FC<PIManagementPageProps> = ({ onPICreated }) => {
  const [pis, setPIs] = useState<ProgramIncrementResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreateForm, setShowCreateForm] = useState(false);
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
      toast.error('Failed to load Program Increments');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateSuccess = () => {
    setShowCreateForm(false);
    loadPIs();
    onPICreated();
    toast.success('Program Increment created successfully');
  };

  const handleDeletePI = async (pi: ProgramIncrementResponse) => {
    if (pi.item_count > 0) {
      toast.error(`Cannot delete PI with ${pi.item_count} items. Remove items first.`);
      return;
    }

    if (window.confirm(`Are you sure you want to delete "${pi.name}"? This action cannot be undone.`)) {
      try {
        await apiClient.deletePI(pi.id);
        toast.success('Program Increment deleted successfully');
        loadPIs();
        onPICreated();
      } catch (error: any) {
        toast.error(error.detail || 'Failed to delete Program Increment');
      }
    }
  };

  const getStatusColor = (status: PIStatus) => {
    switch (status) {
      case PIStatus.PLANNING:
        return 'bg-blue-100 text-blue-800 border-blue-200';
      case PIStatus.ACTIVE:
        return 'bg-green-100 text-green-800 border-green-200';
      case PIStatus.COMPLETED:
        return 'bg-gray-100 text-gray-800 border-gray-200';
      case PIStatus.CANCELLED:
        return 'bg-red-100 text-red-800 border-red-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString();
  };

  const getDaysRemaining = (endDate: string) => {
    const end = new Date(endDate);
    const now = new Date();
    const diffTime = end.getTime() - now.getTime();
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return diffDays;
  };

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <div className="animate-pulse space-y-4">
            <div className="h-8 bg-gray-200 rounded w-1/4"></div>
            <div className="grid gap-4">
              {[1, 2, 3].map((i) => (
                <div key={i} className="h-32 bg-gray-200 rounded"></div>
              ))}
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <div className="bg-red-50 border border-red-200 rounded-md p-4">
            <div className="text-red-800">{error}</div>
            <button
              onClick={loadPIs}
              className="mt-2 px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700"
            >
              Retry
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
      <div className="px-4 py-6 sm:px-0">
        <div className="flex justify-between items-center mb-6">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Program Increment Management</h1>
            <p className="mt-1 text-sm text-gray-600">
              Create and manage Program Increments for your organization
            </p>
          </div>
          <button
            onClick={() => setShowCreateForm(true)}
            className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            <Plus className="h-4 w-4 mr-2" />
            Create PI
          </button>
        </div>

        {pis.length === 0 ? (
          <div className="text-center py-12 bg-white rounded-lg shadow">
            <Calendar className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">No Program Increments</h3>
            <p className="mt-1 text-sm text-gray-500">
              Get started by creating your first Program Increment.
            </p>
            <div className="mt-6">
              <button
                onClick={() => setShowCreateForm(true)}
                className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
              >
                <Plus className="h-4 w-4 mr-2" />
                Create PI
              </button>
            </div>
          </div>
        ) : (
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {pis.map((pi) => {
              const daysRemaining = getDaysRemaining(pi.end_date);
              return (
                <div
                  key={pi.id}
                  className="bg-white overflow-hidden shadow rounded-lg border hover:shadow-md transition-shadow"
                >
                  <div className="px-4 py-5 sm:p-6">
                    <div className="flex items-center justify-between mb-3">
                      <h3 className="text-lg font-medium text-gray-900 truncate">
                        {pi.name}
                      </h3>
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${getStatusColor(pi.status)}`}>
                        {pi.status}
                      </span>
                    </div>
                    
                    {pi.description && (
                      <p className="text-gray-600 text-sm mb-4 line-clamp-2">
                        {pi.description}
                      </p>
                    )}

                    <div className="space-y-2 text-sm text-gray-500 mb-4">
                      <div className="flex items-center">
                        <Calendar className="h-4 w-4 mr-2" />
                        <span>{formatDate(pi.start_date)} - {formatDate(pi.end_date)}</span>
                      </div>
                      <div className="flex items-center">
                        <BarChart3 className="h-4 w-4 mr-2" />
                        <span>{pi.item_count} WSJF items</span>
                      </div>
                      {pi.status === PIStatus.ACTIVE && (
                        <div className="flex items-center">
                          <span className="h-4 w-4 mr-2">⏰</span>
                          <span className={daysRemaining > 0 ? 'text-green-600' : 'text-red-600'}>
                            {daysRemaining > 0 ? `${daysRemaining} days remaining` : `${Math.abs(daysRemaining)} days overdue`}
                          </span>
                        </div>
                      )}
                    </div>

                    <div className="flex justify-end space-x-2">
                      <button
                        onClick={() => handleDeletePI(pi)}
                        className="px-3 py-1 text-xs font-medium text-red-600 hover:text-red-800 hover:bg-red-50 rounded-md border border-red-200 hover:border-red-300"
                        disabled={pi.item_count > 0}
                        title={pi.item_count > 0 ? 'Cannot delete PI with items' : 'Delete PI'}
                      >
                        Delete
                      </button>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}

        {showCreateForm && (
          <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
            <div className="relative top-20 mx-auto p-5 border w-11/12 max-w-2xl shadow-lg rounded-md bg-white">
              <PIForm
                onSuccess={handleCreateSuccess}
                onCancel={() => setShowCreateForm(false)}
              />
            </div>
          </div>
        )}
      </div>
    </div>
  );
};