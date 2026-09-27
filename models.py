from sqlalchemy import Column, Integer, String, Date
from database import Base

class Membro(Base):
    __tablename__ = "membros"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    contato = Column(String, nullable=True)
    data_nascimento = Column(Date, nullable=False)
    funcao = Column(String, nullable=True)
    status = Column(String, default="ativo")
    
    