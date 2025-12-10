# 🧠 Prompt Engineering Descriptors – Power-User Cheatsheet

## What “explicit” means
**Explicit** = stated clearly, directly, and unambiguously, with no reliance on inference.

Opposites:
- implicit
- vague
- assumed
- inferred

Use **explicit language** to reduce model guesswork and constrain outputs.

---

## 1) Scope & Completeness
Controls **how much** the model should do.

- **minimal** – only the essentials
- **exhaustive** – cover all cases
- **comprehensive** – broad, structured coverage
- **bounded** – stay within constraints
- **partial** – omissions allowed
- **self-contained** – no external context required
- **non-speculative** – no guessing or predictions
- **incremental** – add step by step

Example:
> “Provide a **minimal, self-contained** answer.”

---

## 2) Precision & Ambiguity
Controls **how strictly** instructions are interpreted.

- **explicit**
- **unambiguous**
- **literal** (no metaphor)
- **exact** (precise values/behavior)
- **deterministic** (same input → same output)
- **formal** (technical language only)

Example:
> “Use **explicit, literal** language. Avoid analogies.”

---

## 3) Style & Tone
Controls **voice**, not content.

- **concise**
- **neutral**
- **clinical**
- **authoritative**
- **didactic** (teaching)
- **operational** (action-focused)
- **diagnostic** (identify issues)
- **advisory** (recommendations)

Example:
> “Respond in a **clinical, operational** tone.”

---

## 4) Reasoning & Cognition
Controls **how the model reasons**.

- **step-by-step**
- **first-principles**
- **mechanistic**
- **causal**
- **procedural**
- **comparative**
- **failure-mode analysis**
- **tradeoff-aware**

Example:
> “Explain using **first-principles, causal** reasoning.”

---

## 5) Output Format & Structure
Controls **what the output looks like**.

- **single code block**
- **markdown only / no markdown**
- **JSON-only / YAML-only**
- **tabular**
- **bullet list**
- **numbered steps**
- **no preamble**
- **no summary**

Example:
> “Return **JSON only**, no prose.”

---

## 6) Constraints & Exclusions
Prevents drift.

- **do not include**
- **exclude**
- **strictly avoid**
- **never mention**
- **no alternatives**
- **no digressions**

Example:
> “**Strictly avoid** suggesting other tools.”

---

## 7) Context & Assumptions
Anchors the response.

- **assume environment X**
- **current as of**
- **offline**
- **local-only**
- **legacy-compatible**

Example:
> “Assume **macOS Intel, zsh, offline**.”

---

## Mental Model
> Prompt engineering = reducing ambiguity by replacing assumptions with constraints.

---

## One-Line Rule
If a machine followed your prompt **literally**, would the output still be correct?

