# JCI-SYNC specification

## 1. Status and purpose

This document describes the technology-independent process of `SYNC`. The technical meaning depends on [JCI_CONTEXT.md](JCI_CONTEXT.md), the types on [JCI_ONTOLOGY.md](JCI_ONTOLOGY.md) and the valid graph states on [JCI_GRAPH_RULES.md](JCI_GRAPH_RULES.md).

## 2. Terms

```text
SYNC      = stored and historizable definition of the synchronization logic
SyncRun   = mutable technical state during an execution attempt
SyncEvent = immutable domain record after completion or termination
```

`SyncRun` is not a `JCIEntity`, not a `GraphObject` and not a JCI core element. The implementation may store it in a runtime, queue, or protocol structure. In the technical JCI graph it is not created as an intermediate node.

## 3. Binding context

```text
historisierbare JCIEntity ── CHANGED_BY ──► ChangeEvent
ChangeEvent ── startet ──► SyncRun (technisch)
SyncRun ── verwendet ──► SYNC
SyncRun ── completion or controlled termination ──► SyncEvent

ChangeEvent ── TRIGGERS ──► SyncEvent
SyncEvent ── EXECUTES ──► SYNC
SyncEvent ── AFFECTS ──► JCIEntity
SyncEvent ── CREATES_HISTORY ──► PiH
historisierbare JCIEntity ── HAS_HISTORICAL_STATE ──► PiH
SyncEvent ── CREATES_CORRECTION ──► HistoricalCorrection
HistoricalCorrection ── CORRECTS ──► PiH
```

The saved edges represent the final technical result. The technical arrows for `SyncRun` are process steps and not graph relationships.

## 4. Inputs of a SyncRun

A technical `SyncRun` requires at least:

| Input | Meaning |
| ------------------- | ------------------------------------------- |
| `runId` | unique technical run identifier |
| `idempotencyKey` | Identification of the functional change order |
| `changeEventId` | triggering `ChangeEvent` |
| `syncDefinitionId` | active `SYNC` definition to use |
| `startedAt` | Start of the experiment |
| `requestedRevision` | expected revision of the source entity |

The `ChangeEvent` has exactly one `REQUESTED_BY` relationship to a `RoleAssignment`. Optional proofs are connected to `Evidence` via `USES_EVIDENCE`.

## 5. Process

### 5.1 Acceptance

1. Verify that `ChangeEvent`, source entity and SYNC definition exist.
2. Verify that `REQUESTED_BY` exists and that the role activation is valid at the time.
3. Check whether `idempotencyKey` has already been processed successfully.
4. Check whether `requestedRevision` corresponds to the current revision.
5. Start technical `SyncRun` with state `RUNNING`.

### 5.2 Determining who is affected

1. Start at the entity that was immediately changed.
2. Traverse stored relationships according to ontology and graph rules.
3. Record direct and indirect impact separately.
4. Mark already visited entity and relationship path combinations to end cycles.
5. Do not treat concern alone as a change.

When a change is made to a Task, `SYNC` traverses at least:

- the immediately changed Task,
- its direct and all higher-level tasks,
- its direct and all subordinate tasks,
- its requirements about `DEPENDS_ON`,
- all tasks dependent on it via the inverse reading of `DEPENDS_ON`,
- all `PiF1o` affected by this,
- their success criteria and current verifications,
- responsible teams, executing RoleAssignments, used ERoFObjects and relevant `RaN`.

Because `DEPENDS_ON` is allowed to cross PiF1o boundaries, a Task change can affect multiple operational target states.

#### 5.2.1 Binding traversal matrix

The following matrix defines the minimum technical traversal. “Upward” means the WHY path to the parent future and to `CiV`; “Downward” refers to contributing future elements up to operational implementation. Inverse readings use the same stored edge in the opposite direction.

| Changed type | Check directly | Follow up indirectly |
| -------------- | ------------- | ------------------------ |
| `CiV` | associated `PiF2`, context-giving `PiH`, applicable `RaN` | downwards over all future levels to tasks, Result, Verification, RoF and ERoF |
| `PiF2` | justifying `CiV`, contributing `PiF1s`, `RaN` | downwards to `PiF1o` and operational graph objects |
| `PiF1s` | Target `PiF2`, contributing `PiF1t`, `RaN` | upwards to `CiV`, downwards to operational graph objects |
| `PiF1t` | Target `PiF1s`, contributing `PiF1o`, `RaN` | upwards to `CiV`, downwards to Tasks and Testing |
| `PiF1o` | Target-`PiF1t`, Criteria, Accountable, All Tasks, `RaN` | full WHY path, Task graph, results, verifications, teams, roles and ERoF |
| `Task` | Parent, Subtasks, Prerequisites, Dependent Tasks, PiF1o, Team, Executors, ERoFObjects, Results, `RaN` | all resulting Task and PiF1o graphs as well as their future and audit trails |
| `SuccessCriterion` | associated `PiF1o`, checking current verifications, `RaN` | Verification results and tasks; then PiF1o aggregation and future chain |
| `Result` | generating Task, current and superseded verifications, `RaN` | PiF1o, Criteria, Task Graph and Higher Future Levels |
| `Verification` | Result, criterion, predecessor/successor, Evidence | generating Task, PiF1o, all criteria and higher future levels |
| `Evidence` | all incoming `USES_EVIDENCE`, `RaN` | their respective professional target paths; Evidence itself does not decide status |
| `RaN` | `GOVERNS`, `APPLIES_IN`, open conflicts | all regulated goals and their dependent paths according to this matrix |
| `RaNConflict` | Conflict rules, affected entities, detecting SyncEvent, resolution references | upon resolution, fully re-examine all affected entities and rules |
| `RoFOrg` | Teams, organizational relationships, own ERoFObjects, `RaN` | Members, role activations, tasks, PiF1o and foreign organization page |
| `RoFOrgRelationship` | both organizations, representing RoleAssignments, `RaN` | Teams, members, ERoF and, for `SUBSIDIARY`, the entire ancestor/descendant structure |
| `RoFTeam` | Organization, members, role assignments, responsible tasks, `RaN` | PiF1o, Task-Graph, ERoFObjects and organizational relationships of those involved |
| `RoFTeamMember` | Teams, roles, assignments, accountable PiF1o, `RaN` | executed tasks, ERoFObjects, organizations and future paths |
| `RoFRole` | owning members, activating assignments, `RaN` | Teams, tasks, ERoFObjects and affected organizations |
| `RoleAssignment` | Member, Team, Role, Tasks, ERoFObjects, Organizational Representations, `RaN` | Organization, PiF1o, Task graph and environment of all direct uses |
| `ERoFObject` | Assignments and tasks to use, owner, `RaN` | Teams, members, organizations, PiF1o and future paths of the tasks |
| `SYNC` | SyncEvents to be used and valid predecessor definition | the new definition is checked against the previously active definition; no retroactive changes to old SyncEvents |
| `ChangeEvent` | Output entity, requester, Evidence, triggered SyncEvents | only within the existing change process; no recursive ChangeEvent |
| `SyncEvent` | ChangeEvent, SYNC definition executed, entities affected, history generated/fixes/conflicts | unchanging; just check the consistency of its saved references |
| `PiH` | original entity, generating SyncEvent, corrections, context usage | unchanging; Treat deviations exclusively as HistoricalCorrection |
| `HistoricalCorrection` | PiH, ChangeEvent, SyncEvent, corrector, Evidence, predecessor/successor | unchanging; treat a current model correction as a separate process |

When a relationship changes, `SYNC` starts at both endpoints and uses their matrix row for both. For `REPLACED_BY`, `SUPERSEDES`, `DEPENDS_ON`, `DECOMPOSES_INTO`, `CONTRIBUTES_TO` and `SUBSIDIARY`, the respective chain is traversed to its end and checked for cycles.

An applied relationship change increases the revision of both pre-existing mutable endpoints and creates a `PiH` for both. A newly created endpoint in the same order starts with revision `1` and does not yet receive `PiH`. Derived subsequent changes remain in the same SyncRun and do not create another `ChangeEvent`.

The traversal performs a visit set `entityId`, read `revision`, relationship type and direction. An entry that has already been visited will not be expanded again. Technical page sizes may divide up the reading, but never shorten the technical result set. If a technical limit is reached and the complete quantity cannot be determined with certainty, the experiment ends with `FAILED`; no technical partial changes will be adopted.

**Short example:** When Anna's `RoleAssignment` is terminated, SYNC checks membership, role and team, all tasks she has executed and environmental objects used. Through the tasks, SYNC reaches the affected `PiF1o` and checks whether execution, success criteria and higher future states are still valid.

### 5.3 Exam

Before each technical evaluation, `SYNC` checks the status transition against section 2.2.4 of `JCI_CONTEXT.md`. A transition not listed ends with `outcome = CONFLICT`; the current state remains unchanged. Terminal states will not be reopened. A continuation is created as a new entity.

Before activating or completing an atomic task, `SYNC` also checks traceability: The WHY path must lead to at least one `CiV` via `PiF1o`, `PiF1t`, `PiF1s` and `PiF2`. The WHO path must clearly identify executing `RoleAssignment`, member, role, responsible team and organization. A missing mandatory path prevents the status change.

For `changeType = REPLACED`, `SYNC` checks that exactly one successor of the same type is specified via `REPLACED_BY`. For all other statuses, the entity being changed must not have an outgoing `REPLACED_BY` relationship. Self-references and cycles are rejected.

Process artifacts do not create a recursive chain of events. `ChangeEvent`, `SyncEvent`, `PiH`, `HistoricalCorrection` and an open `RaNConflict` detected during the run are created in the existing change process. `SYNC` does not start another `SyncRun` for its own generation.

**Example:** A `COMPLETED` Task may not be reset to `ACTIVE`. If further work is required, a new Task is created and mapped to a `PiF1o` through the regular JCI path.

For every possible change, at least the following are checked:

- permitted source and target types,
- cardinalities,
- status transition,
- current revision,
- relevant `RaN`,
- role and team context,
- temporal coverage of team membership, role ownership and role activation,
- organizational ownership and environmental perspective,
- personal ERoF use,
- Organization rules including `SUBSIDIARY` cycle freedom,
- immutable entity types,
- required Evidence and responsibility,
- Task type, Task hierarchy and cycle freedom,
- Task dependencies and their cycle freedom,
- type-dependent execution, environment and result rules,
- Applicability, compatibility and priority of all relevant `RaN`.

Semantics that cannot be clearly decided and contradictory `RaN` lead to a conflict. `SYNC` she doesn't decide silently.

### 5.3.1 Evaluation of success criteria

If a `Verification` is completed or replaced, `SYNC` also carries out:

1. Check that `EVALUATES` refers to exactly one `Result` and `CHECKS` to exactly one `SuccessCriterion`.
2. For `SUPERSEDES`, check that the predecessor and successor evaluate the same Result and check the same criterion.
3. Determine all completed, unreplaced verifications of the affected criterion.
4. For each Verification, check that the measured value, `measurementType`, `operator`, `targetValue` and optional unit match reproducibly; otherwise the Verification is `INCONCLUSIVE`.
5. For `evaluationMode = ALL`, only rate the criterion as fulfilled if at least one current Verification exists and all are `VALID`.
6. For `evaluationMode = ANY`, rate the criterion as met as soon as at least one current Verification is `VALID`.
7. Treat `INVALID`, `INCONCLUSIVE` and missing current verifications as non-fulfilling according to the graph rules.
8. Aggregate all `REQUIRED` criteria for the associated `PiF1o`.
9. Only consider verifications whose results come from tasks of this `PiF1o`.
10. Prepare the status change to `ACHIEVED` only if at least one mandatory criterion is present, every mandatory criterion is met, all assigned tasks `COMPLETED`, all Task dependencies are met, and there is no model or `RaN` violation.

`OPTIONAL` criteria are documented in the result, but do not block `ACHIEVED`. If the decision is not clear, the status remains unchanged and the attempt is documented `CONFLICT`.

### 5.3.2 Evaluation of Task status

When a Task change occurs, `SYNC` first evaluates the atomic tasks, then the Task hierarchy from bottom to top and finally the affected `PiF1o`:

1. For each `ATOMIC`-Task, determine all targets of `DEPENDS_ON`.
2. At least one prerequisite is not preparing `COMPLETED`, `BLOCKED`.
3. If all requirements are met, check execution, team and `RaN` rules and determine the requested or existing permissible status.
4. Determine the effective direct subtasks for each `COMPOSITE`-Task: A replaced subtask is only replaced by its `REPLACED_BY` successor if it is also a direct subtask of the same parent. After that the following applies: only `DRAFT` → `DRAFT`; only `COMPLETED` → `COMPLETED`; at least one `ACTIVE` or a mixture of `DRAFT` and `COMPLETED` → `ACTIVE`; without `ACTIVE`, but with at least one `BLOCKED` → `BLOCKED`.
5. Repeat the derivation up to all root tasks.
6. Then evaluate the Task degree, success criteria and other model conditions together for each affected `PiF1o`.

An incorrectly connected `REPLACED` or a still connected `REVOKED` subtask as well as a cyclic or conflicting structure result in `CONFLICT`. Every derived status change that is actually adopted creates, like any other business change, a revision and `PiH` of the superseded status.

### 5.3.3 Aggregation of higher-level future states

After each change to a future element, `SYNC` evaluates the future chain from bottom to top:

1. Determine the current directly contributing `PiF1o` for `PiF1t`, the current `PiF1t` for `PiF1s` and the current `PiF1s` for `PiF2`.
2. `REPLACED` and `REVOKED` do not count as current posts. Only consider a replacement if it contributes to the same goal.
3. Do not derive a `ACHIEVED` without at least one recent direct contribution.
4. For `contributionMode = ALL`, only prepare `ACHIEVED` if all current direct contributions are `ACHIEVED`.
5. At `contributionMode = ANY` prepare `ACHIEVED` as soon as at least one current direct post is `ACHIEVED`.
6. After each derived change, recheck the next higher level.

**Example:** Two operational states contribute to a tactical state with `contributionMode = ALL`. Only when both `PiF1o` have been reached can `SYNC` prepare the `PiF1t` as reached.

### 5.3.4 Evaluation of RaN

For each decision affected by rules, `SYNC` executes:

1. Using `governedTypes`, `scopeType` and, if applicable, `APPLIES_IN`, determine all potentially relevant active and time-valid `RaN`; Align `GOVERNS` for the current specific targets and prepare the required target edges.
2. Evaluate each normalized condition reproducibly. Uncataloged or ambiguous paths result in `UNEVALUABLE`.
3. Derive from `effect` and condition per rule `ALLOW`, `DENY` or `NO_DECISION`.
4. Treat a single rule violation as a `DENY` and block the decision without generating a `RaNConflict` alone.
5. Only compare rules with the same `decisionKey`, overlapping scope and common target for conflicting results.
6. For each actual contradiction between `ALLOW` and `DENY`, compare the priorities.
7. If there are different priorities, only give priority to the larger number in contradiction.
8. With the same highest relevant priority, prepare an open `RaNConflict` with `conflictType = PRIORITY_TIE` and a `conflictKey` derived from ChangeEvent, sorted conflict set and decision.
9. If applicability or compatibility cannot be clearly assessed, prepare an open `RaNConflict` with `conflictType = UNEVALUABLE` and the corresponding `conflictKey`.
10. Block automatic changes whose acceptance depends on the open conflict.

A lower priority `RaN` is not overridden by precedence and remains applicable for compatible and other decisions. `ruleType` is not used as a ranking.

Before creating it, `SYNC` checks whether a `RaNConflict` with the same `conflictKey` already exists for the same change order. A retry must not produce a duplicate node. Optional evidence is connected exclusively as `Evidence` nodes via `USES_EVIDENCE`.

To resolve an existing conflict, a subsequent `SyncRun` rechecks the rules connected via `CONFLICTING_RULE` and the affected entities. Only if the documented contradiction no longer exists and the attempt is successful, `SYNC` prepares `status = RESOLVED`, `resolvedAt`, `resolution`, `RESOLVED_BY` and `RESOLVED_THROUGH`. The open initial state is prepared as `PiH`.

### 5.4 Preparing the change

For each existing entity to actually change:

1. Read properties and valid relationships of the initial state completely.
2. Form this into a canonical `StateSnapshot` and sorted `RelationshipSnapshot` entries; then calculate the SHA-256-`contentHash`.
3. Prepare an immutable `PiH` with `originalEntityId`, `originalEntityType`, `originalRevision`, schema versions and the snapshots.
4. Prepare `HAS_HISTORICAL_STATE` and `CREATES_HISTORY`.
5. Prepare new current state with `revision + 1` and new `updatedAt`.

For `changeType = CREATED`, no `PiH` is prepared for the newly created entity.

### 5.5 Historical correction

For `changeType = HISTORICAL_CORRECTION`:

1. Check that the target is an existing `PiH`.
2. Check that `CORRECTED_BY` points to a valid `RoleAssignment`.
3. Check the reason, type of correction, affected fields as well as old and corrected values.
4. Check optional `Evidence` over `USES_EVIDENCE`.
5. For `SUPERSEDES`, check that both corrections affect the same `PiH` and that no cycle occurs.
6. Prepare a new immutable `HistoricalCorrection`.
7. Never change or historicize the existing `PiH`.

If there is a need for additional changes to the current model, a separate change process is created for this purpose.

### 5.6 Technical atomicity and final documentation

In `SUCCESS`, the following contents are taken together atomically:

- new current states,
- prepared `PiH`,
- prepared `HistoricalCorrection` objects,
- resolved `RaNConflict` objects,
- all associated relationships,
- the final `SyncEvent`.

For `CONFLICT` or `FAILED`, the requested technical change and all subsequent changes that have not yet been adopted are completely rolled back. For a status that is not adopted, neither a new revision nor a `PiH` arises. After the rollback, the implementation saves the final documentation with the immutable `SyncEvent` and any newly discovered `RaNConflict` objects. This documentation is part of the attempt, not the rejected technical condition.

```text
Fachliche Transaktion
├── SUCCESS  → vollständig übernehmen
├── CONFLICT → vollständig zurückrollen
└── FAILED   → vollständig zurückrollen

Abschlussdokumentation
└── always store SyncEvent after the attempt has ended
    └── record RaNConflict as needed
```

If event storage is temporarily technically impossible, a permanent obligation to catch up remains. After write capability is restored, the exact missing `SyncEvent` is saved with the same `runId`, the same `ChangeEvent`, and the same idempotency identifier. This operation must not re-execute the failed or conflicting tray change.

## 6. Generation of the SyncEvent

A `SyncEvent` is not generated at the beginning or during the experiment. It only arises when all mandatory information has been determined.

Mandatory fields:

```text
id
entityType = SyncEvent
name
createdAt
updatedAt = createdAt
revision = 1
status = RECORDED
startedAt
completedAt
outcome
affectedCount
changedCount
historyCount
correctionCount
conflictCount
```

Acceptable results:

| Result | Meaning |
| ---------- | ------------------------------------------------------------- |
| `SUCCESS` | Testing and acceptance were successfully completed |
| `CONFLICT` | technical conflict prevents an automatic decision |
| `FAILED` | technical or formal error ended the attempt |

A `SyncRun` that has been completed technically or in a controlled manner produces exactly one `SyncEvent`. If it was temporarily impossible to save, it will be rescheduled. Each `SyncEvent` refers to the SYNC definition used via `EXECUTES` and, read inversely, to exactly one `ChangeEvent` via `TRIGGERS`.

## 7. Count values

The count values ​​must correspond to the saved relationships and changes:

```text
affectedCount   = number of distinct targets of AFFECTS
changedCount    = number of current state changes actually committed
historyCount    = number of targets of CREATES_HISTORY
correctionCount = number of targets of CREATES_CORRECTION
conflictCount   = number of RaNConflict objects inversely assigned through DETECTED_BY
```

All values ​​are non-negative. With `SUCCESS`, the count values ​​must exactly match the adopted graph state. With `CONFLICT` or `FAILED` they only describe conclusively determined or atomically adopted results.

A newly discovered open `RaNConflict` is connected to the final `SyncEvent` in the same atomic takeover via `DETECTED_BY`. The `SyncEvent` receives `outcome = CONFLICT` if at least one requested decision could not be adopted due to an open conflict. The technical change order designated by a `ChangeEvent` forms exactly an atomic transaction boundary: either all of the technical changes belonging to this order are adopted or none. Independent changes require their own `ChangeEvent` and synchronization process.

## 8. Idempotence and repetition

1. The same `idempotencyKey` may only successfully adopt the same technical change at most once.
2. A new technical attempt will receive a new `runId`.
3. Each attempt that is actually completed generates its own `SyncEvent`.
4. A retry rechecks the expected revision.
5. If the change has already been successfully applied, the repetition must not produce any further `PiH`, revisions or corrections.

## 9. Parallelism

Before the atomic takeover, the current revision of each entity to be changed is checked again. If it differs from the revision read at start, no change will be adopted. The attempt ends with `CONFLICT` or is started as a new attempt with a new initial revision.

## 10. Failure and resumption

The technical `SyncRun` is allowed to keep runtime information such as `heartbeatAt`, technical status and diagnostic data. After a crash, the implementation detects orphaned runs and terminates them as failed in a controlled manner or starts a new attempt with the same idempotency identifier.

Technical diagnostic data is not a replacement for the final `SyncEvent`. An attempt that can no longer be continued should receive a `SyncEvent` with `outcome = FAILED` after the technical ability to write has been restored.

## 11. Exchange format

`JCIChangeRequest` and `JCISyncResult` use the JSON formats specified in Section 12.6 of `JCI_CONTEXT.md`. The mandatory JSON schemas are under `docs/schemas/`. A SyncRun rejects documents with unknown `schemaVersion`, additional disallowed fields or invalid operations before each graph change.

**Quick example:** A `CONNECT` can only contain one cataloged relationship type, direction and counterpart entity ID. An unknown `LINKS_TO` is rejected and not interpreted as a new edge.
