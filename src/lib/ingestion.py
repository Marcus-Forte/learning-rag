from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from langchain_core.documents import Document


class Ingestion(ABC):
    """Abstract interface for document ingestion.

    Expected implementations: PDFIngestion, WordIngestion, WebIngestion, ...
    """

    @abstractmethod
    def load(self, document: str | Path) -> list[Document]:
        """Load a document and return a list of LangChain Documents."""
        ...

