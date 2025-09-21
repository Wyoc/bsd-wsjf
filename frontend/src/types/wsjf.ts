export enum WSJFStatus {
  NEW = "New",
  IN_PROGRESS = "In Progress",
  BLOCKED = "Blocked",
  COMPLETED = "Completed",
  CANCELLED = "Cancelled",
}

export enum PIStatus {
  PLANNING = "Planning",
  ACTIVE = "Active",
  COMPLETED = "Completed",
  CANCELLED = "Cancelled",
}

// Sub-value structure for WSJF components
export interface WSJFSubValues {
  pms_business: FibonacciValue | null;
  pos_business: FibonacciValue | null;
  bos_agri_business: FibonacciValue | null;
  bos_cabinet_business: FibonacciValue | null;
  consultants_business: FibonacciValue | null;
  dev_business: FibonacciValue | null;
  dev_technical: FibonacciValue | null;
  ia_business: FibonacciValue | null;
  ia_technical: FibonacciValue | null;
  devops_business: FibonacciValue | null;
  devops_technical: FibonacciValue | null;
  support_business: FibonacciValue | null;
}

// Sub-value labels for display
export const SUB_VALUE_LABELS: Record<keyof WSJFSubValues, string> = {
  pms_business: "PMs Business",
  pos_business: "POs Business", 
  bos_agri_business: "Bos Agri Business",
  bos_cabinet_business: "Bos Cabinet Business",
  consultants_business: "Consultants Business",
  dev_business: "Dev Business",
  dev_technical: "Dev Technical",
  ia_business: "IA Business",
  ia_technical: "IA Technical", 
  devops_business: "DevOps Business",
  devops_technical: "DevOps Technical",
  support_business: "Support Business"
};

// Keep job_size as Fibonacci values for estimation
export const FIBONACCI_VALUES = [1, 2, 3, 5, 8, 13, 21] as const;
export type FibonacciValue = typeof FIBONACCI_VALUES[number];

export interface WSJFItemBase {
  subject: string;
  description: string;
  business_value: WSJFSubValues;
  time_criticality: WSJFSubValues;
  risk_reduction: WSJFSubValues;
  job_size: FibonacciValue;
  status: WSJFStatus;
  owner?: string;
  team?: string;
  program_increment_id: string;
}

export interface WSJFItemCreate extends WSJFItemBase {}

export interface WSJFItemUpdate {
  subject?: string;
  description?: string;
  business_value?: Partial<WSJFSubValues>;
  time_criticality?: Partial<WSJFSubValues>;
  risk_reduction?: Partial<WSJFSubValues>;
  job_size?: FibonacciValue;
  status?: WSJFStatus;
  owner?: string;
  team?: string;
  program_increment_id?: string;
}

export interface WSJFItem extends WSJFItemBase {
  id: string;
  created_date: string;
  wsjf_score: number;
}

export interface WSJFItemResponse extends WSJFItem {
  priority?: number;
}

export interface WSJFItemBatch {
  items: WSJFItemCreate[];
}

export interface APIError {
  detail: string;
}

export interface APIResponse<T = any> {
  data?: T;
  error?: string;
}

// Program Increment interfaces
export interface ProgramIncrementBase {
  name: string;
  description: string;
  start_date: string;
  end_date: string;
  status: PIStatus;
}

export interface ProgramIncrementCreate extends ProgramIncrementBase {}

export interface ProgramIncrementUpdate {
  name?: string;
  description?: string;
  start_date?: string;
  end_date?: string;
  status?: PIStatus;
}

export interface ProgramIncrement extends ProgramIncrementBase {
  id: string;
  created_date: string;
}

export interface ProgramIncrementResponse extends ProgramIncrement {
  item_count: number;
}

export interface ProgramIncrementStats {
  pi: ProgramIncrement;
  total_items: number;
  avg_wsjf_score: number;
  status_distribution: Record<string, number>;
  team_distribution: Record<string, number>;
}

// Utility function to calculate maximum value from sub-values
export function calculateMaxValue(subValues: WSJFSubValues): number {
  const values = Object.values(subValues).filter((v): v is number => v !== null);
  return values.length > 0 ? Math.max(...values) : 0;
}

// Utility function to get display string for sub-values
export function getSubValuesDisplay(subValues: WSJFSubValues): string {
  const nonNullValues = Object.entries(subValues)
    .filter(([_, value]) => value !== null)
    .map(([key, value]) => `${SUB_VALUE_LABELS[key as keyof WSJFSubValues]}: ${value}`);
  
  if (nonNullValues.length === 0) return "No values set";
  if (nonNullValues.length === 1) return nonNullValues[0];
  
  const maxValue = calculateMaxValue(subValues);
  return `Max: ${maxValue} (${nonNullValues.length} values)`;
}