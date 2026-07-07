"""Noyau de la couche de raisonnement : config, erreurs, modèle."""

from __future__ import annotations

from scc_brainai_reasoning.core.clock import canonical, digest, short_id
from scc_brainai_reasoning.core.config import ReasoningConfig, load_config
from scc_brainai_reasoning.core.errors import (
    ConfigError,
    NotFoundError,
    ProblemError,
    ReasoningError,
    SourceUnavailable,
    ValidationError,
)
from scc_brainai_reasoning.core.model import (
    Deliberation,
    DecisionStatus,
    ElementKind,
    Problem,
    ReasoningArbitration,
    ReasoningConstraint,
    ReasoningDecision,
    ReasoningElement,
    ReasoningFact,
    ReasoningHypothesis,
    ReasoningInference,
    ReasoningOption,
    ReasoningRisk,
    can_transition,
)

__all__ = [
    "canonical", "digest", "short_id",
    "ReasoningConfig", "load_config",
    "ReasoningError", "ConfigError", "SourceUnavailable", "ValidationError",
    "NotFoundError", "ProblemError",
    "ElementKind", "DecisionStatus", "can_transition",
    "ReasoningElement", "ReasoningFact", "ReasoningHypothesis", "ReasoningInference",
    "ReasoningRisk", "ReasoningConstraint", "ReasoningOption", "ReasoningArbitration",
    "ReasoningDecision", "Problem", "Deliberation",
]
