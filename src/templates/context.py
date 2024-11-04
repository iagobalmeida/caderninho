from typing import Dict, List, TypedDict

from fastapi import Request
from fastapi.templating import Jinja2Templates

from templates.filters import \
    templates_global_material_symbol as material_symbol


class Button(TypedDict):
    content: str
    symbol: str
    classname: str
    href: str
    attributes: Dict[str, str]


class Context(TypedDict):
    class Navbar(TypedDict):
        class Link(TypedDict):
            title: str
            symbol: str
            url: str
        links: Dict[str, Link]

    class Header(TypedDict):
        pretitle: str
        title: str
        symbol: str
        buttons: List[Button]

    class Breadcrumb(TypedDict):
        label: str
        url: str

    title: str = 'Herbaria'
    navbar: Navbar
    header: Header
    breadcrumbs: List[Breadcrumb]

    @classmethod
    def factory_navbar_link(self, request: Request, title: str, symbol_name: str, url_name: str):
        return Context.Navbar.Link(
            title=title,
            symbol=material_symbol(symbol_name),
            url=request.url_for(url_name)
        )

    @classmethod
    def factory_breadcrumbs(self, request: Request):
        base_url = f"{request.url.scheme}://{request.url.hostname}"
        if request.url.port:
            base_url = f"{base_url}:{request.base_url.port}"
        breadcrumbs = [
            Context.Breadcrumb(
                label='Home',
                url=f'/'
            )
        ]
        current_path = ""
        for b in request.url.path.split('/'):
            if not b:
                continue

            current_path += f"{b}/"
            breadcrumbs.append(
                Context.Breadcrumb(
                    label=b,
                    url=f'{base_url}/{current_path}'
                )
            )
        return breadcrumbs


BASE_NAVBAR_LINKS = [
    ('Home', 'home', 'get_index'),
    ('Vendas', 'shopping_cart', 'get_vendas_index'),
    ('Estoque', 'home_storage', 'get_estoques_index'),
    ('Receitas', 'library_books', 'get_receitas_index'),
    ('Ingredientes', 'package_2', 'get_ingredientes_index')
]


def get_context(request: Request, context: dict, navbar_links: list = BASE_NAVBAR_LINKS):
    base_context = Context(
        title='Herbaria',
        navbar=Context.Navbar(
            links=[
                Context.factory_navbar_link(request, __navbar_link[0], __navbar_link[1], __navbar_link[2])
                for __navbar_link in navbar_links
            ]
        ),
        header=Context.Header(
            pretitle='HERBARIA',
            title='Home',
            symbol='home'
        ),
        breadcrumbs=Context.factory_breadcrumbs(request)
    )
    base_context.update(**context)
    return base_context


def render(templates: Jinja2Templates, request: Request, template_name: str, context: dict):
    return templates.TemplateResponse(
        request=request,
        name=template_name,
        context=get_context(request, context)
    )
