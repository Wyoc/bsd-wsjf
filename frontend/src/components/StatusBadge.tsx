import { WSJFStatus } from '../types/wsjf';

interface StatusBadgeProps {
  status: WSJFStatus;
}

const statusStyles = {
  [WSJFStatus.NEW]: 'bg-gray-100 text-gray-800',
  [WSJFStatus.GO]: 'bg-green-100 text-green-800',
  [WSJFStatus.NO_GO]: 'bg-red-100 text-red-800',
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