"""Weather + News agent stub."""
from __future__ import annotations
from typing import Any, Dict, List

def get_weather(city: str) -> Dict[str, Any]:
    raise NotImplementedError("Implement get_weather")

def get_news(topic: str) -> List[str]:
    raise NotImplementedError("Implement get_news")

def route_prompt(prompt: str) -> Dict[str, Any]:
    raise NotImplementedError("Implement route_prompt")

def main() -> None:
    print("Implement the tools, router, and CLI entry point.")

if __name__ == "__main__":
    main()
