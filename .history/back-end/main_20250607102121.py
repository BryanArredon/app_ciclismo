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
    clima: str
    temperatura_c: float
    viento_kmh: float

class Ruta(BaseModel):
    id: str = Field(default=None, alias="_id")
    usuario_id: int
    nombre: str
    distancia_km: float
    tiempo_minutos: int
    fecha: datetime
    elevacion_m: float
    equipo_usado: List[str]
    notas: str | None = None
    condiciones: Condiciones

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
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