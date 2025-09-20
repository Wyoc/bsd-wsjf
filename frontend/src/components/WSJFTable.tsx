import { useState } from 'react';
import { WSJFItem, WSJFItemUpdate, FibonacciValue } from '../types/wsjf';
import { StatusBadge } from './StatusBadge';
import { InlineEdit } from './InlineEdit';
import { WSJFValueEdit } from './WSJFValueEdit';
import { Edit, Trash2, ArrowUpDown } from 'lucide-react';

interface WSJFTableProps {
  items: WSJFItem[];
  onEdit: (item: WSJFItem) => void;
  onDelete: (id: string) => void;
  onUpdate: (id: string, updates: WSJFItemUpdate) => Promise<void>;
  loading: boolean;
}

type SortField = keyof WSJFItem | 'priority';
type SortDirection = 'asc' | 'desc';

export const WSJFTable = ({ items, onEdit, onDelete, onUpdate, loading }: WSJFTableProps) => {
  const [sortField, setSortField] = useState<SortField>('priority');
  const [sortDirection, setSortDirection] = useState<SortDirection>('asc');

  const handleSort = (field: SortField) => {
    if (field === sortField) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('asc');
    }
  };

  const sortedItems = [...items].sort((a, b) => {
    let aValue: any;
    let bValue: any;

    if (sortField === 'priority') {
      aValue = a.wsjf_score;
      bValue = b.wsjf_score;
      // For priority, higher WSJF score = lower priority number, so reverse the logic
      const result = bValue - aValue;
      return sortDirection === 'asc' ? result : -result;
    } else {
      aValue = a[sortField];
      bValue = b[sortField];
    }

    if (typeof aValue === 'string' && typeof bValue === 'string') {
      const result = aValue.localeCompare(bValue);
      return sortDirection === 'asc' ? result : -result;
    }

    if (typeof aValue === 'number' && typeof bValue === 'number') {
      const result = aValue - bValue;
      return sortDirection === 'asc' ? result : -result;
    }

    return 0;
  });

  const handleFieldUpdate = async (itemId: string, field: keyof WSJFItemUpdate, value: any) => {
    await onUpdate(itemId, { [field]: value });
  };

  const SortButton = ({ field, children }: { field: SortField; children: React.ReactNode }) => (
    <button
      onClick={() => handleSort(field)}
      className="flex items-center space-x-1 hover:text-gray-600"
    >
      <span>{children}</span>
      <ArrowUpDown className="h-3 w-3" />
    </button>
  );

  if (loading && items.length === 0) {
    return (
      <div className="flex justify-center items-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  if (items.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">No WSJF items found. Create your first item to get started.</p>
      </div>
    );
  }

  return (
    <div className="bg-white shadow overflow-hidden sm:rounded-md">
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                <SortButton field="priority">Priority</SortButton>
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                <SortButton field="subject">Subject</SortButton>
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                <SortButton field="wsjf_score">WSJF Score</SortButton>
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Values
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                <SortButton field="status">Status</SortButton>
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                <SortButton field="owner">Owner</SortButton>
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                <SortButton field="team">Team</SortButton>
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                <SortButton field="program_increment">PI</SortButton>
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {sortedItems.map((item, index) => (
              <tr
                key={item.id}
                className={`hover:bg-gray-50 ${
                  item.wsjf_score >= 2.5 ? 'bg-yellow-50' : ''
                }`}
              >
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                  {index + 1}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm font-medium text-gray-900">{item.subject}</div>
                  {item.description && (
                    <div className="text-sm text-gray-500 truncate max-w-xs">
                      {item.description}
                    </div>
                  )}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  <span
                    className={`font-semibold ${
                      item.wsjf_score >= 2.5
                        ? 'text-green-600'
                        : item.wsjf_score >= 1.5
                        ? 'text-yellow-600'
                        : 'text-red-600'
                    }`}
                  >
                    {item.wsjf_score.toFixed(2)}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  <div className="grid grid-cols-2 gap-1">
                    <WSJFValueEdit
                      value={item.business_value}
                      onSave={(value) => handleFieldUpdate(item.id, 'business_value', value)}
                      label="BV"
                    />
                    <WSJFValueEdit
                      value={item.time_criticality}
                      onSave={(value) => handleFieldUpdate(item.id, 'time_criticality', value)}
                      label="TC"
                    />
                    <WSJFValueEdit
                      value={item.risk_reduction}
                      onSave={(value) => handleFieldUpdate(item.id, 'risk_reduction', value)}
                      label="RR"
                    />
                    <WSJFValueEdit
                      value={item.job_size}
                      onSave={(value) => handleFieldUpdate(item.id, 'job_size', value)}
                      label="JS"
                    />
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <StatusBadge status={item.status} />
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  <InlineEdit
                    value={item.owner || ''}
                    onSave={(value) => handleFieldUpdate(item.id, 'owner', value.toString())}
                    placeholder="Add owner"
                  />
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  <InlineEdit
                    value={item.team || ''}
                    onSave={(value) => handleFieldUpdate(item.id, 'team', value.toString())}
                    placeholder="Add team"
                  />
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {item.program_increment}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                  <div className="flex space-x-2">
                    <button
                      onClick={() => onEdit(item)}
                      className="text-indigo-600 hover:text-indigo-900"
                      title="Edit item"
                    >
                      <Edit className="h-4 w-4" />
                    </button>
                    <button
                      onClick={() => onDelete(item.id)}
                      className="text-red-600 hover:text-red-900"
                      title="Delete item"
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};