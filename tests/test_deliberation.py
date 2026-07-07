"""Tests du processus de délibération complet."""

from __future__ import annotations

import pytest

from scc_brainai_reasoning.core.errors import ProblemError


def test_deliberation_structure(deliberation):
    d = deliberation
    for key in ("decomposition", "facts", "constraints", "hypotheses", "inferences",
                "options", "risks", "arbitration", "decision", "explanation"):
        assert key in d, f"section manquante : {key}"
    assert len(d["decomposition"]) >= 4
    assert len(d["options"]) == 2
    assert d["facts"]  # les faits fournis sont présents


def test_distinguishes_element_natures(deliberation):
    d = deliberation
    assert all(f["kind"] == "fact" for f in d["facts"])
    assert all(h["kind"] == "hypothesis" for h in d["hypotheses"])
    assert all(i["kind"] == "inference" for i in d["inferences"])
    assert all(r["kind"] == "risk" for r in d["risks"])
    assert all(c["kind"] == "constraint" for c in d["constraints"])


def test_arbitration_ranks_options(deliberation):
    arb = deliberation["arbitration"]
    ranking = arb["ranking"]
    assert len(ranking) == 2
    # le classement est trié par score décroissant
    assert ranking[0]["total"] >= ranking[1]["total"]
    assert arb["top"] == ranking[0]["option"]


def test_candidate_decision_never_sovereign(deliberation):
    dec = deliberation["decision"]
    assert dec["status"] == "candidate"
    assert dec["data"]["sovereign"] is False
    assert dec["data"]["requires_human_validation"] is True


def test_default_constraints_present(deliberation):
    texts = " ".join(c["statement"] for c in deliberation["constraints"])
    assert "ADR" in texts               # SCC-DOC-0009
    assert "validation humaine" in texts  # garde-fou T3
    assert "jamais appliquée" in texts    # sûreté du raisonnement


def test_risk_identified_for_options(deliberation):
    assert deliberation["risks"]  # au moins un risque identifié


def test_traceability_every_element_has_source(deliberation):
    d = deliberation
    for group in ("facts", "constraints", "hypotheses", "inferences", "options", "risks"):
        for el in d[group]:
            assert el["sources"], f"élément sans source dans {group}: {el['id']}"


def test_empty_question_rejected(engine):
    with pytest.raises(ProblemError):
        engine.reason("   ")


def test_problem_type_without_options(engine):
    # un problème sans options fournies dérive des options canoniques
    d = engine.reason("Pourquoi le taux d'erreur augmente-t-il ?", given_facts=["Erreurs récentes."])
    assert len(d["options"]) >= 2
    assert d["decision"]["status"] == "candidate"
