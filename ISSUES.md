# Issue Log

Kata-Generation [i think i fixed it]
  - Skeleton given is so hard to follow lol. fix the prompt for better skeleton generation. keep best U/X in mind. THIS SHOULD BE SOMETHING PEOPLE PAY $10000000000 FOR TO LEARN.

LLM Local Model Integration
  - Tried to implement local model integration with Ollama, but it's not worth the effort. Model is too slow and not accurate, better off just having codex/claudecode to create the problems on the fly, and for advice.

Progression
  - Idk if the quesitons im doing is even optimal for learning, but just code dont over-optimize.

Align Username on main menu banner
  - Why can't any vibecoding tool align the username on the main menu banner? its so annoying.

Some test cases for new katas are simplified/may not work or be accurate?
  - JWT Notes auth deps: Currently uses plain str emails and a simple PBKDF2 hash to avoid email-validator/bcrypt install issues. For real
    email validation, install email-validator and switch back to EmailStr; for bcrypt hashing, ensure bcrypt works in your env and update the
    hash/verify functions.
  - API/MCP test dependencies: FastAPI smoke tests rely on httpx (fastapi.testclient). If httpx isn’t installed, tests will skip. Install httpx
    (or per-kata requirements.txt) to run tests.
  - Test coverage: Smoke tests are minimal; they don’t cover edge cases/error paths. Expand tests before treating as production-grade.