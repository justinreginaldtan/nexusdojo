# AI Fundamentals: LLMs, RAG Architectures, and Agents

**Date:** December 6, 2025  
**Context:** Deep dive into AI Engineering concepts (Vibe Coding Context)

---

## 1. The Core Reality of LLMs
To understand AI engineering, we must demystify the model.

*   **The "Frozen Brain":** An LLM is a static file of weights (parameters). It contains a snapshot of the internet up to its training cutoff. It cannot learn, it cannot see "now," and it has no inherent memory of you.
*   **The Context Window:** The model's "Short-Term Memory" (RAM). This is the only place where "learning" happens during a conversation. It is finite.
*   **Inference:** The process of the model calculating the next token based on the input.

## 2. RAG (Retrieval-Augmented Generation)
RAG is the architecture used to bridge the gap between the **Frozen Model** and **Dynamic Data**.

> **Analogy:** The Model is a genius with amnesia. RAG is the process of handing it a cheat sheet (Context) before asking it a question.

### The Pipeline
1.  **Retrieval:** Search a Knowledge Base (Vector DB, Files, API).
2.  **Augmentation:** Inject the search results into the Context Window.
3.  **Generation:** The LLM answers based on the injected context.

---

## 3. The Great Divide: Naive vs. Agentic RAG

### A. Naive RAG (The "Pipeline")
*   **Definition:** A deterministic, hard-coded flow. The system *always* searches the database before sending the prompt to the LLM.
*   **Flow:** `Input -> Search DB -> Paste Results -> LLM Answer`
*   **Key Characteristic:** The LLM makes **zero decisions** about retrieving data. The search happens *to* it.
*   **Scenario (The Law Firm):**
    *   *Inefficiency:* Users says "Hi," system searches legal docs (wasteful).
    *   *Goal:* User asks about policy, system guarantees answer comes from the docs.
*   **Why it dominates (90% of Production):**
    *   **Predictability:** Input A always equals Output B.
    *   **Safety:** No risk of the model "going rogue."
    *   **Cost/Speed:** Only 1 LLM call.

### B. Agentic RAG (The "Loop")
*   **Definition:** An autonomous workflow where the LLM decides *if* and *how* to retrieve data.
*   **Flow:** `Input -> LLM Reason -> Tool Call? -> Tool Output -> LLM Synthesis`
*   **The Litmus Test:** Can the system look at a request and **choose** to:
    1. Answer from memory?
    2. Search a database?
    3. Run a script?
    *If yes, it is an Agent.*
*   **Why it's the future (but risky):**
    *   *Pros:* Handles complex, multi-step reasoning (Math + Search + Summarize).
    *   *Cons:* Unpredictable, slower (multiple LLM hops), harder to debug.

---

## 4. Tool Use & The "Market Chaos"
*   **Tool Use:** The mechanism by which an Agent acts. It's "Agentic Retrieval."
*   **How it works:** The System Prompt describes tools. The LLM probabilistically generates a structured string (e.g., `call:get_weather`) which the environment executes.
*   **The Engineering Challenge:** The market is hot because "Flow Engineering" (making these decision loops reliable) is difficult. It involves balancing prompt sensitivity (knowing when to call) with safety (blocking malicious calls).

---

## 5. Glossary
*   **Frozen Weights:** The static parameters of the trained model.
*   **Hallucination:** When the model generates plausible but incorrect facts (often due to lack of context).
*   **Vector Database:** A database that stores data as mathematical embeddings (meaning), allowing for semantic search.
*   **Semantic Search:** Searching by *meaning* ("broken login" matches "auth error") rather than keywords.
*   **Router:** A component in Advanced RAG that directs queries (e.g., "If X, go to Database; If Y, go to LLM").
