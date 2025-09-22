export enum WSJFStatus {
  NEW = "New",
  GO = "Go",
  NO_GO = "No Go",
}

export enum PIStatus {
  PLANNING = "Planning",
  ACTIVE = "Active",
  COMPLETED = "Completed",
  CANCELLED = "Cancelled",
}

// Sub-value structure for WSJF components
export interface WSJFSubValues {
  // Product Management & Ownership
  pms_business: FibonacciValue | null;
  pos_business: FibonacciValue | null;
  
  // Business Leadership
  bos_agri_business: FibonacciValue | null;
  bos_cabinet_business: FibonacciValue | null;
  consultants_business: FibonacciValue | null;
  
  // Development Team
  dev_business: FibonacciValue | null;
  dev_technical: FibonacciValue | null;
  
  // AI team
  ia_business: FibonacciValue | null;
  ia_technical: FibonacciValue | null;
  
  // DevOps & Infrastructure
  devops_business: FibonacciValue | null;
  devops_technical: FibonacciValue | null;
  
  // Support & Operations
  support_business: FibonacciValue | null;
}

// Job Size sub-values structure
export interface JobSizeSubValues {
  dev: FibonacciValue | null;
  ia: FibonacciValue | null;
  devops: FibonacciValue | null;
  exploit: FibonacciValue | null;
}

// Sub-value labels for display (grouped by role category)
export const SUB_VALUE_LABELS: Record<keyof WSJFSubValues, string> = {
  // Product Management & Ownership
  pms_business: "PMs Business",
  pos_business: "POs Business", 
  
  // Business Leadership
  bos_agri_business: "Bos Agri Business",
  bos_cabinet_business: "Bos Cabinet Business",
  consultants_business: "Consultants Business",
  
  // Development Team
  dev_business: "Dev Business",
  dev_technical: "Dev Technical",
  
  // AI team
  ia_business: "IA Business",
  ia_technical: "IA Technical", 
  
  // DevOps & Infrastructure
  devops_business: "DevOps Business",
  devops_technical: "DevOps Technical",
  
  // Support & Operations
  support_business: "Support Business"
};

// Job Size sub-value labels
export const JOB_SIZE_LABELS: Record<keyof JobSizeSubValues, string> = {
  dev: "Dev",
  ia: "IA", 
  devops: "DevOps",
  exploit: "Exploit"
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
  job_size: JobSizeSubValues;
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
  job_size?: Partial<JobSizeSubValues>;
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

// Utility function to calculate maximum value from job size sub-values
export function calculateMaxJobSize(jobSizeSubValues: JobSizeSubValues): number {
  const values = Object.values(jobSizeSubValues).filter((v): v is number => v !== null);
  return values.length > 0 ? Math.max(...values) : 0;
}

// Utility function to check if an item has missing WSJF values
export function hasIncompleteValues(item: WSJFItem): boolean {
  const businessMax = calculateMaxValue(item.business_value);
  const timeMax = calculateMaxValue(item.time_criticality);
  const riskMax = calculateMaxValue(item.risk_reduction);
  const jobSizeMax = calculateMaxJobSize(item.job_size);
  
  return businessMax === 0 || timeMax === 0 || riskMax === 0 || jobSizeMax === 0;
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

// Utility function to get display string for job size sub-values
export function getJobSizeDisplay(jobSizeSubValues: JobSizeSubValues): string {
  const nonNullValues = Object.entries(jobSizeSubValues)
    .filter(([_, value]) => value !== null)
    .map(([key, value]) => `${JOB_SIZE_LABELS[key as keyof JobSizeSubValues]}: ${value}`);
  
  if (nonNullValues.length === 0) return "No values set";
  if (nonNullValues.length === 1) return nonNullValues[0];
  
  const maxValue = calculateMaxJobSize(jobSizeSubValues);
  return `Max: ${maxValue} (${nonNullValues.length} values)`;
}

// Utility function to get active teams with sub-values
export function getActiveTeams(item: WSJFItem): string[] {
  const teams: string[] = [];
  
  // Check Dev team (development related fields)
  const hasDevValues = item.business_value.dev_business !== null || 
                      item.business_value.dev_technical !== null ||
                      item.time_criticality.dev_business !== null || 
                      item.time_criticality.dev_technical !== null ||
                      item.risk_reduction.dev_business !== null || 
                      item.risk_reduction.dev_technical !== null ||
                      item.job_size.dev !== null;
  
  if (hasDevValues) teams.push('Dev');
  
  // Check AI team (IA related fields)
  const hasAIValues = item.business_value.ia_business !== null || 
                     item.business_value.ia_technical !== null ||
                     item.time_criticality.ia_business !== null || 
                     item.time_criticality.ia_technical !== null ||
                     item.risk_reduction.ia_business !== null || 
                     item.risk_reduction.ia_technical !== null ||
                     item.job_size.ia !== null;
  
  if (hasAIValues) teams.push('AI');
  
  // Check Ops team (DevOps related fields)
  const hasOpsValues = item.business_value.devops_business !== null || 
                      item.business_value.devops_technical !== null ||
                      item.time_criticality.devops_business !== null || 
                      item.time_criticality.devops_technical !== null ||
                      item.risk_reduction.devops_business !== null || 
                      item.risk_reduction.devops_technical !== null ||
                      item.job_size.devops !== null;
  
  if (hasOpsValues) teams.push('Ops');
  
  // Check Support team (support related fields)
  const hasSupportValues = item.business_value.support_business !== null ||
                          item.time_criticality.support_business !== null ||
                          item.risk_reduction.support_business !== null ||
                          item.job_size.exploit !== null; // exploit is part of support assessment
  
  if (hasSupportValues) teams.push('Support');
  
  return teams;
}