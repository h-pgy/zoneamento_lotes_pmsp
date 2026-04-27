import unittest
from unittest.mock import MagicMock, patch, mock_open
import os
import pandas as pd
import tempfile
import zipfile
from io import BytesIO
from utils.download_file_geosampa.downloader import GeoSampaScraper

class TestGeoSampaScraper(unittest.TestCase):

    def setUp(self) -> None:
        self.scraper = GeoSampaScraper()
        self.mock_param = "test_path"

    def test_check_file_type_valid(self) -> None:
        result = self.scraper.check_file_type("CSV")
        self.assertEqual(result, "CSV")
        
        result = self.scraper.check_file_type("XLS_CSV")
        self.assertEqual(result, "XLS_CSV")

    def test_check_file_type_invalid(self) -> None:
        with self.assertRaises(NotImplementedError):
            self.scraper.check_file_type("PDF")

    @patch("utils.download_file_geosampa.downloader.zipfile.is_zipfile")
    def test_validate_content_html_error(self, mock_is_zip) -> None:
        mock_is_zip.return_value = False
        # Simula um arquivo que começa com tag html
        m = mock_open(read_data=b"<html><body>Erro</body></html>")
        with patch("builtins.open", m):
            with self.assertRaises(ValueError) as cm:
                self.scraper.validate_content("dummy_path")
            self.assertIn("HTML de erro", str(cm.exception))

    @patch("utils.download_file_geosampa.downloader.zipfile.ZipFile")
    def test_check_zip_no_files(self, mock_zip_class) -> None:
        mock_zip = MagicMock()
        mock_zip.namelist.return_value = ["image.png", "notes.txt"]
        
        with self.assertRaises(FileNotFoundError):
            self.scraper.check_zip(mock_zip)

    @patch("utils.download_file_geosampa.downloader.zipfile.ZipFile")
    def test_check_zip_multiple_files(self, mock_zip_class) -> None:
        mock_zip = MagicMock()
        mock_zip.namelist.return_value = ["data1.csv", "data2.csv"]
        
        with self.assertRaises(NotImplementedError):
            self.scraper.check_zip(mock_zip)

    def test_load_data_csv(self) -> None:
        # Criando um CSV temporário para teste
        csv_content = "col1;col2\nval1;val2"
        with tempfile.NamedTemporaryFile(suffix=".csv", mode="w", delete=False) as tmp:
            tmp.write(csv_content)
            tmp_path = tmp.name

        try:
            df = self.scraper.load_data(tmp_path, sep=';')
            self.assertIsInstance(df, pd.DataFrame)
            self.assertEqual(df.shape, (1, 2))
        finally:
            os.remove(tmp_path)

    @patch.object(GeoSampaScraper, "fetch_and_save_stream")
    @patch.object(GeoSampaScraper, "extract_if_zip")
    @patch.object(GeoSampaScraper, "load_data")
    def test_pipeline_flow(self, mock_load, mock_extract, mock_fetch) -> None:
        # Mocking do fluxo completo
        mock_fetch.return_value = "/tmp/data.zip"
        mock_extract.return_value = "/tmp/data.csv"
        mock_load.return_value = pd.DataFrame({"test": [1]})

        df = self.scraper("param", "CSV")

        mock_fetch.assert_called_once()
        mock_extract.assert_called_once()
        mock_load.assert_called_once()
        self.assertFalse(df.empty)

if __name__ == "__main__":
    unittest.main()