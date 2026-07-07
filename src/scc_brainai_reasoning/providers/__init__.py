"""Fournisseurs de raisonnement : déterministe (défaut) + emplacements LLM."""

from __future__ import annotations

from scc_brainai_reasoning.providers.base import BaseProvider, ReasoningProvider
from scc_brainai_reasoning.providers.deterministic import DeterministicReasoner
from scc_brainai_reasoning.providers.external import (
    ChatGPTReasoner,
    ClaudeReasoner,
    ExternalReasoner,
    GeminiReasoner,
)
from scc_brainai_reasoning.providers.registry import ProviderRegistry

__all__ = [
    "ReasoningProvider", "BaseProvider", "DeterministicReasoner",
    "ExternalReasoner", "ClaudeReasoner", "ChatGPTReasoner", "GeminiReasoner",
    "ProviderRegistry",
]
