from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import transcriptor  # importar funciones desde transcriptor.py
import datetime

app = FastAPI()

# ✅ Habilitar CORS para permitir llamadas desde el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción podés restringirlo a dominios específicos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Obtener clientes desde transcriptor.py
@app.get("/clientes_crm/")
def get_clientes():
    try:
        clientes = transcriptor.obtener_clientes()
        return clientes
    except Exception as e:
        return {"error": str(e)}

# ✅ Ruta de transcripción
@app.post("/transcribir/")
async def transcribir(file: UploadFile = File(...)):
    contents = await file.read()
    filename = f"/tmp/{file.filename}"
    with open(filename, "wb") as f:
        f.write(contents)

    texto = transcriptor.transcribir_audio(filename)
    return {"transcripcion": texto}

# ✅ Ruta de guardado
@app.post("/guardar/")
def guardar(
    cliente: str = Form(...),
    tipo: str = Form(...),
    comentario: str = Form(...),
    comercial: str = Form(...)
):
    fecha = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    mensaje, _ = transcriptor.guardar_en_sheets(fecha, cliente, tipo, comentario, comercial)
    return {"mensaje": mensaje}

from fastapi.staticfiles import StaticFiles
import os

# Ruta absoluta a la carpeta del frontend (ajustá si es necesario)
frontend_path = os.path.abspath("../frontend")

app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")
