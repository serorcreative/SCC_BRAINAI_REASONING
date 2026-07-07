"""Registre des fournisseurs de raisonnement — repli déterministe garanti."""

from __future__ import annotations

from typing import Dict, List, Optional

from scc_brainai_reasoning.providers.base import BaseProvider
from scc_brainai_reasoning.providers.deterministic import DeterministicReasoner
from scc_brainai_reasoning.providers.external import KNOWN_EXTERNAL


class ProviderRegistry:
    def __init__(self) -> None:
        self._providers: Dict[str, BaseProvider] = {}
        self.register(DeterministicReasoner())
        for name, cls in KNOWN_EXTERNAL.items():
            self.register(cls())

    def register(self, provider: BaseProvider) -> BaseProvider:
        self._providers[provider.name] = provider
        return provider

    def names(self) -> List[str]:
        return sorted(self._providers)

    def available(self) -> List[str]:
        return sorted(n for n, p in self._providers.items() if p.available())

    def select(self, order: Optional[List[str]] = None) -> BaseProvider:
        for name in (order or []):
            p = self._providers.get(name)
            if p is not None and p.available():
                return p
        return self._providers["deterministic"]     # repli garanti

    def to_dict(self) -> Dict[str, object]:
        return {"registered": self.names(), "available": self.available(),
                "external_slots": sorted(KNOWN_EXTERNAL)}


__all__ = ["ProviderRegistry"]
