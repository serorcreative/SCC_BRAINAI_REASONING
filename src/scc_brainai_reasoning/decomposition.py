"""Analyse et décomposition d'un problème (déterministe)."""

from __future__ import annotations

from typing import List

from scc_brainai_reasoning.core.model import Problem

# Type de problème → mots-clés déclencheurs.
_TYPES = [
    ("decision", ["faut-il", "faut il", "choisir", "option", "décider", "decider", "vs", "ou bien"]),
    ("diagnostic", ["pourquoi", "cause", "panne", "échec", "echec", "problème", "probleme"]),
    ("design", ["comment construire", "concevoir", "architecture", "concevons", "bâtir", "batir", "construire"]),
    ("evaluation", ["évaluer", "evaluer", "comparer", "mesurer", "juger", "apprécier", "apprecier"]),
]


def analyze_problem(problem: Problem) -> str:
    q = problem.question.lower()
    if problem.options:
        return "decision"
    for ptype, kws in _TYPES:
        if any(k in q for k in kws):
            return ptype
    return "analysis"


def decompose(problem: Problem, ptype: str) -> List[str]:
    """Décompose le problème en sous-questions ordonnées et déterministes."""
    steps: List[str] = [
        "Quels faits établis sont pertinents ?",
        "Quelles contraintes s'appliquent (doctrines, gouvernance, technique) ?",
    ]
    if ptype == "decision":
        steps.append("Quelles options sont en présence et comment se comparent-elles ?")
    elif ptype == "diagnostic":
        steps.append("Quelles hypothèses de cause peut-on formuler et hiérarchiser ?")
    elif ptype == "design":
        steps.append("Quelles approches candidates répondent à l'objectif ?")
    elif ptype == "evaluation":
        steps.append("Selon quels critères évaluer, et quel est le classement ?")
    else:
        steps.append("Quelles hypothèses éclairent la question ?")
    steps += [
        "Quels risques chaque piste comporte-t-elle ?",
        "Quel arbitrage argumenté en découle ?",
        "Quelle décision candidate proposer (à valider par un humain) ?",
    ]
    return steps


__all__ = ["analyze_problem", "decompose"]
