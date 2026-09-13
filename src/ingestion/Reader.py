import csv
import xml.etree.ElementTree as ET
from typing import Generator, Any
import ijson  # pip install ijson for streaming JSON
from abc import ABC, abstractmethod

class AbstractReader(ABC):
    @abstractmethod
    def read(self) -> Generator[Any, None, None]:
        pass


class Reader(AbstractReader):
    def __init__(self, format: str, filename: str, encoding: str = 'utf-8', target_tag: str = 'item', json_path: str = 'item'):
        """
        :param format: 'csv', 'json', or 'xml'
        :param filename: Path to the target file
        :param encoding: File encoding
        :param target_tag: (XML only) Tag name of elements to yield
        :param json_path: (JSON only) JSONPath expression for target array items
        """
        self.format = format.lower()
        self.filename = filename
        self.encoding = encoding
        self.target_tag = target_tag
        self.json_path = json_path

    def read(self) -> Generator[Any, None, None]:
        """Returns a generator yielding records one at a time."""
        if self.format == 'csv':
            yield from self._stream_csv()
        elif self.format == 'json':
            yield from self._stream_json()
        else:
            raise ValueError(f"Unsupported format: {self.format}")

    def _stream_csv(self) -> Generator[list[str], None, None]:
        with open(self.filename, mode='r', encoding=self.encoding) as f:
            reader = csv.reader(f)
            for row in reader:
                yield row

    def _stream_json(self) -> Generator[Any, None, None]:
        # Uses ijson to stream items from large JSON arrays without memory overhead
        with open(self.filename, mode='rb') as f:
            for item in ijson.items(f, self.json_path):
                yield item
