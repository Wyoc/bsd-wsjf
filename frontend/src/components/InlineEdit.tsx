import React, { useState, useEffect, useRef } from 'react';
import { Check, X, Edit3 } from 'lucide-react';

interface InlineEditProps {
  value: string | number;
  onSave: (newValue: string | number) => void;
  type?: 'text' | 'select';
  options?: Array<{ value: string | number; label: string }>;
  placeholder?: string;
  className?: string;
  displayFormatter?: (value: string | number) => string;
}

export const InlineEdit: React.FC<InlineEditProps> = ({
  value,
  onSave,
  type = 'text',
  options = [],
  placeholder = '',
  className = '',
  displayFormatter,
}) => {
  const [isEditing, setIsEditing] = useState(false);
  const [editValue, setEditValue] = useState(value);
  const [isLoading, setIsLoading] = useState(false);
  const inputRef = useRef<HTMLInputElement | HTMLSelectElement>(null);

  useEffect(() => {
    if (isEditing && inputRef.current) {
      inputRef.current.focus();
      if (inputRef.current instanceof HTMLInputElement) {
        inputRef.current.select();
      }
    }
  }, [isEditing]);

  const handleSave = async () => {
    if (editValue === value) {
      setIsEditing(false);
      return;
    }

    setIsLoading(true);
    try {
      await onSave(editValue);
      setIsEditing(false);
    } catch (error) {
      // Reset to original value on error
      setEditValue(value);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCancel = () => {
    setEditValue(value);
    setIsEditing(false);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      handleSave();
    } else if (e.key === 'Escape') {
      e.preventDefault();
      handleCancel();
    }
  };

  const displayValue = displayFormatter ? displayFormatter(value) : value.toString();
  const isEmpty = !value || value.toString().trim() === '';

  if (isEditing) {
    return (
      <div className="flex items-center space-x-1">
        {type === 'select' ? (
          <select
            ref={inputRef as React.RefObject<HTMLSelectElement>}
            value={editValue}
            onChange={(e) => setEditValue(e.target.value)}
            onKeyDown={handleKeyDown}
            className="min-w-0 flex-1 px-2 py-1 text-sm border border-blue-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
            disabled={isLoading}
          >
            {options.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        ) : (
          <input
            ref={inputRef as React.RefObject<HTMLInputElement>}
            type="text"
            value={editValue}
            onChange={(e) => setEditValue(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={placeholder}
            className="min-w-0 flex-1 px-2 py-1 text-sm border border-blue-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
            disabled={isLoading}
          />
        )}
        
        <button
          onClick={handleSave}
          disabled={isLoading}
          className="p-1 text-green-600 hover:text-green-800 disabled:opacity-50"
          title="Save"
        >
          <Check className="h-4 w-4" />
        </button>
        
        <button
          onClick={handleCancel}
          disabled={isLoading}
          className="p-1 text-red-600 hover:text-red-800 disabled:opacity-50"
          title="Cancel"
        >
          <X className="h-4 w-4" />
        </button>
      </div>
    );
  }

  return (
    <div
      onClick={() => setIsEditing(true)}
      className={`group cursor-pointer inline-flex items-center space-x-1 hover:bg-gray-50 px-1 py-1 rounded ${className}`}
      title="Click to edit"
    >
      <span className={isEmpty ? 'text-gray-400 italic' : ''}>
        {isEmpty ? placeholder || 'Click to add' : displayValue}
      </span>
      <Edit3 className="h-3 w-3 opacity-0 group-hover:opacity-50 transition-opacity" />
    </div>
  );
};