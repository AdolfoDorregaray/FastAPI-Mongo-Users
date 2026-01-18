from fastapi import FastAPI, HTTPException, Request, Form, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI(title="SGA - Gestión de Usuarios")
templates = Jinja2Templates(directory="templates")

# --- CONFIGURACIÓN DE MONGODB ATLAS ---
MONGO_URI = "mongodb+srv://adolfojesus2000_db_user:ADJdrh_0620%23%40@userproject.tiqqk1k.mongodb.net/?appName=UserProject"

client = MongoClient(MONGO_URI)
db = client.academia_db
users_collection = db.users

@app.get("/", response_class=HTMLResponse)
async def web_index(request: Request, search: Optional[str] = Query(None), error: Optional[str] = Query(None)):
    query = {}
    if search:
        search_term = search.strip()
        query = {
            "$or": [
                {"nombre": {"$regex": search_term, "$options": "i"}},
                {"apellidos": {"$regex": search_term, "$options": "i"}},
                {"dni": {"$regex": search_term, "$options": "i"}},
                {"$expr": {
                    "$regexMatch": {
                        "input": {"$concat": ["$nombre", " ", "$apellidos"]},
                        "regex": search_term,
                        "options": "i"
                    }
                }}
            ]
        }
    usuarios = list(users_collection.find(query).sort("created", -1))
    return templates.TemplateResponse("index.html", {"request": request, "usuarios": usuarios, "error": error})

@app.post("/web/crear")
async def web_crear(nombre: str = Form(...), apellidos: str = Form(...), dni: str = Form(...), fecha_nacimiento: str = Form(...)):
    if users_collection.find_one({"dni": dni}):
        return RedirectResponse(url="/?error=dni_duplicado", status_code=303)
    ahora = datetime.now()
    users_collection.insert_one({
        "nombre": nombre, "apellidos": apellidos, "dni": dni,
        "fecha_nacimiento": fecha_nacimiento, "created": ahora, "updated": ahora
    })
    return RedirectResponse(url="/", status_code=303)

@app.post("/web/editar/{user_id}")
async def web_editar(user_id: str, nombre: str = Form(...), apellidos: str = Form(...), dni: str = Form(...)):
    users_collection.update_one(
        {"_id": ObjectId(user_id)}, 
        {"$set": {"nombre": nombre, "apellidos": apellidos, "dni": dni, "updated": datetime.now()}}
    )
    return RedirectResponse(url="/", status_code=303)

@app.get("/web/eliminar/{user_id}")
async def web_eliminar(user_id: str):
    users_collection.delete_one({"_id": ObjectId(user_id)})
    return RedirectResponse(url="/", status_code=303)