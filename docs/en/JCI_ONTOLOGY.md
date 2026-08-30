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

`PiH`, `ChangeEvent`, `SyncEvent`, and `HistoricalCorrection` are immutable. For them, `revision = 1` and `updatedAt = createdAt` apply permanently.

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

### 5.6 Change, historization, and correction

```text
historizable JCIEntity CHANGED_BY ChangeEvent
ChangeEvent TRIGGERS SyncEvent
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

`EXECUTES` records in the completed `SyncEvent` which SYNC definition the technical `SyncRun` used. The technical `SyncRun` is not stored as an intermediate node.

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

These four types are immutable and are not historized again. A discrepancy in a `PiH` is documented by a new `HistoricalCorrection` object. The `PiH` itself remains unchanged.

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

Complex properties use the structured types from `JCI_CONTEXT.md` and are transferred as JSON-LD-compatible JSON values. The Neo4j projection as a canonical JSON string does not change the exchange format.

The concrete entity, enum, and relationship types listed in this version form a closed catalogue. A new subtype or relationship requires a versioned semantic model change in `JCI_CONTEXT.md`, followed by updates to all downstream documents, the JSON-LD context, schemas, and tests. Implementations must not silently treat unknown types as known types.

**Short example:** An exported Task entity has `@id = "urn:jci:<UUID>"`, `@type = "jci:Task"`, and relationships such as `jci:RESPONSIBLE_TEAM`. On import, these become the canonical nodes and edges again.
