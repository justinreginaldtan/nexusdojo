# RAG Kata Template

This template provides a basic structure for building a Retrieval-Augmented Generation (RAG) pipeline.

## Goal
Implement the `retrieve_context` function to fetch relevant information based on a query, and then use that information in `generate_response` to produce an LLM-based answer.

## Quickstart
1.  **Implement Logic:** Fill in `retrieve_context` and `generate_response` in `main.py`.
2.  **Run Tests:** `python -m unittest` in this directory.

## Core Concepts
*   **Retrieval:** How do you find the most relevant pieces of information (documents, chunks) from a knowledge base? (e.g., Vector Databases, keyword search).
*   **Augmentation:** How do you inject the retrieved context into the LLM's prompt to improve its answer?
*   **Generation:** How do you formulate the final response from the LLM?
