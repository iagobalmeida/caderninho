import asyncio
import json
import re
from datetime import datetime
from typing import List, Tuple

from fastapi.templating import Jinja2Templates
from jinja2 import pass_context


def __unit_converter(input: float, unity: str = 'g', converter_kg: bool = False, converter_kg_sempre: bool = False):
    if (converter_kg and abs(input) >= 1000 and unity == 'g') or converter_kg_sempre:
        input = input/1000
        unity = 'Kg'
    return (input, unity)


def templates_filter_markdown(input: str):
    input = re.sub(r"`(.*?)`", r"<code>\1</code>", input)
    input = re.sub(r"__(.*?)__", r"<i>\1</i>", input)
    return input


def templates_filter_strftime(input: datetime):
    return input.strftime('%d/%m/%Y ás %H:%M')


def templates_global_material_symbol(icon_name: str, classnames: str = None):
    return f'''<span class="material-symbols-outlined me-1 {classnames}">{icon_name}</span>'''


def status_html(classname: str, content: str, material_symbol: str = None):
    material_symbol_html = f'<span class="material-symbols-outlined"> {material_symbol} </span>' if material_symbol else ''
    return f'''
        <div class="status {classname}">
            {material_symbol_html}
            {content}
        </div>
    '''


def templates_filter_format_stock(input: float, converter_kg: bool = False, converter_kg_sempre: bool = False, icon_positive: str = 'check', icon_zero: str = 'more_horiz', icon_negative: str = 'close', unity: str = 'g'):
    material_symbol = icon_positive
    classname = 'status-success'
    if input < 0:
        material_symbol = icon_negative
        classname = 'status-danger'
    elif input == 0:
        material_symbol = icon_zero
        classname = 'status-secondary'
    input, unity = __unit_converter(input, unity, converter_kg, converter_kg_sempre)

    return status_html(classname, f'{input} {unity}.', material_symbol)


def templates_filter_format_stock_movement(input: float):
    return templates_filter_format_stock(input, icon_positive='arrow_upward', icon_negative='arrow_downward')


def templates_filter_format_quantity(input: float, converter_kg: bool = False, converter_kg_sempre: bool = False, unity: str = 'g'):
    input, unity = __unit_converter(input, unity, converter_kg, converter_kg_sempre)
    return status_html('status-primary', f'{input} {unity}.')


def templates_filter_format_reais(input: float):
    if input == 0 or not input:
        return '-'

    more_decimals = f'{input:.3f}'
    if more_decimals[-1] != '0':
        return f'R$ {more_decimals}'
    else:
        return f'R$ {input:.2f}'


def templates_filter_json(input: str):
    if not input:
        return None
    return json.dumps(input)


def templates_filter_format_log(input: str):
    result = input
    try:
        places = input.split(' | ')
        if len(places) == 1:
            return input
        subplaces = places[2].split(' - ')
        result = f'<b class="text-success">{places[0]}</b> | {places[1]} | <span class="text-primary">{subplaces[0]}</span> - {subplaces[1]}'
    except Exception as ex:
        pass
    finally:
        return result


BASE_FILTERS = [
    ('strftime', templates_filter_strftime),
    ('format_stock', templates_filter_format_stock),
    ('format_stock_movement', templates_filter_format_stock_movement),
    ('format_quantity', templates_filter_format_quantity),
    ('format_reais', templates_filter_format_reais),
    ('format_log', templates_filter_format_log),
    ('json', templates_filter_json),
    ('markdown', templates_filter_markdown)
]

BASE_GLOBALS = [
    ('material_symbol', templates_global_material_symbol)
]


def init_filters(templates: Jinja2Templates, filters: List[Tuple[str, callable]] = BASE_FILTERS):
    for __filter in filters:
        templates.env.filters[__filter[0]] = __filter[1]


def init_globals(templates: Jinja2Templates, _globals: List[Tuple[str, callable]] = BASE_GLOBALS):
    for __global in _globals:
        templates.env.globals[__global[0]] = __global[1]
