import os    # Interação com o sistema operacional
import sys   # Manipulação do caminho de busca de módulos
import re    # Expressões regulares para limpeza de texto
import pandas as pd  # Manipulação e análise de dados


def get_paths() -> tuple[str, str]:
    """
    Resolve os caminhos de importação do Extract e de saída (data/processed)
    com base na localização deste script.

    Returns:
        tuple[str, str]: (caminho de pipeline/extract, caminho de data/processed)
    """
    # Caminho (path) até o arquivo atual (transform.py)
    main_file_path = os.path.abspath(__file__)

    # Retorno do caminho (path) até a raiz do projeto
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(main_file_path)))

    # Caminho (path) até a pasta 'extract' (pipeline/extract)
    extract_path = os.path.join(project_root, 'pipeline', 'extract')

    # Caminho (path) até a pasta 'processed' (data/processed)
    processed_path = os.path.join(project_root, 'data', 'processed')

    # Adição do caminho 'pipeline/extract' ao sys.path, permitindo a importação dos módulos
    sys.path.append(extract_path)

    # Criação do diretório 'data/processed', caso não exista
    os.makedirs(processed_path, exist_ok=True)

    return extract_path, processed_path


def remove_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    """
    Remove linhas com reviewId duplicado, mantendo a ocorrência mais recente.
    reviewId é o identificador único de cada avaliação na Play Store.

    Args:
        df (pd.DataFrame): DataFrame com possíveis duplicatas.

    Returns:
        pd.DataFrame: DataFrame sem duplicatas de reviewId.
    """
    before = len(df)

    # Ordenação por data garante que a review mais recente seja mantida
    df = df.sort_values('at', ascending=False)
    df = df.drop_duplicates(subset='reviewId', keep='first')
    df = df.reset_index(drop=True)

    print(f'[1/5] Duplicatas removidas: {before - len(df):,} | Linhas restantes: {len(df):,}')
    return df


def handle_nulls(df: pd.DataFrame) -> pd.DataFrame:
    """
    Trata valores nulos:
      - 'content' nulo → linha descartada (sem texto, sem análise possível)
      - 'reviewCreatedVersion' / 'appVersion' nulos → preenchidos com 'desconhecida'

    Args:
        df (pd.DataFrame): DataFrame com possíveis nulos.

    Returns:
        pd.DataFrame: DataFrame com nulos tratados.
    """
    # Descarte de reviews sem texto
    before = len(df)
    df = df.dropna(subset=['content'])
    print(f'[2/5] Reviews sem texto descartadas: {before - len(df)}')

    # Preenchimento de versões ausentes com valor sentinela legível
    for col in ['reviewCreatedVersion', 'appVersion']:
        nulls = df[col].isna().sum()
        df[col] = df[col].fillna('desconhecida')
        print(f'     Nulos em \'{col}\' preenchidos: {nulls:,}')

    return df.reset_index(drop=True)


def normalize_types(df: pd.DataFrame) -> pd.DataFrame:
    """
    Padroniza os tipos de dados das colunas:
      - 'at' → datetime com fuso UTC (correto para análise temporal)
      - 'score' e 'thumbsUpCount' → int64
      - Colunas de versão → string limpa

    Args:
        df (pd.DataFrame): DataFrame com tipos brutos.

    Returns:
        pd.DataFrame: DataFrame com tipos padronizados.
    """
    # Conversão da coluna 'at' para datetime com fuso UTC
    df['at'] = pd.to_datetime(df['at'], errors='coerce', utc=True)

    # Descarte de datas inválidas (NaT)
    nat = df['at'].isna().sum()
    if nat:
        df = df.dropna(subset=['at'])
        print(f'[3/5] Datas inválidas descartadas: {nat}')
    else:
        print('[3/5] Tipos normalizados com sucesso')

    # Conversão de colunas numéricas
    df['score']         = df['score'].astype(int)
    df['thumbsUpCount'] = df['thumbsUpCount'].astype(int)

    # Limpeza de espaços nas colunas de versão
    for col in ['reviewCreatedVersion', 'appVersion']:
        df[col] = df[col].str.strip()

    return df.reset_index(drop=True)


def clean_text(df: pd.DataFrame) -> pd.DataFrame:
    """
    Limpa e padroniza a coluna 'content' (texto da avaliação):
      - Remove caracteres de controle
      - Colapsa múltiplos espaços/quebras de linha em um único espaço

    Também limpa 'userName' (espaços e caracteres invisíveis).

    Args:
        df (pd.DataFrame): DataFrame com texto bruto.

    Returns:
        pd.DataFrame: DataFrame com texto limpo.
    """
    def _clean(text: str) -> str:
        text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)  # Caracteres de controle
        text = re.sub(r'[ \t\r\n]+', ' ', text)                         # Espaços múltiplos
        return text.strip()

    df['content']  = df['content'].apply(_clean)
    df['userName'] = df['userName'].str.strip()

    # Descarte de reviews que ficaram vazias após a limpeza
    before = len(df)
    df = df[df['content'].str.len() > 0].reset_index(drop=True)
    print(f'[4/5] Limpeza de texto concluída | Reviews vazias descartadas: {before - len(df)}')
    return df


def enrich(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adiciona colunas derivadas que facilitarão a etapa de Mineração:
      - 'review_length'  → número de caracteres do conteúdo
      - 'word_count'     → número de palavras do conteúdo
      - 'sentiment'      → rótulo textual baseado no score
                           (1-2: negativo | 3: neutro | 4-5: positivo)
      - 'review_year'    → ano da avaliação (para análises temporais)
      - 'review_month'   → mês da avaliação

    Args:
        df (pd.DataFrame): DataFrame limpo e normalizado.

    Returns:
        pd.DataFrame: DataFrame enriquecido com colunas derivadas.
    """
    # Métricas de texto
    df['review_length'] = df['content'].str.len()
    df['word_count']    = df['content'].str.split().str.len()

    # Classificação de sentimento baseada no score
    sentiment_map = {1: 'negativo', 2: 'negativo', 3: 'neutro', 4: 'positivo', 5: 'positivo'}
    df['sentiment'] = df['score'].map(sentiment_map)

    # Colunas temporais
    df['review_year']  = df['at'].dt.year
    df['review_month'] = df['at'].dt.month

    print('[5/5] Colunas derivadas adicionadas: review_length, word_count, sentiment, review_year, review_month')
    return df


def transform() -> pd.DataFrame:
    """
    Executa o pipeline completo de transformação:
        load_dataframe → remove_duplicates → handle_nulls →
        normalize_types → clean_text → enrich → salva em data/processed/

    Returns:
        pd.DataFrame: DataFrame processado.
    """
    print('=' * 50)
    print('  DATA MAJOR — Pipeline Transform')
    print('=' * 50)

    _, processed_path = get_paths()

    # Importação da função 'load_dataframe', declarada no arquivo 'main.py' (Extract)
    from main import load_dataframe  # type: ignore

    # Carregamento do DataFrame bruto via Extract
    df = load_dataframe()
    print(f'Dataset carregado: {len(df):,} linhas | {df.shape[1]} colunas\n')

    df = remove_duplicates(df)
    df = handle_nulls(df)
    df = normalize_types(df)
    df = clean_text(df)
    df = enrich(df)

    # Caminho do arquivo de saída
    output_file = os.path.join(processed_path, 'facebook_reviews_clean.csv.gz')

    # Salvamento do DataFrame processado em formato CSV comprimido
    # O uso de gzip reduz o tamanho do arquivo em ~70% sem perda de dados
    df.to_csv(output_file, index=False, compression='gzip')

    size_mb = os.path.getsize(output_file) / (1024 * 1024)
    print(f'\nArquivo salvo em: {output_file}')
    print(f'Tamanho: {size_mb:.1f} MB | {len(df):,} linhas | {df.shape[1]} colunas')
    print('=' * 50)

    # Retorno do DataFrame processado
    return df


# Chamada da função
# Necessário executar para funcionamento do projeto
if __name__ == '__main__':
    transform()
