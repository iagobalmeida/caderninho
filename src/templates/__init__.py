from fastapi import Request
from fastapi.templating import Jinja2Templates

from templates.context import render as context_render
from templates.filters import init_filters, init_globals

templates = Jinja2Templates(directory='src/templates/html')

init_filters(templates)
init_globals(templates)


async def render(request: Request, template_name: str, session=None, context: dict = None):
    return await context_render(
        templates=templates,
        request=request,
        template_name=template_name,
        session=session,
        context=context
    )
