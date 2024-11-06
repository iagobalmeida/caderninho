import fastapi


def redirect_url_for(request: fastapi.Request, url_name: str, status_code: int = 302, **kwargs):
    return fastapi.responses.RedirectResponse(
        url=request.url_for(url_name, **kwargs),
        status_code=status_code
    )


def redirect_back(request: fastapi.Request, status_code: int = 302):
    return fastapi.responses.RedirectResponse(
        url=request.headers['referer'],
        status_code=status_code
    )
