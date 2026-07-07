"""Modèle de raisonnement BrainAI.

Le raisonnement distingue explicitement cinq natures d'éléments — **faits**,
**hypothèses**, **inférences**, **risques**, **recommandations** — plus les
**contraintes**, **options**, **arbitrages** et la **décision candidate**. Tout est
tracé (sources) et déterministe (identifiants dérivés du contenu). La décision reste
**candidate** : aucune décision souveraine sans validation humaine.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, ClassVar, Dict, List

from scc_brainai_reasoning.core.clock import digest, short_id


class ElementKind(str, Enum):
    FACT = "fact"                 # établi, ancré dans une source
    HYPOTHESIS = "hypothesis"     # proposition tentative, non vérifiée
    INFERENCE = "inference"       # dérivée de faits/hypothèses par une règle
    RISK = "risk"                 # danger identifié
    CONSTRAINT = "constraint"     # limite (doctrine, gouvernance, technique)
    OPTION = "option"             # option candidate à comparer
    ARBITRATION = "arbitration"   # comparaison argumentée
    DECISION = "decision"         # décision candidate (validation humaine requise)


class DecisionStatus(str, Enum):
    CANDIDATE = "candidate"       # produite par le raisonnement ; en attente humaine
    VALIDATED = "validated"       # approuvée par un humain
    REJECTED = "rejected"         # écartée par un humain


_DECISION_TRANSITIONS = {
    "candidate": {"validated", "rejected"},
    "validated": set(),
    "rejected": set(),
}


def can_transition(current: str, target: str) -> bool:
    return target in _DECISION_TRANSITIONS.get(current, set())


@dataclass
class ReasoningElement:
    """Élément atomique de raisonnement (fait, hypothèse, risque…)."""

    statement: str = ""
    sources: List[str] = field(default_factory=list)   # traçabilité (ids/faits amont)
    confidence: float = 0.0
    tags: List[str] = field(default_factory=list)
    data: Dict[str, Any] = field(default_factory=dict)
    id: str = ""
    hash: str = ""

    KIND: ClassVar[str] = "element"

    @property
    def kind(self) -> str:
        return type(self).KIND

    def _content(self) -> Dict[str, Any]:
        return {"kind": self.kind, "statement": self.statement,
                "sources": sorted(self.sources), "data": self.data}

    def finalize(self) -> "ReasoningElement":
        self.id = short_id(self.kind, self._content())
        self.hash = digest({**self._content(), "confidence": self.confidence})
        return self

    def verify(self) -> bool:
        return self.hash == digest({**self._content(), "confidence": self.confidence})

    def to_dict(self) -> Dict[str, Any]:
        return {"id": self.id, "kind": self.kind, "statement": self.statement,
                "sources": list(self.sources), "confidence": self.confidence,
                "tags": list(self.tags), "data": dict(self.data), "hash": self.hash}

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "ReasoningElement":
        target = _KIND_CLASSES.get(d.get("kind", "element"), ReasoningElement)
        el = target(statement=str(d.get("statement", "")), sources=list(d.get("sources", []) or []),
                    confidence=float(d.get("confidence", 0.0)), tags=list(d.get("tags", []) or []),
                    data=dict(d.get("data", {}) or {}))
        el.id = str(d.get("id", "")) or el.finalize().id
        el.hash = str(d.get("hash", "")) or el.hash
        return el


@dataclass
class ReasoningFact(ReasoningElement):
    KIND: ClassVar[str] = "fact"


@dataclass
class ReasoningHypothesis(ReasoningElement):
    KIND: ClassVar[str] = "hypothesis"


@dataclass
class ReasoningInference(ReasoningElement):
    KIND: ClassVar[str] = "inference"


@dataclass
class ReasoningRisk(ReasoningElement):
    KIND: ClassVar[str] = "risk"


@dataclass
class ReasoningConstraint(ReasoningElement):
    KIND: ClassVar[str] = "constraint"


@dataclass
class ReasoningOption(ReasoningElement):
    KIND: ClassVar[str] = "option"


@dataclass
class ReasoningArbitration(ReasoningElement):
    KIND: ClassVar[str] = "arbitration"


@dataclass
class ReasoningDecision(ReasoningElement):
    KIND: ClassVar[str] = "decision"


_KIND_CLASSES = {
    "fact": ReasoningFact, "hypothesis": ReasoningHypothesis, "inference": ReasoningInference,
    "risk": ReasoningRisk, "constraint": ReasoningConstraint, "option": ReasoningOption,
    "arbitration": ReasoningArbitration, "decision": ReasoningDecision, "element": ReasoningElement,
}


# --------------------------------------------------------------------------- #
# Problème (entrée) & Délibération (sortie)
# --------------------------------------------------------------------------- #
@dataclass
class Problem:
    """Problème complexe soumis au raisonnement."""

    question: str
    options: List[Dict[str, Any]] = field(default_factory=list)   # [{name, description, data}]
    criteria: List[str] = field(default_factory=list)
    given_facts: List[str] = field(default_factory=list)
    given_constraints: List[str] = field(default_factory=list)
    actor: str = "brainai"
    tags: List[str] = field(default_factory=list)
    id: str = ""

    def finalize(self) -> "Problem":
        self.id = short_id("prob", {"question": self.question,
                                    "options": self.options, "criteria": sorted(self.criteria)})
        return self

    def to_dict(self) -> Dict[str, Any]:
        return {"id": self.id, "question": self.question, "options": list(self.options),
                "criteria": list(self.criteria), "given_facts": list(self.given_facts),
                "given_constraints": list(self.given_constraints), "actor": self.actor,
                "tags": list(self.tags)}

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "Problem":
        p = cls(question=str(d.get("question", "")), options=list(d.get("options", []) or []),
                criteria=list(d.get("criteria", []) or []),
                given_facts=list(d.get("given_facts", []) or []),
                given_constraints=list(d.get("given_constraints", []) or []),
                actor=str(d.get("actor", "brainai")), tags=list(d.get("tags", []) or []))
        p.id = str(d.get("id", "")) or p.finalize().id
        return p


@dataclass
class Deliberation:
    """Résultat structuré d'un raisonnement (traçable, révocable)."""

    problem: Problem
    as_of: str = ""
    decomposition: List[str] = field(default_factory=list)
    facts: List[ReasoningElement] = field(default_factory=list)
    constraints: List[ReasoningElement] = field(default_factory=list)
    hypotheses: List[ReasoningElement] = field(default_factory=list)
    inferences: List[ReasoningElement] = field(default_factory=list)
    options: List[ReasoningElement] = field(default_factory=list)
    risks: List[ReasoningElement] = field(default_factory=list)
    arbitration: Dict[str, Any] = field(default_factory=dict)
    decision: Dict[str, Any] = field(default_factory=dict)
    explanation: Dict[str, Any] = field(default_factory=dict)
    provider: str = "deterministic"
    id: str = ""

    def finalize(self) -> "Deliberation":
        self.id = short_id("delib", {"problem": self.problem.id,
                                     "options": [o.id for o in self.options]})
        return self

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id, "as_of": self.as_of, "provider": self.provider,
            "problem": self.problem.to_dict(),
            "decomposition": list(self.decomposition),
            "facts": [e.to_dict() for e in self.facts],
            "constraints": [e.to_dict() for e in self.constraints],
            "hypotheses": [e.to_dict() for e in self.hypotheses],
            "inferences": [e.to_dict() for e in self.inferences],
            "options": [e.to_dict() for e in self.options],
            "risks": [e.to_dict() for e in self.risks],
            "arbitration": dict(self.arbitration),
            "decision": dict(self.decision),
            "explanation": dict(self.explanation),
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "Deliberation":
        delib = cls(problem=Problem.from_dict(d.get("problem", {})),
                    as_of=str(d.get("as_of", "")), provider=str(d.get("provider", "deterministic")),
                    decomposition=list(d.get("decomposition", []) or []),
                    facts=[ReasoningElement.from_dict(x) for x in d.get("facts", [])],
                    constraints=[ReasoningElement.from_dict(x) for x in d.get("constraints", [])],
                    hypotheses=[ReasoningElement.from_dict(x) for x in d.get("hypotheses", [])],
                    inferences=[ReasoningElement.from_dict(x) for x in d.get("inferences", [])],
                    options=[ReasoningElement.from_dict(x) for x in d.get("options", [])],
                    risks=[ReasoningElement.from_dict(x) for x in d.get("risks", [])],
                    arbitration=dict(d.get("arbitration", {}) or {}),
                    decision=dict(d.get("decision", {}) or {}),
                    explanation=dict(d.get("explanation", {}) or {}))
        delib.id = str(d.get("id", "")) or delib.finalize().id
        return delib


__all__ = [
    "ElementKind", "DecisionStatus", "can_transition",
    "ReasoningElement", "ReasoningFact", "ReasoningHypothesis", "ReasoningInference",
    "ReasoningRisk", "ReasoningConstraint", "ReasoningOption", "ReasoningArbitration",
    "ReasoningDecision", "Problem", "Deliberation",
]
