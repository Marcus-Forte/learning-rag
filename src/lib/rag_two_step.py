import logging
import sys
from typing import Any

from langchain_core.documents import Document
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.vectorstores import VectorStoreRetriever

log = logging.getLogger(__name__)


# Here we pass the context as part of the prompt.
RAG_SYSTEM_PROMPT_TEMPLATE = (
    "You are a helpful assistant.\n"
    "Answer using ONLY the following context.\n"
    "If the context is insufficient, say you don't know.\n\n"
    "Context: {context}"
)


def _format_docs(docs: list[Document]) -> str:
    return "\n\n".join(d.page_content for d in docs)


def _get_message_text(message: Any) -> str:
    text = getattr(message, "text", None)
    if isinstance(text, str) and text:
        return text
    content = getattr(message, "content", "")
    return content if isinstance(content, str) else str(content)


def build_system_prompt(*, retriever: VectorStoreRetriever, query: str) -> str:
    """Build the system prompt by retrieving context right before model invocation."""
    log.info("Retrieving context for query: `%s`", query)
    context_docs = retriever.invoke(query)
    docs_content = _format_docs(context_docs)
    log.info(
        "Retrieved %s documents. nr of characters: %d",
        len(context_docs),
        len(docs_content),
    )
    return RAG_SYSTEM_PROMPT_TEMPLATE.format(context=docs_content)


def stream_llm_messages(*, llm: Any, messages: list[Any]) -> str:
    """Stream model output to stdout; return the full assistant text."""
    wrote_any = False
    printed_full = ""

    for chunk in llm.stream(messages):
        text = _get_message_text(chunk)
        if not text:
            continue
        wrote_any = True

        # Some backends yield cumulative text; others yield deltas.
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


def stream_rag_answer(
    *,
    llm: Any,
    retriever: Any,
    prompt: str,
    history: list[Any] | None = None,
    show_header: bool = True,
) -> str:
    system_prompt = build_system_prompt(retriever=retriever, query=prompt)
    messages: list[Any] = [SystemMessage(content=system_prompt)]
    if history:
        messages.extend(history)
    messages.append(HumanMessage(content=prompt))

    if show_header:
        print("Answer:")

    return stream_llm_messages(llm=llm, messages=messages)
