"""Multi-modal feature fusion."""
from __future__ import annotations

import numpy as np
from typing import Optional


class MultiModalFusion:
    """Fuses vectors from multiple modalities by simple concatenation."""

    def fuse(
        self,
        text_vec: np.ndarray,
        code_vec: np.ndarray,
        image_vec: Optional[np.ndarray] = None,
        graph_vec: Optional[np.ndarray] = None,
    ) -> np.ndarray:
        parts = [text_vec, code_vec]
        if image_vec is not None:
            parts.append(image_vec)
        if graph_vec is not None:
            parts.append(graph_vec)
        return np.concatenate(parts)
