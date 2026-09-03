# Introducing the JCI Loop

[Documentation overview](../README.md) · [Deutsch](../../guides/JCI_INTRODUCTION.md)

## The initial thesis

Organizations rarely fail because there are no goals, roles or rules at all. They often fail because these elements no longer fit together: a goal changes while tasks, responsibilities, systems or rules remain unchanged.

The **JCI Loop** describes these relationships in a common graph and makes changes traceable. It answers not only *what* is done, but also *why*, *by whom*, *under what rules*, *in what environment* and *with what historical context*.

## The context

```mermaid
flowchart LR
    PiH -->|PROVIDES_CONTEXT_TO| CiV
    CiV -->|HELD_BY| ValueHolder[RoFOrg, RoFTeam, or human]
    CiV -->|INFORMED_BY| SourceCiV[another CiV]
    CiV -->|INSCRIBES_PURPOSE_IN| PiF2
    PiF1s -->|CONTRIBUTES_TO| PiF2
    PiF1t -->|CONTRIBUTES_TO| PiF1s
    PiF1o -->|CONTRIBUTES_TO| PiF1t
    PiF1o -->|DECOMPOSES_INTO| Task
    Task -->|PRODUCES| Result
    Verification -->|EVALUATES| Result
    ChangeEvent -->|TRIGGERS| SyncEvent
    SyncEvent -->|CREATES_HISTORY| PiH
```

Each `CiV` describes one value through the NOT, SELF, and TO SERVE dimensions. `HELD_BY` assigns it to exactly one organization, team, or human. A `PiF2` is developed from explicitly selected CiV; `PiF2` through `PiF1o` make the intended future increasingly concrete. Through `PROTECTS`, `RaN` protects the CiV and PiF2 and governs their concrete implementation through `GOVERNS`. Tasks realize the operational state. Results are checked. `RoF` assigns responsibility and `ERoF` describes the relevant environment. `SYNC` tracks changes; superseded states remain as `PiH`.

## What makes JCI special

- **Graph instead of isolated lists:** Relationships belong to the model and are not just free text.
- **WHY path:** You can go back from a Task to the value-related purpose.
- **WHO path:** Execution, team, member, role and organization remain clear.
- **Testable Goals:** A `PiF1o` has success criteria; Results and verifications remain separate.
- **Value protection as a cross-section:** `RaN` protects CiV and PiF2 and may allow, require, or prohibit concrete implementation decisions.
- **Historization:** Only actually superseded states are preserved as immutable `PiH`.
- **Controlled Change:** `SYNC` checks effects, conflicts, revisions and consequential changes.

## What JCI is not

JCI is not a finished software or an organizational chart. It is a technology-independent professional model. For example, an application can implement it in Neo4j, but must comply with the documented entities, relationships, state rules and invariants.

## Next step

Next, read the [JCI Element Overview](JCI_ELEMENTS.md) or follow the [Walkthrough Example](JCI_EXAMPLE.md).

