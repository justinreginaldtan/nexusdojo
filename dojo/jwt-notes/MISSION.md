# JWT Notes API

Build a FastAPI service with JWT-based auth and per-user notes.

## Setup
- Install kata deps: `pip install -r requirements.txt`
- Run tests: `python -m unittest`

## Requirements
- Endpoints: `/health` (GET), `/auth/signup` (POST email+password), `/auth/login` (POST, returns JWT), `/me` (GET), `/notes` (POST to create, GET to list), `/notes/{note_id}` (PATCH/DELETE).
- Hash passwords (use passlib/bcrypt or stdlib PBKDF2), never store plaintext.
- JWT: signed with HS256; configurable secret; include user id in claims; expire tokens after 1h; reject expired/invalid tokens.
- Notes are stored in memory by user id; enforce that users only see their notes.
- Return structured errors on auth failures (401) and validation issues (400).

## Stretch
- Add refresh tokens and `/auth/refresh`.
- Add simple rate limiting for login attempts.
