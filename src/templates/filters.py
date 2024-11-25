import json
from datetime import datetime
from typing import List, Tuple

from fastapi.templating import Jinja2Templates

CONVERTER_GRAMAS_PARA_KILO = False
CONVERTER_GRAMAS_PARA_KILO_SEMPRE = False


def __unit_converter(input: float, unity: str = 'g'):
    if (CONVERTER_GRAMAS_PARA_KILO and abs(input) > 1000 and unity == 'g') or CONVERTER_GRAMAS_PARA_KILO_SEMPRE:
        input = input/1000
        unity = 'Kg'
    return (input, unity)


def templates_filter_strftime(input: datetime):
    return input.strftime('%d/%m/%Y ás %H:%M')


def templates_global_material_symbol(icon_name: str, classnames: str = None):
    return f'''<span class="material-symbols-outlined me-1 {classnames}">{icon_name}</span>'''


def __status_html(classname: str, content: str, material_symbol: str = None):
    material_symbol_html = f'<span class="material-symbols-outlined"> {material_symbol} </span>' if material_symbol else ''
    return f'''
        <div class="status {classname}">
            {material_symbol_html}
            {content}
        </div>
    '''


def templates_filter_format_stock(input: float, unity: str = 'g', icon_positive: str = 'check', icon_zero: str = 'more_horiz', icon_negative: str = 'close'):
    material_symbol = icon_positive
    classname = 'status-success'
    if input < 0:
        material_symbol = icon_negative
        classname = 'status-danger'
    elif input == 0:
        material_symbol = icon_zero
        classname = 'status-secondary'
    input, unity = __unit_converter(input, unity)

    return __status_html(classname, f'{input} {unity}', material_symbol)


def templates_filter_format_stock_movement(input: float):
    return templates_filter_format_stock(input, icon_positive='arrow_upward', icon_negative='arrow_downward')


def templates_filter_format_quantity(input: float):
    input, unity = __unit_converter(input, 'g')
    return __status_html('status-primary', f'{input} {unity}')


def templates_filter_format_reais(input: float):
    if input == 0:
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


BASE_FILTERS = [
    ('strftime', templates_filter_strftime),
    ('format_stock', templates_filter_format_stock),
    ('format_stock_movement', templates_filter_format_stock_movement),
    ('format_quantity', templates_filter_format_quantity),
    ('format_reais', templates_filter_format_reais),
    ('json', templates_filter_json)
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
