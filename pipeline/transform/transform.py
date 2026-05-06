import pandas as pd  # Manipulação e análise de dados
import os             # Interação com o sistema operacional
import re             # Expressões regulares para limpeza de texto


def get_paths() -> tuple[str, str]:
    """
    Resolve os caminhos de entrada (data/raw) e saída (data/processed)
    com base na localização deste script, independente de onde o projeto
    estiver clonado.

    Returns:
        tuple[str, str]: (caminho do arquivo CSV em raw, caminho da pasta processed)
    """
    # Caminho até o arquivo atual (transform.py)
    main_file_path = os.path.abspath(__file__)

    # Retorno até a raiz do projeto (pipeline/transform/ → raiz)
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(main_file_path)))

    raw_path = os.path.join(project_root, 'data', 'raw')
    processed_path = os.path.join(project_root, 'data', 'processed')

    # Criação do diretório 'data/processed', caso não exista
    os.makedirs(processed_path, exist_ok=True)

    # Localiza o arquivo .csv dentro de 'data/raw'
    raw_files = os.listdir(raw_path)
    if not raw_files:
        raise FileNotFoundError(
            "Nenhum arquivo encontrado em 'data/raw'. "
            "Execute o script de Extract primeiro: python pipeline/extract/system.py"
        )

    csv_file = os.path.join(raw_path, raw_files[0])
    return csv_file, processed_path


def load_raw(csv_path: str) -> pd.DataFrame:
    """
    Carrega o arquivo CSV bruto para um DataFrame.

    Args:
        csv_path (str): Caminho completo do arquivo CSV.

    Returns:
        pd.DataFrame: Dados brutos carregados.
    """
    print(f"[1/6] Carregando dados brutos de: {csv_path}")

    df = pd.read_csv(
        csv_path,
        dtype={
            'reviewId':            str,
            'userName':            str,
            'content':             str,
            'score':               'Int64',   # Int64 (nullable) para lidar com NaN
            'thumbsUpCount':       'Int64',
            'reviewCreatedVersion': str,
            'at':                  str,
            'appVersion':          str,
        }
    )

    print(f"    → {len(df):,} linhas | {df.shape[1]} colunas carregadas")
    return df


def remove_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    """
    Remove linhas com reviewId duplicado, mantendo a ocorrência mais recente.
    reviewId é o identificador único de cada avaliação na Play Store.

    Args:
        df (pd.DataFrame): DataFrame com possíveis duplicatas.

    Returns:
        pd.DataFrame: DataFrame sem duplicatas de reviewId.
    """
    print("[2/6] Removendo duplicatas...")

    before = len(df)

    # Ordenar por 'at' antes de desduplicar garante que a review mais recente
    # seja mantida em caso de re-envio pelo usuário
    df = df.sort_values('at', ascending=False)
    df = df.drop_duplicates(subset='reviewId', keep='first')
    df = df.reset_index(drop=True)

    removed = before - len(df)
    print(f"    → {removed:,} duplicata(s) removida(s) | {len(df):,} linhas restantes")
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
    print("[3/6] Tratando valores nulos...")

    # Descarta reviews sem texto (inúteis para mineração)
    before = len(df)
    df = df.dropna(subset=['content'])
    dropped = before - len(df)
    if dropped:
        print(f"    → {dropped} linha(s) sem 'content' descartada(s)")

    # Versões ausentes → valor sentinela legível
    for col in ['reviewCreatedVersion', 'appVersion']:
        nulls = df[col].isna().sum()
        if nulls:
            df[col] = df[col].fillna('desconhecida')
            print(f"    → {nulls:,} nulo(s) em '{col}' preenchidos com 'desconhecida'")

    return df.reset_index(drop=True)


def normalize_types(df: pd.DataFrame) -> pd.DataFrame:
    """
    Padroniza os tipos de dados das colunas:
      - 'at' → datetime (UTC)
      - 'score' e 'thumbsUpCount' → int (agora que não há mais nulos)
      - Colunas de versão → string limpa (remove sufixo '.0' de floats lidos como str)

    Args:
        df (pd.DataFrame): DataFrame com tipos brutos.

    Returns:
        pd.DataFrame: DataFrame com tipos padronizados.
    """
    print("[4/6] Normalizando tipos de dados...")

    # Converte 'at' para datetime; erros viram NaT (descartados a seguir)
    df['at'] = pd.to_datetime(df['at'], errors='coerce', utc=True)
    nat_count = df['at'].isna().sum()
    if nat_count:
        df = df.dropna(subset=['at'])
        print(f"    → {nat_count} data(s) inválida(s) em 'at' descartada(s)")

    # Colunas numéricas: converte de Int64 (nullable) para int64 padrão
    df['score']         = df['score'].astype(int)
    df['thumbsUpCount'] = df['thumbsUpCount'].astype(int)

    # Remove sufixo '.0' de versões que foram lidas como float pelo CSV
    # Ex.: "545.0.0.43.63" já está ok; "545.0" → vem de linhas com float puro
    for col in ['reviewCreatedVersion', 'appVersion']:
        df[col] = df[col].str.strip()

    print(f"    → Tipos ajustados com sucesso")
    return df


def clean_text(df: pd.DataFrame) -> pd.DataFrame:
    """
    Limpa e padroniza a coluna 'content' (texto da avaliação):
      - Remove espaços em branco no início e fim
      - Colapsa múltiplos espaços/quebras de linha em um único espaço
      - Remove caracteres de controle (exceto espaço normal)

    Também limpa 'userName' (espaços e caracteres invisíveis).

    Args:
        df (pd.DataFrame): DataFrame com texto bruto.

    Returns:
        pd.DataFrame: DataFrame com texto limpo.
    """
    print("[5/6] Limpando e padronizando texto...")

    # Remove caracteres de controle e normaliza espaços
    def clean(text: str) -> str:
        text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)  # Ctrl chars
        text = re.sub(r'[ \t\r\n]+', ' ', text)                         # Espaços múltiplos
        return text.strip()

    df['content']  = df['content'].apply(clean)
    df['userName'] = df['userName'].str.strip()

    # Descarta reviews que ficaram vazias após a limpeza
    before = len(df)
    df = df[df['content'].str.len() > 0].reset_index(drop=True)
    dropped = before - len(df)
    if dropped:
        print(f"    → {dropped} review(s) vazia(s) após limpeza descartada(s)")

    print(f"    → Limpeza de texto concluída")
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
    print("[6/6] Enriquecendo com colunas derivadas...")

    df['review_length'] = df['content'].str.len()
    df['word_count']    = df['content'].str.split().str.len()

    # Mapeamento de score → sentimento
    sentiment_map = {1: 'negativo', 2: 'negativo', 3: 'neutro', 4: 'positivo', 5: 'positivo'}
    df['sentiment'] = df['score'].map(sentiment_map)

    df['review_year']  = df['at'].dt.year
    df['review_month'] = df['at'].dt.month

    print(f"    → Colunas adicionadas: review_length, word_count, sentiment, review_year, review_month")
    return df


def save_processed(df: pd.DataFrame, processed_path: str) -> str:
    """
    Salva o DataFrame transformado em formato CSV comprimido (gzip)
    no diretório 'data/processed'.

    O uso de gzip reduz o tamanho do arquivo em ~70% sem perda de dados,
    e o pandas consegue ler arquivos .csv.gz diretamente.

    Args:
        df (pd.DataFrame): DataFrame final transformado.
        processed_path (str): Caminho da pasta 'data/processed'.

    Returns:
        str: Caminho completo do arquivo gerado.
    """
    output_file = os.path.join(processed_path, 'facebook_reviews_clean.csv.gz')
    df.to_csv(output_file, index=False, compression='gzip')
    size_mb = os.path.getsize(output_file) / (1024 * 1024)
    print(f"\n✅ Arquivo salvo em: {output_file}")
    print(f"   Tamanho: {size_mb:.1f} MB | {len(df):,} linhas | {df.shape[1]} colunas")
    return output_file


def transform() -> str:
    """
    Executa o pipeline completo de transformação:
        load → remove_duplicates → handle_nulls →
        normalize_types → clean_text → enrich → save

    Returns:
        str: Caminho do arquivo processado gerado em 'data/processed'.
    """
    print("=" * 55)
    print("  DATA MAJOR — Pipeline Transform")
    print("=" * 55)

    csv_path, processed_path = get_paths()

    df = load_raw(csv_path)
    df = remove_duplicates(df)
    df = handle_nulls(df)
    df = normalize_types(df)
    df = clean_text(df)
    df = enrich(df)

    output_path = save_processed(df, processed_path)

    print("\nResumo do dataset processado:")
    print(df[['score', 'sentiment', 'review_length', 'word_count']].describe(include='all').to_string())
    print("=" * 55)

    return output_path


# Execução direta do script
if __name__ == '__main__':
    transform()