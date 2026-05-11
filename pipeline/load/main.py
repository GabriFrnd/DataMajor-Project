import os
from pathlib import Path

import pandas as pd
from pymongo.errors import ServerSelectionTimeoutError
from pymongo import ASCENDING, DESCENDING, MongoClient, ReplaceOne


def get_paths() -> tuple[Path, Path]:
    """
    Resolve os caminhos do projeto para localizar o arquivo processado e o load.

    Returns:
        tuple[Path, Path]: (raiz do projeto, arquivo processado)
    """
    project_root = Path(__file__).resolve().parents[2]
    processed_file = project_root / 'data' / 'processed' / 'facebook_reviews_clean.csv.gz'
    return project_root, processed_file


def get_mongo_client() -> MongoClient:
    """
    Cria o cliente MongoDB usando a variável de ambiente MONGODB_URI quando existir.

    Returns:
        MongoClient: cliente conectado ao MongoDB.
    """
    mongo_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017')
    return MongoClient(mongo_uri)


def ensure_mongo_available(client: MongoClient) -> None:
    """
    Valida se o servidor MongoDB está acessível antes de iniciar a carga.

    Args:
        client (MongoClient): cliente MongoDB já configurado.

    Raises:
        ServerSelectionTimeoutError: quando o servidor não responde.
    """
    client.admin.command('ping')


def load_processed_dataframe(path: Path) -> pd.DataFrame:
    """
    Carrega o arquivo tratado gerado pela etapa de transform.

    Args:
        path (Path): caminho do arquivo CSV comprimido.

    Returns:
        pd.DataFrame: dados tratados prontos para carga.
    """
    if not path.exists():
        raise FileNotFoundError(
            f'Arquivo processado não encontrado em {path}. Execute a etapa de transform antes do load.'
        )

    return pd.read_csv(path, compression='gzip')


def dataframe_to_documents(df: pd.DataFrame) -> list[dict]:
    """
    Converte o DataFrame em documentos serializáveis para o MongoDB.

    Args:
        df (pd.DataFrame): DataFrame tratado.

    Returns:
        list[dict]: documentos prontos para inserção.
    """
    documents = df.to_dict(orient='records')
    for document in documents:
        document['load_source'] = 'facebook_reviews_clean.csv.gz'
    return documents


def load_to_mongodb(
    database_name: str = 'data_major',
    collection_name: str = 'facebook_reviews',
    batch_size: int = 1000,
    drop_existing: bool = False,
) -> dict:
    """
    Executa a carga do dataset tratado em uma collection MongoDB.

    Args:
        database_name (str): nome do banco de dados.
        collection_name (str): nome da collection de destino.
        batch_size (int): quantidade de documentos por lote.
        drop_existing (bool): se True, recria a collection antes da carga.

    Returns:
        dict: estatísticas da carga.
    """
    project_root, processed_file = get_paths()
    dataframe = load_processed_dataframe(processed_file)
    documents = dataframe_to_documents(dataframe)

    client = get_mongo_client()
    try:
        ensure_mongo_available(client)
    except ServerSelectionTimeoutError as exc:
        raise RuntimeError(
            'Não foi possível conectar ao MongoDB. Verifique se o serviço está rodando em '
            'localhost:27017 ou ajuste MONGODB_URI para o endereço correto.'
        ) from exc

    database = client[database_name]
    collection = database[collection_name]

    if drop_existing:
        collection.drop()

    inserted_count = 0
    for start_index in range(0, len(documents), batch_size):
        batch = documents[start_index:start_index + batch_size]
        if not batch:
            continue

        operations = [
            ReplaceOne({'reviewId': document['reviewId']}, document, upsert=True)
            for document in batch
        ]
        result = collection.bulk_write(operations, ordered=False)
        inserted_count += result.upserted_count + result.modified_count

    collection.create_index([('reviewId', ASCENDING)], unique=True)
    collection.create_index([('at', DESCENDING)])
    collection.create_index([('sentiment', ASCENDING)])

    metadata = {
        'source_file': str(processed_file),
        'database': database_name,
        'collection': collection_name,
        'documents_loaded': inserted_count,
        'project_root': str(project_root),
    }
    database['load_metadata'].insert_one(metadata)

    return {
        'database': database_name,
        'collection': collection_name,
        'documents_loaded': inserted_count,
        'source_file': str(processed_file),
    }


if __name__ == '__main__':
    result = load_to_mongodb()
    print(
        f"Load concluído: {result['documents_loaded']} documentos inseridos em "
        f"{result['database']}.{result['collection']}"
    )