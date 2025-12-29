from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class TipoUsuario(PyEnum):
    MEDICO = "MEDICO"
    CLINICA = "CLINICA"
    PACIENTE = "PACIENTE"


class StatusExame(PyEnum):
    PENDENTE = "PENDENTE"
    LAUDADO = "LAUDADO"


class Usuarios(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    tipo = Column(Enum(TipoUsuario), nullable=False)
    rqe = Column(String)

    laudos = relationship("Laudos", back_populates="medico")


class Exames(Base):
    __tablename__ = "exames"

    id = Column(Integer, primary_key=True, index=True)
    status = Column(Enum(StatusExame), default=StatusExame.PENDENTE, nullable=False)
    arquivo_url = Column(String, nullable=False)
    data_criacao = Column(DateTime, default=datetime.utcnow, nullable=False)

    laudo = relationship("Laudos", back_populates="exame", uselist=False)


class Laudos(Base):
    __tablename__ = "laudos"

    id = Column(Integer, primary_key=True, index=True)
    conteudo = Column(Text, nullable=False)
    medico_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    exame_id = Column(Integer, ForeignKey("exames.id"), unique=True, nullable=False)

    medico = relationship("Usuarios", back_populates="laudos")
    exame = relationship("Exames", back_populates="laudo")
