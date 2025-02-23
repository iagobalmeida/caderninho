import re
from datetime import datetime

from src.templates import filters


def __remover_espacos(texto: str):
    return re.sub(r"\s+", "", texto)


def test_filters_markdown():
    markdown_expected = '<code>Teste</code> <i>funciona!</i>'
    assert filters.templates_filter_markdown('`Teste` __funciona!__') == markdown_expected


def test_filters_strftime():
    strftime_expected = '01/01/2025 ás 10:10'
    assert filters.templates_filter_strftime(datetime(2025, 1, 1, 10, 10)) == strftime_expected


def test_filters_material_symbol():
    material_symbol_expected = '<span class="material-symbols-outlined me-1 teste">teste</span>'
    assert filters.templates_global_material_symbol('teste', 'teste') == material_symbol_expected


def test_filters_format_stock_movement():
    stock_movement_class_names = ['status-success', 'status-danger', 'status-secondary']
    stock_movement_values = [10, -10, 0]
    stock_movement_symbols = ['arrow_upward', 'arrow_downward', 'more_horiz']

    for i in range(len(stock_movement_class_names)):
        __class_name = stock_movement_class_names[i]
        __value = stock_movement_values[i]
        __symbol = stock_movement_symbols[i]
        __expected = f'''
            <div class="status {__class_name}">
                <span class="material-symbols-outlined"> {__symbol} </span>
                {__value} g.
            </div>
        '''
        result = filters.templates_filter_format_stock_movement(__value)
        assert __remover_espacos(result) == __remover_espacos(__expected)


def test_filters_format_quantity():
    quantity_expected = '''
        <div class="status status-primary">
            1.0 Kg.
        </div>
    '''
    result = filters.templates_filter_format_quantity(1000, converter_kg=True)
    assert __remover_espacos(result) == __remover_espacos(quantity_expected)


def test_filters_format_reais():
    assert filters.templates_filter_format_reais(10.001) == 'R$ 10.001'


def test_filters_json():
    assert filters.templates_filter_json(None) == None
