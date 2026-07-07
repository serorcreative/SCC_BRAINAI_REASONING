"""Contraintes et risques (déterministe).

Les **contraintes** combinent celles fournies par l'appelant, celles ancrées dans
SCC (doctrines) et des garde-fous doctrinaux par défaut. Les **risques** sont
identifiés par option, tracés vers l'option et la contrainte concernées.
"""

from __future__ import annotations

from typing import List

from scc_brainai_reasoning.core.model import (
    Problem,
    ReasoningConstraint,
    ReasoningOption,
    ReasoningRisk,
)

# Garde-fous doctrinaux par défaut (toujours applicables à une décision SCC).
_DEFAULT_CONSTRAINTS = [
    ("Toute décision structurante doit produire un ADR.", "SCC-DOC-0009"),
    ("Aucune action T3 (irréversible/sortante) sans validation humaine.", "gouvernance-T3"),
    ("Une décision candidate n'est jamais appliquée automatiquement.", "reasoning-safety"),
]

# Risques génériques par nom d'option canonique.
_OPTION_RISKS = {
    "Statu quo": ("Risque d'inaction : le problème sous-jacent persiste.", 0.5),
    "Agir maintenant": ("Risque d'irréversibilité : agir tôt peut être coûteux à défaire.", 0.6),
    "Différer": ("Risque de retard : reporter peut aggraver la situation.", 0.5),
    "Approche complète": ("Risque de sur-ingénierie : coût et complexité accrus.", 0.5),
    "Approche minimale": ("Risque de sous-couverture : besoin partiellement satisfait.", 0.4),
    "Investigation élargie": ("Risque de temporisation : analyse sans fin.", 0.4),
}


def derive_constraints(problem: Problem, grounded: List[ReasoningConstraint]) -> List[ReasoningConstraint]:
    constraints: List[ReasoningConstraint] = list(grounded)
    for text in problem.given_constraints:
        constraints.append(ReasoningConstraint(
            statement=text, sources=[f"problem:{problem.id}"], confidence=0.8,
            tags=["constraint", "given"]).finalize())
    for text, ref in _DEFAULT_CONSTRAINTS:
        constraints.append(ReasoningConstraint(
            statement=text, sources=[f"doctrine:{ref}"], confidence=0.9,
            tags=["constraint", "default"], data={"ref": ref}).finalize())
    # déduplique par id, tri déterministe
    uniq = {c.id: c for c in constraints}
    return sorted(uniq.values(), key=lambda e: e.id)


def identify_risks(options: List[ReasoningOption], constraints: List[ReasoningConstraint],
                   facts: List) -> List[ReasoningRisk]:
    risks: List[ReasoningRisk] = []
    health_degraded = any(f.data.get("overall") not in (None, "ok") for f in facts
                          if "health" in f.tags)

    for opt in options:
        name = opt.data.get("name", "")
        # risque générique par option
        generic = _OPTION_RISKS.get(name)
        if generic:
            risks.append(ReasoningRisk(
                statement=generic[0], sources=[opt.id], confidence=0.5,
                tags=["risk", "option"], data={"option": name, "severity": generic[1]}).finalize())
        # risque de santé pour les options d'action
        if health_degraded and name in ("Agir maintenant", "Approche complète"):
            risks.append(ReasoningRisk(
                statement=f"Risque aggravé : agir (« {name} ») alors que la santé système est dégradée.",
                sources=[opt.id, "control_plane:health"], confidence=0.7,
                tags=["risk", "health"], data={"option": name, "severity": 0.7}).finalize())
        # risque de non-conformité si l'option mentionne un contournement
        desc = (opt.data.get("description", "") + " " + name).lower()
        if any(w in desc for w in ("sans adr", "contourner", "ignorer", "bypass")):
            risks.append(ReasoningRisk(
                statement=f"Risque de non-conformité : « {name} » pourrait enfreindre une contrainte.",
                sources=[opt.id], confidence=0.8,
                tags=["risk", "compliance"], data={"option": name, "severity": 0.9}).finalize())

    return sorted(risks, key=lambda e: e.id)


__all__ = ["derive_constraints", "identify_risks"]
