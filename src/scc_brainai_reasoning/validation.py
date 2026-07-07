"""Validation humaine des décisions candidates — garde-fou de souveraineté.

**Aucune décision souveraine sans validation humaine.** Une décision candidate ne
devient « validée » ou « rejetée » que par une **action humaine explicite**, tracée
(approbateur, motif, horodatage figé). Le raisonnement ne peut produire qu'une
décision *candidate*.
"""

from __future__ import annotations

from typing import Any, Dict

from scc_brainai_reasoning.core.errors import ValidationError
from scc_brainai_reasoning.core.model import DecisionStatus, can_transition


class HumanValidationPolicy:
    def __init__(self, as_of: str):
        self._as_of = as_of

    def _apply(self, decision: Dict[str, Any], target: str, action: str,
               approver: str, reason: str) -> Dict[str, Any]:
        if not approver:
            raise ValidationError("Une validation exige un approbateur humain explicite.")
        current = decision.get("status", DecisionStatus.CANDIDATE.value)
        if not can_transition(current, target):
            raise ValidationError(f"Transition interdite : {current} -> {target}.")
        decision["status"] = target
        decision["validation"] = {"action": action, "approver": approver, "reason": reason,
                                  "at": self._as_of, "previous": decision.get("validation", {})}
        return decision

    def validate(self, decision: Dict[str, Any], approver: str, reason: str = "") -> Dict[str, Any]:
        return self._apply(decision, DecisionStatus.VALIDATED.value, "validate", approver, reason)

    def reject(self, decision: Dict[str, Any], approver: str, reason: str = "") -> Dict[str, Any]:
        return self._apply(decision, DecisionStatus.REJECTED.value, "reject", approver, reason)


__all__ = ["HumanValidationPolicy"]
