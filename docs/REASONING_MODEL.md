# Modèle de raisonnement

## 1. Les natures d'éléments (pensée typée)

Reasoning **distingue explicitement** la nature de chaque élément — condition d'un
raisonnement honnête et vérifiable.

| Élément | `kind` | Sens |
|---------|--------|------|
| **ReasoningFact** | `fact` | établi, ancré dans une source |
| **ReasoningHypothesis** | `hypothesis` | proposition tentative, non vérifiée |
| **ReasoningInference** | `inference` | dérivée de faits/hypothèses par une règle |
| **ReasoningRisk** | `risk` | danger identifié (par option) |
| **ReasoningConstraint** | `constraint` | limite (doctrine, gouvernance, technique) |
| **ReasoningOption** | `option` | option candidate à comparer |
| **ReasoningArbitration** | `arbitration` | comparaison argumentée |
| **ReasoningDecision** | `decision` | décision **candidate** (validation humaine requise) |

Tous partagent : `id` (dérivé du contenu, déterministe), `statement`, `sources`
(traçabilité), `confidence`, `tags`, `data`, `hash` (vérifiable par l'audit).

## 2. Le problème (`Problem`)

```json
{
  "id": "prob_…", "question": "Faut-il construire l'API maintenant ou différer ?",
  "options": [{"name": "Construire maintenant", "description": "…", "benefit": 0.7}],
  "criteria": [], "given_facts": ["Le Runtime est livré."],
  "given_constraints": ["Respecter le découplage par contrats."], "actor": "brainai"
}
```

Options facultatives : si absentes, des options canoniques sont dérivées selon le
**type** de problème (décision / diagnostic / design / évaluation / analyse).

## 3. La délibération (`Deliberation`)

Structure de sortie complète :

```
{ problem, decomposition[], facts[], constraints[], hypotheses[], inferences[],
  options[], risks[], arbitration{ranking, argument, top}, decision{status, …},
  explanation{facts, hypotheses, inferences, risks, recommendation, narrative} }
```

- **arbitration.ranking** : options triées par score (bénéfice / risque / conformité
  / confiance).
- **decision.status** : `candidate` → `validated` | `rejected` (par un humain).
- **explanation** : le raisonnement rendu lisible, chaque nature séparée.

## 4. Traçabilité (aval → amont)

```
Décision ──▶ Arbitrage ──▶ Options + Risques ──▶ Faits + Contraintes ──▶ sources
                                                   (given / api:… / control_plane:… / doctrine:…)
```

Chaque élément cite au moins une **source**. L'audit vérifie qu'aucun élément n'est
sans source, et que chaque empreinte correspond au contenu.

## 5. Idempotence & déterminisme

Les identifiants sont dérivés du **contenu** : raisonner deux fois sur le même
problème produit la **même** délibération (vérifié en processus et cross-process).
Aucune horloge murale n'est lue (`as_of` figé).
