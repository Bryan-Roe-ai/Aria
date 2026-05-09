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

import hashlib
import heapq
import logging
import math
import os
import queue
import struct
import threading
from typing import Any, Dict, List, Optional, Sequence, Tuple

try:
    import pyodbc  # type: ignore
except Exception:  # pragma: no cover
    pyodbc = None  # type: ignore

try:  # OpenAI unified SDK
    from openai import AzureOpenAI, OpenAI  # type: ignore
except Exception:  # pragma: no cover
    OpenAI = None  # type: ignore
    AzureOpenAI = None  # type: ignore

try:
    from shared.azure_utils import format_quota_message, is_quota_error
except Exception:  # pragma: no cover - best effort import
    # Provide simple fallbacks if helper isn't available
    def is_quota_error(e: Exception) -> bool:  # noqa: D401
        if e is None:
            return False
        txt = str(e).lower()
        return any(
            k in txt
            for k in (
                "quota",
                "premium",
                "exceed",
                "allowance",
                "insufficient",
                "billing",
            )
        )

    def format_quota_message(
        e: Exception, service_name: str = "Azure OpenAI"
    ) -> str:  # noqa: D401
        return f"{service_name} quota/premium limit reached. Details: {str(e)}"


# ------------------------- DB Helpers with Connection Pooling -------------------------

_logger = logging.getLogger(__name__)

_DEFAULT_MAX_POOL_SIZE = 5
MAX_POOL_SIZE = max(
    1,
    int(os.getenv("QAI_DB_POOL_SIZE", os.getenv("QAI_CHAT_MEMORY_POOL_SIZE", _DEFAULT_MAX_POOL_SIZE))),
)

_conn_lock = threading.RLock()
_thread_local = threading.local()
_thread_connections: Dict[int, Any] = {}


class ConnectionPool:
    """Thread-safe LIFO connection pool with thread-local fast-path caching."""

    def __init__(self, max_size: int = MAX_POOL_SIZE) -> None:
        self._max_size = max_size
        self._pool: "queue.LifoQueue[Any]" = queue.LifoQueue(maxsize=max_size)

    @staticmethod
    def _close_quietly(conn: Any) -> None:
        try:
            conn.close()
        except Exception:
            pass

    @staticmethod
    def _is_alive(conn: Any) -> bool:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            try:
                cursor.fetchone()
            except Exception:
                pass
            try:
                cursor.close()
            except Exception:
                pass
            return True
        except Exception:
            return False

    def _create_conn(self) -> Optional[Any]:
        conn_str = os.getenv("QAI_DB_CONN")
        if not conn_str or not pyodbc:
            return None
        try:
            return pyodbc.connect(conn_str, timeout=4)
        except Exception:
            return None

    def acquire(self) -> Optional[Any]:
        """Get a live connection from thread cache, pool, or a new connect."""
        thread_id = threading.get_ident()

        cached = getattr(_thread_local, "conn", None)
        if cached is not None:
            if self._is_alive(cached):
                with _conn_lock:
                    _thread_connections[thread_id] = cached
                return cached
            self._close_quietly(cached)
            _thread_local.conn = None
            with _conn_lock:
                _thread_connections.pop(thread_id, None)

        while True:
            try:
                pooled = self._pool.get_nowait()
            except queue.Empty:
                break
            if self._is_alive(pooled):
                _thread_local.conn = pooled
                with _conn_lock:
                    _thread_connections[thread_id] = pooled
                return pooled
            self._close_quietly(pooled)

        created = self._create_conn()
        if created is not None and self._is_alive(created):
            _thread_local.conn = created
            with _conn_lock:
                _thread_connections[thread_id] = created
            return created
        if created is not None:
            self._close_quietly(created)
        return None

    def release(self, conn: Any) -> None:
        """Return connection to pool; close if pool is full."""
        if not conn:
            return
        thread_id = threading.get_ident()
        if getattr(_thread_local, "conn", None) is conn:
            with _conn_lock:
                _thread_connections[thread_id] = conn
            return
        with _conn_lock:
            _thread_connections.pop(thread_id, None)
        try:
            self._pool.put_nowait(conn)
        except queue.Full:
            self._close_quietly(conn)

    def close_all(self) -> None:
        """Close all pooled and thread-cached connections."""
        while True:
            try:
                conn = self._pool.get_nowait()
            except queue.Empty:
                break
            self._close_quietly(conn)
        with _conn_lock:
            for thread_id, conn in list(_thread_connections.items()):
                self._close_quietly(conn)
                _thread_connections.pop(thread_id, None)
        current_cached = getattr(_thread_local, "conn", None)
        if current_cached is not None:
            self._close_quietly(current_cached)
            _thread_local.conn = None

    def pool_size(self) -> int:
        return self._pool.qsize()

    def pool_snapshot(self) -> List[Any]:
        items: List[Any] = []
        while True:
            try:
                items.append(self._pool.get_nowait())
            except queue.Empty:
                break
        for item in items:
            try:
                self._pool.put_nowait(item)
            except queue.Full:
                self._close_quietly(item)
        return list(items)

    def add_to_pool(self, conn: Any) -> None:
        if not conn:
            return
        try:
            self._pool.put_nowait(conn)
        except queue.Full:
            self._close_quietly(conn)

    def pop_from_pool(self) -> Any:
        return self._pool.get_nowait()


class _ConnectionPoolView(list):
    """Backward-compatible list-like view over the internal connection pool."""

    def __init__(self, pool: ConnectionPool) -> None:
        self._pool = pool

    def clear(self) -> None:
        while True:
            try:
                conn = self._pool.pop_from_pool()
            except queue.Empty:
                break
            self._pool._close_quietly(conn)

    def append(self, conn: Any) -> None:
        self._pool.add_to_pool(conn)

    def pop(self, index: int = -1) -> Any:
        if index not in (-1, 0):
            raise IndexError("pool view only supports pop() or pop(-1)")
        return self._pool.pop_from_pool()

    def __len__(self) -> int:
        return self._pool.pool_size()

    def __iter__(self):
        return iter(self._pool.pool_snapshot())

    def __getitem__(self, index: int) -> Any:
        return self._pool.pool_snapshot()[index]


_POOL = ConnectionPool(MAX_POOL_SIZE)

# Backward-compatible aliases expected by existing imports/scripts.
_conn_cache = _thread_connections
_connection_pool = _ConnectionPoolView(_POOL)


def _get_conn() -> Optional[Any]:
    """Return a live DB connection from thread cache, pool, or new connect."""
    return _POOL.acquire()


def _return_conn(conn: Any) -> None:
    """Return a connection to the pool or close it when pool is full."""
    _POOL.release(conn)


def close_all_connections() -> None:
    """Close all pooled and thread-local connections for clean shutdown."""
    _POOL.close_all()


# ------------------------- Embedding Generation -------------------------


_LOCAL_DIM = 256  # dimension for lightweight local fallback


def _hash_embedding(text: str, dim: int = _LOCAL_DIM) -> List[float]:
    """Very lightweight deterministic hashing embedding.

    Not semantically rich but provides some signal for similarity
    within the same workspace when no embedding API is configured.

    Optimized: Uses module-level hashlib import and single-pass norm calculation.
    """
    tokens = [t for t in text.lower().split() if t]
    vec = [0.0] * dim
    if not tokens:
        return vec

    # Build vector with hash-based indices
    for tok in tokens:
        h = int(hashlib.sha256(tok.encode("utf-8")).hexdigest(), 16)
        idx = h % dim
        vec[idx] += 1.0

    # L2 normalize in single pass
    sum_sq = sum(v * v for v in vec)
    if sum_sq > 0:
        norm = math.sqrt(sum_sq)
        return [v / norm for v in vec]
    return vec


def generate_embedding(text: str) -> List[float]:  # noqa: ANN001
    """Generate an embedding for text using Azure OpenAI > OpenAI > local hash.

    Returns a list[float]; errors fall back to hash embedding.
    """
    text = text or ""
    # Azure first
    az_key = os.getenv("AZURE_OPENAI_API_KEY")
    az_ep = os.getenv("AZURE_OPENAI_ENDPOINT")
    az_emb = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT")
    if az_key and az_ep and az_emb and AzureOpenAI is not None:
        try:
            client = AzureOpenAI(api_key=az_key, azure_endpoint=az_ep)
            resp = client.embeddings.create(model=az_emb, input=[text])
            return resp.data[0].embedding  # type: ignore[attr-defined]
        except Exception as e:
            # If this looks like a quota/premium issue, log and fall back to
            # the lightweight local hash embedding so the app remains usable.
            if is_quota_error(e):
                try:
                    import logging

                    logging.getLogger(__name__).warning(
                        "Azure embedding call detected quota/premium error: %s", str(e)
                    )
                except Exception:
                    pass
                return _hash_embedding(text)
            # Otherwise continue to try public OpenAI or local fallback
            pass
    # Public OpenAI
    oi_key = os.getenv("OPENAI_API_KEY")
    if oi_key and OpenAI is not None:
        try:
            client = OpenAI(api_key=oi_key)
            resp = client.embeddings.create(
                model="text-embedding-3-small", input=[text]
            )
            return resp.data[0].embedding  # type: ignore[attr-defined]
        except Exception:
            pass
    # Fallback
    return _hash_embedding(text)


# ------------------------- Embedding Persistence -------------------------


def _serialize_f32(vec: Sequence[float]) -> bytes:
    return struct.pack(f"<{len(vec)}f", *[float(v) for v in vec])


def store_embeddings_batch(embeddings: List[Tuple[str, Sequence[float], str]]) -> int:
    """Store embeddings with one executemany() call and one transaction commit.

    Args:
        embeddings: Tuples of ``(message_id, embedding, model)``.

    Returns:
        int: Number of inserted rows.
    """
    if not embeddings:
        return 0
    conn = _get_conn()
    if not conn:
        return 0
    inserted = 0
    try:
        values: List[Tuple[str, str, int, bytes]] = []
        for message_id, embedding, model in embeddings:
            if not message_id or not embedding:
                continue
            values.append(
                (
                    message_id,
                    model or "unknown-model",
                    len(embedding),
                    _serialize_f32(embedding),
                )
            )
        if not values:
            return 0
        cursor = conn.cursor()
        cursor.executemany(
            "INSERT INTO dbo.ChatMessageEmbeddings (MessageId, EmbeddingModel, EmbeddingDim, EmbeddingVector) VALUES (?,?,?,?)",
            values,
        )
        conn.commit()
        inserted = len(values)
        return inserted
    except Exception:
        _logger.exception("Failed storing embeddings batch (size=%d)", len(embeddings))
        try:
            conn.rollback()
        except Exception:
            pass
        return 0
    finally:
        _return_conn(conn)


def store_embedding(
    message_id: Optional[str], embedding: Sequence[float], model: str
) -> bool:  # noqa: ANN001
    if not message_id or not embedding:
        return False
    return store_embeddings_batch([(message_id, embedding, model)]) == 1


# ------------------------- Similarity Search -------------------------


def _deserialize_f32(blob: bytes, dim: int) -> List[float]:
    if not blob:
        return [0.0] * dim
    # Expect exact length = dim * 4
    try:
        return list(struct.unpack(f"<{dim}f", blob[: dim * 4]))
    except Exception:
        # Fallback slice-based
        out = []
        for i in range(dim):
            chunk = blob[i * 4 : (i + 1) * 4]
            if len(chunk) == 4:
                out.append(struct.unpack("<f", chunk)[0])
            else:
                out.append(0.0)
        return out


def _cosine(a: Sequence[float], b: Sequence[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a)) or 1.0
    nb = math.sqrt(sum(y * y for y in b)) or 1.0
    return dot / (na * nb)


def fetch_similar_messages(
    query_embedding: Sequence[float], top_k: int = 5, session_id: Optional[str] = None
) -> List[dict]:  # noqa: ANN001
    """Return top_k similar past messages using Python-side cosine similarity.

    If session_id is provided, restrict search to that session's conversation(s).
    For performance we limit to the most recent 500 embeddings.

    Optimization: Uses heapq.nlargest for O(n log k) top-k selection instead of
    O(n log n) full sort when top_k is small relative to result set.
    Uses connection pooling to avoid creating new connections for every query.
    """
    if not query_embedding:
        return []
    conn = _get_conn()
    if not conn:
        return []
    try:
        cursor = conn.cursor()
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

        # Build scored list with only positive similarities
        scored = []
        for r in rows:
            dim = r.EmbeddingDim
            emb = _deserialize_f32(r.EmbeddingVector, dim)
            sim = _cosine(query_embedding, emb)
            if sim > 0:
                scored.append(
                    {
                        "message_id": r.MessageId,
                        "content": r.Content,
                        "similarity": sim,
                        "embedding_model": r.EmbeddingModel,
                    }
                )

        # Use heapq.nlargest for efficient top-k selection (O(n log k) vs O(n log n))
        # This is more efficient when top_k << len(scored)
        return heapq.nlargest(top_k, scored, key=lambda x: x["similarity"])
    except Exception:
        _logger.exception("Failed fetching similar messages")
        return []
    finally:
        # Return connection to pool instead of closing
        _return_conn(conn)


__all__ = [
    "generate_embedding",
    "store_embedding",
    "store_embeddings_batch",
    "fetch_similar_messages",
    "close_all_connections",
    "_get_conn",
    "_return_conn",
    "_conn_cache",
    "_conn_lock",
    "_connection_pool",
]
