import logging
from typing import Any

from langchain_core.embeddings import Embeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.http import models as qdrant_models
from qdrant_client.http.exceptions import UnexpectedResponse

log = logging.getLogger(__name__)


class VectorDB:
    """Qdrant-backed vector DB wrapper.

    Holds all initialization logic (client + collection creation) and
    exposes a LangChain `QdrantVectorStore` for usage. Embeddings are provided
    by the caller.
    """

    def __init__(
        self,
        *,
        collection_name: str,
        embeddings: Embeddings,
        host: str = "qdrant",
        port: int = 6333,
        distance: qdrant_models.Distance = qdrant_models.Distance.COSINE,
        client: QdrantClient | None = None,
    ) -> None:
        self.collection_name = collection_name
        self.distance = distance

        self.client = client or self._create_client(
            host=host,
            port=port,
        )
        self.embeddings = embeddings

        self._ensure_collection_exists()

        log.info(
            "Initializing vector store collection=%s",
            self.collection_name,
        )
        self.vector_store = QdrantVectorStore(
            client=self.client,
            collection_name=self.collection_name,
            embedding=self.embeddings,
        )

    def as_retriever(self, *, k: int = 5):
        return self.vector_store.as_retriever(search_kwargs={"k": k})

    @staticmethod
    def list_sources(
        *,
        vector_store: QdrantVectorStore,
        max_points: int = 5000,
        batch_size: int = 256,
        max_sources: int = 500,
    ) -> list[str]:
        """List unique document sources stored in the vector DB.

        Works best with `langchain_qdrant.QdrantVectorStore` (expects `client` and
        `collection_name` attrs). Returns a list of lines like:
        `source (chunks=N)`.
        """

        client = getattr(vector_store, "client", None)
        collection_name = getattr(vector_store, "collection_name", None)
        if client is None or collection_name is None:
            return [
                "Listing all sources is not supported by the current vector store. "
                "Try retrieval instead (retrieve_context)."
            ]

        counts: dict[str, int] = {}
        scanned = 0
        offset = None

        while scanned < max_points and len(counts) < max_sources:
            limit = min(batch_size, max_points - scanned)
            points, offset = client.scroll(
                collection_name=collection_name,
                limit=limit,
                offset=offset,
                with_payload=True,
                with_vectors=False,
            )
            if not points:
                break

            for point in points:
                scanned += 1
                payload = getattr(point, "payload", None) or {}

                meta = payload.get("metadata") or payload.get("meta") or {}
                source = meta.get("source") or payload.get("source")
                if not source:
                    continue
                source_str = str(source)
                counts[source_str] = counts.get(source_str, 0) + 1

                if scanned >= max_points or len(counts) >= max_sources:
                    break

            if offset is None:
                break

        if not counts:
            return ["No sources found (or unable to read source metadata)."]

        lines = [
            f"{src} (chunks={cnt})"
            for src, cnt in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))
        ]
        if scanned >= max_points:
            lines.append(f"(stopped after scanning {scanned} points)")
        if len(counts) >= max_sources:
            lines.append(f"(stopped after collecting {len(counts)} sources)")
        return lines

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _create_client(self, *, host: str, port: int) -> QdrantClient:
        if host:
            log.info("Connecting to Qdrant via host=%s port=%s", host, port)
            return QdrantClient(host=host, port=port)

    def _ensure_collection_exists(self) -> None:
        """Create the collection if it doesn't exist.

        Qdrant needs vector size at collection creation time; infer it from the
        embedding model by embedding a short probe string.
        """
        try:
            self.client.get_collection(collection_name=self.collection_name)
            return
        except UnexpectedResponse as e:
            if getattr(e, "status_code", None) != 404:
                raise
            log.info("Collection '%s' missing; creating.", self.collection_name)

        probe = self.embeddings.embed_query("qdrant-collection-dimension-probe")
        dim = len(probe)
        if dim <= 0:
            raise ValueError("Embedding dimension probe returned empty vector")

        self.client.create_collection(
            collection_name=self.collection_name,
            vectors_config=qdrant_models.VectorParams(size=dim, distance=self.distance),
        )
        log.info(
            "Created collection '%s' with dim=%s distance=%s",
            self.collection_name,
            dim,
            self.distance,
        )
