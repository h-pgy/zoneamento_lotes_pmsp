import streamlit as st 
from dashboard.components import LoteSearchUI, PerimetrosMapRenderer
from dashboard.search_utils import load_lote_data

with st.spinner("Carregando dados..."):
    df = load_lote_data()

lote_search = LoteSearchUI(df)
renderizar_mapa_perimetros = PerimetrosMapRenderer()
df_lote = lote_search()

if df_lote is not None:

    if df_lote['id_pol_lote'].nunique() > 1:
        st.warning("Mais de um polígono de lote encontrado. Há de fato alguns casos de lotes com mais de um polígono.")
    for id_pol_lote in df_lote['id_pol_lote'].unique():

        with st.container(border=True):
            st.subheader(f"Perímetros de Zoneamento para o Polígono {id_pol_lote}")
            df_lote_poligono = df_lote[df_lote['id_pol_lote'] == id_pol_lote]
            renderizar_mapa_perimetros(id_pol_lote, df_lote_poligono)



        


