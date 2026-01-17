from chromadb import PersistentClient
from chromadb.utils import embedding_functions
from app.config import settings

def get_collection():
    client = PersistentClient(path=settings.CHROMA_DIR)

    embed_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )

    return client.get_or_create_collection(
        name=settings.COLLECTION_NAME,
        embedding_function=embed_fn
    )
