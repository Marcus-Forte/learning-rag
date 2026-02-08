import argparse
import logging
import os

from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings

from lib.chat import (
    interactive_chat,
    print_sources,
    stream_rag_agent_answer,
    stream_rag_answer,
)
from lib.ingestion_pdf import PDFIngestion
from lib.vector_db import VectorDB


def main(argv: list[str] | None = None) -> int:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )

    parser = argparse.ArgumentParser(
        prog="learning-rag",
        description="Minimal RAG playground (store PDFs, query via retrieval).",
    )

    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument(
        "--store",
        metavar="PDF_PATH",
        help="Store a PDF into the local vector DB.",
    )
    action.add_argument(
        "--prompt",
        dest="prompt",
        metavar="TEXT",
        help="One-shot prompt (retrieval only).",
    )
    action.add_argument(
        "--interactive",
        action="store_true",
        help="Interactive chat loop (multi-turn RAG).",
    )
    action.add_argument(
        "--search-only",
        dest="search_only",
        metavar="QUERY",
        help="Search the vector DB directly (similarity search only; no LLM).",
    )

    parser.add_argument(
        "--top-k",
        type=int,
        default=5,
        help="How many chunks to retrieve for a prompt.",
    )
    parser.add_argument(
        "--agent",
        action="store_true",
        help="Use agentic RAG (tool-based retrieval) instead of two-step RAG.",
    )

    logging.getLogger("httpx").setLevel(logging.WARNING)

    load_dotenv()

    args = parser.parse_args(argv)

    collection_name = os.getenv("QDRANT_COLLECTION", "documents")
    embedding_model = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
    llm_model = os.getenv("OPENAI_CHAT_MODEL", "gpt-5-nano")
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

    if args.interactive:
        retriever = vector_db.as_retriever(k=args.top_k)
        llm = ChatOpenAI(model=llm_model, streaming=True)
        interactive_chat(
            llm=llm,
            retriever=retriever,
            vector_store=vector_store,
            k=args.top_k,
            agent_mode=args.agent,
        )
        return 0

    if getattr(args, "search_only", None):
        query = args.search_only
        results = vector_store.similarity_search_with_score(query, k=args.top_k)
        if results:
            print("Results:")
            for i, (doc, score) in enumerate(results, start=1):
                meta = doc.metadata or {}
                src = meta.get("source", "?")
                page = meta.get("page", "?")
                content = (doc.page_content or "").strip().replace("\n", " ")
                preview = content[:300] + ("..." if len(content) > 300 else "")
                print(f"[{i}] score={float(score):.4f} source={src} page={page}")
                if preview:
                    print(f"    {preview}")
        else:
            print("Results:\n(no matches)")
        return 0

    prompt = args.prompt
    retriever = vector_db.as_retriever(k=args.top_k)
    llm = ChatOpenAI(model=llm_model, streaming=True)

    if args.agent:
        stream_rag_agent_answer(
            llm=llm, vector_store=vector_store, prompt=prompt, k=args.top_k
        )
    else:
        stream_rag_answer(llm=llm, retriever=retriever, prompt=prompt)
    print_sources(vector_store=vector_store, query=prompt, k=args.top_k)

    return 0


if __name__ == "__main__":
    main()
