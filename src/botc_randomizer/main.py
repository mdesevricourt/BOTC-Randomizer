#!/usr/bin/env python3
"""
BOTC Trouble Brewing randomizer with an open-ended constraint system.

Key idea:
- Generate a proposed setup (bag) using per-role weights.
- Compute a log-score from an arbitrary list of constraints.
- Accept/reject proposals with probability proportional to exp(log_score)
  (plus optional pairwise synergies).

This makes it easy to add constraints like:
- “Top 4 roles all in play should be unlikely” (soft penalty).
- “At least one source of misinformation” (hard or soft).
- “At most one of these roles” / “at least k of this set”, etc.
"""

from __future__ import annotations

from random import Random

from botc_randomizer.constraints import (
    HardRequireAny,
    RandomizerConfig,
    SoftDiscourageAll,
)
from botc_randomizer.generator import generate_setup_trouble_brewing

# ----------------------------
# Example: constraints you asked for
# ----------------------------

def main() -> None:
    """Run an example randomization for Trouble Brewing."""
    rng = Random(123)

    # Example “power tiers” you maintain yourself:
    TOP4 = {"Spy", "Poisoner", "Fortune Teller", "Undertaker"}   # example; you choose
    BOTTOM3 = {"Butler", "Saint", "Recluse"}                     # example; you choose

    # Example tag-like set for “misinformation sources” (TB examples):
    # - Drunk changes their own info
    # - Recluse can register as evil/demon
    # - Spy can register as good/townfolk (also disrupts info ecosystem)
    MISINFORMATION = {"Drunk", "Poisoner"}

    config = RandomizerConfig(
        role_weights={
            # Optional: tweak base frequencies without touching constraints
            # "Baron": 1.05,
        },
        constraints=[
            # 1) “All top 4 roles in play should be unlikely”
            SoftDiscourageAll(roleset=TOP4, penalty=3.0),

            # 2) “Some for bottom 3”: example—discourage having ALL 3 at once
            SoftDiscourageAll(roleset=BOTTOM3, penalty=2.0),

            # (Alternative: prefer 0–1 of them rather than 2–3)
            # SoftPreferBetweenKAndL(roleset=BOTTOM3, k=0, l=1, penalty_per_step=1.5),

            # 3) “At least one source of misinformation”
            # Hard version (never allow no-misinfo setups):
            HardRequireAny(roleset=MISINFORMATION),

            # Soft version (instead of hard): encourage misinfo presence
            # SoftEncourageAny(roleset=MISINFORMATION, bonus=1.0),
        ],
        synergies=[
            # You can keep using pairwise terms too (optional):
            ("Spy", "Poisoner", -2.0),
        ],
        synergy_temperature=1.0,
    )

    setup = generate_setup_trouble_brewing(10, rng=rng, config=config)
    print("Setup for 10 players:")
    for k in ["townfolk", "outsiders", "minions", "demons"]:
        print(f"{k:9s}: {setup[k]}")


if __name__ == "__main__":
    main()


