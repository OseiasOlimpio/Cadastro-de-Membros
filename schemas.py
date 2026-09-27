from pydantic import BaseModel
from datetime import date
from typing import Optional

class MembroCreate(BaseModel):
    nome:str
    contato:Optional[str] = None
    data_nascimento:Optional[date] = None
    funcao:Optional[str] = None
    status:Optional[str] = "ativo"

class MembroResponse(MembroCreate):
    id: int
    
    class Config:
        from_attributes = True