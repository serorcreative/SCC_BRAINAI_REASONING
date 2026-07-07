"""Configuration de la couche de raisonnement BrainAI (JSON, sans dépendance).

Le raisonnement **structure la pensée** sur un problème donné. Il peut *ancrer* ses
faits dans les composants existants (API, Control Plane, Memory, Learning) via
leurs interfaces publiques — de façon **optionnelle et dégradable**. Il ne possède
ni ne modifie aucun d'eux, et fonctionne même sans eux.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from scc_brainai_reasoning.core.errors import ConfigError

REASONING_ROOT = Path(__file__).resolve().parents[3]      # .../13_BRAINAI_REASONING
DEFAULT_SCC_ROOT = REASONING_ROOT.parent                   # .../01_CCSC
DEFAULT_CONFIG_PATH = REASONING_ROOT / "config" / "reasoning.json"

DEFAULT_AS_OF = "2026-07-06T00:00:00+00:00"

# Pondérations d'arbitrage par défaut (déterministes, bornées).
DEFAULT_WEIGHTS = {"benefit": 0.4, "risk": 0.3, "constraint_fit": 0.2, "confidence": 0.1}


@dataclass
class ReasoningConfig:
    reasoning_root: Path = REASONING_ROOT
    scc_root: Path = DEFAULT_SCC_ROOT
    data_dir: Path = REASONING_ROOT / "data"
    as_of: str = DEFAULT_AS_OF
    ground_facts: bool = True        # ancrer les faits dans SCC si disponible
    weights: Dict[str, float] = field(default_factory=lambda: dict(DEFAULT_WEIGHTS))
    provider_order: List[str] = field(default_factory=lambda: ["deterministic"])
    extra: Dict[str, Any] = field(default_factory=dict)

    @property
    def api_src(self) -> Path:
        return self.scc_root / "08_API" / "src"

    @property
    def control_plane_src(self) -> Path:
        return self.scc_root / "09_CONTROL_PLANE" / "src"

    @property
    def learning_src(self) -> Path:
        return self.scc_root / "12_BRAINAI_LEARNING" / "src"

    @property
    def deliberations_path(self) -> Path:
        return self.data_dir / "deliberations.jsonl"

    def ensure_directories(self) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "reasoning_root": str(self.reasoning_root), "scc_root": str(self.scc_root),
            "data_dir": str(self.data_dir), "as_of": self.as_of,
            "ground_facts": self.ground_facts, "weights": dict(self.weights),
            "provider_order": list(self.provider_order),
        }


def _resolve(base: Path, value: str) -> Path:
    p = Path(value).expanduser()
    return p if p.is_absolute() else (base / p).resolve()


def load_config(path: Optional[Path] = None) -> ReasoningConfig:
    config = ReasoningConfig()
    target = Path(path) if path else DEFAULT_CONFIG_PATH
    if not target.exists():
        if path is not None:
            raise ConfigError(f"Configuration introuvable : {target}")
        return config
    try:
        raw = json.loads(target.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ConfigError(f"Configuration illisible ({target}) : {exc}") from exc

    base = config.reasoning_root
    if "scc_root" in raw:
        config.scc_root = _resolve(base, raw["scc_root"])
    paths = raw.get("paths", {})
    if "data_dir" in paths:
        config.data_dir = _resolve(base, paths["data_dir"])
    config.as_of = str(raw.get("as_of", DEFAULT_AS_OF))
    config.ground_facts = bool(raw.get("ground_facts", True))
    if "weights" in raw:
        config.weights = {**DEFAULT_WEIGHTS, **dict(raw["weights"])}
    config.provider_order = list(raw.get("provider_order", config.provider_order))
    config.extra = dict(raw.get("extra", {}))
    return config


__all__ = ["REASONING_ROOT", "DEFAULT_SCC_ROOT", "DEFAULT_AS_OF", "DEFAULT_WEIGHTS",
           "ReasoningConfig", "load_config"]
