"""Tiny JSON-backed high-score store."""

from __future__ import annotations

import json
from pathlib import Path


def load_high_score(path: Path) -> int:
    """Return the saved high score, or 0 if none exists yet / the file is bad."""
    try:
        with open(path, encoding="utf-8") as handle:
            data = json.load(handle)
        return int(data.get("high_score", 0))
    except (FileNotFoundError, json.JSONDecodeError, ValueError, TypeError):
        return 0


def save_high_score(path: Path, score: int) -> None:
    """Persist `score` as the new high score, creating the parent directory if needed."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump({"high_score": score}, handle)
