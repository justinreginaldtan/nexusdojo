# Retrying HTTP Client

Implement a small HTTP client with retries, backoff, and a simple circuit-breaker.

## Requirements
- Provide a function `fetch(url, *, retries=3, backoff=0.2, timeout=3.0)` that issues GET requests.
- On retriable errors (timeout, 5xx), retry with exponential backoff; on 4xx, do not retry.
- Implement a circuit-breaker: after N consecutive failures, short-circuit for a cooldown window and raise a descriptive error.
- Return a structured result object with status, text/body, attempts, and whether the breaker is open.
- Add a CLI: `python main.py https://example.com` with flags for retries/backoff/timeout.

## Stretch
- Add jitter to backoff and configurable retriable status codes.
- Add optional caching for successful responses.
