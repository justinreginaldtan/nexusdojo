# --- SECTION 1: IMPORTS & SETUP ---
# Keep the whole pipeline visible here so you see how retrieval feeds generation.
from typing import List


# --- SECTION 2: YOUR LOGIC (Write Code Here) ---
def retrieve_context(query: str, top_k: int = 3) -> List[str]:
    """
    Simulate retrieving relevant text chunks from a vector database.
    Replace this with your actual RAG retrieval (e.g., ChromaDB, FAISS).
    """
    return [f"Context for '{query}' chunk {i + 1}" for i in range(top_k)]


def generate_response(query: str, context: List[str]) -> str:
    """
    Simulate generating a response using an LLM based on query and context.
    Replace this with a real model call and prompt that includes retrieved chunks.
    """
    return f"Response to '{query}' based on context: {context}"


def main() -> None:
    """Simple demo entry point so you can run `python main.py` and see output."""
    print("RAG Pipeline Kata: implement retrieve_context and generate_response.")
    print("Run tests in the 'tests' folder.")


# --- SECTION 3: THE ENGINE (Don't Touch Yet) ---
if __name__ == "__main__":
    # This guard makes sure main() runs only when executing `python main.py`.
    main()
