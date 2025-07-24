"""User personalization and adaptive learning."""
from __future__ import annotations

from typing import Dict, Any


class UserProfileManager:
    """Stores basic user profiles and preferences."""

    def __init__(self) -> None:
        self._profiles: Dict[str, Dict[str, Any]] = {}

    def update_profile(self, user_id: str, data: Dict[str, Any]) -> None:
        self._profiles.setdefault(user_id, {}).update(data)

    def get_profile(self, user_id: str) -> Dict[str, Any]:
        return self._profiles.get(user_id, {})
