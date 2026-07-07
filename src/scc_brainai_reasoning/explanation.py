"""Explication du raisonnement — distingue faits, hypothèses, inférences, risques,
recommandations, et produit un récit lisible et tracé.
"""

from __future__ import annotations

from typing import Any, Dict, List


def build_explanation(problem, facts, hypotheses, inferences, risks, constraints,
                      arbitration, decision) -> Dict[str, Any]:
    def stmts(items):
        return [{"id": e.id, "statement": e.statement, "sources": e.sources} for e in items]

    narrative: List[str] = [
        f"Question : « {problem.question.strip()} ».",
        f"Faits établis : {len(facts)}. Contraintes : {len(constraints)}. "
        f"Hypothèses : {len(hypotheses)}. Risques : {len(risks)}.",
        f"Arbitrage : {arbitration.get('argument', '')}",
        f"Décision candidate : {decision.get('statement', '')}",
        "Cette décision est une PROPOSITION : elle exige une validation humaine "
        "explicite et n'est jamais appliquée automatiquement.",
    ]
    return {
        "facts": stmts(facts),
        "hypotheses": stmts(hypotheses),
        "inferences": stmts(inferences),
        "risks": stmts(risks),
        "constraints": stmts(constraints),
        "recommendation": {"statement": decision.get("statement", ""),
                           "requires_human_validation": True},
        "narrative": narrative,
    }


__all__ = ["build_explanation"]
