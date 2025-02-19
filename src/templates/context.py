from typing import Dict, List, Optional, TypedDict

from fastapi import Request
from fastapi.templating import Jinja2Templates

from src.domain import repository
from src.schemas.auth import SessaoAutenticada
from src.templates.filters import \
    templates_global_material_symbol as material_symbol
from src.utils import url_incluir_query_params


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
            active: bool = False
        links: Dict[str, Link]

    class Header(TypedDict):
        pretitle: str
        title: str
        symbol: str
        buttons: List[Button]

    class Breadcrumb(TypedDict):
        label: str
        url: Optional[str] = None

    data_bs_theme: str = 'dark'
    title: str = 'Caderninho'
    navbar: Navbar
    header: Header
    breadcrumbs: List[Breadcrumb]
    usuario: SessaoAutenticada = None

    @classmethod
    def factory_navbar_link(self, request: Request, title: str, symbol_name: str, url_name: str, query_params: dict = None):
        base_nav_url = request.url_for(url_name)

        if query_params:
            nav_url = url_incluir_query_params(base_nav_url, **query_params)
        else:
            nav_url = base_nav_url

        return Context.Navbar.Link(
            title=title,
            symbol=material_symbol(symbol_name),
            url=nav_url,
            active=(request.url == base_nav_url or str(base_nav_url) in str(request.url))
        )

    @classmethod
    def factory_breadcrumbs(self, request: Request):
        base_url = f"{request.url.scheme}://{request.url.hostname}"
        if request.url.port:
            base_url = f"{base_url}:{request.base_url.port}"
        breadcrumbs = [
            # Context.Breadcrumb(
            #     label='Home',
            #     url=request.url_for('get_home')
            # )
        ]
        current_path = ""
        steps = 0
        for b in request.url.path.split('/'):
            if not b:
                continue

            current_path += f"{b}/"
            breadcrumbs.append(
                Context.Breadcrumb(
                    label=b,
                    url=f'{base_url}/{current_path}/' if steps else None
                )
            )
            steps += 1
        return breadcrumbs


BASE_NAVBAR_LINKS = [
    ('Home', 'home', 'get_home'),
    ('Vendas', 'shopping_cart', 'get_vendas_index', {'page': 1}),
    ('Estoque', 'inventory_2', 'get_estoques_index'),
    ('Receitas', 'library_books', 'get_receitas_index'),
    ('Ingredientes', 'package_2', 'get_ingredientes_index'),
    ('Organização', 'groups', 'get_organizacao_index'),
]


def get_context(request: Request, session=None, context: dict = None, navbar_links: list = BASE_NAVBAR_LINKS):
    theme = request.session.get('theme', 'light')

    base_context = Context(
        title='Caderninho',
        navbar=Context.Navbar(
            links=[
                Context.factory_navbar_link(request, *__navbar_link)
                for __navbar_link in navbar_links
            ]
        ),
        header=Context.Header(
            pretitle='CADERNINHO',
            title='Home',
            symbol='home'
        ),
        breadcrumbs=Context.factory_breadcrumbs(request),
        data_bs_theme=theme
    )

    if session and session.sessao_autenticada:
        base_context.update(usuario=session.sessao_autenticada)

        db_ingredientes, _, _ = repository.get(session, repository.Entities.INGREDIENTE)
        db_receitas, _, _ = repository.get(session, repository.Entities.RECEITA)
        entradas, saidas, caixa = repository.get_fluxo_caixa(session)

        base_context.update(ingredientes=db_ingredientes)
        base_context.update(receitas=db_receitas)
        base_context.update(entradas=entradas)
        base_context.update(saidas=saidas)
        base_context.update(caixa=caixa)

    if context:
        base_context.update(**context)

    return base_context


def render(templates: Jinja2Templates, request: Request, template_name: str, session=None, context: dict = None):
    context = get_context(request=request, session=session, context=context)
    response = templates.TemplateResponse(
        request=request,
        name=template_name,
        context=context
    )
    response.set_cookie('theme', request.session.get('theme', 'light'))
    return response
