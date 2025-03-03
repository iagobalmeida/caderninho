from typing import List

DEFAULT_COLORS = [
    [162, 235, 54],
    [235, 54, 54],
    [162, 162, 235],
    [54, 162, 235],
]


def chart_fluxo_caixa_config(
    data: dict,
    labels: List[str],
    colors: List[List[int]] = DEFAULT_COLORS,
    types: List[str] = None,
):
    colors = [[str(cc) for cc in c] for c in colors]
    datasets = []
    for d in data:
        dataset_index = len(datasets)
        background_color = f'rgba({", ".join(colors[dataset_index])}, 0.5)'
        border_color = f'rgba({", ".join(colors[dataset_index])}, 1)'
        datasets.append({
            'label': d,
            'data': data[d],
            'backgroundColor': background_color,
            'borderColor':  border_color,
            'borderWidth': 1,
            'type': types[dataset_index] if types else 'bar'
        })
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
            }
        }
    }
