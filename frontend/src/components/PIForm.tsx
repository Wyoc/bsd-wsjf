import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { ProgramIncrementCreate, PIStatus } from '../types/wsjf';
import { apiClient } from '../api/client';

interface PIFormProps {
  onSuccess: () => void;
  onCancel: () => void;
}

interface PIFormData {
  name: string;
  description: string;
  start_date: string;
  end_date: string;
  status: PIStatus;
}

export const PIForm: React.FC<PIFormProps> = ({ onSuccess, onCancel }) => {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors },
    watch
  } = useForm<PIFormData>({
    defaultValues: {
      name: '',
      description: '',
      start_date: '',
      end_date: '',
      status: PIStatus.PLANNING,
    },
  });

  const startDate = watch('start_date');

  const onSubmit = async (data: PIFormData) => {
    try {
      setIsSubmitting(true);
      setSubmitError(null);

      const piData: ProgramIncrementCreate = {
        name: data.name,
        description: data.description,
        start_date: new Date(data.start_date).toISOString(),
        end_date: new Date(data.end_date).toISOString(),
        status: data.status,
      };

      await apiClient.createPI(piData);
      onSuccess();
    } catch (error: any) {
      setSubmitError(error.detail || 'Failed to create Program Increment');
    } finally {
      setIsSubmitting(false);
    }
  };

  const today = new Date().toISOString().split('T')[0];

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h2 className="text-xl font-semibold text-gray-800 mb-6">Create Program Increment</h2>
      
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        {submitError && (
          <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-md">
            {submitError}
          </div>
        )}

        <div>
          <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-1">
            Name *
          </label>
          <input
            {...register('name', { 
              required: 'PI name is required',
              minLength: { value: 1, message: 'Name must be at least 1 character' },
              maxLength: { value: 100, message: 'Name must be less than 100 characters' }
            })}
            type="text"
            id="name"
            placeholder="e.g., PI19, Sprint 2024-Q4"
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          {errors.name && (
            <p className="mt-1 text-sm text-red-600">{errors.name.message}</p>
          )}
        </div>

        <div>
          <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-1">
            Description
          </label>
          <textarea
            {...register('description', {
              maxLength: { value: 500, message: 'Description must be less than 500 characters' }
            })}
            id="description"
            rows={3}
            placeholder="Brief description of this Program Increment"
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          {errors.description && (
            <p className="mt-1 text-sm text-red-600">{errors.description.message}</p>
          )}
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label htmlFor="start_date" className="block text-sm font-medium text-gray-700 mb-1">
              Start Date *
            </label>
            <input
              {...register('start_date', { 
                required: 'Start date is required'
              })}
              type="date"
              id="start_date"
              min={today}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            {errors.start_date && (
              <p className="mt-1 text-sm text-red-600">{errors.start_date.message}</p>
            )}
          </div>

          <div>
            <label htmlFor="end_date" className="block text-sm font-medium text-gray-700 mb-1">
              End Date *
            </label>
            <input
              {...register('end_date', { 
                required: 'End date is required',
                validate: (value) => {
                  if (startDate && value && new Date(value) <= new Date(startDate)) {
                    return 'End date must be after start date';
                  }
                  return true;
                }
              })}
              type="date"
              id="end_date"
              min={startDate || today}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            {errors.end_date && (
              <p className="mt-1 text-sm text-red-600">{errors.end_date.message}</p>
            )}
          </div>
        </div>

        <div>
          <label htmlFor="status" className="block text-sm font-medium text-gray-700 mb-1">
            Status
          </label>
          <select
            {...register('status')}
            id="status"
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            {Object.values(PIStatus).map((status) => (
              <option key={status} value={status}>
                {status}
              </option>
            ))}
          </select>
        </div>

        <div className="flex justify-end space-x-3 pt-4">
          <button
            type="button"
            onClick={onCancel}
            disabled={isSubmitting}
            className="px-4 py-2 text-gray-700 bg-gray-100 border border-gray-300 rounded-md hover:bg-gray-200 disabled:opacity-50"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={isSubmitting}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isSubmitting ? 'Creating...' : 'Create PI'}
          </button>
        </div>
      </form>
    </div>
  );
};