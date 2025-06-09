import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Tuple
import uuid

# Load embedding model (local + fast + effective)
embedder = SentenceTransformer("all-MiniLM-L6-v2")  # Small, fast, decent performance

# In-memory index mapping: {vector_id: document metadata}
doc_id_map = {}

def init_faiss(dim: int = 384) -> faiss.IndexFlatL2:
    """
    Initializes a FAISS index for semantic search.
    """
    index = faiss.IndexFlatL2(dim)
    return index


def get_embedding(text: str) -> np.ndarray:
    """
    Converts text to vector embedding using SentenceTransformer.
    """
    return embedder.encode([text])[0]


def add_to_index(doc_id: str, text: str, index: faiss.IndexFlatL2, chunk_size: int = 500):
    """
    Splits document text into chunks, embeds them, and adds to FAISS index.
    Stores document ID to match results later.
    """
    global doc_id_map
    chunks = [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]
    embeddings = embedder.encode(chunks)

    for i, emb in enumerate(embeddings):
        uid = str(uuid.uuid4())
        doc_id_map[uid] = {
            "doc_id": doc_id,
            "chunk": chunks[i]
        }
        index.add(np.array([emb]))


def search_documents(query: str, index: faiss.IndexFlatL2, documents_db: List[Dict], top_k: int = 5) -> List[Dict]:
    """
    Searches the FAISS index for the top_k chunks matching the query.
    Maps those chunks back to document data.
    """
    global doc_id_map
    query_vector = embedder.encode([query])
    distances, indices = index.search(np.array(query_vector), top_k)

    results = []
    for idx in indices[0]:
        if idx >= len(doc_id_map):
            continue
        chunk_id = list(doc_id_map.keys())[idx]
        meta = doc_id_map[chunk_id]
        doc = next((d for d in documents_db if d["id"] == meta["doc_id"]), None)
        if doc:
            results.append({
                "id": doc["id"],
                "name": doc["name"],
                "text": meta["chunk"]
            })
    return results
