# JCI ontology

[Documentation overview](README.md) · [Deutsche Fassung](../JCI_ONTOLOGY.md)

> Controlled English translation. `docs/JCI_CONTEXT.md` remains the canonical specification.

## 1. Type system

`JCIEntity` is the abstract supertype of all stored nodes. `JCIElementInstance` and `GraphObject` are abstract classifications, not additional nodes or core elements. `RoF` and `ERoF` are core model spaces without dedicated nodes. `SyncRun` is technical runtime state only.

### JCIElementInstance

```text
PiH, CiV, RaN, SYNC, PiF2, PiF1s, PiF1t, PiF1o
```

### GraphObject

```text
RoFOrg, RoFOrgRelationship, RoFTeam, RoFTeamMember, RoFRole,
RoleAssignment, Task, SuccessCriterion, Result, Verification, Evidence,
ERoFObject, ChangeEvent, SyncEvent, RaNConflict, HistoricalCorrection
```

Every concrete node has exactly one listed `entityType`. `PiH`, `ChangeEvent`, `SyncEvent`, and `HistoricalCorrection` are immutable with `status = RECORDED`, `revision = 1`, and `updatedAt = createdAt`.

## 2. Canonical relationships

### Purpose and future

```text
PiH PROVIDES_CONTEXT_TO CiV
CiV INSCRIBES_PURPOSE_IN PiF2
PiF1s CONTRIBUTES_TO PiF2
PiF1t CONTRIBUTES_TO PiF1s
PiF1o CONTRIBUTES_TO PiF1t
```

### Operational work and verification

```text
PiF1o HAS_SUCCESS_CRITERIA SuccessCriterion
PiF1o ACCOUNTABLE_MEMBER RoFTeamMember
PiF1o DECOMPOSES_INTO Task
Task DECOMPOSES_INTO Task
Task DEPENDS_ON Task
Task RESPONSIBLE_TEAM RoFTeam
Task EXECUTED_BY RoleAssignment
Task USES ERoFObject
Task PRODUCES Result
Verification EVALUATES Result
Verification CHECKS SuccessCriterion
Verification USES_EVIDENCE Evidence
Verification SUPERSEDES Verification
```

Only `ATOMIC` Tasks have `EXECUTED_BY`, `USES`, and `PRODUCES`. `COMPOSITE` status is derived from direct subtasks.

### Organisation and environment

```text
RoFOrg HAS_TEAM RoFTeam
RoFTeam HAS_MEMBER RoFTeamMember
RoFTeamMember HAS_ROLE RoFRole
RoFTeamMember HAS_ASSIGNMENT RoleAssignment
RoleAssignment IN_TEAM RoFTeam
RoleAssignment ACTIVATES_ROLE RoFRole
RoleAssignment USES ERoFObject
ERoFObject OWNED_BY RoFOrg
RoFOrgRelationship SOURCE_ORG RoFOrg
RoFOrgRelationship TARGET_ORG RoFOrg
RoFOrgRelationship REPRESENTED_BY RoleAssignment
```

### Rules and conflicts

```text
RaN GOVERNS JCIEntity
RaN APPLIES_IN RoFOrg or RoFTeam
RaNConflict CONFLICTING_RULE RaN
RaNConflict AFFECTS JCIEntity
RaNConflict DETECTED_BY SyncEvent
RaNConflict RESOLVED_BY RoleAssignment
RaNConflict RESOLVED_THROUGH ChangeEvent
RaNConflict USES_EVIDENCE Evidence
```

### Actors, change, and history

```text
JCIEntity CREATED_BY RoleAssignment
ChangeEvent REQUESTED_BY RoleAssignment
HistoricalCorrection CORRECTED_BY RoleAssignment
ChangeEvent USES_EVIDENCE Evidence
HistoricalCorrection USES_EVIDENCE Evidence
historisable JCIEntity CHANGED_BY ChangeEvent
ChangeEvent TRIGGERS SyncEvent
SyncEvent EXECUTES SYNC
SyncEvent AFFECTS JCIEntity
historisable JCIEntity HAS_HISTORICAL_STATE PiH
SyncEvent CREATES_HISTORY PiH
HistoricalCorrection CORRECTS PiH
HistoricalCorrection CAUSED_BY ChangeEvent
SyncEvent CREATES_CORRECTION HistoricalCorrection
HistoricalCorrection SUPERSEDES HistoricalCorrection
replaceable JCIEntity REPLACED_BY same concrete JCIEntity type
```

Inverse readings do not constitute additional stored relationships.

## 3. Structured types

The ontology uses `TypedValue`, `StateSnapshot`, `RelationshipSnapshot`, `TypedValueMap`, `RuleExpression`, and `SyncDefinition`. Unstructured implementation-dependent objects are forbidden in canonical properties.

`RaN` has effect, decision key, scope, governed types, normalised condition, priority, and validity. `RaNConflict` is historisable with `OPEN | RESOLVED`. `PiH` preserves state and relationship snapshots with a canonical SHA-256 hash.

## 4. JSON-LD

Complete exports use JSON-LD 1.1 with `schemas/jci-context.jsonld`. Entity identities use `urn:jci:<UUID>`. Types, properties, and relationships use:

```text
https://eeimicke.github.io/junaco-jci-loop/ns/jci/1.0#
```

The public vocabulary page is `docs/ns/jci/1.0/index.html`.

