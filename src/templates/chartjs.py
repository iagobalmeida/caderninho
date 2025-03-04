from typing import List

DEFAULT_COLORS = [
    [47, 179, 68],
    [214, 57, 57],
    [56, 161, 255],
    [162, 162, 235],
]


def chart_fluxo_caixa_config(
    data: dict,
    labels: List[str],
    colors: List[List[int]] = DEFAULT_COLORS,
    types: List[str] = ['bar', 'bar', 'line', 'line'],
):
    colors = [[str(cc) for cc in c] for c in colors]
    datasets = []
    for d in data:
        dataset_index = len(datasets)
        type = types[dataset_index] if types else 'bar'
        background_color = f'rgba({", ".join(colors[dataset_index])}, {"1" if type == "bar" else "0.15"})'
        border_color = f'rgba({", ".join(colors[dataset_index])}, 1)'
        dataset = {
            'label': d,
            'data': data[d],
            'backgroundColor': background_color,
            'borderColor':  border_color,
            'borderWidth': 1,
            'type': types[dataset_index] if types else 'bar'
        }
        if type == 'line':
            dataset['tension'] = .6
        datasets.insert(0, dataset)
    return {
        'type': 'bar',
        'data': {
            'labels': labels,
            'datasets': datasets
        },
        'options': {
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
            'elements': {
                'line': {
                    'fill': True
                }
            }
        }
    }
