"""Temporal Sequence Modeling utilities."""
from __future__ import annotations

import time
from typing import List, Dict

try:
    import torch
    from torch import nn
except Exception:  # pragma: no cover - optional dependency
    torch = None
    nn = None


class TemporalSequenceLogger:
    """Logs user actions with timestamps."""

    def __init__(self) -> None:
        self._logs: Dict[str, List[tuple[str, float]]] = {}

    def log_action(self, user_id: str, action: str) -> None:
        self._logs.setdefault(user_id, []).append((action, time.time()))

    def get_sequence(self, user_id: str) -> List[tuple[str, float]]:
        return self._logs.get(user_id, [])


class LSTMPredictor(nn.Module):
    """Simple LSTM model for sequence prediction demo."""

    def __init__(self, vocab_size: int, hidden_size: int = 16) -> None:
        if nn is None:
            raise RuntimeError("PyTorch is required for LSTMPredictor")
        super().__init__()
        self.embed = nn.Embedding(vocab_size, hidden_size)
        self.lstm = nn.LSTM(hidden_size, hidden_size, batch_first=True)
        self.fc = nn.Linear(hidden_size, vocab_size)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        emb = self.embed(x)
        out, _ = self.lstm(emb)
        return self.fc(out[:, -1, :])
