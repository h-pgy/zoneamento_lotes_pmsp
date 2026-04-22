from typing import Optional
from utils.io.parquet import load_parquet
from .load_df import load_lote_data
import pandas as pd

class LoteDataFilter:

    def __init__(self, df_lotes: Optional[pd.DataFrame] = None):
        self.dataframe_lotes = df_lotes if df_lotes is not None else load_lote_data()
        self.ultimo_sql_buscado = None
        
    def _gerar_sql(self, cd_setor: int, cd_quadra: int, cd_lote: int, cd_condominio: int) -> str:
        setor_str = str(cd_setor).zfill(3)
        quadra_str = str(cd_quadra).zfill(3)
        lote_str = str(cd_lote).zfill(4)
        condominio_str = str(cd_condominio).zfill(2)
        return f"{setor_str}.{quadra_str}.{lote_str}-{condominio_str}"

    def _buscar_registros_lotes(self, sql_formatado: str, cd_tipo_lote: str) -> pd.DataFrame:
        resultado_filtrado = self.dataframe_lotes[(self.dataframe_lotes["sql"] == sql_formatado) \
                                                  & (self.dataframe_lotes["cd_tipo_lote"] == cd_tipo_lote)]
        self.ultimo_sql_buscado = sql_formatado + f" (Tipo Lote: {cd_tipo_lote})"
        return resultado_filtrado.reset_index(drop=True)
    
    def pipeline(self, cd_setor: int, cd_quadra: int, cd_lote: int, cd_condominio: int = 0, cd_tipo_lote='F') -> pd.DataFrame:
        sql_gerado = self._gerar_sql(cd_setor, cd_quadra, cd_lote, cd_condominio)
        return self._buscar_registros_lotes(sql_gerado, cd_tipo_lote)
    def __call__(self, cd_setor: int, cd_quadra: int, cd_lote: int, cd_condominio: int = 0, cd_tipo_lote='F') -> pd.DataFrame:
        
        return self.pipeline(cd_setor, cd_quadra, cd_lote, cd_condominio, cd_tipo_lote)