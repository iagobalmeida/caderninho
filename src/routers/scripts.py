# pragma: nocover
import fastapi

from src import db
from src.env import getenv
from src.scripts import seed

router = fastapi.APIRouter(prefix='/scripts')

SCRIPTS_TOKEN = getenv('SCRIPTS_TOKEN', 'batatafrita')


@router.post('/seed', tags=['Scripts'])
async def post_scripts_seed(token: str = fastapi.Header(None)):
    if not token == SCRIPTS_TOKEN:
        raise fastapi.HTTPException(401, 'Não autorizado')
    seed.main()
    return True


@router.post('/reset_db', tags=['Scripts'])
async def post_scripts_reset_db(token: str = fastapi.Header(None)):
    if not token == SCRIPTS_TOKEN:
        raise fastapi.HTTPException(401, 'Não autorizado')
    db.reset()
    seed.main()
    return True
