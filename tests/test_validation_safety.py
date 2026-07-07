"""Tests des garde-fous : validation humaine, non-souveraineté, audit."""

from __future__ import annotations

import pytest

from scc_brainai_reasoning.core.errors import ValidationError
from scc_brainai_reasoning.providers.registry import ProviderRegistry


def test_validate_requires_human(engine, deliberation):
    with pytest.raises(ValidationError):
        engine.validate(deliberation["id"], "")


def test_validate_then_illegal_reject(engine, deliberation):
    did = deliberation["id"]
    engine.validate(did, "frederique", "pertinent")
    assert engine.get(did)["decision"]["status"] == "validated"
    assert engine.get(did)["decision"]["validation"]["approver"] == "frederique"
    with pytest.raises(ValidationError):
        engine.reject(did, "frederique")


def test_reject_flow(engine, deliberation):
    did = deliberation["id"]
    engine.reject(did, "frederique", "hors périmètre")
    assert engine.get(did)["decision"]["status"] == "rejected"


def test_audit_ok(deliberation, engine):
    a = engine.audit()
    assert a["ok"] is True


def test_audit_detects_tampering(engine, deliberation):
    did = deliberation["id"]
    d = engine.index.get(did)
    d.facts[0].statement = "TAMPERED"
    a = engine.audit()
    assert a["per_deliberation"][did]["integrity"]["ok"] is False


def test_self_check(engine, deliberation):
    sc = engine.self_check()
    assert sc["ok"] is True
    labels = {c["label"] for c in sc["checks"]}
    assert {"no_sovereign_decision", "works_without_external_llm", "no_llm_no_network"} <= labels


def test_providers_registry_fallback():
    reg = ProviderRegistry()
    assert "deterministic" in reg.available()
    for name in ("claude", "chatgpt", "gemini"):
        assert name in reg.names()
        assert name not in reg.available()
    assert reg.select(["claude", "chatgpt"]).name == "deterministic"
