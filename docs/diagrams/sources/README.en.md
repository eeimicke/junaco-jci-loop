# Canonical diagram sources

[Deutsch](README.md) · [English](README.en.md)

The `.mmd` files contain the structurally authoritative Mermaid sources for
the documentation diagrams. Translated documents may translate explanatory
labels but must not change any JCI entity or relationship.

| File                                                                 | Content                                         |
| -------------------------------------------------------------------- | ----------------------------------------------- |
| [`jci-loop.mmd`](jci-loop.mmd)                                       | Overall structure of the loop                   |
| [`entity-model.mmd`](entity-model.mmd)                               | Type hierarchy of stored entities               |
| [`future-chain.mmd`](future-chain.mmd)                               | Future chain and WHY path                       |
| [`rof-model.mmd`](rof-model.mmd)                                     | Organisation, team, member, and role activation |
| [`erof-model.mmd`](erof-model.mmd)                                   | Person-bound environment context                |
| [`task-verification.mmd`](task-verification.mmd)                     | Work, result, and verification                  |
| [`ran-evaluation.mmd`](ran-evaluation.mmd)                           | Rule evaluation and conflict                    |
| [`sync-history.mmd`](sync-history.mmd)                               | Change, synchronization, and historization      |
| [`example-complete-entity-map.mmd`](example-complete-entity-map.mmd) | Complete entity map of the example              |
| [`example-purpose-future.mmd`](example-purpose-future.mmd)           | Values, purpose, future and success criterion   |
| [`example-organisation.mmd`](example-organisation.mmd)               | Organisation, team, roles and partnership       |
| [`example-task-execution.mmd`](example-task-execution.mmd)           | Task hierarchy and explicit prerequisites       |
| [`example-environment.mmd`](example-environment.mmd)                 | Person-bound environment and protection         |
| [`example-ran-types.mmd`](example-ran-types.mmd)                     | Rule types, effect and scope                    |
| [`example-ran-conflict.mmd`](example-ran-conflict.mmd)               | Traceable rule conflict                         |
| [`example-sync-outcomes.mmd`](example-sync-outcomes.mmd)             | Protected completion and three SYNC outcomes    |
| [`example-history-correction.mmd`](example-history-correction.mmd)   | Unchanged PiH and correction overlay            |

Named JCI edges use only canonical relationship names. Unnamed process arrows and dashed explanations describe flow or checks; they introduce no new stored JCI relationships. The task, verification, SYNC and correction diagrams complement the [logic changes 2.0](../../en/changes/JCI_LOGIC_2_0.md). The combined completion graph remains a derived view of existing `DECOMPOSES_INTO` and `DEPENDS_ON` edges.
