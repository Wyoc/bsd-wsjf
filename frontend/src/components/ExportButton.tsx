import { Download } from 'lucide-react';

interface ExportButtonProps {
  onExport: () => void;
  loading: boolean;
  disabled?: boolean;
}

export const ExportButton = ({ onExport, loading, disabled = false }: ExportButtonProps) => {
  const isDisabled = loading || disabled;
  
  return (
    <button
      onClick={onExport}
      disabled={isDisabled}
      className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
      title={disabled ? "Select a Program Increment first" : undefined}
    >
      <Download className="h-4 w-4 mr-2" />
      {loading ? 'Exporting...' : 'Export Excel'}
    </button>
  );
};