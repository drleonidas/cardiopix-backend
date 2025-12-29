"""
Aplicação FastAPI simples para autenticação e roteamento de dashboards
para diferentes perfis de usuários (Clínica, Médico e Paciente).
"""
from dataclasses import dataclass
from typing import Dict, Optional
import secrets

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel


@dataclass
class Clinica:
    username: str
    password: str
    nome: str


@dataclass
class Medico:
    username: str
    password: str
    crm: str


@dataclass
class Paciente:
    username: str
    password: str
    cpf: str


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    message: str
    role: str
    dashboard: str
    token: str


class AuthenticatedUser(BaseModel):
    username: str
    role: str


app = FastAPI(title="CardioPix Backend")
auth_scheme = HTTPBearer(auto_error=False)

# Simula armazenamentos para cada perfil.
clinicas: Dict[str, Clinica] = {
    "clinica123": Clinica(username="clinica123", password="segredo", nome="Clínica Exemplo"),
}
medicos: Dict[str, Medico] = {
    "drhouse": Medico(username="drhouse", password="vitamina", crm="CRM12345"),
}
pacientes: Dict[str, Paciente] = {
    "joao": Paciente(username="joao", password="paciente", cpf="123.456.789-00"),
}

# Armazena tokens emitidos em memória.
sessions: Dict[str, AuthenticatedUser] = {}


def authenticate_user(username: str, password: str) -> Optional[AuthenticatedUser]:
    if username in clinicas and clinicas[username].password == password:
        return AuthenticatedUser(username=username, role="clinica")

    if username in medicos and medicos[username].password == password:
        return AuthenticatedUser(username=username, role="medico")

    if username in pacientes and pacientes[username].password == password:
        return AuthenticatedUser(username=username, role="paciente")

    return None


def generate_token(user: AuthenticatedUser) -> str:
    token = secrets.token_urlsafe(32)
    sessions[token] = user
    return token


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(auth_scheme),
) -> AuthenticatedUser:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de autenticação ausente.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials
    if token not in sessions:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return sessions[token]


def role_required(expected_role: str):
    def dependency(user: AuthenticatedUser = Depends(get_current_user)) -> AuthenticatedUser:
        if user.role != expected_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acesso negado para este painel.",
            )
        return user

    return dependency


@app.post("/login", response_model=LoginResponse)
def login(credentials: LoginRequest) -> LoginResponse:
    user = authenticate_user(credentials.username, credentials.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas para todos os perfis.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    dashboard_path = f"/dashboard/{user.role}"
    token = generate_token(user)
    return LoginResponse(
        message=f"Autenticação bem-sucedida para perfil {user.role}.",
        role=user.role,
        dashboard=dashboard_path,
        token=token,
    )


@app.get("/dashboard/clinica")
def clinica_dashboard(user: AuthenticatedUser = Depends(role_required("clinica"))):
    return {
        "message": "Painel de Clínica",
        "username": user.username,
        "detalhes": "Informações e atalhos para gestão de clínicas.",
    }


@app.get("/dashboard/medico")
def medico_dashboard(user: AuthenticatedUser = Depends(role_required("medico"))):
    return {
        "message": "Painel de Médico",
        "username": user.username,
        "detalhes": "Listagem de pacientes, laudos e agenda do médico.",
    }


@app.get("/dashboard/paciente")
def paciente_dashboard(user: AuthenticatedUser = Depends(role_required("paciente"))):
    return {
        "message": "Painel de Paciente",
        "username": user.username,
        "detalhes": "Acesso a laudos, consultas e mensagens para o paciente.",
    }


@app.delete("/logout")
def logout(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(auth_scheme),
):
    if credentials is None or credentials.credentials not in sessions:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nenhuma sessão ativa para encerrar.",
        )

    token = credentials.credentials
    sessions.pop(token, None)
    return {"message": "Sessão encerrada com sucesso."}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
