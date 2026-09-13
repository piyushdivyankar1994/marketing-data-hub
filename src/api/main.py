from datetime import date
from typing import Optional
from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks, Query
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from sqlalchemy.orm import Session
from sqlalchemy import func

from src.db.session import get_db, init_db, get_db_local
from src.db.models import DeliveryRecord, CampaignMetricRecord
from src.ingestion.Reader import Reader
from src.ingestion.pipeline import IngestionPipeline
from src.reports.report_writer import QualityReportWriter
from src.transformers.campaign_transformer import ConfigurableCampaignTransformer, parse_us_date, TRANSFORM_FUNCTIONS
from src.models.requests import IngestionRequest

app = FastAPI(title="Marketing Data Ingestion API", version="1.0.0")
DELIVERIES_DIR = Path("data/deliveries")

# Configure CORS middleware
origins = [
    "http://localhost:5173",  # Vite default frontend port
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,       # Or ["*"] for open development
    allow_credentials=True,
    allow_methods=["*"],         # Allows GET, POST, DELETE, OPTIONS, etc.
    allow_headers=["*"],         # Allows headers like Content-Type and Authorization
)

@app.on_event("startup")
def on_startup():
    init_db()

# ------------------------------------------------------------------
# FR-6: Trigger Ingestion API
# ------------------------------------------------------------------
def resolve_config_transforms(raw_config: dict) -> dict:
    """Replaces string transform names with actual callable functions."""
    resolved = {}
    for field, rule in raw_config.items():
        rule_dict = dict(rule) if isinstance(rule, dict) else rule
        if isinstance(rule_dict, dict) and "transform" in rule_dict:
            transform_val = rule_dict["transform"]
            if isinstance(transform_val, str):
                if transform_val in TRANSFORM_FUNCTIONS:
                    rule_dict["transform"] = TRANSFORM_FUNCTIONS[transform_val]
                else:
                    raise ValueError(f"Unknown transform function name: '{transform_val}'")
        resolved[field] = rule_dict
    return resolved

def run_ingestion_task(delivery_id: str, filepath: str, file_format: str, config: dict):
    # Remove existing delivery records if re-ingesting
    db = get_db_local()
    existing = db.query(DeliveryRecord).filter(DeliveryRecord.delivery_id == delivery_id).first()
    if existing:
        db.delete(existing)
        db.commit()
    resolved_config = resolve_config_transforms(config)

    reader = Reader(format=file_format, filename=filepath)
    transformer = ConfigurableCampaignTransformer(resolved_config)
    pipeline = IngestionPipeline(reader, transformer)
    
    result = pipeline.process_all()

    writer = QualityReportWriter(delivery_id=delivery_id)
    report = writer.generate_report(result)

    # Save Delivery & Report
    delivery_entry = DeliveryRecord(
        delivery_id=delivery_id,
        filename=filepath,
        health_status=report.health_status.value,
        total_records=report.summary.total_records_processed,
        error_records=report.summary.error_records_count,
        report_json=report.model_dump(),
        applied_config_json=config
    )
    db.add(delivery_entry)

    # Save Valid Canonical Metrics
    for metric in result.metrics:
        db.add(CampaignMetricRecord(
            delivery_id=delivery_id,
            platform=metric.platform,
            campaign=metric.campaign,
            date=metric.date,
            spend_usd=metric.spend_usd,
            impressions=metric.impressions,
            clicks=metric.clicks
        ))
    
    db.commit()

@app.post("/api/v1/ingest", status_code=202)
def trigger_ingestion(
    payload: IngestionRequest,
    background_tasks: BackgroundTasks,
):
    # Default preset config for demonstration
    default_config = {
        "platform": {"default": "Meta"},
        "campaign": {"source": 0},
        "date": {"source": 1, "transform": parse_us_date},
        "spend_usd": {"source": 2, "transform": float},
        "impressions": {"source": 3, "transform": int},
        "clicks": {"source": 4, "transform": int},
    }
    config_to_use = payload.config if payload.config else default_config

    background_tasks.add_task(
        run_ingestion_task,
        payload.delivery_id,
        payload.filepath,
        payload.file_format,
        config_to_use
    )
    return {"message": f"Ingestion job queued for delivery: {payload.delivery_id}"}


# ------------------------------------------------------------------
# FR-4: Campaign Metrics API (Filtering & Grouped Aggregations)
# ------------------------------------------------------------------
@app.get("/api/v1/metrics")
def get_metrics(
    platform: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db)
):
    query = db.query(CampaignMetricRecord)
    if platform:
        query = query.filter(CampaignMetricRecord.platform == platform)
    if start_date:
        query = query.filter(CampaignMetricRecord.date >= start_date)
    if end_date:
        query = query.filter(CampaignMetricRecord.date <= end_date)
    
    records = query.all()
    return [{
        "platform": r.platform,
        "campaign": r.campaign,
        "date": r.date,
        "spend_usd": r.spend_usd,
        "impressions": r.impressions,
        "clicks": r.clicks
    } for r in records]

@app.get("/api/v1/metrics/aggregated")
def get_aggregated_metrics(
    group_by: str = Query(..., enum=["campaign", "platform"]),
    platform: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db)
):
    group_field = CampaignMetricRecord.campaign if group_by == "campaign" else CampaignMetricRecord.platform
    
    query = db.query(
        group_field.label("group_key"),
        func.sum(CampaignMetricRecord.spend_usd).label("total_spend"),
        func.sum(CampaignMetricRecord.impressions).label("total_impressions"),
        func.sum(CampaignMetricRecord.clicks).label("total_clicks")
    )
    
    if platform:
        query = query.filter(CampaignMetricRecord.platform == platform)
    if start_date:
        query = query.filter(CampaignMetricRecord.date >= start_date)
    if end_date:
        query = query.filter(CampaignMetricRecord.date <= end_date)

    results = query.group_by(group_field).all()
    
    aggregated = []
    for r in results:
        spend = r.total_spend or 0.0
        impressions = r.total_impressions or 0
        clicks = r.total_clicks or 0

        # Derived Metrics: CTR & CPC
        ctr = (clicks / impressions) if impressions > 0 else 0.0
        cpc = (spend / clicks) if clicks > 0 else 0.0

        aggregated.append({
            group_by: r.group_key,
            "group_key": r.group_key,
            "total_spend_usd": round(spend, 2),
            "total_impressions": impressions,
            "total_clicks": clicks,
            "ctr": round(ctr, 4), # Click-Through Rate
            "cpc": round(cpc, 2)  # Cost Per Click
        })

    return aggregated


# ------------------------------------------------------------------
# FR-5: Data Health & Quality Report API
# ------------------------------------------------------------------
@app.get("/api/v1/deliveries")
def list_deliveries(db: Session = Depends(get_db)):
    deliveries = db.query(DeliveryRecord).all()
    return [{
        "delivery_id": d.delivery_id,
        "filename": d.filename,
        "processed_at": d.processed_at,
        "health_status": d.health_status,
        "total_records": d.total_records,
        "error_records": d.error_records
    } for d in deliveries]

@app.get("/api/v1/deliveries/{delivery_id}/report")
def get_delivery_report(delivery_id: str, db: Session = Depends(get_db)):
    delivery = db.query(DeliveryRecord).filter(DeliveryRecord.delivery_id == delivery_id).first()
    if not delivery:
        raise HTTPException(status_code=404, detail=f"Delivery report '{delivery_id}' not found")
    return delivery.report_json

@app.get("/api/v1/source_list")
def get_source_list():
    # return files in data/deliveries
    if not DELIVERIES_DIR.exists() or not DELIVERIES_DIR.is_dir():
        raise HTTPException(
            status_code=404, 
            detail="Directory 'data/deliveries' does not exist."
        )
    
    files = []
    for file_path in DELIVERIES_DIR.iterdir():
        # Exclude hidden files (like .DS_Store or .gitkeep) and subdirectories
        if file_path.is_file() and not file_path.name.startswith("."):
            ext = file_path.suffix.lstrip(".").lower()
            files.append({
                "filename": file_path.name,
                "filepath": str(file_path),
                "format": ext if ext in ["csv", "json", "xml"] else "unknown",
                "size_bytes": file_path.stat().st_size
            })
            
    return {"sources": files}

@app.get("/health")
def get_health_check():
    return {"status": "ok"}

@app.get("/api/v1/metrics/lineage", summary="NFR-3 Traceability: Audit lineage for a specific metric")
def get_metric_lineage(
    campaign: Optional[str] = Query(None),
    platform: Optional[str] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(
        CampaignMetricRecord.delivery_id,
        DeliveryRecord.filename,
        DeliveryRecord.applied_config_json,
        func.count(CampaignMetricRecord.id).label("contributing_rows"),
        func.sum(CampaignMetricRecord.spend_usd).label("contributed_spend"),
        func.sum(CampaignMetricRecord.impressions).label("contributed_impressions"),
        func.sum(CampaignMetricRecord.clicks).label("contributed_clicks")
    ).join(DeliveryRecord, CampaignMetricRecord.delivery_id == DeliveryRecord.delivery_id)

    if campaign:
        query = query.filter(CampaignMetricRecord.campaign == campaign)
    if platform:
        query = query.filter(CampaignMetricRecord.platform == platform)
    if start_date:
        query = query.filter(CampaignMetricRecord.date >= start_date)
    if end_date:
        query = query.filter(CampaignMetricRecord.date <= end_date)

    results = query.group_by(CampaignMetricRecord.delivery_id, DeliveryRecord.filename, DeliveryRecord.applied_config_json).all()

    lineage_trace = []
    for r in results:
        lineage_trace.append({
            "delivery_id": r.delivery_id,
            "filename": r.filename,
            "contributing_rows": r.contributing_rows,
            "contributed_spend": round(r.contributed_spend or 0.0, 2),
            "contributed_impressions": r.contributed_impressions or 0,
            "contributed_clicks": r.contributed_clicks or 0,
            "transformation_rules": r.applied_config_json  # Complete rule audit
        })

    return {
        "audit_filter": {"campaign": campaign, "platform": platform, "start_date": start_date, "end_date": end_date},
        "contributing_deliveries_count": len(lineage_trace),
        "deliveries": lineage_trace
    }
