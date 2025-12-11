# 🩸 The 7-Day "Hire Me" Sprint
**Status:** NON-NEGOTIABLE
**Objective:** Transform "Aspiring Student" into "Shipped AI Engineer."
**Daily Cost:** 6-8 Hours.

---

## 📅 The Schedule

### Day 1: The Foundation (Python & Git)
*   **The Goal:** Prove you write clean, documented code that others can run.
*   **Morning (Dojo):** Run `dojo menu` -> `1`. Complete 2 "Script" katas.
*   **Deep Work:** Take your best script (e.g., a data parser or calculator).
    *   Create a **brand new** folder outside the Dojo.
    *   Initialize `git`.
    *   Add a `requirements.txt`.
    *   Write a `README.md` that explains *how to run it* like you're talking to a 5-year-old.
*   **The Deliverable:** **1 Public GitHub Repository** (Clean, Linted, Documented).
*   **Why:** Juniors write code. Engineers write *software*.

### Day 2: The Deployment (FastAPI & Cloud)
*   **The Goal:** Prove you can leave `localhost`.
*   **Morning (Dojo):** `dojo start --template fastapi`. Build a simple API (e.g., "Joke of the Day" or "Unit Converter").
*   **Deep Work:**
    *   Create a `Dockerfile`.
    *   Push to GitHub.
    *   **Deploy it to Render.com** (Free Tier).
*   **The Deliverable:** A **Live URL** (e.g., `my-api.onrender.com/docs`) that you can click.
*   **Why:** "It works on my machine" gets you fired. "Click this link" gets you hired.

### Day 3: The Brain (RAG Prototype)
*   **The Goal:** Prove you understand the "AI" part of "AI Engineer."
*   **Morning (Dojo):** `dojo start --template rag`.
*   **Deep Work:**
    *   Build a script that takes a text file (e.g., your resume) and lets you chat with it.
    *   Use `chromadb` (local) and `ollama` (local) or OpenRouter.
*   **The Deliverable:** A GIF or Screen Recording of you asking the terminal a question and it answering from the text file. Post this on Twitter/LinkedIn.
*   **Why:** Visual proof beats code. Recruiters love GIFs.

### Day 4: The Agent (Tool Use)
*   **The Goal:** Show you are ready for the *next* wave of AI (Agents).
*   **Morning (Dojo):** `dojo start --template mcp`.
*   **Deep Work:**
    *   Build a script where the AI decides to call a function.
    *   Example: "What is 50 USD in JPY?" -> AI calls `get_currency_rate()` -> AI answers.
*   **The Deliverable:** A GitHub Gist showing the code and the output log showing the *decision* process.

### Day 5: The "Cyber" Edge (Security)
*   **The Goal:** Leverage your background as your "Unfair Advantage."
*   **Deep Work:**
    *   Return to your Day 2 API.
    *   Add **Input Validation** (Pydantic `Field(..., min_length=1)`).
    *   Add a simple **Rate Limiter** (or just a check for a header key).
    *   Write a 200-word LinkedIn post: *"How I secured my first AI API against injection attacks."*
*   **The Deliverable:** The LinkedIn Post.
*   **Why:** This brands you as the "Safe Choice."

### Day 6: The Package (Resume & Portfolio)
*   **The Goal:** Connect the dots.
*   **Deep Work:**
    *   Update your Resume.
    *   **Headline:** AI Solutions Engineer | Python Backend.
    *   **Experience:** Under "Projects", list the 3 things you built this week.
        *   *Project:* **Secure AI API** - Deployed FastAPI service with rate limiting (Link).
        *   *Project:* **Local RAG Chat** - Document retrieval system using Vector DB (Link).
    *   **Skills:** Python, FastAPI, Docker, RAG, Git.
*   **The Deliverable:** A PDF Resume that *doesn't* look like a student wrote it.

### Day 7: The Attack (Outreach)
*   **The Goal:** Get seen.
*   **Deep Work:**
    *   Find 10 Job Postings (LinkedIn, Y Combinator Jobs, Wellfound).
    *   **Apply.**
    *   **DM 3 Founders/CTOs:** "Hi [Name], I'm a Solutions Engineer graduating next week. I just built a secure RAG pipeline [Link] and noticed you're hiring for [Role]. Would love to share how I'd approach your [Specific Problem]."
*   **The Deliverable:** 10 Applications Sent.

---

## ⚔️ The Daily Protocol (Non-Negotiable)

1.  **08:00:** Coffee. Phone OFF.
2.  **08:15:** **NexusDojo Quick Train.** (Gets the brain moving).
3.  **09:00:** **The Daily Build.** (Execute the plan above).
4.  **13:00:** Lunch & Walk (No screens).
5.  **14:00:** **Polish & Publish.** (Write the README, record the GIF).
6.  **16:00:** **Dojo Review.** (Refactor yesterday's code).
7.  **17:00:** **Stop.** Rest is engineering fuel.

## 🛑 Rules of Engagement
1.  **No Tutorials.** Use the Docs (FastAPI docs, LangChain docs). Tutorials are for babies. You are an Engineer.
2.  **Ship It.** Ugly and deployed is better than perfect and local.
3.  **Be Loud.** If you built it and didn't post it, it didn't happen.

**Day 1 starts NOW.**
