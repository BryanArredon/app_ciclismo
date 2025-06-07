from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from bson import ObjectId
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field

app = FastAPI()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB Atlas connection with error handling
try:
    MONGODB_URL = "mongodb+srv://byemilio2005:FdY7lYUHpZW0BDEy@practica1.lqtftek.mongodb.net/ciclismo"
    client = MongoClient(MONGODB_URL)
    # Test the connection
    client.admin.command('ping')
    print("Connected successfully to MongoDB Atlas!")
    db = client.ciclismo  # Explicitly select the 'ciclismo' database
    
    # Test if we can access the collections
    print("Available collections:", db.list_collection_names())
    
except ConnectionFailure as e:
    print(f"Could not connect to MongoDB Atlas: {e}")
    raise

# Initialize database with sample data
def init_db():
    try:
        # Check if collections are empty
        if db.usuarios.count_documents({}) == 0:
            usuario = {
                "_id": 100,
                "nombre": "Carlos Méndez",
                "email": "carlos@gmail.com",
                "nivel": "intermedio",
                "bicicleta": "Montaña",
                "fecha_registro": datetime(2023, 1, 15)
            }
            db.usuarios.insert_one(usuario)
            print("Sample user inserted")

        if db.rutas.count_documents({}) == 0:
            ruta = {
                "usuario_id": 100,
                "nombre": "Ruta del Lago",
                "distancia_km": 42.5,
                "tiempo_minutos": 125,
                "fecha": datetime(2023, 5, 10),
                "elevacion_m": 350,
                "equipo_usado": ["casco", "guantes"],
                "notas": "Excelente recorrido, paré a mitad para tomar agua",
                "condiciones": {
                    "clima": "soleado",
                    "temperatura_c": 22,
                    "viento_kmh": 15
                }
            }
            db.rutas.insert_one(ruta)
            print("Sample route inserted")

        if db.eventos.count_documents({}) == 0:
            evento = {
                "nombre": "Gran Fondo de Primavera",
                "fecha_evento": datetime(2023, 6, 15),
                "ubicacion": "Parque Central",
                "tipo": "competencia",
                "participantes": [],
                "distancia_km": 50,
                "organizador": "Club Ciclista Local",
                "inscripcion_abierta": True,
                "costo": 200
            }
            db.eventos.insert_one(evento)
            print("Sample event inserted")

    except Exception as e:
        print(f"Error initializing database: {e}")

# Add this after the try-except block for MongoDB connection
if client:
    init_db()

# Pydantic models
class CondicionesRuta(BaseModel):
    clima: str
    temperatura_c: float
    viento_kmh: float

class Usuario(BaseModel):
    id: Optional[str] = Field(alias="_id")
    nombre: str
    email: str
    nivel: str
    bicicleta: str
    fecha_registro: datetime

    class Config:
        allow_population_by_field_name = True

class Ruta(BaseModel):
    id: Optional[str] = Field(alias="_id")
    usuario_id: str
    nombre: str
    distancia_km: float
    tiempo_minutos: int
    fecha: datetime
    elevacion_m: float
    equipo_usado: List[str]
    notas: str
    condiciones: CondicionesRuta

    class Config:
        allow_population_by_field_name = True

class Evento(BaseModel):
    id: Optional[str] = Field(alias="_id")
    nombre: str
    fecha_evento: datetime
    ubicacion: str
    tipo: str
    participantes: List[str]
    distancia_km: float
    organizador: str
    inscripcion_abierta: bool
    costo: float

    class Config:
        allow_population_by_field_name = True

# Helper functions
def parse_obj_id(id: str) -> ObjectId:
    try:
        return ObjectId(id)
    except:
        raise HTTPException(status_code=400, detail="Invalid ID format")

# Usuario endpoints
@app.get("/api/usuarios", response_model=List[Usuario])
async def get_usuarios():
    usuarios = list(db.usuarios.find())
    return usuarios

@app.get("/api/usuarios/{usuario_id}", response_model=Usuario)
async def get_usuario(usuario_id: str):
    usuario = db.usuarios.find_one({"_id": parse_obj_id(usuario_id)})
    if usuario is None:
        raise HTTPException(status_code=404, detail="Usuario not found")
    return usuario

@app.post("/api/usuarios", response_model=Usuario)
async def create_usuario(usuario: Usuario):
    usuario_dict = usuario.dict(exclude={"id"})
    result = db.usuarios.insert_one(usuario_dict)
    created_usuario = db.usuarios.find_one({"_id": result.inserted_id})
    return created_usuario

@app.put("/api/usuarios/{usuario_id}", response_model=Usuario)
async def update_usuario(usuario_id: str, usuario: Usuario):
    usuario_dict = usuario.dict(exclude={"id"}, exclude_unset=True)
    result = db.usuarios.update_one(
        {"_id": parse_obj_id(usuario_id)},
        {"$set": usuario_dict}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Usuario not found")
    updated_usuario = db.usuarios.find_one({"_id": parse_obj_id(usuario_id)})
    return updated_usuario

@app.delete("/api/usuarios/{usuario_id}")
async def delete_usuario(usuario_id: str):
    result = db.usuarios.delete_one({"_id": parse_obj_id(usuario_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Usuario not found")
    return {"message": "Usuario deleted"}

# Ruta endpoints
@app.get("/api/rutas", response_model=List[Ruta])
async def get_rutas():
    rutas = list(db.rutas.find())
    return rutas

@app.get("/api/rutas/{ruta_id}", response_model=Ruta)
async def get_ruta(ruta_id: str):
    ruta = db.rutas.find_one({"_id": parse_obj_id(ruta_id)})
    if ruta is None:
        raise HTTPException(status_code=404, detail="Ruta not found")
    return ruta

@app.post("/api/rutas", response_model=Ruta)
async def create_ruta(ruta: Ruta):
    ruta_dict = ruta.dict(exclude={"id"})
    result = db.rutas.insert_one(ruta_dict)
    created_ruta = db.rutas.find_one({"_id": result.inserted_id})
    return created_ruta

@app.put("/api/rutas/{ruta_id}", response_model=Ruta)
async def update_ruta(ruta_id: str, ruta: Ruta):
    ruta_dict = ruta.dict(exclude={"id"}, exclude_unset=True)
    result = db.rutas.update_one(
        {"_id": parse_obj_id(ruta_id)},
        {"$set": ruta_dict}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Ruta not found")
    updated_ruta = db.rutas.find_one({"_id": parse_obj_id(ruta_id)})
    return updated_ruta

@app.delete("/api/rutas/{ruta_id}")
async def delete_ruta(ruta_id: str):
    result = db.rutas.delete_one({"_id": parse_obj_id(ruta_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Ruta not found")
    return {"message": "Ruta deleted"}

# Evento endpoints
@app.get("/api/eventos", response_model=List[Evento])
async def get_eventos():
    eventos = list(db.eventos.find())
    return eventos

@app.get("/api/eventos/{evento_id}", response_model=Evento)
async def get_evento(evento_id: str):
    evento = db.eventos.find_one({"_id": parse_obj_id(evento_id)})
    if evento is None:
        raise HTTPException(status_code=404, detail="Evento not found")
    return evento

@app.post("/api/eventos", response_model=Evento)
async def create_evento(evento: Evento):
    evento_dict = evento.dict(exclude={"id"})
    result = db.eventos.insert_one(evento_dict)
    created_evento = db.eventos.find_one({"_id": result.inserted_id})
    return created_evento

@app.put("/api/eventos/{evento_id}", response_model=Evento)
async def update_evento(evento_id: str, evento: Evento):
    evento_dict = evento.dict(exclude={"id"}, exclude_unset=True)
    result = db.eventos.update_one(
        {"_id": parse_obj_id(evento_id)},
        {"$set": evento_dict}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Evento not found")
    updated_evento = db.eventos.find_one({"_id": parse_obj_id(evento_id)})
    return updated_evento

@app.delete("/api/eventos/{evento_id}")
async def delete_evento(evento_id: str):
    result = db.eventos.delete_one({"_id": parse_obj_id(evento_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Evento not found")
    return {"message": "Evento deleted"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)