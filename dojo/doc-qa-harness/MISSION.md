# Doc QA Harness (RAG Eval)

Build a tiny RAG pipeline plus an evaluation harness over a local doc set.

## Requirements
- Include a small corpus (couple markdown/PDF/text files) in `data/`.
- Implement `retrieve(query, k=3)` and `answer(query)` that returns the response plus the contexts used.
- Add an eval script that runs against a fixture of (query, expected snippet or answer) and reports hit rate + exactness.
- Provide a CLI: `python main.py "What is the refund policy?"` -> prints answer + sources.

## Stretch
- Add a basic chunker with overlapping windows and configurable chunk size.
- Add a reranker step that prefers chunks with higher token overlap.
