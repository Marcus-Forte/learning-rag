import logging
import sys
from typing import Any

from langchain_core.messages import AIMessage, AIMessageChunk, HumanMessage, ToolMessage
from langchain_core.vectorstores import VectorStore
from langchain.agents import create_agent
from langchain.tools import tool

from lib.callbacks import ToolCallLoggingCallbackHandler

log = logging.getLogger(__name__)


# Here we let the model decide when to call the retrieval tool
AGENTIC_RAG_SYSTEM_PROMPT = (
    "You have access to a tool that retrieves context from a knowledge base. "
    "Use the tool to help answer user queries. Indicate in the response on the sources"
)


def _get_message_text(message: Any) -> str:
    text = getattr(message, "text", None)
    if isinstance(text, str) and text:
        return text
    content = getattr(message, "content", "")
    return content if isinstance(content, str) else str(content)


def _stream_agent_messages(
    *, agent: Any, messages: list[Any], callbacks: list[Any] | None
) -> str:
    wrote_any = False
    printed_full = ""

    def _iter_stream_events():
        """Prefer token/message streaming; fall back to state-value streaming."""

        callback_config = {"callbacks": callbacks or []}

        # Attempt passing callbacks via config (Runnable-style)
        for mode in ("messages", "values"):
            yield from agent.stream(
                {"messages": messages},
                stream_mode=mode,
                config=callback_config,
            )
            return

        # Last-ditch fallback (should not usually happen)
        yield from agent.stream({"messages": messages}, stream_mode="values")

    for event in _iter_stream_events():
        # stream_mode="messages" typically yields (message, metadata)
        if isinstance(event, tuple) and event:
            message = event[0]
        # stream_mode="values" yields a state dict with a messages list
        elif isinstance(event, dict) and "messages" in event and event["messages"]:
            message = event["messages"][-1]
        else:
            continue

        if isinstance(message, ToolMessage):
            # Tool activity is logged via callbacks; skip printing.
            continue

        if isinstance(message, AIMessageChunk):
            text = _get_message_text(message)
            if not text:
                continue
            wrote_any = True
            sys.stdout.write(text)
            sys.stdout.flush()
            printed_full += text
            continue

        if isinstance(message, AIMessage):
            text = _get_message_text(message)
            if not text:
                continue
            wrote_any = True

            # Some backends yield cumulative text.
            if text.startswith(printed_full):
                delta = text[len(printed_full) :]
                printed_full = text
            else:
                delta = text
                printed_full += text

            if delta:
                sys.stdout.write(delta)
                sys.stdout.flush()

    if wrote_any and not printed_full.endswith("\n"):
        print()

    return printed_full


def stream_rag_agent_answer(
    *,
    llm: Any,
    vector_store: VectorStore,
    prompt: str,
    k: int,
    history: list[Any] | None = None,
    show_header: bool = True,
) -> str:
    """Agentic RAG: let the model call a retrieval tool (per LangChain RAG docs)."""

    @tool(response_format="content_and_artifact")
    def retrieve_context(query: str):
        """Retrieve information to help answer a query."""
        retrieved_docs = vector_store.similarity_search(query, k=k)
        serialized = "\n\n".join(
            (
                f"Source: {doc.metadata}\nContent: {doc.page_content}"
                for doc in retrieved_docs
            )
        )
        return serialized, retrieved_docs

    agent = create_agent(
        llm, tools=[retrieve_context], system_prompt=AGENTIC_RAG_SYSTEM_PROMPT
    )
    messages: list[Any] = []
    if history:
        messages.extend(history)
    messages.append(HumanMessage(content=prompt))

    if show_header:
        print("Answer:")

    return _stream_agent_messages(
        agent=agent, messages=messages, callbacks=[ToolCallLoggingCallbackHandler()]
    )
