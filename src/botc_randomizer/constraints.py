from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Set, Tuple


@dataclass(frozen=True)
class ConstraintResult:
    feasible: bool
    log_weight: float  # add to total log score


class Constraint:
    """
    Implement evaluate(roles_in_play, context) -> ConstraintResult.

    - feasible=False means hard rejection.
    - log_weight is a soft bias term; 0 = neutral, negative discourages, positive encourages.
    """
    def evaluate(self, roles: Set[str], context: Dict) -> ConstraintResult:
        """Evaluate the constraint for the given roles and context."""
        raise NotImplementedError


@dataclass(frozen=True)
class HardRequireAny(Constraint):
    """Require that at least one role from a set is in play."""
    roleset: Set[str]

    def evaluate(self, roles: Set[str], context: Dict) -> ConstraintResult:
        """Return feasible if any role in roleset is present."""
        ok = len(self.roleset.intersection(roles)) >= 1
        return ConstraintResult(feasible=ok, log_weight=0.0)


@dataclass(frozen=True)
class HardRequireAtLeastK(Constraint):
    roleset: Set[str]
    k: int

    def evaluate(self, roles: Set[str], context: Dict) -> ConstraintResult:
        """Return feasible if at least k roles from roleset are present."""
        ok = len(self.roleset.intersection(roles)) >= self.k
        return ConstraintResult(feasible=ok, log_weight=0.0)


@dataclass(frozen=True)
class HardForbidAll(Constraint):
    """Forbid the case where all roles in roleset are simultaneously in play."""
    roleset: Set[str]

    def evaluate(self, roles: Set[str], context: Dict) -> ConstraintResult:
        """Return infeasible if all roles in roleset are present."""
        bad = self.roleset.issubset(roles)
        return ConstraintResult(feasible=not bad, log_weight=0.0)


@dataclass(frozen=True)
class SoftDiscourageAll(Constraint):
    """
    If all roles in roleset are in play, add a penalty log_weight = -penalty.
    Example: discourage Spy+Poisoner or "top4 all together".
    """
    roleset: Set[str]
    penalty: float  # positive number; will be applied as -penalty

    def evaluate(self, roles: Set[str], context: Dict) -> ConstraintResult:
        """Apply a penalty when all roles in roleset are present."""
        if self.roleset.issubset(roles):
            return ConstraintResult(feasible=True, log_weight=-abs(self.penalty))
        return ConstraintResult(feasible=True, log_weight=0.0)


@dataclass(frozen=True)
class SoftEncourageAny(Constraint):
    """If any role from roleset is present, add a bonus."""
    roleset: Set[str]
    bonus: float  # positive number; will be applied as +bonus

    def evaluate(self, roles: Set[str], context: Dict) -> ConstraintResult:
        """Apply a bonus when any role in roleset is present."""
        if self.roleset.intersection(roles):
            return ConstraintResult(feasible=True, log_weight=abs(self.bonus))
        return ConstraintResult(feasible=True, log_weight=0.0)


@dataclass(frozen=True)
class SoftPreferBetweenKAndL(Constraint):
    """
    Soft preference for count of roles in roleset to be within [k, l].
    Outside the band, apply a linear penalty per role outside.
    """
    roleset: Set[str]
    k: int
    l: int
    penalty_per_step: float

    def evaluate(self, roles: Set[str], context: Dict) -> ConstraintResult:
        """Apply a linear penalty for counts outside the preferred range."""
        c = len(self.roleset.intersection(roles))
        if self.k <= c <= self.l:
            return ConstraintResult(True, 0.0)
        dist = (self.k - c) if c < self.k else (c - self.l)
        return ConstraintResult(True, -abs(self.penalty_per_step) * dist)


@dataclass
class RandomizerConfig:
    role_weights: Dict[str, float]
    constraints: List[Constraint]

    # Optional synergy (pairwise) as an additional soft term:
    synergies: List[Tuple[str, str, float]]  # (a, b, score) in log-space
    synergy_temperature: float = 1.0


def log_score_from_synergies(
    roles: Set[str],
    synergies: List[Tuple[str, str, float]],
    temperature: float,
) -> float:
    """Compute total synergy log-score for role pairs."""
    if not synergies or temperature == 0.0:
        return 0.0
    s = 0.0
    for a, b, score in synergies:
        if a in roles and b in roles:
            s += score
    return s * temperature


def evaluate_constraints(
    roles: Set[str],
    context: Dict,
    constraints: List[Constraint],
) -> Tuple[bool, float]:
    """Evaluate constraints and return (feasible, total_log_weight)."""
    logw = 0.0
    for c in constraints:
        r = c.evaluate(roles, context)
        if not r.feasible:
            return False, float("-inf")
        logw += r.log_weight
    return True, logw
