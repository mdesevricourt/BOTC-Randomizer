from __future__ import annotations

from random import Random
from typing import Dict, List, Sequence


def weighted_choice_without_replacement(
    rng: Random,
    items: Sequence[str],
    k: int,
    weights: Dict[str, float],
) -> List[str]:
    """Sample k distinct items from items using non-negative weights."""
    if k < 0:
        raise ValueError("k must be >= 0")
    if k > len(items):
        raise ValueError("k cannot exceed number of available items")

    available = list(items)
    chosen: List[str] = []

    for _ in range(k):
        ws = []
        for it in available:
            w = float(weights.get(it, 1.0))
            ws.append(max(0.0, w))

        total = sum(ws)
        if total <= 0:
            raise ValueError("All remaining weights are zero; cannot sample.")

        r = rng.random() * total
        acc = 0.0
        idx = 0
        for i, w in enumerate(ws):
            acc += w
            if r <= acc:
                idx = i
                break

        chosen_item = available.pop(idx)
        chosen.append(chosen_item)

    return chosen
