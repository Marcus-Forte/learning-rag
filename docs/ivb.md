## Vector DB

The vector DB module wraps Qdrant initialization and provides a LangChain-compatible vector store + retriever.

## Expected API

- `VectorDB(...).vector_store` (LangChain `QdrantVectorStore`)
- `VectorDB.as_retriever(k=...)`

### Notes

- `VectorDB` requires embeddings to be constructed by the caller and passed in.
- On startup it ensures the configured collection exists; if missing, it creates it by probing the embedding dimension.

## Expected implementations

- Qdrant (via `langchain-qdrant` and `qdrant-client`)

