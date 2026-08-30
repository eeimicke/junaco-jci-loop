# JCI SYNC specification

[Documentation overview](README.md) · [Deutsche Fassung](../JCI_SYNC_SPEC.md)

> Controlled English translation. `docs/JCI_CONTEXT.md` remains canonical.

## 1. Separation of concepts

```text
SYNC      = stored, versioned process definition
SyncRun   = mutable technical runtime state; no graph node
SyncEvent = immutable documentation after completion or controlled termination
```

```text
historisable JCIEntity ── CHANGED_BY ──► ChangeEvent
ChangeEvent ── starts ──► SyncRun (technical)
SyncRun ── uses ──► SYNC
SyncRun ── completes/terminates ──► SyncEvent
ChangeEvent ── TRIGGERS ──► SyncEvent
SyncEvent ── EXECUTES ──► SYNC
SyncEvent ── AFFECTS ──► JCIEntity
SyncEvent ── CREATES_HISTORY ──► PiH
SyncEvent ── CREATES_CORRECTION ──► HistoricalCorrection
```

Technical arrows to SyncRun are process steps, not stored graph relationships.

## 2. Input

A SyncRun receives at least `runId`, `idempotencyKey`, `changeEventId`, target identity and type, expected revision, requested operations, and one exact SYNC definition. The ChangeEvent has exactly one `REQUESTED_BY` RoleAssignment and optional Evidence.

Before traversal SYNC validates JSON Schema, identity, entity type, requester, expected revision, idempotency, and permitted status transition.

## 3. Traversal

Traversal begins at the changed entity. A relationship change begins at both endpoints. The implementation follows the complete dependency matrix:

| Starting type | Direct context | Propagation |
|---|---|---|
| `CiV` | PiH context and `PiF2` purpose | all future and operational descendants |
| `PiF2`, `PiF1s`, `PiF1t`, `PiF1o` | direct contributions and targets | both future directions; PiF1o additionally Tasks and criteria |
| `Task` | parent, children, dependencies, team, executors, objects, Results | task graph bottom-up, then owning PiF1o |
| `SuccessCriterion`, `Result`, `Verification`, `Evidence` | their verification paths | related Task and PiF1o evaluation |
| `RoFOrg`, `RoFTeam`, `RoFTeamMember`, `RoFRole`, `RoleAssignment` | organisation and assignment paths | affected Tasks, futures, ERoF, and RaN |
| `RoFOrgRelationship` | both organisations and representatives | ancestors/descendants for subsidiary, both environmental contexts |
| `ERoFObject` | users, owners, Tasks | organisational environment and governing rules |
| `RaN` | governed targets, scope, conflicts | every target and dependent path |
| `RaNConflict` | rules, targets, detection and resolution | full re-evaluation when resolving |
| `SYNC` | prior definition and using events | no retroactive mutation of old events |
| `ChangeEvent`, `SyncEvent`, `PiH`, `HistoricalCorrection` | immutable process context | consistency only; no recursive ChangeEvent |

A visited key includes entity ID, revision, relationship, and direction. Technical pagination is allowed; semantic truncation is not. An incomplete traversal ends as `FAILED` without partial domain changes.

## 4. Domain evaluation

SYNC evaluates in this order:

1. status transition and terminal state
2. endpoint types, directions, cardinalities, and validity intervals
3. complete WHY, WHO, and environmental paths
4. Task hierarchy and dependencies from atomic Tasks upward
5. SuccessCriterion, current Verification chain, and PiF1o achievement
6. future aggregation from PiF1o toward PiF2
7. applicable RaN, rule decisions, priority, and conflicts
8. revisions, PiH snapshots, relationship snapshots, and counters

Derived changes remain in the same SyncRun and do not create recursive ChangeEvents.

## 5. RaN processing

Determine active and temporally valid rules through governed types, scope, `APPLIES_IN`, and `GOVERNS`. Evaluate the normalised condition. A single denial blocks the requested decision without creating a conflict. Compare only decisions with the same decision key, overlapping scope, and shared target. Greater priority resolves the contradiction; equal highest priority creates `PRIORITY_TIE`; uncertainty creates `UNEVALUABLE`.

Conflict keys are deterministic for ChangeEvent, sorted rule set, and decision. Repeated attempts must not duplicate the same conflict. Resolving a conflict requires an explicit later ChangeEvent and successful re-evaluation; the former open state becomes PiH.

## 6. History preparation

For every existing mutable entity that will actually change:

1. read and lock the expected revision,
2. capture complete state properties,
3. capture all currently valid incoming and outgoing relationships,
4. canonicalise and hash the snapshots,
5. prepare `HAS_HISTORICAL_STATE` and `CREATES_HISTORY`,
6. prepare the current entity at revision plus one.

New entities start at revision 1 without history. Relationship changes revise and historise both existing mutable endpoints. An endpoint created in the same request has no PiH.

## 7. Atomicity and attempt documentation

On `SUCCESS`, the requested domain change, deterministic derived changes, PiH, corrections, resolved conflicts, relationships, and final SyncEvent commit atomically.

On `CONFLICT` or `FAILED`, all uncommitted domain changes roll back. They create neither revision nor PiH. The immutable SyncEvent and newly detected conflicts are stored as attempt documentation after rollback. If this write is temporarily impossible, it is recovered later with the same run ID, ChangeEvent, and idempotency key without executing the domain change again.

## 8. SyncEvent

A completed or controlled terminated run creates exactly one SyncEvent with `startedAt`, `completedAt`, `outcome = SUCCESS | CONFLICT | FAILED`, affected, changed, history, correction, and conflict counters, plus optional error code and message.

Counters must equal stored edges and committed results. Every attempt has a distinct SyncEvent. The same idempotency key applies the domain change at most once.

## 9. Concurrency and recovery

Immediately before commit, compare every current revision with the revision read at start. A mismatch prevents all domain changes and ends as conflict or a new attempt. Orphaned technical runs are detected through runtime state such as heartbeat. Recovery never replaces the final SyncEvent.

## 10. Exchange

`JCIChangeRequest` and `JCISyncResult` follow the JSON Schemas under `docs/schemas/`. Unknown schema versions, additional forbidden fields, and invalid operations are rejected before graph mutation. Full exports use JSON-LD 1.1.

