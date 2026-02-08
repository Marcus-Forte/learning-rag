## LLM / Chat

This module consumes the langchain LLM interface library to interact with OpenAI chat and embedding models. 

- Chat model: `langchain_openai.ChatOpenAI`
- Embeddings: `langchain_openai.OpenAIEmbeddings`

The chat/RAG orchestration lives in `src/lib/chat.py`.

### RAG modes

There are two prompt-time RAG implementations:

1) **Two-step RAG** (default)
	- User prompt -> prompts gets embedded -> vector DB chunks are retrieved -> entire context is passed to the LLM (model is called once) -> LLM processes and replies.  

2) **Agentic RAG** (`--agent`)
	- Exposes retrieval as a tool (`retrieve_context`)
	- Uses `langchain.agents.create_agent` so the model can decide when/how to retrieve

### Resources

- [RAG Langchain](https://docs.langchain.com/oss/python/langchain/rag)
