import logging
from typing import Any

from langchain_core.messages import (
    AIMessage,
    HumanMessage,
)
from langchain_core.vectorstores import VectorStore

from lib.rag_agent import stream_rag_agent_answer
from lib.rag_two_step import stream_rag_answer

log = logging.getLogger(__name__)


def print_sources(*, vector_store: VectorStore, query: str, k: int) -> None:
    results = vector_store.similarity_search_with_score(query, k=k)
    log.info("Printing sources for query: `%s`", query)
    if results:
        print("\nSources:")
        for i, (doc, score) in enumerate(results, start=1):
            meta = doc.metadata or {}
            src = meta.get("source", "?")
            page = meta.get("page", "?")
            print(f"[{i}] score={float(score):.4f} source={src} page={page}")
    else:
        print("\nSources:\n(no matches)")


def interactive_chat(
    *,
    llm: Any,
    retriever: Any,
    vector_store: VectorStore,
    k: int,
    agent_mode: bool = False,
) -> None:
    print("Interactive mode. Type 'exit' or 'quit' to leave.")
    history: list[Any] = []

    while True:
        try:
            user_input = input("\nYou: ").strip()
        except EOFError:
            print()
            return

        if not user_input:
            continue
        if user_input.lower() in {"exit", "quit"}:
            return

        if agent_mode:
            assistant_text = stream_rag_agent_answer(
                llm=llm,
                vector_store=vector_store,
                prompt=user_input,
                k=k,
                history=history,
                show_header=False,
            )
        else:
            assistant_text = stream_rag_answer(
                llm=llm,
                retriever=retriever,
                prompt=user_input,
                history=history,
                show_header=False,
            )
        history.append(HumanMessage(content=user_input))
        history.append(AIMessage(content=assistant_text))

        print_sources(vector_store=vector_store, query=user_input, k=k)
