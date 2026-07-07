"""Passerelle de faits — ancre le raisonnement dans SCC (interfaces publiques).

Réutilise, **sans les modifier**, l'API (08), le Control Plane (09) et le Learning
(12) via leurs interfaces publiques pour transformer l'état réel de SCC en **faits**
et **contraintes** tracés. L'ancrage est **optionnel et dégradable** : si une source
est absente, le raisonnement continue sur les faits fournis par l'appelant.
"""

from __future__ import annotations

import importlib
import re
import sys
from typing import Any, Dict, List, Tuple

from scc_brainai_reasoning.core.config import ReasoningConfig
from scc_brainai_reasoning.core.model import ReasoningConstraint, ReasoningFact

_STOPWORDS = {
    "le", "la", "les", "un", "une", "des", "de", "du", "et", "ou", "à", "au", "aux",
    "que", "qui", "quoi", "est", "pour", "dans", "sur", "avec", "faut", "il", "on",
    "quel", "quelle", "quels", "quelles", "comment", "pourquoi", "doit", "peut",
    "the", "a", "an", "of", "to", "is", "should", "we", "how", "why", "what",
}


def _keywords(question: str, limit: int = 6) -> List[str]:
    toks = re.findall(r"[a-zàâäéèêëîïôöùûüç0-9\-]{3,}", question.lower())
    seen: List[str] = []
    for t in toks:
        if t not in _STOPWORDS and t not in seen:
            seen.append(t)
    return sorted(seen)[:limit]


class FactGateway:
    def __init__(self, config: ReasoningConfig):
        self._config = config
        self._api = None
        self._cp = None
        self._learn = None

    def _add_path(self, path) -> bool:
        if not path.exists():
            return False
        if str(path) not in sys.path:
            sys.path.insert(0, str(path))
        return True

    def _api_obj(self):
        if self._api is None and self._add_path(self._config.api_src):
            try:
                self._api = importlib.import_module("scc_api").SccApi()
            except ImportError:  # pragma: no cover
                self._api = None
        return self._api

    def _cp_obj(self):
        if self._cp is None and self._add_path(self._config.control_plane_src):
            try:
                self._cp = importlib.import_module("scc_control_plane").ControlPlane()
            except ImportError:  # pragma: no cover
                self._cp = None
        return self._cp

    def available(self) -> Dict[str, bool]:
        return {"api": self._api_obj() is not None, "control_plane": self._cp_obj() is not None}

    # -- ancrage --------------------------------------------------------- #
    def ground(self, question: str) -> Tuple[List[ReasoningFact], List[ReasoningConstraint], List[str]]:
        facts: List[ReasoningFact] = []
        constraints: List[ReasoningConstraint] = []
        notes: List[str] = []
        kws = _keywords(question)

        api = self._api_obj()
        if api is not None:
            self._ground_api(api, kws, facts, constraints, notes)
        else:
            notes.append("API indisponible : ancrage graphe/readiness ignoré.")

        cp = self._cp_obj()
        if cp is not None:
            try:
                health = cp.health()
                facts.append(ReasoningFact(
                    statement=f"Santé consolidée du système : « {health.get('overall')} ».",
                    sources=["control_plane:health"], confidence=0.9,
                    tags=["fact", "health"], data={"overall": health.get("overall")}).finalize())
            except Exception as exc:  # noqa: BLE001
                notes.append(f"Control Plane indisponible : {exc}")
        else:
            notes.append("Control Plane indisponible : ancrage santé ignoré.")

        return facts, constraints, notes

    def _ground_api(self, api, kws, facts, constraints, notes) -> None:
        try:
            readiness = api.dispatch("system.readiness").to_dict().get("data", {})
            facts.append(ReasoningFact(
                statement=f"Préparation du système : « {readiness.get('verdict')} ».",
                sources=["api:system.readiness"], confidence=0.9,
                tags=["fact", "readiness"], data={"verdict": readiness.get("verdict")}).finalize())
        except Exception as exc:  # noqa: BLE001
            notes.append(f"readiness indisponible : {exc}")

        try:
            summ = api.dispatch("graph.summary").to_dict().get("data", {})
            counts = summ.get("counts", {})
            facts.append(ReasoningFact(
                statement=f"Le graphe SCC compte {counts.get('nodes')} nœuds et {counts.get('edges')} relations.",
                sources=["api:graph.summary"], confidence=0.95,
                tags=["fact", "graph"], data={"counts": counts}).finalize())
        except Exception as exc:  # noqa: BLE001
            notes.append(f"graph.summary indisponible : {exc}")

        # Doctrines pertinentes -> contraintes (les doctrines gouvernent).
        seen = set()
        for kw in kws:
            try:
                nodes = api.dispatch("graph.search", {"type": "Doctrine", "query": kw, "limit": 3}).to_dict().get("data", [])
            except Exception:  # noqa: BLE001
                nodes = []
            for n in nodes:
                if n["id"] in seen:
                    continue
                seen.add(n["id"])
                constraints.append(ReasoningConstraint(
                    statement=f"Respecter la doctrine {n['id']} — {n.get('label', '')}.",
                    sources=[f"api:graph.node:{n['id']}"], confidence=0.85,
                    tags=["constraint", "doctrine"], data={"doctrine": n["id"]}).finalize())
        if not seen:
            notes.append("Aucune doctrine directement pertinente trouvée par mots-clés.")


__all__ = ["FactGateway"]
