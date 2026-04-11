import geopandas as gpd
from pathlib import Path
from utils.io.path import data_path

def save_parquet(gdf: gpd.GeoDataFrame, filename: str, subfolder: str = "") -> Path:
    # Garante a extensão .parquet
    if not filename.endswith(".parquet"):
        filename += ".parquet"
    path = data_path(filename, subfolder)
    gdf.to_parquet(path)
    return path

def load_parquet(filename: str, subfolder: str = "") -> gpd.GeoDataFrame:
    if not filename.endswith(".parquet"):
        raise ValueError(f"O arquivo '{filename}' deve ter a extensão .parquet")
        
    path = data_path(filename, subfolder)
    
    if not path.exists():
        raise FileNotFoundError(f"Arquivo não encontrado no caminho: {path}")
        
    return gpd.read_parquet(path)