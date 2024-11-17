from fastapi import Request
from fastapi.templating import Jinja2Templates

from src.templates.context import render as context_render
from src.templates.filters import init_filters, init_globals

templates = Jinja2Templates(directory='src/templates/html')

init_filters(templates)
init_globals(templates)


def render(request: Request, template_name: str, session=None, context: dict = None):
    return context_render(
        templates=templates,
        request=request,
        template_name=template_name,
        session=session,
        context=context
    )
