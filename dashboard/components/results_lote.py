import streamlit as st
import pandas as pd
from typing import Dict, List

class LoteResultadosUI:
    def __init__(self):
        self.mapeamento_tipos: Dict[str, str] = {
            "M": "Municipal",
            "F": "Fiscal",
            "V": "Viário"
        }

    def _render_header_geral(self, dataframe_lote: pd.DataFrame) -> None:
        registro_base = dataframe_lote.iloc[0]
        
        # Ajustado para cd_setor_fiscal e cd_quadra_fiscal conforme seu snippet
        setor = str(registro_base["cd_setor_fiscal"]).zfill(3)
        quadra = str(registro_base["cd_quadra_fiscal"]).zfill(4)
        lote = str(registro_base["cd_lote"]).zfill(3)
        condominio = str(registro_base["cd_condominio"]).zfill(2)
        
        sql_formatado = f"{setor}.{quadra}.{lote}-{condominio}"
        quantidade_poligonos = dataframe_lote["id_pol_lote"].nunique()
        
        st.success("Lote encontrado com sucesso!")
        st.header(f"Informações sobre o lote {sql_formatado}")
        
        coluna_dados, coluna_status = st.columns([3, 1])
        with coluna_dados:
            st.write(f"**SQL:** {sql_formatado}")
            st.write(f"Encontrados {quantidade_poligonos} polígono(s) associados.")
        
        with coluna_status:
            tipo_sigla = registro_base["cd_tipo_lote"]
            tipo_extenso = self.mapeamento_tipos.get(tipo_sigla, tipo_sigla)
            st.badge(f"Lote de tipo {tipo_extenso}")

    def _render_analise_poligono(self, df_sub_poligono: pd.DataFrame, id_poligono: int) -> None:
        with st.container(border=True):
            st.subheader(f"Polígono ID: {id_poligono}")
            
            indice_maxima_importancia = df_sub_poligono["importancia_zona_para_lote"].idxmax()
            zona_principal = df_sub_poligono.loc[indice_maxima_importancia]
            maior_importancia = zona_principal["importancia_zona_para_lote"]
            
            coluna_1, coluna_2, coluna_3 = st.columns(3)
            with coluna_1:
                st.metric("Zona Predominante", zona_principal["cd_zoneamento_perimetro"])
            with coluna_2:
                st.metric("Importância da Zona", f"{maior_importancia:.1f}%")
            with coluna_3:
                interseccao_total = zona_principal["percentual_area_interseccao_total"]
                st.metric("Intersecção Total", f"{interseccao_total:.1f}%")

            if len(df_sub_poligono) == 1 or maior_importancia >= 99.9:
                st.info("Lote com apenas um zoneamento neste polígono.")
            else:
                self._render_graficos(df_sub_poligono)

    def _render_graficos(self, df_sub_poligono: pd.DataFrame) -> None:
        df_plot = df_sub_poligono.sort_values("importancia_zona_para_lote", ascending=False)
        st.bar_chart(
            df_plot, 
            x="cd_zoneamento_perimetro", 
            y="importancia_zona_para_lote",
            color="#2E7D32"
        )

    def _render_microdados(self, dataframe_lote: pd.DataFrame) -> None:
        # Implementação do expander de microdados integrado
        with st.expander("Acesse os microdados desse lote", expanded=False):
            st.dataframe(
                dataframe_lote, 
                use_container_width=True
            )

    def __call__(self, dataframe_lote: pd.DataFrame) -> None:
        if dataframe_lote is None or dataframe_lote.empty:
            st.warning("Nenhum dado para exibir.")
            return

        # Container principal com borda envolvendo toda a análise
        with st.container(border=True):
            self._render_header_geral(dataframe_lote)
            st.divider()
            
            lista_poligonos = dataframe_lote["id_pol_lote"].unique()
            for id_pol_lote in lista_poligonos:
                df_filtrado = dataframe_lote[dataframe_lote["id_pol_lote"] == id_pol_lote]
                self._render_analise_poligono(df_filtrado, id_pol_lote)
            
            st.divider()
            self._render_microdados(dataframe_lote)