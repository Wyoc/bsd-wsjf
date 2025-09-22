import { useState, useEffect } from 'react';
import { Toaster } from 'react-hot-toast';
import { Plus, Database, BarChart3, Settings } from 'lucide-react';
import { WSJFTable } from './components/WSJFTable';
import { WSJFForm } from './components/WSJFForm';
import { ExportButton } from './components/ExportButton';
import { SimplePISelector } from './components/SimplePISelector';
import { PIManagementPage } from './components/PIManagementPage';
import { TabNavigation, Tab } from './components/TabNavigation';
import { useWSJF } from './hooks/useWSJF';
import { WSJFItem, WSJFItemCreate, WSJFItemUpdate, ProgramIncrementResponse, PIStatus } from './types/wsjf';
import { apiClient } from './api/client';
import toast from 'react-hot-toast';

function App() {
  const [activeTab, setActiveTab] = useState('wsjf');
  const [showForm, setShowForm] = useState(false);
  const [editingItem, setEditingItem] = useState<WSJFItem | null>(null);
  const [selectedPI, setSelectedPI] = useState<ProgramIncrementResponse | null>(null);
  const [availablePIs, setAvailablePIs] = useState<ProgramIncrementResponse[]>([]);
  const [piLoading, setPiLoading] = useState(true);
  const { items, loading, createItem, updateItem, deleteItem, exportExcel, loadSampleData, loadItemsByPI } = useWSJF();

  const tabs: Tab[] = [
    {
      id: 'wsjf',
      label: 'WSJF Items',
      icon: <BarChart3 className="h-4 w-4" />,
    },
    {
      id: 'pi-management',
      label: 'PI Management',
      icon: <Settings className="h-4 w-4" />,
    },
  ];

  const handleCreateItem = async (data: WSJFItemCreate) => {
    await createItem(data);
    // Refresh PI count after creating item
    loadPIs();
  };

  const handleUpdateItem = async (data: WSJFItemCreate) => {
    if (editingItem) {
      const updateData: WSJFItemUpdate = { ...data };
      await updateItem(editingItem.id, updateData);
    }
  };

  const handleEdit = (item: WSJFItem) => {
    setEditingItem(item);
    setShowForm(true);
  };

  const handleDelete = async (id: string) => {
    if (window.confirm('Are you sure you want to delete this item?')) {
      await deleteItem(id);
      // Refresh PI count after deleting item
      loadPIs();
    }
  };

  const handleCloseForm = () => {
    setShowForm(false);
    setEditingItem(null);
  };

  const loadPIs = async () => {
    try {
      setPiLoading(true);
      const pis = await apiClient.getPIs();
      setAvailablePIs(pis);
      
      // Auto-select the next PI in Planning status if no PI is selected
      if (!selectedPI) {
        const planningPIs = pis.filter(pi => pi.status === PIStatus.PLANNING);
        if (planningPIs.length > 0) {
          // Sort by start date and select the next one
          const sortedPlanningPIs = planningPIs.sort((a, b) => 
            new Date(a.start_date).getTime() - new Date(b.start_date).getTime()
          );
          const nextPlanningPI = sortedPlanningPIs[0];
          handlePISelect(nextPlanningPI);
          toast.success(`Auto-loaded next Planning PI: ${nextPlanningPI.name}`);
        }
      }
    } catch (error) {
      console.error('Failed to load PIs:', error);
      toast.error('Failed to load Program Increments');
    } finally {
      setPiLoading(false);
    }
  };

  const handlePISelect = (pi: ProgramIncrementResponse | null) => {
    setSelectedPI(pi);
    loadItemsByPI(pi?.id);
  };

  const handlePICreated = () => {
    loadPIs();
  };

  const handleExport = () => {
    exportExcel(selectedPI?.id);
  };

  const handleTabChange = (tabId: string) => {
    setActiveTab(tabId);
  };

  useEffect(() => {
    loadPIs();
  }, []);

  const renderContent = () => {
    switch (activeTab) {
      case 'wsjf':
        return (
          <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
            <div className="px-4 py-6 sm:px-0">
              {/* Header Actions */}
              <div className="flex justify-between items-center mb-6">
                <div>
                  <h2 className="text-2xl font-bold text-gray-900">WSJF Items</h2>
                  <p className="mt-1 text-sm text-gray-600">
                    Manage Weighted Shortest Job First prioritization items
                  </p>
                </div>
                
                <div className="flex space-x-3">
                  <button
                    onClick={loadSampleData}
                    disabled={loading || !selectedPI}
                    className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
                    title={!selectedPI ? "Select a Program Increment first" : "Load sample data"}
                  >
                    <Database className="h-4 w-4 mr-2" />
                    Load Sample Data
                  </button>
                  
                  <ExportButton 
                    onExport={handleExport} 
                    loading={loading} 
                    disabled={!selectedPI}
                  />
                  
                  <button
                    onClick={() => setShowForm(true)}
                    disabled={!selectedPI}
                    className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
                    title={!selectedPI ? "Select a Program Increment first" : "Create new WSJF item"}
                  >
                    <Plus className="h-4 w-4 mr-2" />
                    New Item
                  </button>
                </div>
              </div>

              {/* PI Selection */}
              <SimplePISelector
                pis={availablePIs}
                selectedPI={selectedPI}
                onPISelect={handlePISelect}
                loading={piLoading}
              />

              {/* Content Area */}
              {selectedPI ? (
                <div>
                  <div className="mb-4 p-3 bg-blue-50 border border-blue-200 rounded-md">
                    <div className="flex items-center justify-between">
                      <div>
                        <h3 className="text-lg font-medium text-blue-800">
                          Items for {selectedPI.name}
                        </h3>
                        <p className="text-sm text-blue-600">
                          {items.length} items loaded
                        </p>
                      </div>

                      {/* Filters will be added here by WSJFTable */}
                      <div id="wsjf-filters-container"></div>
                    </div>
                  </div>
                  <WSJFTable
                    items={items}
                    onEdit={handleEdit}
                    onDelete={handleDelete}
                    onUpdate={updateItem}
                    loading={loading}
                  />
                </div>
              ) : (
                <div className="bg-white rounded-lg shadow-md p-8 text-center">
                  <BarChart3 className="mx-auto h-12 w-12 text-gray-400 mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">
                    {availablePIs.length === 0 ? 'No Program Increments Found' : 'Select a Program Increment'}
                  </h3>
                  <p className="text-gray-600">
                    {availablePIs.length === 0 
                      ? 'Create a Program Increment in the PI Management tab to get started.'
                      : 'Choose a Program Increment above to view and manage WSJF items.'
                    }
                  </p>
                  {availablePIs.length === 0 && (
                    <button
                      onClick={() => setActiveTab('pi-management')}
                      className="mt-4 inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
                    >
                      Go to PI Management
                    </button>
                  )}
                </div>
              )}
            </div>
          </div>
        );
      
      case 'pi-management':
        return <PIManagementPage onPICreated={handlePICreated} />;
      
      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Toaster position="top-right" />
      
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                WSJF Excel Generator
              </h1>
              <p className="mt-2 text-sm text-gray-600">
                Weighted Shortest Job First prioritization tool
              </p>
            </div>
          </div>
        </div>
      </header>

      {/* Tab Navigation */}
      <TabNavigation
        tabs={tabs}
        activeTab={activeTab}
        onTabChange={handleTabChange}
      />

      {/* Main Content */}
      <main>
        {renderContent()}
      </main>

      {/* Modals */}
      {showForm && (
        <WSJFForm
          onSubmit={editingItem ? handleUpdateItem : handleCreateItem}
          onCancel={handleCloseForm}
          initialData={editingItem || undefined}
          loading={loading}
          selectedPI={selectedPI}
          availablePIs={availablePIs}
        />
      )}
    </div>
  );
}

export default App