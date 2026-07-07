"""Hiérarchie d'exceptions de la couche de raisonnement BrainAI."""

from __future__ import annotations


class ReasoningError(Exception):
    """Erreur de base de la couche de raisonnement."""


class ConfigError(ReasoningError):
    """Configuration absente, illisible ou invalide."""


class SourceUnavailable(ReasoningError):
    """Une source de faits (API, Control Plane, Memory, Learning) est indisponible."""


class ValidationError(ReasoningError):
    """Transition de validation humaine interdite."""


class NotFoundError(ReasoningError):
    """Délibération ou élément de raisonnement introuvable."""


class ProblemError(ReasoningError):
    """Problème mal formé (question manquante, options invalides)."""


__all__ = [
    "ReasoningError", "ConfigError", "SourceUnavailable",
    "ValidationError", "NotFoundError", "ProblemError",
]
