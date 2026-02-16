
from datetime import datetime
from enum import Enum
from typing import Any, List, Tuple

BASE_OPTIONS = {
    'responsive': True,
    'interaction': {
        'intersect': False,
        'mode': 'index',
        'position': 'nearest'
    },
    'maintainAspectRatio': False,
    'scales': {
        'y': {
            'beginAtZero': True
        }
    },
    'plugins': {
        'legend': {
            'display': False
        },
        # 'tooltip': {
        #     'position': 'bottom'
        # }
    }
}


class Colors(Enum):
    SUCCESS = [47, 179, 68]
    DANGER = [214, 57, 57]
    WARNING = [247, 103, 7]
    PRIMARY = [56, 161, 255]
    PURPLE = [174, 62, 201]


class Dataset:
    def __init__(self, label: str, data: List[Any], color: Tuple[int, int, int], border_width: int = 1, type: str = 'bar'):
        self.label = label
        self.background_color = f'rgba({", ".join(color)}, {"0.75" if type == "bar" else "0.15"})'
        self.border_color = f'rgba({", ".join(color)}, 1)'
        self.data = data
        self.border_width = border_width
        self.type = type

    def dict(self):
        ret = {
            'label': self.label,
            'data': self.data,
            'backgroundColor': self.background_color,
            'borderColor':  self.border_color,
            'borderWidth': self.border_width,
            'type': self.type
        }
        if self.type == 'line':
            ret.update(tension=0.4)
        return ret


def chart_fluxo_caixa_config(
    data: dict,
    labels: List[str],
    colors: List[Tuple[int, int, int]] = [Colors.SUCCESS.value, Colors.DANGER.value, Colors.WARNING.value, Colors.PRIMARY.value, Colors.PURPLE.value],
    types: List[str] = ['bar', 'bar', 'bar', 'line', 'line'],
):
    colors = [[str(cc) for cc in c] for c in colors]

    datasets = [
        Dataset(label, data, colors[index], type=types[index]).dict()
        for index, (label, data) in enumerate(data.items())
    ]

    options = {**BASE_OPTIONS}
    options['plugins'].update(annotation={
        'annotations': [{
            'type': 'line',
            'xMin': datetime.now().strftime('%Y-%m-%d'),
            'xMax': datetime.now().strftime('%Y-%m-%d'),
            'borderColor': 'rgb(56,161,255)',
            'borderWidth': 2,
            'label': {
                'enabled': True,
                'content': 'Hoje'
            }
        }]
    })
    options['scales'].update(x={
        'ticks': {
            'autoSkip': True,
            'maxTicksLimit': 8
        }
    })
    options['elements'] = {
        'line': {
            'fill': True
        }
    }

    return {
        'type': 'bar',
        'data': {
            'labels': labels,
            'datasets': datasets
        },
        'options': options
    }
