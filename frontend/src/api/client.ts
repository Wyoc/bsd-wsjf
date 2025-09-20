import axios, { AxiosInstance, AxiosResponse } from 'axios';
import { 
  WSJFItem, 
  WSJFItemCreate, 
  WSJFItemUpdate, 
  WSJFItemBatch, 
  APIError,
  ProgramIncrement,
  ProgramIncrementCreate,
  ProgramIncrementUpdate,
  ProgramIncrementResponse,
  ProgramIncrementStats
} from '../types/wsjf';

class APIClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    this.client.interceptors.response.use(
      (response: AxiosResponse) => response,
      (error) => {
        const apiError: APIError = {
          detail: error.response?.data?.detail || error.message || 'An unexpected error occurred',
        };
        return Promise.reject(apiError);
      }
    );
  }

  async getItems(): Promise<WSJFItem[]> {
    const response = await this.client.get<WSJFItem[]>('/api/items');
    return response.data;
  }

  async createItem(item: WSJFItemCreate): Promise<WSJFItem> {
    const response = await this.client.post<WSJFItem>('/api/items', item);
    return response.data;
  }

  async updateItem(id: string, item: WSJFItemUpdate): Promise<WSJFItem> {
    const response = await this.client.put<WSJFItem>(`/api/items/${id}`, item);
    return response.data;
  }

  async deleteItem(id: string): Promise<void> {
    await this.client.delete(`/api/items/${id}`);
  }

  async createItemBatch(batch: WSJFItemBatch): Promise<WSJFItem[]> {
    const response = await this.client.post<WSJFItem[]>('/api/items/batch', batch);
    return response.data;
  }

  async exportExcel(): Promise<Blob> {
    const response = await this.client.get('/api/export/excel', {
      responseType: 'blob',
    });
    return response.data;
  }

  async getSampleData(): Promise<WSJFItem[]> {
    const response = await this.client.get<WSJFItem[]>('/api/sample-data');
    return response.data;
  }

  // Program Increment methods
  async getPIs(): Promise<ProgramIncrementResponse[]> {
    const response = await this.client.get<ProgramIncrementResponse[]>('/api/pis/');
    return response.data;
  }

  async createPI(pi: ProgramIncrementCreate): Promise<ProgramIncrement> {
    const response = await this.client.post<ProgramIncrement>('/api/pis/', pi);
    return response.data;
  }

  async getPI(id: string): Promise<ProgramIncrement> {
    const response = await this.client.get<ProgramIncrement>(`/api/pis/${id}`);
    return response.data;
  }

  async getPIByName(name: string): Promise<ProgramIncrement> {
    const response = await this.client.get<ProgramIncrement>(`/api/pis/name/${name}`);
    return response.data;
  }

  async updatePI(id: string, pi: ProgramIncrementUpdate): Promise<ProgramIncrement> {
    const response = await this.client.put<ProgramIncrement>(`/api/pis/${id}`, pi);
    return response.data;
  }

  async deletePI(id: string): Promise<void> {
    await this.client.delete(`/api/pis/${id}`);
  }

  async getPIStats(id: string): Promise<ProgramIncrementStats> {
    const response = await this.client.get<ProgramIncrementStats>(`/api/pis/${id}/stats`);
    return response.data;
  }

  // Enhanced WSJF methods with PI filtering
  async getItemsByPI(piId?: string): Promise<WSJFItem[]> {
    const url = piId ? `/api/items?program_increment_id=${piId}` : '/api/items';
    const response = await this.client.get<WSJFItem[]>(url);
    return response.data;
  }

  async exportExcelByPI(piId?: string, download: boolean = false): Promise<Blob> {
    const params = new URLSearchParams();
    if (piId) params.append('program_increment_id', piId);
    if (download) params.append('download', 'true');
    
    const response = await this.client.get(`/api/export/excel?${params.toString()}`, {
      responseType: 'blob',
    });
    return response.data;
  }
}

export const apiClient = new APIClient();