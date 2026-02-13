from __future__ import annotations

from math import exp
from random import Random
from typing import Dict, List, Optional, Set

from .constraints import (
    RandomizerConfig,
    evaluate_constraints,
    log_score_from_synergies,
)
from .roles import ALL_ROLES_TB, DEMONS_TB, MINIONS_TB, OUTSIDERS_TB, TOWNFOLK_TB
from .rules import apply_outsider_mods, get_base_counts
from .sampling import weighted_choice_without_replacement

# ----------------------------
# Main generator: proposals + accept/reject with exp(log_score)
# ----------------------------

def generate_setup_trouble_brewing(
    n_players: int,
    rng: Optional[Random] = None,
    config: Optional[RandomizerConfig] = None,
    max_attempts: int = 100_000,
) -> Dict[str, List[str]]:
    """Generate a Trouble Brewing setup using weighted sampling and constraints."""
    rng = rng or Random()

    if config is None:
        config = RandomizerConfig(
            role_weights={},
            constraints=[],
            synergies=[],
            synergy_temperature=1.0,
        )

    base_tf, base_out, base_mn, base_dm = get_base_counts(n_players)

    # Fill missing weights with default 1.0
    weights = {r: 1.0 for r in ALL_ROLES_TB}
    for role, w in config.role_weights.items():
        if role not in weights:
            raise ValueError(f"Unknown role in weights: {role}")
        weights[role] = float(w)

    best_seen: Optional[Dict[str, List[str]]] = None
    best_log_score = float("-inf")
    max_log_score_seen = float("-inf")  # adaptive normalization for accept prob

    for _ in range(max_attempts):
        # Sample minions first, then apply Baron outsider-mod
        minions = set(weighted_choice_without_replacement(rng, MINIONS_TB, base_mn, weights))
        tf_count, out_count, mn_count, dm_count = apply_outsider_mods(
            (base_tf, base_out, base_mn, base_dm),
            included_minions=minions,
        )

        demons = weighted_choice_without_replacement(rng, DEMONS_TB, dm_count, weights)
        outsiders = weighted_choice_without_replacement(rng, OUTSIDERS_TB, out_count, weights)
        townfolk = weighted_choice_without_replacement(rng, TOWNFOLK_TB, tf_count, weights)

        roles_in_play = set(demons) | set(outsiders) | set(townfolk) | set(minions)

        context = {
            "n_players": n_players,
            "counts": {"townfolk": tf_count, "outsiders": out_count, "minions": mn_count, "demons": dm_count},
        }

        feasible, logw_constraints = evaluate_constraints(roles_in_play, context, config.constraints)
        if not feasible:
            continue

        logw_synergy = log_score_from_synergies(roles_in_play, config.synergies, config.synergy_temperature)
        log_score = logw_constraints + logw_synergy

        # Track best (order by script list)
        townfolk_ordered = [r for r in TOWNFOLK_TB if r in townfolk]
        outsiders_ordered = [r for r in OUTSIDERS_TB if r in outsiders]
        minions_ordered = [r for r in MINIONS_TB if r in minions]
        demons_ordered = [r for r in DEMONS_TB if r in demons]

        proposal_dict = {
            "townfolk": townfolk_ordered,
            "outsiders": outsiders_ordered,
            "minions": minions_ordered,
            "demons": demons_ordered,
        }
        if log_score > best_log_score:
            best_log_score = log_score
            best_seen = proposal_dict

        # Adaptive accept/reject using log-scores:
        if log_score > max_log_score_seen:
            max_log_score_seen = log_score

        # accept probability = exp(log_score - max_log_score_seen) in (0, 1]
        accept_p = exp(log_score - max_log_score_seen)
        if rng.random() <= accept_p:
            return proposal_dict

    if best_seen is None:
        raise RuntimeError("Failed to generate any valid setup; constraints may be too strict.")
    return best_seen

    if best_seen is None:
        raise RuntimeError("Failed to generate any valid setup; constraints may be too strict.")
    return best_seen
