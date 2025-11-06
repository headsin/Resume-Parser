import gspread
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv
import os
import json
import base64

# Load environment variables
load_dotenv()

# Google Sheets configuration
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

SHEET_URL = "https://docs.google.com/spreadsheets/d/1a3KSn6yDv4HdPOmEJBSap-ykatsNCPa-hkvCW1yD08g/edit?usp=sharing"

# -----------------------------------
# ✅ Load Service Account Credentials
# -----------------------------------
creds = None

# Option 1: Base64 encoded credentials (safe for GitHub)
encoded_creds = os.getenv("SERVICE_ACCOUNT_BASE64")

# Option 2: Direct JSON in .env (not recommended for deployment)
json_creds = os.getenv("SERVICE_ACCOUNT_FILE")

if encoded_creds:
    try:
        decoded_json = base64.b64decode(encoded_creds).decode()
        service_account_info = json.loads(decoded_json)
        creds = Credentials.from_service_account_info(service_account_info, scopes=SCOPES)
    except Exception as e:
        raise ValueError(f"Error decoding Base64 credentials: {e}")

elif json_creds:
    try:
        service_account_info = json.loads(json_creds)
        creds = Credentials.from_service_account_info(service_account_info, scopes=SCOPES)
    except json.JSONDecodeError:
        raise ValueError("Invalid JSON format in SERVICE_ACCOUNT_FILE. Check your .env formatting.")
else:
    raise ValueError("No valid Google credentials found. Please set SERVICE_ACCOUNT_BASE64 or SERVICE_ACCOUNT_FILE in .env")

# Connect to Google Sheets
client = gspread.authorize(creds)
sheet = client.open_by_url(SHEET_URL).sheet1

# -----------------------------------
# ✅ Utility: Check if phone already exists
# -----------------------------------
def phone_exists(phone: str) -> bool:
    """
    Checks if a phone number already exists in the Google Sheet.
    """
    if not phone:
        return False
    try:
        existing_phones = [str(row[2]).strip() for row in sheet.get_all_values()[1:] if len(row) > 2]
        return phone in existing_phones
    except Exception as e:
        raise RuntimeError(f"Error checking phone number in Google Sheet: {e}")

# -----------------------------------
# ✅ Append Resume Data Function
# -----------------------------------
def append_resume_data(data: dict):
    """
    Appends parsed resume data (dictionary) to Google Sheet.
    Expected keys:
        - name
        - role
        - phone
        - email
        - linkedin_url
        - address
        - comment (optional)
    """
    name = data.get("name", "")
    role = data.get("role", "")
    phone = data.get("phone", "")
    email = data.get("email", "")
    linkedin = data.get("linkedin_url", "")
    address = data.get("address", "")
    comment = data.get("comment", "")

    if phone_exists(phone):
        raise ValueError(f"Phone number {phone} already exists in Google Sheet.")

    try:
        sheet.append_row([name, role, phone, email, linkedin, address, comment])
        print("✅ Row added successfully to Google Sheet!")
    except Exception as e:
        raise RuntimeError(f"Error appending data to Google Sheet: {e}")
