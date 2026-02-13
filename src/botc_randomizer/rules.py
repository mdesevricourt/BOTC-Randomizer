from __future__ import annotations

from typing import Dict, Set, Tuple

# ----------------------------
# Core rules: player count -> base counts
# ----------------------------

BASE_COUNTS: Dict[int, Tuple[int, int, int, int]] = {
    5:  (3, 0, 1, 1),
    6:  (3, 1, 1, 1),
    7:  (5, 0, 1, 1),
    8:  (5, 1, 1, 1),
    9:  (5, 2, 1, 1),
    10: (7, 0, 2, 1),
    11: (7, 1, 2, 1),
    12: (7, 2, 2, 1),
    13: (9, 0, 3, 1),
    14: (9, 1, 3, 1),
    15: (9, 2, 3, 1),
}


def get_base_counts(n_players: int) -> Tuple[int, int, int, int]:
    """Return the base (townfolk, outsiders, minions, demons) counts for a player count."""
    if n_players not in BASE_COUNTS:
        raise ValueError("Supported player counts are 5..15 inclusive.")
    return BASE_COUNTS[n_players]


def apply_outsider_mods(
    base_counts: Tuple[int, int, int, int],
    included_minions: Set[str],
) -> Tuple[int, int, int, int]:
    """Apply minion-based outsider modifiers (e.g., Baron) to base counts."""
    tf, out, mn, dm = base_counts
    if "Baron" in included_minions:
        tf -= 2
        out += 2
    if tf < 0:
        raise ValueError("Invalid counts after outsider mods (Townfolk < 0).")
    return tf, out, mn, dm
