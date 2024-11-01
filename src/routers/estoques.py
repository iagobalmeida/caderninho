from fastapi import Request
from fastapi.routing import APIRouter
from sqlmodel import Session

from db import SESSION_DEP
from domain import repository
from templates import templates

router = APIRouter(prefix='/estoques')


@router.get('/')
async def get_estoques_index(request: Request, session: Session = SESSION_DEP):
    db_estoques = repository.get_estoques(session)
    return templates.TemplateResponse(
        request=request,
        name='estoques/list.html',
        context={
            'estoques': db_estoques
        }
    )
