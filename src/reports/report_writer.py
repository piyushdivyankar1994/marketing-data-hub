from pathlib import Path
from typing import List

from src.models.ingestion_results import TransformationResult
from src.models.quality_schema import (
    CheckScope,
    CheckStatus,
    HealthStatus,
    QualityCheckResult,
    StructuredQualityReport,
    SummaryMetrics,
)


class QualityReportWriter:
    """Ingests TransformationResult objects, runs delivery-level quality checks,

    and persists a structured quality report to disk or output streams.
    """

    def __init__(self, delivery_id: str, error_threshold_pct: float = 5.0):
        self.delivery_id = delivery_id
        self.error_threshold_pct = error_threshold_pct

    def generate_report(self, result: TransformationResult) -> StructuredQualityReport:
        checks: List[QualityCheckResult] = []

        total = len(result.metrics) + len(result.errors)
        valid_count = len(result.metrics)
        error_count = len(result.errors)
        error_rate = (error_count / total * 100.0) if total > 0 else 0.0
        total_spend = sum(m.spend_usd for m in result.metrics)

        # 1. Check: Completeness / Empty Payload
        if total == 0:
            checks.append(
                QualityCheckResult(
                    check_id="FILE_COMPLETENESS",
                    name="File Completeness Check",
                    scope=CheckScope.FILE,
                    status=CheckStatus.FAILED,
                    message="The delivery file contains no readable data records.",
                    details={"total_rows": 0},
                )
            )
        else:
            checks.append(
                QualityCheckResult(
                    check_id="FILE_COMPLETENESS",
                    name="File Completeness Check",
                    scope=CheckScope.FILE,
                    status=CheckStatus.PASSED,
                    message=f"File contains {total} total records.",
                    details={"total_rows": total},
                )
            )

        # 2. Check: Row Validity & Error Rate Threshold
        if error_rate == 0.0:
            checks.append(
                QualityCheckResult(
                    check_id="ROW_VALIDITY",
                    name="Row Parsing & Schema Validation",
                    scope=CheckScope.ROW,
                    status=CheckStatus.PASSED,
                    message="All rows passed validation with zero errors.",
                    details={"error_count": 0, "error_rate_pct": 0.0},
                )
            )
        elif error_rate <= self.error_threshold_pct:
            checks.append(
                QualityCheckResult(
                    check_id="ROW_VALIDITY",
                    name="Row Parsing & Schema Validation",
                    scope=CheckScope.ROW,
                    status=CheckStatus.WARNING,
                    message=f"Encountered minor validation errors ({error_rate:.2f}% of rows).",
                    details={"error_count": error_count, "error_rate_pct": round(error_rate, 2)},
                )
            )
        else:
            checks.append(
                QualityCheckResult(
                    check_id="ROW_VALIDITY",
                    name="Row Parsing & Schema Validation",
                    scope=CheckScope.ROW,
                    status=CheckStatus.FAILED,
                    message=f"High failure rate detected! Exceeds threshold of {self.error_threshold_pct}%.",
                    details={"error_count": error_count, "error_rate_pct": round(error_rate, 2)},
                )
            )

        # 3. Check: Duplication Check (Campaign + Date + Platform uniqueness)
        seen_keys = set()
        duplicate_count = 0
        for metric in result.metrics:
            key = (metric.platform, metric.campaign, str(metric.date))
            if key in seen_keys:
                duplicate_count += 1
            else:
                seen_keys.add(key)

        if duplicate_count > 0:
            checks.append(
                QualityCheckResult(
                    check_id="DELIVERY_DUPLICATION",
                    name="Record Uniqueness Check",
                    scope=CheckScope.DELIVERY,
                    status=CheckStatus.WARNING,
                    message=f"Found {duplicate_count} duplicate campaign/date records in delivery.",
                    details={"duplicate_count": duplicate_count},
                )
            )
        else:
            checks.append(
                QualityCheckResult(
                    check_id="DELIVERY_DUPLICATION",
                    name="Record Uniqueness Check",
                    scope=CheckScope.DELIVERY,
                    status=CheckStatus.PASSED,
                    message="No duplicate records found across campaign metrics.",
                    details={"duplicate_count": 0},
                )
            )

        # Determine overall delivery health
        if any(c.status == CheckStatus.FAILED for c in checks):
            overall_health = HealthStatus.CRITICAL
        elif any(c.status == CheckStatus.WARNING for c in checks):
            overall_health = HealthStatus.DEGRADED
        else:
            overall_health = HealthStatus.HEALTHY

        # Extract up to 5 sample failures for detailed diagnostics
        sample_failures = [err.model_dump() for err in result.errors[:5]]

        summary = SummaryMetrics(
            total_records_processed=total,
            valid_records_count=valid_count,
            error_records_count=error_count,
            error_rate_percentage=round(error_rate, 2),
            duplicate_rows_count=duplicate_count,
            total_spend_usd=round(total_spend, 2),
        )

        return StructuredQualityReport(
            delivery_id=self.delivery_id,
            health_status=overall_health,
            summary=summary,
            checks_executed=checks,
            sample_failures=sample_failures,
        )

    def persist(
        self,
        report: StructuredQualityReport,
        output_dir: str = "reports",
        as_markdown: bool = True,
    ) -> Path:
        """Persists the JSON report (and optional Markdown summary) to disk."""
        out_path = Path(output_dir)
        out_path.mkdir(parents=True, exist_ok=True)

        json_file = out_path / f"quality_report_{report.delivery_id}.json"
        with open(json_file, "w", encoding="utf-8") as f:
            f.write(report.model_dump_json(indent=2))

        if as_markdown:
            md_file = out_path / f"quality_report_{report.delivery_id}.md"
            with open(md_file, "w", encoding="utf-8") as f:
                f.write(self._to_markdown(report))

        return json_file

    def _to_markdown(self, report: StructuredQualityReport) -> str:
        md = [
            f"# Delivery Quality Report: `{report.delivery_id}`",
            f"**Health Status:** `{report.health_status.value}`  ",
            f"**Processed At:** {report.processed_at}\n",
            "## Summary Metrics",
            f"- **Total Rows:** {report.summary.total_records_processed}",
            f"- **Valid Rows:** {report.summary.valid_records_count}",
            f"- **Errors:** {report.summary.error_records_count} ({report.summary.error_rate_percentage}%)",
            f"- **Duplicates:** {report.summary.duplicate_rows_count}",
            f"- **Total Spend:** ${report.summary.total_spend_usd:,.2f}\n",
            "## Executed Quality Checks",
            "| Check ID | Scope | Status | Message |",
            "| --- | --- | --- | --- |",
        ]

        for check in report.checks_executed:
            md.append(
                f"| `{check.check_id}` | {check.scope.value} | **{check.status.value}** | {check.message} |"
            )

        if report.sample_failures:
            md.extend(["\n## Sample Diagnostics (First 5 Failures)", "| Line | Error Type | Reason | Raw Record |", "| --- | --- | --- | --- |"])
            for err in report.sample_failures:
                md.append(
                    f"| {err['line_number']} | `{err['error_type']}` | {err['reason']} | `{err['raw_record']}` |"
                )

        return "\n".join(md)
