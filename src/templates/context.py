import itertools
from datetime import datetime, timedelta
from typing import Dict, List, Optional, TypedDict

from fastapi import Request
from fastapi.templating import Jinja2Templates

from domain import repository
from schemas.auth import AuthSession
from schemas.docs import get_sobre_essa_pagina_html
from templates.chartjs import chart_fluxo_caixa_config
from templates.filters import \
    templates_global_material_symbol as material_symbol
from utils import url_incluir_query_params


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
    usuario: AuthSession = None
    now: datetime

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
        protocol = request.url.scheme
        hostname = request.url.hostname
        port = f':{request.base_url.port}' if request.base_url.port else ''
        base_url = f"{protocol}://{hostname}{port}"
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
                    label=' '.join(b.split('_')),
                    url=f'{base_url}/{current_path}' if steps else None
                )
            )
            steps += 1
        return breadcrumbs


BASE_NAVBAR_LINKS = [
    ('Home', 'home', 'get_home'),
    ('Caixa', 'payments', 'get_caixa_movimentacoes_index', {'page': 1}),
    ('Estoque', 'inventory_2', 'get_estoques_index'),
    ('Receitas', 'library_books', 'get_receitas_index'),
    ('Insumos', 'package_2', 'get_insumos_index'),
    ('Organização', 'groups', 'get_organizacao_index'),
]

ADMIN_NAVBAR_LINKS = [
    ('Logs', 'android', 'get_admin_logs')
]


async def update_context_with_chart(auth_session: AuthSession, db_session, base_context: dict):
    chart_data_inicial = datetime.now() - timedelta(days=30)
    chart_data_final = datetime.now() + timedelta(days=30)

    chart_datasets_cached = await repository.get_chart_fluxo_caixa_datasets(
        auth_session=auth_session,
        db_session=db_session,
        data_inicial=chart_data_inicial,
        data_final=chart_data_final
    )
    chart_datasets = chart_datasets_cached['value']
    labels = [cd[0] for cd in chart_datasets]
    entradas = [c[1] for c in chart_datasets]
    saidas = [c[2] for c in chart_datasets]
    margem = [c[3] for c in chart_datasets]
    saidas_recorrentes = [c[4] for c in chart_datasets]
    margem_final = list(map(int, itertools.accumulate(margem)))
    datas = [datetime.strptime(cd[0], '%Y-%m-%d') for cd in chart_datasets]
    chart_config = chart_fluxo_caixa_config(
        data={
            'Entradas': entradas[10:],
            'Saídas': saidas[10:],
            'Saídas Recorrentes': saidas_recorrentes[10:],
            'Margem': margem[10:],
            'Margem Final': margem_final[10:]
        },
        labels=labels[10:]
    )
    base_context.update(chart_resumo_caixa_data_atualizacao=chart_datasets_cached['created_at'])
    base_context.update(chart_resumo_caixa_data_inicial=datas[10:][0])
    base_context.update(chart_resumo_caixa_data_final=datas[-1])
    base_context.update(chart_resumo_caixa_config=chart_config)
    base_context.update(chart_resumo_caixa_total_entradas=sum(entradas))
    base_context.update(chart_resumo_caixa_total_saidas=sum(saidas))
    base_context.update(chart_resumo_caixa_total_saidas_recorrentes=sum(saidas_recorrentes))
    base_context.update(chart_resumo_caixa_margem_final=margem_final[-1])
    return base_context


async def get_context(request: Request, session=None, context: dict = None, navbar_links: list = BASE_NAVBAR_LINKS):
    auth_session = getattr(request.state, 'auth', None)
    theme = request.session.get('theme', 'light')

    if auth_session and auth_session.administrador:
        navbar_links = [*navbar_links, *ADMIN_NAVBAR_LINKS]

    base_context = Context(
        now=datetime.now(),
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

    if auth_session:
        base_context.update(usuario=auth_session)

        db_insumos, _, _ = await repository.get(auth_session=auth_session, db_session=session, entity=repository.Entities.INSUMO)
        db_receitas, _, _ = await repository.get(auth_session=auth_session, db_session=session, entity=repository.Entities.RECEITA)

        base_context.update(insumos=db_insumos)
        base_context.update(receitas=db_receitas)
        base_context = await update_context_with_chart(auth_session=auth_session, db_session=session, base_context=base_context)

    if context:
        base_context.update(**context)

    return base_context


async def render(templates: Jinja2Templates, request: Request, template_name: str, session=None, context: dict = None):
    context = await get_context(request=request, session=session, context=context)

    if '/app/' in str(request.url):
        nome_pagina = str(request.url).split('app/')[1].split('/')[0]
        sobre_essa_pagina = get_sobre_essa_pagina_html(nome_pagina)
        if sobre_essa_pagina:
            context.update(sobre_essa_pagina_html=sobre_essa_pagina)

    response = templates.TemplateResponse(
        request=request,
        name=template_name,
        context=context
    )
    response.set_cookie('theme', request.session.get('theme', 'light'))
    return response
