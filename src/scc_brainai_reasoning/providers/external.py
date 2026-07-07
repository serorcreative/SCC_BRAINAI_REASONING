"""Adaptateurs LLM externes — emplacements d'extension (non branchés en V1).

Ces classes matérialisent la **place** d'un LLM (Claude, ChatGPT, Gemini…) dans le
raisonnement. Elles ne réalisent **aucun appel réseau** et se déclarent
**indisponibles** tant qu'un transport n'est pas fourni. Le moteur les ignore alors
et raisonne de façon déterministe. Brancher un LLM (plus tard, sous ADR) = fournir
un ``client`` ; l'architecture du raisonnement ne change pas.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from scc_brainai_reasoning.providers.base import BaseProvider


class ExternalReasoner(BaseProvider):
    name = "external"

    def __init__(self, client: Optional[Any] = None):
        self._client = client

    def available(self) -> bool:
        return self._client is not None

    def _guard(self):
        raise NotImplementedError(
            f"Fournisseur '{self.name}' : transport non implémenté dans le socle (aucun réseau).")

    def suggest_hypotheses(self, question: str, facts: List[str]) -> Optional[List[str]]:
        if not self.available():
            return None
        self._guard()

    def suggest_options(self, question: str, facts: List[str]) -> Optional[List[Dict[str, Any]]]:
        if not self.available():
            return None
        self._guard()

    def critique(self, arbitration: Dict[str, Any]) -> Optional[str]:
        if not self.available():
            return None
        self._guard()


class ClaudeReasoner(ExternalReasoner):
    name = "claude"


class ChatGPTReasoner(ExternalReasoner):
    name = "chatgpt"


class GeminiReasoner(ExternalReasoner):
    name = "gemini"


KNOWN_EXTERNAL = {"claude": ClaudeReasoner, "chatgpt": ChatGPTReasoner, "gemini": GeminiReasoner}

__all__ = ["ExternalReasoner", "ClaudeReasoner", "ChatGPTReasoner", "GeminiReasoner", "KNOWN_EXTERNAL"]
