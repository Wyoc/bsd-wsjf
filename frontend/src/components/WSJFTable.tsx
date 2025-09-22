import { useState, useEffect, useRef } from 'react';
import { WSJFItem, WSJFItemUpdate, WSJFStatus, getSubValuesDisplay, getJobSizeDisplay, hasIncompleteValues, getActiveTeams } from '../types/wsjf';
import { InlineEdit } from './InlineEdit';
import { Edit, Trash2, ArrowUpDown } from 'lucide-react';

interface StatusCellProps {
  status: WSJFStatus;
  onStatusChange: (newStatus: WSJFStatus) => Promise<void>;
}

const StatusCell = ({ status, onStatusChange }: StatusCellProps) => {
  const [isEditing, setIsEditing] = useState(false);
  const selectRef = useRef<HTMLSelectElement>(null);
  const statusOptions = [
    { value: WSJFStatus.NEW, label: WSJFStatus.NEW },
    { value: WSJFStatus.GO, label: WSJFStatus.GO },
    { value: WSJFStatus.NO_GO, label: WSJFStatus.NO_GO },
  ];

  const getStatusStyle = (status: WSJFStatus) => {
    switch (status) {
      case WSJFStatus.GO:
        return 'bg-green-100 text-green-800';
      case WSJFStatus.NO_GO:
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const handleStatusChange = async (newStatus: string) => {
    setIsEditing(false);
    if (newStatus !== status) {
      await onStatusChange(newStatus as WSJFStatus);
    }
  };

  const handleMouseEnter = () => {
    setIsEditing(true);
  };

  const handleMouseLeave = () => {
    // Small delay to allow click on options to register
    setTimeout(() => {
      setIsEditing(false);
    }, 150);
  };

  const handleBlur = () => {
    // Small delay to allow click on options to register
    setTimeout(() => {
      setIsEditing(false);
    }, 150);
  };

  useEffect(() => {
    if (isEditing && selectRef.current) {
      // Focus and programmatically open the dropdown
      selectRef.current.focus();
      // Small delay to ensure the element is rendered
      setTimeout(() => {
        if (selectRef.current) {
          const event = new MouseEvent('mousedown', {
            view: window,
            bubbles: true,
            cancelable: true,
          });
          selectRef.current.dispatchEvent(event);
        }
      }, 10);
    }
  }, [isEditing]);

  if (isEditing) {
    return (
      <select
        ref={selectRef}
        value={status}
        onChange={(e) => handleStatusChange(e.target.value)}
        onBlur={handleBlur}
        onMouseLeave={handleMouseLeave}
        className="text-xs font-medium px-2.5 py-0.5 rounded-full border-none focus:outline-none focus:ring-2 focus:ring-blue-500 w-16 min-w-16"
      >
        {statusOptions.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
    );
  }

  return (
    <div
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
      className={`inline-flex items-center justify-center px-2.5 py-0.5 rounded-full text-xs font-medium cursor-pointer hover:opacity-80 w-16 min-w-16 ${getStatusStyle(status)}`}
      title="Hover to change status"
    >
      {status}
    </div>
  );
};

interface TeamBadgesProps {
  item: WSJFItem;
}

const TeamBadges = ({ item }: TeamBadgesProps) => {
  const activeTeams = getActiveTeams(item);
  
  if (activeTeams.length === 0) {
    return <span className="text-gray-400 text-xs">No teams</span>;
  }
  
  const getBadgeStyle = (team: string) => {
    switch (team) {
      case 'Dev':
        return 'bg-blue-100 text-blue-800';
      case 'AI':
        return 'bg-purple-100 text-purple-800';
      case 'Ops':
        return 'bg-green-100 text-green-800';
      case 'Support':
        return 'bg-yellow-100 text-yellow-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };
  
  return (
    <div className="flex flex-wrap gap-1">
      {activeTeams.map((team) => (
        <span
          key={team}
          className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${getBadgeStyle(team)}`}
        >
          {team}
        </span>
      ))}
    </div>
  );
};

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
  const [selectedTeams, setSelectedTeams] = useState<string[]>([]);
  const [selectedStatuses, setSelectedStatuses] = useState<WSJFStatus[]>([]);

  const handleSort = (field: SortField) => {
    if (field === sortField) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('asc');
    }
  };

  // Get all unique teams from items
  const allTeams = [...new Set(items.flatMap(item => getActiveTeams(item)))].sort();

  // Get all unique statuses from items
  const allStatuses = [...new Set(items.map(item => item.status))].sort();

  // Filter items by selected teams and statuses
  const filteredItems = items.filter(item => {
    const teamMatch = selectedTeams.length === 0 || selectedTeams.some(selectedTeam =>
      getActiveTeams(item).includes(selectedTeam)
    );
    const statusMatch = selectedStatuses.length === 0 || selectedStatuses.includes(item.status);
    return teamMatch && statusMatch;
  });

  const sortedItems = [...filteredItems].sort((a, b) => {
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
      {/* Filter Controls */}
      <div className="px-6 py-3 border-b border-gray-200 bg-gray-50">
        <div className="space-y-3">
          <div className="flex items-center space-x-4">
            <span className="text-sm font-medium text-gray-700">Filter by Teams:</span>
            <div className="flex flex-wrap gap-2">
              {allTeams.map((team) => (
                <label key={team} className="inline-flex items-center">
                  <input
                    type="checkbox"
                    className="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
                    checked={selectedTeams.includes(team)}
                    onChange={(e) => {
                      if (e.target.checked) {
                        setSelectedTeams([...selectedTeams, team]);
                      } else {
                        setSelectedTeams(selectedTeams.filter(t => t !== team));
                      }
                    }}
                  />
                  <span className="ml-2 text-sm text-gray-700">{team}</span>
                </label>
              ))}
            </div>
          </div>
          <div className="flex items-center space-x-4">
            <span className="text-sm font-medium text-gray-700">Filter by Status:</span>
            <div className="flex flex-wrap gap-2">
              {allStatuses.map((status) => (
                <label key={status} className="inline-flex items-center">
                  <input
                    type="checkbox"
                    className="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
                    checked={selectedStatuses.includes(status)}
                    onChange={(e) => {
                      if (e.target.checked) {
                        setSelectedStatuses([...selectedStatuses, status]);
                      } else {
                        setSelectedStatuses(selectedStatuses.filter(s => s !== status));
                      }
                    }}
                  />
                  <span className="ml-2 text-sm text-gray-700">{status}</span>
                </label>
              ))}
            </div>
          </div>
          {(selectedTeams.length > 0 || selectedStatuses.length > 0) && (
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <span className="text-sm text-gray-500">
                  Showing {sortedItems.length} of {items.length} items
                </span>
                {selectedTeams.length > 0 && (
                  <span className="text-sm text-gray-500">
                    (teams: {selectedTeams.join(', ')})
                  </span>
                )}
                {selectedStatuses.length > 0 && (
                  <span className="text-sm text-gray-500">
                    (status: {selectedStatuses.join(', ')})
                  </span>
                )}
              </div>
              <button
                onClick={() => {
                  setSelectedTeams([]);
                  setSelectedStatuses([]);
                }}
                className="text-sm text-indigo-600 hover:text-indigo-500"
              >
                Clear all filters
              </button>
            </div>
          )}
        </div>
      </div>
      
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
                Actions
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {sortedItems.map((item, index) => {
              const isIncomplete = hasIncompleteValues(item);
              
              const getRowHighlight = () => {
                if (isIncomplete) {
                  return 'bg-orange-50 border-l-4 border-orange-300';
                }
                
                if (item.status === WSJFStatus.GO) {
                  return 'bg-green-50';
                } else if (item.status === WSJFStatus.NO_GO) {
                  return 'bg-red-50';
                }
                
                return '';
              };
              
              return (
              <tr
                key={item.id}
                className={getRowHighlight()}
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
                  <div className="space-y-1">
                    <div className="flex justify-between items-center">
                      <span className="text-xs font-medium text-blue-600">BV:</span>
                      <span className="text-xs">{getSubValuesDisplay(item.business_value)}</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-xs font-medium text-green-600">TC:</span>
                      <span className="text-xs">{getSubValuesDisplay(item.time_criticality)}</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-xs font-medium text-purple-600">RR:</span>
                      <span className="text-xs">{getSubValuesDisplay(item.risk_reduction)}</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-xs font-medium text-gray-600">JS:</span>
                      <span className="text-xs">{getJobSizeDisplay(item.job_size)}</span>
                    </div>
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <StatusCell 
                    status={item.status}
                    onStatusChange={(newStatus) => handleFieldUpdate(item.id, 'status', newStatus)}
                  />
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  <InlineEdit
                    value={item.owner || ''}
                    onSave={(value) => handleFieldUpdate(item.id, 'owner', value.toString())}
                    placeholder="Add owner"
                  />
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  <TeamBadges item={item} />
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
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
};