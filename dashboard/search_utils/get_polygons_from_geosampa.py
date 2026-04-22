from utils.wfs_geosampa import GeoSampaWFSFetcher
import geopandas as gpd

def get_lote_polygon(lote_pol_id:str)->gpd.GeoDataFrame:
    """
    Função para pegar o polígono do lote a partir do id_pol_lote, utilizando a camada 'lote_cidadao' do GeoSampa.
    """

    fetcher = GeoSampaWFSFetcher(start_index=0, verbose=False)
    camada_lote ='lote_cidadao'
    filtro_pol_lote = 'cd_identificador = {}'.format(lote_pol_id)
    fetcher = GeoSampaWFSFetcher()
    lote = []
    for batch in fetcher(camada_lote, cql_filter=filtro_pol_lote):
        lote.extend(batch)
    gdf_lote = gpd.GeoDataFrame.from_features(lote, crs='EPSG:31983')

    if not len(gdf_lote):
        raise ValueError(f'Nenhum lote encontrado para o id_pol_lote {lote_pol_id}')
    if not len(gdf_lote)==1:
        raise ValueError(f'Múltiplos lotes encontrados para o id_pol_lote {lote_pol_id}')

    return gdf_lote


def get_perimetros_zonas(ls_cds_perimetros:list[str])->gpd.GeoDataFrame:
    """
    Função para pegar os perímetros de zoneamento a partir de uma lista de códigos de perímetros.
    """
    fetcher = GeoSampaWFSFetcher()
    camada_zoneamento = 'perimetro_zona_lei_18177_24'
    codigos_perimetros_formatados = ", ".join([f"'{item}'" for item in ls_cds_perimetros])
    filtro_lista = f"cd_identificador IN ({codigos_perimetros_formatados})"
    
    perimetros_selecionados = []
    for batch in fetcher(camada_zoneamento, cql_filter=filtro_lista):
        perimetros_selecionados.extend(batch)
    gdf_perimetros = gpd.GeoDataFrame.from_features(perimetros_selecionados, crs='EPSG:31983')

    return gdf_perimetros



   