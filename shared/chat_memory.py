"""Semantic chat memory backed by SQL embeddings.

Functions are fault-tolerant and degrade gracefully when the database
or embedding APIs are unavailable.

Design:
  - generate_embedding(text): attempts Azure OpenAI embeddings, then OpenAI,
    then falls back to a lightweight local hashing embedding (fixed dim=256).
  - store_embedding(message_id, embedding, model): persists embedding bytes
    to [dbo].[ChatMessageEmbeddings]. Float32 little-endian layout.
  - fetch_similar_messages(query_embedding, top_k=5, session_id=None): loads
    recent embeddings (optionally scoped to a session) and computes cosine
    similarity in Python, returning the top-k matches with message content.

Environment variables:
  QAI_DB_CONN: SQL connection string (ODBC Driver 18 for SQL Server recommended)
  AZURE_OPENAI_API_KEY / AZURE_OPENAI_ENDPOINT / AZURE_OPENAI_EMBEDDING_DEPLOYMENT
  OPENAI_API_KEY (for public OpenAI embedding fallback)

Table schema created in database/Tables/ChatMessageEmbeddings.sql
"""
from __future__ import annotations

import os
import math
import struct
from typing import Iterable, List, Optional, Sequence

try:
    import pyodbc  # type: ignore
except Exception:  # pragma: no cover
    pyodbc = None  # type: ignore

try:  # OpenAI unified SDK
    from openai import OpenAI, AzureOpenAI  # type: ignore
except Exception:  # pragma: no cover
    OpenAI = None  # type: ignore
    AzureOpenAI = None  # type: ignore

# ------------------------- DB Helpers -------------------------

def _get_conn():  # noqa: ANN001
    conn_str = os.getenv("QAI_DB_CONN")
    if not conn_str or not pyodbc:
        return None
    try:
        return pyodbc.connect(conn_str, timeout=4)
    except Exception:
        return None

# ------------------------- Embedding Generation -------------------------

_LOCAL_EMBEDDING_DIMENSION = 256  # dimension for lightweight local fallback


def _hash_embedding(text: str, dimension: int = _LOCAL_EMBEDDING_DIMENSION) -> List[float]:
    """Very lightweight deterministic hashing embedding.

    Not semantically rich but provides some signal for similarity
    within the same workspace when no embedding API is configured.
    """
    import hashlib
    tokens = [token for token in text.lower().split() if token]
    embedding_vector = [0.0] * dimension
    if not tokens:
        return embedding_vector
    for token in tokens:
        hash_value = int(hashlib.sha256(token.encode("utf-8")).hexdigest(), 16)
        vector_index = hash_value % dimension
        embedding_vector[vector_index] += 1.0
    # L2 normalize
    vector_magnitude = math.sqrt(sum(value * value for value in embedding_vector)) or 1.0
    return [value / vector_magnitude for value in embedding_vector]


def generate_embedding(text: str) -> List[float]:  # noqa: ANN001
    """Generate an embedding for text using Azure OpenAI > OpenAI > local hash.

    Returns a list[float]; errors fall back to hash embedding.
    """
    text = text or ""
    # Azure first
    azure_openai_api_key = os.getenv("AZURE_OPENAI_API_KEY")
    azure_openai_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    azure_embedding_deployment = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT")
    if azure_openai_api_key and azure_openai_endpoint and azure_embedding_deployment and AzureOpenAI is not None:
        try:
            client = AzureOpenAI(api_key=azure_openai_api_key, azure_endpoint=azure_openai_endpoint)
            response = client.embeddings.create(model=azure_embedding_deployment, input=[text])
            return response.data[0].embedding  # type: ignore[attr-defined]
        except Exception:
            pass
    # Public OpenAI
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if openai_api_key and OpenAI is not None:
        try:
            client = OpenAI(api_key=openai_api_key)
            response = client.embeddings.create(model="text-embedding-3-small", input=[text])
            return response.data[0].embedding  # type: ignore[attr-defined]
        except Exception:
            pass
    # Fallback
    return _hash_embedding(text)

# ------------------------- Embedding Persistence -------------------------


def _serialize_float32_to_bytes(embedding_vector: Sequence[float]) -> bytes:
    """Serialize a float32 vector to bytes in little-endian format."""
    return struct.pack(f"<{len(embedding_vector)}f", *[float(value) for value in embedding_vector])


def store_embedding(message_id: Optional[str], embedding: Sequence[float], model: str) -> bool:  # noqa: ANN001
    if not message_id or not embedding:
        return False
    connection = _get_conn()
    if not connection:
        return False
    try:
        cursor = connection.cursor()
        serialized_embedding = _serialize_float32_to_bytes(embedding)
        cursor.execute(
            "INSERT INTO dbo.ChatMessageEmbeddings (MessageId, EmbeddingModel, EmbeddingDim, EmbeddingVector) VALUES (?,?,?,?)",
            message_id,
            model or "unknown-model",
            len(embedding),
            serialized_embedding,
        )
        connection.commit()
        return True
    except Exception:
        return False
    finally:
        try:
            connection.close()
        except Exception:
            pass

# ------------------------- Similarity Search -------------------------

def _deserialize_bytes_to_float32(blob: bytes, dimension: int) -> List[float]:
    """Deserialize bytes to a float32 vector."""
    if not blob:
        return [0.0] * dimension
    # Expect exact length = dimension * 4 bytes
    try:
        return list(struct.unpack(f"<{dimension}f", blob[: dimension * 4]))
    except Exception:
        # Fallback slice-based deserialization
        result = []
        for i in range(dimension):
            chunk = blob[i * 4 : (i + 1) * 4]
            if len(chunk) == 4:
                result.append(struct.unpack("<f", chunk)[0])
            else:
                result.append(0.0)
        return result


def calculate_cosine_similarity(vector_a: Sequence[float], vector_b: Sequence[float]) -> float:
    """Calculate cosine similarity between two vectors."""
    if not vector_a or not vector_b or len(vector_a) != len(vector_b):
        return 0.0
    dot_product = sum(x * y for x, y in zip(vector_a, vector_b))
    magnitude_a = math.sqrt(sum(x * x for x in vector_a)) or 1.0
    magnitude_b = math.sqrt(sum(y * y for y in vector_b)) or 1.0
    return dot_product / (magnitude_a * magnitude_b)


def fetch_similar_messages(query_embedding: Sequence[float], top_k: int = 5, session_id: Optional[str] = None) -> List[dict]:  # noqa: ANN001
    """Return top_k similar past messages using Python-side cosine similarity.

    If session_id is provided, restrict search to that session's conversation(s).
    For performance we limit to the most recent 500 embeddings.
    """
    if not query_embedding:
        return []
    connection = _get_conn()
    if not connection:
        return []
    try:
        cursor = connection.cursor()
        if session_id:
            cursor.execute(
                "SELECT TOP 500 e.MessageId, e.EmbeddingModel, e.EmbeddingDim, e.EmbeddingVector, m.Content "
                "FROM dbo.ChatMessageEmbeddings e JOIN dbo.ChatMessages m ON e.MessageId=m.MessageId "
                "JOIN dbo.ChatConversations c ON m.ConversationId=c.ConversationId "
                "WHERE c.SessionId=? ORDER BY e.CreatedAt DESC",
                session_id,
            )
        else:
            cursor.execute(
                "SELECT TOP 500 e.MessageId, e.EmbeddingModel, e.EmbeddingDim, e.EmbeddingVector, m.Content "
                "FROM dbo.ChatMessageEmbeddings e JOIN dbo.ChatMessages m ON e.MessageId=m.MessageId "
                "ORDER BY e.CreatedAt DESC",
            )
        rows = cursor.fetchall()
        scored_messages = []
        for row in rows:
            embedding_dimension = row.EmbeddingDim
            stored_embedding = _deserialize_bytes_to_float32(row.EmbeddingVector, embedding_dimension)
            similarity_score = calculate_cosine_similarity(query_embedding, stored_embedding)
            if similarity_score <= 0:
                continue
            scored_messages.append({
                "message_id": row.MessageId,
                "content": row.Content,
                "similarity": similarity_score,
                "embedding_model": row.EmbeddingModel,
            })
        scored_messages.sort(key=lambda x: x["similarity"], reverse=True)
        return scored_messages[:top_k]
    except Exception:
        return []
    finally:
        try:
            connection.close()
        except Exception:
            pass

__all__ = [
    "generate_embedding",
    "store_embedding",
    "fetch_similar_messages",
]
