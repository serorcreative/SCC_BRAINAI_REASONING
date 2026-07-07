# Processus de délibération

Comment Reasoning transforme un problème en décision candidate argumentée.

## 1. Analyser & décomposer

`analyze_problem()` classe le problème (décision / diagnostic / design / évaluation
/ analyse) par mots-clés (ou par la présence d'options). `decompose()` produit des
**sous-questions** ordonnées : faits → contraintes → options/hypothèses → risques →
arbitrage → décision.

## 2. Rassembler les faits (ancrage optionnel)

Les faits proviennent de deux sources :
- **fournis** par l'appelant (`given_facts`) ;
- **ancrés dans SCC** via les interfaces publiques (si `ground_facts`) : graphe et
  readiness (API 08), santé (Control Plane 09). Chaque fait porte sa **source**
  (`api:graph.summary`, `control_plane:health`…).

L'ancrage est **dégradable** : si une source manque, le raisonnement continue.

## 3. Contraintes

`derive_constraints()` combine :
- les contraintes **données** par l'appelant ;
- les contraintes **doctrinales** ancrées (doctrines pertinentes du graphe) ;
- des **garde-fous par défaut** toujours applicables :
  - « Toute décision structurante doit produire un ADR » (SCC-DOC-0009) ;
  - « Aucune action T3 sans validation humaine » ;
  - « Une décision candidate n'est jamais appliquée automatiquement ».

## 4. Options, hypothèses, risques

- **Options** : fournies ou canoniques selon le type.
- **Hypothèses** : une générale (par type) + une conditionnelle **falsifiable** par
  option.
- **Risques** : par option (inaction, irréversibilité, sur-ingénierie, santé
  dégradée, non-conformité), avec **sévérité** et **traçabilité** vers l'option.

## 5. Arbitrage (scoring pondéré)

Chaque option est scorée sur quatre critères pondérés (`config.weights`) :

```
score = w_benefit·bénéfice + w_risk·(1 − risque) + w_constraint·conformité + w_confidence·confiance
défaut : 0.4 / 0.3 / 0.2 / 0.1
```

- **bénéfice** : attribut de l'option ;
- **risque** : sévérité du pire risque de l'option ;
- **conformité** : pénalisée en cas de risque de non-conformité ;
- **confiance** : moyenne de confiance des faits (reflète l'ancrage).

Le classement est trié par score décroissant (départage par identifiant). L'arbitrage
**argumente** pourquoi l'option de tête l'emporte.

## 6. Inférence, décision candidate, explication

- **Inférence** : relie le nombre de faits/contraintes au meilleur score.
- **Décision candidate** : l'option de tête, `status = candidate`, `sovereign =
  false`, `requires_human_validation = true`.
- **Explication** : récit typé distinguant faits / hypothèses / inférences / risques
  / recommandation, avec le rappel que la décision **exige une validation humaine**.

## 7. Extension LLM (optionnelle)

Un fournisseur (`ReasoningProvider`) peut, plus tard, **enrichir** : suggérer des
hypothèses/options, critiquer l'arbitrage. Il n'est **jamais requis** et ne **décide
jamais** : le squelette (faits, options, risques, arbitrage, décision) reste produit
par les règles déterministes. Aucun LLM n'est branché dans le socle.
