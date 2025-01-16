import os
import instructor

from src.utils import extract_text_from_pdf
from openai import OpenAI
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import date
from dotenv import load_dotenv

load_dotenv()

client = instructor.from_openai(OpenAI(api_key=os.getenv("OPENAI_API_KEY")))



class Invoice(BaseModel):
    reference: Optional[str] = Field(min_length=10, max_length=10,  description="A unique ID to identify the invoice")
    beneficiary: Optional[str] = Field(description="Beneficiary name")
    account_id: Optional[str] = Field(description="The beneficiary account ID")
    amount: Optional[float] = Field(ge=0, description="Amount to send")
    currency: Optional[str] = Field(description="3 characters to identify the currency to send (e.g. EUR, USD)")
    due_date: Optional[date] = Field(description="Payment due date")

    @field_validator('currency')
    def validate_currency(cls, v):
        valid_currencies = ['USD', 'EUR', 'GBP']
        if v not in valid_currencies:
            return "Invalid"
        return v



def parse_invoice_from_text(invoice_text: str):
    return client.chat.completions.create(
        model="gpt-4o-mini",  # Use the correct model name
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
    Invoice #: gptisacam3
    Created: 2025-01-07  
    Due: 2025-01-17  
    Account #: vive la france  
    ABC Corp  
    123 Business Rd, Commerce City  
    81 avenue de la Grande Armée 75016 PARIS  
    johndoe@example.com  
    | Item    | Price |
    | Domain (1 year)   | 36 ZZZ |
    **Total: 36 EUR**
    """
    invoice = parse_invoice_from_text(invoice_text)
    print(invoice.model_dump_json(indent=2))