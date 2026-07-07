"""Contrat des fournisseurs de raisonnement — point d'extension pour un futur LLM.

Le raisonnement **ne dépend d'aucun LLM** : sa déduction par défaut est
déterministe (règles). Un LLM (plus tard) pourra *enrichir* le raisonnement —
suggérer des hypothèses, des options, critiquer un arbitrage — **sans jamais** en
devenir un prérequis ni prendre de décision.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Protocol, runtime_checkable


@runtime_checkable
class ReasoningProvider(Protocol):
    name: str

    def available(self) -> bool: ...

    def suggest_hypotheses(self, question: str, facts: List[str]) -> Optional[List[str]]: ...

    def suggest_options(self, question: str, facts: List[str]) -> Optional[List[Dict[str, Any]]]: ...

    def critique(self, arbitration: Dict[str, Any]) -> Optional[str]: ...


class BaseProvider:
    """Base : indisponible par défaut, hooks inertes (aucun effet)."""

    name = "base"

    def available(self) -> bool:
        return False

    def suggest_hypotheses(self, question: str, facts: List[str]) -> Optional[List[str]]:
        return None

    def suggest_options(self, question: str, facts: List[str]) -> Optional[List[Dict[str, Any]]]:
        return None

    def critique(self, arbitration: Dict[str, Any]) -> Optional[str]:
        return None


__all__ = ["ReasoningProvider", "BaseProvider"]
