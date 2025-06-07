from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime
from typing import List
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
    logger.info("Successfully connected to MongoDB Atlas!")
    
    db = client.ciclismo
    # List all collections and their contents
    collections = db.list_collection_names()
    logger.info(f"Available collections: {collections}")
    for collection in collections:
        count = db[collection].count_documents({})
        logger.info(f"Collection '{collection}' has {count} documents")
        
except Exception as e:
    logger.error(f"Error connecting to MongoDB Atlas: {e}")
    raise

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, field_schema: JsonSchemaValue) -> JsonSchemaValue:
        field_schema.update(type="string")
        return field_schema

class Usuario(BaseModel):
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
        json_encoders={ObjectId: str}
    )
    
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    nombre: str = Field(...)
    email: str = Field(...)
    nivel: str = Field(...)
    bicicleta: str = Field(...)
    fecha_registro: datetime = Field(default_factory=datetime.now)

# API Endpoints
@app.get("/api/usuarios", response_model=List[Usuario])
async def get_usuarios():
    try:
        usuarios = list(db.usuarios.find())
        logger.info(f"Found {len(usuarios)} users in database")
        return [Usuario(**usuario) for usuario in usuarios]
    except Exception as e:
        logger.error(f"Error retrieving users: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/usuarios/{usuario_id}", response_model=Usuario)
async def get_usuario(usuario_id: str):
    try:
        if usuario := db.usuarios.find_one({"_id": ObjectId(usuario_id)}):
            return Usuario(**usuario)
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Usuario no encontrado: {str(e)}")

@app.post("/api/usuarios", response_model=Usuario)
async def create_usuario(usuario: Usuario):
    usuario_dict = {k: v for k, v in usuario.model_dump(by_alias=True).items() if k != "_id"}
    result = db.usuarios.insert_one(usuario_dict)
    created_usuario = db.usuarios.find_one({"_id": result.inserted_id})
    return Usuario(**created_usuario)

@app.put("/api/usuarios/{usuario_id}", response_model=Usuario)
async def update_usuario(usuario_id: str, usuario: Usuario):
    try:
        usuario_dict = {k: v for k, v in usuario.model_dump(by_alias=True).items() if k != "_id"}
        result = db.usuarios.update_one(
            {"_id": ObjectId(usuario_id)},
            {"$set": usuario_dict}
        )
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        updated_usuario = db.usuarios.find_one({"_id": ObjectId(usuario_id)})
        return Usuario(**updated_usuario)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error actualizando usuario: {str(e)}")

@app.delete("/api/usuarios/{usuario_id}")
async def delete_usuario(usuario_id: str):
    try:
        result = db.usuarios.delete_one({"_id": ObjectId(usuario_id)})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        return {"message": "Usuario eliminado"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error eliminando usuario: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)