import os
import requests
import zipfile
import tempfile
import pandas as pd
from io import BytesIO
from typing import Set, List, Any

class GeoSampaScraper:
    ifr_url: str = "https://geosampa.prefeitura.sp.gov.br/PaginasPublicas/downloadIfr.aspx"
    download_url: str = "https://download.geosampa.prefeitura.sp.gov.br/PaginasPublicas/downloadArquivo.aspx"
    accepted_formats: Set[str] = {"CSV", "XLSX", "XLS_CSV"}

    def __init__(self) -> None:
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Referer": "https://geosampa.prefeitura.sp.gov.br/",
            "Connection": "keep-alive"
        })

    def check_file_type(self, file_type: str) -> str:
        normalized_type = file_type.upper()
        if normalized_type not in self.accepted_formats:
            raise NotImplementedError(f"O formato {file_type} não é suportado. Tipos aceitos: {self.accepted_formats}")
        return normalized_type

    def validate_content(self, file_path: str) -> None:
        if not zipfile.is_zipfile(file_path):
            with open(file_path, "rb") as f:
                header = f.read(100).lower()
                if b"<html" in header or b"<!doctype html" in header:
                    raise ValueError("O conteúdo baixado é um HTML de erro, não um arquivo de dados válido.")

    def save_tmp_file(self, temp_path: str, temp_dir: str, file_type: str) -> str:
        is_zip = zipfile.is_zipfile(temp_path)
        extension = "zip" if is_zip else file_type.lower()
        final_path = os.path.join(temp_dir, f"data.{extension}")
        os.rename(temp_path, final_path)
        return final_path

    def fetch_and_save_stream(self, arq_param: str, file_type: str, temp_dir: str) -> str:
        params = {
            "orig": "DownloadCamadas",
            "arq": arq_param,
            "arqTipo": file_type
        }
        
        #faz requisicao inicial para pegar os cookies necessários para o download
        self.session.get(self.ifr_url, params=params)
        
        raw_temp_path = os.path.join(temp_dir, "downloaded_raw_content")
        
        with self.session.get(self.download_url, params=params, stream=True) as response:
            response.raise_for_status()
            
            with open(raw_temp_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            self.validate_content(raw_temp_path)
            return self.save_tmp_file(raw_temp_path, temp_dir, file_type)

    def check_zip(self, zip_ref: zipfile.ZipFile) -> List[str]:
        files = zip_ref.namelist()
        target_files = [f for f in files if f.lower().endswith(('.csv', '.xlsx', '.xls'))]
        
        if not target_files:
            raise FileNotFoundError("Nenhum arquivo de dados (CSV/XLSX) encontrado no ZIP.")
        
        if len(target_files) > 1:
            target_files = [f for f in target_files if not f.startswith('__MACOSX')]
            if len(target_files) > 1:
                raise NotImplementedError("O arquivo ZIP contém múltiplos arquivos de dados.")
            
        return target_files

    def extract_if_zip(self, file_path: str, temp_dir: str) -> str:
        if not zipfile.is_zipfile(file_path):
            return file_path
            
        with zipfile.ZipFile(file_path, "r") as zip_ref:
            target_files = self.check_zip(zip_ref)
            target_file = target_files[0]
            zip_ref.extract(target_file, path=temp_dir)
            return os.path.join(temp_dir, target_file)

    def load_data(self, file_path: str, **read_file_kwargs: Any) -> pd.DataFrame:
        extension = os.path.splitext(file_path)[1].lower()
        
        if extension == ".csv":
            default_args = {"sep": None, "engine": "python", "encoding": "utf-8"}
            default_args.update(read_file_kwargs)
            return pd.read_csv(file_path, **default_args)
        elif extension in [".xlsx", ".xls"]:
            return pd.read_excel(file_path, **read_file_kwargs)
        else:
            raise NotImplementedError(f"Extensão de arquivo {extension} não reconhecida.")

    def pipeline(self, arq_param: str, file_type: str, **read_file_kwargs: Any) -> pd.DataFrame:
        normalized_type = self.check_file_type(file_type)
        
        with tempfile.TemporaryDirectory() as tmp_dir:
            downloaded_path = self.fetch_and_save_stream(arq_param, normalized_type, tmp_dir)
            final_path = self.extract_if_zip(downloaded_path, tmp_dir)
            return self.load_data(final_path, **read_file_kwargs)

    def __call__(self, arq_param: str, file_type: str = "XLS_CSV", **read_file_kwargs: Any) -> pd.DataFrame:
        return self.pipeline(arq_param, file_type, **read_file_kwargs)

if __name__ == "__main__":

    scraper = GeoSampaScraper()
    
    try:
        df = scraper(
            "12_Cadastro\\\\IPTU_INTER\\\\XLS_CSV\\\\IPTU_2026", 
            file_type="XLS_CSV",
            sep=';', 
            encoding='latin-1', 
            on_bad_lines='skip'
        )
        print(df.head())
    except Exception as e:
        print(f"Erro no processamento: {e}")