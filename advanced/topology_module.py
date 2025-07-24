"""Topological data analysis utilities using giotto-tda."""
from __future__ import annotations

import numpy as np
from typing import Any

try:
    from gtda.homology import VietorisRipsPersistence
except Exception:  # pragma: no cover - optional dependency
    VietorisRipsPersistence = None

try:
    from sklearn.cluster import DBSCAN
except Exception:  # pragma: no cover - optional dependency
    DBSCAN = None


class TopologicalAnalyzer:
    """Compute persistence diagrams and cluster embeddings."""

    def __init__(self) -> None:
        if VietorisRipsPersistence:
            self.pers = VietorisRipsPersistence(homology_dimensions=[0, 1])
        else:  # pragma: no cover - missing dependency
            self.pers = None
        if DBSCAN:
            self.clusterer = DBSCAN(eps=0.5, min_samples=2)
        else:
            self.clusterer = None

    def persistence_diagram(self, vectors: np.ndarray) -> Any:
        if self.pers:
            return self.pers.fit_transform(vectors)
        return []

    def cluster_embeddings(self, vectors: np.ndarray) -> Any:
        if self.clusterer:
            return self.clusterer.fit_predict(vectors)
        return []
