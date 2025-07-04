import whisper
import os
from dotenv import load_dotenv
load_dotenv()
import datetime
import gspread
from google.oauth2.service_account import Credentials
import json
import time
import torch

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

# --- Cargar modelo Whisper ---
try:
    print("⏳ Cargando modelo Whisper...")
    model = whisper.load_model("small", device="cpu")  # CPU
    print("✅ Modelo Whisper cargado correctamente. GPU disponible:", torch.cuda.is_available())
except Exception as e:
    print(f"❌ Error cargando modelo Whisper: {e}")
    model = None

# --- Lista de comerciales ---
comerciales_list = ["BENJAMIN BEN", "CRISTIAN VILLALBA", "IGNACIO GOMEZ", "MARTIN RODRÍGUEZ", "PAULA GALLETTI"]

# --- Lista de clientes desde Google Sheets ---
clientes_list = []
if sheet_clientes:
    try:
        clientes_list = [n.strip() for n in sheet_clientes.col_values(1)[1:] if n.strip()]
    except Exception as e:
        print(f"❌ Error leyendo clientes: {e}")
        clientes_list = []

# --- Funciones útiles para el backend ---
def transcribir_audio(audio_path):
    if model is None:
        return "Error: modelo no cargado"
    try:
        print("🔍 Iniciando transcripción...")
        start = time.time()
        result = model.transcribe(audio_path, language="es", fp16=False)
        duration = time.time() - start
        print(f"✅ Transcripción completada en {duration:.2f} segundos")
        return result["text"]
    except Exception as e:
        return f"❌ Error en transcripción: {e}"

def guardar_en_sheets(fecha, cliente, tipo, comentario, comercial):
    if sheet is None:
        return "❌ Error: Google Sheets no configurado.", False
    try:
        sheet.append_row([fecha, cliente, tipo, comentario, comercial])
        return "✅ Transcripción guardada correctamente.", True
    except Exception as e:
        return f"❌ Error al guardar en Google Sheets: {e}", False

def obtener_comerciales():
    return comerciales_list

def obtener_clientes():
    if sheet_clientes is None:
        return []
    try:
        clientes = sheet_clientes.col_values(1)[1:]  # omite encabezado
        return [c.strip() for c in clientes if c.strip()]
    except Exception as e:
        print(f"❌ Error al obtener clientes desde Google Sheets: {e}")
        return []


