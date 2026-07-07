"""Rapports de raisonnement — résumé d'une délibération et du registre."""

from __future__ import annotations

from typing import Any, Dict, List

from scc_brainai_reasoning.core.model import Deliberation


def deliberation_summary(delib: Deliberation) -> Dict[str, Any]:
    return {
        "id": delib.id, "question": delib.problem.question,
        "counts": {"facts": len(delib.facts), "constraints": len(delib.constraints),
                   "hypotheses": len(delib.hypotheses), "inferences": len(delib.inferences),
                   "options": len(delib.options), "risks": len(delib.risks)},
        "decision": {"statement": delib.decision.get("statement"),
                     "status": delib.decision.get("status"),
                     "option": delib.decision.get("data", {}).get("option")},
    }


def store_report(engine) -> Dict[str, Any]:
    delibs = engine.deliberations
    by_status: Dict[str, int] = {}
    for d in delibs:
        s = d.decision.get("status", "candidate")
        by_status[s] = by_status.get(s, 0) + 1
    audit = engine.audit()
    return {
        "as_of": engine.config.as_of,
        "total_deliberations": len(delibs),
        "by_decision_status": dict(sorted(by_status.items())),
        "audit_ok": audit["ok"],
        "deliberations": [deliberation_summary(d) for d in delibs],
        "safety_note": "Toute décision est candidate ; aucune validation souveraine sans humain.",
    }


def render_markdown(delib: Deliberation) -> str:
    ex = delib.explanation
    lines: List[str] = [
        f"# Raisonnement — {delib.id}",
        "",
        f"> `as_of` : {delib.as_of} · fournisseur : {delib.provider}",
        "",
        f"**Question** : {delib.problem.question}",
        "",
        "## Décomposition", "",
    ]
    for s in delib.decomposition:
        lines.append(f"1. {s}")
    lines += ["", "## Faits", ""]
    for f in delib.facts:
        lines.append(f"- {f.statement}  _(sources : {', '.join(f.sources)})_")
    lines += ["", "## Contraintes", ""]
    for c in delib.constraints:
        lines.append(f"- {c.statement}")
    lines += ["", "## Hypothèses", ""]
    for h in delib.hypotheses:
        lines.append(f"- {h.statement}")
    lines += ["", "## Options & risques", ""]
    ranking = delib.arbitration.get("ranking", [])
    for r in ranking:
        lines.append(f"- **{r['option']}** — score {r['total']} "
                     f"(bénéfice {r['scores']['benefit']}, risque {r['scores']['risk']})")
    lines += ["", "## Risques identifiés", ""]
    for rk in delib.risks:
        lines.append(f"- {rk.statement}")
    lines += ["", "## Arbitrage", "", delib.arbitration.get("argument", ""), ""]
    lines += ["## Inférences", ""]
    for inf in delib.inferences:
        lines.append(f"- {inf.statement}")
    lines += ["", "## Décision candidate", "",
              f"- {delib.decision.get('statement')}",
              f"- statut : **{delib.decision.get('status')}**",
              "",
              "> Décision **candidate** : validation humaine explicite requise ; "
              "jamais appliquée automatiquement.",
              "",
              "*Raisonnement déterministe BrainAI — sans réseau ni LLM obligatoire.*"]
    return "\n".join(lines) + "\n"


__all__ = ["deliberation_summary", "store_report", "render_markdown"]
