import React, { useEffect, useState } from 'react';

interface IngestModalProps {
    isOpen: boolean;
    onClose: () => void;
    onSuccess: () => void;
}

interface SourceFile {
    filename: string;
    filepath: string;
    format: string;
    size_bytes: number;
}

const PRESET_CONFIGS = {
    meta_csv: {
        delivery_id: 'meta_ads_2026-06-01',
        filepath: 'data/deliveries/meta_ads_2026-06-01.csv',
        file_format: 'csv',
        config: {
            platform: { default: 'Meta' },
            campaign: { source: 0 },
            date: { source: 1, transform: 'parse_us_date' },
            spend_usd: { source: 2, transform: 'float' },
            impressions: { source: 3, transform: 'int' },
            clicks: { source: 4, transform: 'int' },
        },
    },
    linkedin_json: {
        delivery_id: 'linkedin_abm_2026-06-01',
        filepath: 'data/deliveries/linkedin_abm_2026-06-01.json',
        file_format: 'json',
        config: {
            platform: { default: 'LinkedIn' },
            campaign: { source: 'campaign' },
            date: { source: 'date_ts', transform: 'parse_epoch_ms' },
            spend_usd: { source: 'spend', transform: 'parse_nested_spend', dependencies: ['spend'] },
            impressions: { source: 'impressions', transform: 'int' },
            clicks: { source: 'clicks', transform: 'int' },
        },
    },
    google_ads: {
        delivery_id: 'google_ads_2026-06-01',
        filepath: 'data/deliveries/google_ads_2026-06-01.csv',
        file_format: 'csv',
        config: {
            platform: { default: 'Google' },
            campaign: { source: 0 },
            date: { source: 1 },
            spend_usd: { source: 2, transform: 'parse_micros', dependencies: [3] },
            impressions: { source: 4, transform: 'int' },
            clicks: { source: 5, transform: 'int' },
        },
    },
};

export const IngestModal: React.FC<IngestModalProps> = ({ isOpen, onClose, onSuccess }) => {
    const [sources, setSources] = useState<SourceFile[]>([]);
    const [loadingSources, setLoadingSources] = useState<boolean>(false);
    const [deliveryId, setDeliveryId] = useState<string>('meta_ads_2026-06-01');
    const [filepath, setFilepath] = useState<string>('data/deliveries/meta_ads_2026-06-01.csv');
    const [fileFormat, setFileFormat] = useState<string>('csv');
    const [configJson, setConfigJson] = useState<string>(
        JSON.stringify(PRESET_CONFIGS.meta_csv.config, null, 2)
    );

    const [loading, setLoading] = useState<boolean>(false);
    const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

    useEffect(() => {
        if (isOpen) {
            fetchSourceList();
        }
    }, [isOpen]);


    const loadPreset = (presetKey: keyof typeof PRESET_CONFIGS) => {
        const preset = PRESET_CONFIGS[presetKey];
        if (!deliveryId) setDeliveryId(preset.delivery_id);
        if (!filepath) setFilepath(preset.filepath);
        if (!fileFormat) setFileFormat(preset.file_format);
        setConfigJson(JSON.stringify(preset.config, null, 2));
    };

    const fetchSourceList = async () => {
        setLoadingSources(true);
        try {
            const res = await fetch('http://localhost:8000/api/v1/source_list');
            const data = await res.json();
            const availableFiles: SourceFile[] = data.sources || [];
            setSources(availableFiles);

            // Auto-select first source if available
            if (availableFiles.length > 0) {
                handleSourceSelect(availableFiles[0].filepath, availableFiles);
            }
        } catch (err) {
            console.error('Failed to fetch source files:', err);
        } finally {
            setLoadingSources(false);
        }
    };

    const handleSourceSelect = (selectedPath: string, fileList: SourceFile[] = sources) => {
        setFilepath(selectedPath);
        const selectedFile = fileList.find((s) => s.filepath === selectedPath);
        if (selectedFile) {
            if (selectedFile.format !== 'unknown') {
                setFileFormat(selectedFile.format);
            }
            // Auto-generate delivery ID from filename (strip extension)
            const autoId = selectedFile.filename.replace(/\.[^/.]+$/, '');
            setDeliveryId(autoId);
        }
    };

    const handleTriggerIngestion = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        setMessage(null);

        try {
            const parsedConfig = JSON.parse(configJson);

            const response = await fetch('http://localhost:8000/api/v1/ingest', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    delivery_id: deliveryId,
                    filepath: filepath,
                    file_format: fileFormat,
                    config: parsedConfig,
                }),
            });

            if (!response.ok) {
                throw new Error(`Ingestion failed with status ${response.status}`);
            }

            const data = await response.json();
            setMessage({ type: 'success', text: data.message || 'Ingestion queued successfully!' });
            setTimeout(() => {
                onSuccess();
                onClose();
            }, 1500);
        } catch (err: any) {
            setMessage({ type: 'error', text: err.message || 'Failed to submit ingestion job.' });
        } finally {
            setLoading(false);
        }
    };

    if (!isOpen) return null;

    return (
        <div style={{
            position: 'fixed', top: 0, left: 0, width: '100%', height: '100%',
            backgroundColor: 'rgba(0,0,0,0.5)', display: 'flex', justifyContent: 'center', alignItems: 'center', zIndex: 1000
        }}>
            <div style={{ background: '#fff', width: '600px', padding: '25px', borderRadius: '8px', boxShadow: '0 4px 15px rgba(0,0,0,0.3)', fontFamily: 'sans-serif' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '15px' }}>
                    <h3 style={{ margin: 0 }}>FR-6: Trigger Data Ingestion</h3>
                    <button onClick={onClose} style={{ border: 'none', background: 'transparent', cursor: 'pointer', fontSize: '18px' }}>✕</button>
                </div>

                {/* Presets */}
                <div style={{ marginBottom: '15px', background: '#f8f9fa', padding: '10px', borderRadius: '4px' }}>
                    <small style={{ fontWeight: 'bold' }}>Load Configuration Preset:</small>
                    <div style={{ display: 'flex', gap: '10px', marginTop: '5px' }}>
                        <button type="button" onClick={() => loadPreset('meta_csv')} style={{ padding: '4px 8px', cursor: 'pointer' }}>Meta CSV Preset</button>
                        <button type="button" onClick={() => loadPreset('linkedin_json')} style={{ padding: '4px 8px', cursor: 'pointer' }}>LinkedIn JSON Preset</button>
                        <button type="button" onClick={() => loadPreset('google_ads')} style={{ padding: '4px 8px', cursor: 'pointer' }}>Google Ads CSV Preset</button>
                    </div>
                </div>

                <form onSubmit={handleTriggerIngestion}>
                    <div style={{ marginBottom: '12px' }}>
                        <label style={{ display: 'block', fontWeight: 'bold', fontSize: '12px' }}>Delivery ID:</label>
                        <input type="text" value={deliveryId} onChange={(e) => setDeliveryId(e.target.value)} required style={{ width: '100%', padding: '6px', boxSizing: 'border-box' }} />
                    </div>

                    <div style={{ display: 'flex', gap: '10px', marginBottom: '12px' }}>
                        <div style={{ flex: 3 }}>
                            <label style={{ display: 'block', fontWeight: 'bold', fontSize: '12px' }}>File Path:</label>
                            <select
                                value={filepath}
                                onChange={(e) => handleSourceSelect(e.target.value)}
                                required
                                disabled={loadingSources}
                                style={{ width: '100%', padding: '6px', boxSizing: 'border-box' }}
                            >
                                {loadingSources ? (
                                    <option value="">Loading files...</option>
                                ) : sources.length === 0 ? (
                                    <option value="">No delivery files found in data/deliveries</option>
                                ) : (
                                    sources.map((src) => (
                                        <option key={src.filepath} value={src.filepath}>
                                            {src.filename} ({src.format.toUpperCase()})
                                        </option>
                                    ))
                                )}
                            </select>
                        </div>
                        <div style={{ flex: 1 }}>
                            <label style={{ display: 'block', fontWeight: 'bold', fontSize: '12px' }}>Format:</label>
                            <select value={fileFormat} onChange={(e) => setFileFormat(e.target.value)} style={{ width: '100%', padding: '6px' }}>
                                <option value="csv">CSV</option>
                                <option value="json">JSON</option>
                                <option value="xml">XML</option>
                            </select>
                        </div>
                    </div>

                    <div style={{ marginBottom: '15px' }}>
                        <label style={{ display: 'block', fontWeight: 'bold', fontSize: '12px' }}>Schema Config (JSON):</label>
                        <textarea
                            rows={8}
                            value={configJson}
                            onChange={(e) => setConfigJson(e.target.value)}
                            required
                            style={{ width: '100%', fontFamily: 'monospace', fontSize: '12px', padding: '6px', boxSizing: 'border-box' }}
                        />
                    </div>

                    {message && (
                        <div style={{
                            padding: '10px', borderRadius: '4px', marginBottom: '15px',
                            backgroundColor: message.type === 'success' ? '#d4edda' : '#f8d7da',
                            color: message.type === 'success' ? '#155724' : '#721c24'
                        }}>
                            {message.text}
                        </div>
                    )}

                    <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px' }}>
                        <button type="button" onClick={onClose} style={{ padding: '8px 16px' }}>Cancel</button>
                        <button type="submit" disabled={loading} style={{ padding: '8px 16px', backgroundColor: '#28a745', color: '#fff', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>
                            {loading ? 'Queuing Ingestion...' : 'Execute Ingestion'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};
