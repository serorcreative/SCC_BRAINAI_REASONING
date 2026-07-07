"""Index des délibérations (recherche déterministe)."""

from __future__ import annotations

from typing import Dict, List, Optional

from scc_brainai_reasoning.core.clock import canonical
from scc_brainai_reasoning.core.model import Deliberation


class DeliberationIndex:
    def __init__(self) -> None:
        self._by_id: Dict[str, Deliberation] = {}
        self._text: Dict[str, str] = {}

    def add(self, delib: Deliberation) -> None:
        self._by_id[delib.id] = delib
        blob = f"{delib.problem.question} {canonical(delib.decision)} {' '.join(delib.decomposition)}"
        self._text[delib.id] = blob.lower()

    def rebuild(self, delibs: List[Deliberation]) -> None:
        self._by_id.clear()
        self._text.clear()
        for d in delibs:
            self.add(d)

    def get(self, delib_id: str) -> Optional[Deliberation]:
        return self._by_id.get(delib_id)

    def search(self, *, status: Optional[str] = None, text: Optional[str] = None,
               limit: int = 50) -> List[Deliberation]:
        q = (text or "").strip().lower()
        out: List[Deliberation] = []
        for did in sorted(self._by_id):
            d = self._by_id[did]
            if status and d.decision.get("status") != status:
                continue
            if q and q not in self._text.get(did, ""):
                continue
            out.append(d)
        return out[:limit] if limit and limit > 0 else out

    def all(self) -> List[Deliberation]:
        return [self._by_id[k] for k in sorted(self._by_id)]

    def __len__(self) -> int:
        return len(self._by_id)


__all__ = ["DeliberationIndex"]
