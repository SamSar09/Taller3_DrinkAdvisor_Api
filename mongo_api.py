from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from datetime import datetime
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

client = MongoClient(os.environ["MONGO_URI"])

db = client["ISIS2304A24202620"]


@app.get("/")
def inicio():
    return {"estado": "API funcionando correctamente"}

@app.get('/bares/{bar_id}/comentarios')
def get_comentarios(bar_id: int):
    comentarios = list(db['comentarios_bares'].find({'bar_id': bar_id}, {'_id': 0}).sort('fecha', -1))
    return comentarios

@app.post('/bares/{bar_id}/comentarios')
def post_comentario(bar_id: int, datos: dict):
    datos['bar_id'] = bar_id
    datos['fecha']  = datetime.now().isoformat()

    if 'calificacion' in datos:
        try:
            datos['calificacion'] = int(datos['calificacion'])
        except (TypeError, ValueError):
            raise HTTPException(status_code=400, detail="calificacion debe ser un entero")
        if not 1 <= datos['calificacion'] <= 5:
            raise HTTPException(status_code=400, detail="calificacion debe estar entre 1 y 5")

    db['comentarios_bares'].insert_one(datos)
    return {'mensaje': 'Comentario guardado'}

@app.get('/bares/{bar_id}/eventos')
def get_eventos(bar_id: int):
    eventos = list(db['eventos'].find({'bar_id': bar_id}, {'_id': 0}).sort('fecha_creacion', -1))
    return eventos

@app.post('/bares/{bar_id}/eventos')
def post_evento(bar_id: int, datos: dict):
    if not str(datos.get('nombre', '')).strip():
        raise HTTPException(status_code=400, detail="El evento debe tener nombre")
    datos = {k: v for k, v in datos.items() if v not in (None, "")}

    datos['bar_id'] = bar_id
    datos['fecha_creacion'] = datetime.now().isoformat()
    db['eventos'].insert_one(datos)
    return {'mensaje': 'Evento guardado'}
