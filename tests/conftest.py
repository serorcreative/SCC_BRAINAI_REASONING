"""Fixtures des tests de raisonnement (isolées, déterministes, hermétiques).

L'ancrage des faits dans SCC (``ground_facts``) est désactivé par défaut pour des
tests rapides et hermétiques ; un test dédié vérifie l'ancrage réel via l'API.
"""

from __future__ import annotations

import pytest

from scc_brainai_reasoning.core.config import ReasoningConfig
from scc_brainai_reasoning.engine import ReasoningEngine


@pytest.fixture
def config(tmp_path):
    return ReasoningConfig(data_dir=tmp_path / "data", ground_facts=False)


@pytest.fixture
def engine(config):
    return ReasoningEngine(config=config)


@pytest.fixture
def deliberation(engine):
    return engine.reason(
        "Faut-il construire l'API maintenant ou différer ?",
        options=[{"name": "Construire maintenant", "description": "livrer tout de suite", "benefit": 0.7},
                 {"name": "Différer", "description": "attendre le prochain cycle", "benefit": 0.4}],
        given_facts=["Le Runtime est livré et testé.", "Le Control Plane est opérationnel."],
        given_constraints=["Respecter le découplage par contrats."])
