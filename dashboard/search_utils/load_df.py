from utils.io.parquet import load_parquet
import streamlit as st
import pandas as pd

DATA_FILE = 'df_microdados_final.parquet'
DATA_SUBFOLDER = 'dados_dashboard'

@st.cache_data(show_spinner=True)
def load_lote_data() -> pd.DataFrame:

    return load_parquet(DATA_FILE, DATA_SUBFOLDER, output=True, gdf=False)