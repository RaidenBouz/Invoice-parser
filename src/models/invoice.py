import re
from datetime import date
from typing import Optional

from pydantic import BaseModel, Field
from schwifty import IBAN

from src.constants import ALL_CURRENCIES


class Invoice(BaseModel):
    reference: Optional[str] = Field(description="A unique ID to identify the invoice")
    beneficiary: Optional[str] = Field(description="Beneficiary name")
    account_id: Optional[str] = Field(description="The beneficiary account ID (IBAN)")
    amount: Optional[float] = Field(ge=0, description="Amount to send")
    currency: Optional[str] = Field(
        description="3 characters to identify the currency to send (e.g. EUR, USD)"
    )
    due_date: Optional[date] = Field(description="Payment due date")

    @classmethod
    def validate_reference(cls, v):
        if v is None:
            return v
        pattern = re.compile(r"^[a-z0-9]{8}-[a-z]$")
        if not pattern.match(v):
            raise ValueError(
                "Reference must be in the format: 8 alphanumeric characters, a hyphen, and 1 lowercase letter (e.g., '287605fd-a')"
            )
        return v

    @classmethod
    def validate_currency(cls, v):
        if v is not None and v.upper() not in ALL_CURRENCIES:
            raise ValueError(f"Invalid currency: {v}")
        return v

    @classmethod
    def validate_amount(cls, v):
        if v is not None and v <= 0:
            raise ValueError("Amount must be a positive number")
        return v

    @classmethod
    def validate_account_id(cls, v):
        if v is not None:
            try:
                IBAN(v)
            except ValueError as e:
                raise ValueError(f"Invalid IBAN: {e}")
        return v

    @classmethod
    def validate_beneficiary(cls, v):
        if v is not None:
            v = v.strip()
            if len(v) < 2 or len(v) > 100:
                raise ValueError(
                    "Beneficiary name must be between 2 and 100 characters"
                )
            if not re.match(r"^[a-zA-Z\s\-\'\.]+$", v):
                raise ValueError("Beneficiary name contains invalid characters")
        return v
