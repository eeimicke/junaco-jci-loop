# JCI graph rules

[Documentation overview](README.md) · [Deutsche Fassung](../JCI_GRAPH_RULES.md)

> Controlled English translation. `docs/JCI_CONTEXT.md` remains canonical.

## 1. General invariants

1. Every node is a `JCIEntity` with exactly one valid concrete `entityType`.
2. UUID and creation time never change; every committed domain change increments revision exactly once.
3. Terminal states never reopen.
4. `PiH`, `ChangeEvent`, `SyncEvent`, and `HistoricalCorrection` are immutable process artifacts.
5. Active or closed entities have exactly one `CREATED_BY`; bootstrap drafts may temporarily have none.
6. Only canonical relationship names, directions, endpoint types, and cardinalities are permitted.
7. Inverse readings never create duplicate edges.
8. `REPLACED_BY`, `SUPERSEDES`, Task hierarchy, Task dependency, and subsidiary graphs are acyclic.

## 2. Traceability

An active or completed atomic Task has:

```text
WHY: Task ← PiF1o → PiF1t → PiF1s → PiF2 ← CiV
WHO: Task → RoleAssignment → member, role, team → RoFOrg
WHERE: Task and executing RoleAssignment → ERoFObject
```

Missing mandatory traceability blocks activation or completion.

## 3. Future graph

`CONTRIBUTES_TO` is directed from the more concrete to the more general future state and forms a many-to-many graph. Current contributions exclude `REPLACED` and `REVOKED`. A replacement counts only after its own contribution to the same target exists. `ALL` requires all current direct contributions to be `ACHIEVED`; `ANY` requires at least one. No future can be achieved without a current direct contribution.

## 4. Tasks, results, and verification

1. Each Task belongs to exactly one `PiF1o` and one responsible team.
2. `ATOMIC` Tasks may be executed, use environmental objects, and produce Results.
3. `COMPOSITE` Tasks only structure direct subtasks and derive their status.
4. Task hierarchy and `DEPENDS_ON` are acyclic.
5. A Task can complete only when all dependencies and completion conditions hold.
6. Every Result is produced by exactly one atomic Task.
7. Every Verification evaluates exactly one Result and checks exactly one SuccessCriterion.
8. Current Verification chains use `SUPERSEDES` without cycles.
9. Required criteria, completed Tasks, dependencies, and model rules must all hold before `PiF1o → ACHIEVED`.

## 5. RoF rules

1. Every team belongs to exactly one organisation and has at least one member.
2. A member may belong to several teams and organisations while retaining one identity.
3. Each RoleAssignment belongs to exactly one member, one team, and one role owned by that member.
4. Membership and role ownership have validity intervals; the assignment lies within their intersection.
5. Optional allocation satisfies `0 < allocation <= 1`; overlapping allocations total at most one per member.
6. An active organisation relationship connects two different organisations and has at least one valid representative assignment per side.
7. `SUBSIDIARY` has at most one immediate active parent and no cycle.
8. `PARTNERSHIP` is mutual but stored by ascending organisation UUID.
9. Equal active relationship type, pair, and overlapping interval are forbidden.

## 6. ERoF rules

1. Every active `ERoFObject` is used by at least one RoleAssignment.
2. A Task may use an object only when an executing RoleAssignment uses it too.
3. `OWNED_BY` expresses ownership but never replaces `USES`.
4. Internal and external are derived relative to a `RoFOrg`.
5. Organisations remain `RoFOrg` and are never duplicated as `ERoFObject`.

## 7. RaN rules

Applicable rules are active, temporally valid, type-compatible, target-relevant, and inside their declared scope. `GLOBAL` and `ENTITY` have no `APPLIES_IN`; organisation and team scope each have exactly one type-correct scope edge.

A single `DENY` is a violation, not a conflict. A contradiction requires the same `decisionKey`, overlapping scope, shared target, and simultaneous `ALLOW` and `DENY`. Greater priority wins only the contradiction. Equal highest priority creates `PRIORITY_TIE`; unevaluable conditions create `UNEVALUABLE`. Open conflicts block dependent automatic changes.

## 8. History and corrections

1. A successfully superseded existing state creates exactly one `PiH` for that revision.
2. New entities and merely affected entities create no `PiH`.
3. Every PiH has exactly one original entity and one creating SyncEvent.
4. PiH and process artifacts are never modified or recursively historised.
5. Historical corrections preserve the original PiH and form an acyclic optional `SUPERSEDES` chain.

## 9. SYNC and revision rules

1. `SyncRun` is technical state, not a graph node.
2. Every completed or controlled terminated attempt eventually has exactly one immutable SyncEvent.
3. On `SUCCESS`, domain changes and required history commit atomically.
4. On `CONFLICT` or `FAILED`, uncommitted domain changes roll back and create no revision or PiH.
5. Attempt documentation remains and a temporarily failed event write must be recovered without re-executing the domain change.
6. Idempotency prevents the same domain change from being applied twice.
7. Counters equal their stored relationships and committed outcomes.

These rules are closed for version 1.0. Extensions require a versioned model change and automated tests.

