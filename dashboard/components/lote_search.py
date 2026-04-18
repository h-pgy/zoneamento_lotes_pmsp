import streamlit as st
import pandas as pd
from ..search_utils import LoteDataFilter
from typing import Optional, Dict

class LoteSearchUI:
    def __init__(self, dataframe_lotes: Optional[pd.DataFrame] = None):
        self.search_lote = LoteDataFilter(dataframe_lotes)
        self.is_condominial: bool = False
        self.parametros_busca: Dict[str, int] = {}
        self.dataframe_resultado: Optional[pd.DataFrame] = None

    def _configurar_modo_busca(self) -> None:
        self.is_condominial = st.toggle("Lote Condominial")

    def _renderizar_campos_input(self) -> Dict[str, int]:
        coluna_setor, coluna_quadra, coluna_lote = st.columns(3)
        
        with coluna_setor:
            cd_setor = st.number_input("Setor", min_value=1, max_value=999, step=1)
        
        with coluna_quadra:
            cd_quadra = st.number_input("Quadra", min_value=1, max_value=999, step=1)
            
        with coluna_lote:
            cd_lote = st.number_input("Lote", min_value=1, max_value=9999, step=1)

        cd_condominio = 0
        if self.is_condominial:
            cd_condominio = st.number_input("Código do Condomínio", min_value=0, max_value=99, step=1)

        return {
            "cd_setor": cd_setor,
            "cd_quadra": cd_quadra,
            "cd_lote": cd_lote,
            "cd_condominio": cd_condominio
        }

    def _executar_pesquisa(self, dados_input: Dict[str, int]) -> None:
        if st.button("Buscar Dados do Lote", type="primary"):
            with st.spinner("Buscando informações do lote..."):
                self.dataframe_resultado = self.search_lote(
                    cd_setor=dados_input["cd_setor"],
                    cd_quadra=dados_input["cd_quadra"],
                    cd_lote=dados_input["cd_lote"],
                    cd_condominio=dados_input["cd_condominio"]
                )
            
            if self.dataframe_resultado.empty:
                st.warning(f"Nenhum registro encontrado para o SQL informado: {self.search_lote.ultimo_sql_buscado}.")

    def _exibir_resultados(self) -> None:
        if self.dataframe_resultado is not None and not self.dataframe_resultado.empty:
            with st.expander("Acesse os microdados desse lote", expanded=True):
                st.dataframe(self.dataframe_resultado, width='stretch')

    def render_pipeline(self) -> pd.DataFrame|None:
        st.subheader("Busca de Lote Fiscal")
        self._configurar_modo_busca()
        self.parametros_busca = self._renderizar_campos_input()
        self._executar_pesquisa(self.parametros_busca)
        self._exibir_resultados()

        return self.dataframe_resultado

    def __call__(self) -> pd.DataFrame|None:
        self.render_pipeline()