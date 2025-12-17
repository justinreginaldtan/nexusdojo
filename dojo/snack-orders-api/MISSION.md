# Snack Orders API

Build a FastAPI service that manages snack orders in memory. Expose endpoints to create orders, list them, update status, and provide simple analytics.

## Setup
- Install kata deps: `pip install -r requirements.txt`
- Run tests: `python -m unittest`

## Requirements
- Endpoints: `/health` (GET), `/orders` (POST to create, GET to list), `/orders/{order_id}` (PATCH to update status), `/stats` (GET summary totals by status and most popular snack).
- Validate payloads (customer name, snack name, quantity >=1, status in {pending, preparing, ready, served}).
- Add a lightweight rate-limit stub middleware (per-client counter with in-memory bucket) and return 429 when exceeded.
- Return JSON with consistent shapes and helpful error messages.
- Keep storage in memory; no DB.

## Stretch
- Add optional query params to filter orders by status and customer.
- Add a background task that marks old pending orders as canceled after N minutes (configurable constant) and expose the value via `/health`.
