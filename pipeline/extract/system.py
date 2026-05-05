import kagglehub # Download do dataset
import os # Interação com o sistema operacional
import shutil # Operações de arquivo de alto nível

def get_dataset_path() -> str:
    """
    Esta função realiza o download do dataset, em formato .csv, via Kagglehub. Posteriormente, o traz para 
    o diretório 'data/raw', caso não esteja, pois é direcionado a um outro local.

    Returns:
        str: Caminho completo do arquivo .csv em 'data/raw'.
    """

    # Caminho (path) até o arquivo atual (system.py)
    main_file_path = os.path.abspath(__file__)

    # Retorno do caminho (path) até a raiz do projeto
    file_return = os.path.dirname(os.path.dirname(os.path.dirname(main_file_path)))

    # Caminho (path) até a pasta 'raw' (data/raw)
    raw_path = os.path.join(file_return, 'data', 'raw')

    # Caso não exista, criar o diretório 'data/raw'
    # 'exist_ok=True' para evitar erros caso o diretório já exista
    os.makedirs(raw_path, exist_ok=True)

    # Caso o arquivo .csv do dataset não esteja em 'data/raw', executar este bloco
    if not os.listdir(raw_path):
        # Download da última versão do dataset via Kagglehub
        data_path = kagglehub.dataset_download('ashishkumarak/play-store-reviews-facebook')

        # Array com listagem dos arquivos no diretório de download do dataset
        files_array = os.listdir(data_path)

        # Caminho do arquivo .csv do dataset no diretório de dowload
        kagglehub_file_path = os.path.join(data_path, files_array[0])

        # Cópia do arquivo para 'data/raw', antes localizado em outro diretório
        shutil.copy(kagglehub_file_path, raw_path)

    # Retorno do caminho do arquivo .csv, agora em 'data/raw'
    return os.path.join(raw_path, os.listdir(raw_path)[0])

# Chamada da função
# Necessário executar para funcionamento do projeto
if __name__ == '__main__':
    get_dataset_path()