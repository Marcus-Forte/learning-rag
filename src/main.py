from __future__ import annotations

import logging
import os
import sys
from typing import Any

from dotenv import load_dotenv

from langchain_core.documents import Document as LCDocument
from langchain_core.messages import AIMessageChunk, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings

from lib.cli import parse_args
from lib.ingestion_pdf import PDFIngestion
from lib.vector_db import VectorDB


def _format_docs(docs: list[LCDocument]) -> str:
    return "\n\n".join(d.page_content for d in docs)


def _get_message_text(message) -> str:
    text = getattr(message, "text", None)
    if isinstance(text, str) and text:
        return text
    content = getattr(message, "content", "")
    return content if isinstance(content, str) else str(content)


def _stream_rag_answer(*, llm: Any, retriever: Any, prompt: str) -> None:
    # Dynamic prompt concept (per LangChain RAG docs): retrieve right before calling
    # the model and inject context into a system message.
    context_docs = retriever.invoke(prompt)
    docs_content = _format_docs(context_docs)
    system_prompt = (
        "You are a helpful assistant. Answer using ONLY the following context. "
        "If the context is insufficient, say you don't know."
        f"\n\n{docs_content}"
    )

    print("Answer:")
    wrote_any = False
    last_text = ""

    messages = [SystemMessage(content=system_prompt), HumanMessage(content=prompt)]
    for chunk in llm.stream(messages):
        if isinstance(chunk, AIMessageChunk):
            text = _get_message_text(chunk)
        else:
            text = _get_message_text(chunk)

        if not text:
            continue
        wrote_any = True

        # Defensive: some models return cumulative text.
        if text.startswith(last_text):
            delta = text[len(last_text) :]
        else:
            delta = text
        if delta:
            sys.stdout.write(delta)
            sys.stdout.flush()
            last_text = text

    if wrote_any and not last_text.endswith("\n"):
        print()


def _print_sources(*, vector_store: Any, query: str, k: int) -> None:
    results = vector_store.similarity_search_with_score(query, k=k)
    if results:
        print("\nSources:")
        for i, (doc, score) in enumerate(results, start=1):
            meta = doc.metadata or {}
            src = meta.get("source", "?")
            page = meta.get("page", "?")
            print(f"[{i}] score={float(score):.4f} source={src} page={page}")
    else:
        print("\nSources:\n(no matches)")


def main(argv: list[str] | None = None) -> int:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )
    load_dotenv()

    args = parse_args(argv)

    collection_name = os.getenv("QDRANT_COLLECTION", "documents")
    embedding_model = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
    embeddings = OpenAIEmbeddings(model=embedding_model)

    vector_db = VectorDB(
        collection_name=collection_name,
        embeddings=embeddings,
    )
    vector_store = vector_db.vector_store

    if args.store:
        ingestion = PDFIngestion()
        lc_docs = ingestion.load(args.store)

        vector_store.add_documents(lc_docs)
        print(f"Stored {len(lc_docs)} chunks into collection '{collection_name}'.")
        return 0

    prompt = args.prompt
    retriever = vector_db.as_retriever(k=args.top_k)
    llm = ChatOpenAI(model="gpt-5-nano", streaming=True)

    _stream_rag_answer(llm=llm, retriever=retriever, prompt=prompt)
    _print_sources(vector_store=vector_store, query=prompt, k=args.top_k)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
