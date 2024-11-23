import fastapi

from src import db
from src.scripts import seed

router = fastapi.APIRouter(prefix='/scripts')


@router.post('/seed', tags=['Scripts'])
async def post_scripts_seed(Authorization: str = fastapi.Header(None)):
    if not Authorization == 'batatafrita':
        raise fastapi.HTTPException(401, 'Não autorizado')
    seed.main()
    return True


@router.post('/reset_db', tags=['Scripts'])
async def post_scripts_reset_db(Authorization: str = fastapi.Header(None)):
    if not Authorization == 'batatafrita':
        raise fastapi.HTTPException(401, 'Não autorizado')
    db.reset()
    seed.main()
    return True
