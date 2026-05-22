#!/usr/bin/env python3
"""
CLI tool to index transcript .txt files into the RAG vector store.

Usage:
    python indexer.py data/transcripts/           # index all .txt in dir
    python indexer.py file1.txt file2.txt         # index specific files
    python indexer.py --status                    # show collection info
    python indexer.py --reset                     # wipe and re-index a dir
"""
import sys
import argparse
import shutil
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))


def main() -> None:
    parser = argparse.ArgumentParser(description="Index transcripts into RAG store")
    parser.add_argument("paths", nargs="*", help=".txt files or directories")
    parser.add_argument("--status", action="store_true", help="Show collection status")
    parser.add_argument("--reset", action="store_true",
                        help="Wipe existing store before indexing")
    args = parser.parse_args()

    from rag import index_file, collection_count, CHROMA_PATH

    if args.status:
        n = collection_count()
        print(f"RAG store: {CHROMA_PATH}")
        print(f"Chunks in collection: {n}")
        return

    if args.reset and CHROMA_PATH.exists():
        shutil.rmtree(CHROMA_PATH)
        print(f"Wiped {CHROMA_PATH}")

    files: list[Path] = []
    for p in args.paths:
        p = Path(p)
        if p.is_dir():
            files.extend(sorted(p.glob("*.txt")))
        elif p.is_file():
            files.append(p)
        else:
            print(f"Warning: {p} not found, skipped", file=sys.stderr)

    if not files:
        print("No .txt files found. Provide file paths or a directory.")
        print("  python indexer.py data/transcripts/")
        sys.exit(1)

    total = 0
    for f in files:
        n = index_file(f)
        print(f"  {f.name}: {n} chunks")
        total += n

    print(f"\nTotal indexed: {total} chunks")
    print(f"Collection size: {collection_count()} chunks")


if __name__ == "__main__":
    main()
