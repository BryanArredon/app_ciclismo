from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime
from typing import List, Any, Optional
from pydantic import BaseModel, Field, ConfigDict

app = FastAPI()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB Atlas connection
MONGODB_URL = "mongodb+srv://byemilio2005:FdY7lYUHpZW0BDEy@practica1.lqtftek.mongodb.net/ciclismo"
client = MongoClient(MONGODB_URL)
db = client.ciclismo

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
    def __get_pydantic_json_schema__(cls, field_schema: Any) -> Any:
        field_schema.update(type="string")
        return field_schema

# Pydantic models
class Usuario(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True, populate_by_name=True)
    
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    nombre: str = Field(...)
    email: str = Field(...)
    nivel: str = Field(...)
    bicicleta: str = Field(...)
    fecha_registro: datetime = Field(default_factory=datetime.now)

    def dict(self, *args, **kwargs):
        if kwargs.get("by_alias", True):
            return {
                "_id": str(self.id),
                "nombre": self.nombre,
                "email": self.email,
                "nivel": self.nivel,
                "bicicleta": self.bicicleta,
                "fecha_registro": self.fecha_registro
            }
        return super().dict(*args, **kwargs)

# Usuario endpoints
@app.get("/api/usuarios", response_model=List[Usuario])
async def get_usuarios():
    usuarios = list(db.usuarios.find())
    return [Usuario(**usuario) for usuario in usuarios]

@app.get("/api/usuarios/{usuario_id}", response_model=Usuario)
async def get_usuario(usuario_id: str):
    try:
        usuario = db.usuarios.find_one({"_id": ObjectId(usuario_id)})
        if usuario:
            return Usuario(**usuario)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Usuario no encontrado: {str(e)}")
    raise HTTPException(status_code=404, detail="Usuario no encontrado")

@app.post("/api/usuarios", response_model=Usuario)
async def create_usuario(usuario: Usuario):
    usuario_dict = usuario.dict(by_alias=True)
    del usuario_dict["_id"]  # Remove _id for insertion
    result = db.usuarios.insert_one(usuario_dict)
    created_usuario = db.usuarios.find_one({"_id": result.inserted_id})
    return Usuario(**created_usuario)

@app.put("/api/usuarios/{usuario_id}", response_model=Usuario)
async def update_usuario(usuario_id: str, usuario: Usuario):
    try:
        usuario_dict = usuario.dict(by_alias=True)
        del usuario_dict["_id"]  # Remove _id for update
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