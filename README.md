Here’s the complete **`README.md` file code** for the **Invoice Parser** project, including all the documentation:

```markdown
# Invoice Parser

## Description

This project extracts and validates invoice details from PDF files. The extracted data is parsed and validated using `instructor` for field validation, and errors are displayed if any required fields are missing or invalid.

## Requirements

- Python 3.x
- `argparse`, `pydantic`, `openai`, `instructor`, `python-dotenv`, `pdfminer.six`

Install dependencies:

```bash
pip install -r requirements.txt
```

## Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/invoice-parser.git
   ```

2. Install the required packages:

   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file with your OpenAI API key:

   ```
   OPENAI_API_KEY=your_openai_api_key
   ```

## Usage

Run the script by providing the path to a PDF file:

```bash
python main.py <file_path>
```

Example:

```bash
python main.py ./invoices/invoice1.pdf
```

### Output

The script outputs the parsed invoice data as JSON, along with any validation errors.

```json
{
    "reference": "287605fd-a",
    "beneficiary": "John Doe",
    "account_id": "DE89370400440532013000",
    "amount": 100.50,
    "currency": "EUR",
    "due_date": "2025-01-20"
}
```

## Testing



1. Run the tests:

   ```bash
   pytest
   ```

## License

This project is licensed under the MIT License.
```