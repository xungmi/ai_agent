import json
import sys
import os
import sqlite3
import google.generativeai as genai

from pypdf import PdfReader
from dotenv import load_dotenv
import requests
import logging


# --- Setup logging ---
logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%H:%M:%S"
)


# --- Setup database ---
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

# --- Define JSON Schema ---
invoice_schema = {
    "type": "object",
    "properties": {
        "vendor": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Vendor name"},
                "address": {"type": "string", "description": "Vendor address"},
                "taxId": {"type": "string", "description": "Vendor tax ID"},
            },
            "required": ["name", "address", "taxId"]
        },
        "customer": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Customer name"},
                "address": {"type": "string", "description": "Customer address"},
                "taxId": {"type": "string", "description": "Customer tax ID"},
            },
            "required": ["name", "address", "taxId"]
        },
        "invoiceNumber": {"type": "string", "description": "Invoice ID"},
        "date": {"type": "string", "description": "Invoice date"},
        "totalAmount": {"type": "number", "description": "Total amount"},
        "tax": {"type": "number", "description": "Tax amount"},
    },
    "required": ["vendor", "customer", "invoiceNumber", "date", "totalAmount", "tax"]
}

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


def get_pdf_content(pdf_path: str) -> str:
    with open(pdf_path, "rb") as f:
        reader = PdfReader(f)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
    return text


def extract_invoice_details(pdf_content: str) -> dict:
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
            "response_schema": invoice_schema,
            "response_mime_type": "application/json",
        }
    )
    response = model.generate_content(prompt)
    logging.info("🟢 Response received from Gemini API")
    return response.text


def insert_invoice_data(conn, invoice_data):
    invoice_data = json.loads(invoice_data) # parse str to dict
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO invoices (
            vendor_name, vendor_address, vendor_tax_id,
            customer_name, customer_address, customer_tax_id,
            invoice_number, "date", total_amount, tax
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        invoice_data.get("vendor", {}).get("name"),
        invoice_data.get("vendor", {}).get("address"),
        invoice_data.get("vendor", {}).get("taxId"),
        invoice_data.get("customer", {}).get("name"),
        invoice_data.get("customer", {}).get("address"),
        invoice_data.get("customer", {}).get("taxId"),
        invoice_data.get("invoiceNumber"),
        invoice_data.get("date"),
        invoice_data.get("totalAmount"),
        invoice_data.get("tax")
    ))
    conn.commit()
    
    

    
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
            invoice_details = extract_invoice_details(pdf_content)
            insert_invoice_data(conn, invoice_details)
            print("Extracted Invoice Details:")
            print(invoice_details)
        except Exception as e:
            print(f"An error occurred while processing {pdf_file}: {e}")

    conn.close()
    

if __name__ == "__main__":
    main()