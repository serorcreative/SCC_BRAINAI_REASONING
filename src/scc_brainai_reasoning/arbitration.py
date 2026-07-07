"""Arbitrage argumenté : scoring des options, classement, inférences, décision.

Scoring déterministe pondéré (bénéfice, risque inversé, conformité, confiance). La
décision produite est **candidate** : elle exige une validation humaine et n'est
jamais appliquée.
"""

from __future__ import annotations

from typing import Any, Dict, List

from scc_brainai_reasoning.core.model import (
    Problem,
    ReasoningArbitration,
    ReasoningDecision,
    ReasoningInference,
    ReasoningOption,
)


def score_options(options: List[ReasoningOption], risks: List, facts: List,
                  weights: Dict[str, float]) -> Dict[str, Dict[str, Any]]:
    fact_conf = round(sum(f.confidence for f in facts) / len(facts), 3) if facts else 0.5
    out: Dict[str, Dict[str, Any]] = {}
    for opt in options:
        name = opt.data.get("name", "")
        benefit = float(opt.data.get("benefit", 0.5))
        opt_risks = [r for r in risks if r.data.get("option") == name]
        risk = round(max([r.data.get("severity", 0.5) for r in opt_risks], default=0.1), 3)
        compliance = any("compliance" in r.tags for r in opt_risks)
        constraint_fit = round(1.0 - (0.5 if compliance else 0.0), 3)
        total = round(
            weights.get("benefit", 0.4) * benefit
            + weights.get("risk", 0.3) * (1.0 - risk)
            + weights.get("constraint_fit", 0.2) * constraint_fit
            + weights.get("confidence", 0.1) * fact_conf, 4)
        out[opt.id] = {"option": name, "benefit": benefit, "risk": risk,
                       "constraint_fit": constraint_fit, "confidence": fact_conf,
                       "total": total, "risk_count": len(opt_risks)}
    return out


def arbitrate(problem: Problem, options: List[ReasoningOption],
              scores: Dict[str, Dict[str, Any]], provider=None) -> ReasoningArbitration:
    ranking = sorted(options, key=lambda o: (-scores[o.id]["total"], o.id))
    ranked_view = [{"option": scores[o.id]["option"], "total": scores[o.id]["total"],
                    "scores": scores[o.id]} for o in ranking]
    top = ranking[0]
    top_name = scores[top.id]["option"]
    if len(ranking) > 1:
        runner = ranking[1]
        argument = (f"« {top_name} » (score {scores[top.id]['total']}) l'emporte sur "
                    f"« {scores[runner.id]['option']} » (score {scores[runner.id]['total']}) : "
                    f"meilleur équilibre bénéfice/risque/conformité.")
    else:
        argument = f"« {top_name} » est la seule option évaluée (score {scores[top.id]['total']})."

    data = {"ranking": ranked_view, "top": top_name, "top_option_id": top.id,
            "argument": argument, "weights_used": dict(scores[top.id])}
    if provider is not None and provider.available():
        note = provider.critique(data)
        if note:
            data["assisted_critique"] = note

    return ReasoningArbitration(
        statement=f"Arbitrage : {argument}", sources=[o.id for o in options],
        confidence=round(scores[top.id]["total"], 3), tags=["arbitration"], data=data).finalize()


def infer(facts: List, constraints: List, arbitration: ReasoningArbitration) -> List[ReasoningInference]:
    top = arbitration.data.get("top", "")
    inf = ReasoningInference(
        statement=(f"Compte tenu de {len(facts)} fait(s) et {len(constraints)} contrainte(s), "
                   f"l'option « {top} » obtient le meilleur score d'arbitrage."),
        sources=[arbitration.id] + [f.id for f in facts[:3]],
        confidence=arbitration.confidence, tags=["inference"],
        data={"top": top}).finalize()
    return [inf]


def build_decision(arbitration: ReasoningArbitration) -> ReasoningDecision:
    top = arbitration.data.get("top", "")
    return ReasoningDecision(
        statement=f"Décision candidate : retenir « {top} » (à valider par un humain).",
        sources=[arbitration.id], confidence=arbitration.confidence,
        tags=["decision", "candidate"],
        data={"option": top, "score": arbitration.confidence,
              "requires_human_validation": True, "sovereign": False}).finalize()


__all__ = ["score_options", "arbitrate", "infer", "build_decision"]
