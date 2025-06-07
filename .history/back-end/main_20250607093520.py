from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime
from typing import List, Any, Annotated
from pydantic import BaseModel, Field, ConfigDict, BeforeValidator
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
    allow_headers=["*"],
)

# MongoDB Atlas connection
try:
    MONGODB_URL = "mongodb+srv://byemilio2005:FdY7lYUHpZW0BDEy@practica1.lqtftek.mongodb.net/ciclismo"
    client = MongoClient(MONGODB_URL)
    db = client.ciclismo
except Exception as e:
    logger.error(f"Error connecting to MongoDB: {e}")
    raise

# ObjectId validation
def validate_object_id(v: Any) -> str:
    if isinstance(v, ObjectId):
        return str(v)
    if isinstance(v, str) and ObjectId.is_valid(v):
        return v
    raise ValueError("Invalid ObjectId")

# Update the Usuario model
class Usuario(BaseModel):
    id: Annotated[str, BeforeValidator(validate_object_id)] = Field(alias="_id", default=None)
    nombre: str
    email: str
    nivel: str
    bicicleta: str
    fecha_registro: datetime | str | None = None

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )

@app.get("/api/usuarios", response_model=List[Usuario])
async def get_usuarios():
    try:
        usuarios_cursor = db.usuarios.find()
        usuarios = []
        
        for usuario in usuarios_cursor:
            # Convert ObjectId to string
            usuario["_id"] = str(usuario["_id"])
            
            # Handle datetime
            if isinstance(usuario.get("fecha_registro"), datetime):
                usuario["fecha_registro"] = usuario["fecha_registro"].isoformat()
            
            usuarios.append(usuario)
        
        logger.info(f"Successfully retrieved {len(usuarios)} users")
        return usuarios
        
    except Exception as e:
        logger.error(f"Error retrieving users: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving users from database: {str(e)}"
        )

@app.get("/api/usuarios/{usuario_id}", response_model=Usuario)
async def get_usuario(usuario_id: str):
    try:
        usuario = db.usuarios.find_one({"_id": ObjectId(usuario_id)})
        if usuario:
            usuario["_id"] = str(usuario["_id"])
            return Usuario(**usuario)
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Usuario no encontrado: {str(e)}")