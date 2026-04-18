import streamlit as st 
from dashboard.components import LoteSearchUI
from dashboard.search_utils import load_lote_data

with st.spinner("Carregando dados..."):
    df = load_lote_data()

lote_search = LoteSearchUI(df)
df_lote = lote_search()


