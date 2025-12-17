# Weather + News Agent (LangChain Tools)

Build an agent that routes between two tools: a weather stub and a news stub.

## Requirements
- Implement two deterministic tools:
  - `get_weather(city)`: returns a fake but structured forecast (temp/high/low/condition).
  - `get_news(topic)`: returns 3 stub headlines for the topic.
- Build a router chain that decides which tool to call based on the prompt; default to a refusal when neither matches.
- Return structured JSON with `tool_used`, `data`, and a short `explanation`.
- Add a CLI: `python main.py "What's the weather in Paris?"` or `... "Give me news about AI"`.
- Log each request/response pair to an in-memory list and support `--log` to print the log.

## Stretch
- Allow combined prompts (weather + news) by running both tools and merging the response.
- Add simple input normalization (city/title casing, trimming, etc.).
