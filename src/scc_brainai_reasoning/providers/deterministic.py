"""Raisonneur déterministe — la déduction par défaut de BrainAI Reasoning.

Aucun LLM, aucun réseau : la « pensée » du raisonnement est ici une composition de
règles pures. C'est ce fournisseur qui garantit que le raisonnement **fonctionne
toujours**, même sans aucune IA externe. Il ne suggère rien de plus que le noyau ;
il matérialise le fait que le fournisseur par défaut est autonome.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from scc_brainai_reasoning.providers.base import BaseProvider


class DeterministicReasoner(BaseProvider):
    name = "deterministic"

    def available(self) -> bool:
        return True

    # Le raisonnement déterministe est porté par le moteur lui-même (règles) :
    # le fournisseur n'ajoute pas de suggestions au-delà, il confirme sa présence.
    def suggest_hypotheses(self, question: str, facts: List[str]) -> Optional[List[str]]:
        return None

    def suggest_options(self, question: str, facts: List[str]) -> Optional[List[Dict[str, Any]]]:
        return None

    def critique(self, arbitration: Dict[str, Any]) -> Optional[str]:
        return None


__all__ = ["DeterministicReasoner"]
