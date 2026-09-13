import React, { useState, useEffect } from 'react';

interface LineageDrawerProps {
    campaign: string;
    onClose: () => void;
}

export const LineageDrawer: React.FC<LineageDrawerProps> = ({ campaign, onClose }) => {
    const [lineage, setLineage] = useState<any>(null);
    const [loading, setLoading] = useState<boolean>(true);

    useEffect(() => {
        fetch(`http://localhost:8000/api/v1/metrics/lineage?campaign=${encodeURIComponent(campaign)}`)
            .then((res) => res.json())
            .then((data) => {
                setLineage(data);
                setLoading(false);
            });
    }, [campaign]);

    return (
        <div style={{
            position: 'fixed', top: 0, right: 0, width: '550px', height: '100%',
            backgroundColor: '#fff', boxShadow: '-2px 0 10px rgba(0,0,0,0.2)',
            padding: '20px', overflowY: 'auto', zIndex: 1100, fontFamily: 'sans-serif'
        }}>
            <button onClick={onClose} style={{ float: 'right' }}>Close ✕</button>
            <h3>NFR-3 Lineage Audit: {campaign}</h3>

            {loading ? <p>Tracing data provenance...</p> : (
                <div>
                    <p><strong>Contributing Deliveries:</strong> {lineage.contributing_deliveries_count}</p>
                    <hr />
                    {lineage.deliveries.map((d: any) => (
                        <div key={d.delivery_id} style={{ border: '1px solid #ddd', padding: '12px', marginBottom: '12px', borderRadius: '4px' }}>
                            <div><strong>Delivery ID:</strong> <code>{d.delivery_id}</code></div>
                            <div><strong>File Source:</strong> {d.filename}</div>
                            <div><strong>Contributing Rows:</strong> {d.contributing_rows}</div>
                            <div><strong>Contributed Spend:</strong> ${d.contributed_spend.toFixed(2)}</div>

                            <details style={{ marginTop: '8px' }}>
                                <summary style={{ cursor: 'pointer', fontWeight: 'bold', color: '#007bff' }}>
                                    View Applied Transformation Rules
                                </summary>
                                <pre style={{ background: '#f8f9fa', padding: '8px', fontSize: '11px', overflowX: 'auto' }}>
                                    {JSON.stringify(d.transformation_rules, null, 2)}
                                </pre>
                            </details>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};
