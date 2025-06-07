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
        # Remove id field and convert to dict
        usuario_dict = usuario.model_dump(exclude={'id'}, by_alias=True)
        
        # Update in MongoDB
        result = db.usuarios.update_one(
            {"_id": ObjectId(usuario_id)},
            {"$set": usuario_dict}
        )
        
        if result.modified_count == 0:
            logger.error(f"User with ID {usuario_id} not found")
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
            
        # Get the updated user
        updated_usuario = db.usuarios.find_one({"_id": ObjectId(usuario_id)})
        if updated_usuario:
            updated_usuario["_id"] = str(updated_usuario["_id"])
            logger.info(f"Updated user with ID: {updated_usuario['_id']}")
            return Usuario(**updated_usuario)
            
        raise HTTPException(status_code=404, detail="User update failed")
        
    except Exception as e:
        logger.error(f"Error updating user: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error updating user: {str(e)}"
        )