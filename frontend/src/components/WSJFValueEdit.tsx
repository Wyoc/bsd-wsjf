import React from 'react';
import { InlineEdit } from './InlineEdit';
import { FIBONACCI_VALUES, FibonacciValue } from '../types/wsjf';

interface WSJFValueEditProps {
  value: FibonacciValue;
  onSave: (newValue: FibonacciValue) => void;
  label: string;
}

export const WSJFValueEdit: React.FC<WSJFValueEditProps> = ({ value, onSave, label }) => {
  const fibonacciOptions = FIBONACCI_VALUES.map(val => ({
    value: val,
    label: val.toString()
  }));

  const handleSave = async (newValue: string | number) => {
    const numValue = Number(newValue) as FibonacciValue;
    await onSave(numValue);
  };

  return (
    <div className="text-xs">
      <span className="text-gray-500">{label}: </span>
      <InlineEdit
        value={value}
        onSave={handleSave}
        type="select"
        options={fibonacciOptions}
        className="font-medium"
      />
    </div>
  );
};