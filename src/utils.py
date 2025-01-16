import logging

import pdfplumber


def extract_text_from_pdf(file_path):
    """
    Extracts text from a PDF file. Logs a warning if images are detected in the PDF.

    Args:
        file_path (str): Path to the PDF file.

    Returns:
        str: Extracted text or None if an error occurs.
    """
    try:
        with pdfplumber.open(file_path) as pdf:
            extracted_text = []
            images_found = False

            for page in pdf.pages:
                # Check for images on the page
                if page.images:
                    images_found = True

                # Extract text from the page
                text = page.extract_text()
                if text:
                    extracted_text.append(text)

            # Log a warning if images are found
            if images_found:
                logging.warning("Warning: PDF contains images.")

            return "".join(extracted_text)
    except FileNotFoundError:
        logging.error(f"File not found: {file_path}")
        return None
    except Exception as e:
        logging.error(f"An error occurred while processing the PDF: {e}")
        return None
