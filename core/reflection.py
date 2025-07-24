"""Simple reflection helper for recording outcomes."""

from __future__ import annotations

import logging


def reflect(outcome: str, details: str = "") -> str:
    """Log an outcome and return a basic lesson learned summary."""
    lesson = f"Outcome: {outcome}. {details}".strip()
    logging.info("Reflection: %s", lesson)
    return f"Lesson learned: {lesson}"
