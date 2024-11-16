from functools import wraps

from fastapi import Request

from src.auth import header_authorization
from src.utils import redirect_url_for


def authorized(func):
    @wraps(func)
    async def wrapper(*args, request: Request, **kwargs):
        user = header_authorization(request, request.headers.get('Authorization', None))
        print(f'user: {user}')
        if not user:
            return redirect_url_for(request, 'get_index')
        kwargs['request'] = request
        return await func(*args, **kwargs)
    return wrapper
