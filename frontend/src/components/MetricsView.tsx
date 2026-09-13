import React, { useState, useMemo, useEffect } from 'react';
import { type AggregatedMetric } from '../types';
import { LineageDrawer } from './LineageDrawer';

export const MetricsView: React.FC = () => {
    const [platform, setPlatform] = useState<string>('');
    const [startDate, setStartDate] = useState<string>('');
    const [endDate, setEndDate] = useState<string>('');
    const [sortField, setSortField] = useState<'total_spend_usd' | 'ctr'>('total_spend_usd');
    const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');

    const [metrics, setMetrics] = useState<AggregatedMetric[]>([]);
    const [loading, setLoading] = useState<boolean>(false);
    const [selectedAuditCampaign, setSelectedAuditCampaign] = useState<string | null>();

    useEffect(() => {
        fetchMetrics();
    }, [platform, startDate, endDate]);

    const fetchMetrics = async () => {
        setLoading(true);
        try {
            const params = new URLSearchParams({ group_by: 'campaign' });
            if (platform) params.append('platform', platform);
            if (startDate) params.append('start_date', startDate);
            if (endDate) params.append('end_date', endDate);

            const res = await fetch(`http://localhost:8000/api/v1/metrics/aggregated?${params.toString()}`);
            const data = await res.json();
            setMetrics(data);
        } catch (err) {
            console.error('Failed to load metrics:', err);
        } finally {
            setLoading(false);
        }
    };

    // Sort Metrics
    const sortedMetrics = useMemo(() => {
        return [...metrics].sort((a, b) => {
            const valA = a[sortField];
            const valB = b[sortField];
            return sortOrder === 'desc' ? valB - valA : valA - valB;
        });
    }, [metrics, sortField, sortOrder]);

    // Totals Summary calculated across active filters
    const totals = useMemo(() => {
        return metrics.reduce(
            (acc, item) => {
                acc.spend += item.total_spend_usd;
                acc.impressions += item.total_impressions;
                acc.clicks += item.total_clicks;
                return acc;
            },
            { spend: 0, impressions: 0, clicks: 0 }
        );
    }, [metrics]);

    const overallCTR = totals.impressions > 0 ? (totals.clicks / totals.impressions) : 0;
    const overallCPC = totals.clicks > 0 ? (totals.spend / totals.clicks) : 0;

    const handleSort = (field: 'total_spend_usd' | 'ctr') => {
        if (sortField === field) {
            setSortOrder(sortOrder === 'desc' ? 'asc' : 'desc');
        } else {
            setSortField(field);
            setSortOrder('desc');
        }
    };

    return (
        <div style={{ padding: '20px', fontFamily: 'sans-serif' }}>
            <h2>FR-7: Campaign Metrics</h2>

            {/* Filters Bar */}
            <div style={{ display: 'flex', gap: '15px', marginBottom: '20px', background: '#f5f5f5', padding: '15px', borderRadius: '6px' }}>
                <div>
                    <label style={{ display: 'block', fontWeight: 'bold' }}>Platform:</label>
                    <select value={platform} onChange={(e) => setPlatform(e.target.value)} style={{ padding: '6px' }}>
                        <option value="">All Platforms</option>
                        <option value="Meta">Meta</option>
                        <option value="Google">Google</option>
                        <option value="LinkedIn">LinkedIn</option>
                        <option value="TikTok">TikTok</option>
                    </select>
                </div>

                <div>
                    <label style={{ display: 'block', fontWeight: 'bold' }}>Start Date:</label>
                    <input type="date" value={startDate} onChange={(e) => setStartDate(e.target.value)} style={{ padding: '5px' }} />
                </div>

                <div>
                    <label style={{ display: 'block', fontWeight: 'bold' }}>End Date:</label>
                    <input type="date" value={endDate} onChange={(e) => setEndDate(e.target.value)} style={{ padding: '5px' }} />
                </div>
            </div>

            {/* Totals Summary Cards */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: '10px', marginBottom: '20px' }}>
                <div style={{ background: '#eef6ff', padding: '12px', borderRadius: '4px', textAlign: 'center' }}>
                    <small>Total Spend (USD)</small>
                    <h3>${totals.spend.toLocaleString(undefined, { minimumFractionDigits: 2 })}</h3>
                </div>
                <div style={{ background: '#eef6ff', padding: '12px', borderRadius: '4px', textAlign: 'center' }}>
                    <small>Total Impressions</small>
                    <h3>{totals.impressions.toLocaleString()}</h3>
                </div>
                <div style={{ background: '#eef6ff', padding: '12px', borderRadius: '4px', textAlign: 'center' }}>
                    <small>Total Clicks</small>
                    <h3>{totals.clicks.toLocaleString()}</h3>
                </div>
                <div style={{ background: '#eef6ff', padding: '12px', borderRadius: '4px', textAlign: 'center' }}>
                    <small>Avg CTR</small>
                    <h3>{(overallCTR * 100).toFixed(2)}%</h3>
                </div>
                <div style={{ background: '#eef6ff', padding: '12px', borderRadius: '4px', textAlign: 'center' }}>
                    <small>Avg CPC</small>
                    <h3>${overallCPC.toFixed(2)}</h3>
                </div>
            </div>

            {/* Metrics Table */}
            {loading ? <p>Loading metrics...</p> : (
                <table border={1} cellPadding={8} style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
                    <thead>
                        <tr style={{ background: '#eaeaea' }}>
                            <th>Campaign Name</th>
                            <th onClick={() => handleSort('total_spend_usd')} style={{ cursor: 'pointer' }}>
                                Spend (USD) {sortField === 'total_spend_usd' ? (sortOrder === 'desc' ? '▼' : '▲') : ''}
                            </th>
                            <th>Impressions</th>
                            <th>Clicks</th>
                            <th onClick={() => handleSort('ctr')} style={{ cursor: 'pointer' }}>
                                CTR (%) {sortField === 'ctr' ? (sortOrder === 'desc' ? '▼' : '▲') : ''}
                            </th>
                            <th>CPC (USD)</th>
                        </tr>
                    </thead>
                    <tbody>
                        {sortedMetrics.map((row) => (
                            <tr key={row.group_key}>
                                <td><strong>{row.group_key}</strong></td>
                                <td>${row.total_spend_usd.toLocaleString(undefined, { minimumFractionDigits: 2 })}</td>
                                <td>{row.total_impressions.toLocaleString()}</td>
                                <td>{row.total_clicks.toLocaleString()}</td>
                                <td>{(row.ctr * 100).toFixed(2)}%</td>
                                <td>${row.cpc.toFixed(2)}</td>
                                <td style={{ textAlign: 'center' }}>
                                    <button
                                        onClick={() => setSelectedAuditCampaign(row.group_key)}
                                        style={{
                                            padding: '4px 8px',
                                            backgroundColor: '#17a2b8',
                                            color: '#fff',
                                            border: 'none',
                                            borderRadius: '4px',
                                            cursor: 'pointer',
                                            fontSize: '12px'
                                        }}
                                    >
                                        🔍 Audit Lineage
                                    </button>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            )}
            {/* Audit Drawer Triggered by Column Action */}
            {selectedAuditCampaign && (
                <LineageDrawer
                    campaign={selectedAuditCampaign}
                    onClose={() => setSelectedAuditCampaign(null)}
                />
            )}
        </div>
    );
};
