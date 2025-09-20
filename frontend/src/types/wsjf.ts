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

export const FIBONACCI_VALUES = [1, 2, 3, 5, 8, 13, 21] as const;
export type FibonacciValue = typeof FIBONACCI_VALUES[number];

export interface WSJFItemBase {
  subject: string;
  description: string;
  business_value: FibonacciValue;
  time_criticality: FibonacciValue;
  risk_reduction: FibonacciValue;
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
  business_value?: FibonacciValue;
  time_criticality?: FibonacciValue;
  risk_reduction?: FibonacciValue;
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