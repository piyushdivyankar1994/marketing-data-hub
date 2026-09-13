import unittest
from unittest.mock import patch, mock_open, MagicMock
from src.ingestion.Reader import Reader


class TestReader(unittest.TestCase):

    @patch("builtins.open", new_callable=mock_open, read_data="header1,header2\nval1,val2\n")
    @patch("csv.reader")
    def test_read_csv(self, mock_csv_reader, mock_file):
        # Mock CSV rows returned by csv.reader
        mock_csv_reader.return_value = [["header1", "header2"], ["val1", "val2"]]

        reader = Reader(format="csv", filename="dummy.csv")
        results = list(reader.read())

        # Assertions
        mock_file.assert_called_once_with("dummy.csv", mode="r", encoding="utf-8")
        mock_csv_reader.assert_called_once()
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0], ["header1", "header2"])
        self.assertEqual(results[1], ["val1", "val2"])

    @patch("ijson.items")
    @patch("builtins.open", new_callable=mock_open, read_data=b'[{"id": 1}, {"id": 2}]')
    def test_read_json(self, mock_file, mock_ijson_items):
        # Mock objects yielded by ijson
        mock_ijson_items.return_value = iter([{"id": 1}, {"id": 2}])

        reader = Reader(format="json", filename="dummy.json", json_path="item")
        results = list(reader.read())

        # Assertions
        mock_file.assert_called_once_with("dummy.json", mode="rb")
        mock_ijson_items.assert_called_once_with(mock_file(), "item")
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0], {"id": 1})
        self.assertEqual(results[1], {"id": 2})

    def test_unsupported_format(self):
        reader = Reader(format="yaml", filename="dummy.yaml")
        with self.assertRaises(ValueError) as context:
            list(reader.read())
        
        self.assertIn("Unsupported format: yaml", str(context.exception))


if __name__ == "__main__":
    unittest.main()
