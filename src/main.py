import argparse
import json

from src.invoice_parser import parse_invoice_from_text
from src.utils import extract_text_from_pdf


def main():
    parser = argparse.ArgumentParser(
        description="Extract invoice details from a PDF file."
    )
    parser.add_argument("file_path", type=str, help="Path to the PDF file")
    args = parser.parse_args()

    # Extract text from the PDF
    invoice_text = extract_text_from_pdf(args.file_path)
    print(invoice_text)
    if not invoice_text:
        print("Failed to extract text from the PDF.")
        return

    # Parse and validate the invoice
    try:
        valid_data, errors = parse_invoice_from_text(invoice_text)
        print(json.dumps(valid_data, indent=4))
        if errors:
            print("\nErrors:")
            print(json.dumps(errors, indent=4))
    except ValueError as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
