import streamlit as st
import pandas as pd
from ..search_utils import LoteDataFilter
from typing import Dict, Any

class LoteSearchUI:
    MAPEAMENTO_TIPOS = {
        "F": "Fiscal",
        "M": "Municipal",
        "V": "Viário"
    }

    def __init__(self, dataframe_lotes: pd.DataFrame):
        self.dataframe_original = dataframe_lotes
        self.search_lote = LoteDataFilter(self.dataframe_original)
        self.is_condominial: bool = False
        self.parametros_busca: Dict[str, Any] = {}
        self.dataframe_resultado: pd.DataFrame | None = None
        self.lista_tipos_lote = self._definir_opcoes_tipo_lote()

    def _map_tipo_lote(self, tipo_lote: str, inverted: bool = False) -> str:
        if inverted:
            reverse_mapping = {v: k for k, v in self.MAPEAMENTO_TIPOS.items()}
            return reverse_mapping.get(tipo_lote, tipo_lote)
        return self.MAPEAMENTO_TIPOS.get(tipo_lote, tipo_lote)

    def _definir_opcoes_tipo_lote(self) -> list[str]:
        tipos_disponiveis = self.dataframe_original["cd_tipo_lote"].unique().tolist()
        opcoes_exibicao = []
        for tipo in tipos_disponiveis:
            if tipo in self.MAPEAMENTO_TIPOS:
                opcoes_exibicao.append(self._map_tipo_lote(tipo))
            else:
                opcoes_exibicao.append(tipo)
        
        if "Fiscal" in opcoes_exibicao:
            opcoes_exibicao.remove("Fiscal")
            opcoes_exibicao.insert(0, "Fiscal")
            
        return opcoes_exibicao

    def _renderizar_busca_detalhada(self) -> Dict[str, Any]:
        with st.expander("Opções Avançadas", expanded=False):
            cols = st.columns(2)
            self.is_condominial = st.toggle("Lote Condominial")
            with cols[0]:
                tipo_selecionado = st.selectbox("Tipo lote", options=self.lista_tipos_lote)
                cd_tipo_lote = self._map_tipo_lote(tipo_selecionado, inverted=True)
            
            with cols[1]:
                
                
                cd_condominio = 0
                if self.is_condominial:
                    cd_condominio = st.number_input("Código do Condomínio", min_value=0, max_value=99, step=1)
    
        return {
            "cd_tipo_lote": cd_tipo_lote,
            "cd_condominio": cd_condominio
        }

    def _renderizar_campos_input(self) -> Dict[str, Any]:
        coluna_setor, coluna_quadra, coluna_lote = st.columns(3)
        
        with coluna_setor:
            cd_setor = st.number_input("Setor", min_value=1, max_value=999, step=1)
        
        with coluna_quadra:
            cd_quadra = st.number_input("Quadra", min_value=1, max_value=999, step=1)
            
        with coluna_lote:
            cd_lote = st.number_input("Lote", min_value=1, max_value=9999, step=1)

        detalhes = self._renderizar_busca_detalhada()

        return {
            "cd_setor": cd_setor,
            "cd_quadra": cd_quadra,
            "cd_lote": cd_lote,
            **detalhes
        }

    def _executar_pesquisa(self, dados_input: Dict[str, Any]) -> None:
        cols = st.columns(3)
        with cols[1]:
            if st.button("Buscar Dados do Lote", type="primary"):
                with st.spinner("Buscando informações do lote..."):
                    self.dataframe_resultado = self.search_lote(
                        cd_setor=dados_input["cd_setor"],
                        cd_quadra=dados_input["cd_quadra"],
                        cd_lote=dados_input["cd_lote"],
                        cd_condominio=dados_input["cd_condominio"],
                        cd_tipo_lote=dados_input["cd_tipo_lote"]
                    )
                
        if self.dataframe_resultado is not None and self.dataframe_resultado.empty:
            st.warning(f"Nenhum registro encontrado para o SQL informado: {self.search_lote.ultimo_sql_buscado}.")

    def _exibir_resultados(self) -> None:
        if self.dataframe_resultado is not None and not self.dataframe_resultado.empty:
            with st.expander("Acesse os microdados desse lote", expanded=True):
                st.dataframe(self.dataframe_resultado, width='content')

    def render_pipeline(self) -> pd.DataFrame | None:

        with st.container(border=True):
            st.subheader("Busca de Lote Fiscal")
            self.parametros_busca = self._renderizar_campos_input()
            self._executar_pesquisa(self.parametros_busca)
        self._exibir_resultados()

        return self.dataframe_resultado

    def __call__(self) -> pd.DataFrame | None:
        return self.render_pipeline()