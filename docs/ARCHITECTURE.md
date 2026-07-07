# Architecture de BrainAI Reasoning

## 1. Position dans SCC

Reasoning (`13`) est la couche de **délibération** de BrainAI. Elle ne conserve pas
(Memory), n'apprend pas (Learning), n'orchestre pas (Kernel) : elle **structure la
pensée** sur un problème donné.

```
   Memory (11)   Learning (12)   Kernel (10)   API (08)   Control Plane (09)
        \             \            (orchestre)    │            │
         \             \                          │ interfaces publiques (lecture)
          ────────────────────────────────────────┴────────────
   ▶ Reasoning (13) ── ReasoningEngine : analyse -> décomposition -> faits
        │              -> contraintes -> hypothèses -> options -> risques
        │              -> arbitrage -> DÉCISION CANDIDATE -> explication
   data/deliberations.jsonl (registre de délibérations — seul espace d'écriture)
```

## 2. Distinction des rôles

| Couche | Rôle |
|--------|------|
| Memory (11) | conserve l'expérience |
| Learning (12) | transforme l'expérience en apprentissages |
| Kernel (10) | orchestre agents et exécution |
| **Reasoning (13)** | **structure analyse, hypothèses, arbitrages, chaînes de décision** |

Aucune duplication : Reasoning délibère *par problème* (situationnel), là où Learning
généralise *sur l'expérience* (longitudinal) et Kernel *exécute*.

## 3. Chaîne de délibération (déterministe)

```
Problem
  │  analyze_problem() -> type   (decision / diagnostic / design / evaluation / analysis)
  ▼
decompose()                      -> sous-questions ordonnées
gather facts                     -> faits fournis + ancrés dans SCC (optionnel)
derive_constraints()             -> contraintes (données + doctrinales + ancrées)
build_options() / formulate_hypotheses()
identify_risks()                 -> risques par option
score_options() -> arbitrate()   -> arbitrage argumenté (classement)
infer()                          -> inférences
build_decision()                 -> DÉCISION CANDIDATE (jamais souveraine)
build_explanation()              -> récit typé (faits/hypothèses/inférences/risques/reco)
```

Chaque étape est **pure** : mêmes entrées ⇒ même délibération. Identifiants dérivés
du contenu.

## 4. Composants

```
core/        config (as_of, poids) · errors · clock (digest) · model (8 natures + Problem + Deliberation)
providers/   base · deterministic (défaut) · external (Claude/ChatGPT/Gemini) · registry
sources/     fact_gateway (ancrage SCC via API/Control Plane, lecture seule)
decomposition · generation · risk_analysis · arbitration · explanation
validation   HumanValidationPolicy (souveraineté humaine)
index        DeliberationIndex · audit · report
engine       ReasoningEngine (façade)
cli          scc-brain-reasoning
```

## 5. Frontière de sûreté

Le `ReasoningEngine` **ne détient aucune API d'écriture** vers une autre couche : il
lit des faits (interfaces publiques) et n'écrit que dans son registre de
délibérations. Il est donc **structurellement incapable** de modifier Memory,
Learning, Kernel, le graphe, une doctrine ou du code. La décision produite est
toujours **candidate** (voir [`GOVERNANCE_SAFETY.md`](GOVERNANCE_SAFETY.md)).

## 6. Invariants tenus

| Invariant | Comment |
|-----------|---------|
| Aucun composant modifié | ancrage via interfaces publiques seules |
| Aucune auto-modification | aucun accès en écriture hors du registre de délibérations |
| Aucune décision souveraine sans humain | décision `candidate` + `HumanValidationPolicy` |
| Fonctionne sans LLM | raisonnement déterministe par défaut ; LLM optionnel |
| Aucun réseau / dépendance externe | stdlib pur ; adaptateurs LLM non branchés |
| Déterminisme maximal | identifiants de contenu + horodatage figé + règles pures |
