# Documentação Técnica: GeoSampaScraper

Classe desenvolvida para automatizar o fluxo de download e processamento de dados do portal GeoSampa da Prefeitura de São Paulo, lidando com autenticação de sessão, downloads via stream e extração automatizada.

## Visão Geral

A classe `GeoSampaScraper` orquestra o acesso ao portal contornando as validações de sessão ASP.NET e garantindo a eficiência de memória ao processar grandes volumes de dados (como bases de IPTU).

## Atributos de Classe

- `ifr_url`: URL de interface usada para inicializar o contexto da sessão.
- `download_url`: URL do subdomínio de download que fornece o stream de bits.
- `accepted_formats`: Conjunto de formatos permitidos para validação de entrada.

## Métodos

### `__call__(arq_param, file_type="XLS_CSV", **read_file_kwargs)`
Torna a classe chamável. Ponto de entrada que inicia o pipeline.
- `arq_param`: Caminho do arquivo no servidor.
- `file_type`: Formato solicitado (padrão: `XLS_CSV`).
- `read_file_kwargs`: Argumentos repassados para `pd.read_csv` ou `pd.read_excel`.

### `pipeline(arq_param, file_type, **read_file_kwargs)`
Gerencia o fluxo lógico dentro de um diretório temporário:
1. Valida o tipo de arquivo.
2. Realiza o download via stream.
3. Valida se o conteúdo é binário (evita HTML de erro).
4. Extrai o conteúdo se estiver compactado (ZIP).
5. Carrega os dados em um DataFrame.

### `fetch_and_save_stream(arq_param, file_type, temp_dir)`
Realiza a requisição inicial para captura de cookies e executa o download em chunks de 8KB para otimização de RAM.

### `validate_content(file_path)`
Método de segurança que inspeciona o cabeçalho do arquivo baixado para garantir que o servidor não retornou uma página de erro HTML em vez dos dados solicitados.

### `extract_if_zip(file_path, temp_dir)`
Verifica se o download resultou em um ZIP. Em caso positivo, extrai o arquivo de dados (.csv ou .xlsx) e retorna o caminho para o arquivo descompactado.

### `load_data(file_path, **read_file_kwargs)`
Identifica a extensão real do arquivo no disco e utiliza o motor apropriado do Pandas para carregar o DataFrame.

## Exemplo de Uso

```python
scraper = GeoSampaScraper()
param_iptu = "12_Cadastro\\\\IPTU_INTER\\\\XLS_CSV\\\\IPTU_2026"

# Carregamento direto para memória
df = scraper(
    param_iptu, 
    sep=';', 
    encoding='latin-1', 
    on_bad_lines='skip'
)

print(df.info())