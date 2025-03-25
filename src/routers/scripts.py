# pragma: nocover
import fastapi

import db
from env import getenv
from scripts import seed

router = fastapi.APIRouter(prefix='/scripts')

SCRIPTS_TOKEN = getenv('SCRIPTS_TOKEN', 'batatafrita')


@router.post('/seed', tags=['Scripts'])
async def post_scripts_seed(token: str = fastapi.Header(None)):  # pragma: nocover
    if not token == SCRIPTS_TOKEN:
        raise fastapi.HTTPException(401, 'Não autorizado')
    await seed.main()
    return True


@router.post('/reset_db', tags=['Scripts'])
async def post_scripts_reset_db(token: str = fastapi.Header(None)):  # pragma: nocover
    if not token == SCRIPTS_TOKEN:
        raise fastapi.HTTPException(401, 'Não autorizado')
    await db.reset()
    await seed.main()
    return True
