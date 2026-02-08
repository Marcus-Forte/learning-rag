# Docs

This folder contains:

- Architecture diagrams (Structurizr): `workspace.dsl`, `workspace.json`, `.structurizr/`
- System documentation: `cli.md`, `ing.md`, `ivb.md`, `illm.md`

## Rendering the Architecture

From the repo root:

```bash
docker run -it --rm -p 8080:8080 -v ./docs:/usr/local/structurizr structurizr/lite
```

Then open `http://localhost:8080/`.

## Quick Start (CLI)

See `cli.md` for full usage.

- Store a PDF: `uv run src/main.py --store test_docs/some.pdf`
- Ask a question: `uv run src/main.py --prompt "..."`
- Interactive: `uv run src/main.py --interactive`