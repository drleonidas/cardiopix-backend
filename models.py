from datetime import date
from typing import Optional
from uuid import uuid4

from pydantic import BaseModel, EmailStr, Field

__all__ = ["Clinica", "Medico", "Paciente"]


class Clinica(BaseModel):
    """Informações básicas de uma clínica médica."""

    id: str = Field(default_factory=lambda: str(uuid4()), description="Identificador único da clínica")
    nome: str = Field(..., description="Nome fantasia da clínica")
    cnpj: str = Field(..., description="Documento de identificação da clínica")
    telefone: Optional[str] = Field(None, description="Telefone para contato")
    endereco: Optional[str] = Field(None, description="Endereço completo")


class Medico(BaseModel):
    """Dados de profissionais médicos associados a uma clínica."""

    id: str = Field(default_factory=lambda: str(uuid4()), description="Identificador único do médico")
    nome: str = Field(..., description="Nome completo")
    crm: str = Field(..., description="CRM do profissional")
    especialidade: Optional[str] = Field(None, description="Especialidade médica")
    email: Optional[EmailStr] = Field(None, description="Email para contato")
    telefone: Optional[str] = Field(None, description="Telefone para contato")
    clinica_id: Optional[str] = Field(None, description="Identificador da clínica a que pertence")


class Paciente(BaseModel):
    """Informações cadastrais de pacientes."""

    id: str = Field(default_factory=lambda: str(uuid4()), description="Identificador único do paciente")
    nome: str = Field(..., description="Nome completo")
    cpf: str = Field(..., description="Documento de identificação do paciente")
    data_nascimento: Optional[date] = Field(None, description="Data de nascimento")
    email: Optional[EmailStr] = Field(None, description="Email do paciente")
    telefone: Optional[str] = Field(None, description="Telefone de contato")
    clinica_id: Optional[str] = Field(None, description="Identificador da clínica do paciente")
