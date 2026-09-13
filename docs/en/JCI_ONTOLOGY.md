# JCI Ontology

## 1. Status and purpose

This document translates the domain meaning from [`JCI_CONTEXT.md`](../JCI_CONTEXT.md) into unambiguously named entity and relationship types. [`JCI_CONTEXT.md`](JCI_CONTEXT.md) remains the canonical domain source. If a conflict exists, the state documented there applies; the conflict must be reported before changing the model.

Cardinalities and invariants are defined in [`JCI_GRAPH_RULES.md`](JCI_GRAPH_RULES.md). The `SYNC` process is defined in [`JCI_SYNC_SPEC.md`](JCI_SYNC_SPEC.md). Database-specific labels, properties, constraints, and indexes belong in [`implementations/neo4j/JCI_NEO4J_SCHEMA.md`](implementations/neo4j/JCI_NEO4J_SCHEMA.md).

**Rule package 2.0:** Ontology, graph rules, SYNC, new snapshots, correction values, and the exchange format use version `2.0`. JSON-LD remains `1.1`; existing namespace IRIs ending in `/1.0#` remain stable vocabulary identities and are not the rule version. Earlier records are interpreted only through their explicit version profiles.

Approval-protected operations supplement this rule package with `approvalProfileVersion = "1.0"`. The underlying exchange format remains `2.0`; approval envelopes and full approval receipts are technical records outside `JCIEntity`.

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

| Property      | Data type | Required | Rule                                     |
| ------------- | --------- | -------: | ---------------------------------------- |
| `id`          | UUID      | yes      | globally unique and immutable            |
| `entityType`  | Enum      | yes      | exactly matches the concrete entity type |
| `name`        | String    | yes      | not empty                                |
| `description` | String    | no       | domain description                       |
| `createdAt`   | DateTime  | yes      | ISO 8601 with time zone                  |
| `updatedAt`   | DateTime  | yes      | not before `createdAt`                   |
| `revision`    | Integer   | yes      | at least `1`                             |
| `status`      | Enum      | yes      | type-specific permitted status           |

`PiH`, `ChangeEvent`, `SyncEvent`, and `HistoricalCorrection` are immutable in content. For them, `revision = 1` and `updatedAt = createdAt` apply permanently. A `ChangeEvent` documents an accepted change request, whereas a `SyncEvent` documents the result of exactly one completed or controlled-aborted technical `SyncRun`. The `TRIGGERS` relationship created when the run finishes may only be appended. For a successful `CREATED`, exactly one `CHANGED_BY` relationship from the newly created entity to the existing `ChangeEvent` may additionally be established once. These provenance additions do not change any property of the `ChangeEvent`.

The following type-specific required fields apply in particular to the entity types refined here:

| Entity type            | Additional required fields                                                  |
| ---------------------- | --------------------------------------------------------------------------- |
| `CiV`                  | `notCiV`, `selfCiV`, `toServeCiV`                                           |
| `ChangeEvent`          | `idempotencyKey`, `targetEntityId`, `targetEntityType`, `requestedRevision` |
| `SyncEvent`            | `runId`                                                                     |
| `Verification`         | `evaluatedResultRevision`, `checkedCriterionRevision`                       |
| `HistoricalCorrection` | `baseHistoryViewHash`                                                       |

`requestedRevision` is `null` exclusively for `changeType = CREATED`; otherwise it is a positive integer. The target details of the `ChangeEvent` are immutable audit coordinates of the request and do not replace a domain relationship. `runId` identifies exactly one technical attempt. `baseHistoryViewHash` binds a historical correction to the effective historical view immediately preceding it.

Type-specific required fields and enumeration values are canonically defined in section 2.2.5 of [`JCI_CONTEXT.md`](../JCI_CONTEXT.md). Binding status transitions are defined in section 2.2.4. A database implementation may make them technically concrete but must not weaken or semantically reinterpret them.

A `SyncDefinition` capable of executing approval-protected operations must have `approvalProfileVersion = "1.0"`. A `RaN` may additionally carry a typed `approvalPolicy`:

```text
ApprovalPolicy = {
  profileVersion = "1.0",
  mode = ACCOUNTABLE_CHAIN | VALUE_SCOPE,
  roleIds = non-empty unique RoFRole UUID[],
  levels = FutureType[]
}

FutureType = PiF1o | PiF1t | PiF1s | PiF2
```

For `ACCOUNTABLE_CHAIN`, `levels` is non-empty and unique. For `VALUE_SCOPE`, `levels` is absent or empty. The policy alone does not grant approval; it limits which human role assignments may approve under an active, temporally valid, scope-matching `PERMIT` rule whose condition holds. Approval profile 1.0 evaluates only the two-part paths `target.<property>`, `actor.<property>`, and `request.<property>` defined in `JCI_CONTEXT`. Other paths and unresolved types are `UNEVALUABLE`.

Complex values exclusively use the types `TypedValue`, `StateSnapshot`, `RelationshipSnapshot`, `TypedValueMap`, `RuleExpression`, and `SyncDefinition` defined in section 2.2.7. Unstructured, implementation-dependent object content is not permitted.

## 5. Relationship catalogue

### 5.1 Purpose and future

```text
PiH PROVIDES_CONTEXT_TO CiV
CiV HELD_BY RoFOrg, RoFTeam, or human RoFTeamMember
CiV INFORMED_BY CiV
CiV INSCRIBES_PURPOSE_IN PiF2
PiF1s CONTRIBUTES_TO PiF2
PiF1t CONTRIBUTES_TO PiF1s
PiF1o CONTRIBUTES_TO PiF1t
```

Each `CiV` describes exactly one value through the three non-empty dimensions `notCiV`, `selfCiV`, and `toServeCiV`. Exactly one `HELD_BY` determines its scope; a `RoFTeamMember` is permitted only with `memberType = HUMAN`. `INFORMED_BY` documents only explicitly confirmed domain provenance between different CiV and causes neither inheritance nor copying. All CiV directly grounding one `PiF2` have the same `HELD_BY` target; the scope of the `PiF2` is derived from it. The purpose developed in the `PiF2` is not stored redundantly as a CiV property.

### 5.2 Operational implementation and verification

```text
PiF2 ACCOUNTABLE_MEMBER RoFTeamMember
PiF1s ACCOUNTABLE_MEMBER RoFTeamMember
PiF1t ACCOUNTABLE_MEMBER RoFTeamMember
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

`ACCOUNTABLE_MEMBER` is optional for `PiF2`, `PiF1s`, and `PiF1t`, with at most one target per future entity. This permits gradual adoption by existing data. As soon as one of these levels is needed for an approval route, however, its accountable member must be present unambiguously; accountability is not inherited between levels. Exactly one accountable member remains mandatory for `PiF1o`.

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
RaN PROTECTS CiV or PiF2
RaN GOVERNS permitted JCIEntity
RaN APPLIES_IN RoFOrg or RoFTeam
RaNConflict CONFLICTING_RULE RaN
RaNConflict AFFECTS JCIEntity
RaNConflict DETECTED_BY SyncEvent
RaNConflict RESOLVED_BY RoleAssignment
RaNConflict RESOLVED_THROUGH ChangeEvent
RaNConflict USES_EVIDENCE Evidence
```

`PROTECTS` targets only `CiV` or `PiF2`. Permitted `GOVERNS` target types are `PiF1s`, `PiF1t`, `PiF1o`, `Task`, `SuccessCriterion`, `Result`, `Verification`, `Evidence`, `RoFOrg`, `RoFOrgRelationship`, `RoFTeam`, `RoFTeamMember`, `RoFRole`, `RoleAssignment`, and `ERoFObject`. `PiF2` is no longer a `GOVERNS` target and is protected through `PROTECTS` instead.

A `RaN` has `effect`, `decisionKey`, `scopeType`, `governedTypes`, and a normalized `condition`. `PROTECTS` connects the explicitly protected values and long-term future states. An active RaN protects at least one CiV and one PiF2; both sides are coherently connected by `INSCRIBES_PURPOSE_IN`. `GOVERNS` connects at least one currently governed concrete implementation element. `APPLIES_IN` limits an organization or team scope. `priority` is an explicitly stored integer; a larger number means higher precedence in a detected contradiction. `ruleType` has no implicit ranking. `RaNConflict` is a historizable graph object with `status = OPEN | RESOLVED`. It does not replace a participating rule but documents the conflict that cannot be decided automatically and its later resolution. A `PRIORITY_TIE` connects at least two rules; an `UNEVALUABLE` conflict may concern a single rule whose evaluation is not unambiguous.

### 5.5 Actors and evidence

```text
JCIEntity CREATED_BY RoleAssignment
ChangeEvent REQUESTED_BY RoleAssignment
ChangeEvent APPROVED_BY RoleAssignment
HistoricalCorrection CORRECTED_BY RoleAssignment
RaNConflict RESOLVED_BY RoleAssignment
RaNConflict USES_EVIDENCE Evidence
ChangeEvent USES_EVIDENCE Evidence
HistoricalCorrection USES_EVIDENCE Evidence
```

`REQUESTED_BY` preserves the original requester. `APPROVED_BY` records only approvals for an accepted approval-protected request. Each such edge carries exactly one `receiptId`, `decidedAt`, `requestHash`, and `approvalHash`; at most one edge is allowed per `ChangeEvent` and `RoleAssignment`. The edges are born immutably with the accepted `ChangeEvent` and are never appended or changed later. The same human may request and approve unless an applicable `RaN` explicitly requires separation.

A pending proposal and rejected or abandoned approvals remain, with their full technical states or decision receipts, outside the JCI graph. They create no `ChangeEvent`, `APPROVED_BY`, `SyncRun`, `SyncEvent`, or domain change. Receipts carry only `outcome = APPROVED | REJECTED`; pending is the technical state of the proposal, not an invented third receipt outcome.

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

A `HistoricalCorrection` binds the effective pre-correction content through `baseHistoryViewHash`. Profile `2.0` defines canonical property and stable relationship paths, segment-based ancestor/descendant overlap, complete supersession of exactly one active predecessor, and absolute value overlays for reconstruction. Snapshot and view hashes use the same content object. Missing values differ from existing `NULL`; prior profile data and hashes remain immutable. Section 2.2.9 of [`JCI_CONTEXT.md`](JCI_CONTEXT.md) defines the binding contract.

**Short example:** While the first SyncRun is still running, the `ChangeEvent` has no `TRIGGERS` target. Only its completion creates the `SyncEvent`. A later historical correction already refers to the affected `PiH` via `TARGETS_HISTORY` without changing it.

`REPLACED_BY` is the stored successor relationship of an entity with `status = REPLACED`. Source and target have the same concrete `entityType`; self-references and cycles are prohibited.

Revision ownership is part of the relationship contract, not a new edge or entity type. `EVALUATES`, `CHECKS`, and verification `SUPERSEDES` belong to the new `Verification`; their targets retain their revisions. `CREATED_BY` never revises the referenced `RoleAssignment`. New snapshots use `snapshotSchemaVersion = "2.0"` and include only the entity's owned relationship state. The complete matrix in section 2.2.8 of [`JCI_CONTEXT.md`](JCI_CONTEXT.md) is binding for every implementation.

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

These four types have immutable properties and owned provenance and are not historized again. Endpoint ownership is defined by section 2.2.8 of [`JCI_CONTEXT.md`](JCI_CONTEXT.md): new references owned by another object do not revise the referenced record. `TRIGGERS`, `CHANGED_BY`, `TARGETS_HISTORY`, and `CORRECTS` follow that explicit matrix. A discrepancy in a `PiH` creates a separate `HistoricalCorrection` without rewriting the `PiH`.

## 8. Task types and task graph

Every `Task` has exactly one `taskKind`:

```text
ATOMIC    = directly executable activity
COMPOSITE = structural node made up of at least one subordinate Task
```

`PiF1o DECOMPOSES_INTO Task` assigns every Task, irrespective of hierarchy level, to exactly one operational future state. `Task DECOMPOSES_INTO Task` forms an acyclic hierarchy in which a Task has at most one direct parent. `Task DEPENDS_ON Task` describes a domain execution prerequisite and may cross hierarchy and PiF1o boundaries, but remains free of self-references and cycles.

`HAS_MEMBER` and `HAS_ROLE` have `validFrom` and optionally `validUntil`. The validity period of a `RoleAssignment` lies completely within the simultaneously valid membership and role ownership. `OWNED_BY` enables the organization-relative derivation of internal and external environment context; actual interaction remains person-bound through `USES`.

Only `ATOMIC` Tasks have `EXECUTED_BY`, `USES`, and `PRODUCES`. An active or completed atomic Task has at least one executing `RoleAssignment`. The status of a released `COMPOSITE` Task follows own prerequisites and then current direct subtasks under section 9.4.2 of the canonical context document.

Current scope excludes `REPLACED` and `REVOKED` while retaining stored goal assignments and completed Tasks. An achieved `PiF1o` needs a non-empty completed current Task set and at least one current required criterion; current required criteria must be active and satisfied. Replacement and revocation require explicit authorization; old Results are not automatically transferred. The precise scope contract is defined in section 9.4.2 of [`JCI_CONTEXT.md`](JCI_CONTEXT.md).

The completion graph is a virtual union of current hierarchy and explicit prerequisites, with source waiting for target. It introduces no entity or relationship type. Mixed cycles across goals are prohibited. Atomic and composite Tasks are evaluated together with prerequisites first. A released composite’s own unmet prerequisite yields `BLOCKED` before its children are aggregated; `DRAFT` requires explicit release and terminal states are not reopened.

## 9. Machine-readable exchange and extension

Complete graph and ontology exports use JSON-LD 1.1 with the context [`schemas/jci-context.jsonld`](../schemas/jci-context.jsonld). Entities are identified as `urn:jci:<UUID>`; concrete types and relationships use the public, versioned namespace `https://eeimicke.github.io/junaco-jci-loop/ns/jci/1.0#`.

`JCIChangeRequest` and `JCISyncResult` use `schemaVersion = "2.0"`. For `HISTORICAL_CORRECTION`, a structured `historicalCorrection` object replaces the general `operations`; it includes in particular `expectedHistoryViewHash`, unique lexicographically sorted `correctedFields`, `previousValue`, and `correctedValue`.

An approval-protected proposal embeds that unchanged `JCIChangeRequest` in an approval envelope containing `approvalProfileVersion`, `decisionKey`, `requestHash`, `contextHash`, and complete technical decision receipts. Only a fully approved envelope revalidated against both hashes may be accepted as a request. Its valid `APPROVED` receipts become immutable `APPROVED_BY` edges when the `ChangeEvent` is created; the envelope, waiting states, and rejected receipts do not become graph nodes.

For the first `Model.action.CONFIRM` value decision, an installation may maintain initial authority explicitly configured by an authenticated human for one exact member, role assignment, and value holder. It never applies to Task release and gives the technical root `RoleAssignment` no human authority. Once the first active `VALUE_SCOPE` policy has been adopted for that value holder, a durable technical disable latch deactivates the initial authority; later policy revocation never enables it again.

Complex properties use the structured types from [`JCI_CONTEXT.md`](JCI_CONTEXT.md) and are transferred as JSON-LD-compatible JSON values. The Neo4j projection as a canonical JSON string does not change the exchange format.

The concrete entity, enum, and relationship types listed in this version form a closed catalogue. A new subtype or relationship requires a versioned semantic model change in [`JCI_CONTEXT.md`](JCI_CONTEXT.md), followed by updates to all downstream documents, the JSON-LD context, schemas, and tests. Implementations must not silently treat unknown types as known types.

The technical commit gate, `graphEpoch`, durable payload, run ownership, and idempotent commit record under section 12.8 of [`JCI_CONTEXT.md`](JCI_CONTEXT.md) are implementation infrastructure outside `JCIEntity`. They protect all JCI writes without introducing a core element, semantic edge, or domain cardinality. Legacy exchange schemas remain separately available; version `2.0` does not rewrite older snapshots or hashes.

**Short example:** An exported Task entity has `@id = "urn:jci:<UUID>"`, `@type = "jci:Task"`, and relationships such as `jci:RESPONSIBLE_TEAM`. On import, these become the canonical nodes and edges again.
