from typing import Optional

from fastapi import Request
from pydantic import BaseModel


class AuthSession(BaseModel):
    valid: bool = False
    id: int = None
    nome: str = None
    email: str = None
    dono: bool = None
    administrador: bool = False
    organizacao_id: Optional[int] = None
    organizacao_descricao: Optional[str] = None
    expires: Optional[float] = None

    @classmethod
    def from_request_session(cls, request: Request):
        request_session_sessao_autenticada = request.session.get('sessao_autenticada', None)
        if request_session_sessao_autenticada:
            return cls(**request_session_sessao_autenticada)

    def dict(self):
        return self.model_dump()
