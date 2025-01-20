from unittest.mock import Mock

import pytest

from src.invoice_parser import \
    parse_invoice_from_text  # Assuming the code is in invoice_parser.py
from src.models.invoice import Invoice


# Test valid invoice extraction with mock
def test_valid_invoice(mocker):
    invoice_text = "Invoice Reference: 287605fd-a, Beneficiary: John Doe, IBAN: DE89370400440532013000, Amount: 100.50, Currency: EUR, Due Date: 2025-01-20"

    # Create a mock response object with a model_dump method
    mock_response = Mock()
    mock_response.model_dump.return_value = {
        "reference": "287605fd-a",
        "beneficiary": "John Doe",
        "amount": 100.50,
        "currency": "EUR",
        "due_date": "2025-01-20",
    }

    # Mock the OpenAI API call to return the mock response
    mocker.patch(
        "src.invoice_parser.client.chat.completions.create", return_value=mock_response
    )

    valid_data, errors = parse_invoice_from_text(invoice_text)

    assert errors == {}
    assert valid_data["reference"] == "287605fd-a"
    assert valid_data["beneficiary"] == "John Doe"
    assert valid_data["amount"] == 100.50
    assert valid_data["currency"] == "EUR"


# Test invalid invoice reference (wrong format) with mock
def test_invalid_invoice_reference(mocker):
    invoice_text = "Invoice Reference: invalid-ref, Beneficiary: John Doe, IBAN: DE89370400440532013000, Amount: 100.50, Currency: EUR, Due Date: 2025-01-20"

    mock_response = Mock()
    mock_response.model_dump.return_value = {
        "reference": "invalid-ref",
        "beneficiary": "John Doe",
        "amount": 100.50,
        "currency": "EUR",
        "due_date": "2025-01-20",
    }

    mocker.patch(
        "src.invoice_parser.client.chat.completions.create", return_value=mock_response
    )

    valid_data, errors = parse_invoice_from_text(invoice_text)

    assert "reference" in errors
    assert "Reference must be in the format" in errors["reference"]


# Test invalid IBAN with mock
def test_invalid_iban(mocker):
    invoice_text = "Invoice Reference: 287605fd-a, Beneficiary: John Doe, IBAN: invalid_iban, Amount: 100.50, Currency: EUR, Due Date: 2025-01-20"

    mock_response = Mock()
    mock_response.model_dump.return_value = {
        "reference": "287605fd-a",
        "beneficiary": "John Doe",
        "account_id": "invalid_iban",
        "amount": 100.50,
        "currency": "EUR",
        "due_date": "2025-01-20",
    }

    mocker.patch(
        "src.invoice_parser.client.chat.completions.create", return_value=mock_response
    )

    valid_data, errors = parse_invoice_from_text(invoice_text)

    assert "account_id" in errors
    assert "Invalid IBAN" in errors["account_id"]


# Test negative amount (should be an error) with mock
def test_missing_amount(mocker):
    invoice_text = "Invoice Reference: 287605fd-a, Beneficiary: John Doe, IBAN: DE89370400440532013000, Currency: EUR, Due Date: 2025-01-20"

    mock_response = Mock()
    mock_response.model_dump.return_value = {
        "reference": "287605fd-a",
        "beneficiary": "John Doe",
        "account_id": "DE89370400440532013000",
        "currency": "EUR",
        "due_date": "2025-01-20",
        "amount": -200,
    }

    mocker.patch(
        "src.invoice_parser.client.chat.completions.create", return_value=mock_response
    )

    valid_data, errors = parse_invoice_from_text(invoice_text)

    assert "amount" in errors
    assert "Amount must be a positive number" in errors["amount"]


# Test invalid currency (non-existent currency) with mock
def test_invalid_currency(mocker):
    invoice_text = "Invoice Reference: 287605fd-a, Beneficiary: John Doe, IBAN: DE89370400440532013000, Amount: 100.50, Currency: ABC, Due Date: 2025-01-20"

    mock_response = Mock()
    mock_response.model_dump.return_value = {
        "reference": "287605fd-a",
        "beneficiary": "John Doe",
        "account_id": "DE89370400440532013000",
        "amount": 100.50,
        "currency": "ABC",  # Invalid currency
        "due_date": "2025-01-20",
    }

    mocker.patch(
        "src.invoice_parser.client.chat.completions.create", return_value=mock_response
    )

    valid_data, errors = parse_invoice_from_text(invoice_text)

    assert "currency" in errors
    assert "Invalid currency" in errors["currency"]


# Test empty beneficiary name with mock
def test_empty_beneficiary(mocker):
    invoice_text = "Invoice Reference: 287605fd-a, Beneficiary: , IBAN: DE89370400440532013000, Amount: 100.50, Currency: EUR, Due Date: 2025-01-20"

    mock_response = Mock()
    mock_response.model_dump.return_value = {
        "reference": "287605fd-a",
        "beneficiary": "",
        "account_id": "DE89370400440532013000",
        "amount": 100.50,
        "currency": "EUR",
        "due_date": "2025-01-20",
    }

    mocker.patch(
        "src.invoice_parser.client.chat.completions.create", return_value=mock_response
    )

    valid_data, errors = parse_invoice_from_text(invoice_text)

    assert "beneficiary" in errors
    assert (
        "Beneficiary name must be between 2 and 100 characters" in errors["beneficiary"]
    )
