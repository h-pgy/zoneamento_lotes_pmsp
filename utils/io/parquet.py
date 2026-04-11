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