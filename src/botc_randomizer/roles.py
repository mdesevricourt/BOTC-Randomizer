from __future__ import annotations

from typing import List

# ----------------------------
# Trouble Brewing role lists
# ----------------------------

TOWNFOLK_TB: List[str] = [
    "Washerwoman", "Librarian", "Investigator", "Chef", "Empath",
    "Fortune Teller", "Undertaker", "Monk", "Ravenkeeper", "Virgin",
    "Slayer", "Soldier", "Mayor",
]
OUTSIDERS_TB: List[str] = ["Butler", "Drunk", "Recluse", "Saint"]
MINIONS_TB: List[str] = ["Poisoner", "Spy", "Scarlet Woman", "Baron"]
DEMONS_TB: List[str] = ["Imp"]

ALL_ROLES_TB: List[str] = TOWNFOLK_TB + OUTSIDERS_TB + MINIONS_TB + DEMONS_TB
