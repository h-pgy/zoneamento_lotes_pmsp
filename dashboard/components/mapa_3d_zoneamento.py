import streamlit as st
import pydeck as pdk
import pandas as pd
import geopandas as gpd
import numpy as np
from dashboard.search_utils import get_lote_polygon, get_perimetros_zonas

class LoteVisualizer3D:
    MAPEAMENTO_CORES_BASE = {
        "F": [255, 100, 100],
        "M": [100, 255, 100],
        "V": [100, 100, 255]
    }

    def __init__(self, df_lote: pd.DataFrame):
        self.df_lote = df_lote

    def _obter_lote_geometria(self, id_pol_lote: str) -> gpd.GeoDataFrame:
        lote_gdf = get_lote_polygon(id_pol_lote)
        return lote_gdf.to_crs(epsg=4326)
    
    def _add_importancia_zona(self, perimetros_gdf: gpd.GeoDataFrame, registro_lote: pd.Series) -> gpd.GeoDataFrame:
        mapa_importancia = self.df_lote.set_index('cd_zoneamento_perimetro')['importancia_zona_para_lote'].to_dict()
        perimetros_gdf['importancia_zona_para_lote'] = perimetros_gdf['cd_zoneamento_perimetro'].map(mapa_importancia)
        return perimetros_gdf

    def _obter_perimetros_processados(self, registro_lote: pd.Series) -> gpd.GeoDataFrame:
        ids_zonas = registro_lote['lst_id_perimetro_zoneamento'].split(';')
        
        perimetros_zonas = get_perimetros_zonas(ids_zonas)
        
        # Consolidação topográfica por zona
        perimetros_zonas = perimetros_zonas.dissolve(by='cd_zoneamento_perimetro').reset_index()
        
        # Enriquecimento com importância
        perimetros_zonas = self._add_importancia_zona(perimetros_zonas, registro_lote)
        
        return perimetros_zonas.to_crs(epsg=4326)

    def _atribuir_estilizacao(self, zonas_gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:

        zonas_unicas = zonas_gdf['cd_zoneamento_perimetro'].unique()
        np.random.seed(42)
        
        cores_map = {
            zona: list(np.random.choice(range(256), size=3)) + [180]
            for zona in zonas_unicas
        }
        
        zonas_gdf['fill_color'] = zonas_gdf['cd_zoneamento_perimetro'].map(cores_map)
        return zonas_gdf

    def _preparar_pipeline_dados(self, id_pol_lote: str) -> tuple[gpd.GeoDataFrame, gpd.GeoDataFrame]:
        registro_lote = self.df_lote[self.df_lote['id_pol_lote'] == id_pol_lote]
        
        if registro_lote.empty:
            return None, None
            
        registro_series = registro_lote.iloc[0]
        
        lote_gdf = self._obter_lote_geometria(id_pol_lote)
        zonas_gdf = self._obter_perimetros_processados(registro_series)
        zonas_gdf = self._atribuir_estilizacao(zonas_gdf)
        
        return lote_gdf, zonas_gdf

    def render(self, id_pol_lote: int, elevacao_multiplicador: int = 0.5):
        lote_gdf, zonas_gdf = self._preparar_pipeline_dados(id_pol_lote)
        
        if lote_gdf is None or zonas_gdf is None:
            st.error(f"Erro ao processar dados para o ID: {id_pol_lote}")
            return

        centroid = lote_gdf.geometry.centroid.iloc[0]
        view_state = pdk.ViewState(
            latitude=centroid.y,
            longitude=centroid.x,
            zoom=17,
            pitch=45,
            bearing=-15
        )

        camada_lote = pdk.Layer(
            "GeoJsonLayer",
            lote_gdf,
            get_fill_color=[60, 60, 60, 100],
            get_line_color=[255, 255, 255],
            line_width_min_pixels=1,
            pickable=True,
            auto_highlight=True
        )

        camada_zonas = pdk.Layer(
            "GeoJsonLayer",
            zonas_gdf,
            extruded=True,
            get_elevation=f"importancia_zona_para_lote * {elevacao_multiplicador}",
            get_fill_color="fill_color",
            get_line_color=[255, 255, 255, 120],
            pickable=True,
            auto_highlight=True,
        )

        st.pydeck_chart(pdk.Deck(
            layers=[camada_lote, camada_zonas],
            initial_view_state=view_state,
            map_style="mapbox://styles/mapbox/dark-v10",
            tooltip={
                "html": """
                <b>SQL:</b> {cd_setor}.{cd_quadra}.{cd_lote} <br/>
                <b>Zona:</b> {cd_zoneamento_perimetro} <br/>
                <b>Importância:</b> {importancia_zona_para_lote}
                """,
                "style": {"color": "white"}
            }
        ))