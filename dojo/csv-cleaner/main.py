"""CSV Cleaner stub."""
from __future__ import annotations
from pathlib import Path
from typing import Dict, List

def clean_csv(input_path: Path, output_path: Path, required_columns: List[str]) -> Dict[str, int]:
    raise NotImplementedError("Implement clean_csv")

def main() -> None:
    print("Implement CLI to clean a CSV file and emit stats.")

if __name__ == "__main__":
    main()
