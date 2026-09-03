# JUNACO Continuous Integration for Organizations
## 1. JUNACO Continuous Integration for Organizations

### 1.1 Origin and purpose

This document describes the **JUNACO Continuous Integration Model for Organizations** and the resulting **JCI Loop**. The model is based on the Viable System Model (VSM) by Stafford Beer and the Intrinsic Value Based System Model developed by Ernst Rother, now Ernst Eimicke, in his master's thesis. In the practice of Junaco Organizationsentwicklung GmbH it was further developed into today's JCI model by Jana Eimicke and Julian Ulbricht.

The master's thesis and the practical further development form historical reference points for the creation of the JCI model.

### 1.2 Sources and people involved

- [Master's thesis by Ernst Rother, today Ernst Eimicke](https://monami.hs-mittweida.de/frontdoor/deliver/index/docId/6494/file/Masterarbeit_komplett.pdf)
- [Ernst Eimicke on LinkedIn](https://www.linkedin.com/in/eeimicke/)
- [Junaco Organizational Development GmbH](https://junaco.de/)
- [Julian Ulbricht on LinkedIn](https://www.linkedin.com/in/junaco/), involved in the practical development of the JCI model
- [Jana Eimicke on LinkedIn](https://www.linkedin.com/in/janaeimicke/)

### 1.3 Goal and scope

JCI is a graph-based organizational model to describe:

- goals and future states,
- Roles and responsibilities,
- tasks and results,
- rules and guard rails,
- environmental relations,
- historical development and change.

The central question is:

> Why do we act this way, with what goals, in what roles, under what conditions and with what historical context?

The model logic is graph-oriented. Individual elements are not only connected to one another hierarchically, but can also be connected via multiple paths and relationships.

### 1.4 From model to JCI loop

The JCI loop is created when the elements of the organizational model are continuously compared with one another. A change is checked by `SYNC` for its effects in the graph. Conditions that have been replaced remain comprehensible as `PiH` and can once again act as a historical context for values, goals and decisions. This closes the connection between past, present and future into a continuous loop.

The following chapter describes the elements, graph objects and relationships of this JCI loop.

---

## 2. The JCI Loop

### 2.1 Timing

#### 2.1.1 Past

- historical layer (`PiH` – **Point in History**)

#### 2.1.2 Present

- dimensioned values (`CiV` – **Core Influential Values**)
- Rules and Norms (`RaN` – **Rules and Norms**)
- Roles and organizational structure (`RoF` – **Roles and Functions**)
- Environmental Relations (`ERoF` – **Environment of Roles or Functions**)
- Synchronization process (`SYNC` – **Synchronization**)

#### 2.1.3 Future

- long-term future horizon (`PiF2` – **Point in Future, Second Order**)
- strategic future horizon (`PiF1s` – **Point in Future, First Order – Strategic**)
- tactical future horizon (`PiF1t` – **Point in Future, First Order – Tactical**)
- operational future horizon (`PiF1o` – **Point in Future, First Order – Operational**)

| JCI element | Time horizon                             |
| ----------- | ---------------------------------------- |
| `PiF1o`     | less than 1 year                         |
| `PiF1t`     | from 1 year up to and including 5 years  |
| `PiF1s`     | more than 5 up to and including 10 years |
| `PiF2`      | more than 10 years up to `n` years       |

`n` denotes an open, not fixed long-term time horizon.

### 2.2 Demarcation of core elements from graph objects

The JCI consists of exactly ten core elements:

```text
PiH, CiV, RaN, RoF, ERoF, SYNC,
PiF2, PiF1s, PiF1t, and PiF1o
```

A JCI core element denotes a fundamental technical component of the model. Belonging to the ten core elements does not automatically mean that the core element itself is stored as a node. Technical meaning and technical storage are therefore described separately.

| JCI core element | Memory status    | Saved Meaning                                                     |
| ---------------- | ---------------- | ----------------------------------------------------------------- |
| `PiH`            | own element type | unchanging historical condition                                   |
| `CiV`            | own element type | one value described through three dimensions                      |
| `RaN`            | own element type | concrete rule or norm                                             |
| `RoF`            | no own node      | conceptual model space for organization, teams, members and roles |
| `ERoF`           | no own node      | conceptual and derived model space of the relevant environment    |
| `SYNC`           | own element type | stored definition of the synchronization logic                    |
| `PiF2`           | own element type | concrete long-term future state                                   |
| `PiF1s`          | own element type | concrete strategic future state                                   |
| `PiF1t`          | own element type | concrete tactical future state                                    |
| `PiF1o`          | own element type | concrete operational future state                                 |

For the specific application and storage in the graph, additional graph objects are required. They make the core elements executable, testable and traceable, but are not further JCI core elements.

| Area                       | Graph object           | Meaning                                                    |
| -------------------------- | ---------------------- | ---------------------------------------------------------- |
| Organization               | `RoFOrg`               | independently acting organization                          |
| Organizational Relations   | `RoFOrgRelationship`   | Typical relationship between two independent organizations |
| Organization               | `RoFTeam`              | organizational or functional group                         |
| Organization               | `RoFTeamMember`        | human or technical actor                                   |
| Rolls                      | `RoFRole`              | Role, function and responsibility                          |
| Rolls                      | `RoleAssignment`       | active role of a member in a team                          |
| Operational implementation | `Task`                 | Activity to realize a `PiF1o`                              |
| Success and exam           | `SuccessCriterion`     | expected success criterion                                 |
| Success and exam           | `Result`               | Result generated by a Task                                 |
| Success and exam           | `Verification`         | Checking a result                                          |
| Success and exam           | `Evidence`             | independent, verifiable proof                              |
| Environment                | `ERoFObject`           | concrete object of the relevant environment                |
| change                     | `ChangeEvent`          | documented trigger of a change                             |
| change                     | `SyncEvent`            | documented synchronization run                             |
| Rules conflict             | `RaNConflict`          | understandable conflict between applicable rules           |
| Historical correction      | `HistoricalCorrection` | unchangeable correction or addition of a `PiH`             |

The core elements describe the basic technical structure of the JCI. The additional graph objects represent concrete organizations, people, roles, activities, environmental objects, results, tests and changes within this structure.

An ongoing technical synchronization process is referred to as `SyncRun`. `SyncRun` is part of the implementation, is not a `JCIEntity`, is not a `GraphObject`, and is not an additional JCI core element. Only the completion or controlled termination of a `SyncRun` creates the unchangeable technical `SyncEvent`.

#### 2.2.1 JCIEntity as a common generic term

`JCIEntity` is the abstract generic term for any concrete and uniquely identifiable instance that is stored as a node in the JCI graph. `JCIEntity` is not an eleventh core element or an additional node next to the concrete instance.

A `JCIElementInstance` is a saved instance of a savable JCI core element. A `GraphObject` specifies the practical application of the core elements. `JCIElementInstance` and `GraphObject` are abstract types for classifying stored nodes and are not additional core technical elements.

```text
JCIEntity
├── JCIElementInstance
│   ├── PiH
│   ├── CiV
│   ├── RaN
│   ├── SYNC
│   ├── PiF2
│   ├── PiF1s
│   ├── PiF1t
│   └── PiF1o
│
└── GraphObject
    ├── RoFOrg
    ├── RoFOrgRelationship
    ├── RoFTeam
    ├── RoFTeamMember
    ├── RoFRole
    ├── RoleAssignment
    ├── Task
    ├── SuccessCriterion
    ├── Result
    ├── Verification
    ├── Evidence
    ├── ERoFObject
    ├── ChangeEvent
    ├── SyncEvent
    ├── RaNConflict
    └── HistoricalCorrection
```

`RoF` and `ERoF` are not missing from this tree structure: both remain JCI core elements, but are conceptual model spaces without their own nodes. `RoF` is made concrete by its organization and role objects. `ERoF` is derived from environmental objects, organizational relationships and their use by acting roles.

Example of the distinction:

```text
Core element: CiV
└── stored JCIElementInstance:
    CiV "Clarity" with NOT, SELF, and TO SERVE dimensions

Core element: RoF
└── no separate RoF node
    ├── RoFOrg „Junaco“
    ├── RoFTeam “Development”
    └── RoleAssignment "Anna as Developer in Engineering"
```

In principle, every existing `JCIEntity` can be historized. The exceptions are `PiH`, `ChangeEvent`, `SyncEvent` and `HistoricalCorrection`: a `PiH` is immutable after creation and is not historized again. A `ChangeEvent` records an accepted change request; `SyncEvent` and `HistoricalCorrection` record completed facts. Their stored content and existing provenance relationships are not changed later. The `TRIGGERS` relationship created when a technical `SyncRun` ends is added append-only. When an entity is created successfully for the first time, exactly one `CHANGED_BY` relationship from that new entity to the existing `ChangeEvent` may also be added. These additions change neither `revision` nor `updatedAt` of the `ChangeEvent`. Creating a `JCIEntity` for the first time does not create a `PiH` because no previous state exists.

#### 2.2.2 Common properties of all JCI entities

Each stored `JCIEntity` has an immutable identity, a specific type and traceable time and revision information. Property names are stored in `camelCase`, enum values ​​in uppercase, and times in ISO 8601 with time zone.

| Property      | data type | duty | Meaning                                |
| ------------- | --------- | ---: | -------------------------------------- |
| `id`          | UUID      | yes  | globally unique, immutable identity    |
| `entityType`  | Enum      | yes  | concrete entity type                   |
| `name`        | String    | yes  | short, technically understandable name |
| `description` | String    | no   | detailed technical description         |
| `createdAt`   | DateTime  | yes  | Time of creation                       |
| `updatedAt`   | DateTime  | yes  | Time of last permitted change          |
| `revision`    | Integers  | yes  | positive revision of the current state |
| `status`      | Enum      | yes  | type-dependent technical status        |

`revision = 1` and `updatedAt = createdAt` apply during generation. Every independently requested or observed technical change, including a status change, generates a `ChangeEvent` and a synchronization run. Subsequent changes derived deterministically through this run remain part of the same change process and do not generate a recursive `ChangeEvent`; they are documented by `SyncEvent`, `AFFECTS`, revision and historization. If an initial state already exists, it is recorded as `PiH` before the change is applied; then `revision` of the current element is increased by exactly one. Purely technical read operations do not change either `updatedAt` or `revision`.

`PiH`, `ChangeEvent`, `SyncEvent` and `HistoricalCorrection` permanently retain `revision = 1` and `updatedAt = createdAt`. Their properties are not changed after creation. Only the append-only provenance additions described in section 2.2.1 apply to `ChangeEvent`.

The responsibility for creation is stored as a relationship to a specific `RoleAssignment` and is not additionally duplicated as an actor ID or free text:

```text
JCIEntity ── CREATED_BY ──► RoleAssignment
```

For imported data, `CREATED_BY` may be temporarily missing. Before such an entity receives `ACTIVE` or a type-specific completed status, the responsible role activation must be added. The only permanent exception is the root `RoleAssignment` with `bootstrapKey = "ROOT"` defined in section 12.7. A technical system identity is modeled as a regular `RoleAssignment` of a technical `RoFTeamMember`.

#### 2.2.3 Status model

The following status values ​​form the common pool. Each concrete entity type only uses the values ​​specified for it.

| Status      | Meaning                                                 |
| ----------- | ------------------------------------------------------- |
| `DRAFT`     | technically not yet complete                            |
| `ACTIVE`    | valid and usable in the model                           |
| `BLOCKED`   | Task waits for at least one unfulfilled dependency      |
| `ACHIEVED`  | described future state has been achieved                |
| `COMPLETED` | time-limited activity or examination has been completed |
| `REPLACED`  | replaced by another current state                       |
| `REVOKED`   | professionally reserved                                 |
| `RECORDED`  | unchangeably documented                                 |
| `OPEN`      | detected rule conflict has not yet been resolved        |
| `RESOLVED`  | Rule conflict was resolved by a confirmed model change  |

| Entity Types                                                                                                                   | Allowed status values ​​                                         |
| ------------------------------------------------------------------------------------------------------------------------------ | ---------------------------------------------------------------- |
| `CiV`, `RaN`, `SYNC`, `RoFOrg`, `RoFOrgRelationship`,<br>`RoFTeam`, `RoFTeamMember`, `RoFRole`, `RoleAssignment`, `ERoFObject` | `DRAFT`, `ACTIVE`, `REPLACED`, `REVOKED`                         |
| `PiF2`, `PiF1s`, `PiF1t`, `PiF1o`                                                                                              | `DRAFT`, `ACTIVE`, `ACHIEVED`, `REPLACED`, `REVOKED`             |
| `Task`                                                                                                                         | `DRAFT`, `ACTIVE`, `BLOCKED`, `COMPLETED`, `REPLACED`, `REVOKED` |
| `Result`                                                                                                                       | `DRAFT`, `ACTIVE`, `COMPLETED`, `REPLACED`, `REVOKED`            |
| `SuccessCriterion`, `Evidence`                                                                                                 | `DRAFT`, `ACTIVE`, `REPLACED`, `REVOKED`                         |
| `Verification`                                                                                                                 | `COMPLETED`                                                      |
| `RaNConflict`                                                                                                                  | `OPEN`, `RESOLVED`                                               |
| `PiH`, `ChangeEvent`, `SyncEvent`, `HistoricalCorrection`                                                                      | `RECORDED`                                                       |

Every permissible change in status is a technical change. A status may only be adopted if the cardinalities and model conditions applicable to the target status are met. A transition from `ACHIEVED`, `REPLACED`, `REVOKED`, `RECORDED`, `RESOLVED` or `COMPLETED` back to a changeable state is not permitted; a necessary continuation is modeled as a new entity.

#### 2.2.4 Binding status transitions

A status change is only permitted if it is listed in the following table. `SYNC` additionally checks all type-specific conditions, relationships and applicable `RaN`. The entry `Erzeugung` denotes the initial state of a new entity; This does not produce a `PiH`.

| Entity type or group                                      | Permitted transition                | `ChangeEvent.changeType` | Central condition                                                              |
| --------------------------------------------------------- | ----------------------------------- | ------------------------ | ------------------------------------------------------------------------------ |
| six bootstrap entities under section 12.7                 | bootstrap → `ACTIVE`                | –                        | completely empty graph; atomic and fully validated minimal graph               |
| mutable subject entity                                    | Generation → `DRAFT`                | `CREATED`                | Mandatory fields for a draft are present                                       |
| mutable subject entity                                    | `DRAFT` → `ACTIVE`                  | `CHANGED`                | all mandatory fields, actors and active cardinalities are fulfilled            |
| mutable subject entity                                    | `DRAFT` → `REVOKED`                 | `REVOKED`                | Draft is discarded                                                             |
| mutable subject entity                                    | `ACTIVE` → `REPLACED`               | `REPLACED`               | a technically valid successor takes over the function                          |
| mutable subject entity                                    | `ACTIVE` → `REVOKED`                | `REVOKED`                | Validity will end without successor                                            |
| `PiF2`, `PiF1s`, `PiF1t`, `PiF1o`                         | `ACTIVE` → `ACHIEVED`               | `ACHIEVED`               | Type-specific target and contribution conditions are met                       |
| `Task`                                                    | `DRAFT` → `BLOCKED`                 | `CHANGED`                | at least one necessary dependency is not fulfilled                             |
| `Task`                                                    | `ACTIVE` → `BLOCKED`                | `CHANGED`                | at least one necessary dependency is unfulfilled                               |
| `Task`                                                    | `BLOCKED` → `ACTIVE`                | `CHANGED`                | all necessary dependencies are fulfilled again                                 |
| `Task`                                                    | `BLOCKED` → `COMPLETED`             | `COMPLETED`              | all dependencies and completion conditions are satisfied in the same SyncRun   |
| `Task`                                                    | `ACTIVE` → `COMPLETED`              | `COMPLETED`              | Execution, dependency and completion conditions are met                        |
| `Task`                                                    | `BLOCKED` → `REPLACED` or `REVOKED` | `REPLACED` or `REVOKED`  | blocked Task is replaced or canceled                                           |
| `Result`                                                  | `ACTIVE` → `COMPLETED`              | `COMPLETED`              | Result is fully generated and immutable ready for testing                      |
| `RaNConflict`                                             | Generation → `OPEN`                 | –                        | Conflict is confirmed within the triggering change process                     |
| `RaNConflict`                                             | `OPEN` → `RESOLVED`                 | `RESOLVED`               | explicit model change and successful subsequent SyncRun eliminate the conflict |
| `Verification`                                            | Generation → `COMPLETED`            | `CREATED`                | Method, result, time, Result and SuccessCriterion are fixed                    |
| `PiH`, `ChangeEvent`, `SyncEvent`, `HistoricalCorrection` | Generation → `RECORDED`             | –                        | all mandatory information in the unchangeable document is fixed                |

For `CiV`, `RaN`, `SYNC`, `RoFOrg`, `RoFOrgRelationship`, `RoFTeam`, `RoFTeamMember`, `RoFRole`, `RoleAssignment`, `SuccessCriterion`, `Evidence` and `ERoFObject` apply the transitions of the variable subject entities. `Result` may be completed additionally. Future elements may also be achieved and tasks may be blocked or completed due to dependencies.

The bootstrap row is a one-time technical trust root and not a `ChangeEvent`. Apart from this explicitly bounded exception, direct shortcuts are permitted only where the table provides for creation into an immutable target state. In particular, active domain entities must not become drafts again as a result of a change. A domain continuation of a terminal state is created as a new entity and connected through the intended successor relationship.

Process artifacts do not create a recursive event chain: `ChangeEvent`, `SyncEvent`, `PiH`, `HistoricalCorrection` and an open `RaNConflict` recognized by SYNC are generated within the change process that is already in progress and do not trigger another `ChangeEvent` for their own creation. However, a later permitted change of a `RaNConflict` from `OPEN` to `RESOLVED` is a new technical change process.

**Short example:** A Task is created as `DRAFT`. If the team, executive role activation and requirements are valid, he switches to `ACTIVE`. If a requirement is omitted, `SYNC` sets it to `BLOCKED`. As soon as the requirement is met again, it can become `ACTIVE` again. After confirmed execution it becomes `COMPLETED`; this state will not be reopened.

#### 2.2.5 Type-specific mandatory fields

In addition to the common properties, the following type-specific fields apply. Relationships such as `CREATED_BY`, `REQUESTED_BY`, `CORRECTED_BY` and `USES_EVIDENCE` are stored exclusively as edges and therefore do not appear as ID or reference fields in this table.

| Entity type              | Additional mandatory fields                                                                                                                                                                                                                                                                          | Optional fields                                                                                                            |
| ------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------- |
| `PiH`                    | `originalEntityId: UUID`, `originalEntityType: Enum`,<br>`originalRevision: Integer`, `recordedAt: DateTime`,<br>`validFrom: DateTime`, `validUntil: DateTime`,<br>`snapshotSchemaVersion: String`, `stateData: StateSnapshot`,<br>`relationshipData: RelationshipSnapshot[]`, `contentHash: String` | –                                                                                                                          |
| `CiV`                    | `notCiV: String`, `selfCiV: String`, `toServeCiV: String`                                                                                                                                                                                                                                            | –                                                                                                                          |
| `RaN`                    | `ruleType: Enum`, `effect: Enum`, `statement: String`,<br>`decisionKey: String`, `scopeType: Enum`,<br>`governedTypes: Enum[]`, `condition: RuleExpression`,<br>`priority: Integer`, `validFrom: DateTime`                                                                                           | `validUntil: DateTime`                                                                                                     |
| `RaNConflict`            | `conflictKey: String`, `conflictType: Enum`,<br>`detectedAt: DateTime`, `reason: String`                                                                                                                                                                                                             | `resolvedAt: DateTime`, `resolution: String`                                                                               |
| `SYNC`                   | `version: String`, `definition: SyncDefinition`, `validFrom: DateTime`                                                                                                                                                                                                                               | `validUntil: DateTime`                                                                                                     |
| `PiF2`, `PiF1s`, `PiF1t` | `targetState: String`, `horizonStart: Date`,<br>`contributionMode: Enum`                                                                                                                                                                                                                             | `horizonEnd: Date`, `targetDate: Date`                                                                                     |
| `PiF1o`                  | `targetState: String`, `horizonStart: Date`                                                                                                                                                                                                                                                          | `horizonEnd: Date`, `targetDate: Date`                                                                                     |
| `RoFOrg`                 | `legalName: String`, `orgType: Enum`                                                                                                                                                                                                                                                                 | `externalReference: String`                                                                                                |
| `RoFOrgRelationship`     | `type: Enum`, `validFrom: DateTime`                                                                                                                                                                                                                                                                  | `validUntil: DateTime`                                                                                                     |
| `RoFTeam`                | `teamType: Enum`, `validFrom: DateTime`                                                                                                                                                                                                                                                              | `validUntil: DateTime`                                                                                                     |
| `RoFTeamMember`          | `memberType: Enum`, `displayName: String`                                                                                                                                                                                                                                                            | `externalReference: String`                                                                                                |
| `RoFRole`                | `roleName: String`, `responsibility: String`                                                                                                                                                                                                                                                         | `roleType: String`                                                                                                         |
| `RoleAssignment`         | `validFrom: DateTime`                                                                                                                                                                                                                                                                                | `validUntil: DateTime`, `allocation: Decimal`,<br>`bootstrapKey: String`                                                   |
| `Task`                   | `taskKind: Enum`                                                                                                                                                                                                                                                                                     | `taskType: String`, `plannedStart: DateTime`,<br>`plannedEnd: DateTime`, `actualStart: DateTime`,<br>`actualEnd: DateTime` |
| `SuccessCriterion`       | `criterion: String`, `measurementType: Enum`,<br>`requirementLevel: Enum`, `evaluationMode: Enum`,<br>`operator: Enum`, `targetValue: String`                                                                                                                                                        | `unit: String`                                                                                                             |
| `Result`                 | `resultType: String`, `value: TypedValue`, `producedAt: DateTime`                                                                                                                                                                                                                                    | –                                                                                                                          |
| `Verification`           | `method: String`, `outcome: Enum`, `verifiedAt: DateTime`,<br>`evaluatedResultRevision: Integer`,<br>`checkedCriterionRevision: Integer`                                                                                                                                                             | `reason: String`                                                                                                           |
| `Evidence`               | `evidenceType: String`, `reference: String`, `capturedAt: DateTime`                                                                                                                                                                                                                                  | `checksum: String`                                                                                                         |
| `ERoFObject`             | `objectType: Enum`, `validFrom: DateTime`                                                                                                                                                                                                                                                            | `validUntil: DateTime`, `externalReference: String`                                                                        |
| `ChangeEvent`            | `changeType: Enum`, `occurredAt: DateTime`, `reason: String`,<br>`idempotencyKey: String`, `targetEntityId: UUID`,<br>`targetEntityType: Enum`, `requestedRevision: Integer or null`                                                                                                                 | –                                                                                                                          |
| `SyncEvent`              | `runId: UUID`, `startedAt: DateTime`, `completedAt: DateTime`,<br>`outcome: Enum`, `affectedCount: Integer`, `changedCount: Integer`,<br>`historyCount: Integer`, `correctionCount: Integer`,<br>`conflictCount: Integer`                                                                            | `errorCode: String`, `errorMessage: String`                                                                                |
| `HistoricalCorrection`   | `correctionType: Enum`, `reason: String`, `correctedAt: DateTime`,<br>`valueSchemaVersion: String`, `baseHistoryViewHash: String`,<br>`correctedFields: String[]`, `previousValue: TypedValueMap`,<br>`correctedValue: TypedValueMap`                                                                | –                                                                                                                          |

Mandatory enumeration values ​​are:

```text
JCIEntity.entityType       = PiH | CiV | RaN | SYNC | PiF2 | PiF1s | PiF1t | PiF1o |
                             RoFOrg | RoFOrgRelationship | RoFTeam | RoFTeamMember |
                             RoFRole | RoleAssignment | Task | SuccessCriterion |
                             Result | Verification | Evidence | ERoFObject |
                             ChangeEvent | SyncEvent | RaNConflict | HistoricalCorrection
RaN.ruleType              = RULE | NORM | POLICY | CONSTRAINT | LAW
RaN.effect                = REQUIRE | PROHIBIT | PERMIT
RaN.scopeType             = GLOBAL | ORGANIZATION | TEAM | ENTITY
RaN.condition.combiner    = ALL | ANY
RaN.condition.clause.operator = EXISTS | NOT_EXISTS | EQUALS | NOT_EQUALS |
                                LESS_THAN | LESS_OR_EQUAL | GREATER_THAN |
                                GREATER_OR_EQUAL | IN | NOT_IN | CONTAINS | MATCHES
RaNConflict.conflictType  = PRIORITY_TIE | UNEVALUABLE
RoFOrgRelationship.type  = SUBSIDIARY | PARTNERSHIP
RoFOrg.orgType           = COMPANY | PUBLIC_ORGANIZATION | NONPROFIT |
                           ASSOCIATION | COOPERATIVE | NETWORK | OTHER
RoFTeam.teamType         = FUNCTIONAL | PROJECT | MANAGEMENT | SERVICE |
                           TEMPORARY | OTHER
RoFTeamMember.memberType = HUMAN | TECHNICAL
ERoFObject.objectType    = SYSTEM | APPLICATION | DATA | DOCUMENT | TOOL |
                           FACILITY | CONTRACT | SERVICE | OTHER
SuccessCriterion.measurementType = BOOLEAN | NUMERIC | TEXTUAL
SuccessCriterion.requirementLevel = REQUIRED | OPTIONAL
SuccessCriterion.evaluationMode   = ALL | ANY
SuccessCriterion.operator         = EQUALS | NOT_EQUALS | LESS_THAN | LESS_OR_EQUAL |
                                    GREATER_THAN | GREATER_OR_EQUAL | CONTAINS | MATCHES
PiF2.contributionMode             = ALL | ANY
PiF1s.contributionMode            = ALL | ANY
PiF1t.contributionMode            = ALL | ANY
Verification.outcome    = VALID | INVALID | INCONCLUSIVE
Task.taskKind           = ATOMIC | COMPOSITE
ChangeEvent.changeType  = CREATED | CHANGED | ACHIEVED | COMPLETED |
                          REPLACED | REVOKED | RESOLVED | HISTORICAL_CORRECTION
SyncEvent.outcome        = SUCCESS | CONFLICT | FAILED
HistoricalCorrection.correctionType = ADDITION | CORRECTION | CLARIFICATION
```

`allocation`, if specified, is between `0` and `1`. `bootstrapKey` is permitted exclusively on exactly one root `RoleAssignment` and has the immutable value `ROOT` there. The bound revisions of a `Verification` are positive integers. `ChangeEvent.id` equals the `requestId` of the accepted change request; `idempotencyKey` is unique per domain change request. `SyncEvent.runId` is unique per technical attempt. Counts of a `SyncEvent` are not negative, `completedAt` is not before `startedAt`, and `validUntil` is not before `validFrom`. For new success criteria, `requirementLevel = REQUIRED` and `evaluationMode = ALL` apply by default. Parent future elements default to `contributionMode = ALL`. For `RaN.priority`, a larger integer means higher priority. The `ruleType` does not generate automatic priority.

The following combinations apply to `SuccessCriterion.operator` depending on the measurement type:

| `measurementType` | Allowed operators                                                                        | Rule for `targetValue`                           |
| ----------------- | ---------------------------------------------------------------------------------------- | ------------------------------------------------ |
| `BOOLEAN`         | `EQUALS`, `NOT_EQUALS`                                                                   | exactly `true` or `false`                        |
| `NUMERIC`         | `EQUALS`, `NOT_EQUALS`, `LESS_THAN`, `LESS_OR_EQUAL`, `GREATER_THAN`, `GREATER_OR_EQUAL` | interpretable as a decimal number                |
| `TEXTUAL`         | `EQUALS`, `NOT_EQUALS`, `CONTAINS`, `MATCHES`                                            | not empty; at `MATCHES` valid regular expression |

**Quick example:** "Response time 24 hours or less" is stored as `measurementType = NUMERIC`, `operator = LESS_OR_EQUAL`, `targetValue = "24"` and `unit = "hours"`. This allows each implementation to evaluate the same condition.

If the value `OTHER` is used for `RoFOrg.orgType`, `RoFTeam.teamType` or `ERoFObject.objectType`, `description` must clearly explain the technical type. `OTHER` may not be used if a suitable cataloged value already exists.

#### 2.2.6 Actors and evidence

Actors are assigned exclusively via active roles in the specific team context:

| Source                 | relationship   | Target           | Targets per source | Sources per destination |
| ---------------------- | -------------- | ---------------- | -----------------: | ----------------------: |
| `JCIEntity`            | `CREATED_BY`   | `RoleAssignment` | `0..1`             | `0..n`                  |
| `ChangeEvent`          | `REQUESTED_BY` | `RoleAssignment` | `1`                | `0..n`                  |
| `HistoricalCorrection` | `CORRECTED_BY` | `RoleAssignment` | `1`                | `0..n`                  |
| `RaNConflict`          | `RESOLVED_BY`  | `RoleAssignment` | `0..1`             | `0..n`                  |

`CREATED_BY = 0..1` allows import states and the unique root `RoleAssignment`. For domain-active or completed entities, exactly one creator is required by an additional invariant, except for that root. `REQUESTED_BY` denotes the role activation that requested a change. `CORRECTED_BY` denotes the role activation responsible for a historical correction.

Evidence is stored exclusively as standalone `Evidence` nodes:

| Source                 | relationship    | Target     | Targets per source | Sources per destination |
| ---------------------- | --------------- | ---------- | -----------------: | ----------------------: |
| `Verification`         | `USES_EVIDENCE` | `Evidence` | `0..n`             | `0..n`                  |
| `ChangeEvent`          | `USES_EVIDENCE` | `Evidence` | `0..n`             | `0..n`                  |
| `HistoricalCorrection` | `USES_EVIDENCE` | `Evidence` | `0..n`             | `0..n`                  |
| `RaNConflict`          | `USES_EVIDENCE` | `Evidence` | `0..n`             | `0..n`                  |

A `HistoricalCorrection` may arise without Evidence if no independent evidence is available; the justification remains mandatory. Strings, file paths, or URLs to evidence are stored in the `reference` field of the associated `Evidence` node and are not duplicated in the occupied entity.

#### 2.2.7 Structured data formats

All complex values ​​use a technology-independent, JSON-compatible format. Objects do not have a meaningful field order; Lists only keep their order if this is technically necessary.

A `TypedValue` consists of:

```text
valueType = NULL | BOOLEAN | INTEGER | DECIMAL | STRING |
            DATE | DATETIME | OBJECT | ARRAY
value     = JSON-compatible value matching valueType
```

Decimal numbers are stored as a canonical decimal string without binary rounding. `DATE` and `DATETIME` use ISO 8601; `DATETIME` contains a time zone.

A `StateSnapshot` contains:

```text
entityType
revision
properties = Map<String, TypedValue>
```

`properties` contains all common and type-specific properties associated with the superseded state, except for the identity and time fields stored separately on `PiH`. Volatile technical runtime data is excluded.

A `RelationshipSnapshot` contains:

```text
relationshipType
direction = OUTGOING | INCOMING
otherEntityId
otherEntityType
properties = Map<String, TypedValue>
```

For each functional link that exists at the end of its validity, exactly one snapshot is saved from the perspective of the historized entity. The list is sorted into `relationshipType`, `direction` and `otherEntityId` for hashing. `contentHash` is the hexadecimal SHA-256 value of the canonically serialized combination of `StateSnapshot` and sorted `RelationshipSnapshots`.

A `TypedValueMap` assigns exactly one typed old and corrected value to each entry in `correctedFields`. `correctedFields` contains unique, lexicographically sorted canonical JSON Pointers. A historical relationship is addressed through a stable key composed of `direction`, `relationshipType` and `otherEntityId`, never through a mutable array index. For `ADDITION`, the old value is `NULL`. A correction may only change the listed paths; other snapshot content remains effectively unchanged.

The effective `HistoryView` of a `PiH` is produced by applying all non-superseded `HistoricalCorrection` objects in deterministic order to the immutable snapshot. `baseHistoryViewHash` is the hexadecimal SHA-256 value of the canonical serialization of the exact effective view on which a new correction is based.

**Short example:** If Anna's team relationship is historicized, `relationshipData` contains an outgoing or incoming edge with type `HAS_MEMBER`, the team ID, and `validFrom` and `validUntil`. A later correction names exactly this relationship path and does not replace the entire snapshot.

### 2.3 Basic structure

The simplified basic structure of the JCI model is:

```text
                         RaN
                          │ governs and constrains
                          ▼
PiH → CiV → PiF2 → PiF1s → PiF1t → PiF1o → COMPOSITE Task → ATOMIC Task → Result ← Verification
                                                │
                                                                  ├── is executed by RoleAssignments
                                                                  └── interacts with ERoFObjects (ERoF)

RoF-Modellraum:  RoFOrg → RoFTeam → RoFTeamMember → RoleAssignment
ERoF-Modellraum: RoleAssignment → ERoFObject

JCIEntity → ChangeEvent → technical SyncRun → SyncEvent
     │                                                │
     │                                                ├── EXECUTES → SYNC-Definition
     │                                                └── AFFECTS → betroffene JCIEntities
     └── previous state → PiH
```

**Quick example:** An organization wants to improve its customer service. Their values ​​(`CiV`) create a long-term picture of the future (`PiF2`), which leads to a concrete operational target state (`PiF1o`) via strategic (`PiF1s`) and tactical future states (`PiF1t`). A team member is accountable for this condition. The tasks derived from this are carried out by responsible teams and carried out through concrete role activations. The executive roles (`RoF`) interact with systems and information from the environment (`ERoF`). Rules and standards (`RaN`) provide the permissible framework. The results generated are checked based on defined success criteria. When a relevant change occurs, `SYNC` tracks the impact. The status replaced by the change is recorded as a separate `PiH`; The new status is then considered current. If further changes occur, additional `PiH` are created, so that the previous states remain traceable in their chronological order.

The representation describes an orientation and not a single linear process. `RaN`, `RoF`, `ERoF` and `SYNC` are therefore not inserted as consecutive stations in the future chain. `RoF` and `ERoF` denote model spaces; `SYNC` denotes the stored process definition. The actual relationships between the stored `JCIEntities` form a graph and can contain branches and back references.

### 2.4 Relationships between JCI entities

The following tables show the stored relationships along the JCI chain and the uniquely derived ERoF mappings. Derived relationships are explicitly marked and are not stored as additional edges.

#### 2.4.1 Purpose, values ​​and future

Reading example for `PiF1s ── CONTRIBUTES_TO ──► PiF2`: **Targets per source `1..n`** means that a `PiF1s` must contribute to at least one or more `PiF2`. **Sources per target `0..n`** means that none, one or more `PiF1s` can temporarily contribute to a `PiF2`.

| Source  | relationship           | Target                                           | Goals depending on<br>Source | Sources per<br>Target |
| ------- | ---------------------- | ------------------------------------------------ | ---------------------------: | --------------------: |
| `PiH`   | `PROVIDES_CONTEXT_TO`  | `CiV`                                            | `0..n`                       | `0..n`                |
| `CiV`   | `HELD_BY`              | `RoFOrg`, `RoFTeam`, or<br>human `RoFTeamMember` | `1`                          | `0..n`                |
| `CiV`   | `INFORMED_BY`          | `CiV`                                            | `0..n`                       | `0..n`                |
| `CiV`   | `INSCRIBES_PURPOSE_IN` | `PiF2`                                           | `0..n`                       | `1..n`                |
| `PiF1s` | `CONTRIBUTES_TO`       | `PiF2`                                           | `1..n`                       | `0..n`                |
| `PiF1t` | `CONTRIBUTES_TO`       | `PiF1s`                                          | `1..n`                       | `0..n`                |
| `PiF1o` | `CONTRIBUTES_TO`       | `PiF1t`                                          | `1..n`                       | `0..n`                |

#### 2.4.2 Operational implementation, roles and environment

Reading example for `RoleAssignment ── USES ──► ERoFObject`: **Targets per source `0..n`** means that a `RoleAssignment` can temporarily not use one, one or more `ERoFObjects`. **Sources per destination `1..n`** means that each active `ERoFObject` must be used by at least one or more `RoleAssignments` and therefore personal.

| Source           | relationship           | Target             | Goals depending on<br>Source | Sources per<br>Target |
| ---------------- | ---------------------- | ------------------ | ---------------------------: | --------------------: |
| `PiF1o`          | `HAS_SUCCESS_CRITERIA` | `SuccessCriterion` | `1..n`                       | `1`                   |
| `PiF1o`          | `ACCOUNTABLE_MEMBER`   | `RoFTeamMember`    | `1`                          | `0..n`                |
| `PiF1o`          | `DECOMPOSES_INTO`      | `Task`             | `1..n`                       | `1`                   |
| `Task`           | `DECOMPOSES_INTO`      | `Task`             | `0..n`                       | `0..1`                |
| `Task`           | `DEPENDS_ON`           | `Task`             | `0..n`                       | `0..n`                |
| `Task`           | `EXECUTED_BY`          | `RoleAssignment`   | `0..n`                       | `0..n`                |
| `Task`           | `RESPONSIBLE_TEAM`     | `RoFTeam`          | `1`                          | `0..n`                |
| `Task`           | `USES`                 | `ERoFObject`       | `0..n`                       | `0..n`                |
| `RoleAssignment` | `USES`                 | `ERoFObject`       | `0..n`                       | `1..n`                |
| `ERoFObject`     | `OWNED_BY`             | `RoFOrg`           | `0..n`                       | `0..n`                |

`HAS_MEMBER` and `HAS_ROLE` have a mandatory `validFrom: DateTime` and an optional `validUntil: DateTime` on the relationship. A `RoleAssignment` may only be valid within the temporal intersection of its team membership and role ownership. `validUntil` is never before `validFrom`.

`OWNED_BY` describes professional ownership or joint ownership. It does not replace personal use: each active `ERoFObject` must continue to be used by at least one `RoleAssignment`.

#### 2.4.3 Relationships between independent organizations

Parent companies, subsidiaries and partner companies are each stored as independent `RoFOrg`. Their different meaning arises from a `RoFOrgRelationship`, not from different organization types or additional storage as a `ERoFObject`.

| Source               | relationship     | Target           | Goals depending on<br>Source | Sources per<br>Target |
| -------------------- | ---------------- | ---------------- | ---------------------------: | --------------------: |
| `RoFOrgRelationship` | `SOURCE_ORG`     | `RoFOrg`         | `1`                          | `0..n`                |
| `RoFOrgRelationship` | `TARGET_ORG`     | `RoFOrg`         | `1`                          | `0..n`                |
| `RoFOrgRelationship` | `REPRESENTED_BY` | `RoleAssignment` | `2..n`                       | `0..n`                |

`type = SUBSIDIARY` describes a directed parent-daughter relationship from `SOURCE_ORG` to `TARGET_ORG`. A subsidiary organization can itself be the source of additional `SUBSIDIARY` relationships. `type = PARTNERSHIP` describes a professionally reciprocal relationship between independent organizations; `SOURCE_ORG` and `TARGET_ORG` are only used for clear storage. `2..n` means that an active organizational relationship requires a total of at least two representative `RoleAssignments`: at least one from each participating organization.

#### 2.4.4 Derived ERoF mappings

Reading example for the derivation `RoFOrg ── through teams, members, and RoleAssignments ──► ERoFObject`: **Targets per source `0..n`** means that for a `RoFOrg` none, one or more `ERoFObjects` can be derived from the person-bound environmental relationships. **Sources per target `1..n`** means that each active `ERoFObject` can thereby be assigned to at least one or more `RoFOrgs` without storing a direct relationship to the organization.

| Source          | Derivation                                               | Target       | Goals depending on<br>Source | Sources per<br>Target |
| --------------- | -------------------------------------------------------- | ------------ | ---------------------------: | --------------------: |
| `RoFTeamMember` | about its `RoleAssignments`                              | `ERoFObject` | `0..n`                       | `1..n`                |
| `RoFTeam`       | about members;<br>then about `RoleAssignments`           | `ERoFObject` | `0..n`                       | `1..n`                |
| `RoFOrg`        | about teams and members;<br>then about `RoleAssignments` | `ERoFObject` | `0..n`                       | `1..n`                |

#### 2.4.5 Results and testing

Reading example for `Verification ── EVALUATES ──► Result`: **Targets per source `1`** means that each `Verification` evaluates exactly one `Result`. **Sources per target `0..n`** means that a `Result` cannot yet be evaluated by none, by one or by several `Verifications`.

| Source         | relationship    | Target             | Goals depending on<br>Source | Sources per<br>Target |
| -------------- | --------------- | ------------------ | ---------------------------: | --------------------: |
| `Task`         | `PRODUCES`      | `Result`           | `0..n`                       | `1`                   |
| `Verification` | `EVALUATES`     | `Result`           | `1`                          | `0..n`                |
| `Verification` | `CHECKS`        | `SuccessCriterion` | `1`                          | `0..n`                |
| `Verification` | `USES_EVIDENCE` | `Evidence`         | `0..n`                       | `0..n`                |
| `Verification` | `SUPERSEDES`    | `Verification`     | `0..1`                       | `0..1`                |

#### 2.4.6 Rules, priority and conflicts

Reading example for `RaNConflict ── CONFLICTING_RULE ──► RaN`: **Targets per source `1..n`** means that each rule conflict names at least one affected rule. A tie in priority requires at least two rules; If the applicability cannot be evaluated, one rule can be sufficient. **Sources per destination `0..n`** means that a `RaN` can be involved in none, one or more conflicts.

| Source        | relationship       | Target                           | Goals depending on<br>Source | Sources per<br>Target |
| ------------- | ------------------ | -------------------------------- | ---------------------------: | --------------------: |
| `RaN`         | `PROTECTS`         | `CiV`                            | `0..n`                       | `0..n`                |
| `RaN`         | `PROTECTS`         | `PiF2`                           | `0..n`                       | `0..n`                |
| `RaN`         | `GOVERNS`          | permitted implementation element | `0..n`                       | `0..n`                |
| `RaN`         | `APPLIES_IN`       | `RoFOrg` or `RoFTeam`            | `0..1`                       | `0..n`                |
| `RaNConflict` | `CONFLICTING_RULE` | `RaN`                            | `1..n`                       | `0..n`                |
| `RaNConflict` | `AFFECTS`          | `JCIEntity`                      | `1..n`                       | `0..n`                |
| `RaNConflict` | `DETECTED_BY`      | `SyncEvent`                      | `1`                          | `0..n`                |
| `RaNConflict` | `RESOLVED_BY`      | `RoleAssignment`                 | `0..1`                       | `0..n`                |
| `RaNConflict` | `RESOLVED_THROUGH` | `ChangeEvent`                    | `0..1`                       | `0..n`                |
| `RaNConflict` | `USES_EVIDENCE`    | `Evidence`                       | `0..n`                       | `0..n`                |

#### 2.4.7 Change

Reading example for `ChangeEvent ── TRIGGERS ──► SyncEvent`: **Targets per source `0..n`** means that an accepted change request may have no `SyncEvent` until its first technical attempt ends and may have several after completed retry attempts. **Sources per target `1`** means that every final `SyncEvent` originates from exactly one triggering `ChangeEvent`.

`SYNC`, `SyncRun` and `SyncEvent` have different tasks: `SYNC` is the stored definition of the synchronization logic. `SyncRun` is the changeable technical running state during execution. A `SyncEvent` is only created after completion or controlled termination, documents the unchangeable result of this attempt and refers to the definition used via `EXECUTES`. `SyncRun` is not stored in the functional JCI graph.

| Source                   | relationship      | Target                    | Goals depending on<br>Source | Sources per<br>Target |
| ------------------------ | ----------------- | ------------------------- | ---------------------------: | --------------------: |
| historizable `JCIEntity` | `CHANGED_BY`      | `ChangeEvent`             | `0..n`                       | `0..1`                |
| `ChangeEvent`            | `TRIGGERS`        | `SyncEvent`               | `0..n`                       | `1`                   |
| `ChangeEvent`            | `REQUESTED_BY`    | `RoleAssignment`          | `1`                          | `0..n`                |
| `ChangeEvent`            | `USES_EVIDENCE`   | `Evidence`                | `0..n`                       | `0..n`                |
| `ChangeEvent`            | `TARGETS_HISTORY` | `PiH`                     | `0..1`                       | `0..n`                |
| `SyncEvent`              | `EXECUTES`        | `SYNC`                    | `1`                          | `0..n`                |
| `SyncEvent`              | `AFFECTS`         | `JCIEntity`               | `0..n`                       | `0..n`                |
| replaceable `JCIEntity`  | `REPLACED_BY`     | same concrete entity type | `0..1`                       | `0..n`                |

Reading example for `SyncEvent ── EXECUTES ──► SYNC`: **Targets per source `1`** means that each `SyncEvent` documents exactly one SYNC definition used. **Sources per destination `0..n`** means that a SYNC definition may not have been used in any, one or more completed synchronization attempts.

Conditional invariants apply to `CHANGED_BY`, `TARGETS_HISTORY` and `AFFECTS`: a normal change has exactly one `CHANGED_BY` source. For `CREATED`, it is absent until successful creation; the new entity then points exactly once to the `ChangeEvent`. A failed or conflicting creation has no `CHANGED_BY` source. A `ChangeEvent` with `changeType = HISTORICAL_CORRECTION` has no `CHANGED_BY` source, but exactly one `TARGETS_HISTORY` to the unchanged `PiH`; all other change types have no such relationship. A `SyncEvent` with `outcome = SUCCESS` or `CONFLICT` affects at least one existing or newly committed entity. Only a `FAILED` attempt that ends before successful target resolution may have no `AFFECTS` target.

Every accepted `ChangeEvent` must schedule at least one technical `SyncRun`. While no attempt has ended, `TRIGGERS = 0` is the correct stored intermediate state. Every completed or controlled-aborted attempt adds exactly one `TRIGGERS` relationship append-only; it is never removed or redirected.

`REPLACED_BY` connects a replaced entity with its functional successor. Source and destination have the same concrete `entityType`. An entity with `status = REPLACED` has exactly one successor; in all other statuses it has no outgoing `REPLACED_BY` relationship. A successor may merge several previous entities. The relationship must not form self-references or cycles.

**Short example:** If the rule “release from 5,000 euros” is replaced by “release from 3,000 euros”, the old `RaN` receives the status `REPLACED` and refers to the new `RaN` via `REPLACED_BY`. Both remain distinct entities; the previous state of the old rule is also recorded as `PiH`.

#### 2.4.8 Historicization

Reading example for `JCIEntity ── HAS_HISTORICAL_STATE ──► PiH`: **Targets per source `0..n`** means that a historizable `JCIEntity` cannot have one, one or more earlier states than `PiH`. **Sources per target `1`** means that each `PiH` records the detached state of exactly one `JCIEntity`.

| Source                   | relationship           | Target | Goals depending on<br>Source | Sources per<br>Target |
| ------------------------ | ---------------------- | ------ | ---------------------------: | --------------------: |
| historizable `JCIEntity` | `HAS_HISTORICAL_STATE` | `PiH`  | `0..n`                       | `1`                   |
| `SyncEvent`              | `CREATES_HISTORY`      | `PiH`  | `0..n`                       | `1`                   |

An existing `PiH` will never be overwritten. If missing, incorrect or ambiguous historical information is later discovered, a separate `HistoricalCorrection` object documents the correction. The original `PiH` remains completely intact.

| Source                 | relationship         | Target                 | Goals depending on<br>Source | Sources per<br>Target |
| ---------------------- | -------------------- | ---------------------- | ---------------------------: | --------------------: |
| `HistoricalCorrection` | `CORRECTS`           | `PiH`                  | `1`                          | `0..n`                |
| `HistoricalCorrection` | `CAUSED_BY`          | `ChangeEvent`          | `1`                          | `0..n`                |
| `SyncEvent`            | `CREATES_CORRECTION` | `HistoricalCorrection` | `0..n`                       | `1`                   |
| `HistoricalCorrection` | `SUPERSEDES`         | `HistoricalCorrection` | `0..1`                       | `0..1`                |

`CORRECTS` means the corrected `PiH`; `CAUSED_BY` captures the occasion. `CREATES_CORRECTION` assigns the correction to exactly the synchronization run that checked and generated it. `SUPERSEDES` is only used when a later correction supersedes an earlier correction of the same `PiH`. Correction chains must be forward in time and cycle-free.

##### 2.4.8.1 Process of change and historization

An accepted change request is recorded as an immutable `ChangeEvent` before its first technical attempt. Its `id` equals the `requestId`; target ID, target type, expected revision and idempotency key therefore remain traceable even if no target entity exists yet or the attempt fails. Every `ChangeEvent` schedules at least one technical `SyncRun`, which executes exactly one SYNC definition. It determines the affected `JCIEntity` instances and checks which existing state would be superseded. After completion or controlled termination, the immutable `SyncEvent` is created with its unique `runId` and outcome. Only then is `ChangeEvent ── TRIGGERS ──► SyncEvent` added append-only. The technical `SyncRun` is not stored as a JCI node.

Before the new state is adopted, the synchronization run records the previous state of the affected element, including its relationships valid at that time, as its own `PiH`. The changed state is then considered the current state. An additional `HistoricalSnapshot` is not required.

```text
current state → ChangeEvent → technical SyncRun → new current state
       │                                      │
       └── previous state ──► PiH              └── completion/termination ──► SyncEvent
                                                                         └── EXECUTES ──► SYNC
```

When a `JCIEntity` is created for the first time, no previous state exists. Therefore, `changeType = CREATED` creates no `PiH` for that entity. At acceptance, the requested target ID must be unused and `requestedRevision = null`. Only on `SUCCESS` is the new entity created atomically with `revision = 1`, `CREATED_BY` and its `CHANGED_BY` relationship. On `CONFLICT` or `FAILED`, no target node, `CHANGED_BY` or history is created; the `ChangeEvent` and final `SyncEvent` still document the attempt.

If a deviation is detected in an existing `PiH`, `SYNC` processes it as a separate correction process. Its `ChangeEvent` has `changeType = HISTORICAL_CORRECTION`, exactly one `TARGETS_HISTORY`, and no `CHANGED_BY` source. Neither the `PiH` nor a `PiH` of that `PiH` is created or changed. After successful validation, an immutable `HistoricalCorrection` is created whose `CORRECTS` points to the same `PiH`. Any resulting change to the current model is processed in a separate change process.

#### 2.4.9 Mandatory traceability

The tables in sections 2.2.6 and 2.4 together form the complete technical relationship catalog. Other relationship names are only permitted after an explicit model change. Inverse formulations are for reading only and are not saved as a second edge.

Four paths must be comprehensible for any active operational work:

| path              | Starting point                       | Binding goal                                              | Purpose                                                  |
| ----------------- | ------------------------------------ | --------------------------------------------------------- | -------------------------------------------------------- |
| WHY               | `Task`                               | at least one `CiV`                                        | explains why the work is done                            |
| WHO               | `Task`                               | `RoleAssignment`, `RoFTeamMember`, `RoFTeam` and `RoFOrg` | demonstrates execution and organizational responsibility |
| WHERE             | `Task` or executing `RoleAssignment` | used `ERoFObject` and relevant `RoFOrgRelationship`       | describes the environment touched                        |
| UNDER WHICH RULES | affected `JCIEntity`                 | all applicable `RaN`                                      | shows rules, norms and conflicts                         |

The WHY path is read backwards via the stored arrows:

```text
Task
  ◄── DECOMPOSES_INTO ── PiF1o
  ── CONTRIBUTES_TO ──► PiF1t
  ── CONTRIBUTES_TO ──► PiF1s
  ── CONTRIBUTES_TO ──► PiF2
  ◄── INSCRIBES_PURPOSE_IN ── CiV
                                      └── HELD_BY ──► RoFOrg, RoFTeam, or human RoFTeamMember
```

The WHO path connects execution and organization:

```text
Task ── EXECUTED_BY ──► RoleAssignment
                           ├── ACTIVATES_ROLE ──► RoFRole
                           └── IN_TEAM ─────────► RoFTeam ◄── HAS_TEAM ── RoFOrg
RoFTeamMember ── HAS_ASSIGNMENT ──► RoleAssignment
```

For a `ACTIVE` or `COMPLETED` atomic Task, WHY and WHO must be complete. A draft may be temporarily incomplete. `SYNC` may only activate it when each step can be clearly navigated. Environmental and control paths may be empty if neither an environmental object nor an applicable `RaN` actually exists; However, they must not appear empty due to a lack of modeling.

Adding, removing, or technically changing a saved relationship changes the relationship state of both endpoints. For each existing, changeable endpoint, the revision and `updatedAt` are increased and the previous state is recorded as a separate `PiH`. An endpoint newly created in the same order does not yet have a previous state. The `ChangeEvent` remains connected to the immediately requested origin point; all other endpoints appear above `SyncEvent ── AFFECTS`.

**Short example:** The Task “Deploy API” belongs to the operational goal “Response time under 24 hours”. Through tactical and strategic states, this contributes to the long-term goal grounded by the organization-held CiV “Clarity” and “Responsibility”. The Task is executed by Anna's Developer RoleAssignment in the responsible team. Value grounding, scope, and responsibility are therefore fully traceable from the Task.


## 3. Point in History - PiH

### 3.1 Meaning

`PiH` stands for **Point in History**. A `PiH` preserves the previous state of a historizable `JCIEntity` if this is replaced by a change.

The current `JCIEntity` does not become `PiH` itself. The synchronization run documented by a `SyncEvent` records an independent historical image of the previous state immediately before a change is adopted. This preserves:

- identity and type of the original element,
- the previous characteristics,
- the previously valid relationships and responsibilities,
- the time of historization as `recordedAt`,
- the reference to `ChangeEvent` and `SyncEvent`.

### 3.2 Origin

1. An accepted change request is recorded as an immutable `ChangeEvent`.
2. The `ChangeEvent` schedules at least one technical `SyncRun`.
3. The `SyncRun` executes exactly one saved SYNC definition.
4. The SYNC definition identifies affected elements and relationships.
5. It checks `RaN` and other model conditions.
6. If an existing state is actually superseded, the synchronization run records that state as `PiH`.
7. The changed state becomes the current state.
8. Upon completion or controlled abort, exactly one immutable `SyncEvent` with the run's unique `runId` is created and `TRIGGERS` is added append-only.
9. The `SyncEvent` documents times, results, SYNC definition used and effects of the synchronization attempt.

```text
JCIEntity ── CHANGED_BY ──► ChangeEvent ── schedules ──► technical SyncRun
                                                             │
                                                             └── completion/termination ──► SyncEvent
                                                                                         ├── EXECUTES ──► SYNC
                                                                                         ├── AFFECTS ──► JCIEntity
                                                                                         └── CREATES_HISTORY ──► PiH

JCIEntity ── HAS_HISTORICAL_STATE ──► PiH
```

### 3.3 Objects and Relationships

`PiH`, `ChangeEvent`, `SyncEvent` and `HistoricalCorrection` remain separate `JCIEntity` instances. `PiH` is a `JCIElementInstance`; the three other types are `GraphObjects`.

| Object                 | Meaning                                            |
| ---------------------- | -------------------------------------------------- |
| `ChangeEvent`          | Documents the reason and cause of the change.      |
| `SyncEvent`            | Documents the synchronization run and its effects. |
| `PiH`                  | Preserves the state replaced by the change.        |
| `HistoricalCorrection` | Corrects or adds to a `PiH` without changing it.   |

A `SyncEvent` is not a `PiH`. However, it can generate several `PiH` if a synchronization run replaces several existing states.

| Source                   | relationship           | Target                 | Targets per source | Sources per destination |
| ------------------------ | ---------------------- | ---------------------- | -----------------: | ----------------------: |
| historizable `JCIEntity` | `CHANGED_BY`           | `ChangeEvent`          | `0..n`             | `0..1`                  |
| `ChangeEvent`            | `TRIGGERS`             | `SyncEvent`            | `0..n`             | `1`                     |
| `ChangeEvent`            | `TARGETS_HISTORY`      | `PiH`                  | `0..1`             | `0..n`                  |
| `SyncEvent`              | `EXECUTES`             | `SYNC`                 | `1`                | `0..n`                  |
| `SyncEvent`              | `AFFECTS`              | `JCIEntity`            | `0..n`             | `0..n`                  |
| historizable `JCIEntity` | `HAS_HISTORICAL_STATE` | `PiH`                  | `0..n`             | `1`                     |
| `SyncEvent`              | `CREATES_HISTORY`      | `PiH`                  | `0..n`             | `1`                     |
| `HistoricalCorrection`   | `CORRECTS`             | `PiH`                  | `1`                | `0..n`                  |
| `HistoricalCorrection`   | `CAUSED_BY`            | `ChangeEvent`          | `1`                | `0..n`                  |
| `SyncEvent`              | `CREATES_CORRECTION`   | `HistoricalCorrection` | `0..n`             | `1`                     |
| `HistoricalCorrection`   | `SUPERSEDES`           | `HistoricalCorrection` | `0..1`             | `0..1`                  |
| `HistoricalCorrection`   | `CORRECTED_BY`         | `RoleAssignment`       | `1`                | `0..n`                  |
| `HistoricalCorrection`   | `USES_EVIDENCE`        | `Evidence`             | `0..n`             | `0..n`                  |

### 3.4 Rules and Exception

1. A `PiH` only arises from the already existing state of a historizable `JCIEntity`.
2. Each state replaced by an actual change is recorded as a separate `PiH`.
3. Each `PiH` belongs to exactly one original `JCIEntity`.
4. A historizable `JCIEntity` can have several `PiH` arranged in time over `recordedAt`.
5. A `PiH` is unchangeable after its creation, is not added to and is not historicized again.
6. The properties of `ChangeEvent`, `SyncEvent` and `HistoricalCorrection` are not changed or historized after creation. Only the append-only provenance additions explicitly defined for a `ChangeEvent` are permitted.
7. With `changeType = CREATED`, no `PiH` is created because no previous state exists. The `ChangeEvent` and, after every completed synchronization attempt, one `SyncEvent` are still created. Only `SUCCESS` also creates the new entity with `revision = 1` and exactly one `CHANGED_BY` relationship.
8. Any later clarification or correction is stored as a new `HistoricalCorrection` object and may not overwrite the existing `PiH`.
9. Every `HistoricalCorrection` corrects exactly one `PiH` via `CORRECTS` and belongs to exactly one `SyncEvent` via `CREATES_CORRECTION`.
10. Every `HistoricalCorrection` requires exactly one `ChangeEvent` via `CAUSED_BY`. It has `changeType = HISTORICAL_CORRECTION`, exactly one `TARGETS_HISTORY` to the same `PiH`, and no `CHANGED_BY` source. `ChangeEvent.reason` records the reported discrepancy; `HistoricalCorrection.reason` records the correction confirmed after validation.
11. Several active corrections of one `PiH` are permitted only if their `correctedFields` are pairwise disjoint.
12. If a new correction overlaps an active correction, it must supersede exactly that one correction via `SUPERSEDES`. An overlap with several active corrections is not resolved automatically.
13. A superseding correction may only supersede a correction of the same `PiH`, must include its predecessor's complete set of `correctedFields`, and must repeat all values that remain effective. Additional fields must not overlap any other active correction. `SUPERSEDES` chains are time-forward and acyclic.
14. For every path, `previousValue` must equal the value effective in the `HistoryView` immediately before the new correction; for `ADDITION`, it is `NULL`. `baseHistoryViewHash` must match that base view.
15. Before commit, `SYNC` compares the request's `expectedHistoryViewHash` with the newly calculated effective `HistoryView` hash. A mismatch produces `CONFLICT` and no correction.
16. Correction commits for the same `PiH` are serialized. After acquiring the write lock, `SYNC` calculates the effective view and overlap again to prevent lost updates.
17. The effective historical view results deterministically from the immutable `PiH` and all active, non-superseded corrections. The current model state remains separate.
18. The `ChangeEvent` connected via `CAUSED_BY` must be the same `ChangeEvent` that triggered the synchronization run connected via `CREATES_CORRECTION`.

### 3.5 Subsequent correction

A `HistoricalCorrection` is used if a deviation in content does not result from a change in status at the time, but from incorrect, incomplete or ambiguous historical documentation that was later identified.

```text
Detected historical discrepancy
                  │
                  ▼
             ChangeEvent ── TARGETS_HISTORY ──► PiH
                  │
               starts
                  ▼
          SyncRun (technical)
                  │
         completion or termination
                  ▼
              SyncEvent ── EXECUTES ──► SYNC
                  │
          CREATES_CORRECTION
                  ▼
       HistoricalCorrection
                  │
                CORRECTS
                  ▼
                 PiH
```

A `HistoricalCorrection` contains at least:

| Property              | Meaning                                                     |
| --------------------- | ----------------------------------------------------------- |
| `id`                  | unique identity of the correction                           |
| `correctionType`      | Type of correction                                          |
| `reason`              | technical justification                                     |
| `correctedAt`         | Time of capture                                             |
| `baseHistoryViewHash` | Hash of the effective historical view used as the basis     |
| `correctedFields`     | affected properties or relationships                        |
| `previousValue`       | Value effective in the `HistoryView` before this correction |
| `correctedValue`      | Information subsequently determined to be correct           |

Permissible correction types are:

```text
ADDITION      = add missing historical information
CORRECTION    = correct incorrect historical information
CLARIFICATION = explain ambiguous historical information
```

The properties of a `HistoricalCorrection` object only describe the deviation and its correction. They do not replace the corrected `PiH` nor do they constitute a completely new historical state if left unchecked.

The responsible person is connected to their specific `RoleAssignment` via `CORRECTED_BY`. Optional credentials are mapped via `USES_EVIDENCE` as standalone `Evidence` nodes. Neither actor IDs nor evidence references are additionally stored in the correction object.

### 3.6 Examples

A `PiF1o` initially reads:

> Customer inquiries will be responded to within 48 hours.

The target value is then changed to 24 hours:

```text
PiF1o: Response within 48 hours
                  │
                  │ ChangeEvent
                  ▼
                 SYNC
                  ├── previous state becomes PiH
                  └── new current state:
                      Response within 24 hours
```

The current `PiF1o` then contains the target value of 24 hours. The previous state of 48 hours remains as `PiH`.

If it is later determined through verifiable evidence that a `PiH` incompletely reflects Anna's team assignment at the time, the `PiH` remains unchanged. The missing information is documented by a separate `HistoricalCorrection` object:

```text
PiH: Anna am 10.08.2026
  ├── documented role: Developer
  └── documented team: Team A

HistoricalCorrection
  ├── correctionType: ADDITION
  ├── reason: the team assignment at the time was incompletely documented
  ├── baseHistoryViewHash: <SHA-256 of the effective view>
  ├── correctedFields: /stateData/teamB
  ├── previousValue: NULL
  ├── correctedValue: Team B
  ├── CORRECTED_BY ──► RoleAssignment: responsible reviewer
  ├── USES_EVIDENCE ──► Evidence: team assignment at that time
  └── CORRECTS ──► PiH: Anna am 10.08.2026
```

The original `PiH` still shows the historical documentation saved first. For domain evaluation, it is read together with the non-superseded `HistoricalCorrection`. A later correction of the same path must supersede this correction completely; an addition to a different path may remain active alongside it. If this results in a necessary change to Anna's current state, that change is processed independently by a new `ChangeEvent` and `SyncEvent`.

---

## 4. Core Influential Values ​​– CiV

### 4.1 Meaning

`CiV` stands for **Core Influential Values**. Each stored `CiV` instance describes exactly one fundamental value, such as clarity or responsibility, through three inseparable dimensions. It answers the question:

> Which value gives a particular future direction, and for whom does it apply?

`CiV` gives future states a grounded direction. It is itself neither a future state nor a task, rule, or role. No additional purpose statement is stored on the `CiV`; purpose becomes visible when a `PiF2` is developed from connected values.

### 4.2 Origin

A `CiV` is created when one value is explicitly described through three dimensions and assigned to exactly one value holder:

```text
NOT CiV      = What contradicts this value and is excluded?
SELF CiV     = How does the value appear in one's own identity and stance?
TO SERVE CiV = Whom or what does the value serve, and what contribution does it make?
```

The required fields `notCiV`, `selfCiV`, and `toServeCiV` represent these dimensions structurally. The value holder is not stored as free text but through exactly one `HELD_BY` relationship to a `RoFOrg`, `RoFTeam`, or human `RoFTeamMember`. A technical `RoFTeamMember` has no personal value construct.

Organizations, teams, and people may hold their own CiV, including CiV with the same name. They remain independent entities because their three dimensions and historical development may differ. A team may develop additional team-held values. Organization-held values are developed by the responsible team and acting `RoleAssignments`; `CREATED_BY`, the triggering `ChangeEvent`, and its `REQUESTED_BY` preserve human decision provenance.

When a team- or organization-held value is explicitly developed from other CiV, that provenance is stored through `INFORMED_BY`. Equal names, team membership, or organizational affiliation never create such a relationship automatically and never copy dimensions. Only explicitly selected CiV are connected to a long-term future state (`PiF2`) through `INSCRIBES_PURPOSE_IN`.

If an existing `CiV` is changed, the model records the change as `ChangeEvent`. `SYNC` checks the impact on related `PiF2` and other dependent elements. The superseded CiV state remains as `PiH`.

### 4.3 Objects and Relationships

| Object                               | Meaning                                                                   |
| ------------------------------------ | ------------------------------------------------------------------------- |
| `CiV`                                | Describes exactly one three-dimensional value of a specific value holder. |
| `PiF2`                               | Describes a long-term future state developed from connected CiV.          |
| `PiH`                                | Preserves a superseded CiV state or provides historical context.          |
| `RoFOrg`, `RoFTeam`, `RoFTeamMember` | Holds a CiV in an unambiguous scope.                                      |

| Source | relationship           | Target                                           | Targets per source | Sources per destination |
| ------ | ---------------------- | ------------------------------------------------ | -----------------: | ----------------------: |
| `PiH`  | `PROVIDES_CONTEXT_TO`  | `CiV`                                            | `0..n`             | `0..n`                  |
| `CiV`  | `HELD_BY`              | `RoFOrg`, `RoFTeam`, or<br>human `RoFTeamMember` | `1`                | `0..n`                  |
| `CiV`  | `INFORMED_BY`          | `CiV`                                            | `0..n`             | `0..n`                  |
| `CiV`  | `INSCRIBES_PURPOSE_IN` | `PiF2`                                           | `0..n`             | `1..n`                  |

```text
PiH ── PROVIDES_CONTEXT_TO ──► CiV ── HELD_BY ──► RoF scope
                                      ├── INFORMED_BY ──► another CiV
                                      └── INSCRIBES_PURPOSE_IN ──► PiF2
```

### 4.4 Rules and Exceptions

1. Each `CiV` instance describes exactly one value; `name` identifies that value.
2. `notCiV`, `selfCiV`, and `toServeCiV` are non-empty and describe distinct, jointly required dimensions of the same value.
3. Every `CiV` has exactly one `HELD_BY` relationship to a `RoFOrg`, `RoFTeam`, or `RoFTeamMember` with `memberType = HUMAN`.
4. The same value name in different scopes creates independent CiV. Values and dimensions are never inherited or copied automatically between person, team, and organization.
5. `INFORMED_BY` optionally connects a CiV to zero, one, or more other CiV that explicitly influenced its confirmed development. Self-relationships are prohibited.
6. Creation and every change of a CiV remain traceable through `CREATED_BY`, or through `ChangeEvent` and `REQUESTED_BY`, to a valid `RoleAssignment`. `SYNC` does not derive human value decisions.
7. A `CiV` may ground zero, one, or more `PiF2` through `INSCRIBES_PURPOSE_IN`. It may therefore exist before a future state has been formulated.
8. Every `PiF2` must be value-grounded by at least one `CiV`. All CiV directly grounding one `PiF2` have the same `HELD_BY` target; that shared value holder determines the scope of the `PiF2`.
9. Historical `PiH` may provide context for forming or changing a `CiV`.
10. When a `CiV`, its scope, or its `INFORMED_BY` provenance changes, `SYNC` must inspect every connected `PiF2` and dependent future and work path. Only states actually changed receive their own `PiH`.

### 4.5 Example

The organization describes the individual value “Clarity” and assigns it to itself:

```text
CiV: Clarity
  notCiV     = Decisions and responsibilities are not intentionally left unclear.
  selfCiV    = We make contexts, responsibilities, and decisions understandable.
  toServeCiV = Customers and partners receive the orientation needed for effective action.
  └── HELD_BY ──► RoFOrg: Example Ltd
```

A long-term future state is developed from this and further organization-held CiV:

```text
CiV: Clarity ── INSCRIBES_PURPOSE_IN ──► PiF2

PiF2 = In the long term, the organization provides a reliable,
       transparent and customer-oriented service.
```

When a dimension or value holder changes, `SYNC` checks the effects on this `PiF2`. The previous CiV state is recorded as `PiH` before the change.

---

## 5. Point in Future, Second Order – PiF2

### 5.1 Meaning

`PiF2` describes a long-term future state with a time horizon of more than ten years until an open point in time `n`. It formulates which long-term future is wanted from one or more explicitly connected CiV.

`PiF2` is a second-order future state. It is neither a strategy nor a task and is not immediately carried out operationally.

### 5.2 Origin

A `PiF2` is created by translating the three dimensions of one or more CiV held by the same value holder into a long-term future state. Purpose is developed in the `PiF2`, not pre-formulated as a redundant field on a CiV. Strategic future states (`PiF1s`) specify their contributions to this long-term state.

If a `PiF2` is changed, `SYNC` checks the connected `CiV`, contributing `PiF1s` and future states dependent on them. The detached state is recorded as `PiH`.

### 5.3 Objects and Relationships

| Object  | Meaning                                             |
| ------- | --------------------------------------------------- |
| `CiV`   | Grounds the `PiF2` with its three value dimensions. |
| `PiF2`  | Describes the long-term future state.               |
| `PiF1s` | Makes a strategic contribution to the `PiF2`.       |

| Source  | relationship           | Target | Targets per source | Sources per destination |
| ------- | ---------------------- | ------ | -----------------: | ----------------------: |
| `CiV`   | `INSCRIBES_PURPOSE_IN` | `PiF2` | `0..n`             | `1..n`                  |
| `PiF1s` | `CONTRIBUTES_TO`       | `PiF2` | `1..n`             | `0..n`                  |

### 5.4 Rules and Exceptions

1. Every `PiF2` must be value-grounded by at least one `CiV`.
2. All CiV directly grounding a `PiF2` have exactly the same value holder. The scope of the `PiF2` is derived from this shared `HELD_BY` target.
3. A `PiF2` may receive contributions from none, one or more `PiF1s`; `0..n` allows a draft that has not yet been fully formulated.
4. A `PiF1s` must contribute to at least one `PiF2` and can support multiple `PiF2`.
5. `PiF2` describes a state and not an activity.
6. A change to `PiF2` does not automatically change all connected elements; `SYNC` first checks the effects.
7. A `PiF2` may only reach `ACHIEVED` if at least one current `PiF1s` contributes. For `contributionMode = ALL`, all current direct contributions must be `ACHIEVED`; for `ANY` at least one current direct contribution must be `ACHIEVED`.
8. Contributing items that are not `REPLACED` or `REVOKED` are considered current. Replaced contributions will be taken into account via their `REPLACED_BY` successor as soon as it contributes to the same goal.

### 5.5 Example

```text
CiV: Clarity ── HELD_BY ──► RoFOrg: Example Ltd
  └── INSCRIBES_PURPOSE_IN ──► PiF2
                                = In the long term, the organization is established
                                  for reliable and transparent
                                  Kundenservice etabliert.
```

---

## 6. Rules and Norms – RaN

### 6.1 Meaning

`RaN` stands for **Rules and Norms** and describes rules, norms, limits and guard rails of the JCI model. A RaN protects the explicitly connected values (`CiV`) and long-term future states (`PiF2`). Through its governed implementation elements, it determines under what conditions future concretizations, tasks, results, verifications, organization, roles, and environmental interactions are permitted.

`RaN` is not a linear step of the future chain. It acts as a cross-sectional element on the respective regulated goals.

### 6.2 Origin

A `RaN` is created through the explicit formulation of a domain rule, legal requirement, internal norm, or binding limit. The rule names the CiV and PiF2 to protect, its effect, the governed decision, its scope, the affected implementation types, and a machine-readable condition. `PROTECTS` documents what and why is protected; `GOVERNS` connects the concrete implementation where the rule is enforced.

A draft may initially exist without a target. Before a `RaN` becomes active, it must protect at least one CiV and one PiF2 and govern at least one implementation element. If an existing `RaN` changes, `SYNC` checks all protected and governed targets and their dependent elements. The superseded RaN state is recorded as `PiH`.

Each `RaN` is explicitly given an integer priority. A larger number means higher priority. The value describes the technically decided priority in the event of an actual contradiction; it is not derived from `ruleType` nor from the name or position in the graph.

`decisionKey` stably denotes the settled decision, for example `Task.status.COMPLETED` or `ERoFObject.action.MODIFY`. Only rules with the same `decisionKey`, overlapping scope and at least one common target can conflict with each other for this decision.

The machine-readable `condition` has exactly one `combiner = ALL | ANY` and at least one clause. Each clause contains:

| field      | Meaning                                                            |
| ---------- | ------------------------------------------------------------------ |
| `path`     | unique property or relationship path from the governed target      |
| `operator` | mandatory comparison operator                                      |
| `value`    | comparative value; only not required for `EXISTS` and `NOT_EXISTS` |

Paths are allowed to traverse properties directly or explicitly named relationships from the canonical relationship catalog. Unlimited or uncataloged traversals are not permitted. If a path cannot be evaluated clearly, the rule is `UNEVALUABLE`.

The effect is read like this:

| `effect`   | condition true   | Condition false |
| ---------- | ---------------- | --------------- |
| `REQUIRE`  | Decision allowed | Decision denied |
| `PROHIBIT` | Decision denied  | no own decision |
| `PERMIT`   | Decision allowed | no own decision |

A single refusal is a rule violation and not a `RaNConflict`. An actual contradiction only arises when applicable rules with the same `decisionKey` simultaneously allow and deny the same specific decision.

### 6.3 Objects and Relationships

| Relationship | Area                        | Permitted targets                                        |
| ------------ | --------------------------- | -------------------------------------------------------- |
| `PROTECTS`   | value                       | `CiV`                                                    |
| `PROTECTS`   | long-term future            | `PiF2`                                                   |
| `GOVERNS`    | future concretization       | `PiF1s`, `PiF1t`, `PiF1o`                                |
| `GOVERNS`    | work                        | `Task`                                                   |
| `GOVERNS`    | success and verification    | `SuccessCriterion`, `Result`, `Verification`, `Evidence` |
| `GOVERNS`    | organization                | `RoFOrg`, `RoFTeam`, `RoFTeamMember`                     |
| `GOVERNS`    | organizational relationship | `RoFOrgRelationship`                                     |
| `GOVERNS`    | roles                       | `RoFRole`, `RoleAssignment`                              |
| `GOVERNS`    | environment                 | `ERoFObject`                                             |

The relationships are stored as follows:

```text
RaN ── PROTECTS ──► CiV or PiF2
RaN ── GOVERNS ──► governed JCI element or GraphObject
RaN ── APPLIES_IN ──► RoFOrg or RoFTeam
```

| Source | relationship | Target                           | Targets per source | Sources per destination |
| ------ | ------------ | -------------------------------- | -----------------: | ----------------------: |
| `RaN`  | `PROTECTS`   | `CiV` or `PiF2`                  | `0..n`             | `0..n`                  |
| `RaN`  | `GOVERNS`    | permitted implementation element | `0..n`             | `0..n`                  |
| `RaN`  | `APPLIES_IN` | `RoFOrg` or `RoFTeam`            | `0..1`             | `0..n`                  |

Cardinality `0..n` applies to stored relationships and permits incomplete drafts. An active `RaN` has at least one `PROTECTS` to a CiV, at least one `PROTECTS` to a PiF2, and at least one current target via `GOVERNS`. Each protected CiV grounds at least one PiF2 protected by the same RaN; each protected PiF2 is grounded by at least one CiV protected by the same RaN. The RaN need not protect every other CiV of that PiF2. `SYNC` keeps the governed target set current for new, changed, or out-of-scope entities; protection relationships are set only through human-confirmed changes.

The following rules apply to the scope:

| `scopeType`    | `APPLIES_IN`          | Meaning                                                                  |
| -------------- | --------------------- | ------------------------------------------------------------------------ |
| `GLOBAL`       | no relationship       | applies model-wide to suitable `governedTypes`                           |
| `ORGANIZATION` | exactly one `RoFOrg`  | applies within the organization that can be derived from teams and roles |
| `TEAM`         | exactly one `RoFTeam` | applies in the specified team context                                    |
| `ENTITY`       | no relationship       | applies exclusively to the entities directly connected via `GOVERNS`     |

The protection scope must be organizationally compatible with the area of application. `GLOBAL` may connect protection targets from different scopes. For `ORGANIZATION`, the value holders of protected CiV or PiF2 lie within the same organization, its teams, or its human members. For `TEAM`, they may identify the team, a valid human team member, or the parent organization. For `ENTITY`, the protected CiV and PiF2 must be reachable through the WHY path of the directly governed implementation elements. Unconnected external organizations are prohibited.

If several active and time-valid `RaN` target the same goal or the same decision, `SYNC` first checks their applicability and then their compatibility:

```text
anwendbare RaN bestimmen
        │
        ├── compatible ──► apply all rules together
        │
        └── contradictory
                ├── different priority ──► higher priority takes precedence
                └── same priority ─────────────► RaNConflict with status = OPEN
```

A lower priority rule remains active in a priority case and continues to apply wherever there is no contradiction to the higher priority rule. If `SYNC` cannot clearly determine the applicability or compatibility, an open `RaNConflict` with `conflictType = UNEVALUABLE` is also created; a mere uncertainty must not be ignored by priority.

A `RaNConflict` documents the rules involved, affected entities and the recognizing synchronization run. It is not automatically decided by `SYNC`. To resolve it, an authorized `RoleAssignment` must initiate an explicit technical change, for example specifying a rule, changing its scope or priority, or replacing or repealing a rule. Only a subsequent successful synchronization run, which no longer detects any ongoing contradictions, may set the conflict via `RESOLVED_BY` and `RESOLVED_THROUGH` to `RESOLVED`. The previous open state is recorded as `PiH`.

### 6.4 Rules and Exceptions

1. `RaN` is a cross-sectional element and not part of the linear future chain.
2. A RaN draft may lack complete protection or governance targets.
3. An active `RaN` protects at least one `CiV` and at least one `PiF2` and governs at least one permitted implementation element.
4. Each protected CiV grounds at least one PiF2 protected by the same RaN via `INSCRIBES_PURPOSE_IN`.
5. Each protected PiF2 is grounded by at least one CiV protected by the same RaN.
6. A RaN need not protect every CiV of a protected PiF2.
7. `PROTECTS` targets only `CiV` or `PiF2`. `GOVERNS` targets only the defined implementation elements.
8. A `RaN` may govern multiple implementation elements from different areas. A target may simultaneously be governed by zero, one, or more rules.
9. When a `RaN` changes, `SYNC` checks all directly protected and governed targets and their relevant dependencies.
10. `PROTECTS` is created or changed only through an explicit domain decision traceable to a valid `RoleAssignment`. `SYNC` does not infer it from names, scope, or existing paths.
11. Protection targets and area of application satisfy the defined organizational scope compatibility; unconnected external organizations are prohibited.
12. Before comparison, only active, temporally valid `RaN` applicable to the affected entity or decision are considered.
13. Compatible applicable rules apply together and are not ignored merely because of lower priority.
14. If applicable rules conflict with different `priority`, the larger number prevails for exactly that conflict. `ruleType` creates no automatic precedence.
15. If at least two applicable rules with the same highest relevant priority conflict, `SYNC` creates exactly one open `RaNConflict` for that conflict set and decision.
16. If compatibility or applicability cannot be evaluated unambiguously, `SYNC` creates an open `RaNConflict` with `conflictType = UNEVALUABLE` and makes no automatic decision.
17. An open `RaNConflict` has a `conflictKey` deterministic for change request, rule set, and decision, names at least one `CONFLICTING_RULE`, at least one affected `JCIEntity`, and exactly the detecting `SyncEvent`. `PRIORITY_TIE` requires at least two rules; `UNEVALUABLE` may involve one rule that cannot be evaluated unambiguously. The same synchronization request must not create the same conflict repeatedly.
18. A conflict may be set to `RESOLVED` only through an explicit domain change and a subsequent successful synchronization run. It then has exactly one `RESOLVED_BY` and one `RESOLVED_THROUGH`.
19. Resolution does not retroactively change the recorded `SyncEvent`; the conflict status change is historized like any other domain change.
20. `governedTypes` is not empty. Every `GOVERNS` target has a concrete `entityType` listed in it.
21. `GLOBAL` and `ENTITY` have no `APPLIES_IN`; `ORGANIZATION` and `TEAM` have exactly one type-correct `APPLIES_IN` relationship.
22. An unmet applicable `REQUIRE` or a met `PROHIBIT` blocks the decision as a rule violation even if no other rule conflicts.
23. Priority is used only when the same decision is simultaneously allowed and denied. Two denying or two allowing rules are not a priority conflict.
24. `PROTECTS` replaces neither `GOVERNS` nor `APPLIES_IN`; all three relationships have separate, jointly required functions.

### 6.5 Example

A rule limits which roles are allowed to change a specific system:

```text
RaN = Only authorized roles may modify the production system.
  effect = PROHIBIT
  decisionKey = ERoFObject.action.MODIFY
  scopeType = ORGANIZATION
  governedTypes = [RoFRole, RoleAssignment, ERoFObject]
  condition = ALL(
    path = executingRole.roleName,
    operator = NOT_IN,
    value = [Security, Administrator]
  )
  │
  ├── PROTECTS ──► CiV: Security
  ├── PROTECTS ──► PiF2: trusted and resilient organization
  ├── GOVERNS ──► RoFRole
  ├── GOVERNS ──► RoleAssignment
  └── GOVERNS ──► ERoFObject: Produktivsystem
```

If the rule is changed, `SYNC` checks the affected role activations and environmental interactions. Only states that have actually changed are recorded as separate `PiH`.

If two additional rules apply to the same productive system, the following applies, for example:

```text
RaN A: Changes only by Security role, priority = 80
RaN B: Changes by all Developers,      priority = 50
```

In the event of a contradiction, `RaN A` takes precedence; `RaN B` remains applicable outside of this contradiction. If both rules have `priority = 80`, `SYNC` creates an open `RaNConflict` and does not automatically make a change based on this conflict.

---

## 7. Point in Future, First Order – Strategic – PiF1s

### 7.1 Meaning

`PiF1s` describes a strategic future state with a time horizon of more than five to ten years inclusive. It formulates which strategic state contributes to one or more `PiF2`.

`PiF1s` is a first-order state and not a strategy activity or task.

### 7.2 Origin

A `PiF1s` is created through the strategic specification of one or more long-term `PiF2`. Tactical future states (`PiF1t`) then describe their contributions to this strategic state.

When a `PiF1s` is changed, `SYNC` checks the connected `PiF2`, contributing `PiF1t` and other dependent elements. The detached state is recorded as `PiH`.

### 7.3 Objects and Relationships

| Object  | Meaning                                       |
| ------- | --------------------------------------------- |
| `PiF2`  | Long-term future state.                       |
| `PiF1s` | Strategic future state.                       |
| `PiF1t` | Makes a tactical contribution to the `PiF1s`. |

| Source  | relationship     | Target  | Targets per source | Sources per destination |
| ------- | ---------------- | ------- | -----------------: | ----------------------: |
| `PiF1s` | `CONTRIBUTES_TO` | `PiF2`  | `1..n`             | `0..n`                  |
| `PiF1t` | `CONTRIBUTES_TO` | `PiF1s` | `1..n`             | `0..n`                  |

### 7.4 Rules and Exceptions

1. Each `PiF1s` must contribute to at least one `PiF2`.
2. One `PiF1s` can contribute to multiple `PiF2` at the same time.
3. A `PiF1s` may receive contributions from none, one or more `PiF1t`; `0..n` allows a draft that has not yet been fully formulated.
4. `PiF1s` describes a strategic state and not an activity to be carried out.
5. Changes are checked for impact by `SYNC` in both directions of the connected future graph.
6. A `PiF1s` may only reach `ACHIEVED` if at least one current `PiF1t` contributes. `ALL` requires all current direct contributions in `ACHIEVED`; `ANY` requires at least one.

### 7.5 Example

```text
PiF1s = A uniform and scalable service organization
         is established across the organization.
   │
   └── CONTRIBUTES_TO ──► PiF2
```

---

## 8. Point in Future, First Order – Tactical – PiF1t

### 8.1 Meaning

`PiF1t` describes a tactical future state with a time horizon from one year up to and including five years. It formulates which tactical state contributes to one or more strategic `PiF1s`.

`PiF1t` is a condition and not an action plan or Task.

### 8.2 Origin

A `PiF1t` is created through the tactical specification of one or more `PiF1s`. Operational future states (`PiF1o`) then describe their contributions to this tactical state.

When a `PiF1t` is changed, `SYNC` checks the connected `PiF1s`, contributing `PiF1o` and other dependent elements. The detached state is recorded as `PiH`.

### 8.3 Objects and Relationships

| Object  | Meaning                                           |
| ------- | ------------------------------------------------- |
| `PiF1s` | Strategic future state.                           |
| `PiF1t` | Tactical future state.                            |
| `PiF1o` | Makes an operational contribution to the `PiF1t`. |

| Source  | relationship     | Target  | Targets per source | Sources per destination |
| ------- | ---------------- | ------- | -----------------: | ----------------------: |
| `PiF1t` | `CONTRIBUTES_TO` | `PiF1s` | `1..n`             | `0..n`                  |
| `PiF1o` | `CONTRIBUTES_TO` | `PiF1t` | `1..n`             | `0..n`                  |

### 8.4 Rules and Exceptions

1. Each `PiF1t` must contribute to at least one `PiF1s`.
2. One `PiF1t` can contribute to multiple `PiF1s` at the same time.
3. A `PiF1t` may receive contributions from none, one or more `PiF1o`; `0..n` allows a draft that has not yet been fully formulated.
4. `PiF1t` describes a tactical state and not an activity.
5. Changes are reviewed by `SYNC` for strategic and operational impact.
6. A `PiF1t` may only reach `ACHIEVED` if at least one current `PiF1o` contributes. `ALL` requires all current direct contributions in `ACHIEVED`; `ANY` requires at least one.

### 8.5 Example

```text
PiF1t = All service areas work with a uniform
         responsibility and processing model.
   │
   └── CONTRIBUTES_TO ──► PiF1s
```

---

## 9. Point in Future, First Order – Operational – PiF1o

### 9.1 Meaning

`PiF1o` describes a concrete, achievable operational future state with a time horizon of less than one year. He formulates what should be achieved. The activity required for this is modeled separately as `Task`.

```text
PiF1o       = What state should be achieved?
Task        = What must be done to achieve it?
Result      = What did the Task produce?
Verification = Does the Result satisfy the SuccessCriterion?
```

### 9.2 Origin

A `PiF1o` is created through the operational specification of one or more `PiF1t`. For each `PiF1o`, at least one `SuccessCriterion`, exactly one responsible `RoFTeamMember` and at least one `Task` are defined.

Each Task is assigned to exactly one responsible `RoFTeam` and typed as `ATOMIC` or `COMPOSITE`. An atomic Task is immediately executable and is executed in `ACTIVE` or `COMPLETED` by at least one `RoleAssignment`. At least one of these RoleAssignments belongs to the responsible team; additional RoleAssignments from other teams can provide support. A composite Task, on the other hand, bundles at least one subordinate Task and has no execution, environmental use, or result production of its own. The team member assigned to the `PiF1o` via `ACCOUNTABLE_MEMBER` is allowed to execute atomic tasks, but does not have to be one of the people executing them.

Tasks can name other tasks via `DEPENDS_ON` as prerequisites. As long as at least one prerequisite is not `COMPLETED`, the dependent Task is `BLOCKED`. An atomic Task can use `ERoFObjects` and produce `Results`. A `Verification` evaluates a completed `Result` against an active `SuccessCriterion` belonging to the same `PiF1o`. It stores the exact target revisions as `evaluatedResultRevision` and `checkedCriterionRevision`. If the same combination is tested again, a new `Verification` is created and may supersede its immediate predecessor via `SUPERSEDES`.

When a `PiF1o` or a related operational graph object is changed, `SYNC` checks the impact on future contributions, success criteria, responsibility, tasks, role activations, environmental objects, results and audits. Only states that have actually been replaced are recorded as separate `PiH`.

### 9.3 Objects and Relationships

| Object             | Meaning                                                             |
| ------------------ | ------------------------------------------------------------------- |
| `PiF1t`            | Tactical future state.                                              |
| `PiF1o`            | Operational future state.                                           |
| `SuccessCriterion` | Criterion for successful implementation.                            |
| `RoFTeamMember`    | Member responsible for the `PiF1o`.                                 |
| `Task`             | Atomic activity or composite work structure to realize the `PiF1o`. |
| `RoleAssignment`   | Active role through which a Task is executed.                       |
| `ERoFObject`       | Concrete environmental object used at work.                         |
| `Result`           | Result generated by a Task.                                         |
| `Verification`     | Checking a result against a success criterion.                      |
| `Evidence`         | Optional, separately managed proof.                                 |

| Source           | relationship           | Target             | Targets per source | Sources per destination |
| ---------------- | ---------------------- | ------------------ | -----------------: | ----------------------: |
| `PiF1o`          | `CONTRIBUTES_TO`       | `PiF1t`            | `1..n`             | `0..n`                  |
| `PiF1o`          | `HAS_SUCCESS_CRITERIA` | `SuccessCriterion` | `1..n`             | `1`                     |
| `PiF1o`          | `ACCOUNTABLE_MEMBER`   | `RoFTeamMember`    | `1`                | `0..n`                  |
| `PiF1o`          | `DECOMPOSES_INTO`      | `Task`             | `1..n`             | `1`                     |
| `Task`           | `DECOMPOSES_INTO`      | `Task`             | `0..n`             | `0..1`                  |
| `Task`           | `DEPENDS_ON`           | `Task`             | `0..n`             | `0..n`                  |
| `Task`           | `EXECUTED_BY`          | `RoleAssignment`   | `0..n`             | `0..n`                  |
| `Task`           | `RESPONSIBLE_TEAM`     | `RoFTeam`          | `1`                | `0..n`                  |
| `Task`           | `USES`                 | `ERoFObject`       | `0..n`             | `0..n`                  |
| `RoleAssignment` | `USES`                 | `ERoFObject`       | `0..n`             | `1..n`                  |
| `Task`           | `PRODUCES`             | `Result`           | `0..n`             | `1`                     |
| `Verification`   | `EVALUATES`            | `Result`           | `1`                | `0..n`                  |
| `Verification`   | `CHECKS`               | `SuccessCriterion` | `1`                | `0..n`                  |
| `Verification`   | `USES_EVIDENCE`        | `Evidence`         | `0..n`             | `0..n`                  |
| `Verification`   | `SUPERSEDES`           | `Verification`     | `0..1`             | `0..1`                  |

```text
PiF1o
  ├── HAS_SUCCESS_CRITERIA ──► SuccessCriterion ◄── CHECKS ── Verification
  ├── ACCOUNTABLE_MEMBER ──► RoFTeamMember
  └── DECOMPOSES_INTO ──► COMPOSITE Task
                                  ├── RESPONSIBLE_TEAM ──► RoFTeam
                                  └── DECOMPOSES_INTO ──► ATOMIC Task ── PRODUCES ──► Result
                                                               ├── DEPENDS_ON ──► Task
                                                               ├── EXECUTED_BY ──► RoleAssignment
                                                               └── USES ──► ERoFObject
```

### 9.4 Rules and Exceptions

1. Each `PiF1o` must contribute to at least one `PiF1t` and can support multiple `PiF1t`.
2. Each `PiF1o` has at least one `SuccessCriterion`.
3. Each `PiF1o` is assigned to exactly one responsible `RoFTeamMember`.
4. Each `PiF1o` is broken down into at least one `Task`; Each Task is directly assigned to exactly one `PiF1o`, regardless of its hierarchy level.
5. Each Task has exactly one `taskKind = ATOMIC | COMPOSITE` and exactly one responsible `RoFTeam`.
6. A `ATOMIC`-Task has no child tasks. In `ACTIVE` or `COMPLETED` it has at least one executive `RoleAssignment`; at least one of them belongs to the responsible team via `IN_TEAM`.
7. A `COMPOSITE`-Task has at least one direct subtask and no `EXECUTED_BY`, `USES` or `PRODUCES` relationships. Its status is derived exclusively from the direct subtasks.
8. A Task can have at most one direct parent Task. Parent Task and subtask belong to the same `PiF1o`; the Task hierarchy is cycle-free.
9. Additional `RoleAssignments` from other teams may support an atomic Task.
10. The `ACCOUNTABLE_MEMBER` of a `PiF1o` may execute its atomic tasks, but does not have to belong to an executing `RoleAssignment`.
11. Accountability for the `PiF1o`, team responsibility for the Task and the actual execution of atomic tasks by `RoleAssignments` remain technically separate.
12. An atomic Task can have none, one or more relationships with `ERoFObjects`. If he uses an environment object, at least one executing `RoleAssignment` must use the same `ERoFObject`.
13. `DEPENDS_ON` may exist between tasks of the same or different `PiF1o`, but may not form self-references or cycles. One requirement is only met with `status = COMPLETED`.
14. If a Task has at least one unfulfilled prerequisite, its status is `BLOCKED`. `REPLACED` or `REVOKED` does not meet a requirement; a valid successor must be explicitly reconnected via `DEPENDS_ON`.
15. An atomic Task may only achieve `COMPLETED` if all prerequisites are completed, at least one valid executing RoleAssignment is on the responsible team, relevant `RaN` are met and completion is confirmed. A `Result` is not mandatory for every Task.
16. The status of a composite task is derived from its effective direct subtasks: only `DRAFT` gives `DRAFT`; all `COMPLETED` result in `COMPLETED`; at least one `ACTIVE` results in `ACTIVE`; a mixture of `DRAFT` and `COMPLETED` produces `ACTIVE`; without `ACTIVE`, but with at least one `BLOCKED`, results in `BLOCKED`. A `REPLACED` subtask is only replaced by its successor if it is connected via `REPLACED_BY` and is also a direct subtask of the same composite task. A `REVOKED` subtask that remains connected or a `REPLACED` subtask without such a connected successor creates a conflict.
17. An atomic Task may not yet have produced one, one or more `Results`; each Result belongs to exactly one atomic Task.
18. A `Verification` evaluates exactly one `Result`, checks exactly one `SuccessCriterion`, and may only be created when the Result is `COMPLETED`, the criterion is `ACTIVE`, and both belong to the same `PiF1o` context.
19. `evaluatedResultRevision` equals the current revision of the evaluated Result; `checkedCriterionRevision` equals the current revision of the checked SuccessCriterion. `SYNC` reads both from one consistent view and checks them again immediately before commit.
20. The test result is stored on `Verification` as `VALID`, `INVALID` or `INCONCLUSIVE`.
21. `Evidence` is used only as a separate node when evidence must be managed, reused or audited independently.
22. `PiF1o` is a state and never itself a Task.
23. A PiF1o draft is only domain-complete when its future contribution, success criteria, accountability and tasks exist.
24. A `Verification` is current and applicable only if it has not been superseded and its bound revisions still match the current revisions of Result and criterion.
25. A later change to the Result or criterion does not change the immutable `Verification`. It remains as a test fact but is no longer applicable to the new state; until a new test exists, the affected criterion is not satisfied by that verification.
26. `SUPERSEDES` only connects Verifications that evaluate the same `Result` and check the same `SuccessCriterion`. A successor's bound target revisions may not be lower than those of its predecessor; equal revisions are permitted for retesting with a new method or Evidence. The chain is time-forward and acyclic.
27. For the same combination of Result, SuccessCriterion and both bound revisions, at most one non-superseded `Verification` exists.
28. `verifiedAt` is not earlier than `updatedAt` of either bound target revision.
29. Each `PiF1o` has at least one `SuccessCriterion` with `requirementLevel = REQUIRED`.
30. A `PiF1o` may only reach `ACHIEVED` if all mandatory success criteria are satisfied by applicable current Verifications, all assigned Tasks are `COMPLETED`, all Task dependencies are satisfied, and no relevant model or `RaN` violation exists.
31. `ACHIEVED` is terminal. A later goal or criterion change is modeled as a new operational future element.

#### 9.4.1 Aggregation of success criteria

For each `SuccessCriterion`, `requirementLevel = REQUIRED | OPTIONAL` and `evaluationMode = ALL | ANY` apply. Unless expressly stated otherwise, `REQUIRED` and `ALL` apply.

For `evaluationMode = ALL`, the criterion is satisfied if at least one applicable current `Verification` exists and all applicable current Verifications have `outcome = VALID`. For `evaluationMode = ANY`, at least one applicable current Verification with `outcome = VALID` is sufficient. `INVALID`, `INCONCLUSIVE`, a missing applicable Verification, or only revision-stale Verifications do not satisfy a criterion; with `ALL`, one non-valid applicable outcome already prevents satisfaction.

```text
ALL: VALID + VALID        = satisfied
ALL: VALID + INVALID      = not satisfied
ALL: VALID + INCONCLUSIVE = not satisfied
ANY: VALID + INVALID      = satisfied
ANY: INVALID + INVALID    = not satisfied
no applicable current Verification = not satisfied
only revision-stale Verifications = not satisfied
```

The criteria condition of a `PiF1o` is satisfied if all of its `REQUIRED` criteria are satisfied. `OPTIONAL` criteria are evaluated and documented, but do not block `ACHIEVED`. Only applicable current Verifications evaluating Results from Tasks of the same `PiF1o` are considered. All Task and model conditions must also be satisfied for `ACHIEVED`.

The measured value of a Verification is determined from the evaluated `Result` according to the method specified in the success criterion and compared with `operator`, `targetValue` and, if applicable, `unit`. `outcome = VALID` is only allowed if this comparison is successful and reproducible using the specified method. If no clear comparison is possible, the result is `INCONCLUSIVE`.

```text
PiF1o.ACHIEVED
= at least one REQUIRED criterion exists
+ all REQUIRED criteria satisfied
+ all assigned Tasks COMPLETED
+ all Task dependencies satisfied
+ all considered Verifications completed and revision-applicable
+ no relevant model or RaN violation
```

### 9.5 Example

“Develop customer portal” refers to an activity and is therefore saved as a composite Task. The associated `PiF1o` describes the state achieved:

```text
PiF1o: The customer portal is usable in production.
  └── DECOMPOSES_INTO ──► COMPOSITE Task: Develop customer portal
                              ├── DECOMPOSES_INTO ──► ATOMIC Task: Implement user interface
                              ├── DECOMPOSES_INTO ──► ATOMIC Task: Provide API
                              ├── DECOMPOSES_INTO ──► ATOMIC Task: Set up database
                              ├── DECOMPOSES_INTO ──► ATOMIC Task: Test portal
                              │                              └── DEPENDS_ON ──► Provide API
                              └── DECOMPOSES_INTO ──► ATOMIC Task: Publish portal
                                                             └── DEPENDS_ON ──► Test portal
```

All tasks also remain directly connected to this `PiF1o`. This means that the WHY path from each atomic Task to the operational state remains short, while `DECOMPOSES_INTO` represents the work structure between tasks.

```text
PiF1o = At least 95% of customer inquiries are answered
         within 24 hours.
   │
   ├── CONTRIBUTES_TO ──► PiF1t
   ├── HAS_SUCCESS_CRITERIA ──►
   │      SuccessCriterion = Response time at most 24 hours
   ├── ACCOUNTABLE_MEMBER ──► RoFTeamMember: Jana
   └── DECOMPOSES_INTO ──► Task
             ├── RESPONSIBLE_TEAM ──► RoFTeam: Development
             ├── EXECUTED_BY ──► RoleAssignment: Ernst as Developer in Engineering
             ├── EXECUTED_BY ──► RoleAssignment: Anna as Tester in Quality Assurance
             ├── USES ──► ERoFObject: Ticketsystem
             └── PRODUCES ──► Result: answered request
                                      ◄── EVALUATES ── Verification
                                               └── CHECKS ──► SuccessCriterion
```

Jana remains accountable for the `PiF1o`, even though Ernst and Anna execute the Task. The development team is responsible for the Task; at least one of its `RoleAssignments` must participate in execution. The `Verification` stores `VALID`, `INVALID` or `INCONCLUSIVE` together with the exact revisions of the evaluated Result and checked criterion. A separate `Evidence` node is created only if the evidence must be managed independently. If Result or criterion changes later, the prior Verification remains traceable but no longer counts toward current target achievement. `SYNC` sets the `PiF1o` to `ACHIEVED` only when all mandatory criteria are satisfied according to their evaluation modes.

---

## 10. Roles and Functions – RoF

### 10.1 Meaning

`RoF` stands for **Roles and Functions** and describes the organizational ability to act in the JCI model. It organizes independent organizations, their relationships, teams, members, roles and the concrete activation of a role in a team.

`RoF` is one of the ten functional JCI core elements, but is not stored as a separate node. The RoF model space is fully concretized by `RoFOrg`, `RoFOrgRelationship`, `RoFTeam`, `RoFTeamMember`, `RoFRole`, `RoleAssignment` and their relationships. An additional `RoF` node would only combine the same connections redundantly.

A `RoFOrg` is always an organization capable of acting independently. Parent companies, subsidiaries and partner companies are therefore each modeled as separate `RoFOrg`. Their relationship to each other is described by a typified `RoFOrgRelationship`.

`RoF` specifically answers:

- In which organization does the work take place?
- Which team has operational responsibility?
- Which member is responsible for a future state?
- What roles does the member have?
- What role is active for the member in a specific team?
- Which independent organizations are related to each other as mother, daughter or partner?
- Which distinct values are held by an organization, team, or human?

### 10.2 Origin

A `RoFOrg` forms the organizational framework for operational work. One or more `RoFTeams` are assigned to it. A team owns at least one `RoFTeamMember`; a member can belong to multiple teams.

A `RoFOrgRelationship` is created when two independent `RoFOrg`s have a technically relevant organizational relationship. `SUBSIDIARY` describes a directed mother-daughter relationship. `PARTNERSHIP` describes a two-way partnership between independent organizations. A subsidiary organization can own other subsidiary organizations and enter into its own partnerships.

Every active organizational relationship is personally supported by at least one `RoleAssignment` from each participating organization. Teams, members and roles are derived via this `RoleAssignments` and are not additionally saved directly to the organizational relationship.

A member's roles are saved once via `HAS_ROLE`, regardless of the team context. If the member is to perform one of his roles in a specific team, a separate `RoleAssignment` is created for this purpose. This connects the member with exactly one team and activates exactly one role from his role inventory.

An organization-held CiV is assigned to the `RoFOrg` through `HELD_BY`, even when an executive or other mandated team develops the value. A team-held CiV points to the respective `RoFTeam`; a personal CiV points to a `RoFTeamMember` with `memberType = HUMAN`. The value holder and the roles acting in its development therefore remain separate: `HELD_BY` states whose value it is; `CREATED_BY` and `REQUESTED_BY` state who created or changed it in the model.

If a RoF element, an organizational assignment or a `RoFOrgRelationship` is changed, `SYNC` checks both organizations involved, their representative role activations, affected future states, tasks, rules and environmental relationships. States that have actually been replaced are recorded as separate `PiH`.

### 10.3 Objects and Relationships

| Object               | Meaning                                                   |
| -------------------- | --------------------------------------------------------- |
| `RoFOrg`             | Organization capable of acting independently.             |
| `RoFOrgRelationship` | Typed and personal relationship between two `RoFOrg`.     |
| `RoFTeam`            | Organizational or functional group.                       |
| `RoFTeamMember`      | Capable human or technical actor.                         |
| `RoFRole`            | Role, function and responsibilities of a member.          |
| `RoleAssignment`     | Activation of a member's role in a team.                  |
| `CiV`                | Individual value held by an organization, team, or human. |

Reading example for `RoFOrg ── HAS_TEAM ──► RoFTeam`: **Targets per source `1..n`** means that each `RoFOrg` has at least one team; **Sources per destination `1`** means that each `RoFTeam` is assigned to exactly one `RoFOrg`.

| Source           | relationship         | Target                                           | Targets per source | Sources per destination |
| ---------------- | -------------------- | ------------------------------------------------ | -----------------: | ----------------------: |
| `RoFOrg`         | `HAS_TEAM`           | `RoFTeam`                                        | `1..n`             | `1`                     |
| `RoFTeam`        | `HAS_MEMBER`         | `RoFTeamMember`                                  | `1..n`             | `1..n`                  |
| `RoFTeamMember`  | `HAS_ROLE`           | `RoFRole`                                        | `1..n`             | `0..n`                  |
| `RoFTeamMember`  | `HAS_ASSIGNMENT`     | `RoleAssignment`                                 | `0..n`             | `1`                     |
| `RoleAssignment` | `IN_TEAM`            | `RoFTeam`                                        | `1`                | `0..n`                  |
| `RoleAssignment` | `ACTIVATES_ROLE`     | `RoFRole`                                        | `1`                | `0..n`                  |
| `PiF1o`          | `ACCOUNTABLE_MEMBER` | `RoFTeamMember`                                  | `1`                | `0..n`                  |
| `Task`           | `RESPONSIBLE_TEAM`   | `RoFTeam`                                        | `1`                | `0..n`                  |
| `Task`           | `EXECUTED_BY`        | `RoleAssignment`                                 | `0..n`             | `0..n`                  |
| `CiV`            | `HELD_BY`            | `RoFOrg`, `RoFTeam`, or<br>human `RoFTeamMember` | `1`                | `0..n`                  |

Reading example for `RoFOrgRelationship ── SOURCE_ORG ──► RoFOrg`: **Targets per source `1`** means that each organizational relationship has exactly one source organization; **Sources per target `0..n`** means that a `RoFOrg` source can be none, one or more organizational relationships.

| Source               | relationship     | Target           | Targets per source | Sources per destination |
| -------------------- | ---------------- | ---------------- | -----------------: | ----------------------: |
| `RoFOrgRelationship` | `SOURCE_ORG`     | `RoFOrg`         | `1`                | `0..n`                  |
| `RoFOrgRelationship` | `TARGET_ORG`     | `RoFOrg`         | `1`                | `0..n`                  |
| `RoFOrgRelationship` | `REPRESENTED_BY` | `RoleAssignment` | `2..n`             | `0..n`                  |

```text
RoFOrg ── HAS_TEAM ──► RoFTeam ── HAS_MEMBER ──► RoFTeamMember
                                                        ├── HAS_ROLE ──► RoFRole
                                                        └── HAS_ASSIGNMENT ──► RoleAssignment
                                                                                  ├── IN_TEAM ──► RoFTeam
                                                                                  └── ACTIVATES_ROLE ──► RoFRole

RoFOrg ◄── SOURCE_ORG ── RoFOrgRelationship ── TARGET_ORG ──► RoFOrg
                              └── REPRESENTED_BY ──► RoleAssignment
```

### 10.4 Rules and Exceptions

1. Operational work takes place within a `RoFOrg`.
2. Parent companies, subsidiaries and partner companies are each independent `RoFOrg`.
3. A `RoFOrg` reaches members and roles exclusively via `RoFTeam → RoFTeamMember → RoFRole`; Direct relationships from the organization to members or roles are not saved.
4. Each `RoFTeam` belongs to exactly one `RoFOrg` and has at least one member.
5. A `RoFTeamMember` can be a member of multiple teams.
6. A member owns at least one `RoFRole`; The same role is only saved once in a member's role inventory.
7. A `RoleAssignment` belongs to exactly one member, exactly one team and activates exactly one role.
8. A `RoleAssignment` may only activate a role that the associated member has through `HAS_ROLE`.
9. The member of a `RoleAssignment` must belong to the team referenced therein via `HAS_MEMBER`.
10. The same role can be active for a member in multiple teams; Each team uses its own `RoleAssignment`.
11. Each `RoFOrgRelationship` connects exactly two different `RoFOrg` via `SOURCE_ORG` and `TARGET_ORG`.
12. `SUBSIDIARY` is directed from the parent organization to the subsidiary organization. A subsidiary organization may itself be the source of additional `SUBSIDIARY` relationships.
13. Active `SUBSIDIARY` relationships are not allowed to form cycles. In the current model, a `RoFOrg` may have at most one immediate parent organization.
14. `PARTNERSHIP` connects independent organizations on a professional level. The stored source and destination direction does not establish organizational subordination.
15. Each active `RoFOrgRelationship` is represented by at least one valid `RoleAssignment` from each participating organization.
16. A `RoFTeamMember` describes the same human or technical identity even when operating across multiple teams or organizations. The respective contexts arise from separate memberships and `RoleAssignments`, not from duplicating the person.
17. Each `HAS_MEMBER` and `HAS_ROLE` relationship has a validity period. The period of a `RoleAssignment` must be entirely within a concurrent team membership and concurrent role ownership.
18. If `allocation` is set, the value is greater than `0` and at most `1`. The sum of simultaneously valid `allocation` values ​​of a `RoFTeamMember` must not exceed `1`. If the value is missing, capacity for this role activation is not evaluated quantitatively.
19. For an active `PARTNERSHIP`, the technically stored direction is chosen deterministically: The lexicographically smaller organizational UUID is `SOURCE_ORG`. This does not change the professional reciprocity.
20. Two active `RoFOrgRelationship` objects with the same type and the same organization pair cannot have overlapping validity periods.
21. The team of each represented `RoleAssignment` must belong to the represented `RoFOrg`.
22. A participating organization is not additionally duplicated as `ERoFObject`.
23. Each `PiF1o` has exactly one accountable `RoFTeamMember`. Each of its tasks has exactly one responsible `RoFTeam`; only active or completed atomic tasks require at least one executing `RoleAssignment`. The accountable member does not have to execute the Task themselves.
24. A `HELD_BY` relationship to a `RoFTeamMember` is permitted only when `memberType = HUMAN`. Technical members have no personal value construct.
25. The scope of a CiV is determined exclusively by `HELD_BY`. Team membership and organizational affiliation create no additional implicit scopes.
26. An organization-held CiV remains assigned to the `RoFOrg`, even when an executive or other mandated team develops it. The people acting remain traceable through their `RoleAssignments`.

### 10.5 Example

Anna owns the role `Developer` exactly once. She is a member of Team A and Team B. Because she performs the role on both teams, two separate role activations are required:

```text
RoFTeamMember: Anna
  ├── HAS_ROLE ──► RoFRole: Developer
  ├── HAS_ASSIGNMENT ──► RoleAssignment A
  │                          ├── IN_TEAM ──► Team A
  │                          └── ACTIVATES_ROLE ──► Developer
  └── HAS_ASSIGNMENT ──► RoleAssignment B
                             ├── IN_TEAM ──► Team B
                             └── ACTIVATES_ROLE ──► Developer
```

The role `Developer` is not stored twice on the member. Only their team-related activation is modeled separately for each team. This makes it clear which team Anna carries out which tasks in which role.

A group A owns an independent subsidiary B. B in turn owns the independent subsidiary C and maintains a partnership with the independent company D:

```text
RoFOrgRelationship: A zu B
  ├── type = SUBSIDIARY
  ├── SOURCE_ORG ──► RoFOrg A
  ├── TARGET_ORG ──► RoFOrg B
  └── REPRESENTED_BY ──► RoleAssignments from A and B

RoFOrgRelationship: B zu C
  ├── type = SUBSIDIARY
  ├── SOURCE_ORG ──► RoFOrg B
  ├── TARGET_ORG ──► RoFOrg C
  └── REPRESENTED_BY ──► RoleAssignments from B and C

RoFOrgRelationship: B and D
  ├── type = PARTNERSHIP
  ├── SOURCE_ORG ──► RoFOrg B
  ├── TARGET_ORG ──► RoFOrg D
  └── REPRESENTED_BY ──► RoleAssignments from B and D
```

All four companies remain able to operate independently and retain their own teams, members and roles. The organizational relationships do not lead to their other model contexts being automatically merged; the relationship types only describe their position in relation to each other.

---

## 11. Environment of Roles or Functions – ERoF

### 11.1 Meaning

`ERoF` stands for **Environment of Roles or Functions** and describes the technical model space of the relevant environment. It includes the systems, tools, documents, data, infrastructure, standards, rules, organizational relationships and other environmental components with which roles interact in their work.

`ERoF` is one of the ten functional JCI core elements, but is not stored as a separate node. The ERoF model space is derived from concrete `ERoFObjects`, `RoFOrgRelationships` and their use by acting `RoleAssignments`. Another organization remains an independent `RoFOrg`. Its significance as a relevant environment arises from a `RoFOrgRelationship`; the organization is not additionally saved as `ERoFObject`.

Example:

```text
RoleAssignment: Anna as Developer
  ├── USES ──► ERoFObject: Repository
  └── USES ──► ERoFObject: API

Anna's ERoF
= Repository + API
```

The ERoF model space is therefore technically available without an additional `ERoF` node being created.

From the perspective of a parent organization, its subsidiary organization can be recognized as part of the relevant `ERoF` via an active `RoFOrgRelationship` with `type = SUBSIDIARY`. The assignment is derived from the mother as `SOURCE_ORG` and the daughter as `TARGET_ORG`:

```text
ERoF of RoFOrg: parent organization
  └── umfasst ──► RoFOrgRelationship: SUBSIDIARY
                       ├── SOURCE_ORG ──► RoFOrg: Mutter
                       └── TARGET_ORG ──► RoFOrg: Tochter
```

The subsidiary organization remains exclusively an independent `RoFOrg`. It is not additionally saved as `ERoFObject`. Only specific objects of the parent-subsidiary relationship, such as a contract, a shared system or a data room, can be modeled as separate `ERoFObjects`.

### 11.2 Origin

A `ERoFObject` is created when a specific environmental component becomes relevant to the work in the JCI model. The object is described according to its technical type. Whether it is internal or external from an organization's perspective is not stored absolutely on the object, but is derived from ownership and organizational perspective.

Examples of possible types are:

```text
SYSTEM, APPLICATION, DATA, DOCUMENT, TOOL,
FACILITY, CONTRACT, SERVICE, OTHER
```

If an organization owns the object via `OWNED_BY`, it is internal from their perspective. If it is used by roles of this organization without this organization being one of the owners, it is external from their perspective. Shared ownership by multiple organizations is permitted.

An active `ERoFObject` is assigned to at least one `RoleAssignment`. This means that every environmental interaction is associated with a member, a team and a role activated there.

A `RoFOrgRelationship` of type `PARTNERSHIP` belongs to the ERoF perspective of both organizations involved. A `SUBSIDIARY` relationship structurally describes its RoF classification and at the same time the environmental relationship relevant for mother and daughter. In both cases, the specific interaction is tied to `RoleAssignments` of the organizations involved via `REPRESENTED_BY`.

If a `ERoFObject` or its usage changes, `SYNC` checks the affected `RoleAssignments`, tasks, teams, rules and dependents. States that have actually been replaced are recorded as separate `PiH`.

### 11.3 Objects and Relationships

| Concept or graph object | Meaning                                                                      |
| ----------------------- | ---------------------------------------------------------------------------- |
| `ERoF`                  | Technical and derived model space without its own node.                      |
| `ERoFObject`            | Specific saved environmental object.                                         |
| `RoFOrgRelationship`    | Environmental or structural relationship between two distinct organizations. |
| `RoleAssignment`        | Active role of a member in a team.                                           |
| `Task`                  | Activity that can directly use an environmental object.                      |
| `RoFTeamMember`         | Member whose environment can be derived via role activations.                |
| `RoFTeam`               | Team whose environment is derived from its members.                          |
| `RoFOrg`                | Organization whose environment is derived from its teams.                    |

#### Saved Relationships

| Source           | relationship | Target       | Targets per source | Sources per destination |
| ---------------- | ------------ | ------------ | -----------------: | ----------------------: |
| `RoleAssignment` | `USES`       | `ERoFObject` | `0..n`             | `1..n`                  |
| `Task`           | `USES`       | `ERoFObject` | `0..n`             | `0..n`                  |
| `ERoFObject`     | `OWNED_BY`   | `RoFOrg`     | `0..n`             | `0..n`                  |

| Source               | relationship     | Target           | Targets per source | Sources per destination |
| -------------------- | ---------------- | ---------------- | -----------------: | ----------------------: |
| `RoFOrgRelationship` | `SOURCE_ORG`     | `RoFOrg`         | `1`                | `0..n`                  |
| `RoFOrgRelationship` | `TARGET_ORG`     | `RoFOrg`         | `1`                | `0..n`                  |
| `RoFOrgRelationship` | `REPRESENTED_BY` | `RoleAssignment` | `2..n`             | `0..n`                  |

```text
Task ── EXECUTED_BY ──► RoleAssignment ── USES ──► ERoFObject
  └──────────────────────── USES ───────────────────────►
```

#### Inferred environmental attributions - not saved

| Starting point  | Derivation                                       | Target       |
| --------------- | ------------------------------------------------ | ------------ |
| `RoFTeamMember` | about its `RoleAssignments`                      | `ERoFObject` |
| `RoFTeam`       | about members and their `RoleAssignments`        | `ERoFObject` |
| `RoFOrg`        | about teams, members and their `RoleAssignments` | `ERoFObject` |

```text
ERoF(RoFTeamMember)
= all ERoFObjects of its RoleAssignments

ERoF(RoFTeam)
= union of the ERoFObjects of its members in this team

ERoF(RoFOrg)
= union of the ERoFObjects of all members of all teams in the organization
  and its active RoFOrgRelationships
```

### 11.4 Rules and Exceptions

1. `ERoF` is the technical category; concrete environmental objects are saved as `ERoFObject`.
2. Each active `ERoFObject` must be used by at least one `RoleAssignment`.
3. A `RoleAssignment` can use none, one or more `ERoFObjects`.
4. One `ERoFObject` can be shared by multiple `RoleAssignments`.
5. The environment of a member, team or organization is derived from the personal role activations.
6. Direct environmental relationships of `RoFOrg`, `RoFTeam` or `RoFTeamMember` are not stored as a substitute for this derivation.
7. An atomic Task may use a `ERoFObject` directly if at least one `RoleAssignment` executing the Task uses the same environmental object. A composite Task has no direct environmental use.
8. A direct Task relationship specifies the work-related environmental context, but never replaces the assignment to an acting person.
9. An organization-wide relevant environmental object also requires at least one responsible member with a suitable `RoleAssignment`.
10. `RaN` can regulate the use of a `ERoFObject`. If there are rule conflicts, `SYNC` reports the conflict without silently resolving it.
11. A parent, subsidiary or partner organization remains exclusively an independent `RoFOrg` and is not duplicated as `ERoFObject`.
12. An active `RoFOrgRelationship` belongs to the ERoF perspective of both participating organizations and is supported by at least one `RoleAssignment` from each side.
13. Contracts, shared systems, data rooms, guidelines or other items of an organizational relationship can also be modeled as their own `ERoFObjects`.
14. `INTERNAL` and `EXTERNAL` are always derived for a `RoFOrg` under consideration: `INTERNAL` if there is a `OWNED_BY` relationship with this organization, otherwise `EXTERNAL`.
15. A `ERoFObject` may not have an ownership relationship if the owner lies outside the modeled organization graph. It then remains external to using modeled organizations; the external owner can be documented via `externalReference`.
16. `OWNED_BY` does not replace a `USES` relationship. Property alone does not prove actual environmental interaction.

**Quick example:** A shared platform references Organization A and B via `OWNED_BY`. It is internal to both. If a role activation from Organization C uses the same platform, it is external to C, even though only one `ERoFObject` is stored.

### 11.5 Example

Anna works as `Developer` on Team A. Her active role uses a repository and a API. A concrete Task uses the same environmental objects:

```text
RoFTeamMember: Anna
  └── HAS_ASSIGNMENT ──► RoleAssignment: Developer in Team A
                              ├── USES ──► ERoFObject: Repository
                              └── USES ──► ERoFObject: API

Task: Schnittstelle erweitern
  ├── EXECUTED_BY ──► RoleAssignment: Developer in Team A
  ├── USES ─────────► ERoFObject: Repository
  └── USES ─────────► ERoFObject: API
```

Anna's environment contains repository and API. The environment of Team A and the associated `RoFOrg` also contains these objects because they are derivable via Anna's team-related `RoleAssignment`. No additional direct environmental relationships to the team or organization are saved.

If Anna's `RoFOrg` is in a partnership with another `RoFOrg`, the `RoFOrgRelationship` belongs to the relevant environment of both organizations. The partner organization remains a `RoFOrg`. A shared contract, data exchange system or shared platform, on the other hand, is stored as `ERoFObjects` and used via the participating `RoleAssignments`.

---

## 12. Synchronization – SYNC

### 12.1 Meaning

`SYNC` is the stored and historizable definition of the synchronization logic of the JCI model. It determines how a change is recognized, checked for effects along the stored relationships and historicized in the event of an actual change in status.

A `SyncEvent` is clearly separate from this: It documents the unchangeable result of a synchronization attempt that has been completed or aborted in a controlled manner. Via `EXECUTES` it refers to exactly the SYNC definition that was used. During execution, a technical `SyncRun` maintains the variable running state. `SyncRun` is part of the implementation and is not stored as a JCI node.

```text
SYNC      = Welche Synchronisationslogik gilt?
SyncRun   = What happens technically during execution?
SyncEvent = When and with what outcome was the attempt completed?
```

`SYNC` is not a historical condition. If the saved SYNC definition is changed, the synchronization run carried out for it records its previous state as its own `PiH`. However, the mere use of a SYNC definition by a `SyncRun` and its documentation in the `SyncEvent` does not change the definition.

A `SyncDefinition` contains at least:

```text
definitionSchemaVersion
ontologyVersion
graphRulesVersion
syncSpecVersion
supportedEntityTypes[]
supportedRelationshipTypes[]
handlerSetVersion
implementationReference
implementationChecksum
```

The version information determines exactly which ontology, graph rules and SYNC specification are checked against. `implementationReference` means the executable rules package or artifact; `implementationChecksum` is its SHA-256 value. A SYNC definition may only become `ACTIVE` if all concrete entity and relationship types present in the model are supported and the checksum comparison is successful.

**Short example:** `SYNC 1.0` refers to ontology 1.0, graph rules 1.0 and the handler package `jci-sync-1.0` with its checksum. A `SyncEvent` not only records “SYNC 1.0”, but also the exact definition in a comprehensible manner.

### 12.2 Origin

A synchronization attempt originates from an accepted change request:

1. Before execution, the request is recorded as an immutable `ChangeEvent`. This applies to changes of existing entities, `CREATED` and `HISTORICAL_CORRECTION`.
2. The `ChangeEvent` schedules at least one technical `SyncRun`.
3. The `SyncRun` uses exactly one saved SYNC definition.
4. The `SYNC` definition used identifies all directly and indirectly affected elements and relationships.
5. It checks `RaN`, cardinalities and other model conditions.
6. It determines applicable `RaN`, checks their compatibility and applies the expressly saved priority if a contradiction is detected. Ties or non-evaluable semantics produce an open `RaNConflict`.
7. It distinguishes between elements that are merely affected and those that actually need to be changed.
8. For Task changes, it traverses parent, subtask, and dependency relationships, determines affected `PiF1o`, and infers Task status upward from the atomic tasks.
9. When a `Verification` is completed, it determines applicable current Verifications, checks their bound target revisions, and aggregates all `REQUIRED` criteria of the associated `PiF1o`.
10. Immediately before commit, it checks again whether the revisions of `Result` and `SuccessCriterion` bound by a `Verification` are still current.
11. Before every actual change to an existing historizable entity, the previous state is prepared as a separate `PiH`.
12. With `SUCCESS`, the requested domain change, permitted subsequent changes, associated `PiH`, corrections, conflict resolutions and relationships are committed atomically.
13. With `CONFLICT` or `FAILED`, the requested domain change and all uncommitted subsequent changes are rolled back completely. Neither a new revision nor a `PiH` arises from an uncommitted state.
14. Upon completion or controlled abort, exactly one immutable `SyncEvent` with a unique `runId` is created and `TRIGGERS` is added append-only. A newly recognized `RaNConflict` is also retained as final documentation.
15. The `SyncEvent` documents start, end, outcome, SYNC definition used, elements checked, changes actually committed, `PiH` created, corrections, rule conflicts and errors.

Atomicity refers to the requested technical change and its permitted subsequent changes. The final `SyncEvent` and required conflict documents, however, form the permanent documentation of the experiment. With `SUCCESS`, subject changes and closing documentation can be saved in the same transaction. With `CONFLICT` or `FAILED`, the technical transaction is first rolled back and then the final documentation is permanently saved.

```text
Domain transaction
├── SUCCESS  → change, subsequent changes, and associated PiH are committed
├── CONFLICT → domain changes are not committed
└── FAILED   → domain changes are not committed

Completion documentation
└── every completed or controlled-terminated SyncRun
    └── creates exactly one immutable SyncEvent
        └── records a RaNConflict when required
```

With `changeType = CREATED`, there is no source entity for `CHANGED_BY` before successful commit. On `SUCCESS`, the new entity with `revision = 1`, its creation provenance and exactly one `CHANGED_BY` relationship are created together. On `CONFLICT` or `FAILED`, no target node, `CHANGED_BY` or history is created.

When a deviation is detected in a `PiH`, `SYNC` uses the same controlled event frame but does not create a new historical state of that `PiH`. The `ChangeEvent` points via `TARGETS_HISTORY` to exactly this `PiH` and has no `CHANGED_BY` source. After successful validation, the `SyncEvent` creates a `HistoricalCorrection` whose `CORRECTS` points to the same unchanged `PiH`.

```text
JCIEntity ── CHANGED_BY ──► ChangeEvent ── schedules ──► SyncRun (technical)
                                                         │
                                                         └── completion/termination ──► SyncEvent
                                                                                     ├── EXECUTES ──► SYNC
                                                                                     ├── AFFECTS ──► JCIEntity
                                                                                     └── CREATES_HISTORY ──► PiH

ChangeEvent:HISTORICAL_CORRECTION ── TARGETS_HISTORY ──► PiH
              │
              └── completed SyncRun ──► SyncEvent
                                             └── CREATES_CORRECTION ──► HistoricalCorrection
                                                                            └── CORRECTS ─────► same PiH
```

### 12.3 Objects and Relationships

| Object                 | Meaning                                                          |
| ---------------------- | ---------------------------------------------------------------- |
| `SYNC`                 | Saved and historizable definition of the synchronization logic.  |
| `ChangeEvent`          | Documents the reason, type and starting point of a change.       |
| `SyncRun`              | Changeable technical running condition; no `JCIEntity`.          |
| `SyncEvent`            | Unchangeable result of a completed synchronization attempt.      |
| `PiH`                  | Preserves a state superseded by the change.                      |
| `HistoricalCorrection` | Corrects a `PiH` without changing its content.                   |
| `RaN`                  | Provides rules, standards and limits for testing.                |
| `RaNConflict`          | Documents a rule conflict that cannot be resolved automatically. |
| `JCIEntity`            | Can be starting point, affected or changed entity.               |

| Source                   | relationship         | Target                 | Targets per source | Sources per destination |
| ------------------------ | -------------------- | ---------------------- | -----------------: | ----------------------: |
| historizable `JCIEntity` | `CHANGED_BY`         | `ChangeEvent`          | `0..n`             | `0..1`                  |
| `ChangeEvent`            | `TRIGGERS`           | `SyncEvent`            | `0..n`             | `1`                     |
| `ChangeEvent`            | `TARGETS_HISTORY`    | `PiH`                  | `0..1`             | `0..n`                  |
| `SyncEvent`              | `EXECUTES`           | `SYNC`                 | `1`                | `0..n`                  |
| `SyncEvent`              | `AFFECTS`            | `JCIEntity`            | `0..n`             | `0..n`                  |
| `SyncEvent`              | `CREATES_HISTORY`    | `PiH`                  | `0..n`             | `1`                     |
| `SyncEvent`              | `CREATES_CORRECTION` | `HistoricalCorrection` | `0..n`             | `1`                     |
| `HistoricalCorrection`   | `CORRECTS`           | `PiH`                  | `1`                | `0..n`                  |
| `HistoricalCorrection`   | `CAUSED_BY`          | `ChangeEvent`          | `1`                | `0..n`                  |
| `HistoricalCorrection`   | `SUPERSEDES`         | `HistoricalCorrection` | `0..1`             | `0..1`                  |
| `RaNConflict`            | `DETECTED_BY`        | `SyncEvent`            | `1`                | `0..n`                  |
| `RaNConflict`            | `RESOLVED_THROUGH`   | `ChangeEvent`          | `0..1`             | `0..n`                  |

```text
Depending on the changed element, the executed SYNC definition checks in particular:

CiV and PiF2 through PiF1o
RaN and governed targets
RoFOrg, RoFTeam, RoFTeamMember, RoFRole, and RoleAssignment
RoFOrgRelationship with both participating RoFOrg and their representing RoleAssignments
Task, SuccessCriterion, Result, Verification, and Evidence
ERoFObject and its person-bound uses
PiH and associated HistoricalCorrections for historical discrepancies
```

### 12.4 Rules and Exceptions

1. Every accepted `ChangeEvent` schedules at least one technical `SyncRun`.
2. While no attempt has ended, the `ChangeEvent` has no `SyncEvent`; `TRIGGERS = 0` is the correct intermediate state.
3. Every completed or controlled-aborted `SyncRun` creates exactly one immutable `SyncEvent` and adds exactly one `TRIGGERS` relationship append-only.
4. Every `SyncEvent` belongs to exactly one triggering `ChangeEvent`, has a unique `runId`, and points via `EXECUTES` to exactly the SYNC definition used.
5. A SYNC definition may be documented as used by zero, one or more `SyncEvents`.
6. A `SyncEvent` with `SUCCESS` or `CONFLICT` names at least one affected `JCIEntity`. Only a `FAILED` attempt ending before successful target resolution may have no `AFFECTS` target.
7. Being affected alone creates no `PiH`. Only a state actually superseded is historized.
8. A `SyncEvent` may create zero, one or more `PiH`. Every created `PiH` remains connected to exactly this `SyncEvent` via `CREATES_HISTORY` and to its original `JCIEntity` via `HAS_HISTORICAL_STATE`.
9. For `changeType = CREATED`, the target ID must be unused and `requestedRevision = null`. Only `SUCCESS` creates the new entity with `revision = 1`, `CREATED_BY` and exactly one `CHANGED_BY`; no `PiH` is created. `CONFLICT` or `FAILED` creates no target node, `CHANGED_BY` or history.
10. The executed SYNC definition checks all `RaN` and model conditions relevant to the change.
11. Clearly derivable and permissible adjustments may be processed. When applicable `RaN` conflict, the higher `priority` decides only that concrete contradiction. A tie or unevaluable semantics creates an open `RaNConflict` and is not resolved silently.
12. `SYNC` is the stored process definition; `SyncRun` is mutable technical runtime state; `SyncEvent` is immutable completion documentation. If the SYNC definition itself changes, its previous state is recorded as `PiH` like any other historizable `JCIEntity`.
13. When a `RoFOrgRelationship` changes, the executed SYNC definition checks both involved `RoFOrg`, the validity of their representing `RoleAssignments`, relevant `RaN`, connected `ERoFObjects`, and for `SUBSIDIARY` the absence of organizational cycles.
14. A `ChangeEvent` for `HISTORICAL_CORRECTION` has exactly one `TARGETS_HISTORY`, no `CHANGED_BY` source, and `requestedRevision = 1`. The `PiH` later connected through `CORRECTS` must be the same target.
15. A confirmed historical discrepancy creates a `HistoricalCorrection` after successful validation and never a new `PiH` of the existing `PiH`.
16. Every `HistoricalCorrection` created by a run remains connected to exactly one `SyncEvent` via `CREATES_CORRECTION`, to that event's triggering `ChangeEvent` via `CAUSED_BY`, and to exactly one unchanged `PiH` via `CORRECTS`.
17. Before a historical correction, `SYNC` computes the effective `HistoryView`, compares its hash with `expectedHistoryViewHash`, and serializes commits per `PiH`. A stale hash produces `CONFLICT` and no correction.
18. Multiple active corrections of one `PiH` may only have disjoint `correctedFields`. An overlapping correction must fully supersede exactly one active predecessor via `SUPERSEDES`; ambiguous or multiple overlaps produce `CONFLICT`.
19. A correction to the current model is processed separately from the historical correction and has its own change process.
20. A `SyncEvent` is created only after the technical attempt has completed or been stopped in a controlled manner and all required facts are known.
21. If final `SyncEvent` storage is temporarily impossible, it is retried with the same `runId`, the same `ChangeEvent` and the same idempotency key.
22. A failed attempt creates a `SyncEvent` with `outcome = FAILED`; incomplete domain changes must not remain as current model state. Retrying event storage must not re-execute the failed domain change.
23. Repeated submission of the same change request must be detected through immutable `idempotencyKey`. Every actual attempt receives a unique `runId` and its own `SyncEvent`, but must not apply the same domain change more than once.
24. A new `Verification` binds the tested revisions through `evaluatedResultRevision` and `checkedCriterionRevision`. `SYNC` validates them in a consistent view and again immediately before commit.
25. A `Verification` is applicable only if it has not been superseded and the current revisions of its `Result` and `SuccessCriterion` still equal the bound revisions. A later target change makes the prior Verification revision-stale.
26. For a new `Verification`, `SYNC` checks the `SUPERSEDES` chain, determines all applicable current Verifications of the criterion, and evaluates its `evaluationMode`.
27. `SYNC` sets a `PiF1o` to `ACHIEVED` only if at least one mandatory criterion exists, every `REQUIRED` criterion is satisfied, all assigned Tasks are `COMPLETED`, all Task dependencies are satisfied, and no model or `RaN` violation exists. Optional criteria do not block the transition.
28. Missing, revision-stale or inapplicable Verifications, `INVALID`, `INCONCLUSIVE` or a rule conflict prevent automatic achievement. `SYNC` reports the reason and does not change the status.
29. For Task changes, `SYNC` checks Task kind, hierarchy, parent, subtasks, prerequisites, dependent Tasks and all affected `PiF1o`. Derived Task statuses are determined bottom-up and historized like any domain change.
30. An open `RaNConflict` blocks every automatic change whose permissibility depends on its resolution. A resolved conflict remains traceable to the detecting `SyncEvent`, resolving `ChangeEvent` and responsible `RoleAssignment`.
31. When CiV, `HELD_BY`, or `INFORMED_BY` changes, `SYNC` validates the three required dimensions, the permitted value holder, human decision provenance, and the shared scope of every `PiF2` grounded by it. It neither creates nor adopts a value decision automatically.

### 12.5 Example

An operational future state is changed from 48 to 24 hour response time:

```text
PiF1o: Response within 48 hours
                  │
                  └── CHANGED_BY ──► ChangeEvent
                                          │
                                          └── schedules ──► SyncRun (technical)
                                                               │
                                                               └── completion ──► SyncEvent
                                                                                     ├── EXECUTES ──► SYNC: JCI-Standardprozess 1.0
                                                                                     ├── AFFECTS ──► PiF1o
                                                                                     ├── AFFECTS ──► SuccessCriterion
                                                                                     ├── AFFECTS ──► Task
                                                                                     └── CREATES_HISTORY ──► PiH
```

The technical `SyncRun` uses the SYNC definition `JCI-Standardprozess 1.0`. This checks the `PiF1o`, its success criteria, tasks, responsibilities, role activations and used `ERoFObjects`. The previous PiF1o state is recorded as `PiH`. Dependent elements only get their own `PiH` when their state is actually changed. Only after atomic completion is the immutable `SyncEvent` created; it documents the definition used as well as all checks, changes and conflicts.

---

### 12.6 Technology-independent exchange format

JCI uses UTF-8 encoded JSON documents for change requests and SYNC results. The form described here is incompatibly refined from version 1.0 and uses `schemaVersion = "1.1"`. UUIDs are transmitted as strings, timestamps follow ISO 8601 with a time zone, and domain values use `TypedValue`.

A `JCIChangeRequest` contains at least:

```text
schemaVersion
requestId
idempotencyKey
requestedAt
requestedRevision = null for CREATED | Integer >= 1 for all other types
changeType
target = {id, entityType}
requestedByRoleAssignmentId
reason
```

For all change types except `HISTORICAL_CORRECTION`, `operations[]` with at least one operation is additionally required. An operation uses `op = ADD | REPLACE | REMOVE | CONNECT | DISCONNECT`. Property operations have a unique `path` and, where required, `value: TypedValue`. Relationship operations have `relationshipType`, `direction`, `otherEntityId` and optionally a typed property map. `CONNECT` and `DISCONNECT` may use only relationships from the canonical catalog.

For `changeType = HISTORICAL_CORRECTION`, `target` denotes exactly the immutable `PiH`, `requestedRevision` is `1`, and exactly one structured `historicalCorrection` object replaces `operations[]`:

```text
historicalCorrection = {
  correctionType = ADDITION | CORRECTION | CLARIFICATION,
  reason,
  valueSchemaVersion,
  expectedHistoryViewHash,
  correctedFields[],
  previousValue,
  correctedValue
}
```

`correctedFields` contains unique, lexicographically sorted canonical JSON Pointers. `previousValue` and `correctedValue` are `TypedValueMaps` with exactly the same key set. `expectedHistoryViewHash` binds the request to the effective historical view, which is checked again before commit. A historical correction must not contain generic operations because the addressed `PiH` itself is never modified.

When stored, `requestId` becomes `ChangeEvent.id`, while `idempotencyKey`, target ID, target type and `requestedRevision` are copied unchanged to the `ChangeEvent`. This keeps even a failed or not-yet-completed request uniquely addressable.

A `JCISyncResult` contains at least:

```text
schemaVersion
requestId
runId
syncEventId
outcome = SUCCESS | CONFLICT | FAILED
completedAt
affectedCount
changedCount
historyCount
correctionCount
conflictCount
affectedEntityIds[]
conflictIds[]
errors[]
```

Transport references such as `requestedByRoleAssignmentId` are converted to the canonical `REQUESTED_BY` relationship when stored and are not retained as an additional domain field on the node. The JSON document remains referenceable as input evidence through an `Evidence` node.

For `JCISyncResult`, `affectedCount >= 1` applies to `SUCCESS` and `CONFLICT`. Only a `FAILED` result whose run ends before successful target resolution may have `affectedCount = 0` and an empty `affectedEntityIds` list. Every count must exactly match the corresponding list length or number of relationships and objects created in the graph.

Full graph or ontology exports use JSON-LD 1.1. Each entity has `@id = "urn:jci:<UUID>"` and its concrete type in `@type`. Relationships use only the canonical relationship names; Relationship properties are transferred as standalone JSON-LD relationship objects. The export contains the used versions of context, ontology and graph rules.

The mandatory machine-readable schemas are under `docs/schemas/`.

**Short example:** A change to the Task label is transmitted as `REPLACE` on the path `/name`. The role ID in the transport becomes `REQUESTED_BY`; after successful processing, the result names the generated `SyncEvent` and the historical state of the previous Task name.

### 12.7 Initial Bootstrap

The initial bootstrap solves only the trust-root problem of a completely empty graph. It is not a normal change request and may run exactly once in one atomic transaction.

The bootstrap creates at least:

```text
RoFOrg
└── RoFTeam
    └── technical RoFTeamMember
        ├── RoFRole
        └── RoleAssignment with bootstrapKey = "ROOT"

active SYNC definition
```

All required RoF relationships are created in the same transaction. The six bootstrap entities `RoFOrg`, `RoFTeam`, technical `RoFTeamMember`, `RoFRole`, root `RoleAssignment`, and `SYNC` are created directly with `status = ACTIVE`, `revision = 1`, and the same value for `createdAt` and `updatedAt`. Wherever the concrete type or a bootstrap relationship has `validFrom`, that value also equals the same bootstrap timestamp. This is the only exception to the rule that mutable domain entities are initially created as `DRAFT`: without an active organization, role, role assignment, and SYNC definition, the trust root could not execute the first regular request.

Only this one root `RoleAssignment` may permanently lack `CREATED_BY`, because no acting role exists before it. All other bootstrap entities point to the root `RoleAssignment` through `CREATED_BY`. The bootstrap creates no `ChangeEvent`, technical `SyncRun`, `SyncEvent`, or `PiH`.

Bootstrap is permitted only while no `JCIEntity` exists. Uniqueness of `bootstrapKey = "ROOT"`, completeness of the minimal graph and activatability of the SYNC definition are checked before commit. Any error rolls back the whole transaction; an incomplete bootstrap must never become visible. After successful commit, a repetition or second root `RoleAssignment` is forbidden and every later change uses the normal SYNC process exclusively.

A data import is not a bootstrap. Imported entities without provable creation provenance remain `DRAFT` until a regular synchronization run requested by a `RoleAssignment` confirms their provenance and model validity.

**Short example:** In an empty database, deployment atomically creates the organization “Junaco”, a technical administration team, a technical member, its administration role, the root `RoleAssignment` and the active SYNC definition. Only after that may this root `RoleAssignment` submit a normal `CREATED` request for the first domain entity.

## 13. Conclusion

The JUNACO Continuous Integration Loop connects purpose, future, responsibility, work, environment, rules, testing and historical development in a common technical graph.

`JCIEntity` is the abstract superclass of all stored instances. Eight of the ten core elements have their own stored `JCIElementInstances`. `RoF` and `ERoF` remain domain model spaces without their own nodes and become visible through concrete graph objects and relationships. `PiH`, `ChangeEvent`, `SyncEvent` and `HistoricalCorrection` remain content-immutable and are not historized again. Only explicitly defined provenance relationships are added append-only during successful creation or completion of a technical run.

Each `CiV` describes one value through NOT, SELF, and TO SERVE dimensions and exactly one value holder. Explicitly selected CiV ground why a future is wanted. `PiF2` to `PiF1o` describe this future at a long-term, strategic, tactical and operational level. The stored `CONTRIBUTES_TO` relationships lead from the more concrete to the higher-level future state and allow a directed `n:m` graph.

A `PiF1o` describes an achievable operational state. It has at least one mandatory success criterion and exactly one accountable `RoFTeamMember`. Composite Tasks structure the work; atomic Tasks are executed through team-bound `RoleAssignments`, use concrete `ERoFObjects` and may produce `Results`. Task dependencies determine the permitted execution order. Applicable current `Verifications` evaluate explicitly bound revisions of Results and SuccessCriteria. Only when all `REQUIRED` criteria, all Tasks and all dependencies are satisfied may `SYNC` set the terminal status `ACHIEVED`.

The RoF model space provides organizational, team, member, and role context. Parent, subsidiary and partner companies each remain independent `RoFOrg`; their relationship to each other is described by a personal `RoFOrgRelationship`. `SUBSIDIARY` can form recursive but cycle-free parent-child structures. `PARTNERSHIP` connects independent organizations and belongs to the ERoF perspective of both sides. The ERoF model space also describes the relevant environment, whereby concrete environmental interactions always remain traceable via active role activations. `RaN` acts as a regulating cross-section on the respective regulated future, work, organizational, role and environmental areas. In the event of an actual rule contradiction, the higher explicitly stored priority takes precedence; Ties and non-evaluable semantics remain traceable as `RaNConflict` until a resolution is humanly initiated and confirmed by `SYNC`.

`SYNC` is the stored definition of synchronization logic. An accepted `ChangeEvent` schedules at least one technical `SyncRun`; until the first attempt ends, it may have no `SyncEvent`. Only completion or controlled abort creates an immutable `SyncEvent` with its own `runId`, pointing through `EXECUTES` to the SYNC definition used. Only when an existing state is actually superseded does the run record that previous state as its own `PiH`. Being affected alone creates no historical state; conflicts are reported rather than silently resolved. A later discrepancy in a `PiH` is addressed through `TARGETS_HISTORY` and recorded as an immutable `HistoricalCorrection`. The original `PiH` remains unchanged, and any resulting change to the current model is processed separately. The one-time atomic bootstrap creates only the trust root in an empty graph; afterwards, the normal SYNC process applies without exception.

```text
PiH ── PROVIDES_CONTEXT_TO ──► CiV ── HELD_BY ──► RoFOrg | RoFTeam | human RoFTeamMember
                                      ├── INFORMED_BY ──► CiV
                                      └── INSCRIBES_PURPOSE_IN ──► PiF2
                                                                     ▲
PiF1o ── CONTRIBUTES_TO ──► PiF1t ── CONTRIBUTES_TO ──► PiF1s ─────┘
  │
  ├── HAS_SUCCESS_CRITERIA ──► SuccessCriterion
  ├── ACCOUNTABLE_MEMBER ────► RoFTeamMember
  └── DECOMPOSES_INTO ───────► COMPOSITE Task
                                   └── DECOMPOSES_INTO ──► ATOMIC Task
                                                                  ├── DEPENDS_ON ──► Task
                                                                  ├── EXECUTED_BY ──► RoleAssignment
                                                                  ├── USES ──► ERoFObject
                                                                  └── PRODUCES ──► Result ◄── EVALUATES ── Verification
                                                                                                             └── CHECKS ──► SuccessCriterion

RaN ── PROTECTS ──► CiV | PiF2
    └── GOVERNS ──► relevant implementation elements
RaNConflict ── CONFLICTING_RULE ──► RaN
      ├── DETECTED_BY ──► SyncEvent
      └── RESOLVED_BY ──► RoleAssignment
RoFOrg ◄── SOURCE_ORG ── RoFOrgRelationship ── TARGET_ORG ──► RoFOrg
                              └── REPRESENTED_BY ──► RoleAssignment
ChangeEvent ── TRIGGERS ──► SyncEvent ── AFFECTS ──► JCIEntity
                                      ├── EXECUTES ──► SYNC
                                      └── CREATES_HISTORY ──► PiH

ChangeEvent:HISTORICAL_CORRECTION ── TARGETS_HISTORY ──► PiH
SyncEvent ── CREATES_CORRECTION ──► HistoricalCorrection ── CORRECTS ──► same PiH
                                                └── SUPERSEDES ──► earlier HistoricalCorrection
```

This means that it is possible to trace backwards from a specific Task which operational status, which future context and which value-related purpose it serves. At the same time, responsibility, environmental reference, rules, test results and replaced states remain clearly assigned. This consistent traceability forms the core of the JCI loop.
