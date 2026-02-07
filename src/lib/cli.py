from __future__ import annotations

import argparse


def build_parser() -> argparse.ArgumentParser:
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
		"--promtp",
		dest="prompt",
		metavar="TEXT",
		help="One-shot prompt (retrieval only).",
	)

	parser.add_argument(
		"--db-path",
		default="qdrant_data",
		help="Path to the local Qdrant (disk) store.",
	)
	parser.add_argument(
		"--top-k",
		type=int,
		default=5,
		help="How many chunks to retrieve for a prompt.",
	)
	return parser


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
	return build_parser().parse_args(argv)
