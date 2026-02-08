import logging
from pathlib import Path

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf import PdfReader

from .ingestion import Ingestion


class PDFIngestion(Ingestion):
    """Loads a PDF file and returns chunked LangChain Documents.

    Each chunk carries metadata: source (path) and page (1-based).
    """

    def __init__(self, *, chunk_size: int = 900, chunk_overlap: int = 150) -> None:
        self._log = logging.getLogger(__name__)
        self._splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )

    def load(self, document: str | Path) -> list[Document]:
        path = Path(document)
        if not path.exists():
            raise FileNotFoundError(path)
        if path.suffix.lower() != ".pdf":
            raise ValueError(f"Expected a .pdf file, got: {path}")

        reader = PdfReader(str(path))
        lc_docs: list[Document] = []
        for idx, page in enumerate(reader.pages):
            page_text = (page.extract_text() or "").strip()
            if not page_text:
                continue

            for chunk in self._splitter.split_text(page_text):
                lc_docs.append(
                    Document(
                        page_content=chunk,
                        metadata={"source": str(path), "page": idx + 1},
                    )
                )

        if not lc_docs:
            raise ValueError(f"No extractable text found in {path}")
        self._log.info("Loaded %s chunks from %s", len(lc_docs), path)
        return lc_docs
