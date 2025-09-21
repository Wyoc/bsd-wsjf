import { useForm } from 'react-hook-form';
import { WSJFItemCreate, WSJFStatus, WSJFItem, FIBONACCI_VALUES, WSJFSubValues, JobSizeSubValues, ProgramIncrementResponse } from '../types/wsjf';
import { ScoreCalculator } from './ScoreCalculator';
import { X, Users, Target, TrendingUp, Clock, Shield, Zap } from 'lucide-react';

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

  const createEmptyJobSize = (): JobSizeSubValues => ({
    dev: null,
    ia: null,
    devops: null,
    exploit: null,
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
      job_size: createEmptyJobSize(),
      status: WSJFStatus.NEW,
      owner: '',
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
    <div className="fixed inset-0 bg-black bg-opacity-60 overflow-y-auto h-full w-full z-50 backdrop-blur-sm">
      <div className="relative top-8 mx-auto p-6 w-11/12 max-w-7xl shadow-2xl rounded-xl bg-white">
        {/* Header */}
        <div className="flex justify-between items-center mb-8 pb-6 border-b border-gray-200">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-gradient-to-r from-indigo-500 to-purple-600 rounded-lg flex items-center justify-center">
              <Target className="h-6 w-6 text-white" />
            </div>
            <div>
              <h3 className="text-2xl font-bold text-gray-900">
                {initialData ? 'Edit WSJF Item' : 'Create New WSJF Item'}
              </h3>
              <p className="text-sm text-gray-500 mt-1">
                Weighted Shortest Job First prioritization
              </p>
            </div>
          </div>
          <button
            onClick={onCancel}
            className="text-gray-400 hover:text-gray-600 hover:bg-gray-100 p-2 rounded-full transition-colors duration-200"
          >
            <X className="h-6 w-6" />
          </button>
        </div>

        <form onSubmit={handleSubmit(handleFormSubmit)} className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left Section - Basic Information */}
          <div className="lg:col-span-2 space-y-6">
            {/* Basic Info Card */}
            <div className="bg-gray-50 rounded-lg p-6 border border-gray-200">
              <div className="flex items-center space-x-2 mb-4">
                <Target className="h-5 w-5 text-indigo-600" />
                <h4 className="text-lg font-semibold text-gray-900">Basic Information</h4>
              </div>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Subject *
                  </label>
                  <input
                    {...register('subject', { required: 'Subject is required' })}
                    className="block w-full border border-gray-300 rounded-lg shadow-sm py-3 px-4 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-colors duration-200"
                    placeholder="Enter a descriptive subject for this item..."
                  />
                  {errors.subject && (
                    <p className="mt-2 text-sm text-red-600 flex items-center">
                      <span className="w-4 h-4 rounded-full bg-red-100 text-red-600 text-xs flex items-center justify-center mr-2">!</span>
                      {errors.subject.message}
                    </p>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Description
                  </label>
                  <textarea
                    {...register('description')}
                    rows={4}
                    className="block w-full border border-gray-300 rounded-lg shadow-sm py-3 px-4 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-colors duration-200"
                    placeholder="Provide additional details about this item..."
                  />
                </div>
              </div>
            </div>

            {/* Business Value Section */}
            <div className="bg-gradient-to-br from-green-50 to-emerald-50 rounded-lg p-6 border border-green-200">
              <div className="flex items-center space-x-2 mb-4">
                <TrendingUp className="h-5 w-5 text-green-600" />
                <h4 className="text-lg font-semibold text-gray-900">Business Value</h4>
                <span className="text-sm text-gray-500 bg-white px-2 py-1 rounded-full">Economic Impact</span>
              </div>
              <div className="space-y-6">
                {/* Product Management & Ownership */}
              <div>
                <h4 className="text-sm font-semibold text-gray-800 mb-2">Product Management & Ownership</h4>
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-xs font-medium text-gray-600 mb-1">PMs Business</label>
                    <select
                      {...register('business_value.pms_business', { valueAsNumber: true })}
                      className="block w-full bg-white border border-gray-300 rounded-lg shadow-sm py-2 px-3 text-sm focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500 transition-colors duration-200"
                    >
                      <option value="">Select</option>
                      {FIBONACCI_VALUES.map((value) => (
                        <option key={value} value={value}>{value}</option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-gray-600 mb-1">POs Business</label>
                    <select
                      {...register('business_value.pos_business', { valueAsNumber: true })}
                      className="block w-full border border-gray-300 rounded-md shadow-sm py-1 px-2 text-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                    >
                      <option value="">Select</option>
                      {FIBONACCI_VALUES.map((value) => (
                        <option key={value} value={value}>{value}</option>
                      ))}
                    </select>
                  </div>
                </div>
              </div>

              {/* Business Leadership */}
              <div>
                <h4 className="text-sm font-semibold text-gray-800 mb-2">Business Leadership</h4>
                <div className="grid grid-cols-3 gap-3">
                  <div>
                    <label className="block text-xs font-medium text-gray-600 mb-1">Bos Agri Business</label>
                    <select
                      {...register('business_value.bos_agri_business', { valueAsNumber: true })}
                      className="block w-full border border-gray-300 rounded-md shadow-sm py-1 px-2 text-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                    >
                      <option value="">Select</option>
                      {FIBONACCI_VALUES.map((value) => (
                        <option key={value} value={value}>{value}</option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-gray-600 mb-1">Bos Cabinet Business</label>
                    <select
                      {...register('business_value.bos_cabinet_business', { valueAsNumber: true })}
                      className="block w-full border border-gray-300 rounded-md shadow-sm py-1 px-2 text-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                    >
                      <option value="">Select</option>
                      {FIBONACCI_VALUES.map((value) => (
                        <option key={value} value={value}>{value}</option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-gray-600 mb-1">Consultants Business</label>
                    <select
                      {...register('business_value.consultants_business', { valueAsNumber: true })}
                      className="block w-full border border-gray-300 rounded-md shadow-sm py-1 px-2 text-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                    >
                      <option value="">Select</option>
                      {FIBONACCI_VALUES.map((value) => (
                        <option key={value} value={value}>{value}</option>
                      ))}
                    </select>
                  </div>
                </div>
              </div>

              {/* Development Team */}
              <div>
                <h4 className="text-sm font-semibold text-gray-800 mb-2">Development Team</h4>
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-xs font-medium text-gray-600 mb-1">Dev Business</label>
                    <select
                      {...register('business_value.dev_business', { valueAsNumber: true })}
                      className="block w-full border border-gray-300 rounded-md shadow-sm py-1 px-2 text-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                    >
                      <option value="">Select</option>
                      {FIBONACCI_VALUES.map((value) => (
                        <option key={value} value={value}>{value}</option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-gray-600 mb-1">Dev Technical</label>
                    <select
                      {...register('business_value.dev_technical', { valueAsNumber: true })}
                      className="block w-full border border-gray-300 rounded-md shadow-sm py-1 px-2 text-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                    >
                      <option value="">Select</option>
                      {FIBONACCI_VALUES.map((value) => (
                        <option key={value} value={value}>{value}</option>
                      ))}
                    </select>
                  </div>
                </div>
              </div>

              {/* AI team */}
              <div>
                <h4 className="text-sm font-semibold text-gray-800 mb-2">AI team</h4>
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-xs font-medium text-gray-600 mb-1">IA Business</label>
                    <select
                      {...register('business_value.ia_business', { valueAsNumber: true })}
                      className="block w-full border border-gray-300 rounded-md shadow-sm py-1 px-2 text-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                    >
                      <option value="">Select</option>
                      {FIBONACCI_VALUES.map((value) => (
                        <option key={value} value={value}>{value}</option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-gray-600 mb-1">IA Technical</label>
                    <select
                      {...register('business_value.ia_technical', { valueAsNumber: true })}
                      className="block w-full border border-gray-300 rounded-md shadow-sm py-1 px-2 text-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                    >
                      <option value="">Select</option>
                      {FIBONACCI_VALUES.map((value) => (
                        <option key={value} value={value}>{value}</option>
                      ))}
                    </select>
                  </div>
                </div>
              </div>

              {/* DevOps & Infrastructure */}
              <div>
                <h4 className="text-sm font-semibold text-gray-800 mb-2">DevOps & Infrastructure</h4>
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-xs font-medium text-gray-600 mb-1">DevOps Business</label>
                    <select
                      {...register('business_value.devops_business', { valueAsNumber: true })}
                      className="block w-full border border-gray-300 rounded-md shadow-sm py-1 px-2 text-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                    >
                      <option value="">Select</option>
                      {FIBONACCI_VALUES.map((value) => (
                        <option key={value} value={value}>{value}</option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-gray-600 mb-1">DevOps Technical</label>
                    <select
                      {...register('business_value.devops_technical', { valueAsNumber: true })}
                      className="block w-full border border-gray-300 rounded-md shadow-sm py-1 px-2 text-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                    >
                      <option value="">Select</option>
                      {FIBONACCI_VALUES.map((value) => (
                        <option key={value} value={value}>{value}</option>
                      ))}
                    </select>
                  </div>
                </div>
              </div>

              {/* Support & Operations */}
              <div>
                <h4 className="text-sm font-semibold text-gray-800 mb-2">Support & Operations</h4>
                <div className="grid grid-cols-1 gap-3">
                  <div>
                    <label className="block text-xs font-medium text-gray-600 mb-1">Support Business</label>
                    <select
                      {...register('business_value.support_business', { valueAsNumber: true })}
                      className="block w-full border border-gray-300 rounded-md shadow-sm py-1 px-2 text-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                    >
                      <option value="">Select</option>
                      {FIBONACCI_VALUES.map((value) => (
                        <option key={value} value={value}>{value}</option>
                      ))}
                    </select>
                  </div>
                </div>
              </div>
            </div>
          </div>

            {/* Time Criticality Section */}
            <div className="bg-gradient-to-br from-orange-50 to-yellow-50 rounded-lg p-6 border border-orange-200">
              <div className="flex items-center space-x-2 mb-4">
                <Clock className="h-5 w-5 text-orange-600" />
                <h4 className="text-lg font-semibold text-gray-900">Time Criticality</h4>
                <span className="text-sm text-gray-500 bg-white px-2 py-1 rounded-full">Urgency Factor</span>
              </div>
              <div className="space-y-6">
              {/* Product Management & Ownership */}
              <div>
                <h4 className="text-sm font-semibold text-gray-800 mb-2">Product Management & Ownership</h4>
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-xs font-medium text-gray-600 mb-1">PMs Business</label>
                    <select
                      {...register('time_criticality.pms_business', { valueAsNumber: true })}
                      className="block w-full border border-gray-300 rounded-md shadow-sm py-1 px-2 text-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                    >
                      <option value="">Select</option>
                      {FIBONACCI_VALUES.map((value) => (
                        <option key={value} value={value}>{value}</option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-gray-600 mb-1">POs Business</label>
                    <select
                      {...register('time_criticality.pos_business', { valueAsNumber: true })}
                      className="block w-full border border-gray-300 rounded-md shadow-sm py-1 px-2 text-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                    >
                      <option value="">Select</option>
                      {FIBONACCI_VALUES.map((value) => (
                        <option key={value} value={value}>{value}</option>
                      ))}
                    </select>
                  </div>
                </div>
              </div>

              {/* Business Leadership */}
              <div>
                <h4 className="text-sm font-semibold text-gray-800 mb-2">Business Leadership</h4>
                <div className="grid grid-cols-3 gap-3">
                  <div>
                    <label className="block text-xs font-medium text-gray-600 mb-1">Bos Agri Business</label>
                    <select
                      {...register('time_criticality.bos_agri_business', { valueAsNumber: true })}
                      className="block w-full border border-gray-300 rounded-md shadow-sm py-1 px-2 text-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                    >
                      <option value="">Select</option>
                      {FIBONACCI_VALUES.map((value) => (
                        <option key={value} value={value}>{value}</option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-gray-600 mb-1">Bos Cabinet Business</label>
                    <select
                      {...register('time_criticality.bos_cabinet_business', { valueAsNumber: true })}
                      className="block w-full border border-gray-300 rounded-md shadow-sm py-1 px-2 text-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                    >
                      <option value="">Select</option>
                      {FIBONACCI_VALUES.map((value) => (
                        <option key={value} value={value}>{value}</option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-gray-600 mb-1">Consultants Business</label>
                    <select
                      {...register('time_criticality.consultants_business', { valueAsNumber: true })}
                      className="block w-full border border-gray-300 rounded-md shadow-sm py-1 px-2 text-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                    >
                      <option value="">Select</option>
                      {FIBONACCI_VALUES.map((value) => (
                        <option key={value} value={value}>{value}</option>
                      ))}
                    </select>
                  </div>
                </div>
              </div>

              {/* Development Team */}
              <div>
                <h4 className="text-sm font-semibold text-gray-800 mb-2">Development Team</h4>
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-xs font-medium text-gray-600 mb-1">Dev Business</label>
                    <select
                      {...register('time_criticality.dev_business', { valueAsNumber: true })}
                      className="block w-full border border-gray-300 rounded-md shadow-sm py-1 px-2 text-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                    >
                      <option value="">Select</option>
                      {FIBONACCI_VALUES.map((value) => (
                        <option key={value} value={value}>{value}</option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-gray-600 mb-1">Dev Technical</label>
                    <select
                      {...register('time_criticality.dev_technical', { valueAsNumber: true })}
                      className="block w-full border border-gray-300 rounded-md shadow-sm py-1 px-2 text-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                    >
                      <option value="">Select</option>
                      {FIBONACCI_VALUES.map((value) => (
                        <option key={value} value={value}>{value}</option>
                      ))}
                    </select>
                  </div>
                </div>
              </div>

              {/* AI team */}
              <div>
                <h4 className="text-sm font-semibold text-gray-800 mb-2">AI team</h4>
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-xs font-medium text-gray-600 mb-1">IA Business</label>
                    <select
                      {...register('time_criticality.ia_business', { valueAsNumber: true })}
                      className="block w-full border border-gray-300 rounded-md shadow-sm py-1 px-2 text-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                    >
                      <option value="">Select</option>
                      {FIBONACCI_VALUES.map((value) => (
                        <option key={value} value={value}>{value}</option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-gray-600 mb-1">IA Technical</label>
                    <select
                      {...register('time_criticality.ia_technical', { valueAsNumber: true })}
                      className="block w-full border border-gray-300 rounded-md shadow-sm py-1 px-2 text-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                    >
                      <option value="">Select</option>
                      {FIBONACCI_VALUES.map((value) => (
                        <option key={value} value={value}>{value}</option>
                      ))}
                    </select>
                  </div>
                </div>
              </div>

              {/* DevOps & Infrastructure */}
              <div>
                <h4 className="text-sm font-semibold text-gray-800 mb-2">DevOps & Infrastructure</h4>
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-xs font-medium text-gray-600 mb-1">DevOps Business</label>
                    <select
                      {...register('time_criticality.devops_business', { valueAsNumber: true })}
                      className="block w-full border border-gray-300 rounded-md shadow-sm py-1 px-2 text-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                    >
                      <option value="">Select</option>
                      {FIBONACCI_VALUES.map((value) => (
                        <option key={value} value={value}>{value}</option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-gray-600 mb-1">DevOps Technical</label>
                    <select
                      {...register('time_criticality.devops_technical', { valueAsNumber: true })}
                      className="block w-full border border-gray-300 rounded-md shadow-sm py-1 px-2 text-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                    >
                      <option value="">Select</option>
                      {FIBONACCI_VALUES.map((value) => (
                        <option key={value} value={value}>{value}</option>
                      ))}
                    </select>
                  </div>
                </div>
              </div>

              {/* Support & Operations */}
              <div>
                <h4 className="text-sm font-semibold text-gray-800 mb-2">Support & Operations</h4>
                <div className="grid grid-cols-1 gap-3">
                  <div>
                    <label className="block text-xs font-medium text-gray-600 mb-1">Support Business</label>
                    <select
                      {...register('time_criticality.support_business', { valueAsNumber: true })}
                      className="block w-full border border-gray-300 rounded-md shadow-sm py-1 px-2 text-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                    >
                      <option value="">Select</option>
                      {FIBONACCI_VALUES.map((value) => (
                        <option key={value} value={value}>{value}</option>
                      ))}
                    </select>
                  </div>
                </div>
              </div>
            </div>
          </div>

            {/* Risk Reduction Section */}
            <div className="bg-gradient-to-br from-purple-50 to-pink-50 rounded-lg p-6 border border-purple-200">
              <div className="flex items-center space-x-2 mb-4">
                <Shield className="h-5 w-5 text-purple-600" />
                <h4 className="text-lg font-semibold text-gray-900">Risk Reduction</h4>
                <span className="text-sm text-gray-500 bg-white px-2 py-1 rounded-full">Risk Mitigation</span>
              </div>
              <div className="space-y-6">
              {/* Product Management & Ownership */}
              <div>
                <h4 className="text-sm font-semibold text-gray-800 mb-2">Product Management & Ownership</h4>
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-xs font-medium text-gray-600 mb-1">PMs Business</label>
                    <select
                      {...register('risk_reduction.pms_business', { valueAsNumber: true })}
                      className="block w-full border border-gray-300 rounded-md shadow-sm py-1 px-2 text-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                    >
                      <option value="">Select</option>
                      {FIBONACCI_VALUES.map((value) => (
                        <option key={value} value={value}>{value}</option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-gray-600 mb-1">POs Business</label>
                    <select
                      {...register('risk_reduction.pos_business', { valueAsNumber: true })}
                      className="block w-full border border-gray-300 rounded-md shadow-sm py-1 px-2 text-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                    >
                      <option value="">Select</option>
                      {FIBONACCI_VALUES.map((value) => (
                        <option key={value} value={value}>{value}</option>
                      ))}
                    </select>
                  </div>
                </div>
              </div>

              {/* Business Leadership */}
              <div>
                <h4 className="text-sm font-semibold text-gray-800 mb-2">Business Leadership</h4>
                <div className="grid grid-cols-3 gap-3">
                  <div>
                    <label className="block text-xs font-medium text-gray-600 mb-1">Bos Agri Business</label>
                    <select
                      {...register('risk_reduction.bos_agri_business', { valueAsNumber: true })}
                      className="block w-full border border-gray-300 rounded-md shadow-sm py-1 px-2 text-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                    >
                      <option value="">Select</option>
                      {FIBONACCI_VALUES.map((value) => (
                        <option key={value} value={value}>{value}</option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-gray-600 mb-1">Bos Cabinet Business</label>
                    <select
                      {...register('risk_reduction.bos_cabinet_business', { valueAsNumber: true })}
                      className="block w-full border border-gray-300 rounded-md shadow-sm py-1 px-2 text-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                    >
                      <option value="">Select</option>
                      {FIBONACCI_VALUES.map((value) => (
                        <option key={value} value={value}>{value}</option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-gray-600 mb-1">Consultants Business</label>
                    <select
                      {...register('risk_reduction.consultants_business', { valueAsNumber: true })}
                      className="block w-full border border-gray-300 rounded-md shadow-sm py-1 px-2 text-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                    >
                      <option value="">Select</option>
                      {FIBONACCI_VALUES.map((value) => (
                        <option key={value} value={value}>{value}</option>
                      ))}
                    </select>
                  </div>
                </div>
              </div>

              {/* Development Team */}
              <div>
                <h4 className="text-sm font-semibold text-gray-800 mb-2">Development Team</h4>
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-xs font-medium text-gray-600 mb-1">Dev Business</label>
                    <select
                      {...register('risk_reduction.dev_business', { valueAsNumber: true })}
                      className="block w-full border border-gray-300 rounded-md shadow-sm py-1 px-2 text-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                    >
                      <option value="">Select</option>
                      {FIBONACCI_VALUES.map((value) => (
                        <option key={value} value={value}>{value}</option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-gray-600 mb-1">Dev Technical</label>
                    <select
                      {...register('risk_reduction.dev_technical', { valueAsNumber: true })}
                      className="block w-full border border-gray-300 rounded-md shadow-sm py-1 px-2 text-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                    >
                      <option value="">Select</option>
                      {FIBONACCI_VALUES.map((value) => (
                        <option key={value} value={value}>{value}</option>
                      ))}
                    </select>
                  </div>
                </div>
              </div>

              {/* AI team */}
              <div>
                <h4 className="text-sm font-semibold text-gray-800 mb-2">AI team</h4>
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-xs font-medium text-gray-600 mb-1">IA Business</label>
                    <select
                      {...register('risk_reduction.ia_business', { valueAsNumber: true })}
                      className="block w-full border border-gray-300 rounded-md shadow-sm py-1 px-2 text-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                    >
                      <option value="">Select</option>
                      {FIBONACCI_VALUES.map((value) => (
                        <option key={value} value={value}>{value}</option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-gray-600 mb-1">IA Technical</label>
                    <select
                      {...register('risk_reduction.ia_technical', { valueAsNumber: true })}
                      className="block w-full border border-gray-300 rounded-md shadow-sm py-1 px-2 text-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                    >
                      <option value="">Select</option>
                      {FIBONACCI_VALUES.map((value) => (
                        <option key={value} value={value}>{value}</option>
                      ))}
                    </select>
                  </div>
                </div>
              </div>

              {/* DevOps & Infrastructure */}
              <div>
                <h4 className="text-sm font-semibold text-gray-800 mb-2">DevOps & Infrastructure</h4>
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-xs font-medium text-gray-600 mb-1">DevOps Business</label>
                    <select
                      {...register('risk_reduction.devops_business', { valueAsNumber: true })}
                      className="block w-full border border-gray-300 rounded-md shadow-sm py-1 px-2 text-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                    >
                      <option value="">Select</option>
                      {FIBONACCI_VALUES.map((value) => (
                        <option key={value} value={value}>{value}</option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-gray-600 mb-1">DevOps Technical</label>
                    <select
                      {...register('risk_reduction.devops_technical', { valueAsNumber: true })}
                      className="block w-full border border-gray-300 rounded-md shadow-sm py-1 px-2 text-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                    >
                      <option value="">Select</option>
                      {FIBONACCI_VALUES.map((value) => (
                        <option key={value} value={value}>{value}</option>
                      ))}
                    </select>
                  </div>
                </div>
              </div>

              {/* Support & Operations */}
              <div>
                <h4 className="text-sm font-semibold text-gray-800 mb-2">Support & Operations</h4>
                <div className="grid grid-cols-1 gap-3">
                  <div>
                    <label className="block text-xs font-medium text-gray-600 mb-1">Support Business</label>
                    <select
                      {...register('risk_reduction.support_business', { valueAsNumber: true })}
                      className="block w-full border border-gray-300 rounded-md shadow-sm py-1 px-2 text-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                    >
                      <option value="">Select</option>
                      {FIBONACCI_VALUES.map((value) => (
                        <option key={value} value={value}>{value}</option>
                      ))}
                    </select>
                  </div>
                </div>
              </div>
            </div>
          </div>

            {/* Job Size Section */}
            <div className="bg-gradient-to-br from-red-50 to-pink-50 rounded-lg p-6 border border-red-200">
              <div className="flex items-center space-x-2 mb-4">
                <Users className="h-5 w-5 text-red-600" />
                <h4 className="text-lg font-semibold text-gray-900">Job Size</h4>
                <span className="text-sm text-gray-500 bg-white px-2 py-1 rounded-full">Effort Estimation</span>
              </div>
              <div className="space-y-4">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-medium text-gray-600 mb-1">Dev</label>
                  <select
                    {...register('job_size.dev', { valueAsNumber: true })}
                    className="block w-full border border-gray-300 rounded-md shadow-sm py-1 px-2 text-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                  >
                    <option value="">Select</option>
                    {FIBONACCI_VALUES.map((value) => (
                      <option key={value} value={value}>{value}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-600 mb-1">IA</label>
                  <select
                    {...register('job_size.ia', { valueAsNumber: true })}
                    className="block w-full border border-gray-300 rounded-md shadow-sm py-1 px-2 text-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                  >
                    <option value="">Select</option>
                    {FIBONACCI_VALUES.map((value) => (
                      <option key={value} value={value}>{value}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-600 mb-1">DevOps</label>
                  <select
                    {...register('job_size.devops', { valueAsNumber: true })}
                    className="block w-full border border-gray-300 rounded-md shadow-sm py-1 px-2 text-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                  >
                    <option value="">Select</option>
                    {FIBONACCI_VALUES.map((value) => (
                      <option key={value} value={value}>{value}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-600 mb-1">Exploit</label>
                  <select
                    {...register('job_size.exploit', { valueAsNumber: true })}
                    className="block w-full border border-gray-300 rounded-md shadow-sm py-1 px-2 text-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                  >
                    <option value="">Select</option>
                    {FIBONACCI_VALUES.map((value) => (
                      <option key={value} value={value}>{value}</option>
                    ))}
                  </select>
                </div>
              </div>
            </div>
            </div>
          </div>

          {/* Right Sidebar - WSJF Calculator & Actions */}
          <div className="lg:col-span-1 space-y-6">
            {/* WSJF Score Card */}
            <div className="bg-gradient-to-br from-indigo-50 to-blue-50 rounded-lg p-6 border border-indigo-200 sticky top-8">
              <div className="flex items-center space-x-2 mb-4">
                <Zap className="h-5 w-5 text-indigo-600" />
                <h4 className="text-lg font-semibold text-gray-900">WSJF Score</h4>
              </div>
              <ScoreCalculator
                businessValue={businessValue}
                timeCriticality={timeCriticality}
                riskReduction={riskReduction}
                jobSize={jobSize}
              />
            </div>

            {/* Status & Ownership Card */}
            <div className="bg-gray-50 rounded-lg p-6 border border-gray-200">
              <div className="flex items-center space-x-2 mb-4">
                <Users className="h-5 w-5 text-gray-600" />
                <h4 className="text-lg font-semibold text-gray-900">Status & Ownership</h4>
              </div>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Status</label>
                  <select
                    {...register('status')}
                    className="block w-full bg-white border border-gray-300 rounded-lg shadow-sm py-3 px-4 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-colors duration-200"
                  >
                    {Object.values(WSJFStatus).map((status) => (
                      <option key={status} value={status}>
                        {status}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Owner</label>
                  <input
                    {...register('owner')}
                    className="block w-full bg-white border border-gray-300 rounded-lg shadow-sm py-3 px-4 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-colors duration-200"
                    placeholder="Assign an owner..."
                  />
                </div>

                {/* Program Increment Selection */}
                {availablePIs && availablePIs.length > 0 && (
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Program Increment *</label>
                    <select
                      {...register('program_increment_id', { required: 'Program Increment is required' })}
                      className="block w-full bg-white border border-gray-300 rounded-lg shadow-sm py-3 px-4 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-colors duration-200"
                    >
                      <option value="">Select Program Increment</option>
                      {availablePIs.map((pi) => (
                        <option key={pi.id} value={pi.id}>
                          {pi.name} - {pi.status}
                        </option>
                      ))}
                    </select>
                    {errors.program_increment_id && (
                      <p className="mt-2 text-sm text-red-600 flex items-center">
                        <span className="w-4 h-4 rounded-full bg-red-100 text-red-600 text-xs flex items-center justify-center mr-2">!</span>
                        {errors.program_increment_id.message}
                      </p>
                    )}
                  </div>
                )}
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex flex-col space-y-3">
              <button
                type="submit"
                disabled={loading}
                className="w-full bg-gradient-to-r from-indigo-600 to-purple-600 text-white py-3 px-6 rounded-lg font-semibold shadow-lg hover:shadow-xl hover:from-indigo-700 hover:to-purple-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 transform hover:scale-105"
              >
                {loading ? (
                  <div className="flex items-center justify-center space-x-2">
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                    <span>Saving...</span>
                  </div>
                ) : (
                  <div className="flex items-center justify-center space-x-2">
                    <Target className="h-5 w-5" />
                    <span>{initialData ? 'Update Item' : 'Create Item'}</span>
                  </div>
                )}
              </button>
              <button
                type="button"
                onClick={onCancel}
                className="w-full bg-white border border-gray-300 text-gray-700 py-3 px-6 rounded-lg font-semibold shadow-sm hover:bg-gray-50 hover:shadow-md focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-all duration-200"
              >
                Cancel
              </button>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
};