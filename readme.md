# Larning-RAG

This repository holds code to demonstrate the concept of RAG (Retrieval Augmented Generation), where an LLM becomes capable of searching custom-made files in a vector database.

## Usage

Update LLM keys at `.env`

```bash
uv run src/main.py --store <pdf file>
uv run src/main.py --prompt "question about content"
```

Navigate to `http://localhost:6333/dashboard/collections` to manipulate the db.

## Development

### Formatting

```bash
uv run black .
```