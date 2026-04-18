import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
import geopandas as gpd
from typing import List, Dict, Any
from dashboard.search_utils import get_lote_polygon, get_perimetros_zonas

class PerimetrosMapRenderer:
    def __init__(self):
        self.cores_base: List[str] = [
            '#e6194b', '#3cb44b', '#ffe119', '#4363d8', '#f58231', 
            '#911eb4', '#46f0f0', '#f032e6', '#bcf60c', '#fabebe'
        ]

    def _extrair_ids_perimetros(self, dataframe_lote_filtrado: pd.DataFrame) -> List[str]:
        lista_ids_total: List[str] = []
        coluna_perimetros = dataframe_lote_filtrado['lst_id_perimetro_zoneamento'].dropna()
        
        for registro in coluna_perimetros:
            ids_extraidos = str(registro).split(';')
            lista_ids_total.extend([id_item.strip() for id_item in ids_extraidos if id_item.strip()])
            
        return list(set(lista_ids_total))

    def _gerar_colormap(self, categorias: List[str]) -> Dict[str, str]:
        return {
            categoria: self.cores_base[indice % len(self.cores_base)] 
            for indice, categoria in enumerate(categorias)
        }

    def _configurar_mapa_base(self, gdf_lote: gpd.GeoDataFrame) -> folium.Map:
        gdf_wgs84 = gdf_lote.to_crs(epsg=4326)
        centroide = gdf_wgs84.geometry.centroid.iloc[0]
        return folium.Map(
            location=[centroide.y, centroide.x], 
            zoom_start=18, 
            tiles="OpenStreetMap"
        )

    def _adicionar_camada_lote(self, mapa: folium.Map, gdf_lote: gpd.GeoDataFrame) -> None:
        folium.GeoJson(
            gdf_lote.to_crs(epsg=4326),
            name="Lote Fiscal",
            style_function=lambda _: {
                "fillColor": "#808080",
                "color": "#080808",
                "weight": 4,
                "fillOpacity": 0.5,
            }
        ).add_to(mapa)

    def _adicionar_camada_zoneamento(self, mapa: folium.Map, gdf_zonas: gpd.GeoDataFrame) -> None:
        categorias_zonas = gdf_zonas['cd_zoneamento_perimetro'].unique().tolist()
        mapa_cores = self._gerar_colormap(categorias_zonas)

        folium.GeoJson(
            gdf_zonas.to_crs(epsg=4326),
            name="Perímetros de Zoneamento",
            style_function=lambda feature: {
                "fillColor": mapa_cores.get(feature['properties']['cd_zoneamento_perimetro'], "#0000FF"),
                "color": mapa_cores.get(feature['properties']['cd_zoneamento_perimetro'], "#0000FF"),
                "weight": 2,
                "fillOpacity": 0.5,
            },
            tooltip=folium.GeoJsonTooltip(
                fields=['cd_zoneamento_perimetro'], 
                aliases=['Zona:']
            )
        ).add_to(mapa)

    def __call__(self, id_pol_lote: str, df_lote_contexto: pd.DataFrame) -> None:
        gdf_lote = get_lote_polygon(id_pol_lote)
        
        filtro_poligono = df_lote_contexto[df_lote_contexto['id_pol_lote'] == id_pol_lote]
        ids_perimetros = self._extrair_ids_perimetros(filtro_poligono)

        if not ids_perimetros:
            st.info(f"Nenhum perímetro de zoneamento para o polígono {id_pol_lote}.")
            return

        gdf_zonas = get_perimetros_zonas(ids_perimetros)
        
        mapa_final = self._configurar_mapa_base(gdf_lote)
        self._adicionar_camada_lote(mapa_final, gdf_lote)
        self._adicionar_camada_zoneamento(mapa_final, gdf_zonas)

        
        folium.LayerControl().add_to(mapa_final)
        
        st.markdown(f"#### Mapa do Polígono: {id_pol_lote}")
        st_folium(mapa_final, width=700, height=500, returned_objects=[], key=f"map_{id_pol_lote}")