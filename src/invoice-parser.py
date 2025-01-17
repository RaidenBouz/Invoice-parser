import os
import instructor
import re

from schwifty import IBAN
from src.constants import ALL_CURRENCIES
from src.utils import extract_text_from_pdf
from openai import OpenAI
from pydantic import BaseModel, Field, field_validator, ValidationError, ValidationInfo
from typing import Optional
from datetime import date
from dotenv import load_dotenv

load_dotenv()

client = instructor.from_openai(OpenAI(api_key=os.getenv("OPENAI_API_KEY")))



class Invoice(BaseModel):
    reference: Optional[str] = Field( description="A unique ID to identify the invoice")
    beneficiary: Optional[str] = Field(description="Beneficiary name")
    account_id: Optional[str] = Field(description="The beneficiary account ID (IBAN)")
    amount: Optional[float] = Field(ge=0, description="Amount to send")
    currency: Optional[str] = Field(description="3 characters to identify the currency to send (e.g. EUR, USD)")
    due_date: Optional[date] = Field(description="Payment due date")

    
    @field_validator('reference')
    @classmethod
    def validate_reference(cls, v):
        if v is None:
            return v
        # Regex pattern: 8 alphanumeric characters, a hyphen, and 1 lowercase letter
        pattern = re.compile(r'^[a-z0-9]{8}-[a-z]$')
        if not pattern.match(v):
            raise ValueError("Reference must be in the format: 8 alphanumeric characters, a hyphen, and 1 lowercase letter (e.g., '287605fd-a')")
        return v
    
    
    @field_validator('currency')
    @classmethod
    def validate_currency(cls, v):
        if v not in ALL_CURRENCIES:
            return "Invalid"
        return v
    
    @field_validator('amount')
    @classmethod
    def validate_amount(cls, v):
        if v is not None:
            # Ensure the amount is non-negative
            if v <= 0:
                raise ValueError("Amount must be a non-negative number")
            
            # Ensure the amount is a valid decimal number
            if not isinstance(v, (float, int)):
                raise ValueError("Amount must be a valid decimal number")
        
        return v
    
    @field_validator('account_id')
    @classmethod
    def validate_iban(cls, v):
        if v is not None:
            try:
                # Validate the IBAN using schwifty
                IBAN(v)
            except ValueError as e:
                raise ValueError(f"Invalid IBAN: {e}")
        return v
    
    @field_validator('beneficiary')
    def validate_beneficiary(cls, v):
        if v is not None:
            # Trim leading and trailing whitespace
            v = v.strip()
            
            # Check minimum and maximum length
            if len(v) < 2 or len(v) > 100:
                raise ValueError("Beneficiary name must be between 2 and 100 characters")
            
            # Check for allowed characters (letters, spaces, hyphens, apostrophes, and periods)
            if not re.match(r'^[a-zA-Z\s\-\'\.]+$', v):
                raise ValueError("Beneficiary name can only contain letters, spaces, hyphens, apostrophes, and periods")
            
            # Ensure the name contains at least one letter (to prevent numbers or meaningless strings)
            if not re.search(r'[a-zA-Z]', v):
                raise ValueError("Beneficiary name must contain at least one letter")
        
        return v



def parse_invoice_from_text(invoice_text: str):
    return client.chat.completions.create(
        model="gpt-4o-mini",
        max_retries=2,
        response_model=Invoice,
        messages=[
            {
                "role": "system",
                "content": "You are a data extraction system that extracts invoice details from text. "
            },

            {
                "role": "user",
                "content": f"Extract the invoice details from this text: {invoice_text}",
            },
        ],
    )



if __name__ == "__main__":
    # Example usage
    invoice_text = """
    Invoice #: 287605fd-a
    Created: 2025-01-07  
    Due: 2025-01-17  
    Account #: FR7630006000011234567890189  
    ABC Inc  
    123 Business Rd, Commerce City  
    81 avenue de la Grande Armée 75016 PARIS  
    johndoe@example.com  
    | Item    | Price |
    | Domain (1 year)   | 8 EUR |
    **Total: -8 EUR**
    """
    try:
        invoice = parse_invoice_from_text(invoice_text)
        print(invoice.model_dump_json(indent=2))
    except ValidationError as e:
        print(f"Validation Error: {e}")