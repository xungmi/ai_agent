import json
import sys
import os
import sqlite3
import google.generativeai as genai

from pypdf import PdfReader
from dotenv import load_dotenv
import requests
import logging
from pydantic import BaseModel, Field


# --- Setup logging ---
logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%H:%M:%S"
)



# ========== Pydantic models ==========
class Vendor(BaseModel):
    name: str = Field(...,
                      description="The name of the vendor or company issuing the invoice.")
    address: str = Field(..., description="The address of the vendor.")
    taxId: str = Field(...,
                       description="The tax identification number of the vendor.")


class Customer(BaseModel):
    name: str = Field(..., description="The name of the customer or client.")
    address: str = Field(..., description="The address of the customer.")
    taxId: str = Field(...,
                       description="The tax identification number of the customer.")


class Invoice(BaseModel):
    vendor: Vendor = Field(...,
                           description="Details of the vendor issuing the invoice.")
    customer: Customer = Field(...,
                               description="Details of the customer receiving the invoice.")
    invoiceNumber: str = Field(...,
                               description="Unique identifier for the invoice.")
    date: str = Field(..., description="Date when the invoice was issued.")
    totalAmount: float = Field(...,
                               description="Total amount due on the invoice.")
    tax: float = Field(...,
                       description="Total tax amount applied to the invoice.")
    

# ========== DB ==========
def setup_database():
    conn = sqlite3.connect("invoices.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS invoices (
            id INTEGER PRIMARY KEY,
            vendor_name TEXT,
            vendor_address TEXT,
            vendor_tax_id TEXT,
            customer_name TEXT,
            customer_address TEXT,
            customer_tax_id TEXT,
            invoice_number TEXT,
            date TEXT,
            total_amount REAL,
            tax REAL
        )
    ''')
    conn.commit()
    return conn


def insert_invoice_data(conn, invoice_obj):
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO invoices (
            vendor_name, vendor_address, vendor_tax_id,
            customer_name, customer_address, customer_tax_id,
            invoice_number, "date", total_amount, tax
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        invoice_obj.vendor.name,
        invoice_obj.vendor.address,
        invoice_obj.vendor.taxId,
        invoice_obj.customer.name,
        invoice_obj.customer.address,
        invoice_obj.customer.taxId,
        invoice_obj.invoiceNumber,
        invoice_obj.date,
        invoice_obj.totalAmount,
        invoice_obj.tax
    ))
    conn.commit()


# --- Define JSON Schema ---
INVOICE_RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "vendor": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Vendor name"},
                "address": {"type": "string", "description": "Vendor address"},
                "taxId": {"type": "string", "description": "Vendor tax ID"}
            },
            "required": ["name", "address", "taxId"]
        },
        "customer": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Customer name"},
                "address": {"type": "string", "description": "Customer address"},
                "taxId": {"type": "string", "description": "Customer tax ID"}
            },
            "required": ["name", "address", "taxId"]
        },
        "invoiceNumber": {"type": "string", "description": "Invoice ID"},
        "date": {"type": "string", "description": "Invoice date"},
        "totalAmount": {"type": "number", "description": "Total amount"},
        "tax": {"type": "number", "description": "Tax amount"}
    },
    "required": ["vendor", "customer", "invoiceNumber", "date", "totalAmount", "tax"]
}


# ========== Gemini ==========
def load_api_key() -> str:
    logging.info("🔑 Loading API key...")
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        logging.error("🔴 GEMINI_API_KEY not found in .env")
        raise ValueError("⚠️ GEMINI_API_KEY is not configured in .env")
    logging.info("🟢 API key loaded successfully")
    return api_key


def configure_genai(api_key: str):
    logging.info("⚙️ Configuring Gemini client...")
    genai.configure(api_key=api_key)
    logging.info("🟢 Gemini client configured")


# ========== PDF ==========
def get_pdf_content(pdf_path: str) -> str:
    with open(pdf_path, "rb") as f:
        reader = PdfReader(f)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
    return text


def extract_invoice_details(pdf_content: str) -> Invoice:
    prompt = f"""
    You are an expert data extractor who excels at analyzing invoices.

    Extract all relevant data from the below invoice content (which was extracted from a PDF document).
    Make sure to capture data like vendor name, date, amount, tax, tax IDs etc.

    <invoice-content>
    {pdf_content}
    </invoice-content>

    Return your response as a JSON object without any extra text or explanation.
    """
    
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        generation_config={
            "response_schema": INVOICE_RESPONSE_SCHEMA,
            "response_mime_type": "application/json",
        }
    )
    response = model.generate_content(prompt)
    logging.info("🟢 Response received from Gemini API")
    invoice_dict = json.loads(response.text)
    invoice_obj = Invoice(**invoice_dict)
    return invoice_obj


def main():
    api_key = load_api_key()
    configure_genai(api_key)
    
    if len(sys.argv) < 2:
        print("Usage: python main.py /path/to/file_or_folder")
        return
    
    path = sys.argv[1]
    pdf_files = []
    
    if not os.path.exists(path):
        print(f"Error: The path '{path}' does not exist.")
        return
    
    if os.path.isfile(path):
        if path.lower().endswith(".pdf"):
            pdf_files.append(path)
        else:
            print(f"Error: The file '{path}' is not a PDF file.")
            return
    elif os.path.isdir(path):
        for filename in os.listdir(path):
            if filename.lower().endswith(".pdf"):
                pdf_files.append(os.path.join(path, filename))
                
    if not pdf_files:
        print("No PDF files found.")
        return

    conn = setup_database()
    

    for pdf_file in pdf_files:
        print(f"Processing {pdf_file}...")
        try:
            pdf_content = get_pdf_content(pdf_file)
            invoices = extract_invoice_details(pdf_content)
            insert_invoice_data(conn, invoices)
            print("Extracted Invoice Details:")
            print(invoices.model_dump())
        except Exception as e:
            print(f"An error occurred while processing {pdf_file}: {e}")

    conn.close()
    

if __name__ == "__main__":
    main()



