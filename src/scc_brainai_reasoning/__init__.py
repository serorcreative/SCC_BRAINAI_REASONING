"""SCC BrainAI Reasoning — couche officielle de raisonnement de BrainAI.

Structure la **pensée** : analyse d'une demande complexe, décomposition, hypothèses,
comparaison d'options, risques, contraintes, **arbitrage argumenté**, explication et
**décision candidate**. Distingue explicitement faits / hypothèses / inférences /
risques / recommandations.

Reasoning n'est ni Memory (expérience), ni Learning (apprentissages), ni Kernel
(orchestration). Il **réutilise** leurs interfaces publiques pour ancrer ses faits,
sans jamais les modifier.

Garde-fous : aucune auto-modification ; **aucune décision souveraine sans validation
humaine** (la décision reste candidate). Fonctionne **sans aucune IA** (raisonnement
déterministe ; LLM optionnel et branchable). Stdlib pur, sans réseau, déterministe.
"""

from __future__ import annotations

__version__ = "1.0.0"

from scc_brainai_reasoning.core.config import ReasoningConfig, load_config
from scc_brainai_reasoning.core.model import (
    Deliberation,
    Problem,
    ReasoningArbitration,
    ReasoningConstraint,
    ReasoningDecision,
    ReasoningFact,
    ReasoningHypothesis,
    ReasoningInference,
    ReasoningOption,
    ReasoningRisk,
)
from scc_brainai_reasoning.engine import ReasoningEngine
from scc_brainai_reasoning.providers.registry import ProviderRegistry
from scc_brainai_reasoning.validation import HumanValidationPolicy

__all__ = [
    "__version__",
    "ReasoningEngine",
    "ReasoningConfig",
    "load_config",
    "Problem",
    "Deliberation",
    "ReasoningFact",
    "ReasoningHypothesis",
    "ReasoningInference",
    "ReasoningRisk",
    "ReasoningConstraint",
    "ReasoningOption",
    "ReasoningArbitration",
    "ReasoningDecision",
    "ProviderRegistry",
    "HumanValidationPolicy",
]
