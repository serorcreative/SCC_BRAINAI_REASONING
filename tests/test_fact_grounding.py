"""Test d'intégration : ancrage des faits dans SCC via l'API (réutilisation).

Vérifie que le raisonnement peut ancrer ses faits dans l'état réel de SCC via les
interfaces publiques (API / Control Plane), sans modifier ces composants. Ignoré
proprement si l'API n'est pas localisable.
"""

from __future__ import annotations

import pytest

from scc_brainai_reasoning.core.config import ReasoningConfig
from scc_brainai_reasoning.engine import ReasoningEngine
from scc_brainai_reasoning.sources.fact_gateway import FactGateway


def _api_available() -> bool:
    return FactGateway(ReasoningConfig()).available().get("api", False)


pytestmark = pytest.mark.skipif(not _api_available(),
                                reason="API SCC non localisable depuis ce module.")


def test_grounding_adds_scc_facts(tmp_path):
    eng = ReasoningEngine(config=ReasoningConfig(data_dir=tmp_path / "d", ground_facts=True))
    d = eng.reason("Faut-il matérialiser la doctrine de traçabilité dans le graphe ?",
                   options=[{"name": "Oui", "benefit": 0.7}, {"name": "Non", "benefit": 0.3}])
    sources = {s for f in d["facts"] for s in f["sources"]}
    # au moins un fait ancré dans SCC (graphe / readiness / santé)
    assert any(s.startswith("api:") or s.startswith("control_plane:") for s in sources)
    # des contraintes doctrinales ont pu être dérivées du graphe
    assert d["decision"]["status"] == "candidate"
    assert eng.audit()["ok"] is True
