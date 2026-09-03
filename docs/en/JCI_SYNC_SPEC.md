# JCI-SYNC Specification

## 1. Status and Purpose

This document describes the technology-independent process of `SYNC`. Its domain meaning is defined by [JCI_CONTEXT.md](JCI_CONTEXT.md), its types by [JCI_ONTOLOGY.md](JCI_ONTOLOGY.md), and its valid graph states by [JCI_GRAPH_RULES.md](JCI_GRAPH_RULES.md).

## 2. Terms

```text
SYNC        = stored and historizable definition of the synchronization logic
SyncRun     = mutable technical state during an execution attempt
SyncEvent   = immutable domain record after completion or controlled termination
ChangeEvent = immutable record of an accepted change request
```

`SyncRun` is not a `JCIEntity`, `GraphObject`, or JCI core element. The implementation may store it in a runtime, queue, or logging structure. It is not created as an intermediate node in the domain JCI graph.

## 3. Binding Context

```text
existing historizable JCIEntity ── CHANGED_BY ──► ChangeEvent
ChangeEvent ── schedules ──► SyncRun (technical)
SyncRun ── uses ──► SYNC
SyncRun ── completion or controlled termination ──► SyncEvent

ChangeEvent ── TRIGGERS ──► SyncEvent
SyncEvent ── EXECUTES ──► SYNC
SyncEvent ── AFFECTS ──► JCIEntity
SyncEvent ── CREATES_HISTORY ──► PiH
historizable JCIEntity ── HAS_HISTORICAL_STATE ──► PiH

ChangeEvent:HISTORICAL_CORRECTION ── TARGETS_HISTORY ──► PiH
SyncEvent ── CREATES_CORRECTION ──► HistoricalCorrection
HistoricalCorrection ── CORRECTS ──► same PiH
```

The stored edges represent domain provenance. The technical arrows to `SyncRun` are process steps, not graph relationships; a `SyncRun` is never created as a JCI node. An accepted `ChangeEvent` may initially have no `TRIGGERS` target. Each attempt that completes or is terminated in a controlled manner appends exactly one such edge.

## 4. Inputs of a SyncRun

A technical `SyncRun` requires at least:

| Input               | Meaning                                   |
| ------------------- | ----------------------------------------- |
| `runId`             | unique technical run identifier           |
| `idempotencyKey`    | identifier of the domain change request   |
| `changeEventId`     | triggering `ChangeEvent`                  |
| `syncDefinitionId`  | active `SYNC` definition to use           |
| `startedAt`         | start of the attempt                      |
| `requestedRevision` | expected revision or `null` for `CREATED` |

The `ChangeEvent` already stored before the run has at least:

```text
id = requestId
idempotencyKey
targetEntityId
targetEntityType
requestedRevision
changeType
occurredAt
reason
status = RECORDED
revision = 1
```

It has exactly one `REQUESTED_BY` relationship to a `RoleAssignment`. Optional evidence is connected to `Evidence` through `USES_EVIDENCE`. Its properties are not changed after acceptance.

## 5. Process

### 5.1 Acceptance

1. Verify that the `ChangeEvent` and active SYNC definition exist and that all immutable request fields are complete.
2. Verify that `REQUESTED_BY` exists and that the role assignment is valid at the relevant time.
3. Check whether the `idempotencyKey` has already been processed successfully.
4. Validate the target state according to `changeType`:
   - For `CREATED`, `targetEntityId` must not yet exist and `requestedRevision` must be `null`.
   - For `HISTORICAL_CORRECTION`, the target must be an existing `PiH`, `requestedRevision = 1`, exactly one `TARGETS_HISTORY` relationship to that PiH and no `CHANGED_BY` source must exist.
   - For all other change types, the historizable target entity must exist, its current revision must equal `requestedRevision`, and it must be the sole `CHANGED_BY` source of the ChangeEvent.
5. Start a technical `SyncRun` with a unique `runId` and state `RUNNING`.

A failure before successful target resolution terminates the attempt in a controlled manner with `FAILED`. In this exceptional case, the final `SyncEvent` may have no `AFFECTS` target. For `SUCCESS` or `CONFLICT`, at least one affected `JCIEntity` must have been identified.

**Short example:** A `CREATED` request reserves the desired UUID only as `targetEntityId`. The node is created only by a successful commit; a failed attempt leaves only the `ChangeEvent` and final `SyncEvent`.

### 5.2 Impact Determination

1. Start with the entity identified by `targetEntityId` and `targetEntityType` or with the validated `CREATED` candidate.
2. Traverse stored relationships according to the ontology and graph rules.
3. Record direct and indirect impact separately.
4. Mark already visited combinations of entity and relationship path to terminate cycles.
5. Do not treat impact alone as a change.
6. Identify at least one affected `JCIEntity` for `SUCCESS` and `CONFLICT`. `AFFECTS = 0` is permitted only for an early `FAILED` before target resolution.

For a change to a Task, `SYNC` traverses at least:

- the directly changed Task,
- its direct parent and all higher-level Tasks,
- its direct and all lower-level Tasks,
- its prerequisites through `DEPENDS_ON`,
- all Tasks depending on it through the inverse reading of `DEPENDS_ON`,
- all thereby affected `PiF1o`,
- their success criteria and applicable current Verifications,
- responsible teams, executing RoleAssignments, used ERoFObjects, and relevant `RaN`.

Because `DEPENDS_ON` may cross PiF1o boundaries, a Task change can affect multiple operational target states.

#### 5.2.1 Mandatory Traversal Matrix

The following matrix defines the minimum domain traversal. “Upward” means the WHY path to the higher-level future and to `CiV`; “downward” means contributing future elements through operational implementation. Inverse readings use the same stored edge in the opposite direction.

| Changed type           | Check directly                                                                                                 | Continue indirectly                                                                                                  |
| ---------------------- | -------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------- |
| `CiV`                  | three dimensions, `HELD_BY`, `INFORMED_BY`, protecting `RaN`, connected `PiF2`, context-providing `PiH`        | to source CiV, value holder, and protected PiF2; downward to every governed implementation element                   |
| `PiF2`                 | grounding `CiV`, shared value holder, protecting `RaN`, contributing `PiF1s`                                   | to protected CiV; downward to `PiF1o` and every governed implementation element                                      |
| `PiF1s`                | target `PiF2`, contributing `PiF1t`, `RaN`                                                                     | upward to `CiV`, downward to operational graph objects                                                               |
| `PiF1t`                | target `PiF1s`, contributing `PiF1o`, `RaN`                                                                    | upward to `CiV`, downward to Tasks and verification                                                                  |
| `PiF1o`                | target `PiF1t`, criteria, accountable member, all Tasks, `RaN`                                                 | complete WHY path, Task graph, Results, Verifications, teams, roles, and ERoF                                        |
| `Task`                 | parent, subtasks, prerequisites, dependent Tasks, PiF1o, team, executors, ERoFObjects, Results, `RaN`          | all Task and PiF1o graphs reached from them, including their future and verification paths                           |
| `SuccessCriterion`     | associated `PiF1o`, checking applicable current Verifications, `RaN`                                           | Results and Tasks of the Verifications; then PiF1o aggregation and future chain                                      |
| `Result`               | producing Task, current and superseded Verifications, `RaN`                                                    | PiF1o, criteria, Task graph, and higher future levels                                                                |
| `Verification`         | Result, criterion, their bound revisions, predecessor/successor, Evidence                                      | producing Task, PiF1o, all applicable current Verifications, criteria, and higher future levels                      |
| `Evidence`             | all incoming `USES_EVIDENCE`, `RaN`                                                                            | their respective domain target paths; Evidence itself determines no status                                           |
| `RaN`                  | `PROTECTS`, `GOVERNS`, `APPLIES_IN`, open conflicts                                                            | all protected CiV and PiF2, all governed implementation elements, and their dependent paths according to this matrix |
| `RaNConflict`          | conflicting rules, affected entities, detecting SyncEvent, resolution references                               | upon resolution, fully recheck all affected entities and rules                                                       |
| `RoFOrg`               | teams, organization relationships, owned ERoFObjects, `RaN`                                                    | members, role assignments, Tasks, PiF1o, and the other organization side                                             |
| `RoFOrgRelationship`   | both organizations, representing RoleAssignments, `RaN`                                                        | teams, members, ERoF and, for `SUBSIDIARY`, the complete ancestor/descendant structure                               |
| `RoFTeam`              | organization, members, RoleAssignments, responsible Tasks, `RaN`                                               | PiF1o, Task graph, ERoFObjects, and organization relationships of the participants                                   |
| `RoFTeamMember`        | teams, roles, assignments, accountable PiF1o, `RaN`                                                            | executed Tasks, ERoFObjects, organizations, and future paths                                                         |
| `RoFRole`              | owning members, activating assignments, `RaN`                                                                  | teams, Tasks, ERoFObjects, and affected organizations                                                                |
| `RoleAssignment`       | member, team, role, Tasks, ERoFObjects, organization representations, `RaN`                                    | organization, PiF1o, Task graph, and environment of all direct uses                                                  |
| `ERoFObject`           | using assignments and Tasks, owners, `RaN`                                                                     | teams, members, organizations, PiF1o, and future paths of the Tasks                                                  |
| `SYNC`                 | using SyncEvents and valid predecessor definition                                                              | the new definition is checked by the previously active definition; no retroactive change to old SyncEvents           |
| `ChangeEvent`          | target coordinates, optional `CHANGED_BY` source, `TARGETS_HISTORY`, requester, Evidence, triggered SyncEvents | only within the existing change process; no recursive ChangeEvent                                                    |
| `SyncEvent`            | ChangeEvent, executed SYNC definition, affected entities, created history/corrections/conflicts                | immutable; check only the consistency of its stored references                                                       |
| `PiH`                  | original entity, creating SyncEvent, corrections, context use                                                  | immutable; treat deviations exclusively as HistoricalCorrection                                                      |
| `HistoricalCorrection` | PiH, ChangeEvent, SyncEvent, corrector, Evidence, `baseHistoryViewHash`, predecessor/successor                 | immutable; determine the effective `HistoryView` and treat a current model correction as a separate process          |

When a relationship changes, `SYNC` starts at both endpoints and uses the matrix row for each. For `REPLACED_BY`, `SUPERSEDES`, `DEPENDS_ON`, `DECOMPOSES_INTO`, `CONTRIBUTES_TO`, and `SUBSIDIARY`, the respective chain is traversed to its end and checked for cycles.

A committed relationship change increases the revision of both pre-existing mutable endpoints and creates a `PiH` for each. An endpoint newly created in the same request starts at revision `1` and does not yet receive a `PiH`. Derived follow-up changes remain in the same SyncRun and create no additional `ChangeEvent`.

The traversal maintains a visited set of `entityId`, read `revision`, relationship type, and direction. An already visited entry is not expanded again. Technical page sizes may split reading into parts but must never truncate the domain result set. If a technical limit is reached and the complete set cannot be determined safely, the attempt ends with `FAILED`; no partial domain changes are committed.

**Short example:** When Anna’s `RoleAssignment` ends, SYNC checks membership, role, team, every Task it executes, and every environmental object it uses. Through the Tasks, SYNC reaches the affected `PiF1o` and checks whether execution, success criteria, and higher future states remain valid.

### 5.3 Validation

Before any domain evaluation, `SYNC` checks the status transition against section 2.2.4 of [`JCI_CONTEXT.md`](JCI_CONTEXT.md). A transition not listed there ends with `outcome = CONFLICT`; the current state remains unchanged. Terminal states are not reopened. A continuation is created as a new entity.

Before activating or completing an atomic Task, `SYNC` also checks traceability: the WHY path must lead through `PiF1o`, `PiF1t`, `PiF1s`, and `PiF2` to at least one `CiV`. The WHO path must unambiguously identify the executing `RoleAssignment`, member, role, responsible team, and organization. A missing mandatory path prevents the status transition.

Whenever a CiV is created or changed, `SYNC` validates that it describes exactly one value through the three non-empty dimensions `notCiV`, `selfCiV`, and `toServeCiV`, has exactly one permitted `HELD_BY` value holder, and does not use a technical member as personal scope. `INFORMED_BY` must not form a self-relationship and is never inferred from names, memberships, or affiliations. For every connected `PiF2`, all directly grounding CiV must have the same value holder. A value decision or adoption of dimensions requires human confirmation and is never created by `SYNC` itself.

Whenever a RaN is created, activated, or changed, `SYNC` validates `PROTECTS` separately from `GOVERNS`: an active RaN protects at least one CiV and one PiF2, governs at least one permitted implementation element, and satisfies bidirectional coherence through `INSCRIBES_PURPOSE_IN`. Protection targets must be organizationally compatible with `scopeType`, `APPLIES_IN`, and, for `ENTITY`, the WHY paths of the governed targets. `GOVERNS` to `PiF2` is prohibited. `SYNC` validates human-requested protection edges but neither creates nor guesses them itself.

For `changeType = REPLACED`, `SYNC` checks that exactly one successor of the same concrete type is specified through `REPLACED_BY`. For every other status, the entity being changed must have no outgoing `REPLACED_BY` relationship. Self-references and cycles are rejected.

Process artifacts do not create a recursive event chain. `ChangeEvent`, `SyncEvent`, `PiH`, `HistoricalCorrection`, and an open `RaNConflict` detected during the run are created within the existing change process. `SYNC` starts no additional `SyncRun` for their own creation.

**Example:** A `COMPLETED` Task cannot be set back to `ACTIVE`. If more work is required, a new Task is created and assigned to a `PiF1o` through the regular JCI path.

For every possible change, at least the following are checked:

- permitted source and target types,
- cardinalities,
- status transition,
- current revision,
- relevant `RaN`,
- role and team context,
- temporal overlap of team membership, role ownership, and role assignment,
- organization-relative ownership and environmental perspective,
- CiV dimensions, unique value holder, explicit `INFORMED_BY` provenance, and shared PiF2 scope,
- RaN protection edges, protected CiV-PiF2 coherence, permitted `GOVERNS` implementation types, and protection scope,
- person-bound ERoF use,
- organization rules, including freedom from `SUBSIDIARY` cycles,
- immutable entity types,
- required Evidence and responsibility,
- Task type, Task hierarchy, and freedom from cycles,
- Task dependencies and their freedom from cycles,
- type-dependent execution, environment, and Result rules,
- applicability, compatibility, and priority of all relevant `RaN`.

Semantics that cannot be decided unambiguously and contradictory `RaN` lead to a conflict. `SYNC` does not resolve them silently.

### 5.3.1 Evaluation of Success Criteria

When a `Verification` is created or an existing Verification is superseded by a new one, `SYNC` additionally performs:

1. Verify that `EVALUATES` points to exactly one `Result` and `CHECKS` to exactly one `SuccessCriterion`.
2. Verify that the Result is `COMPLETED`, the criterion is `ACTIVE`, and both belong to the same `PiF1o` through the producing Task and `HAS_SUCCESS_CRITERIA` respectively.
3. Read the current revisions of both targets from one consistent read view and bind them as positive integers in `evaluatedResultRevision` and `checkedCriterionRevision`.
4. For `SUPERSEDES`, verify that predecessor and successor evaluate the same Result and check the same criterion.
5. Immediately before commit, read both target revisions again. Any deviation produces `CONFLICT`; the Verification is not stored.
6. For aggregation, consider only completed, non-superseded Verifications whose bound target revisions still match the current revisions.
7. For every applicable current Verification, verify that measured value, `measurementType`, `operator`, `targetValue`, and optional unit match reproducibly; otherwise the Verification is `INCONCLUSIVE`.
8. For `evaluationMode = ALL`, evaluate the criterion as fulfilled only if at least one applicable current Verification exists and all are `VALID`.
9. For `evaluationMode = ANY`, evaluate the criterion as fulfilled as soon as at least one applicable current Verification is `VALID`.
10. Treat `INVALID`, `INCONCLUSIVE`, revision-stale, and missing applicable Verifications as not fulfilling the criterion according to the graph rules.
11. Aggregate all `REQUIRED` criteria for the associated `PiF1o` and consider only Verifications of Results produced by Tasks of that `PiF1o`.
12. Prepare the status transition to `ACHIEVED` only if at least one required criterion exists, every required criterion is fulfilled, all assigned Tasks are `COMPLETED`, all Task dependencies are fulfilled, and no model or `RaN` violation exists.

`OPTIONAL` criteria are documented in the result but do not block `ACHIEVED`. If the decision is not unambiguous, the status remains unchanged and the attempt records `CONFLICT`.

**Short example:** A Verification binds revision 3 of a completed Result and revision 5 of the active criterion. If a concurrent request changes the criterion to revision 6 before commit, the Verification is not committed. If the criterion changes only later, the Verification remains as a record of checking the old revision but no longer counts as applicable.

### 5.3.2 Evaluation of Task Status

When a Task changes, `SYNC` first evaluates the atomic Tasks, then the Task hierarchy from bottom to top, and finally the affected `PiF1o`:

1. Determine all targets of `DEPENDS_ON` for every `ATOMIC` Task.
2. If at least one prerequisite is not `COMPLETED`, prepare `BLOCKED`.
3. If all prerequisites are fulfilled, check execution, team, and `RaN` rules and determine the requested or currently permitted status.
4. Determine the effective direct subtasks for every `COMPOSITE` Task: a replaced subtask is replaced by its `REPLACED_BY` successor only if that successor is also a direct subtask of the same parent. Then apply: only `DRAFT` → `DRAFT`; only `COMPLETED` → `COMPLETED`; at least one `ACTIVE` or a mixture of `DRAFT` and `COMPLETED` → `ACTIVE`; no `ACTIVE` but at least one `BLOCKED` → `BLOCKED`.
5. Repeat the derivation through all root Tasks.
6. Then jointly evaluate Task completion, success criteria, and the remaining model conditions for every affected `PiF1o`.

An incorrectly connected `REPLACED` subtask, a still connected `REVOKED` subtask, or a cyclic or contradictory structure produces `CONFLICT`. Every derived status transition that is actually committed creates, like any other domain change, a revision and a `PiH` for the superseded state.

### 5.3.3 Aggregation of Higher-Level Future States

After every change to a future element, `SYNC` evaluates the future chain from bottom to top:

1. Determine the current directly contributing `PiF1o` for `PiF1t`, the current `PiF1t` for `PiF1s`, and the current `PiF1s` for `PiF2`.
2. Do not count `REPLACED` and `REVOKED` as current contributions. Consider a replacement only once it itself contributes to the same target.
3. Do not derive `ACHIEVED` without at least one current direct contribution.
4. For `contributionMode = ALL`, prepare `ACHIEVED` only if all current direct contributions are `ACHIEVED`.
5. For `contributionMode = ANY`, prepare `ACHIEVED` as soon as at least one current direct contribution is `ACHIEVED`.
6. Recheck the next higher level after every derived change.

**Example:** Two operational states contribute to a tactical state with `contributionMode = ALL`. Only after both `PiF1o` are achieved may `SYNC` prepare the `PiF1t` as achieved.

### 5.3.4 Evaluation of RaN

For every decision affected by rules, `SYNC` performs:

1. For each active RaN, validate at least one protected CiV, one protected PiF2, their coherence through `INSCRIBES_PURPOSE_IN`, and organizational compatibility with the scope. Missing or contradictory protection relationships block activation or the decision; `SYNC` does not add them automatically.
2. Use `governedTypes`, `scopeType`, and, where applicable, `APPLIES_IN` to identify all potentially relevant active and temporally valid `RaN`; compare `GOVERNS` with the current concrete implementation elements and prepare any required target edges.
3. Evaluate every normalized condition reproducibly. Non-cataloged or ambiguous paths produce `UNEVALUABLE`.
4. Derive `ALLOW`, `DENY`, or `NO_DECISION` from `effect` and the condition for each rule.
5. Treat a single rule violation as `DENY` and block the decision without creating a `RaNConflict` solely for that violation.
6. Compare only rules with the same `decisionKey`, overlapping scope, and a common target for contradictory results.
7. For every actual contradiction between `ALLOW` and `DENY`, compare priorities.
8. If priorities differ, give the larger number precedence only within that contradiction.
9. If the highest relevant priority is tied, prepare an open `RaNConflict` with `conflictType = PRIORITY_TIE` and a `conflictKey` derived from the ChangeEvent, sorted conflict set, and decision.
10. If applicability or compatibility cannot be evaluated unambiguously, prepare an open `RaNConflict` with `conflictType = UNEVALUABLE` and a corresponding `conflictKey`.
11. Block automatic changes whose permissibility depends on the open conflict.

A lower-priority `RaN` is not revoked by precedence and remains applicable to compatible and other decisions. `ruleType` is not used as a ranking.

Before creating a conflict, `SYNC` checks whether a `RaNConflict` with the same `conflictKey` already exists for the same change request. A retry must not create a duplicate node. Optional evidence is connected exclusively as `Evidence` nodes through `USES_EVIDENCE`.

To resolve an existing conflict, a subsequent `SyncRun` rechecks the rules connected through `CONFLICTING_RULE` and the affected entities. Only when the documented contradiction no longer exists and the attempt succeeds does `SYNC` prepare `status = RESOLVED`, `resolvedAt`, `resolution`, `RESOLVED_BY`, and `RESOLVED_THROUGH`. The initial open state is prepared as a `PiH`.

### 5.4 Preparing the Change

For every existing entity that will actually change:

1. Read all properties and valid relationships of the initial state.
2. Form a canonical `StateSnapshot` and sorted `RelationshipSnapshot` entries from them; then calculate the SHA-256 `contentHash`.
3. Prepare an immutable `PiH` with `originalEntityId`, `originalEntityType`, `originalRevision`, schema versions, and the snapshots.
4. Prepare `HAS_HISTORICAL_STATE` and `CREATES_HISTORY`.
5. Prepare the new current state with `revision + 1` and a new `updatedAt`.

For `changeType = CREATED`, first form only a candidate from the requested fields and relationships. `SYNC` validates the permitted creation status, all required fields, cardinalities, and `RaN`. On `SUCCESS`, the target node with `revision = 1`, `CREATED_BY`, and exactly one `CHANGED_BY` edge to the already existing `ChangeEvent` are created together atomically. No `PiH` is created for the new entity. On `CONFLICT` or `FAILED`, neither the target node nor these edges are stored.

### 5.5 Historical Correction

For `changeType = HISTORICAL_CORRECTION`:

1. Verify that `targetEntityId` identifies an existing `PiH`, `targetEntityType = PiH`, `requestedRevision = 1`, exactly one `TARGETS_HISTORY` relationship to that PiH, and no `CHANGED_BY` source exist.
2. Read the structured `historicalCorrection` payload from exchange format 1.1; generic `operations` are not permitted for this change type.
3. Verify that `CORRECTED_BY` points to a valid `RoleAssignment`.
4. Validate the reason, correction type, `valueSchemaVersion`, affected fields, and previous and corrected values.
5. Validate `correctedFields` as unique, lexicographically sorted canonical JSON Pointers. `previousValue` and `correctedValue` must have exactly the same key set.
6. Deterministically construct the effective `HistoryView` from the immutable `PiH` and all non-superseded corrections and calculate its SHA-256 hash.
7. Verify that the calculated hash equals `expectedHistoryViewHash`. For every corrected path, `previousValue` must equal the effective value; for `ADDITION` it is `NULL`.
8. Identify all active corrections of the same `PiH`. Without field overlap, the new correction may coexist with them.
9. If fields overlap, the new correction must completely replace exactly one active predecessor through `SUPERSEDES`. It adopts at least that predecessor’s complete `correctedFields` set; additional fields must not overlap any other active correction. Partial adoption or overlap with multiple active corrections produces `CONFLICT`.
10. Verify that correction chains point to the same PiH, move forward in time, and are acyclic.
11. Serialize commits per `PiH`, recalculate the `HistoryView` immediately before commit, and compare its hash to `expectedHistoryViewHash` again. A mismatch produces `CONFLICT` and no correction.
12. Prepare a new immutable `HistoricalCorrection` with `baseHistoryViewHash = expectedHistoryViewHash`. `CORRECTS` points to the same PiH as `TARGETS_HISTORY`; `CAUSED_BY` points to the triggering `ChangeEvent`.
13. Validate optional `Evidence` through `USES_EVIDENCE`.
14. Never modify or historicize the existing `PiH`.

If an additional need to change the current model arises, create a separate change process for it.

**Short example:** One effective correction corrects `/stateData/name`. A new correction to a disjoint relationship path may apply in parallel. To correct `/stateData/name` again, the new correction must completely supersede exactly the currently effective correction and use the current `HistoryView` hash.

### 5.6 Domain Atomicity and Completion Documentation

On `SUCCESS`, the following contents are committed together atomically:

- new current states,
- for `CREATED`, the new target node with `revision = 1`, `CREATED_BY`, and `CHANGED_BY`,
- prepared `PiH`,
- prepared `HistoricalCorrection` objects,
- resolved `RaNConflict` objects,
- all associated relationships,
- the final `SyncEvent` with its `runId`,
- the new append-only `TRIGGERS` relationship.

On `CONFLICT` or `FAILED`, the requested domain change and all follow-up changes not yet committed are rolled back completely. No new revision or `PiH` is created for a state that was not committed. After rollback, the implementation stores the completion documentation with the immutable `SyncEvent` and, where applicable, newly detected `RaNConflict` objects. This documentation belongs to the attempt, not to the rejected domain state.

```text
Domain transaction
├── SUCCESS  → commit completely
├── CONFLICT → roll back completely
└── FAILED   → roll back completely

Completion documentation
└── always store SyncEvent after the attempt has ended
    └── record RaNConflict where required
```

If event storage is temporarily technically impossible, a durable obligation to complete it remains. After write capability has been restored, exactly the missing `SyncEvent` is stored with the same `runId`, the same `ChangeEvent`, and the same `idempotencyKey`, and `TRIGGERS` is appended once. This operation must not execute the failed or conflicting domain change again.

## 6. Creation of the SyncEvent

A `SyncEvent` is not created at the beginning of or during the attempt. It is created only after all required information is known.

Required fields:

```text
id
entityType = SyncEvent
name
createdAt
updatedAt = createdAt
revision = 1
status = RECORDED
runId
startedAt
completedAt
outcome
affectedCount
changedCount
historyCount
correctionCount
conflictCount
```

Permitted outcomes:

| Outcome    | Meaning                                            |
| ---------- | -------------------------------------------------- |
| `SUCCESS`  | validation and commit completed successfully       |
| `CONFLICT` | a domain conflict prevented an automatic decision  |
| `FAILED`   | a technical or formal error terminated the attempt |

A `SyncRun` that ends either through domain completion or controlled technical termination creates exactly one `SyncEvent` with the same unique `runId`. If storing it was temporarily impossible, the event is stored later. Every `SyncEvent` points through `EXECUTES` to the SYNC definition used and, read inversely through `TRIGGERS`, to exactly one `ChangeEvent`. A second completion record for the same `runId` is not permitted.

## 7. Counters

The counters must correspond to the stored relationships and changes:

```text
affectedCount   = number of distinct targets of AFFECTS
changedCount    = number of current state changes actually committed
historyCount    = number of targets of CREATES_HISTORY
correctionCount = number of targets of CREATES_CORRECTION
conflictCount   = number of RaNConflict objects assigned inversely through DETECTED_BY
```

All values are non-negative. For `SUCCESS`, the counters must exactly match the committed graph state. For `CONFLICT` or `FAILED`, they describe only conclusively determined or atomically committed results. For `SUCCESS` and `CONFLICT`, `affectedCount >= 1`. Only a `FAILED` attempt that ends before successful target resolution may have `affectedCount = 0`.

A newly detected open `RaNConflict` is connected to the final `SyncEvent` in the same atomic commit through `DETECTED_BY`. The `SyncEvent` has `outcome = CONFLICT` if at least one requested decision could not be committed because of an open conflict. The domain change request identified by a `ChangeEvent` forms exactly one atomic transaction boundary: either all domain changes belonging to this request are committed or none are. Independent changes require their own `ChangeEvent` and synchronization process.

## 8. Idempotency and Retry

1. The same `idempotencyKey` may successfully commit the same domain change at most once.
2. A new technical attempt receives a new `runId`.
3. Every attempt that actually ends creates its own `SyncEvent`.
4. A retry rechecks the expected revision.
5. If the change has already been committed successfully, the retry must create no additional `PiH`, revisions, or corrections.
6. Every completed `runId` has exactly one `SyncEvent`; each of these events is connected to the same `ChangeEvent` by exactly one append-only `TRIGGERS` edge.

## 9. Concurrency

Before the atomic commit, the current revision of every entity to be changed is checked again. If it differs from the revision read at the start, no change is committed. The attempt ends with `CONFLICT` or is started as a new attempt with a new initial revision.

For a new `Verification`, the revisions of the connected Result and SuccessCriterion are compared to `evaluatedResultRevision` and `checkedCriterionRevision` immediately before commit. Historical corrections are serialized per `PiH`; immediately before their commit, the current `HistoryView` hash is checked again. A stale `expectedHistoryViewHash` always ends with `CONFLICT`.

## 10. Failure and Recovery

The technical `SyncRun` may maintain runtime information such as `heartbeatAt`, technical status, and diagnostic data. After a crash, the implementation detects orphaned runs and terminates them in a controlled manner as failed or starts a new attempt with the same idempotency identifier.

Technical diagnostic data does not replace the final `SyncEvent`. An attempt that cannot be continued should receive a `SyncEvent` with `outcome = FAILED` after technical write capability has been restored.

## 11. Exchange Format

`JCIChangeRequest` and `JCISyncResult` use the exchange format defined in section 12.6 of [`JCI_CONTEXT.md`](JCI_CONTEXT.md), incompatibly refined from 1.0, with `schemaVersion = "1.1"`. The binding JSON Schemas are stored under `docs/schemas/`. Before any graph change, a SyncRun rejects documents with an unknown `schemaVersion`, additional disallowed fields, or invalid content.

An accepted `JCIChangeRequest` contains at least `requestId`, `idempotencyKey`, `requestedAt`, `requestedRevision`, `changeType`, `target`, `requestedByRoleAssignmentId`, and `reason`. When stored, the following mappings apply:

```text
ChangeEvent.id                = requestId
ChangeEvent.idempotencyKey    = idempotencyKey
ChangeEvent.targetEntityId    = target.id
ChangeEvent.targetEntityType  = target.entityType
ChangeEvent.requestedRevision = requestedRevision
```

For `CREATED`, `requestedRevision = null`; for every other change type, it is a positive integer. General changes use at least one operation from `ADD | REPLACE | REMOVE | CONNECT | DISCONNECT`.

`HISTORICAL_CORRECTION` uses no generic `operations` but exactly one structured payload:

```text
historicalCorrection = {
  correctionType,
  reason,
  valueSchemaVersion,
  expectedHistoryViewHash,
  correctedFields[],
  previousValue,
  correctedValue
}
```

`correctedFields` is unique and lexicographically sorted. `previousValue` and `correctedValue` have exactly the same key set. Through `target`, the request addresses the same `PiH` that is connected through `TARGETS_HISTORY` in the graph.

In addition to `requestId` and `syncEventId`, a `JCISyncResult` requires `runId`, `outcome`, `completedAt`, all five counters, and lists of affected entities, conflicts, and errors. For `SUCCESS` or `CONFLICT`, `affectedCount >= 1`; only an early `FAILED` before target resolution permits a value of `0`.

**Short example:** A `CONNECT` may contain only a cataloged relationship type, direction, and counterpart entity ID. An unknown `LINKS_TO` is rejected and is not interpreted as a new edge.

## 12. Initial Bootstrap

The initial bootstrap is not a `SyncRun`, change request, or import. It solves the trust-root problem of a completely empty graph exactly once.

1. Before it begins, the graph must be completely empty.
2. In a single atomic transaction, create one `RoFOrg`, one `RoFTeam`, one technical `RoFTeamMember`, one `RoFRole`, exactly one root `RoleAssignment` with `bootstrapKey = "ROOT"`, one `SYNC` definition, and all required RoF relationships.
3. All six bootstrap entities directly receive `status = ACTIVE`, `revision = 1`, and the same value for `createdAt` and `updatedAt`. Any `validFrom` values on the types and relationships equal the same bootstrap timestamp. This is the only exception to the regular `DRAFT` start.
4. Only the root `RoleAssignment` permanently has no `CREATED_BY`. Every other bootstrap entity has exactly one `CREATED_BY` relationship to the root `RoleAssignment`.
5. The bootstrap creates no `ChangeEvent`, technical `SyncRun`, `SyncEvent`, or `PiH`.
6. Before commit, validate uniqueness of the trust root, completeness of the minimal graph, `ACTIVE` status of all six entities, and executability of the SYNC definition. On any error, roll everything back.
7. After a successful commit, repetition and a second root `RoleAssignment` are prohibited. Every subsequent change uses only the normal SYNC process.
8. Imported entities without complete creation provenance remain `DRAFT`; an import cannot claim the bootstrap exception.

**Short example:** The deployment creates the organization, administration team, technical member, role, root assignment, and active SYNC definition together. The root `RoleAssignment` then requests the first regular `CREATED` process.
