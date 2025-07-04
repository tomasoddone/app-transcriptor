from fastapi import FastAPI, Form
from fastapi.middleware.cors import CORSMiddleware
import transcriptor
import datetime

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/clientes_crm/")
def get_clientes():
    try:
        return transcriptor.obtener_clientes()
    except Exception as e:
        return {"error": str(e)}

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


