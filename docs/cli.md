## CLI

Entry point: `src/main.py`

Run with `uv`:

```bash
uv run src/main.py -h
```

### Modes

Exactly one of these is required:

- `--store PDF_PATH` ingest + embed + store a PDF
- `--prompt TEXT` one-shot RAG question
- `--interactive` multi-turn chat loop

### Flags

- `--top-k N` number of chunks to retrieve (default: 5)
- `--agent` use *agentic RAG* (tool-based retrieval) instead of two-step RAG
	- Works with both `--prompt` and `--interactive`

### Examples

Store a PDF:

```bash
uv run src/main.py --store test_docs/Astronomy-For-Mere-Mortals-v-23.pdf
```

One-shot (two-step RAG):

```bash
uv run src/main.py --prompt "what is the chandrasekhar limit" --top-k 8
```

One-shot (agentic RAG):

```bash
uv run src/main.py --prompt "what is the chandrasekhar limit" --agent
```

Interactive (two-step RAG):

```bash
uv run src/main.py --interactive
```

Interactive (agentic RAG):

```bash
uv run src/main.py --interactive --agent
```

### Environment variables

Loaded from `.env` via `python-dotenv`.

- `OPENAI_API_KEY` (required)
- `OPENAI_EMBEDDING_MODEL` (optional, default: `text-embedding-3-small`)
- `OPENAI_CHAT_MODEL` (optional, default: `gpt-5-nano`)
- `QDRANT_COLLECTION` (optional, default: `documents`)

Qdrant connection:

- The current `VectorDB` implementation defaults to `host=qdrant` and `port=6333`.
	- In dev containers this typically maps to a service named `qdrant`.
