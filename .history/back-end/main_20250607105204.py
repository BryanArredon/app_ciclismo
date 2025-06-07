from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime
from typing import List, Any
from pydantic import BaseModel, Field, ConfigDict
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200", "http://localhost:53796", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# MongoDB Atlas connection
try:
    MONGODB_URL = "mongodb+srv://byemilio2005:FdY7lYUHpZW0BDEy@practica1.lqtftek.mongodb.net/ciclismo"
    client = MongoClient(MONGODB_URL)
    db = client.ciclismo
    logger.info("Connected to MongoDB successfully")
except Exception as e:
    logger.error(f"Error connecting to MongoDB: {e}")
    raise

class PyObjectId(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return str(v)

class Usuario(BaseModel):
    id: str = Field(default=None, alias="_id")
    nombre: str
    email: str
    nivel: str
    bicicleta: str
    fecha_registro: datetime | None = None

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )

class Condiciones(BaseModel):
    clima: str = Field(...)
    temperatura_c: float = Field(...)
    viento_kmh: float = Field(...)
    model_config = ConfigDict(arbitrary_types_allowed=True)

class Ruta(BaseModel):
    id: PyObjectId = Field(default=None, alias="_id")
    usuario_id: int = Field(...)
    nombre: str = Field(...)
    distancia_km: float = Field(...)
    tiempo_minutos: int = Field(...)
    fecha: datetime = Field(default_factory=datetime.now)
    elevacion_m: float = Field(...)
    equipo_usado: List[str] = Field(default_factory=list)  # Changed from str to List[str]
    notas: str = Field(default="")
    condiciones: Condiciones = Field(...)
    
    model_config = ConfigDict(
        arbitrary_types_allowed=True, 
        populate_by_name=True,
        json_encoders={ObjectId: str}
    )

class Evento(BaseModel):
    id: str = Field(default=None, alias="_id")
    nombre: str
    fecha_evento: datetime
    ubicacion: str
    tipo: str
    participantes: List[int] = []
    distancia_km: float
    organizador: str
    inscripcion_abierta: bool = True
    costo: float

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )

@app.get("/api/usuarios", response_model=List[Usuario])
async def get_usuarios():
    try:
        usuarios = []
        for usuario in db.usuarios.find():
            # Convert ObjectId to string
            usuario["_id"] = str(usuario["_id"])
            
            # Convert datetime to ISO format if present
            if isinstance(usuario.get("fecha_registro"), datetime):
                usuario["fecha_registro"] = usuario["fecha_registro"].isoformat()
                
            usuarios.append(Usuario(**usuario))
            
        logger.info(f"Retrieved {len(usuarios)} users successfully")
        return usuarios
    except Exception as e:
        logger.error(f"Error retrieving users: {e}")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@app.post("/api/usuarios", response_model=Usuario)
async def create_usuario(usuario: Usuario):
    try:
        # Remove id field and convert to dict
        usuario_dict = usuario.model_dump(exclude={'id'}, by_alias=True)
        
        # Ensure fecha_registro is set
        if not usuario_dict.get('fecha_registro'):
            usuario_dict['fecha_registro'] = datetime.now()
        
        # Insert into MongoDB
        result = db.usuarios.insert_one(usuario_dict)
        
        # Get the created user with the new ID
        created_usuario = db.usuarios.find_one({"_id": result.inserted_id})
        if created_usuario:
            created_usuario["_id"] = str(created_usuario["_id"])
            logger.info(f"Created new user with ID: {created_usuario['_id']}")
            return Usuario(**created_usuario)
        
        raise HTTPException(status_code=404, detail="User creation failed")
        
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error creating user: {str(e)}"
        )

@app.put("/api/usuarios/{usuario_id}", response_model=Usuario)
async def update_usuario(usuario_id: str, usuario: Usuario):
    try:
        # Validate ObjectId format first
        try:
            object_id = ObjectId(usuario_id)
        except Exception:
            logger.error(f"Invalid ObjectId format: {usuario_id}")
            raise HTTPException(
                status_code=400, 
                detail="ID de usuario inválido - debe ser un ObjectId válido de MongoDB"
            )

        # Convert to dict and exclude id field
        usuario_dict = {
            k: v for k, v in usuario.model_dump(by_alias=True).items() 
            if k != '_id' and v is not None
        }
        
        # Update document in MongoDB
        result = db.usuarios.find_one_and_update(
            {"_id": object_id},
            {"$set": usuario_dict},
            return_document=True
        )
        
        if not result:
            logger.error(f"User with ID {usuario_id} not found")
            raise HTTPException(
                status_code=404,
                detail="Usuario no encontrado"
            )
            
        # Convert ObjectId to string for response
        result["_id"] = str(result["_id"])
        logger.info(f"Successfully updated user with ID: {result['_id']}")
        
        return Usuario(**result)
        
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error updating user: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al actualizar usuario: {str(e)}"
        )

@app.delete("/api/usuarios/{usuario_id}")
async def delete_usuario(usuario_id: str):
    try:
        # Validate ObjectId format
        if not ObjectId.is_valid(usuario_id):
            logger.error(f"Invalid ObjectId format: {usuario_id}")
            raise HTTPException(
                status_code=400, 
                detail="ID de usuario inválido"
            )

        object_id = ObjectId(usuario_id)
        
        # Delete from MongoDB
        result = db.usuarios.delete_one({"_id": object_id})
        
        if result.deleted_count == 0:
            logger.error(f"User with ID {usuario_id} not found")
            raise HTTPException(
                status_code=404,
                detail="Usuario no encontrado"
            )
            
        logger.info(f"Successfully deleted user with ID: {usuario_id}")
        return {"message": "Usuario eliminado correctamente"}
        
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error deleting user: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al eliminar usuario: {str(e)}"
        )

@app.get("/api/eventos", response_model=List[Evento])
async def get_eventos():
    try:
        eventos = []
        for evento in db.eventos.find():
            evento["_id"] = str(evento["_id"])
            if isinstance(evento.get("fecha_evento"), datetime):
                evento["fecha_evento"] = evento["fecha_evento"].isoformat()
            eventos.append(Evento(**evento))
        logger.info(f"Retrieved {len(eventos)} events successfully")
        return eventos
    except Exception as e:
        logger.error(f"Error retrieving events: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/eventos", response_model=Evento)
async def create_evento(evento: Evento):
    try:
        evento_dict = evento.model_dump(exclude={'id'}, by_alias=True)
        result = db.eventos.insert_one(evento_dict)
        created_evento = db.eventos.find_one({"_id": result.inserted_id})
        if created_evento:
            created_evento["_id"] = str(created_evento["_id"])
            return Evento(**created_evento)
        raise HTTPException(status_code=404, detail="Event creation failed")
    except Exception as e:
        logger.error(f"Error creating event: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/eventos/{evento_id}", response_model=Evento)
async def update_evento(evento_id: str, evento: Evento):
    try:
        if not ObjectId.is_valid(evento_id):
            raise HTTPException(status_code=400, detail="Invalid event ID format")
        
        evento_dict = {k: v for k, v in evento.model_dump(by_alias=True).items() 
                      if k != '_id' and v is not None}
        
        result = db.eventos.find_one_and_update(
            {"_id": ObjectId(evento_id)},
            {"$set": evento_dict},
            return_document=True
        )
        
        if not result:
            raise HTTPException(status_code=404, detail="Event not found")
            
        result["_id"] = str(result["_id"])
        return Evento(**result)
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error updating event: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/eventos/{evento_id}")
async def delete_evento(evento_id: str):
    try:
        if not ObjectId.is_valid(evento_id):
            raise HTTPException(status_code=400, detail="Invalid event ID format")
            
        result = db.eventos.delete_one({"_id": ObjectId(evento_id)})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Event not found")
            
        return {"message": "Event deleted successfully"}
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error deleting event: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Ruta endpoints
@app.get("/api/rutas", response_model=List[Ruta])
async def get_rutas():
    try:
        rutas = []
        for ruta in db.rutas.find():
            ruta["_id"] = str(ruta["_id"])
            if isinstance(ruta.get("fecha"), datetime):
                ruta["fecha"] = ruta["fecha"].isoformat()
            rutas.append(Ruta(**ruta))
        logger.info(f"Retrieved {len(rutas)} routes successfully")
        return rutas
    except Exception as e:
        logger.error(f"Error retrieving routes: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/rutas/{ruta_id}", response_model=Ruta)
async def get_ruta(ruta_id: str):
    try:
        if not ObjectId.is_valid(ruta_id):
            raise HTTPException(status_code=400, detail="Invalid route ID")
        ruta = db.rutas.find_one({"_id": ObjectId(ruta_id)})
        if ruta is None:
            raise HTTPException(status_code=404, detail="Route not found")
        ruta["_id"] = str(ruta["_id"])
        if isinstance(ruta.get("fecha"), datetime):
            ruta["fecha"] = ruta["fecha"].isoformat()
        return Ruta(**ruta)
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error retrieving route {ruta_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/rutas", response_model=Ruta)
async def create_ruta(ruta: Ruta):
    try:
        # Convert model to dict, excluding id field
        ruta_dict = ruta.model_dump(exclude={"id"}, by_alias=True)
        
        # Ensure equipo_usado is a list
        if isinstance(ruta_dict.get("equipo_usado"), str):
            ruta_dict["equipo_usado"] = ruta_dict["equipo_usado"].split(",")
            
        # Insert into MongoDB
        result = db.rutas.insert_one(ruta_dict)
        
        # Get the created route
        created_ruta = db.rutas.find_one({"_id": result.inserted_id})
        if not created_ruta:
            raise HTTPException(status_code=404, detail="Route creation failed")
            
        # Convert ObjectId to string
        created_ruta["_id"] = str(created_ruta["_id"])
        
        # Convert datetime to ISO format
        if isinstance(created_ruta.get("fecha"), datetime):
            created_ruta["fecha"] = created_ruta["fecha"].isoformat()
            
        logger.info(f"Created new route with ID: {created_ruta['_id']}")
        return Ruta(**created_ruta)
        
    except Exception as e:
        logger.error(f"Error creating route: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al crear ruta: {str(e)}"
        )

@app.put("/api/rutas/{ruta_id}", response_model=Ruta)
async def update_ruta(ruta_id: str, ruta: Ruta):
    try:
        if not ObjectId.is_valid(ruta_id):
            raise HTTPException(status_code=400, detail="Invalid route ID")
        ruta_dict = ruta.model_dump(exclude={"id"}, by_alias=True)
        result = db.rutas.update_one(
            {"_id": ObjectId(ruta_id)},
            {"$set": ruta_dict}
        )
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Route not found")
        updated_ruta = db.rutas.find_one({"_id": ObjectId(ruta_id)})
        updated_ruta["_id"] = str(updated_ruta["_id"])
        if isinstance(updated_ruta.get("fecha"), datetime):
            updated_ruta["fecha"] = updated_ruta["fecha"].isoformat()
        logger.info(f"Updated route with ID: {ruta_id}")
        return Ruta(**updated_ruta)
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error updating route {ruta_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/rutas/{ruta_id}")
async def delete_ruta(ruta_id: str):
    try:
        if not ObjectId.is_valid(ruta_id):
            raise HTTPException(status_code=400, detail="Invalid route ID")
        result = db.rutas.delete_one({"_id": ObjectId(ruta_id)})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Route not found")
        logger.info(f"Deleted route with ID: {ruta_id}")
        return {"message": "Route deleted successfully"}
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error deleting route {ruta_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)