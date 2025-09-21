import { Tooltip } from './Tooltip';
import { WSJFSubValues, calculateMaxValue } from '../types/wsjf';

interface ScoreCalculatorProps {
  businessValue: WSJFSubValues;
  timeCriticality: WSJFSubValues;
  riskReduction: WSJFSubValues;
  jobSize: number;
}

export const ScoreCalculator = ({
  businessValue,
  timeCriticality,
  riskReduction,
  jobSize,
}: ScoreCalculatorProps) => {
  const calculateWSJF = () => {
    if (jobSize === 0) return 0;
    const businessScore = calculateMaxValue(businessValue);
    const timeScore = calculateMaxValue(timeCriticality);
    const riskScore = calculateMaxValue(riskReduction);
    return Math.round(((businessScore + timeScore + riskScore) / jobSize) * 100) / 100;
  };

  const score = calculateWSJF();

  const getScoreColor = (score: number) => {
    if (score >= 2.5) return 'text-green-600 font-bold';
    if (score >= 1.5) return 'text-yellow-600 font-semibold';
    return 'text-red-600';
  };

  const businessScore = calculateMaxValue(businessValue);
  const timeScore = calculateMaxValue(timeCriticality);
  const riskScore = calculateMaxValue(riskReduction);

  const tooltipContent = (
    <div className="text-left">
      <div className="font-semibold mb-2 text-white">WSJF Calculation</div>
      <div className="space-y-1 text-sm">
        <div className="grid grid-cols-2 gap-x-4 gap-y-1">
          <span className="text-gray-300">Business Value:</span>
          <span className="font-medium text-white">Max: {businessScore}</span>
          
          <span className="text-gray-300">Time Criticality:</span>
          <span className="font-medium text-white">Max: {timeScore}</span>
          
          <span className="text-gray-300">Risk Reduction:</span>
          <span className="font-medium text-white">Max: {riskScore}</span>
          
          <span className="text-gray-300">Job Size:</span>
          <span className="font-medium text-white">{jobSize}</span>
        </div>
        
        <div className="border-t border-gray-600 pt-2 mt-2">
          <div className="text-xs text-gray-400">
            Formula: (BV + TC + RR) ÷ JS
          </div>
          <div className="text-xs text-gray-400">
            ({businessScore} + {timeScore} + {riskScore}) ÷ {jobSize} = {score.toFixed(2)}
          </div>
        </div>
        
        <div className="text-xs text-gray-400 mt-2">
          <div>Score Guidelines:</div>
          <div className="text-green-300">• &ge; 2.5: High Priority</div>
          <div className="text-yellow-300">• 1.5-2.4: Medium Priority</div>
          <div className="text-red-300">• &lt; 1.5: Low Priority</div>
        </div>
      </div>
    </div>
  );

  return (
    <div className="flex items-center space-x-2">
      <span className="text-sm font-medium text-gray-700">WSJF Score:</span>
      <Tooltip content={tooltipContent} position="top">
        <span className={`text-lg cursor-help ${getScoreColor(score)}`}>
          {score.toFixed(2)}
        </span>
      </Tooltip>
    </div>
  );
};