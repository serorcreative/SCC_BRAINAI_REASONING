"""Audit du raisonnement : intégrité, traçabilité, sûreté (non-souveraineté).

* **intégrité** : l'empreinte de chaque élément correspond à son contenu ;
* **traçabilité** : chaque élément cite au moins une source ;
* **sûreté** : toute décision est *candidate* ou porte un approbateur **humain** ;
  aucune décision n'est marquée souveraine ou appliquée automatiquement.
"""

from __future__ import annotations

from typing import Any, Dict, List

from scc_brainai_reasoning.core.model import Deliberation, DecisionStatus


def _elements(delib: Deliberation) -> List:
    return (list(delib.facts) + list(delib.constraints) + list(delib.hypotheses)
            + list(delib.inferences) + list(delib.options) + list(delib.risks))


def audit_deliberation(delib: Deliberation) -> Dict[str, Any]:
    els = _elements(delib)
    integrity_broken = sorted(e.id for e in els if not e.verify())
    untraced = sorted(e.id for e in els if not e.sources)

    decision = delib.decision
    status = decision.get("status", DecisionStatus.CANDIDATE.value)
    safe = True
    reasons: List[str] = []
    if status != DecisionStatus.CANDIDATE.value and not decision.get("validation", {}).get("approver"):
        safe = False
        reasons.append("décision non-candidate sans approbateur humain")
    if decision.get("sovereign") is True or decision.get("data", {}).get("sovereign") is True:
        safe = False
        reasons.append("décision marquée souveraine")
    if decision.get("applied") is True:
        safe = False
        reasons.append("décision marquée appliquée")

    return {
        "ok": not integrity_broken and not untraced and safe,
        "integrity": {"ok": not integrity_broken, "broken": integrity_broken},
        "traceability": {"ok": not untraced, "untraced": untraced},
        "safety": {"ok": safe, "reasons": reasons, "decision_status": status},
        "elements": len(els),
    }


def audit_all(delibs: List[Deliberation]) -> Dict[str, Any]:
    reports = {d.id: audit_deliberation(d) for d in delibs}
    return {"ok": all(r["ok"] for r in reports.values()) if reports else True,
            "count": len(delibs), "per_deliberation": reports}


__all__ = ["audit_deliberation", "audit_all"]
