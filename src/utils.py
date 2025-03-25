import os
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

import fastapi
import fastapi.security


def is_testing() -> bool:
    return 'PYTEST_VERSION' in os.environ or 'COVERAGE_RUN' in os.environ


def url_incluir_query_params(url: str, **params):
    parsed_url = urlparse(url=str(url))
    query_params = parse_qs(parsed_url.query)
    query_params.update(**params)
    new_query = urlencode(query_params, doseq=True)
    parsed_url = parsed_url._replace(query=new_query)
    return urlunparse(parsed_url)


def redirect_url(url: str, status_code: int = 302, message: str = None, error: str = None):
    query_params = {}
    if message:
        query_params.update(message=message)
    if error:
        query_params.update(error=error)
    if query_params:
        url = url_incluir_query_params(url, **query_params)

    return fastapi.responses.RedirectResponse(
        url=url,
        status_code=status_code
    )


def redirect_url_for(request: fastapi.Request, url_name: str, status_code: int = 302, message: str = None, error: str = None, **kwargs):
    url = request.url_for(url_name, **kwargs)
    return redirect_url(url, status_code, message, error)


def redirect_back(request: fastapi.Request, status_code: int = 302, message: str = None, error: str = None):
    url = request.headers.get('referer', request.url_for('get_home'))

    query_params = {}
    if message:
        query_params.update(message=message)
    if error:
        query_params.update(error=error)
    if query_params:
        url = url_incluir_query_params(url, **query_params)

    return fastapi.responses.RedirectResponse(
        url=url,
        status_code=status_code
    )
