from .path import static_output_path
import json
from matplotlib.figure import Figure

def save_static_binary_file(fname:str, data:bytes)->str:

    path = static_output_path(fname)

    with open(path, 'wb') as f:
        f.write(data)
    return str(path)

def save_json(fname:str, data:dict)->str:

    if not fname.endswith('.json'):
        fname += '.json'

    path = static_output_path(fname)

    with open(path, 'w') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    return str(path)

def save_img(fname:str, fig:Figure)->str:

    if not fname.endswith('.png'):
        fname += '.png'

    path = static_output_path(fname)
    fig.savefig(path, dpi=300, bbox_inches='tight')

    return str(path)
    
    
