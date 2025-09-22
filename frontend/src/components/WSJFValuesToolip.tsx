import React from 'react';
import { WSJFItem, calculateMaxValue, calculateMaxJobSize } from '../types/wsjf';
import { Tooltip } from './Tooltip';

interface WSJFValesTooltipProps {
  item: WSJFItem;
  children: React.ReactNode;
}

export const WSJFValuesToolip: React.FC<WSJFValesTooltipProps> = ({ item, children }) => {
  const tooltipContent = (
    <div className="text-left">
      <div className="font-semibold mb-2 text-white">{item.subject}</div>
      <div className="space-y-1 text-sm">
        <div className="grid grid-cols-2 gap-x-4 gap-y-1">
          <span className="text-gray-300">Business Value:</span>
          <span className="font-medium text-white">{calculateMaxValue(item.business_value)}</span>
          
          <span className="text-gray-300">Time Criticality:</span>
          <span className="font-medium text-white">{calculateMaxValue(item.time_criticality)}</span>
          
          <span className="text-gray-300">Risk Reduction:</span>
          <span className="font-medium text-white">{calculateMaxValue(item.risk_reduction)}</span>
          
          <span className="text-gray-300">Job Size:</span>
          <span className="font-medium text-white">{calculateMaxJobSize(item.job_size)}</span>
        </div>
        
        <div className="border-t border-gray-600 pt-2 mt-2">
          <div className="grid grid-cols-2 gap-x-4">
            <span className="text-gray-300">WSJF Score:</span>
            <span className="font-bold text-green-300">{item.wsjf_score.toFixed(2)}</span>
          </div>
        </div>
        
        <div className="text-xs text-gray-400 mt-2">
          Formula: (BV + TC + RR) ÷ JS = ({calculateMaxValue(item.business_value)} + {calculateMaxValue(item.time_criticality)} + {calculateMaxValue(item.risk_reduction)}) ÷ {calculateMaxJobSize(item.job_size)} = {item.wsjf_score.toFixed(2)}
        </div>
      </div>
    </div>
  );

  return (
    <Tooltip content={tooltipContent} position="top" className="cursor-help">
      {children}
    </Tooltip>
  );
};