from datetime import date as datetype, datetime
from sqlalchemy import String, Float, Integer, Date, DateTime, ForeignKey, JSON
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass

class DeliveryRecord(Base):
    __tablename__ = "deliveries"

    delivery_id: Mapped[str] = mapped_column(String, primary_key=True)
    filename: Mapped[str] = mapped_column(String, nullable=False)
    processed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    health_status: Mapped[str] = mapped_column(String, nullable=False) # HEALTHY, DEGRADED, CRITICAL
    total_records: Mapped[int] = mapped_column(Integer, default=0)
    error_records: Mapped[int] = mapped_column(Integer, default=0)
    report_json: Mapped[dict] = mapped_column(JSON, nullable=False) # Full FR-2 Quality Report
    # NFR-3: Persist exact schema mapping config used for this delivery
    applied_config_json = mapped_column(JSON, nullable=False)

    metrics: Mapped[list["CampaignMetricRecord"]] = relationship(back_populates="delivery", cascade="all, delete-orphan")

class CampaignMetricRecord(Base):
    __tablename__ = "campaign_metrics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    delivery_id: Mapped[str] = mapped_column(String, ForeignKey("deliveries.delivery_id"), index=True)
    platform: Mapped[str] = mapped_column(String, index=True)
    campaign: Mapped[str] = mapped_column(String, index=True)
    date: Mapped[datetype] = mapped_column(Date, index=True)
    spend_usd: Mapped[float] = mapped_column(Float, default=0.0)
    impressions: Mapped[int] = mapped_column(Integer, default=0)
    clicks: Mapped[int] = mapped_column(Integer, default=0)

    delivery: Mapped[DeliveryRecord] = relationship(back_populates="metrics")
