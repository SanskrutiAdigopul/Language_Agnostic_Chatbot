import faiss
import numpy as np
from Backend.database.connect import chunks_collection

def build_faiss_index():
    """
    Load embeddings from MongoDB and build a FAISS index in memory.
    Returns (index, ids) where ids maps FAISS positions back to chunk_ids.
    """
    chunks = list(chunks_collection.find({}, {"embedding": 1, "chunk_id": 1, "_id": 0}))
    if not chunks:
        return None, []

    embeddings = [chunk["embedding"] for chunk in chunks]
    ids = [chunk["chunk_id"] for chunk in chunks]

    dim = len(embeddings[0])  # embedding dimension
    index = faiss.IndexFlatL2(dim)  # L2 distance index
    index.add(np.array(embeddings).astype("float32"))

    return index, ids