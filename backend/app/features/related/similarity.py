"""
Similarity math: how alike two embeddings are, as a number from -1 to 1.
Higher means closer in meaning.
"""

import numpy as np


def cosine_similarity(a: list[float], b: list[float]) -> float:
    va, vb = np.asarray(a), np.asarray(b)
    norm = np.linalg.norm(va) * np.linalg.norm(vb)
    return float(va @ vb / norm) if norm else 0.0
