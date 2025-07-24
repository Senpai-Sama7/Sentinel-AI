from __future__ import annotations

"""Self-reflection utilities."""

from datetime import datetime


def reflect(outcome: str, log_file: str = "reflection.log") -> str:
    """Log the outcome and return a simple lesson learned."""

    timestamp = datetime.utcnow().isoformat()
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"{timestamp} - {outcome}\n")

    lower = outcome.lower()
    if "fail" in lower or "error" in lower:
        return "Identify root cause and adjust strategy."
    return "Approach succeeded; reinforce successful steps."
