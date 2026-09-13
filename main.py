from src.ingestion.Reader import Reader
from src.transformers.campaign_transformer import ConfigurableCampaignTransformer
from src.ingestion.pipeline import IngestionPipeline
from src.reports.report_writer import QualityReportWriter
from src.schemas.definitions import abm_json_config

# 1. Setup ingestion & processing
reader = Reader(format="json", filename="data/deliveries/linkedin_ads_2026-06-01.json")

transformer = ConfigurableCampaignTransformer(abm_json_config)
pipeline = IngestionPipeline(reader, transformer)

# 2. Run pipeline
result = pipeline.process_all()

# 3. Generate and persist quality report
writer = QualityReportWriter(delivery_id="linkedin_ads_2026-06-01")
report = writer.generate_report(result)
saved_path = writer.persist(report, output_dir="data/reports")

print(f"Report generated successfully: {saved_path}")
print(f"Overall Delivery Status: {report.health_status}")
