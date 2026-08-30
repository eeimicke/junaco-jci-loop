# Complete JCI Example

[Documentation overview](../README.md) · [Deutsch](../../guides/JCI_EXAMPLE.md)

This example uses one scenario to cover all 24 concrete JCI entity types. It explains stored relationships, forward and backward navigation, and the `SUCCESS`, `CONFLICT`, and `FAILED` outcomes of a synchronisation attempt.

## 1. Reading relationships

A stored relationship is read from source to target:

```text
Source ── RELATIONSHIP ──► Target
```

`Task ── PRODUCES ──► Result` asks forward: “Which Result does this Task produce?” Backward navigation asks: “Which Task produced this Result?” The backward question does not create another stored edge.

| Stored direction | Forward question | Backward question |
| --- | --- | --- |
| `PiF1o ── DECOMPOSES_INTO ──► Task` | Which Tasks realise the target? | To which operational target does the Task belong? |
| `Task ── EXECUTED_BY ──► RoleAssignment` | Which active role executes the Task? | Which Tasks does this role assignment execute? |
| `Verification ── CHECKS ──► SuccessCriterion` | Which criterion is checked? | Which Verifications evaluate this criterion? |
| `SyncEvent ── CREATES_HISTORY ──► PiH` | Which history did the run create? | Which run created this `PiH`? |

## 2. Initial situation and purpose

Example GmbH wants to answer customer enquiries reliably. Earlier complaints about late responses provide historical context:

```mermaid
flowchart LR
    History[PiH: earlier customer complaints] -->|PROVIDES_CONTEXT_TO| Values[CiV: customer-focused and reliable]
    Values -->|INSCRIBES_PURPOSE_IN| LongTerm[PiF2: reliable partner]
    Strategic[PiF1s: digital learning service] -->|CONTRIBUTES_TO| LongTerm
    Tactical[PiF1t: shared service process] -->|CONTRIBUTES_TO| Strategic
    Operational[PiF1o: response within 24 hours] -->|CONTRIBUTES_TO| Tactical
```

| Entity | Example content |
| --- | --- |
| `PiH` | Earlier complaints caused by late responses |
| `CiV` | We act with customer focus, transparency, and reliability. |
| `PiF2` | Customers experience the organisation as a reliable long-term partner. |
| `PiF1s` | Customer service operates digitally and learns continuously. |
| `PiF1t` | All enquiry channels share one service process. |
| `PiF1o` | Every enquiry receives a qualified response within 24 hours. |

Backward navigation from `PiF1o` reaches `CiV` and its historical context, explaining why the operational target exists.

## 3. Organisation, partnership, and roles

Example GmbH uses a platform operated by Service Cloud AG. Both remain independent organisations:

```mermaid
flowchart LR
    Relation[RoFOrgRelationship: service partnership]
    Relation -->|SOURCE_ORG| Customer[RoFOrg: Example GmbH]
    Relation -->|TARGET_ORG| Partner[RoFOrg: Service Cloud AG]
    Customer -->|HAS_TEAM| Team[RoFTeam: Customer Service]
    Team -->|HAS_MEMBER| Anna[RoFTeamMember: Anna]
    Anna -->|HAS_ROLE| Role[RoFRole: Service Agent]
    Anna -->|HAS_ASSIGNMENT| Assignment[RoleAssignment: Anna in Customer Service]
    Assignment -->|IN_TEAM| Team
    Assignment -->|ACTIVATES_ROLE| Role
    Relation -->|REPRESENTED_BY| Assignment
    Relation -->|REPRESENTED_BY| PartnerAssignment[RoleAssignment: partner representative]
```

A second RoleAssignment from Service Cloud AG represents the partner side. `RoFOrgRelationship` connects organisations without merging their teams or roles.

Accountability, responsibility, and execution remain separate:

```text
PiF1o ── ACCOUNTABLE_MEMBER ──► RoFTeamMember: Anna
Task   ── RESPONSIBLE_TEAM ───► RoFTeam: Customer Service
Task   ── EXECUTED_BY ────────► RoleAssignment: Anna as Service Agent
```

## 4. Task hierarchy and work

The `PiF1o` is structured through one composite Task. Every Task belongs directly to this `PiF1o`; Task-to-Task relationships additionally form the hierarchy.

```mermaid
flowchart TD
    Goal[PiF1o] -->|DECOMPOSES_INTO| Parent[COMPOSITE: Handle customer enquiry]
    Goal -->|DECOMPOSES_INTO| Analyse[ATOMIC: Analyse enquiry]
    Goal -->|DECOMPOSES_INTO| Draft[ATOMIC: Draft response]
    Goal -->|DECOMPOSES_INTO| Send[ATOMIC: Send response]
    Parent -->|DECOMPOSES_INTO| Analyse
    Parent -->|DECOMPOSES_INTO| Draft
    Parent -->|DECOMPOSES_INTO| Send
    Draft -->|DEPENDS_ON| Analyse
    Send -->|DEPENDS_ON| Draft
```

Only atomic Tasks carry `EXECUTED_BY`, `USES`, and `PRODUCES`. Composite status is derived from direct subtasks.

## 5. Environment

Anna and the Task use internal and external environmental objects:

```mermaid
flowchart LR
    Task[Task: Analyse enquiry] -->|EXECUTED_BY| Assignment[RoleAssignment: Anna]
    Task -->|USES| Ticket[ERoFObject: Ticket system]
    Assignment -->|USES| Ticket
    Ticket -->|OWNED_BY| Internal[RoFOrg: Example GmbH]
    Task -->|USES| API[ERoFObject: Service API]
    Assignment -->|USES| API
    API -->|OWNED_BY| External[RoFOrg: Service Cloud AG]
```

The ticket system is internal relative to Example GmbH. The service API is external because the partner owns it. `OWNED_BY` determines this perspective; only `USES` proves actual interaction.

## 6. Success, Result, and Verification

The operational state has a required numeric criterion:

```text
SuccessCriterion
├── measurementType = NUMERIC
├── operator = LESS_OR_EQUAL
├── targetValue = 24
├── unit = hours
└── requirementLevel = REQUIRED
```

```mermaid
flowchart LR
    Goal[PiF1o] -->|HAS_SUCCESS_CRITERIA| Criterion[SuccessCriterion: at most 24 hours]
    Task[Task: Send response] -->|PRODUCES| Result[Result: response after 18 hours]
    Verification -->|EVALUATES| Result
    Verification -->|USES_EVIDENCE| Evidence[Evidence: ticket timestamp]
    Verification -->|CHECKS| Criterion
```

Because 18 is less than or equal to 24, the complete `Verification` is recorded with the domain result `VALID`. A later check can point to the former `Verification` through `SUPERSEDES`.

## 7. RaN types and structure

`RaN` is an entity type. `RULE`, `NORM`, `POLICY`, `CONSTRAINT`, and `LAW` are values of its `ruleType` property, not additional nodes.

| `ruleType` | Example |
| --- | --- |
| `RULE` | Every enquiry requires a category. |
| `NORM` | Responses use the approved template. |
| `POLICY` | Only authorised roles may use customer data. |
| `CONSTRAINT` | Responses must be sent within 24 hours. |
| `LAW` | Personal data must be processed lawfully. |

Every `RaN` also carries `effect = REQUIRE | PROHIBIT | PERMIT`, `scopeType = GLOBAL | ORGANIZATION | TEAM | ENTITY`, `decisionKey`, `governedTypes`, `priority`, and a normalised `condition` with `combiner = ALL | ANY`.

```mermaid
flowchart LR
    RaN --> Type{ruleType}
    Type --> Rule[RULE]
    Type --> Norm[NORM]
    Type --> Policy[POLICY]
    Type --> Constraint[CONSTRAINT]
    Type --> Law[LAW]
    RaN --> Effect{effect}
    Effect --> Require[REQUIRE]
    Effect --> Prohibit[PROHIBIT]
    Effect --> Permit[PERMIT]
    RaN --> Scope{scopeType}
    Scope --> Global[GLOBAL]
    Scope --> Organization[ORGANIZATION]
    Scope --> Team[TEAM]
    Scope --> Entity[ENTITY]
```

The arrows in this type diagram illustrate properties and are not stored JCI relationships.

```mermaid
flowchart LR
    Rule[RaN: access to customer data]
    Rule -->|GOVERNS| Task[Task: Analyse enquiry]
    Rule -->|GOVERNS| Object[ERoFObject: Ticket system]
    Rule -->|APPLIES_IN| Team[RoFTeam: Customer Service]
```

Condition clauses exclusively use `EXISTS`, `NOT_EXISTS`, `EQUALS`, `NOT_EQUALS`, `LESS_THAN`, `LESS_OR_EQUAL`, `GREATER_THAN`, `GREATER_OR_EQUAL`, `IN`, `NOT_IN`, `CONTAINS`, or `MATCHES`.

| `effect` | Condition true | Condition false |
| --- | --- | --- |
| `REQUIRE` | `ALLOW` | `DENY` |
| `PROHIBIT` | `DENY` | `NO_DECISION` |
| `PERMIT` | `ALLOW` | `NO_DECISION` |

One `DENY` blocks the decision but is not yet a `RaNConflict`.

## 8. RaNConflict and resolution

Two rules govern the same deletion decision:

- `RaN A`: Delete customer data after 30 days.
- `RaN B`: Retain complaint data for at least 90 days.

If both apply at the same highest priority, they create a `PRIORITY_TIE`:

```mermaid
flowchart LR
    Conflict[RaNConflict: PRIORITY_TIE]
    Conflict -->|CONFLICTING_RULE| RuleA[RaN A: delete after 30 days]
    Conflict -->|CONFLICTING_RULE| RuleB[RaN B: retain for 90 days]
    Conflict -->|AFFECTS| Object[ERoFObject: Ticket system]
    Conflict -->|DETECTED_BY| Event[SyncEvent]
    Conflict -->|USES_EVIDENCE| Evidence
```

`UNEVALUABLE` is the second conflict type and may involve only one rule that cannot be evaluated unambiguously. `PRIORITY_TIE` requires at least two `CONFLICTING_RULE` edges. Only an explicit domain change followed by a successful run may move the conflict from `OPEN` to `RESOLVED`; its former open state becomes a `PiH`.

The subsequently resolved state additionally carries:

```mermaid
flowchart LR
    Resolved[RaNConflict: RESOLVED] -->|RESOLVED_BY| Assignment[RoleAssignment]
    Resolved -->|RESOLVED_THROUGH| ChangeEvent
```

## 9. Change and SYNC

The response target is later tightened from 24 to 12 hours. Anna requests the change:

```text
PiF1o      ── CHANGED_BY ───► ChangeEvent
ChangeEvent ── REQUESTED_BY ──► RoleAssignment: Anna
```

`SYNC` is the stored and historisable process definition. `SyncRun` is mutable technical runtime state and not a graph node. `SyncEvent` is stored immutably only after completion or controlled termination.

```mermaid
flowchart TD
    Entity[JCIEntity: requested change] -->|CHANGED_BY| ChangeEvent
    ChangeEvent -. starts technically .-> Run[SyncRun]
    Run -. uses .-> Definition[SYNC]
    Run -. validates model, revisions, and RaN .-> Decision{outcome}
    Decision --> Success[SUCCESS]
    Decision --> Conflict[CONFLICT]
    Decision --> Failed[FAILED]
    Success --> Apply[commit atomically]
    Conflict --> Rollback[roll back completely]
    Failed --> Rollback
    Apply --> Event[SyncEvent]
    Rollback --> Event
    ChangeEvent -->|TRIGGERS| Event
    Event -->|EXECUTES| Definition
```

Dashed arrows are technical process steps, not stored relationships.

## 10. The three SYNC outcomes

| Outcome | Domain change | Revision and `PiH` | Completion documentation |
| --- | --- | --- | --- |
| `SUCCESS` | commit completely and atomically | for every existing entity that actually changes | always one `SyncEvent` |
| `CONFLICT` | roll back completely | none for rejected states | `SyncEvent`, optionally `RaNConflict` |
| `FAILED` | roll back completely | none for rejected states | `SyncEvent` immediately or after technical recovery |

The completed event records the definition used and affected entities:

```text
ChangeEvent ── TRIGGERS ──► SyncEvent
SyncEvent ── EXECUTES ─────► SYNC
SyncEvent ── AFFECTS ──────► JCIEntity
```

On `SUCCESS`, only states that were actually superseded are historised:

```text
PiF1o    ── HAS_HISTORICAL_STATE ──► PiH: PiF1o revision 3
SyncEvent ── CREATES_HISTORY ───────► PiH: PiF1o revision 3
```

If the `SuccessCriterion` also changes, it receives its own `PiH`. A Task that was only evaluated but remained unchanged receives no history.

## 11. HistoricalCorrection

An error in an existing `PiH` is never corrected by overwriting it:

```mermaid
flowchart LR
    Correction[HistoricalCorrection]
    Correction -->|CORRECTS| History[PiH]
    Correction -->|CAUSED_BY| ChangeEvent
    Correction -->|CORRECTED_BY| Assignment[RoleAssignment]
    Correction -->|USES_EVIDENCE| Evidence
    SyncEvent -->|CREATES_CORRECTION| Correction
```

A later correction may point to the former `HistoricalCorrection` through `SUPERSEDES`. Both remain immutable.

## 12. Complete traceability

| Perspective | Path or question |
| --- | --- |
| **WHY** | From `Task` through `PiF1o`, `PiF1t`, `PiF1s`, and `PiF2` to `CiV`: Why does the work exist? |
| **WHO** | From `Task` through `RoleAssignment`, `RoFTeamMember`, `RoFRole`, `RoFTeam`, and `RoFOrg`: Who acts in which context? |
| **WHERE** | From `Task` and `RoleAssignment` through `USES` to `ERoFObject` and its `OWNED_BY`: Which environment is used? |
| **UNDER WHICH RULES** | Backward from a target to `RaN` nodes connected through `GOVERNS`: Which rules apply? |
| **WITH WHAT RESULT** | From `Task` to `Result`, `Verification`, `SuccessCriterion`, and `Evidence`: What was produced and how was it checked? |
| **WITH WHAT HISTORY** | From `JCIEntity` and `SyncEvent` to `PiH` and `HistoricalCorrection`: Which former states and corrections exist? |

## 13. Coverage of all concrete entities

The complete map shows every concrete entity type at least once. Detailed rules and cardinalities remain documented in the smaller diagrams above and in the canonical specification.

```mermaid
flowchart LR
    PiH -->|PROVIDES_CONTEXT_TO| CiV
    CiV -->|INSCRIBES_PURPOSE_IN| PiF2
    PiF1s -->|CONTRIBUTES_TO| PiF2
    PiF1t -->|CONTRIBUTES_TO| PiF1s
    PiF1o -->|CONTRIBUTES_TO| PiF1t
    PiF1o -->|HAS_SUCCESS_CRITERIA| SuccessCriterion
    PiF1o -->|ACCOUNTABLE_MEMBER| RoFTeamMember
    PiF1o -->|DECOMPOSES_INTO| Task
    RoFOrg -->|HAS_TEAM| RoFTeam
    RoFTeam -->|HAS_MEMBER| RoFTeamMember
    RoFTeamMember -->|HAS_ROLE| RoFRole
    RoFTeamMember -->|HAS_ASSIGNMENT| RoleAssignment
    RoleAssignment -->|IN_TEAM| RoFTeam
    RoleAssignment -->|ACTIVATES_ROLE| RoFRole
    RoFOrgRelationship -->|SOURCE_ORG| RoFOrg
    RoFOrgRelationship -->|TARGET_ORG| PartnerOrg[RoFOrg Partner]
    RoFOrgRelationship -->|REPRESENTED_BY| RoleAssignment
    Task -->|RESPONSIBLE_TEAM| RoFTeam
    Task -->|EXECUTED_BY| RoleAssignment
    Task -->|USES| ERoFObject
    RoleAssignment -->|USES| ERoFObject
    ERoFObject -->|OWNED_BY| RoFOrg
    Task -->|PRODUCES| Result
    Verification -->|EVALUATES| Result
    Verification -->|CHECKS| SuccessCriterion
    Verification -->|USES_EVIDENCE| Evidence
    RaN -->|GOVERNS| Task
    RaNConflict -->|CONFLICTING_RULE| RaN
    RaNConflict -->|DETECTED_BY| SyncEvent
    Task -->|CHANGED_BY| ChangeEvent
    ChangeEvent -->|TRIGGERS| SyncEvent
    SyncEvent -->|EXECUTES| SYNC
    SyncEvent -->|CREATES_HISTORY| PiH
    SyncEvent -->|CREATES_CORRECTION| HistoricalCorrection
    HistoricalCorrection -->|CORRECTS| PiH
```

| Area | Entities |
| --- | --- |
| Core-element instances | `PiH`, `CiV`, `RaN`, `SYNC`, `PiF2`, `PiF1s`, `PiF1t`, `PiF1o` |
| Organisation | `RoFOrg`, `RoFOrgRelationship`, `RoFTeam`, `RoFTeamMember`, `RoFRole`, `RoleAssignment` |
| Work and verification | `Task`, `SuccessCriterion`, `Result`, `Verification`, `Evidence`, `ERoFObject` |
| Change | `ChangeEvent`, `SyncEvent`, `RaNConflict`, `HistoricalCorrection` |

`JCIEntity`, `JCIElementInstance`, and `GraphObject` are abstract types. `RoF` and `ERoF` are model spaces. `SyncRun` is technical runtime state. They are not counted as additional domain nodes.
