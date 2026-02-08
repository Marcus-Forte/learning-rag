# Learning-RAG

This repository holds code to demonstrate the concept of RAG (Retrieval Augmented Generation), where an LLM becomes capable of searching custom-made files in a vector database.

## Usage

Open this repository as a devcontainer in vscode. It will start a [qdrant](https://qdrant.tech/) database where document embeddings will be stored to. Navigate to `http://localhost:6333/dashboard#/collections` to manipulate the db.

Update your LLM supplier keys/tokens at `.env`

```bash
uv run src/main.py --store <pdf file>
uv run src/main.py --prompt "question about content" # Chain mode
uv run src/main.py --prompt "question about content" --agent # Agent mode.
uv run src/main.py --prompt "list sources" --agent # agent consult "list sources" tool
```



## Development

### Formatting

```bash
uv run black .
```

## Resources

- https://docs.langchain.com/oss/python/langchain/rag