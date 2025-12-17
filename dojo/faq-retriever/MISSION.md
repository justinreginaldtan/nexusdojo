# FAQ Retriever (RAG Mini)

Implement a small Retrieval-Augmented QA system over a local FAQ corpus.

## Requirements
- Seed a small FAQ dataset (YAML/JSON) with at least 10 Q&A items and tags.
- Embed/store the questions (use a simple embedding stub: e.g., bag-of-words or sentence-transformers if available; keep offline-friendly).
- Implement `retrieve_context(query, k=3)` that returns the top relevant Q&As.
- Implement `generate_response(query, context)` that composes an answer citing which FAQs were used.
- Provide a CLI: `python main.py "How do I reset my password?"` -> prints answer and sources.

## Stretch
- Add metadata filtering (e.g., `--tag billing`).
- Add a simple reranker that prioritizes exact token overlap.
