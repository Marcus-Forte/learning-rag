from __future__ import annotations

import logging
import os
from pathlib import Path

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
        collection_name: str = "documents",
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

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _create_client(
        self,
        *,
        host: str,
        port: int   
    ) -> QdrantClient:
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
