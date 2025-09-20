import { WSJFStatus } from '../types/wsjf';

interface StatusBadgeProps {
  status: WSJFStatus;
}

const statusStyles = {
  [WSJFStatus.NEW]: 'bg-blue-100 text-blue-800',
  [WSJFStatus.IN_PROGRESS]: 'bg-yellow-100 text-yellow-800',
  [WSJFStatus.BLOCKED]: 'bg-red-100 text-red-800',
  [WSJFStatus.COMPLETED]: 'bg-green-100 text-green-800',
  [WSJFStatus.CANCELLED]: 'bg-gray-100 text-gray-800',
};

export const StatusBadge = ({ status }: StatusBadgeProps) => {
  return (
    <span
      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
        statusStyles[status]
      }`}
    >
      {status}
    </span>
  );
};