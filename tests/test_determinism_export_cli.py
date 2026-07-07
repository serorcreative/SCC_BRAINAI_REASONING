"""Tests de déterminisme, export, explication et CLI."""

from __future__ import annotations

import json

import pytest

from scc_brainai_reasoning.cli import main
from scc_brainai_reasoning.core.config import ReasoningConfig
from scc_brainai_reasoning.engine import ReasoningEngine


def _reason(data_dir):
    eng = ReasoningEngine(config=ReasoningConfig(data_dir=data_dir, ground_facts=False))
    return eng.reason("Faut-il agir ou différer ?",
                      options=[{"name": "Agir", "benefit": 0.6}, {"name": "Différer", "benefit": 0.5}],
                      given_facts=["Contexte stable."])


def test_deterministic_reasoning(tmp_path):
    a = _reason(tmp_path / "a")
    b = _reason(tmp_path / "b")
    assert json.dumps(a, sort_keys=True, ensure_ascii=False) == \
           json.dumps(b, sort_keys=True, ensure_ascii=False)


def test_explain_markdown(engine, deliberation):
    md = engine.explain(deliberation["id"])
    for section in ("## Faits", "## Contraintes", "## Arbitrage", "## Décision candidate"):
        assert section in md
    assert "validation humaine" in md


def test_export_and_report(engine, deliberation, tmp_path):
    data = engine.export_dict()
    assert data["deliberations"]
    jp = engine.export_json(tmp_path / "r.json")
    assert jp.exists()
    report = engine.report()
    assert report["total_deliberations"] == 1
    assert report["by_decision_status"].get("candidate") == 1


def test_persistence_roundtrip(config):
    e1 = ReasoningEngine(config=config)
    d = e1.reason("Faut-il agir ?", given_facts=["x"])
    e2 = ReasoningEngine(config=config)   # relit depuis le disque
    assert e2.get(d["id"])["id"] == d["id"]
    assert e2.audit()["ok"] is True


def test_cli_reason_and_validate(tmp_path, capsys):
    cfg = tmp_path / "reasoning.json"
    cfg.write_text(json.dumps({"paths": {"data_dir": str(tmp_path / "d")},
                               "as_of": "2026-07-06T00:00:00+00:00",
                               "ground_facts": False}), encoding="utf-8")
    rc = main(["--config", str(cfg), "reason", "Faut-il agir ou différer ?",
               "--option", "Agir|agir vite|0.6", "--option", "Différer|attendre|0.5",
               "--fact", "Contexte stable."])
    out = json.loads(capsys.readouterr().out)
    assert rc == 0
    did = out["id"]
    assert out["decision"]["status"] == "candidate"
    rc = main(["--config", str(cfg), "validate", did, "--by", "frederique", "--reason", "ok"])
    out = json.loads(capsys.readouterr().out)
    assert rc == 0
    assert out["status"] == "validated"
