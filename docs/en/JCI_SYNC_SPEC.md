# JCI-SYNC Specification

## 1. Status and Purpose

This document describes the technology-independent process of `SYNC`. Its domain meaning is defined by [`JCI_CONTEXT.md`](JCI_CONTEXT.md), its types by [`JCI_ONTOLOGY.md`](JCI_ONTOLOGY.md), and its valid graph states by [`JCI_GRAPH_RULES.md`](JCI_GRAPH_RULES.md).

For new operations, the rule package, `ontologyVersion`, `graphRulesVersion`, `syncSpecVersion`, `snapshotSchemaVersion`, `valueSchemaVersion`, and exchange `schemaVersion` use `2.0`. JSON-LD remains `1.1`; namespace IRIs containing `/1.0#` are stable identities, not rule versions. Explicitly versioned resolvers retain readability of old profiles; existing PiH, corrections, and hashes are neither rewritten nor recalculated.

Approval-protected operations remain base requests `2.0`, but require a SYNC definition with `approvalProfileVersion = "1.0"` and a valid technical approval envelope. A missing or unknown profile fails closed.

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
ChangeEvent ── APPROVED_BY ──► RoleAssignment
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

The stored edges represent domain provenance. `APPROVED_BY` is optional for general events and occurs at least once on accepted protected requests. The technical arrows to `SyncRun` are process steps, not graph relationships; a `SyncRun` is never created as a JCI node. An accepted `ChangeEvent` may initially have no `TRIGGERS` target. Each attempt that completes or is terminated in a controlled manner appends exactly one such edge.

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

The technical request/run record also contains the complete immutable payload or a durably resolvable reference to it, run ownership with a fencing token, and the executed SYNC revision with package checksum. decisionAt and graphEpoch are added at the protected decision point and commit respectively. These technical fields do not belong to the ChangeEvent entity catalog.

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

It has exactly one `REQUESTED_BY` relationship to a `RoleAssignment`. An accepted protected request additionally has at least one `APPROVED_BY` fixed at its creation to a human role assignment; each edge stores `receiptId`, `decidedAt`, `requestHash`, and `approvalHash`. These source-owned edges must not be appended or changed later. Optional evidence is connected to `Evidence` through `USES_EVIDENCE`. Its properties are not changed after acceptance.

## 5. Process

### 5.1 Acceptance

1. Durably store the complete normalized `JCIChangeRequest`, including `operations` or `historicalCorrection`, in a technical record and immutably bind it to `requestId` and `idempotencyKey`. Reject a reused key with different content before accepting another request. An identical request already successful returns its stored result without a new run.
2. For `Task.action.RELEASE` and `Model.action.CONFIRM`, first register only a technical approval proposal. `PENDING`, `REJECTED`, and abandoned proposals create no `ChangeEvent`; an authentic refusal by a required actor is immutable for that request and cannot be replaced through escalation.
3. For a protected request, under the write gate in section 9 accept only a fully approved envelope that remains current; general acceptance of unprotected base requests `2.0` is unchanged. The `ChangeEvent`, unchanged `REQUESTED_BY`, any required `APPROVED_BY` edges, and durable scheduling of the first attempt are created atomically. Request, approval, run, and outbox records are not `JCIEntity`.
4. Acquire the same gate before authoritative reads. Recheck the base request, profile capability, hashes, receipts, identity, time, route, and RaN, as well as valid `REQUESTED_BY`, run ownership with its fencing token, idempotency state, and active SYNC definition. Technically bind the definition revision and package checksum actually used.
5. `CREATED` requires an unused target ID and `requestedRevision = null`. Historical correction requires target type PiH, revision 1, exactly one `TARGETS_HISTORY`, and no `CHANGED_BY` source. Otherwise the historizable target must provide exactly one matching `CHANGED_BY` source and still have exactly the immutably requested revision.
6. Start the scheduled `SyncRun` with a unique `runId`. A stale worker must not commit after losing its fencing token. `TRIGGERS = 0` remains valid until completion.

Failure before successful target resolution ends with FAILED; only this case permits empty AFFECTS. SUCCESS and CONFLICT document at least one actually existing or successfully created affected entity. A CREATED candidate is not stored merely to document failure.

**Short example:** The same request arrives twice. The second acceptance uses the existing request and returns its stored result after success. A new target revision under the same idempotency key is not a retry.

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

| Changed type           | Check directly                                                                                                  | Continue indirectly                                                                                                  |
| ---------------------- | --------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------- |
| `CiV`                  | three dimensions, `HELD_BY`, `INFORMED_BY`, protecting `RaN`, connected `PiF2`, context-providing `PiH`         | to source CiV, value holder, and protected PiF2; downward to every governed implementation element                   |
| `PiF2`                 | grounding `CiV`, value holder, optional accountable, protecting `RaN`, contributing `PiF1s`                     | to protected CiV; downward to `PiF1o` and every governed implementation element                                      |
| `PiF1s`                | target `PiF2`, optional accountable, contributing `PiF1t`, `RaN`                                                | upward to `CiV`, downward to operational graph objects                                                               |
| `PiF1t`                | target `PiF1s`, optional accountable, contributing `PiF1o`, `RaN`                                               | upward to `CiV`, downward to Tasks and verification                                                                  |
| `PiF1o`                | target `PiF1t`, criteria, accountable member, all Tasks, `RaN`                                                  | complete WHY path, Task graph, Results, Verifications, teams, roles, and ERoF                                        |
| `Task`                 | parent, subtasks, prerequisites, dependent Tasks, PiF1o, team, executors, ERoFObjects, Results, `RaN`           | all Task and PiF1o graphs reached from them, including their future and verification paths                           |
| `SuccessCriterion`     | associated `PiF1o`, checking applicable current Verifications, `RaN`                                            | Results and Tasks of the Verifications; then PiF1o aggregation and future chain                                      |
| `Result`               | producing Task, current and superseded Verifications, `RaN`                                                     | PiF1o, criteria, Task graph, and higher future levels                                                                |
| `Verification`         | Result, criterion, their bound revisions, predecessor/successor, Evidence                                       | producing Task, PiF1o, all applicable current Verifications, criteria, and higher future levels                      |
| `Evidence`             | all incoming `USES_EVIDENCE`, `RaN`                                                                             | their respective domain target paths; Evidence itself determines no status                                           |
| `RaN`                  | `PROTECTS`, `GOVERNS`, `APPLIES_IN`, optional `approvalPolicy`, open conflicts                                  | all protected CiV and PiF2, all governed implementation elements, and their dependent paths according to this matrix |
| `RaNConflict`          | conflicting rules, affected entities, detecting SyncEvent, resolution references                                | upon resolution, fully recheck all affected entities and rules                                                       |
| `RoFOrg`               | teams, organization relationships, owned ERoFObjects, `RaN`                                                     | members, role assignments, Tasks, PiF1o, and the other organization side                                             |
| `RoFOrgRelationship`   | both organizations, representing RoleAssignments, `RaN`                                                         | teams, members, ERoF and, for `SUBSIDIARY`, the complete ancestor/descendant structure                               |
| `RoFTeam`              | organization, members, RoleAssignments, responsible Tasks, `RaN`                                                | PiF1o, Task graph, ERoFObjects, and organization relationships of the participants                                   |
| `RoFTeamMember`        | teams, roles, assignments, accountable `PiF2`/`PiF1s`/`PiF1t`/`PiF1o`, `RaN`                                    | executed Tasks, ERoFObjects, organizations, and future paths                                                         |
| `RoFRole`              | owning members, activating assignments, `RaN`                                                                   | teams, Tasks, ERoFObjects, and affected organizations                                                                |
| `RoleAssignment`       | member, team, role, Tasks, ERoFObjects, organization representations, `RaN`                                     | organization, PiF1o, Task graph, and environment of all direct uses                                                  |
| `ERoFObject`           | using assignments and Tasks, owners, `RaN`                                                                      | teams, members, organizations, PiF1o, and future paths of the Tasks                                                  |
| `SYNC`                 | using SyncEvents and valid predecessor definition                                                               | the new definition is checked by the previously active definition; no retroactive change to old SyncEvents           |
| `ChangeEvent`          | target coordinates, optional `CHANGED_BY` source, `TARGETS_HISTORY`, requester, approvers, Evidence, SyncEvents | only within the existing change process; no recursive ChangeEvent                                                    |
| `SyncEvent`            | ChangeEvent, executed SYNC definition, affected entities, created history/corrections/conflicts                 | immutable; check only the consistency of its stored references                                                       |
| `PiH`                  | original entity, creating SyncEvent, corrections, context use                                                   | immutable; treat deviations exclusively as HistoricalCorrection                                                      |
| `HistoricalCorrection` | PiH, ChangeEvent, SyncEvent, corrector, Evidence, `baseHistoryViewHash`, predecessor/successor                  | immutable; determine the effective `HistoryView` and treat a current model correction as a separate process          |

When a relationship changes, `SYNC` starts at both endpoints and uses the matrix row for each. For `REPLACED_BY`, `SUPERSEDES`, `DEPENDS_ON`, `DECOMPOSES_INTO`, `CONTRIBUTES_TO`, and `SUBSIDIARY`, the respective chain is traversed to its end and checked for cycles.

Revision and history follow versioned revision ownership in [`JCI_CONTEXT.md`](JCI_CONTEXT.md). New Verification, HistoricalCorrection, ChangeEvent, and SyncEvent references do not change existing targets merely by referring to them. TRIGGERS, CHANGED_BY, and HAS_HISTORICAL_STATE do not cause history recursion. CREATED_BY belongs to the source creation state; a permitted addition to an existing imported draft changes only that draft. Resolving a RaNConflict revisions the conflict exactly once, not its referenced rules or actors. PiH PROVIDES_CONTEXT_TO CiV belongs to the CiV context state. Both mutable endpoints remain owners for the other explicitly cataloged domain structure relationships.

Each existing owner with an actual change receives exactly one new revision and one PiH per request; new entities start at revision 1. New verification or event references do not authorize changing completed document content. All relationships remain part of impact and concurrency checks, including those without domain revisions. Follow-up changes remain in the same SyncRun without another ChangeEvent.

The traversal maintains a visited set of `entityId`, read `revision`, relationship type, and direction. An already visited entry is not expanded again. Technical page sizes may split reading into parts but must never truncate the domain result set. If a technical limit is reached and the complete set cannot be determined safely, the attempt ends with `FAILED`; no partial domain changes are committed.

**Short example:** When Anna’s `RoleAssignment` ends, SYNC checks membership, role, team, every Task it executes, and every environmental object it uses. Through the Tasks, SYNC reaches the affected `PiF1o` and checks whether execution, success criteria, and higher future states remain valid.

### 5.3 Validation

Before any domain evaluation, `SYNC` checks the status transition against section 2.2.4 of [`JCI_CONTEXT.md`](JCI_CONTEXT.md). A transition not listed there ends with `outcome = CONFLICT`; the current state remains unchanged. Terminal states are not reopened. A continuation is created as a new entity.

Before activating or completing an atomic Task, `SYNC` also checks traceability: the WHY path must lead through `PiF1o`, `PiF1t`, `PiF1s`, and `PiF2` to at least one `CiV`. The WHO path must unambiguously identify the executing `RoleAssignment`, member, role, responsible team, and organization. A missing mandatory path prevents the status transition.

Whenever a CiV is created or changed, `SYNC` validates that it describes exactly one value through the three non-empty dimensions `notCiV`, `selfCiV`, and `toServeCiV`, has exactly one permitted `HELD_BY` value holder, and does not use a technical member as personal scope. `INFORMED_BY` must not form a self-relationship and is never inferred from names, memberships, or affiliations. For every connected `PiF2`, all directly grounding CiV must have the same value holder. A value decision or adoption of dimensions requires human confirmation and is never created by `SYNC` itself.

Whenever a RaN is created, activated, or changed, `SYNC` validates `PROTECTS` separately from `GOVERNS`: an active RaN protects at least one CiV and one PiF2, governs at least one permitted implementation element, and satisfies bidirectional coherence through `INSCRIBES_PURPOSE_IN`. Protection targets must be organizationally compatible with `scopeType`, `APPLIES_IN`, and, for `ENTITY`, the WHY paths of the governed targets. `GOVERNS` to `PiF2` is prohibited. `SYNC` validates human-approved protection edges but neither creates nor guesses them itself; the technical requester need not be the approving human.

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

T_current(G) contains all Tasks directly assigned to PiF1o G except REPLACED and REVOKED; K_current(G) contains its criteria with the same status exclusion. COMPLETED Tasks remain current contributions. Historical assignments are not deleted. A current REQUIRED criterion in DRAFT blocks achievement.

1. A new Verification connects exactly one COMPLETED Result and one ACTIVE SuccessCriterion of the same PiF1o. For current aggregation, the producing Task must belong to T_current(G); Results of retired Tasks are not adopted automatically.
2. Bind Result and criterion revisions from the finally protected candidate state as positive evaluatedResultRevision and checkedCriterionRevision. EVALUATES and CHECKS do not change these revisions. A genuine change of a verification target in the same request requires evaluating its final state; otherwise CONFLICT.
3. Allow at most one non-superseded Verification for the same Result, criterion, and pair of revisions. A further verification must supersede the existing one through SUPERSEDES. Succession remains unbranched, forward in time, revision-monotonic, and limited to the same Result/criterion.
4. Recheck target revisions and the complete current verification set under the write gate before commit. Supersession may change this set without a new target revision.
5. Aggregate only COMPLETED, non-superseded verifications of current Results/criteria with matching revisions. Earlier verifications remain immutable facts; later criterion revocation makes them inapplicable and is no reason to delete historical documentation.
6. Measured value, measurementType, operator, targetValue, and optional unit must agree reproducibly under the method; otherwise INCONCLUSIVE.
7. ALL requires at least one applicable verification and exclusively VALID outcomes; ANY requires at least one applicable VALID verification. Missing, stale, INVALID, or INCONCLUSIVE verifications do not fulfill the criterion; for ALL, every applicable non-valid outcome prevents fulfillment.
8. Prepare ACHIEVED only if T_current(G) is non-empty and contains only COMPLETED Tasks with fulfilled prerequisites, at least one current REQUIRED criterion exists, all current required criteria are ACTIVE and fulfilled, and WHY, WHO, model, and RaN rules hold. OPTIONAL is documented but does not block.
9. SYNC must not revoke Tasks or required criteria itself to enable success. Requested scope changes need valid replacement scope or another permitted target status; empty current scope of a still active goal produces CONFLICT.

Earlier work is reused only through explicitly adopted current work with traceable Evidence; the old PRODUCES reference is not reassigned. ACHIEVED remains terminal.

**Short example:** T1 remains connected to G as REPLACED; its explicitly connected successor T2 is COMPLETED. T1 does not block G. A new Verification of T2 binds criterion revision 2 without increasing it through CHECKS. Only a genuine criterion change to 3 makes the verification stale.

### 5.3.2 Evaluation of Task Status

SYNC derives a completion graph from the complete candidate: COMPOSITE → current direct child and Task → DEPENDS_ON prerequisite both mean the source cannot complete before the target. All edges created in the request and all prerequisites reached across PiF1o boundaries are considered jointly. Replaced or revoked prerequisites remain visible and unmet; they are not automatically redirected to successors.

1. Continue checking the stored hierarchy, dependencies, and succession chains separately. Additionally report every mixed cycle as CONFLICT before commit, including the complete path and original relationship types.
2. Current direct Composite children exclude REPLACED and REVOKED. A current Composite needs at least one current child. A replacement must explicitly belong to the same PiF1o and, where applicable, current parent. Retiring a parent does not automatically revoke current descendants; unresolved subtrees produce CONFLICT.
3. Evaluate the joint completion graph with prerequisites first. Atomic and Composite Tasks are ordered together; evaluating all atomic Tasks before all Composites is prohibited.
4. Check each current Task's own DEPENDS_ON. An unmet own Composite prerequisite makes its release status BLOCKED and prevents completion and takes precedence over child aggregation. It is not automatically inherited by descendants.
5. DRAFT remains a draft without explicit regular release. DRAFT → BLOCKED requires that release, complete activation checks, and own or aggregated blocking under canonical section 9.4.2. At explicit composite release, the same prerequisite and child-blocking priority determines `ACTIVE` or `BLOCKED`; even if every child is completed, release first produces `ACTIVE`. Completion requires a later evaluation of that released state. Scope reduction is not release. DRAFT → COMPLETED is prohibited; even a draft with only completed children needs its own regular release process before later completion.
6. For released Composites in ACTIVE or BLOCKED, apply the ordered table. Child scope and status preconditions must already be valid.
7. Then jointly validate current PiF1o scopes, criteria, and higher future levels. Terminal Tasks are not reopened; reject a candidate contradicting their recorded completion.

| Condition                                                                   | Derived status |
| --------------------------------------------------------------------------- | -------------- |
| At least one own prerequisite unmet                                         | BLOCKED        |
| Own prerequisites fulfilled, all current children COMPLETED                 | COMPLETED      |
| Own prerequisites fulfilled, at least one current child ACTIVE              | ACTIVE         |
| Own prerequisites fulfilled, no ACTIVE child, at least one BLOCKED child    | BLOCKED        |
| Own prerequisites fulfilled, only DRAFT or a mixture of DRAFT and COMPLETED | ACTIVE         |

A released Composite never returns to DRAFT. Atomic Tasks still require execution, team, RaN, and confirmed completion conditions. Every actually committed status transition is historicized exactly once.

**Short example:** C contains A and A depends on C: C → A → C is a mixed cycle. If all children of C are completed but its own prerequisite B is open, C stays BLOCKED.

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

### 5.3.5 Evaluation of protected approvals

1. For `Task.action.RELEASE` and `Model.action.CONFIRM`, validate capability `approvalProfileVersion = "1.0"`, the exact base request `2.0`, `requestHash`, `contextHash`, and every receipt. Each receipt binds both hashes, `decidedAt`, `validUntil`, outcome, role assignment, member, and an attestation verified by the trusted adapter; `decidedAt <= decisionAt < validUntil` applies. At most one receipt per role assignment is permitted.
2. Derive authority only from an active, time- and scope-valid `PERMIT` RaN with matching `decisionKey`, satisfied condition, and `approvalPolicy`. The policy has `profileVersion = "1.0"`, nonempty unique `roleIds`, and either `mode = ACCOUNTABLE_CHAIN` with nonempty unique `levels` from `PiF1o`, `PiF1t`, `PiF1s`, `PiF2`, or `mode = VALUE_SCOPE` without levels. Missing `PERMIT` is no permission; `DENY`, `UNEVALUABLE`, conflict, and an authentic `REJECTED` outcome block without escalation.
3. Only direct scalar two-segment paths `target.*`, `actor.*`, and `request.*` are executable in this profile. `target` identifies the candidate Task for release and the approving role assignment for model confirmation. Types are not coerced; unsupported paths, operators, or types yield `UNEVALUABLE`, and `ANY` still evaluates every clause.
4. For Task release, start at exactly one directly assigned `PiF1o` and inspect every current `CONTRIBUTES_TO` branch. Its `ACCOUNTABLE_MEMBER` is the first anchor checked; a technical member may be traversed but cannot approve. Only if explicit human authority alone is missing may routing escalate through `PiF1t`, `PiF1s`, and `PiF2`; each branch ends at its first authorized accountability proven `HUMAN`. Every branch must be approved independently, including under `contributionMode = ANY`. Missing or ambiguous accountability fails closed.
5. For model confirmation, derive every affected previous and candidate value holder for changes to CiV, `HELD_BY`, `INFORMED_BY`, `INSCRIBES_PURPOSE_IN`, `PROTECTS`, policies, and accountability. A `VALUE_SCOPE` permission applies only to holders derived from the same RaN's `PROTECTS`-linked CiV/PiF2 and only to an actor within the matching holder scope; `GLOBAL` does not extend that mandate. Policies valid before the request govern their own change so the candidate cannot authorize itself.
6. Immediately before commit, hash and validate the complete current domain basis again. A changed revision, graph, policy, route, scope, or candidate invalidates previous receipts. Only a complete set of `APPROVED` receipts permits the attempt; approval alone transitions a Task only after all model checks to `ACTIVE` or `BLOCKED`, never to `COMPLETED` and never a future element to `ACHIEVED`. On `CONFLICT` or `FAILED`, no domain delta is applied; the already accepted event and its immutable approval and attempt provenance remain.

### 5.4 Preparing the Change

1. Compare the complete validated candidate with the initial state; deduplicate entities with actual property or owned-relationship changes. Pure new verification, audit, and history references do not change their targets.
2. For each existing mutable owner, read its previous domain state and the relationships assigned by its snapshot profile. New PiH use `snapshotSchemaVersion = "2.0"`; other objects' later verification references do not retroactively belong to that state.
3. Form StateSnapshot and sorted RelationshipSnapshot entries under canonical profile 2.0 and calculate SHA-256 contentHash. Prepare exactly one PiH, HAS_HISTORICAL_STATE, and CREATES_HISTORY per existing entity actually changed.
4. Prepare the current state with exactly revision + 1 and a new updatedAt. Existing PiH and hashes remain unchanged and are read under their own old profile.
5. A valid request with no actual change may document SUCCESS with changedCount = historyCount = 0. Audit references create no fictitious history; the technical success record nevertheless marks the request processed.

For CREATED, first form only a candidate. Only SUCCESS atomically creates the target with revision 1, CREATED_BY, and exactly one CHANGED_BY edge to the existing ChangeEvent. The new entity receives no PiH; existing owners actually changed may receive their own PiH. CONFLICT or FAILED creates neither the target nor its creation references.

### 5.5 Historical Correction

1. Validate the existing target PiH, requestedRevision = 1, exactly one matching TARGETS_HISTORY, and no CHANGED_BY source. Exchange schema and new valueSchemaVersion use 2.0; only the structured historicalCorrection payload is permitted.
2. Validate valid CORRECTED_BY, reason, and optional Evidence. Use explicitly registered resolvers for older snapshot/correction profiles. Ambiguous legacy paths produce CONFLICT; no automatic reinterpretation or recalculation of stored hashes.
3. relationshipData remains a list. For addressing only, build a map keyed by direction + ":" + relationshipType + ":" + canonicalUUID(otherEntityId). Duplicate keys are invalid.
4. Allow only the path forms below. Property corrections replace a complete TypedValue property; descent into value, array indices, wildcards, root replacement, and array appends are prohibited. The referenced snapshot profile defines permitted properties. Identity, original revision, and relationship identity components are not reinterpreted at the same address.
5. Split JSON Pointers into segments, decode ~1 and ~0 under RFC 6901, and require canonical re-encoding. correctedFields is unique, lexicographically sorted, and free of equal or nested paths within the request. previousValue and correctedValue have exactly the same key set.
6. Build HistoryView from the immutable PiH and absolute correctedValue overlays of non-superseded corrections. Earlier previousValue entries are not checked again against the original PiH on each rebuild.
7. Calculate SHA-256 uniformly over effective {stateData, relationshipData} under canonical profile 2.0. relationshipData is sorted by relationshipType, direction, and otherEntityId. The technical address map, PiH ID, and correction IDs are excluded from the hash input. Compare with expectedHistoryViewHash.
8. Validate existence and previous effective value for each new path. ADDITION requires actual absence and typed NULL as previousValue; existing NULL is not absent. CORRECTION and CLARIFICATION require existence. NULL is not a deletion command.
9. Paths overlap when either decoded segment sequence is a prefix of the other, including equality. Without overlap a correction may coexist. If exactly one active correction is affected, completely supersede exactly it through SUPERSEDES: retain all previous canonical paths and still-valid values. Additional paths must overlap neither each other nor another active correction. Multiple overlaps or silent granularity changes produce CONFLICT.
10. Validate correction chains for the same PiH, forward time, and freedom from cycles. Under the common write gate immediately before commit, recheck view, hash, previous values, existence, paths, and supersession. A stale hash creates no correction.
11. Create a new immutable HistoricalCorrection with baseHistoryViewHash = expectedHistoryViewHash and matching CORRECTS, CAUSED_BY, and CREATES_CORRECTION. PiH remains unchanged; current-model changes remain a separate request.

```text
/stateData/properties/<property>
/relationshipData/<relationship-key>
/relationshipData/<relationship-key>/properties/<property>
```

A complete relationship entry is transferred as TypedValue OBJECT. Direction, type, and other entity ID must match its address. The stored relationship list does not become a map.

Profile 2.0 uses UTF-8 without BOM or extra whitespace, object keys sorted by Unicode code point, and JSON string escaping without blanket ASCII escaping. INTEGER remains exact and unbounded; binary floating-point values are prohibited even within OBJECT/ARRAY. DECIMAL is a canonical decimal string without exponent, leading zeros, unnecessary trailing fractional zeros, or -0; nested decimal values are represented as TypedValue DECIMAL. The resolver follows section 2.2.9 of [`JCI_CONTEXT.md`](JCI_CONTEXT.md) and shared hash test vectors.

**Short example:** /stateData/properties/name and /stateData/properties/nameLong are disjoint. A complete relationship entry overlaps with its /properties/validUntil. After complete supersession of an earlier addition, its absolutely corrected value remains in HistoryView.

### 5.6 Domain Atomicity and Completion Documentation

On `SUCCESS`, the following contents are committed together atomically:

- new current states,
- for `CREATED`, the new target node with `revision = 1`, `CREATED_BY`, and `CHANGED_BY`,
- prepared `PiH`,
- prepared `HistoricalCorrection` objects,
- resolved `RaNConflict` objects,
- all associated relationships,
- the final `SyncEvent` with its `runId`,
- the new append-only `TRIGGERS` relationship,
- technical success record, outbox, and increased graphEpoch under section 9.

On `CONFLICT` or `FAILED`, the requested domain change and all follow-up changes not yet committed are rolled back completely. No new revision or `PiH` is created for a state that was not committed. After rollback, the implementation stores the completion documentation with the immutable `SyncEvent` and, where applicable, newly detected `RaNConflict` objects. This documentation belongs to the attempt, not to the rejected domain state.

```text
Domain transaction
├── SUCCESS  → atomically commit domain delta, SyncEvent, success record, and outbox
├── CONFLICT → roll back completely
└── FAILED   → roll back completely

Completion documentation
└── always store SyncEvent after the attempt has ended
    └── record RaNConflict where required
```

If FAILED/CONFLICT event storage is temporarily technically impossible after confirmed rollback, a durable obligation to complete it remains. After write capability has been restored, exactly the missing `SyncEvent` is stored with the same `runId`, the same `ChangeEvent`, and the same `idempotencyKey`, and `TRIGGERS` is appended once. This operation must not execute the failed or conflicting domain change again.

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

1. Durably bind the complete normalized request to its identity and idempotency key; reject reuse with different content.
2. Before another technical attempt, check under the gate whether the request has already succeeded. Then return the existing result without starting another domain execution.
3. Each actually executed and completed attempt has its own runId and exactly one immutable SyncEvent. Technical retry never changes requestedRevision in the ChangeEvent.
4. Revision conflict ends the attempt with CONFLICT. Reassessment against a different base revision requires a new request and a new ChangeEvent.
5. On SUCCESS, the success record, delta, PiH, corrections, SyncEvent, and outbox must be stored together atomically. A successful domain no-op is also marked processed.
6. If the commit outcome is unknown, first check stored success and event under the gate using the same runId. A lost response is no reason to repeat a domain change.

## 9. Concurrency

The reference uses exactly one technical write gate per shared JCI model store or database, acquired before decision-relevant reads and held until commit/rollback. It is not partitioned by RoFOrg or dynamically connected subcomponent: cross-boundary rules and dependencies share its protection boundary.

Under the gate, reread all properties, relationships, sets, and relevant absences and validate the complete candidate. This protects newly added RaN, memberships, scope changes, jointly cyclic edges, and competing capacity allocations. Every JCI write path, including bootstrap, migration, audit append, Verifications, SUPERSEDES, corrections, and recovered events, uses the same gate. Technical locks are not JCIEntity and create no domain revisions/PiH.

Before commit, choose a server-side domain decision instant and store it in the technical commit record. Finally reevaluate all temporal conditions and dependent decisions for exactly that instant, including newly applicable rules and expired roles. completedAt remains completion time. Validity is guaranteed at the decision instant, not later physical commit confirmation or external execution.

A later optimization may read a snapshot with technical graphEpoch under the gate, compute outside, and validate after reacquiring the gate. Every committed JCI write transaction increases the epoch, including purely revision-neutral verification/audit references. A mismatch discards preparation; reread without changing the requested target revision. Recheck time conditions independently of the epoch. Comparing only domain revisions or locking known entities is insufficient.

## 10. Failure and Recovery

The complete technical request/run record remains durably available. Run ownership uses a fencing token: a stale worker resuming after claim loss must not commit domain changes or completion documentation. Heartbeats may run separately; ownership changes and completion must be coordinated with the protected commit decision.

Database failures roll back the entire domain transaction. Once writing is restored, recovery first checks the actual outcome under the same gate. Existing success is not executed again. If the event is missing after the original transaction has definitively ended, recover FAILED/CONFLICT completion documentation with the same runId exactly once. SUCCESS already has its success record and SyncEvent atomically stored.

The technical outbox is stored with the completion event. Redelivery after dispatcher failure is possible; recipients need a stable deduplication key. Outbox/run records are not domain graph objects and do not change domain counters.

## 11. Exchange Format

`JCIChangeRequest` and `JCISyncResult` use the exchange format defined in section 12.6 of [`JCI_CONTEXT.md`](JCI_CONTEXT.md), incompatibly refined from 1.1, with `schemaVersion = "2.0"`. The binding JSON Schemas are stored under `docs/schemas/`. Before any graph change, a SyncRun rejects documents with an unknown `schemaVersion`, additional disallowed fields, or invalid content.

An accepted `JCIChangeRequest` contains at least `requestId`, `idempotencyKey`, `requestedAt`, `requestedRevision`, `changeType`, `target`, `requestedByRoleAssignmentId`, and `reason`. When stored, the following mappings apply:

```text
ChangeEvent.id                = requestId
ChangeEvent.idempotencyKey    = idempotencyKey
ChangeEvent.targetEntityId    = target.id
ChangeEvent.targetEntityType  = target.entityType
ChangeEvent.requestedRevision = requestedRevision
```

For `CREATED`, `requestedRevision = null`; for every other change type, it is a positive integer. General changes use at least one operation from `ADD | REPLACE | REMOVE | CONNECT | DISCONNECT`.

Before acceptance, a protected operation is wrapped by the [approval envelope](../schemas/jci-approval-envelope.schema.json); the base request remains unchanged:

```text
JCIApprovalEnvelope = {
  approvalProfileVersion: "1.0",
  decisionKey: "Task.action.RELEASE" | "Model.action.CONFIRM",
  proposal: JCIChangeRequest 2.0,
  requestHash: SHA-256,
  contextHash: SHA-256,
  receipts: ApprovalReceipt[]
}
```

`requestHash` covers the complete canonical base request without receipts. `contextHash` additionally covers profile and decision, the ordered relevant domain graph view, derived requirements and candidates, and technical enrollment authorities with permanent latches. A receipt contains `receiptId`, both hashes, `decidedAt`, `validUntil`, `outcome = APPROVED | REJECTED`, `roleAssignmentId`, `memberId`, and `attestation`; its complete canonical form yields `approvalHash`. Pending, rejected, and abandoned envelopes remain durable technical audit data outside the JCI graph. Only on complete acceptance are their approvals projected as immutable `APPROVED_BY` edges of the new `ChangeEvent`.

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

`valueSchemaVersion = "2.0"`; correctedFields is unique, lexicographically sorted, and free of segment-prefix overlaps under section 5.5. `previousValue` and `correctedValue` have exactly the same key set. Through `target`, the request addresses the same `PiH` that is connected through `TARGETS_HISTORY` in the graph.

In addition to `requestId` and `syncEventId`, a `JCISyncResult` requires `runId`, `outcome`, `completedAt`, all five counters, and lists of affected entities, conflicts, and errors. For `SUCCESS` or `CONFLICT`, `affectedCount >= 1`; only an early `FAILED` before target resolution permits a value of `0`.

**Short example:** A `CONNECT` may contain only a cataloged relationship type, direction, and counterpart entity ID. An unknown `LINKS_TO` is rejected and is not interpreted as a new edge.

## 12. Initial Bootstrap

The initial bootstrap is not a `SyncRun`, change request, or import. It solves the trust-root problem of a completely empty graph exactly once.

1. Before it begins, the domain graph must be completely empty; technical gate/run records are not JCIEntity. Bootstrap also holds the shared write gate until commit.
2. In a single atomic transaction, create one `RoFOrg`, one `RoFTeam`, one technical `RoFTeamMember`, one `RoFRole`, exactly one root `RoleAssignment` with `bootstrapKey = "ROOT"`, one `SYNC` definition, and all required RoF relationships.
3. All six bootstrap entities directly receive `status = ACTIVE`, `revision = 1`, and the same value for `createdAt` and `updatedAt`. Any `validFrom` values on the types and relationships equal the same bootstrap timestamp. This is the only exception to the regular `DRAFT` start.
4. Only the root `RoleAssignment` permanently has no `CREATED_BY`. Every other bootstrap entity has exactly one `CREATED_BY` relationship to the root `RoleAssignment`.
5. The bootstrap creates no `ChangeEvent`, technical `SyncRun`, `SyncEvent`, or `PiH`.
6. Before commit, validate uniqueness of the trust root, completeness of the minimal graph, `ACTIVE` status of all six entities, and executability of the SYNC definition. On any error, roll everything back.
7. After a successful commit, repetition and a second root `RoleAssignment` are prohibited. Every subsequent change uses only the normal SYNC process.
8. Imported entities without complete creation provenance remain `DRAFT`; an import cannot claim the bootstrap exception.
9. The technical root `RoleAssignment` gains no human approval authority. If this installation processes protected operations, its SYNC definition must explicitly enable `approvalProfileVersion = "1.0"`. Exactly configured human enrollment authority for `Model.action.CONFIRM` remains technical state and is permanently latched off per holder on the first commit of an active `VALUE_SCOPE` policy; it never applies to Task release.

**Short example:** The deployment creates the organization, administration team, technical member, role, root assignment, and active SYNC definition together. The root `RoleAssignment` then requests the first regular `CREATED` process.
