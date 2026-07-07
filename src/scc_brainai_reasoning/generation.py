"""Génération d'hypothèses et d'options (déterministe, augmentable par un LLM)."""

from __future__ import annotations

from typing import List

from scc_brainai_reasoning.core.model import (
    Problem,
    ReasoningHypothesis,
    ReasoningOption,
)

# Options canoniques par type de problème, si l'appelant n'en fournit pas.
_CANONICAL_OPTIONS = {
    "decision": [("Statu quo", "Ne rien changer pour l'instant."),
                 ("Agir maintenant", "Mettre en œuvre le changement sans délai."),
                 ("Différer", "Reporter la décision en attendant plus d'éléments.")],
    "design": [("Approche minimale", "Réaliser la version la plus simple qui répond au besoin."),
               ("Approche complète", "Réaliser une version étendue et robuste.")],
    "diagnostic": [("Hypothèse principale", "Traiter d'abord la cause la plus probable."),
                   ("Investigation élargie", "Collecter davantage d'éléments avant d'agir.")],
    "evaluation": [("Retenir", "Conclure favorablement selon les critères."),
                   ("Écarter", "Conclure défavorablement selon les critères.")],
    "analysis": [("Poursuivre l'analyse", "Approfondir avant toute décision."),
                 ("Conclure", "Statuer avec les éléments disponibles.")],
}


def build_options(problem: Problem, ptype: str, provider=None) -> List[ReasoningOption]:
    raw = problem.options
    if not raw:
        raw = [{"name": n, "description": d} for n, d in _CANONICAL_OPTIONS.get(ptype, _CANONICAL_OPTIONS["analysis"])]
        # extension LLM (optionnelle) : suggestions supplémentaires, jamais requises.
        if provider is not None and provider.available():
            extra = provider.suggest_options(problem.question, problem.given_facts) or []
            raw = raw + [e for e in extra if isinstance(e, dict) and e.get("name")]

    options: List[ReasoningOption] = []
    for o in raw:
        name = str(o.get("name", "")).strip()
        if not name:
            continue
        options.append(ReasoningOption(
            statement=f"Option : {name}",
            sources=[f"problem:{problem.id}"], confidence=0.5,
            tags=["option"],
            data={"name": name, "description": str(o.get("description", "")),
                  "benefit": float(o.get("benefit", 0.5)), **{k: v for k, v in o.items()
                  if k not in ("name", "description", "benefit")}}).finalize())
    return sorted(options, key=lambda e: e.id)


def formulate_hypotheses(problem: Problem, ptype: str, options: List[ReasoningOption],
                         provider=None) -> List[ReasoningHypothesis]:
    hyps: List[ReasoningHypothesis] = []
    # Hypothèse générale liée au type.
    general = {
        "decision": "L'option la mieux notée sur les critères retenus est préférable.",
        "diagnostic": "La cause la plus fréquente/impactante explique l'essentiel du problème.",
        "design": "Commencer minimal puis étendre réduit le risque global.",
        "evaluation": "Le respect des critères pondérés détermine la conclusion.",
        "analysis": "Des éléments supplémentaires modifieraient peu la conclusion.",
    }.get(ptype, "Des éléments supplémentaires modifieraient peu la conclusion.")
    hyps.append(ReasoningHypothesis(statement=f"Hypothèse : {general}",
                                    sources=[f"problem:{problem.id}"], confidence=0.4,
                                    tags=["hypothesis", ptype]).finalize())
    # Une hypothèse conditionnelle par option (falsifiable).
    for opt in options:
        name = opt.data.get("name", "")
        hyps.append(ReasoningHypothesis(
            statement=f"Hypothèse : « {name} » est préférable si ses bénéfices l'emportent sur ses risques.",
            sources=[opt.id], confidence=0.4, tags=["hypothesis", "conditional"],
            data={"option": name}).finalize())
    # extension LLM (optionnelle).
    if provider is not None and provider.available():
        for s in provider.suggest_hypotheses(problem.question, problem.given_facts) or []:
            hyps.append(ReasoningHypothesis(statement=f"Hypothèse (assistée) : {s}",
                                            sources=[f"problem:{problem.id}"], confidence=0.4,
                                            tags=["hypothesis", "assisted"]).finalize())
    return sorted(hyps, key=lambda e: e.id)


__all__ = ["build_options", "formulate_hypotheses"]
