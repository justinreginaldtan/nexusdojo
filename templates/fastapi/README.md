# {{IDEA}}

- Template: fastapi
- Created: {{CREATED_AT}}
- Slug: {{SLUG}}

## Task
Build a tiny HTTP API with FastAPI that fulfills the idea above. Start from the health check and echo endpoints and extend with your own routes.

## Suggested steps
1) Install deps: `python -m pip install -r requirements.txt`
2) Run the server locally: `python main.py` (hot reload on change).
3) Add or adjust endpoints to match the idea.
4) Tighten the seeded `tests/test_smoke.py` and unskip `tests/test_edge_cases.py` with your riskiest scenarios.
5) Log progress: `dojo log {{SLUG}} --note "<what you did>"`

## Testing
```bash
python -m unittest
```
