import streamlit as st 
from dashboard.components import LoteSearchUI
from dashboard.search_utils import load_lote_data
from dashboard.components.mapa_3d_zoneamento import LoteVisualizer3D

with st.spinner("Carregando dados..."):
    df = load_lote_data()

lote_search = LoteSearchUI(df)
df_lote = lote_search()

if df_lote is not None:

    if df_lote['id_pol_lote'].nunique() > 1:
        st.warning("Mais de um polígono de lote encontrado. Há de fato alguns casos de lotes com mais de um polígono.")
    for id_pol_lote in df_lote['id_pol_lote'].unique():
        
        visualizador = LoteVisualizer3D(df_lote)
        visualizador.render(id_pol_lote)



        


