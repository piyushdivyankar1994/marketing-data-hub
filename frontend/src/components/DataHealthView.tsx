import React, { useState, useEffect } from 'react';
import type { DeliverySummary, HealthStatus, QualityReport } from '../types';

export const DataHealthView: React.FC = () => {
    const [deliveries, setDeliveries] = useState<DeliverySummary[]>([]);
    const [selectedReport, setSelectedReport] = useState<QualityReport | null>(null);
    const [loading, setLoading] = useState<boolean>(false);

    useEffect(() => {
        fetchDeliveries();
    }, []);

    const fetchDeliveries = async () => {
        try {
            const res = await fetch('http://localhost:8000/api/v1/deliveries');
            const data = await res.json();
            setDeliveries(data);
        } catch (err) {
            console.error('Failed to fetch deliveries:', err);
        }
    };

    const fetchReportDetails = async (deliveryId: string) => {
        setLoading(true);
        try {
            const res = await fetch(`http://localhost:8000/api/v1/deliveries/${deliveryId}/report`);
            const data = await res.json();
            setSelectedReport(data);
        } catch (err) {
            console.error('Failed to fetch report detail:', err);
        } finally {
            setLoading(false);
        }
    };

    const getStatusBadge = (status: HealthStatus) => {
        const styles: Record<HealthStatus, { bg: string; color: string }> = {
            HEALTHY: { bg: '#d4edda', color: '#155724' },
            DEGRADED: { bg: '#fff3cd', color: '#856404' },
            CRITICAL: { bg: '#f8d7da', color: '#721c24' },
        };
        const s = styles[status] || styles.HEALTHY;
        return (
            <span style={{ backgroundColor: s.bg, color: s.color, padding: '4px 8px', borderRadius: '4px', fontWeight: 'bold' }}>
                {status}
            </span>
        );
    };

    return (
        <div style={{ padding: '20px', fontFamily: 'sans-serif' }}>
            <h2>FR-8: Data Health Dashboard</h2>

            {/* Deliveries List */}
            <table border={1} cellPadding={8} style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
                <thead>
                    <tr style={{ background: '#eaeaea' }}>
                        <th>Delivery ID</th>
                        <th>File Path</th>
                        <th>Health Classification</th>
                        <th>Total Rows</th>
                        <th>Failed Rows</th>
                        <th>Action</th>
                    </tr>
                </thead>
                <tbody>
                    {deliveries.map((d) => (
                        <tr key={d.delivery_id}>
                            <td><code>{d.delivery_id}</code></td>
                            <td>{d.filename}</td>
                            <td>{getStatusBadge(d.health_status)}</td>
                            <td>{d.total_records}</td>
                            <td><strong style={{ color: d.error_records > 0 ? 'red' : 'inherit' }}>{d.error_records}</strong></td>
                            <td>
                                <button onClick={() => fetchReportDetails(d.delivery_id)}>
                                    View Report
                                </button>
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>

            {/* Detailed Report Modal / Drawer */}
            {selectedReport && (
                <div style={{
                    position: 'fixed', top: 0, right: 0, width: '500px', height: '100%',
                    backgroundColor: '#fff', boxShadow: '-2px 0 10px rgba(0,0,0,0.2)',
                    padding: '20px', overflowY: 'auto'
                }}>
                    <button onClick={() => setSelectedReport(null)} style={{ float: 'right' }}>Close ✕</button>
                    <h3>Delivery Report: {selectedReport.delivery_id}</h3>
                    <p>Overall Health: {getStatusBadge(selectedReport.health_status)}</p>
                    <hr />

                    <h4>Quality Checks Outcome</h4>
                    <ul>
                        {selectedReport.checks_executed.map((check) => (
                            <li key={check.check_id} style={{ marginBottom: '10px' }}>
                                <strong>[{check.status}]</strong> {check.name}: {check.message}
                            </li>
                        ))}
                    </ul>

                    <hr />
                    <h4>Failure Diagnostics (Sample {selectedReport.sample_failures.length})</h4>
                    {selectedReport.sample_failures.length === 0 ? <p>No errors recorded.</p> : (
                        <div>
                            {selectedReport.sample_failures.map((fail, i) => (
                                <div key={i} style={{ background: '#f8d7da', padding: '10px', borderRadius: '4px', marginBottom: '10px', fontSize: '12px' }}>
                                    <div><strong>Line {fail.line_number}:</strong> {fail.error_type}</div>
                                    <div><em>{fail.reason}</em></div>
                                    <pre style={{ overflowX: 'auto', background: '#fff', padding: '5px' }}>
                                        {JSON.stringify(fail.raw_record, null, 2)}
                                    </pre>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            )}
        </div>
    );
};
