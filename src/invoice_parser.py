import os
from typing import Tuple

import instructor
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import ValidationError

from src.models.invoice import Invoice

load_dotenv()

# Initialize OpenAI instructor
client = instructor.from_openai(OpenAI(api_key=os.getenv("OPENAI_API_KEY")))


def parse_invoice_from_text(invoice_text: str):
    """Parse invoice details from text using OpenAI and validate partially."""
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            max_retries=2,
            response_model=Invoice,
            messages=[
                {
                    "role": "system",
                    "content": "You are a data extraction system that extracts invoice details from text.",
                },
                {
                    "role": "user",
                    "content": f"Extract the invoice details from this text: {invoice_text}",
                },
            ],
        )
        extracted_data = response.model_dump()

        # Validate fields partially
        valid_data, errors = validate_invoice_partially(extracted_data)

        return valid_data, errors

    except ValidationError as e:
        # If OpenAI returns an invalid response model
        raise ValueError(f"OpenAI Response Validation Error: {e}")


def validate_invoice_partially(data: dict) -> Tuple[dict, dict]:
    """
    Validate the extracted invoice data partially.
    :param data: Dictionary containing extracted invoice fields.
    :return: Tuple of (valid_data, errors).
    """
    valid_data = {}
    errors = {}

    for field, value in data.items():
        try:
            # Dynamically call the field's validator if it exists
            if hasattr(Invoice, f"validate_{field}"):
                validate_method = getattr(Invoice, f"validate_{field}")
                valid_data[field] = validate_method(value)
            else:
                # If no custom validator, accept the value as-is
                valid_data[field] = value
        except Exception as e:
            errors[field] = str(e)

    return valid_data, errors
