## Ingestion

The ingestion module is responsible for taking a source document (e.g. a PDF) and producing chunked LangChain `Document` objects ready to be embedded + stored.

## Expected implementations

- PDFIngestion
- WordIngestion
- WebIngestion
- ...

## Expected API

- `load(document) -> list[langchain_core.documents.Document]`

### PDF ingestion behavior

Implemented in `src/lib/ingestion_pdf.py` as `PDFIngestion`.

- Reads the PDF via `pypdf.PdfReader`
- Splits each page into chunks using `RecursiveCharacterTextSplitter`
- Returns a list of LangChain `Document` chunks with metadata:
	- `source`: file path
	- `page`: 1-based page number

Defaults:

- `chunk_size=900`
- `chunk_overlap=150`