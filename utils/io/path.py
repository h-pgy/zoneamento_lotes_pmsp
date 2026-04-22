from pathlib import Path
from typing import Union
import geopandas as gpd
from config import DATA_DIR, OUTPUT_DIR

def ensure_dir(path: Union[str, Path]) -> Path:
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path

def join_and_ensure(directory: Union[str, Path], filename: str) -> Path:
    directory = ensure_dir(directory)
    return directory / filename

def data_path(fname: str, subfolder: str = "") -> Path:
    full_dir = DATA_DIR / subfolder
    return join_and_ensure(full_dir, fname)

def output_path(fname: str, subfolder: str = "") -> Path:
    full_dir = OUTPUT_DIR / subfolder
    return join_and_ensure(full_dir, fname)

def static_output_path(fname: str) -> Path:
    static = join_and_ensure(OUTPUT_DIR, 'static')

    return join_and_ensure(static, fname)