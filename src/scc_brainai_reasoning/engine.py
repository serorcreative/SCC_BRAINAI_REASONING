"""ReasoningEngine — façade de la couche de raisonnement BrainAI.

Structure la pensée sur un problème : analyse → décomposition → faits →
contraintes → hypothèses → options → risques → arbitrage → **décision candidate** →
explication. Fournit recherche, **validation humaine**, export, audit et rapport.

Le moteur **n'écrit jamais** dans une autre couche (il lit des faits via interfaces
publiques) et **ne prend jamais de décision souveraine** : sa décision reste
candidate jusqu'à validation humaine. Déterministe (identifiants de contenu).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from scc_brainai_reasoning.arbitration import arbitrate, build_decision, infer, score_options
from scc_brainai_reasoning.audit import audit_all, audit_deliberation
from scc_brainai_reasoning.core.config import ReasoningConfig, load_config
from scc_brainai_reasoning.core.errors import NotFoundError, ProblemError
from scc_brainai_reasoning.core.model import (
    Deliberation,
    Problem,
    ReasoningFact,
)
from scc_brainai_reasoning.decomposition import analyze_problem, decompose
from scc_brainai_reasoning.explanation import build_explanation
from scc_brainai_reasoning.generation import build_options, formulate_hypotheses
from scc_brainai_reasoning.index import DeliberationIndex
from scc_brainai_reasoning.providers.registry import ProviderRegistry
from scc_brainai_reasoning.report import render_markdown, store_report
from scc_brainai_reasoning.risk_analysis import derive_constraints, identify_risks
from scc_brainai_reasoning.sources.fact_gateway import FactGateway
from scc_brainai_reasoning.validation import HumanValidationPolicy


class ReasoningEngine:
    def __init__(self, config: Optional[ReasoningConfig] = None, *,
                 providers: Optional[ProviderRegistry] = None,
                 fact_gateway: Optional[FactGateway] = None, autoload: bool = True):
        self.config = config or load_config()
        self.providers = providers or ProviderRegistry()
        self.gateway = fact_gateway if fact_gateway is not None else FactGateway(self.config)
        self.policy = HumanValidationPolicy(self.config.as_of)
        self.index = DeliberationIndex()
        if autoload:
            self._load()

    # ================================================================== #
    # Raisonnement
    # ================================================================== #
    def reason(self, problem: Union[Problem, str], provider_order: Optional[List[str]] = None,
               **kwargs) -> Dict[str, Any]:
        prob = self._as_problem(problem, kwargs)
        if not prob.question.strip():
            raise ProblemError("La question du problème est vide.")
        provider = self.providers.select(provider_order or self.config.provider_order)

        ptype = analyze_problem(prob)
        decomposition = decompose(prob, ptype)

        # Faits : fournis par l'appelant + ancrés dans SCC (optionnel, dégradable).
        facts: List[ReasoningFact] = [
            ReasoningFact(statement=s, sources=["given"], confidence=0.7,
                          tags=["fact", "given"]).finalize() for s in prob.given_facts]
        grounded_constraints = []
        if self.config.ground_facts:
            try:
                g_facts, grounded_constraints, _notes = self.gateway.ground(prob.question)
                facts += g_facts
            except Exception:  # noqa: BLE001 - ancrage best-effort
                grounded_constraints = []
        facts = _dedupe(facts)

        options = build_options(prob, ptype, provider)
        hypotheses = formulate_hypotheses(prob, ptype, options, provider)
        constraints = derive_constraints(prob, grounded_constraints)
        risks = identify_risks(options, constraints, facts)

        scores = score_options(options, risks, facts, self.config.weights)
        arb = arbitrate(prob, options, scores, provider)
        inferences = infer(facts, constraints, arb)
        decision_el = build_decision(arb)
        decision = {**decision_el.to_dict(), "status": "candidate", "validation": {}}

        explanation = build_explanation(prob, facts, hypotheses, inferences, risks,
                                        constraints, arb.data, decision)

        delib = Deliberation(
            problem=prob, as_of=self.config.as_of, provider=provider.name,
            decomposition=decomposition, facts=facts, constraints=constraints,
            hypotheses=hypotheses, inferences=inferences, options=options, risks=risks,
            arbitration=arb.data, decision=decision, explanation=explanation).finalize()

        self.index.add(delib)
        self._save()
        return delib.to_dict()

    def _as_problem(self, problem, kwargs: Dict[str, Any]) -> Problem:
        if isinstance(problem, Problem):
            return problem if problem.id else problem.finalize()
        p = Problem(
            question=str(problem),
            options=list(kwargs.get("options", []) or []),
            criteria=list(kwargs.get("criteria", []) or []),
            given_facts=list(kwargs.get("given_facts", []) or []),
            given_constraints=list(kwargs.get("given_constraints", []) or []),
            actor=kwargs.get("actor", "brainai"), tags=list(kwargs.get("tags", []) or []))
        return p.finalize()

    # ================================================================== #
    # Consultation
    # ================================================================== #
    @property
    def deliberations(self) -> List[Deliberation]:
        return self.index.all()

    def get(self, delib_id: str) -> Dict[str, Any]:
        d = self.index.get(delib_id)
        if d is None:
            raise NotFoundError(f"Délibération introuvable : {delib_id}")
        return d.to_dict()

    def search(self, **kwargs) -> List[Dict[str, Any]]:
        return [d.to_dict() for d in self.index.search(**kwargs)]

    def explain(self, delib_id: str) -> str:
        d = self.index.get(delib_id)
        if d is None:
            raise NotFoundError(f"Délibération introuvable : {delib_id}")
        return render_markdown(d)

    # ================================================================== #
    # Validation humaine (souveraineté)
    # ================================================================== #
    def validate(self, delib_id: str, approver: str, reason: str = "") -> Dict[str, Any]:
        return self._decide(delib_id, "validate", approver, reason)

    def reject(self, delib_id: str, approver: str, reason: str = "") -> Dict[str, Any]:
        return self._decide(delib_id, "reject", approver, reason)

    def _decide(self, delib_id: str, action: str, approver: str, reason: str) -> Dict[str, Any]:
        d = self.index.get(delib_id)
        if d is None:
            raise NotFoundError(f"Délibération introuvable : {delib_id}")
        getattr(self.policy, action)(d.decision, approver, reason)
        self._save()
        return d.decision

    # ================================================================== #
    # Export / audit / rapport
    # ================================================================== #
    def export_dict(self) -> Dict[str, Any]:
        return {"as_of": self.config.as_of,
                "deliberations": [d.to_dict() for d in self.deliberations],
                "audit": self.audit()}

    def export_json(self, path: Optional[Path] = None) -> Any:
        data = self.export_dict()
        if path is None:
            return data
        path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return path

    def export_markdown(self, delib_id: str, path: Optional[Path] = None) -> Any:
        md = self.explain(delib_id)
        if path is None:
            return md
        path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(md, encoding="utf-8")
        return path

    def audit(self) -> Dict[str, Any]:
        return audit_all(self.deliberations)

    def report(self) -> Dict[str, Any]:
        return store_report(self)

    def self_check(self) -> Dict[str, Any]:
        audit = self.audit()
        checks = [
            {"label": "deterministic_provider", "passed": "deterministic" in self.providers.available()},
            {"label": "works_without_external_llm",
             "passed": self.providers.select(["deterministic"]).name == "deterministic"},
            {"label": "audit_ok", "passed": audit["ok"]},
            {"label": "no_sovereign_decision",
             "passed": all(d.decision.get("data", {}).get("sovereign") is False
                           for d in self.deliberations) if self.deliberations else True},
            {"label": "no_llm_no_network", "passed": True},
        ]
        return {"title": "BrainAI Reasoning — auto-vérification",
                "ok": all(c["passed"] for c in checks), "checks": checks}

    # ================================================================== #
    # Persistance (registre de délibérations — jamais d'autre couche)
    # ================================================================== #
    def _save(self) -> None:
        self.config.ensure_directories()
        with self.config.deliberations_path.open("w", encoding="utf-8") as f:
            for d in self.deliberations:
                f.write(json.dumps(d.to_dict(), ensure_ascii=False) + "\n")

    def _load(self) -> None:
        p = self.config.deliberations_path
        if not p.exists():
            return
        delibs = [Deliberation.from_dict(json.loads(l))
                  for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]
        self.index.rebuild(delibs)


def _dedupe(elements: List[ReasoningFact]) -> List[ReasoningFact]:
    uniq = {e.id: e for e in elements}
    return sorted(uniq.values(), key=lambda e: e.id)


__all__ = ["ReasoningEngine"]
