from typing import Optional
from uuid import UUID

from fastapi import Request
from loguru import logger
from pydantic import BaseModel


class AuthSession(BaseModel):
    valid: bool = False
    id: UUID = None
    nome: str = None
    email: str = None
    dono: bool = None
    administrador: bool = False
    organizacao_id: Optional[UUID] = None
    organizacao_descricao: Optional[str] = None
    expires: Optional[float] = None

    @classmethod
    def from_request_session(cls, request: Request):
        request_session_sessao_autenticada = request.session.get('sessao_autenticada', None)
        logger.info(request_session_sessao_autenticada)
        if request_session_sessao_autenticada:
            if request_session_sessao_autenticada.get('organizacao_id', 'None') == 'None':
                logger.info('Cleaning "organizacao_id"')
                request_session_sessao_autenticada['organizacao_id'] = None
            return cls(**request_session_sessao_autenticada)

    def data_bs_payload(self):
        return {
            **self.model_dump(),
            'id': str(self.id),
            'organizacao_id': str(self.organizacao_id)
        }

    def __hash__(self):
        return hash((self.organizacao_id, self.id))
