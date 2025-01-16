import os
import unittest
from unittest.mock import mock_open, patch

from src.utils import extract_text_from_pdf


class TestExtractTextFromPDF(unittest.TestCase):

    def setUp(self):
        # Setup mock PDFs or files
        self.valid_pdf_path = "valid.pdf"
        self.empty_pdf_path = "empty.pdf"
        self.invalid_pdf_path = "not_a_pdf.txt"
        self.nonexistent_pdf_path = "nonexistent.pdf"
        self.corrupted_pdf_path = "corrupted.pdf"
        self.mock_pdf_with_text = "This is a test PDF.Page 2 content here."
        self.mock_empty_pdf = ""

    @patch("pdfplumber.open")
    def test_valid_pdf(self, mock_pdfplumber_open):
        # Mock a valid PDF with text
        mock_pdf = mock_pdfplumber_open.return_value.__enter__.return_value
        mock_pdf.pages = [
            MockPage("This is a test PDF."),
            MockPage("Page 2 content here."),
        ]

        result = extract_text_from_pdf(self.valid_pdf_path)
        self.assertEqual(result, self.mock_pdf_with_text)

    @patch("pdfplumber.open")
    def test_empty_pdf(self, mock_pdfplumber_open):
        # Mock an empty PDF
        mock_pdf = mock_pdfplumber_open.return_value.__enter__.return_value
        mock_pdf.pages = []

        result = extract_text_from_pdf(self.empty_pdf_path)
        self.assertEqual(result, self.mock_empty_pdf)

    @patch("pdfplumber.open")
    def test_corrupted_pdf(self, mock_pdfplumber_open):
        # Simulate exception for corrupted PDF
        mock_pdfplumber_open.side_effect = Exception("Corrupted PDF file")

        result = extract_text_from_pdf(self.corrupted_pdf_path)
        self.assertIsNone(result)

    def test_nonexistent_file(self):
        # Test a file that does not exist
        result = extract_text_from_pdf(self.nonexistent_pdf_path)
        self.assertIsNone(result)

    @patch("pdfplumber.open")
    def test_invalid_file_type(self, mock_pdfplumber_open):
        # Simulate exception for invalid file type
        mock_pdfplumber_open.side_effect = Exception("Invalid file format")

        result = extract_text_from_pdf(self.invalid_pdf_path)
        self.assertIsNone(result)


# Helper class to mock PDF pages
class MockPage:
    def __init__(self, text, has_image=False):
        self.text = text
        self.has_image = has_image

    def extract_text(self):
        return self.text

    @property
    def images(self):
        return ["image"] if self.has_image else []


if __name__ == "__main__":
    unittest.main()
