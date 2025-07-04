import os
import json
import gspread
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv

load_dotenv()

SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']  # Intentamos con solo lectura

credentials_json_str = os.environ.get('GSPREAD_CREDENTIALS_JSON')

if not credentials_json_str:
    print("❌ No se encontró la variable GSPREAD_CREDENTIALS_JSON")
    exit()

try:
    creds_info = json.loads(credentials_json_str)
    creds = Credentials.from_service_account_info(creds_info, scopes=SCOPES)
    client = gspread.authorize(creds)

    # Intentamos abrir el archivo
    sheet = client.open("clientes_crm").worksheet("Hoja 1")
    values = sheet.col_values(1)
    
    print(f"✅ Conectado. Primeros valores de la columna A:")
    for val in values[:5]:
        print("-", val)

except Exception as e:
    print("❌ Error:", e)
