# Gouvernance & sûreté du raisonnement

> **Principes cardinaux : aucune auto-modification ; aucune décision souveraine sans
> validation humaine.** Reasoning *délibère et propose* ; il ne *décide* pas seul et
> n'*agit* jamais.

## 1. La décision reste candidate

Toute délibération produit une décision au statut **`candidate`**, avec
`sovereign = false` et `requires_human_validation = true`. Le raisonnement ne peut
pas produire une décision « validée » ou « souveraine ».

## 2. Validation humaine obligatoire

Seule une **action humaine explicite** change le statut, via `HumanValidationPolicy` :

| Action | Transition | Exigence |
|--------|-----------|----------|
| `validate` | candidate → validated | approbateur **requis** |
| `reject` | candidate → rejected | approbateur requis |

- Sans approbateur → refus (`ValidationError`).
- Transition illégale (ex. `reject` après `validate`) → refus.
- Chaque décision humaine est **tracée** : action, approbateur, motif, horodatage.

Une décision **validée** relèverait, si elle est structurante, du processus **ADR**
(SCC-DOC-0009) — hors du périmètre automatique de Reasoning.

## 3. Aucune capacité d'auto-modification

Le `ReasoningEngine` **n'importe aucune API d'écriture** d'une autre couche. Il lit
des faits (interfaces publiques) et n'écrit que dans son registre de délibérations
(`data/deliberations.jsonl`). Il est donc **structurellement incapable** de modifier
Memory, Learning, Kernel, le graphe, une doctrine ou du code. La sûreté est une
**frontière d'architecture**, pas une simple politique.

## 4. Audit

`audit()` vérifie, pour chaque délibération :

- **intégrité** : l'empreinte de chaque élément correspond à son contenu ;
- **traçabilité** : chaque élément cite au moins une source ;
- **sûreté** :
  - toute décision non-candidate porte un **approbateur humain** ;
  - aucune décision n'est marquée `sovereign` ni `applied`.

Sur un registre sain : `audit.ok = true`.

## 5. Fonctionne sans IA — LLM optionnel et subordonné

Le raisonnement par défaut est **déterministe** (règles) : il fonctionne sans aucune
IA. Un LLM (Claude, ChatGPT, Gemini…) pourra plus tard *enrichir* (hypothèses,
options, critique) via `ReasoningProvider`, **sans jamais** :
- devenir un prérequis (repli déterministe garanti) ;
- prendre une décision (la décision reste candidate et humaine).

## 6. Alignement doctrinal

- **Traçabilité complète** ([[SCC-DOC-0016]]) : chaque élément cite ses sources.
- **Gouvernance avant extension** ([[SCC-DOC-0015]]) : rien n'est décidé sans humain.
- **ADR obligatoire** ([[SCC-DOC-0009]]) : une décision structurante validée passe
  par un ADR.
- **Intelligence lourde optionnelle et branchable** ([[SCC-DOC-0029]]) : le LLM est
  une capacité optionnelle, jamais un prérequis.
