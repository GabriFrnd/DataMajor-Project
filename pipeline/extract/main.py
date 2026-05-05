import pandas as pd # Manipulação e análise de dados
import chardet # Detecção de encodings

import csv # Leitura e escrita de arquivos .csv
from system import get_dataset_path # Função 'get_dataset_path', declarada no arquivo 'system.py'

def encoding_finder(path: str) -> str:
    """
    Esta função detecta o encoding do dataset com auxílio da biblioteca chardet.

    Args:
        path: str: caminho (path) do arquivo .csv em 'data/raw'.

    Returns:
        str: Encoding do dataset.
    """

    with open(path, 'rb') as file:
        # Retorno do encoder do dataset, utilizado na função 'load_dataframe'
        return chardet.detect(file.read()).get('encoding')
    
def sniffer_finder(path: str, encoding: str) -> str:
    """
    Esta função detecta o delimitador (sep) do dataset com auxílio da biblioteca csv.

    Args:
        path: str: caminho (path) do arquivo .csv em 'data/raw'.
        encoding: str: Encoding do dataset, retornado pela função 'encoding_finder'.

    Returns:
        str: Delimitador (sep) do dataset.
    """

    with open(path, 'r', encoding=encoding) as file:
        # Leitura de uma amostra do arquivo para detecção do delimitador
        sample = file.read(1024)

        # Detecção do delimitador (sep) do dataset com auxílio do 'csv.Sniffer'
        delimiter = csv.Sniffer().sniff(sample=sample).delimiter

        # Retorno do delimitador (sep) do dataset, utilizado na função 'load_dataframe'
        return delimiter

def load_dataframe() -> pd.DataFrame:
    """
    Esta função tem por objetivo realizar a leitura do dataset com auxílio da biblioteca Pandas.
    Com 'read_csv', o dataset, em formato .csv, é lido junto com seus parâmetros, encontrados nas funções anteriores.

    Returns:
        pd.DataFrame: DataFrame do projeto.
    """

    # Retorna o caminho (path) do arquivo .csv, agora em 'data/raw' (função declarada no arquivo 'system.py')
    path = get_dataset_path()

    # Retorna o encoder do dataset (função declarada neste arquivo)
    encoding = encoding_finder(path)

    # Retorna o delimitador (sep) do dataset (função declarada neste arquivo)
    sep = sniffer_finder(path, encoding)

    # Leitura do dataset, em formato .csv, com auxílio da biblioteca Pandas
    # Os atributos 'path', 'encoding' e 'sep' foram encontrados em outras funções
    data = pd.read_csv(path, encoding=encoding, sep=sep)

    # A função retorna o DataFrame do projeto
    return data