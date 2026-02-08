## LLM / Chat

This project no longer has a custom “LLM interface” abstraction.

Instead it uses LangChain directly:

- Chat model: `langchain_openai.ChatOpenAI`
- Embeddings: `langchain_openai.OpenAIEmbeddings`

The chat/RAG orchestration lives in `src/lib/chat.py`.

### RAG modes

There are two prompt-time RAG implementations:

1) **Two-step RAG** (default)
	- Retrieve relevant chunks first
	- Inject them into a system prompt
	- Call the model once

2) **Agentic RAG** (`--agent`)
	- Exposes retrieval as a tool (`retrieve_context`)
	- Uses `langchain.agents.create_agent` so the model can decide when/how to retrieve

### Streaming + token logging

- Both modes stream output to stdout.
- Token usage is logged using LangChain’s OpenAI callback (when available):
  - `OpenAI tokens prompt=... completion=... total=...`

### Tool-call logging (agent mode)

Tool-call sequence logging is not enabled by default.
