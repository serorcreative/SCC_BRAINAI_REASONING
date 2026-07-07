# SCC BrainAI Reasoning

**Couche officielle de raisonnement de BrainAI.**

Reasoning **structure la pensée**. Il n'est ni Memory (l'expérience), ni Learning
(les apprentissages), ni Kernel (l'orchestration) :

- **Memory** conserve l'expérience.
- **Learning** transforme l'expérience en apprentissages.
- **Kernel** orchestre.
- **Reasoning** structure l'**analyse**, les **hypothèses**, les **arbitrages** et
  les **chaînes de décision**.

> Sur un problème complexe, Reasoning produit une **délibération** : décomposition,
> faits, contraintes, hypothèses, options comparées, risques, **arbitrage argumenté**,
> explication, et une **décision candidate**. Il distingue explicitement **faits /
> hypothèses / inférences / risques / recommandations**.

> **Garde-fous : aucune auto-modification ; aucune décision souveraine sans
> validation humaine** (la décision reste *candidate*). **Fonctionne sans aucune
> IA** (raisonnement déterministe ; LLM optionnel et branchable). Stdlib pur, sans
> réseau, déterministe.

## Réutilisation, jamais duplication

Reasoning **ancre** ses faits dans SCC via les **interfaces publiques** existantes,
sans les modifier : API (08) pour le graphe / doctrines / readiness, Control Plane
(09) pour la santé. L'ancrage est **optionnel et dégradable** : le raisonnement
fonctionne même sans ces composants, sur les faits fournis.

## Installation

```bash
cd 13_BRAINAI_REASONING
python -m pip install -e .        # expose la commande `scc-brain-reasoning`
```

Aucune dépendance externe.

## Utilisation (CLI)

```bash
scc-brain-reasoning reason "Faut-il construire l'API maintenant ou différer ?" \
    --option "Construire maintenant|livrer tout de suite|0.7" \
    --option "Différer|attendre le prochain cycle|0.4" \
    --fact "Le Runtime est livré et testé." \
    --constraint "Respecter le découplage par contrats."
scc-brain-reasoning explain <id>        # explication lisible (Markdown)
scc-brain-reasoning validate <id> --by frederique --reason "pertinent"   # validation HUMAINE
scc-brain-reasoning reject   <id> --by frederique
scc-brain-reasoning search --status candidate
scc-brain-reasoning report | audit | self-check | providers
```

## Utilisation (Python)

```python
from scc_brainai_reasoning import ReasoningEngine

engine = ReasoningEngine()
d = engine.reason("Faut-il agir ou différer ?",
                  options=[{"name": "Agir", "benefit": 0.6}, {"name": "Différer", "benefit": 0.5}],
                  given_facts=["Contexte stable."])
print(d["arbitration"]["argument"])          # arbitrage argumenté
engine.validate(d["id"], approver="frederique", reason="pertinent")   # humain requis
```

## Composants

`ReasoningEngine` · `Problem` · `Deliberation` · `ReasoningFact` ·
`ReasoningHypothesis` · `ReasoningInference` · `ReasoningRisk` ·
`ReasoningConstraint` · `ReasoningOption` · `ReasoningArbitration` ·
`ReasoningDecision` · `HumanValidationPolicy` · `ProviderRegistry` (LLM optionnel).

Détails : [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) ·
[`docs/REASONING_MODEL.md`](docs/REASONING_MODEL.md) ·
[`docs/DELIBERATION_PROCESS.md`](docs/DELIBERATION_PROCESS.md) ·
[`docs/GOVERNANCE_SAFETY.md`](docs/GOVERNANCE_SAFETY.md).

## Tests

```bash
python -m pytest -q      # 22 tests (déterministes ; 1 intégration d'ancrage réel)
```
