## Documentação Técnica: GeoSampaWFSFetcher

Esta classe foi projetada para facilitar a extração massiva de dados geoespaciais da plataforma **GeoSampa** via serviço **WFS (Web Feature Service)**. Ela gerencia automaticamente a paginação de grandes volumes de dados, permitindo a iteração por lotes (batches) para evitar sobrecarga de memória e timeouts de rede.

---

### Funcionalidades Principais

* **Paginação Automática**: Utiliza os parâmetros `startIndex` e `count` para navegar por bases que superam o limite de retorno do servidor (ex: mais de 1,6 milhão de lotes).
* **Interface Geradora (Generator)**: Implementa um padrão de projeto que devolve os dados em blocos, permitindo processamento em tempo real sem carregar todo o dataset na RAM.
* **Abstração de Camadas**: Embora configurada por padrão para o namespace `geoportal`, pode ser utilizada para qualquer camada disponível no GeoServer do GeoSampa.
* **Flexibilidade de Query**: Suporta parâmetros adicionais como `cql_filter` para buscas específicas (ex: filtrar por um SQL ou Distrito específico).
* **Controle de Estado**: Mantém rastreio interno de quantos registros já foram obtidos e o índice atual da paginação.

---

### Estrutura da Classe

#### Atributos de Configuração
* `domain`: O domínio base do serviço (wfs.geosampa.prefeitura.sp.gov.br).
* `endpoint`: O caminho específico do GeoServer.
* `service` / `version`: Configurações padrão do protocolo WFS (WFS 1.0.0).
* `namespace`: O workspace padrão no GeoServer (`geoportal`).

#### Métodos Principais
* `__init__(count=5000)`: Inicializa o buscador com o tamanho do lote desejado.
* `gen_get_features_parameters()`: Monta o dicionário de parâmetros da URL, injetando filtros personalizados.
* `get_layer_data()`: Executa a requisição HTTP e valida o status da resposta, levantando exceções em caso de erro.
* `fetch_all_batches()`: A lógica central que controla o loop de paginação e dá `yield` em cada lista de features.
* `__call__(nome_camada, **query_parameters)`: Atalho semântico para iniciar a busca.

---

### Exemplo de Uso

```python
# Instancia o buscador com lotes de 10.000 registros
fetcher = GeoSampaWFSFetcher(count=10000)

# Define um filtro opcional (exemplo: apenas lotes de um setor específico)
filtros = {
    "cql_filter": "setor='042'"
}

# Itera sobre os batches de resultados
for batch in fetcher("lote_cidadao", **filtros):
    print(f"Processando bloco de {len(batch)} features...")
    print(f"Progresso total: {fetcher.features_fetched_count} registros.")
    
    # Aqui você pode salvar no banco de dados ou processar com GeoPandas
    # processar_dados(batch)
```

---

### Tratamento de Erros

A classe utiliza `response.raise_for_status()`, garantindo que falhas de conexão, erros de permissão (403) ou instabilidades no servidor (500/504) interrompam a execução de forma explícita, facilitando a depuração em pipelines de dados.