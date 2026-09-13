from typing import Generator, Union
from src.models.ingestion_results import TransformationError, TransformationResult
from src.models.models import CampaignMetric


class IngestionPipeline:
    def __init__(self, reader, transformer):
        """
        :param reader: Instance of Reader (yields raw chunks)
        :param transformer: Instance of ConfigurableCampaignTransformer
        """
        self.reader = reader
        self.transformer = transformer

    def process_stream(self) -> Generator[Union[CampaignMetric, TransformationError], None, None]:
        """
        Yields results immediately line-by-line as either a CampaignMetric or TransformationError.
        """
        # Start tracking line numbers (1-indexed, accounting for potential headers)
        for line_idx, raw_chunk in enumerate(self.reader.read(), start=1):
            try:
                metric = self.transformer.transform(raw_chunk)
                yield metric
            except Exception as e:
                yield TransformationError(
                    line_number=line_idx,
                    raw_record=raw_chunk,
                    error_type=type(e).__name__,
                    reason=str(e),
                )

    def process_all(self) -> TransformationResult:
        """
        Processes the entire stream into a collected TransformationResult container.
        """
        result = TransformationResult()
        for item in self.process_stream():
            if isinstance(item, CampaignMetric):
                result.metrics.append(item)
            elif isinstance(item, TransformationError):
                result.errors.append(item)
        return result
