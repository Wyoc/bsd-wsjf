import { useState, useEffect } from 'react';
import { WSJFItem, WSJFItemCreate, WSJFItemUpdate, APIError } from '../types/wsjf';
import { apiClient } from '../api/client';
import toast from 'react-hot-toast';

export const useWSJF = () => {
  const [items, setItems] = useState<WSJFItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchItems = async (piId?: string) => {
    try {
      setLoading(true);
      setError(null);
      const data = await apiClient.getItemsByPI(piId);
      const sortedItems = data.sort((a, b) => b.wsjf_score - a.wsjf_score);
      const itemsWithPriority = sortedItems.map((item, index) => ({
        ...item,
        priority: index + 1,
      }));
      setItems(itemsWithPriority);
    } catch (err) {
      const error = err as APIError;
      setError(error.detail);
      toast.error(`Failed to load items: ${error.detail}`);
    } finally {
      setLoading(false);
    }
  };

  const loadItemsByPI = async (piId?: string) => {
    await fetchItems(piId);
  };

  const createItem = async (item: WSJFItemCreate) => {
    try {
      setLoading(true);
      await apiClient.createItem(item);
      toast.success('Item created successfully');
      await fetchItems();
    } catch (err) {
      const error = err as APIError;
      toast.error(`Failed to create item: ${error.detail}`);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const updateItem = async (id: string, item: WSJFItemUpdate) => {
    try {
      setLoading(true);
      await apiClient.updateItem(id, item);
      toast.success('Item updated successfully');
      await fetchItems();
    } catch (err) {
      const error = err as APIError;
      toast.error(`Failed to update item: ${error.detail}`);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const deleteItem = async (id: string) => {
    try {
      setLoading(true);
      await apiClient.deleteItem(id);
      toast.success('Item deleted successfully');
      await fetchItems();
    } catch (err) {
      const error = err as APIError;
      toast.error(`Failed to delete item: ${error.detail}`);
    } finally {
      setLoading(false);
    }
  };

  const exportExcel = async (piId?: string) => {
    try {
      setLoading(true);
      const blob = await apiClient.exportExcelByPI(piId, true);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `wsjf-export-${new Date().toISOString().split('T')[0]}.xlsx`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      toast.success('Excel file downloaded successfully');
    } catch (err) {
      const error = err as APIError;
      toast.error(`Failed to export Excel: ${error.detail}`);
    } finally {
      setLoading(false);
    }
  };

  const loadSampleData = async () => {
    try {
      setLoading(true);
      await apiClient.getSampleData();
      toast.success('Sample data loaded successfully');
      await fetchItems();
    } catch (err) {
      const error = err as APIError;
      toast.error(`Failed to load sample data: ${error.detail}`);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchItems();
  }, []);

  return {
    items,
    loading,
    error,
    createItem,
    updateItem,
    deleteItem,
    exportExcel,
    loadSampleData,
    refetch: fetchItems,
    loadItemsByPI,
  };
};