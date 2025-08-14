# app/pinecone_client.py
import os
from pinecone import Pinecone, ServerlessSpec
from dotenv import load_dotenv

load_dotenv()

pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
INDEX_NAME = "coveriq-index"

def init_pinecone():
    """Initializes the Pinecone index if it doesn't exist."""
    if INDEX_NAME not in pc.list_indexes().names():
        pc.create_index(
            name=INDEX_NAME,
            dimension=768,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1")
        )
    return pc.Index(INDEX_NAME)

index = init_pinecone()

def upsert_vectors(vectors: list):
    """Upserts vectors into the main Pinecone index."""
    if not vectors:
        return
    # We no longer use namespaces
    index.upsert(vectors=vectors)

def query_vectors(query_embedding: list[float], top_k: int = 5) -> list[dict]:
    """Queries the Pinecone index for the most similar vectors."""
    if not query_embedding:
        return []
        
    results = index.query(
        vector=query_embedding,
        top_k=top_k,
        include_metadata=True
    )
    # Return the full match data, including metadata with the source file
    return results.get('matches', [])
