import { useForm } from 'react-hook-form';
import { WSJFItemCreate, WSJFStatus, WSJFItem, FIBONACCI_VALUES, FibonacciValue, WSJFSubValues, SUB_VALUE_LABELS, ProgramIncrementResponse } from '../types/wsjf';
import { ScoreCalculator } from './ScoreCalculator';
import { X } from 'lucide-react';

interface WSJFFormProps {
  onSubmit: (data: WSJFItemCreate) => Promise<void>;
  onCancel: () => void;
  initialData?: WSJFItem;
  loading?: boolean;
  selectedPI?: ProgramIncrementResponse | null;
  availablePIs?: ProgramIncrementResponse[];
}

export const WSJFForm = ({ onSubmit, onCancel, initialData, loading, selectedPI, availablePIs }: WSJFFormProps) => {
  const createEmptySubValues = (): WSJFSubValues => ({
    pms_business: null,
    pos_business: null,
    bos_agri_business: null,
    bos_cabinet_business: null,
    consultants_business: null,
    dev_business: null,
    dev_technical: null,
    ia_business: null,
    ia_technical: null,
    devops_business: null,
    devops_technical: null,
    support_business: null,
  });

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors },
  } = useForm<WSJFItemCreate>({
    defaultValues: initialData || {
      subject: '',
      description: '',
      business_value: createEmptySubValues(),
      time_criticality: createEmptySubValues(),
      risk_reduction: createEmptySubValues(),
      job_size: 5 as FibonacciValue,
      status: WSJFStatus.NEW,
      owner: '',
      team: '',
      program_increment_id: selectedPI?.id || '',
    },
  });

  const businessValue = watch('business_value');
  const timeCriticality = watch('time_criticality');
  const riskReduction = watch('risk_reduction');
  const jobSize = watch('job_size');

  const handleFormSubmit = async (data: WSJFItemCreate) => {
    try {
      await onSubmit(data);
      onCancel();
    } catch (error) {
      // Error handling is done in the hook
    }
  };

  return (
    <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
      <div className="relative top-20 mx-auto p-5 border w-11/12 max-w-6xl shadow-lg rounded-md bg-white">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-medium text-gray-900">
            {initialData ? 'Edit WSJF Item' : 'Create New WSJF Item'}
          </h3>
          <button
            onClick={onCancel}
            className="text-gray-400 hover:text-gray-600"
          >
            <X className="h-6 w-6" />
          </button>
        </div>

        <form onSubmit={handleSubmit(handleFormSubmit)} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700">
              Subject *
            </label>
            <input
              {...register('subject', { required: 'Subject is required' })}
              className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
            />
            {errors.subject && (
              <p className="mt-1 text-sm text-red-600">{errors.subject.message}</p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">
              Description
            </label>
            <textarea
              {...register('description')}
              rows={3}
              className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
            />
          </div>

          {/* Business Value Sub-Values */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Business Value *
            </label>
            <div className="grid grid-cols-3 gap-3 p-4 border border-gray-200 rounded-md bg-gray-50">
              {Object.entries(SUB_VALUE_LABELS).map(([key, label]) => (
                <div key={key}>
                  <label className="block text-xs font-medium text-gray-600 mb-1">
                    {label}
                  </label>
                  <select
                    {...register(`business_value.${key as keyof WSJFSubValues}`, {
                      valueAsNumber: true,
                    })}
                    className="block w-full border border-gray-300 rounded-md shadow-sm py-1 px-2 text-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                  >
                    <option value="">Select</option>
                    {FIBONACCI_VALUES.map((value) => (
                      <option key={value} value={value}>
                        {value}
                      </option>
                    ))}
                  </select>
                </div>
              ))}
            </div>
          </div>

          {/* Time Criticality Sub-Values */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Time Criticality *
            </label>
            <div className="grid grid-cols-3 gap-3 p-4 border border-gray-200 rounded-md bg-gray-50">
              {Object.entries(SUB_VALUE_LABELS).map(([key, label]) => (
                <div key={key}>
                  <label className="block text-xs font-medium text-gray-600 mb-1">
                    {label}
                  </label>
                  <select
                    {...register(`time_criticality.${key as keyof WSJFSubValues}`, {
                      valueAsNumber: true,
                    })}
                    className="block w-full border border-gray-300 rounded-md shadow-sm py-1 px-2 text-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                  >
                    <option value="">Select</option>
                    {FIBONACCI_VALUES.map((value) => (
                      <option key={value} value={value}>
                        {value}
                      </option>
                    ))}
                  </select>
                </div>
              ))}
            </div>
          </div>

          {/* Risk Reduction Sub-Values */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Risk Reduction *
            </label>
            <div className="grid grid-cols-3 gap-3 p-4 border border-gray-200 rounded-md bg-gray-50">
              {Object.entries(SUB_VALUE_LABELS).map(([key, label]) => (
                <div key={key}>
                  <label className="block text-xs font-medium text-gray-600 mb-1">
                    {label}
                  </label>
                  <select
                    {...register(`risk_reduction.${key as keyof WSJFSubValues}`, {
                      valueAsNumber: true,
                    })}
                    className="block w-full border border-gray-300 rounded-md shadow-sm py-1 px-2 text-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                  >
                    <option value="">Select</option>
                    {FIBONACCI_VALUES.map((value) => (
                      <option key={value} value={value}>
                        {value}
                      </option>
                    ))}
                  </select>
                </div>
              ))}
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">
              Job Size *
            </label>
            <select
              {...register('job_size', {
                required: 'Job size is required',
                valueAsNumber: true,
              })}
              className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
            >
              {FIBONACCI_VALUES.map((value) => (
                <option key={value} value={value}>
                  {value}
                </option>
              ))}
            </select>
            {errors.job_size && (
              <p className="mt-1 text-sm text-red-600">{errors.job_size.message}</p>
            )}
          </div>

          <div>
            <ScoreCalculator
              businessValue={businessValue}
              timeCriticality={timeCriticality}
              riskReduction={riskReduction}
              jobSize={jobSize}
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">Status</label>
              <select
                {...register('status')}
                className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
              >
                {Object.values(WSJFStatus).map((status) => (
                  <option key={status} value={status}>
                    {status}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">
                Program Increment *
              </label>
              {availablePIs && availablePIs.length > 0 ? (
                <select
                  {...register('program_increment_id', { required: 'Program increment is required' })}
                  className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                >
                  <option value="">Select a Program Increment</option>
                  {availablePIs.map((pi) => (
                    <option key={pi.id} value={pi.id}>
                      {pi.name} ({pi.item_count} items)
                    </option>
                  ))}
                </select>
              ) : (
                <input
                  {...register('program_increment_id', { required: 'Program increment is required' })}
                  placeholder="No PIs available - create one first"
                  className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                  readOnly
                />
              )}
              {errors.program_increment_id && (
                <p className="mt-1 text-sm text-red-600">{errors.program_increment_id.message}</p>
              )}
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">Owner</label>
              <input
                {...register('owner')}
                className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">Team</label>
              <input
                {...register('team')}
                className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
              />
            </div>
          </div>

          <div className="flex justify-end space-x-3 pt-4">
            <button
              type="button"
              onClick={onCancel}
              className="px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Saving...' : initialData ? 'Update' : 'Create'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};