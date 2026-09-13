import React, { useState } from 'react';
import { MetricsView } from './components/MetricsView';
import { DataHealthView } from './components/DataHealthView';
import { IngestModal } from './components/IngestModal';

export const App: React.FC = () => {
    const [activeTab, setActiveTab] = useState<'metrics' | 'health'>('metrics');
    const [isIngestModalOpen, setIsIngestModalOpen] = useState<boolean>(false);
    const [refreshTrigger, setRefreshTrigger] = useState<number>(0);

    const handleIngestionSuccess = () => {
        // Trigger component re-fetch by updating key state counter
        setRefreshTrigger((prev) => prev + 1);
    };

    return (
        <div>
            {/* Top Header & Navigation */}
            <nav style={{ background: '#333', padding: '10px 20px', color: '#fff', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div style={{ display: 'flex', gap: '20px', alignItems: 'center' }}>
                    <h3 style={{ margin: 0, paddingRight: '20px' }}>Marketing Pipeline Engine</h3>
                    <button
                        onClick={() => setActiveTab('metrics')}
                        style={{ padding: '8px 16px', background: activeTab === 'metrics' ? '#007bff' : '#555', color: '#fff', border: 'none', borderRadius: '4px', cursor: 'pointer' }}
                    >
                        FR-7: Campaign Metrics
                    </button>
                    <button
                        onClick={() => setActiveTab('health')}
                        style={{ padding: '8px 16px', background: activeTab === 'health' ? '#007bff' : '#555', color: '#fff', border: 'none', borderRadius: '4px', cursor: 'pointer' }}
                    >
                        FR-8: Data Health
                    </button>
                </div>

                {/* FR-6 Ingestion Trigger Button */}
                <button
                    onClick={() => setIsIngestModalOpen(true)}
                    style={{ padding: '8px 16px', backgroundColor: '#28a745', color: '#fff', border: 'none', borderRadius: '4px', cursor: 'pointer', fontWeight: 'bold' }}
                >
                    + Ingest New File (FR-6)
                </button>
            </nav>

            {/* Main Content Views */}
            <main key={refreshTrigger}>
                {activeTab === 'metrics' ? <MetricsView /> : <DataHealthView />}
            </main>

            {/* Ingestion Trigger Modal */}
            <IngestModal
                isOpen={isIngestModalOpen}
                onClose={() => setIsIngestModalOpen(false)}
                onSuccess={handleIngestionSuccess}
            />
        </div>
    );
};

export default App;
