export interface Metric {
    platform: string;
    campaign: string;
    date: string;
    spend_usd: number;
    impressions: number;
    clicks: number;
}

export interface AggregatedMetric {
    group_key: string;
    total_spend_usd: number;
    total_impressions: number;
    total_clicks: number;
    ctr: number;
    cpc: number;
}

export type HealthStatus = 'HEALTHY' | 'DEGRADED' | 'CRITICAL';

export interface DeliverySummary {
    delivery_id: string;
    filename: string;
    processed_at: string;
    health_status: HealthStatus;
    total_records: number;
    valid_records: number;
    error_records: number;
}

export interface QualityCheck {
    check_id: string;
    name: string;
    scope: string;
    status: 'PASSED' | 'WARNING' | 'FAILED';
    message: string;
    details: Record<string, any>;
}

export interface QualityReport {
    delivery_id: string;
    processed_at: string;
    health_status: HealthStatus;
    summary: {
        total_records_processed: number;
        valid_records_count: number;
        error_records_count: number;
        error_rate_percentage: number;
        duplicate_rows_count: number;
        total_spend_usd: number;
    };
    checks_executed: QualityCheck[];
    sample_failures: Array<{
        line_number: number;
        error_type: string;
        reason: string;
        raw_record: any;
    }>;
}
