"""CLI de la couche de raisonnement BrainAI (``scc-brain-reasoning``).

Raisonner sur un problème, expliquer, **valider humainement** une décision
candidate, exporter, auditer. Sortie JSON déterministe. Aucune commande n'applique
une décision : seule la validation humaine change son statut.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from scc_brainai_reasoning import __version__
from scc_brainai_reasoning.core.config import load_config
from scc_brainai_reasoning.core.errors import ReasoningError
from scc_brainai_reasoning.engine import ReasoningEngine


def _out(obj: Any) -> None:
    print(json.dumps(obj, ensure_ascii=False, indent=2))


def _engine(args) -> ReasoningEngine:
    return ReasoningEngine(config=load_config(args.config))


def _parse_options(raw: Optional[List[str]]) -> List[Dict[str, Any]]:
    options = []
    for item in raw or []:
        parts = item.split("|")
        opt: Dict[str, Any] = {"name": parts[0].strip()}
        if len(parts) > 1:
            opt["description"] = parts[1].strip()
        if len(parts) > 2:
            try:
                opt["benefit"] = float(parts[2])
            except ValueError:
                pass
        options.append(opt)
    return options


def cmd_reason(args) -> int:
    eng = _engine(args)
    order = args.provider_order.split(",") if args.provider_order else None
    try:
        d = eng.reason(args.question, options=_parse_options(args.option),
                       given_facts=args.fact or [], given_constraints=args.constraint or [],
                       provider_order=order)
    except ReasoningError as exc:
        _out({"error": str(exc)}); return 1
    _out(d)
    return 0


def cmd_get(args) -> int:
    try:
        _out(_engine(args).get(args.id)); return 0
    except ReasoningError as exc:
        _out({"error": str(exc)}); return 1


def cmd_explain(args) -> int:
    try:
        print(_engine(args).explain(args.id)); return 0
    except ReasoningError as exc:
        _out({"error": str(exc)}); return 1


def cmd_search(args) -> int:
    _out(_engine(args).search(status=args.status, text=args.text, limit=int(args.limit))); return 0


def _transition(args, action: str) -> int:
    try:
        _out(getattr(_engine(args), action)(args.id, args.by, args.reason)); return 0
    except ReasoningError as exc:
        _out({"error": str(exc)}); return 1


def cmd_report(args) -> int:
    _out(_engine(args).report()); return 0


def cmd_audit(args) -> int:
    a = _engine(args).audit(); _out(a); return 0 if a["ok"] else 1


def cmd_self_check(args) -> int:
    sc = _engine(args).self_check(); _out(sc); return 0 if sc["ok"] else 1


def cmd_providers(args) -> int:
    _out(_engine(args).providers.to_dict()); return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="scc-brain-reasoning",
                                     description="Couche de raisonnement de BrainAI (décisions candidates).")
    parser.add_argument("--version", action="version", version=f"scc-brain-reasoning {__version__}")
    parser.add_argument("--config", type=Path, default=None)
    sub = parser.add_subparsers(dest="command", required=True)

    p_r = sub.add_parser("reason", help="Raisonner sur un problème.")
    p_r.add_argument("question")
    p_r.add_argument("--option", action="append", help="'nom|description|benefice' (répétable)")
    p_r.add_argument("--fact", action="append", help="fait établi (répétable)")
    p_r.add_argument("--constraint", action="append", help="contrainte (répétable)")
    p_r.add_argument("--provider-order", default=None)
    p_r.set_defaults(func=cmd_reason)

    p_get = sub.add_parser("get", help="Détail d'une délibération.")
    p_get.add_argument("id"); p_get.set_defaults(func=cmd_get)

    p_ex = sub.add_parser("explain", help="Explication lisible (Markdown).")
    p_ex.add_argument("id"); p_ex.set_defaults(func=cmd_explain)

    p_s = sub.add_parser("search", help="Recherche de délibérations.")
    p_s.add_argument("--status", default=None); p_s.add_argument("--text", default=None)
    p_s.add_argument("--limit", default="50"); p_s.set_defaults(func=cmd_search)

    for action in ("validate", "reject"):
        p = sub.add_parser(action, help=f"{action} (validation humaine) une décision candidate.")
        p.add_argument("id"); p.add_argument("--by", required=True); p.add_argument("--reason", default="")
        p.set_defaults(func=lambda a, _act=action: _transition(a, _act))

    sub.add_parser("report", help="Rapport du registre de raisonnement.").set_defaults(func=cmd_report)
    sub.add_parser("audit", help="Audit (intégrité, traçabilité, sûreté).").set_defaults(func=cmd_audit)
    sub.add_parser("self-check", help="Auto-vérification.").set_defaults(func=cmd_self_check)
    sub.add_parser("providers", help="Fournisseurs de raisonnement.").set_defaults(func=cmd_providers)
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


__all__ = ["main", "build_parser"]
