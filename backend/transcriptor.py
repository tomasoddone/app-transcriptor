import os
from dotenv import load_dotenv
load_dotenv()

import gspread
from google.oauth2.service_account import Credentials
import json

# --- Configuración Google Sheets ---
SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
credentials_json_str = os.environ.get('GSPREAD_CREDENTIALS_JSON')

if credentials_json_str:
    try:
        creds_info = json.loads(credentials_json_str)
        creds = Credentials.from_service_account_info(creds_info, scopes=SCOPES)
        client = gspread.authorize(creds)
        sheet = client.open("crm_audio_transcriptions").sheet1
        sheet_clientes = client.open("clientes_crm").sheet1
        print("✅ Google Sheets autorizado correctamente")
    except Exception as e:
        print(f"❌ Error al configurar Google Sheets: {e}")
        sheet = None
        sheet_clientes = None
else:
    print("⚠️ No se encontró la variable de entorno 'GSPREAD_CREDENTIALS_JSON'")
    sheet = None
    sheet_clientes = None

# --- Funciones útiles ---
def guardar_en_sheets(fecha, cliente, tipo, comentario, comercial):
    if sheet is None:
        return "❌ Error: Google Sheets no configurado.", False
    try:
        sheet.append_row([fecha, cliente, tipo, comentario, comercial])
        return "✅ Transcripción guardada correctamente.", True
    except Exception as e:
        return f"❌ Error al guardar en Google Sheets: {e}", False

def obtener_clientes():
    if sheet_clientes is None:
        return []
    try:
        clientes = sheet_clientes.col_values(1)[1:]  # omite encabezado
        return [c.strip() for c in clientes if c.strip()]
    except Exception as e:
        print(f"❌ Error al obtener clientes desde Google Sheets: {e}")
        return []
