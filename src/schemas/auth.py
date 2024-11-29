from typing import Optional

from fastapi import Request
from pydantic import BaseModel
from sqlmodel import Session


class SessaoAutenticada(BaseModel):
    valid: bool = False
    id: int = None
    nome: str = None
    email: str = None
    dono: bool = None
    administrador: bool = False
    organizacao_id: int = None
    organizacao_descricao: str = None
    expires: Optional[float] = None

    @classmethod
    def from_request_session(cls, request: Request):
        request_session_sessao_autenticada = request.session.get('sessao_autenticada', None)
        if request_session_sessao_autenticada:
            return cls(**request_session_sessao_autenticada)

    def dict(self):
        return self.model_dump()


class DBSessaoAutenticada(Session):
    sessao_autenticada: SessaoAutenticada = None

    def __init__(self, *args, request: Request = None, **kwargs):
        self.sessao_autenticada = SessaoAutenticada.from_request_session(request)
        return super().__init__(*args, **kwargs)
