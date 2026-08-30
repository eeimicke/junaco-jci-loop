# JUNACO Continuous Integration for Organisations

[Documentation overview](README.md) · [Kanonische deutsche Fassung](../JCI_CONTEXT.md)

> This document is the controlled English translation of the canonical German JCI specification. If the two versions differ, `docs/JCI_CONTEXT.md` is authoritative until the discrepancy has been resolved.

## 1. Origin, purpose, and scope

The **JUNACO Continuous Integration Model for Organisations** and its **JCI Loop** build on Stafford Beer's Viable System Model and the Intrinsic Value Based System Model developed by Ernst Rother, now Ernst Eimicke, in his master's thesis. Jana Eimicke and Julian Ulbricht further developed the model in the practice of JUNACO Organisationsentwicklungs GmbH.

JCI is a graph-based organisational model for purpose and values, future states, rules, roles, responsibilities, work, results, environmental relationships, verification, change, and history. Its central question is:

> Why do we act this way, towards which future, in which roles, under which conditions, and with which historical context?

The master's thesis remains an independent work and is not relicensed through this repository.

## 2. The JCI Loop and its entities

### 2.1 Ten core elements

| Time | Core element | Meaning |
|---|---|---|
| history | `PiH` | Point in History; immutable former state |
| present | `CiV` | Core Influential Values; purpose and values |
| present | `RaN` | Rules and Norms |
| present | `RoF` | Roles and Functions model space |
| present | `ERoF` | Environment of Roles or Functions model space |
| present | `SYNC` | stored Synchronisation definition |
| future | `PiF2` | Point in Future, Second Order; beyond ten years |
| future | `PiF1s` | First Order Strategic; beyond five up to ten years |
| future | `PiF1t` | First Order Tactical; one to five years |
| future | `PiF1o` | First Order Operational; less than one year |

Eight core elements have stored instances. `RoF` and `ERoF` remain conceptual model spaces without dedicated nodes.

### 2.2 Type hierarchy

```text
JCIEntity
├── JCIElementInstance
│   ├── PiH, CiV, RaN, SYNC
│   └── PiF2, PiF1s, PiF1t, PiF1o
└── GraphObject
    ├── RoFOrg, RoFOrgRelationship, RoFTeam, RoFTeamMember
    ├── RoFRole, RoleAssignment
    ├── Task, SuccessCriterion, Result, Verification, Evidence, ERoFObject
    └── ChangeEvent, SyncEvent, RaNConflict, HistoricalCorrection
```

`JCIEntity` is an abstract supertype, not an eleventh core element. Every stored entity has an immutable UUID, one concrete `entityType`, `name`, optional `description`, `createdAt`, `updatedAt`, positive `revision`, and a type-specific `status`. Timestamps use ISO 8601 with timezone; property names use camelCase and enum values uppercase.

### 2.3 Status model

| Types | Permitted statuses |
|---|---|
| mutable domain entities | `DRAFT`, `ACTIVE`, `REPLACED`, `REVOKED` |
| `PiF2`, `PiF1s`, `PiF1t`, `PiF1o` | plus `ACHIEVED` |
| `Task` | plus `BLOCKED`, `COMPLETED` |
| `Result` | plus `COMPLETED` |
| `Verification` | `COMPLETED` |
| `RaNConflict` | `OPEN`, `RESOLVED` |
| `PiH`, `ChangeEvent`, `SyncEvent`, `HistoricalCorrection` | `RECORDED` |

Terminal statuses are `ACHIEVED`, `COMPLETED`, `REPLACED`, `REVOKED`, `RECORDED`, and `RESOLVED`. They never reopen. Continuation requires a new entity. Immutable process artifacts are created directly as `RECORDED`, remain at revision 1, and are not historised again.

A new mutable entity starts as `DRAFT`. Valid common transitions are `DRAFT → ACTIVE`, `DRAFT → REVOKED`, `ACTIVE → REPLACED`, and `ACTIVE → REVOKED`. Futures may transition `ACTIVE → ACHIEVED`; Results may transition `ACTIVE → COMPLETED`; Tasks use the additional transitions defined in Chapter 9. `RaNConflict` transitions only `OPEN → RESOLVED` after an explicit change and successful later SyncRun.

### 2.4 Actors, evidence, and structured values

Actors are represented through `RoleAssignment` relationships, never duplicated as actor IDs on domain nodes:

```text
JCIEntity ── CREATED_BY ──► RoleAssignment
ChangeEvent ── REQUESTED_BY ──► RoleAssignment
HistoricalCorrection ── CORRECTED_BY ──► RoleAssignment
RaNConflict ── RESOLVED_BY ──► RoleAssignment
```

Evidence is always a dedicated `Evidence` node connected through `USES_EVIDENCE`. Complex values use `TypedValue`, `StateSnapshot`, `RelationshipSnapshot`, `TypedValueMap`, `RuleExpression`, and `SyncDefinition`. Decimal values use canonical decimal strings; dates and datetimes use ISO 8601.

### 2.5 Canonical relationship catalogue

Only the following stored relationship names are permitted:

```text
PROVIDES_CONTEXT_TO, INSCRIBES_PURPOSE_IN, CONTRIBUTES_TO,
HAS_SUCCESS_CRITERIA, ACCOUNTABLE_MEMBER, DECOMPOSES_INTO, DEPENDS_ON,
RESPONSIBLE_TEAM, EXECUTED_BY, USES, PRODUCES, EVALUATES, CHECKS,
USES_EVIDENCE, SUPERSEDES, HAS_TEAM, HAS_MEMBER, HAS_ROLE,
HAS_ASSIGNMENT, IN_TEAM, ACTIVATES_ROLE, SOURCE_ORG, TARGET_ORG,
REPRESENTED_BY, OWNED_BY, GOVERNS, APPLIES_IN, CONFLICTING_RULE,
AFFECTS, DETECTED_BY, RESOLVED_BY, RESOLVED_THROUGH, CREATED_BY,
REQUESTED_BY, CORRECTED_BY, CHANGED_BY, TRIGGERS, EXECUTES,
REPLACED_BY, HAS_HISTORICAL_STATE, CREATES_HISTORY, CORRECTS,
CAUSED_BY, CREATES_CORRECTION
```

Inverse readings are navigation aids and do not create duplicate edges.

## 3. PiH – Point in History

`PiH` preserves the complete former state of one historisable `JCIEntity` when that state is actually superseded. It stores original identity and type, original revision, validity interval, `StateSnapshot`, sorted `RelationshipSnapshot` values, schema version, and a SHA-256 `contentHash`.

```text
historisable JCIEntity ── HAS_HISTORICAL_STATE ──► PiH
SyncEvent ── CREATES_HISTORY ──► PiH
```

Creation of a new entity produces no `PiH`. Merely affected entities produce no `PiH`. Existing `PiH` objects are never edited or historised. A discovered historical error is documented through an immutable `HistoricalCorrection` connected by `CORRECTS`, `CAUSED_BY`, `CORRECTED_BY`, `CREATES_CORRECTION`, and optionally `SUPERSEDES` and `USES_EVIDENCE`.

**Example:** Changing a Task name from “Prepare launch” to “Prepare customer portal launch” preserves the former Task properties and relationships as one `PiH`; the current Task advances exactly one revision.

## 4. CiV – Core Influential Values

`CiV` records an organisation's purpose, values, and scope. It provides the value-based reason for the future graph.

```text
PiH ── PROVIDES_CONTEXT_TO ──► CiV
CiV ── INSCRIBES_PURPOSE_IN ──► PiF2
```

An active `CiV` must inscribe purpose in at least one `PiF2`. A `PiF2` receives purpose from at least one `CiV`. Historical context can inform several values, and a value can use several historical contexts.

**Example:** “We act transparently and reliably” is inscribed in a long-term future in which customers can understand decisions and commitments.

## 5. PiF2 – long-term future

`PiF2` describes a target state beyond ten years. It receives purpose from `CiV` and contributions from `PiF1s`.

```text
CiV ── INSCRIBES_PURPOSE_IN ──► PiF2
PiF1s ── CONTRIBUTES_TO ──► PiF2
```

An active or achieved `PiF2` requires purpose. `contributionMode = ALL` requires all current direct contributions to be `ACHIEVED`; `ANY` requires at least one. At least one current contribution is always necessary.

**Example:** “The organisation is sustainably self-steering” is supported by several strategic future states.

## 6. RaN – Rules and Norms

An active `RaN` has `ruleType`, `effect = REQUIRE | PROHIBIT | PERMIT`, `statement`, `decisionKey`, `scopeType`, `governedTypes`, normalised `RuleExpression`, integer `priority`, and validity interval.

```text
RaN ── GOVERNS ──► JCIEntity
RaN ── APPLIES_IN ──► RoFOrg or RoFTeam
RaNConflict ── CONFLICTING_RULE ──► RaN
RaNConflict ── AFFECTS ──► JCIEntity
RaNConflict ── DETECTED_BY ──► SyncEvent
RaNConflict ── RESOLVED_THROUGH ──► ChangeEvent
```

`GLOBAL` and `ENTITY` scopes have no `APPLIES_IN`; `ORGANIZATION` has exactly one `RoFOrg` scope and `TEAM` exactly one `RoFTeam`. A true `REQUIRE` allows and a false one denies. A true `PROHIBIT` denies; a false one makes no decision. A true `PERMIT` allows; a false one makes no decision.

A single denial is a rule violation, not a conflict. A real conflict requires applicable rules with the same `decisionKey`, overlapping scope, a shared target, and simultaneous `ALLOW` and `DENY`. The greatest priority wins only that contradiction. Equal highest priority creates `PRIORITY_TIE`; unevaluable semantics creates `UNEVALUABLE`. Both create an open `RaNConflict` and block dependent automatic changes.

**Example:** A payment rule with priority 100 overrides a contradictory team rule with priority 50 for the concrete payment decision; the lower rule remains applicable elsewhere.

## 7. PiF1s – strategic future

`PiF1s` describes a strategic state beyond five and up to ten years. It contributes to one or more `PiF2` and receives contributions from `PiF1t`. Achievement follows the same `ALL` or `ANY` aggregation rule.

**Example:** “All business units operate through self-steering teams” contributes to the long-term self-steering organisation.

## 8. PiF1t – tactical future

`PiF1t` describes a tactical state from one to five years. It contributes to one or more `PiF1s` and receives contributions from `PiF1o`. Achievement follows the same current-contribution rules.

**Example:** “The new team structure is introduced across the organisation” supports the strategic state.

## 9. PiF1o, Tasks, Results, and Verification

`PiF1o` describes an operational target within one year. It contributes to one or more `PiF1t`, has exactly one accountable `RoFTeamMember`, one or more `SuccessCriterion` nodes, and one or more Tasks.

```text
PiF1o ── HAS_SUCCESS_CRITERIA ──► SuccessCriterion
PiF1o ── ACCOUNTABLE_MEMBER ──► RoFTeamMember
PiF1o ── DECOMPOSES_INTO ──► Task
Task ── DEPENDS_ON ──► Task
Task ── RESPONSIBLE_TEAM ──► RoFTeam
Task ── EXECUTED_BY ──► RoleAssignment
Task ── USES ──► ERoFObject
Task ── PRODUCES ──► Result
Verification ── EVALUATES ──► Result
Verification ── CHECKS ──► SuccessCriterion
Verification ── USES_EVIDENCE ──► Evidence
Verification ── SUPERSEDES ──► Verification
```

An `ATOMIC` Task carries execution, environmental use, and production. A `COMPOSITE` Task only structures direct subtasks. Task hierarchies and `DEPENDS_ON` are acyclic. Active or completed atomic Tasks require a complete WHY path to at least one `CiV` and a complete WHO path through RoleAssignment, member, role, team, and organisation.

Composite aggregation is deterministic: only `DRAFT` yields `DRAFT`; all `COMPLETED` yields `COMPLETED`; any `ACTIVE` or a mix of `DRAFT` and `COMPLETED` yields `ACTIVE`; without active work, any `BLOCKED` yields `BLOCKED`. Invalid replacement or a still-connected revoked child yields conflict.

Success criteria use `BOOLEAN`, `NUMERIC`, or `TEXTUAL` measurement and a compatible operator. A Verification is created complete and yields `VALID`, `INVALID`, or `INCONCLUSIVE`. A `PiF1o` becomes `ACHIEVED` only when at least one required criterion exists, all required criteria are validly verified, all assigned Tasks are completed, all dependencies hold, and no model or RaN violation exists.

**Example:** “Customer response within 24 hours” uses `NUMERIC`, `LESS_OR_EQUAL`, target `24`, and unit `hours`.

## 10. RoF – Roles and Functions

`RoF` is realised by `RoFOrg`, `RoFOrgRelationship`, `RoFTeam`, `RoFTeamMember`, `RoFRole`, `RoleAssignment`, and their relationships.

```text
RoFOrg ── HAS_TEAM ──► RoFTeam ── HAS_MEMBER ──► RoFTeamMember
RoFTeamMember ── HAS_ROLE ──► RoFRole
RoFTeamMember ── HAS_ASSIGNMENT ──► RoleAssignment
RoleAssignment ── IN_TEAM ──► RoFTeam
RoleAssignment ── ACTIVATES_ROLE ──► RoFRole
```

Every team belongs to exactly one organisation. A member may belong to several teams and organisations. `HAS_MEMBER` and `HAS_ROLE` carry `validFrom` and optional `validUntil`; a RoleAssignment must fall inside the intersection of both validity intervals. Optional allocation is greater than zero and at most one; overlapping allocations of one member total at most one.

Independent organisations are connected through `RoFOrgRelationship` with exactly one `SOURCE_ORG`, one different `TARGET_ORG`, and at least one valid representative RoleAssignment from each side. `SUBSIDIARY` is directed, permits arbitrary depth, at most one immediate active parent, and no cycle. `PARTNERSHIP` is semantically mutual and stored in UUID order. Overlapping duplicate active relationships are forbidden.

**Example:** Anna owns the Developer role once but activates it through separate RoleAssignments in Team A and Team B.

## 11. ERoF – Environment of Roles or Functions

`ERoF` is derived from concrete `ERoFObject` use and active organisational relationships. Another organisation remains a `RoFOrg`; it is never duplicated as an `ERoFObject`.

```text
RoleAssignment ── USES ──► ERoFObject
Task ── USES ──► ERoFObject
ERoFObject ── OWNED_BY ──► RoFOrg
```

Every active `ERoFObject` is used by at least one RoleAssignment. An atomic Task may use an object only if at least one executing RoleAssignment uses the same object. `OWNED_BY` expresses ownership, not interaction. An object is internal relative to an owning organisation and external to a non-owning user organisation.

`ERoF(RoFTeamMember)` is the union of objects used by its RoleAssignments. Team and organisation environments are derived through membership and team paths. Active partnerships and subsidiary relationships are relevant to both organisations' environmental perspective and remain represented by acting RoleAssignments.

**Example:** A shared platform owned by organisations A and B is internal to both and external to a using organisation C.

## 12. SYNC – synchronisation

`SYNC` is a stored, versioned, historisable process definition. A `SyncRun` is mutable technical runtime state and is neither a `JCIEntity` nor a graph node. An immutable `SyncEvent` is created only after completion or controlled termination and points through `EXECUTES` to the exact SYNC definition used.

```text
JCIEntity ── CHANGED_BY ──► ChangeEvent
ChangeEvent ── TRIGGERS ──► SyncEvent
SyncEvent ── EXECUTES ──► SYNC
SyncEvent ── AFFECTS ──► JCIEntity
SyncEvent ── CREATES_HISTORY ──► PiH
SyncEvent ── CREATES_CORRECTION ──► HistoricalCorrection
```

For each request SYNC validates schema, identity, expected revision, status transition, relationship types, cardinalities, traceability, Tasks, future aggregation, applicable RaN, history, and counters. Traversal starts from both endpoints of a relationship change, follows the complete entity-specific dependency matrix, prevents cycles with a visited set, and has no semantic truncation boundary.

On `SUCCESS`, the requested change, deterministic derived changes, revisions, PiH, corrections, conflict resolutions, relationships, and final SyncEvent are committed atomically. On `CONFLICT` or `FAILED`, domain changes are rolled back and create neither revision nor PiH; the final SyncEvent and newly detected conflicts remain attempt documentation. If event persistence is temporarily impossible, it must be recovered with the same run ID, ChangeEvent, and idempotency key without re-executing the failed domain change.

One ChangeEvent defines one atomic domain transaction. Repeated requests use immutable idempotency keys; each actually completed attempt has its own SyncEvent but may not apply the same domain change twice.

**Example:** Tightening a PiF1o response target from 24 to 12 hours checks criteria, Tasks, responsibility, roles, objects, and RaN. The former PiF1o becomes PiH only when the new revision is successfully committed.

### 12.1 Technology-independent exchange

`JCIChangeRequest` and `JCISyncResult` are UTF-8 JSON documents with `schemaVersion = "1.0"`. Schemas are stored under `docs/schemas/`. Full exports use JSON-LD 1.1, `urn:jci:<UUID>` entity identifiers, and the public namespace `https://eeimicke.github.io/junaco-jci-loop/ns/jci/1.0#`.

## 13. Closing model statement

JCI joins purpose, future, responsibility, work, environment, rules, evidence, verification, synchronisation, and history in one graph. Every active or completed atomic Task remains traceable to its value-based purpose and acting organisational context. Changes preserve superseded states without confusing them with current state. Rules are evaluated explicitly; unresolved contradictions are documented rather than silently decided.

This end-to-end traceability is the core of the JCI Loop.

