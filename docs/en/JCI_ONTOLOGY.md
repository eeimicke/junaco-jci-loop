# JCI Ontology

## 1. Status and purpose

This document translates the domain meaning from [JCI_CONTEXT.md](../JCI_CONTEXT.md) into unambiguously named entity and relationship types. `JCI_CONTEXT.md` remains the canonical domain source. If a conflict exists, the state documented there applies; the conflict must be reported before changing the model.

Cardinalities and invariants are defined in [JCI_GRAPH_RULES.md](JCI_GRAPH_RULES.md). The `SYNC` process is defined in [JCI_SYNC_SPEC.md](JCI_SYNC_SPEC.md). Database-specific labels, properties, constraints, and indexes belong in [implementations/neo4j/JCI_NEO4J_SCHEMA.md](implementations/neo4j/JCI_NEO4J_SCHEMA.md).

## 2. Abstract types

`JCIEntity` is the abstract supertype of every instance stored as a node. Its abstract subtypes are not stored as additional domain nodes:

```text
JCIEntity
├── JCIElementInstance
└── GraphObject
```

`JCIElementInstance` is a stored instance of a storable JCI core element. `GraphObject` makes its operational, organizational, verifying, or documenting application concrete.

`RoF` and `ERoF` remain core elements but are model spaces without their own nodes. `SyncRun` is exclusively technical runtime state and is neither a `JCIEntity` nor a `GraphObject`.

## 3. Concrete entity types

### 3.1 JCIElementInstance

```text
PiH
CiV
RaN
SYNC
PiF2
PiF1s
PiF1t
PiF1o
```

### 3.2 GraphObject

```text
RoFOrg
RoFOrgRelationship
RoFTeam
RoFTeamMember
RoFRole
RoleAssignment
Task
SuccessCriterion
Result
Verification
Evidence
ERoFObject
ChangeEvent
SyncEvent
RaNConflict
HistoricalCorrection
```

## 4. Common properties

Every concrete `JCIEntity` has:

| Property | Data type | Required | Rule |
|---|---|---:|---|
| `id` | UUID | yes | globally unique and immutable |
| `entityType` | Enum | yes | exactly matches the concrete entity type |
| `name` | String | yes | not empty |
| `description` | String | no | domain description |
| `createdAt` | DateTime | yes | ISO 8601 with time zone |
| `updatedAt` | DateTime | yes | not before `createdAt` |
| `revision` | Integer | yes | at least `1` |
| `status` | Enum | yes | type-specific permitted status |

`PiH`, `ChangeEvent`, `SyncEvent`, and `HistoricalCorrection` are immutable in content. For them, `revision = 1` and `updatedAt = createdAt` apply permanently. A `ChangeEvent` documents an accepted change request, whereas a `SyncEvent` documents the result of exactly one completed or controlled-aborted technical `SyncRun`. The `TRIGGERS` relationship created when the run finishes may only be appended. For a successful `CREATED`, exactly one `CHANGED_BY` relationship from the newly created entity to the existing `ChangeEvent` may additionally be established once. These provenance additions do not change any property of the `ChangeEvent`.

The following type-specific required fields apply in particular to the entity types refined here:

| Entity type | Additional required fields |
| ----------- | -------------------------- |
| `ChangeEvent` | `idempotencyKey`, `targetEntityId`, `targetEntityType`, `requestedRevision` |
| `SyncEvent` | `runId` |
| `Verification` | `evaluatedResultRevision`, `checkedCriterionRevision` |
| `HistoricalCorrection` | `baseHistoryViewHash` |

`requestedRevision` is `null` exclusively for `changeType = CREATED`; otherwise it is a positive integer. The target details of the `ChangeEvent` are immutable audit coordinates of the request and do not replace a domain relationship. `runId` identifies exactly one technical attempt. `baseHistoryViewHash` binds a historical correction to the effective historical view immediately preceding it.

Type-specific required fields and enumeration values are canonically defined in section 2.2.5 of [JCI_CONTEXT.md](../JCI_CONTEXT.md). Binding status transitions are defined in section 2.2.4. A database implementation may make them technically concrete but must not weaken or semantically reinterpret them.

Complex values exclusively use the types `TypedValue`, `StateSnapshot`, `RelationshipSnapshot`, `TypedValueMap`, `RuleExpression`, and `SyncDefinition` defined in section 2.2.7. Unstructured, implementation-dependent object content is not permitted.

## 5. Relationship catalogue

### 5.1 Purpose and future

```text
PiH PROVIDES_CONTEXT_TO CiV
CiV INSCRIBES_PURPOSE_IN PiF2
PiF1s CONTRIBUTES_TO PiF2
PiF1t CONTRIBUTES_TO PiF1s
PiF1o CONTRIBUTES_TO PiF1t
```

### 5.2 Operational implementation and verification

```text
PiF1o HAS_SUCCESS_CRITERIA SuccessCriterion
PiF1o ACCOUNTABLE_MEMBER RoFTeamMember
PiF1o DECOMPOSES_INTO Task
Task DECOMPOSES_INTO Task
Task DEPENDS_ON Task
Task RESPONSIBLE_TEAM RoFTeam
Task EXECUTED_BY RoleAssignment
Task USES ERoFObject
RoleAssignment USES ERoFObject
ERoFObject OWNED_BY RoFOrg
Task PRODUCES Result
Verification EVALUATES Result
Verification CHECKS SuccessCriterion
Verification USES_EVIDENCE Evidence
Verification SUPERSEDES Verification
```

A `Verification` uses `evaluatedResultRevision` and `checkedCriterionRevision` to bind exactly the revisions that were checked. Its `Result` is `COMPLETED`, its `SuccessCriterion` is `ACTIVE`, and both belong to the same `PiF1o`. Only a non-superseded Verification whose bound revisions still match the current revisions of both targets is applicable.

**Short example:** A Verification checks revision 3 of a completed Result against revision 2 of an active success criterion. If the criterion is later changed to revision 3, the Verification remains documented but is no longer applicable to the current aggregation.

### 5.3 Organisation and roles

```text
RoFOrg HAS_TEAM RoFTeam
RoFTeam HAS_MEMBER RoFTeamMember
RoFTeamMember HAS_ROLE RoFRole
RoFTeamMember HAS_ASSIGNMENT RoleAssignment
RoleAssignment IN_TEAM RoFTeam
RoleAssignment ACTIVATES_ROLE RoFRole
RoFOrgRelationship SOURCE_ORG RoFOrg
RoFOrgRelationship TARGET_ORG RoFOrg
RoFOrgRelationship REPRESENTED_BY RoleAssignment
```

### 5.4 Rules

```text
RaN GOVERNS permitted JCIEntity
RaN APPLIES_IN RoFOrg or RoFTeam
RaNConflict CONFLICTING_RULE RaN
RaNConflict AFFECTS JCIEntity
RaNConflict DETECTED_BY SyncEvent
RaNConflict RESOLVED_BY RoleAssignment
RaNConflict RESOLVED_THROUGH ChangeEvent
RaNConflict USES_EVIDENCE Evidence
```

Permitted target types are `PiF2`, `PiF1s`, `PiF1t`, `PiF1o`, `Task`, `RoFOrg`, `RoFOrgRelationship`, `RoFTeam`, `RoFTeamMember`, `RoFRole`, `RoleAssignment`, and `ERoFObject`.

A `RaN` has `effect`, `decisionKey`, `scopeType`, `governedTypes`, and a normalized `condition`. `GOVERNS` connects the concrete targets currently governed. `APPLIES_IN` limits an organization or team scope. `priority` is an explicitly stored integer; a larger number means higher precedence in a detected contradiction. `ruleType` has no implicit ranking. `RaNConflict` is a historizable graph object with `status = OPEN | RESOLVED`. It does not replace a participating rule but documents the conflict that cannot be decided automatically and its later resolution. A `PRIORITY_TIE` connects at least two rules; an `UNEVALUABLE` conflict may concern a single rule whose evaluation is not unambiguous.

### 5.5 Actors and evidence

```text
JCIEntity CREATED_BY RoleAssignment
ChangeEvent REQUESTED_BY RoleAssignment
HistoricalCorrection CORRECTED_BY RoleAssignment
RaNConflict RESOLVED_BY RoleAssignment
RaNConflict USES_EVIDENCE Evidence
ChangeEvent USES_EVIDENCE Evidence
HistoricalCorrection USES_EVIDENCE Evidence
```

The initial bootstrap exclusively establishes the trust root of a completely empty graph. It creates exactly one root `RoleAssignment` with `bootstrapKey = "ROOT"`. Only this RoleAssignment may permanently exist without `CREATED_BY`. The atomic minimal graph contains one `RoFOrg`, one `RoFTeam`, one technical `RoFTeamMember`, one `RoFRole`, the root `RoleAssignment`, and one `SYNC` definition. All six entities are created directly with `status = ACTIVE`, `revision = 1`, and the same `createdAt` and `updatedAt`; any `validFrom` values on the types and relationships equal the same bootstrap timestamp. This is the only exception to the regular `DRAFT` start. All entities except the root `RoleAssignment` refer to this trust root via `CREATED_BY`. The bootstrap creates neither a `ChangeEvent`, `SyncRun`, `SyncEvent`, nor `PiH`, cannot be repeated, and is not a data import.

**Short example:** After the technical administration team has been created once, its root `RoleAssignment` can request the first regular `CREATED` operation. A later import must not run the bootstrap again.

### 5.6 Change, historization, and correction

```text
historizable JCIEntity CHANGED_BY ChangeEvent
ChangeEvent TRIGGERS SyncEvent
ChangeEvent TARGETS_HISTORY PiH
SyncEvent EXECUTES SYNC
SyncEvent AFFECTS JCIEntity
historizable JCIEntity HAS_HISTORICAL_STATE PiH
SyncEvent CREATES_HISTORY PiH
HistoricalCorrection CORRECTS PiH
HistoricalCorrection CAUSED_BY ChangeEvent
SyncEvent CREATES_CORRECTION HistoricalCorrection
HistoricalCorrection SUPERSEDES HistoricalCorrection
replaceable JCIEntity REPLACED_BY same concrete JCIEntity type
```

`EXECUTES` records in the completed `SyncEvent` which SYNC definition the technical `SyncRun` used. The technical `SyncRun` is not stored as an intermediate node. An accepted `ChangeEvent` may initially have no target via `TRIGGERS`. Each completed or controlled-aborted attempt creates exactly one new `SyncEvent` and appends exactly one `TRIGGERS` edge.

`CHANGED_BY` has conditional semantics: a normal change has exactly one source entity. For `CREATED`, the source is absent until the successful commit; the target entity and the edge are created together only for `SUCCESS`. A `ChangeEvent` for `HISTORICAL_CORRECTION`, by contrast, has no `CHANGED_BY` source but exactly one `TARGETS_HISTORY` edge to the unchanged `PiH`. The PiH later connected through `CORRECTS` must be the same target.

`AFFECTS` may be empty if an attempt ends with `outcome = FAILED` before successful target resolution. A `SyncEvent` with `SUCCESS` or `CONFLICT` has at least one `AFFECTS` target.

A `HistoricalCorrection` stores in `baseHistoryViewHash` the hash of the effective `HistoryView` immediately before its creation. Non-superseded corrections of the same `PiH` must be disjoint by field. A new correction with overlapping `correctedFields` fully replaces exactly one active predecessor correction via `SUPERSEDES`; otherwise a conflict occurs.

**Short example:** While the first SyncRun is still running, the `ChangeEvent` has no `TRIGGERS` target. Only its completion creates the `SyncEvent`. A later historical correction already refers to the affected `PiH` via `TARGETS_HISTORY` without changing it.

`REPLACED_BY` is the stored successor relationship of an entity with `status = REPLACED`. Source and target have the same concrete `entityType`; self-references and cycles are prohibited.

## 6. Inverse readings

Inverse wording is used only for navigation and is not stored as an additional edge. Examples:

```text
USED_BY           = inverse reading of USES
REALIZES          = inverse reading of DECOMPOSES_INTO
TRIGGERED_BY      = inverse reading of TRIGGERS
CREATED_FROM      = inverse reading of CREATES_HISTORY
CORRECTED_THROUGH = inverse reading of CORRECTS
SUPERSEDED_BY     = inverse reading of SUPERSEDES
```

## 7. Historizability

All existing `JCIEntities` are generally historizable except:

```text
PiH
ChangeEvent
SyncEvent
HistoricalCorrection
```

These four types are immutable in content and are not historized again. Only the append-only provenance additions to `ChangeEvent` described above are permitted. A discrepancy in a `PiH` is documented by a new `HistoricalCorrection` object. The `PiH` itself remains unchanged. `TARGETS_HISTORY` only addresses the reason for the correction and is not a change to the historical state.

## 8. Task types and task graph

Every `Task` has exactly one `taskKind`:

```text
ATOMIC    = directly executable activity
COMPOSITE = structural node made up of at least one subordinate Task
```

`PiF1o DECOMPOSES_INTO Task` assigns every Task, irrespective of hierarchy level, to exactly one operational future state. `Task DECOMPOSES_INTO Task` forms an acyclic hierarchy in which a Task has at most one direct parent. `Task DEPENDS_ON Task` describes a domain execution prerequisite and may cross hierarchy and PiF1o boundaries, but remains free of self-references and cycles.

`HAS_MEMBER` and `HAS_ROLE` have `validFrom` and optionally `validUntil`. The validity period of a `RoleAssignment` lies completely within the simultaneously valid membership and role ownership. `OWNED_BY` enables the organization-relative derivation of internal and external environment context; actual interaction remains person-bound through `USES`.

Only `ATOMIC` Tasks have `EXECUTED_BY`, `USES`, and `PRODUCES`. An active or completed atomic Task has at least one executing `RoleAssignment`. The status of a `COMPOSITE` Task is derived from its direct subtasks.

## 9. Machine-readable exchange and extension

Complete graph and ontology exports use JSON-LD 1.1 with the context `schemas/jci-context.jsonld`. Entities are identified as `urn:jci:<UUID>`; concrete types and relationships use the public, versioned namespace `https://eeimicke.github.io/junaco-jci-loop/ns/jci/1.0#`.

`JCIChangeRequest` and `JCISyncResult` use `schemaVersion = "1.1"`. For `HISTORICAL_CORRECTION`, a structured `historicalCorrection` object replaces the general `operations`; it includes in particular `expectedHistoryViewHash`, unique lexicographically sorted `correctedFields`, `previousValue`, and `correctedValue`.

Complex properties use the structured types from `JCI_CONTEXT.md` and are transferred as JSON-LD-compatible JSON values. The Neo4j projection as a canonical JSON string does not change the exchange format.

The concrete entity, enum, and relationship types listed in this version form a closed catalogue. A new subtype or relationship requires a versioned semantic model change in `JCI_CONTEXT.md`, followed by updates to all downstream documents, the JSON-LD context, schemas, and tests. Implementations must not silently treat unknown types as known types.

**Short example:** An exported Task entity has `@id = "urn:jci:<UUID>"`, `@type = "jci:Task"`, and relationships such as `jci:RESPONSIBLE_TEAM`. On import, these become the canonical nodes and edges again.
