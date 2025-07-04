from flask import Flask, jsonify
from flask_cors import CORS
import os
import gspread
from google.oauth2.service_account import Credentials

# --- Inicializar Flask ---
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": ["http://localhost:5000", "http://127.0.0.1:5000", "null"]}})

# --- Configuración de Google Sheets ---
SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']

CREDENTIALS_FILE = "credentials.json"  # Asegurate de que esté en la carpeta `backend`

clientes_data = []  # Lista global para almacenar los datos de clientes

if os.path.exists(CREDENTIALS_FILE):
    try:
        creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=SCOPES)
        client = gspread.authorize(creds)
        sheet = client.open("clientes_crm").worksheet("Hoja 1")  # Usá "Hoja 1" con espacio
        print("✅ Conectado a Google Sheets")

        # Cargar clientes desde la primera columna, omitiendo el encabezado
        clientes_data = [n.strip() for n in sheet.col_values(1)[1:] if n.strip()]
        print(f"✅ Se cargaron {len(clientes_data)} clientes")

    except Exception as e:
        print(f"❌ Error al conectar con Google Sheets: {e}")
else:
    print("❌ No se encontró el archivo credentials.json.")

# --- Endpoint para obtener los clientes ---
@app.route('/clientes_crm', methods=['GET'])
def get_clientes():
    return jsonify(clientes_data)

# --- Ejecutar servidor ---
if __name__ == '__main__':
    print("🚀 Servidor iniciado en http://127.0.0.1:5000/clientes_crm")
    app.run(port=5000, debug=False)
