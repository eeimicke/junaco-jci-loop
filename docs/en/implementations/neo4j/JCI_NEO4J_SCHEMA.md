# JCI-Neo4j scheme

## Status and purpose

This document specifies the technical mapping of the JCI model to Neo4j. It implements [JCI_CONTEXT.md](../../JCI_CONTEXT.md), [JCI_ONTOLOGY.md](../../JCI_ONTOLOGY.md), [JCI_GRAPH_RULES.md](../../JCI_GRAPH_RULES.md), and [JCI_SYNC_SPEC.md](../../JCI_SYNC_SPEC.md). In the event of a conflict, the domain specification applies; this schema must not change its semantics.

## Common label and property strategy

Each technical node carries `JCIEntity` and exactly one of the abstract labels `JCIElementInstance` or `GraphObject`. In addition, it carries exactly a specific type label that matches `entityType`.

```cypher
CREATE CONSTRAINT jci_entity_id_unique IF NOT EXISTS
FOR (e:JCIEntity) REQUIRE e.id IS UNIQUE;

CREATE CONSTRAINT jci_entity_type_exists IF NOT EXISTS
FOR (e:JCIEntity) REQUIRE e.entityType IS NOT NULL;

CREATE CONSTRAINT jci_entity_name_exists IF NOT EXISTS
FOR (e:JCIEntity) REQUIRE e.name IS NOT NULL;

CREATE CONSTRAINT jci_entity_status_exists IF NOT EXISTS
FOR (e:JCIEntity) REQUIRE e.status IS NOT NULL;

CREATE CONSTRAINT jci_entity_revision_exists IF NOT EXISTS
FOR (e:JCIEntity) REQUIRE e.revision IS NOT NULL;

CREATE CONSTRAINT jci_entity_created_at_exists IF NOT EXISTS
FOR (e:JCIEntity) REQUIRE e.createdAt IS NOT NULL;

CREATE CONSTRAINT jci_entity_updated_at_exists IF NOT EXISTS
FOR (e:JCIEntity) REQUIRE e.updatedAt IS NOT NULL;

CREATE INDEX jci_entity_type_index IF NOT EXISTS FOR (e:JCIEntity) ON (e.entityType);
CREATE INDEX jci_entity_status_index IF NOT EXISTS FOR (e:JCIEntity) ON (e.status);

CREATE CONSTRAINT civ_not_dimension_exists IF NOT EXISTS
FOR (v:CiV) REQUIRE v.notCiV IS NOT NULL;

CREATE CONSTRAINT civ_self_dimension_exists IF NOT EXISTS
FOR (v:CiV) REQUIRE v.selfCiV IS NOT NULL;

CREATE CONSTRAINT civ_to_serve_dimension_exists IF NOT EXISTS
FOR (v:CiV) REQUIRE v.toServeCiV IS NOT NULL;
```

The globally unique `JCIEntity.id` makes additional ID constraints for each specific label technically redundant. Specific constraints are only created for other technically unique keys.

### Complex structured values

Neo4j properties do not store nested JSON objects. The canonical structures from [`JCI_CONTEXT.md`](../../JCI_CONTEXT.md) are therefore projected as canonical JSON character strings without loss of semantics:

| Technical field                       | Neo4j Property         |
| ------------------------------------- | ---------------------- |
| `RaN.condition`                       | `conditionJson`        |
| `SYNC.definition`                     | `definitionJson`       |
| `Result.value`                        | `valueJson`            |
| `PiH.stateData`                       | `stateDataJson`        |
| `PiH.relationshipData`                | `relationshipDataJson` |
| `HistoricalCorrection.previousValue`  | `previousValueJson`    |
| `HistoricalCorrection.correctedValue` | `correctedValueJson`   |

The JSON strings use UTF-8, lexicographically sorted object keys, and the canonical data type rules from section 2.2.7. `PiH.contentHash` is calculated from the domain structures before this Neo4j projection.

### Technical required fields for change, verification, and correction

The following fields specify how the already defined domain processes are stored. Every listed node additionally carries the `JCIEntity` label and its abstract and concrete type labels.

| Node                   | Property                   | Meaning                                                                                |
| ---------------------- | -------------------------- | -------------------------------------------------------------------------------------- |
| `ChangeEvent`          | `idempotencyKey`           | immutable, graph-wide unique identifier of the domain change request                   |
| `ChangeEvent`          | `targetEntityId`           | UUID of the requested target entity, even if a `CREATED` attempt fails before creation |
| `ChangeEvent`          | `targetEntityType`         | concrete type of the requested target entity                                           |
| `ChangeEvent`          | `requestedRevision`        | expected positive source revision; absent for `CREATED`                                |
| `SyncEvent`            | `runId`                    | immutable, graph-wide unique identifier of the completed technical run                 |
| `RoleAssignment`       | `bootstrapKey`             | value `ROOT`, set exclusively on the initial root assignment                           |
| `Verification`         | `evaluatedResultRevision`  | exact revision of the `Result` connected through `EVALUATES` that was evaluated        |
| `Verification`         | `checkedCriterionRevision` | exact revision of the `SuccessCriterion` connected through `CHECKS` that was checked   |
| `HistoricalCorrection` | `baseHistoryViewHash`      | SHA-256 of the effective historical view reread before correction                      |

Neo4j does not store `null` as a property. `requestedRevision` is therefore absent exactly when `changeType = 'CREATED'`. For every other change type, the property must exist and be a positive integer.

A historical correction request additionally uses the canonical relationship:

```text
(:ChangeEvent)-[:TARGETS_HISTORY]->(:PiH)
```

It identifies the immutable `PiH` addressed by the request. It replaces neither `CHANGED_BY` nor `CORRECTS`: a `PiH` never receives `CHANGED_BY`; the `HistoricalCorrection` created only after successful validation still points through `CORRECTS` to the same `PiH`.

## Labels and properties for tasks

Each Task carries at least the labels `JCIEntity`, `GraphObject` and `Task`. In addition to the common mandatory fields, it is mandatory to have:

```text
taskKind = ATOMIC | COMPOSITE
status   = DRAFT | ACTIVE | BLOCKED | COMPLETED | REPLACED | REVOKED
```

`PiF1o` is a desired state. `Task` is an activity. “Develop customer portal” is therefore modeled as `COMPOSITE`-Task; For example, the associated `PiF1o` reads “The customer portal can be used productively”.

## Relationship types for tasks

| Source  | Relationship       | Target           | Meaning                                        |
| ------- | ------------------ | ---------------- | ---------------------------------------------- |
| `PiF1o` | `DECOMPOSES_INTO`  | `Task`           | direct operational target context of each task |
| `Task`  | `DECOMPOSES_INTO`  | `Task`           | direct parent/subtask structure                |
| `Task`  | `DEPENDS_ON`       | `Task`           | technical execution requirements               |
| `Task`  | `RESPONSIBLE_TEAM` | `RoFTeam`        | exactly one responsible team                   |
| `Task`  | `EXECUTED_BY`      | `RoleAssignment` | Execution of exclusively atomic tasks          |
| `Task`  | `USES`             | `ERoFObject`     | Environmental use of exclusively atomic tasks  |
| `Task`  | `PRODUCES`         | `Result`         | Result of exclusively atomic tasks             |

## Directly enforceable constraints

The following Cypher instructions require Neo4j 5:

```cypher
CREATE CONSTRAINT task_id_unique IF NOT EXISTS
FOR (t:Task) REQUIRE t.id IS UNIQUE;

CREATE CONSTRAINT task_entity_type_exists IF NOT EXISTS
FOR (t:Task) REQUIRE t.entityType IS NOT NULL;

CREATE CONSTRAINT task_kind_exists IF NOT EXISTS
FOR (t:Task) REQUIRE t.taskKind IS NOT NULL;

CREATE CONSTRAINT task_status_exists IF NOT EXISTS
FOR (t:Task) REQUIRE t.status IS NOT NULL;

CREATE CONSTRAINT task_revision_exists IF NOT EXISTS
FOR (t:Task) REQUIRE t.revision IS NOT NULL;

CREATE INDEX task_kind_index IF NOT EXISTS FOR (t:Task) ON (t.taskKind);
CREATE INDEX task_status_index IF NOT EXISTS FOR (t:Task) ON (t.status);

CREATE CONSTRAINT change_event_idempotency_key_exists IF NOT EXISTS
FOR (e:ChangeEvent) REQUIRE e.idempotencyKey IS NOT NULL;

CREATE CONSTRAINT change_event_idempotency_key_unique IF NOT EXISTS
FOR (e:ChangeEvent) REQUIRE e.idempotencyKey IS UNIQUE;

CREATE CONSTRAINT change_event_idempotency_key_type IF NOT EXISTS
FOR (e:ChangeEvent) REQUIRE e.idempotencyKey IS :: STRING;

CREATE CONSTRAINT change_event_target_entity_id_exists IF NOT EXISTS
FOR (e:ChangeEvent) REQUIRE e.targetEntityId IS NOT NULL;

CREATE CONSTRAINT change_event_target_entity_type_exists IF NOT EXISTS
FOR (e:ChangeEvent) REQUIRE e.targetEntityType IS NOT NULL;

CREATE CONSTRAINT change_event_target_entity_id_type IF NOT EXISTS
FOR (e:ChangeEvent) REQUIRE e.targetEntityId IS :: STRING;

CREATE CONSTRAINT change_event_target_entity_type_type IF NOT EXISTS
FOR (e:ChangeEvent) REQUIRE e.targetEntityType IS :: STRING;

CREATE CONSTRAINT change_event_requested_revision_type IF NOT EXISTS
FOR (e:ChangeEvent) REQUIRE e.requestedRevision IS :: INTEGER;

CREATE INDEX change_event_target_index IF NOT EXISTS
FOR (e:ChangeEvent) ON (e.targetEntityId, e.targetEntityType);

CREATE CONSTRAINT sync_event_run_id_exists IF NOT EXISTS
FOR (e:SyncEvent) REQUIRE e.runId IS NOT NULL;

CREATE CONSTRAINT sync_event_run_id_unique IF NOT EXISTS
FOR (e:SyncEvent) REQUIRE e.runId IS UNIQUE;

CREATE CONSTRAINT sync_event_run_id_type IF NOT EXISTS
FOR (e:SyncEvent) REQUIRE e.runId IS :: STRING;

CREATE CONSTRAINT role_assignment_bootstrap_key_unique IF NOT EXISTS
FOR (a:RoleAssignment) REQUIRE a.bootstrapKey IS UNIQUE;

CREATE CONSTRAINT role_assignment_bootstrap_key_type IF NOT EXISTS
FOR (a:RoleAssignment) REQUIRE a.bootstrapKey IS :: STRING;

CREATE CONSTRAINT verification_result_revision_exists IF NOT EXISTS
FOR (v:Verification) REQUIRE v.evaluatedResultRevision IS NOT NULL;

CREATE CONSTRAINT verification_result_revision_type IF NOT EXISTS
FOR (v:Verification) REQUIRE v.evaluatedResultRevision IS :: INTEGER;

CREATE CONSTRAINT verification_criterion_revision_exists IF NOT EXISTS
FOR (v:Verification) REQUIRE v.checkedCriterionRevision IS NOT NULL;

CREATE CONSTRAINT verification_criterion_revision_type IF NOT EXISTS
FOR (v:Verification) REQUIRE v.checkedCriterionRevision IS :: INTEGER;

CREATE CONSTRAINT historical_correction_base_view_hash_exists IF NOT EXISTS
FOR (c:HistoricalCorrection) REQUIRE c.baseHistoryViewHash IS NOT NULL;

CREATE CONSTRAINT historical_correction_base_view_hash_type IF NOT EXISTS
FOR (c:HistoricalCorrection) REQUIRE c.baseHistoryViewHash IS :: STRING;

CREATE CONSTRAINT historical_correction_fields_exists IF NOT EXISTS
FOR (c:HistoricalCorrection) REQUIRE c.correctedFields IS NOT NULL;

CREATE CONSTRAINT historical_correction_fields_type IF NOT EXISTS
FOR (c:HistoricalCorrection) REQUIRE c.correctedFields IS :: LIST<STRING NOT NULL>;

CREATE CONSTRAINT pih_origin_revision_unique IF NOT EXISTS
FOR (h:PiH) REQUIRE (h.originalEntityId, h.originalRevision) IS UNIQUE;

CREATE CONSTRAINT sync_event_started_at_exists IF NOT EXISTS
FOR (e:SyncEvent) REQUIRE e.startedAt IS NOT NULL;

CREATE CONSTRAINT sync_event_completed_at_exists IF NOT EXISTS
FOR (e:SyncEvent) REQUIRE e.completedAt IS NOT NULL;

CREATE CONSTRAINT sync_event_outcome_exists IF NOT EXISTS
FOR (e:SyncEvent) REQUIRE e.outcome IS NOT NULL;

CREATE CONSTRAINT sync_event_affected_count_exists IF NOT EXISTS
FOR (e:SyncEvent) REQUIRE e.affectedCount IS NOT NULL;

CREATE CONSTRAINT sync_event_changed_count_exists IF NOT EXISTS
FOR (e:SyncEvent) REQUIRE e.changedCount IS NOT NULL;

CREATE CONSTRAINT sync_event_history_count_exists IF NOT EXISTS
FOR (e:SyncEvent) REQUIRE e.historyCount IS NOT NULL;

CREATE CONSTRAINT sync_event_correction_count_exists IF NOT EXISTS
FOR (e:SyncEvent) REQUIRE e.correctionCount IS NOT NULL;

CREATE CONSTRAINT sync_event_conflict_count_exists IF NOT EXISTS
FOR (e:SyncEvent) REQUIRE e.conflictCount IS NOT NULL;
```

## Atomic bootstrap of an empty graph

The bootstrap is the only creation that cannot use an existing `RoleAssignment` and a previously active SYNC definition. It is permitted only while no node with the `JCIEntity` label exists. One transaction creates the minimal organization, one technical member, its role, the root assignment, and exactly one initial active SYNC definition. The root assignment is permanently identified by `bootstrapKey = 'ROOT'` and remains the only active `JCIEntity` without `CREATED_BY`.

The following parameterized query is an executable bootstrap example. It returns exactly one row when it writes. If it returns no row, the graph was not empty; the calling deployment step must treat this as an error and must not attempt a second bootstrap.

```cypher
MATCH (existing:JCIEntity)
WITH count(existing) AS existingCount
WHERE existingCount = 0
WITH datetime() AS now
CREATE (org:JCIEntity:GraphObject:RoFOrg {
  id: randomUUID(), entityType: 'RoFOrg', name: $organizationName,
  legalName: $organizationName, orgType: 'COMPANY', status: 'ACTIVE',
  revision: 1, createdAt: now, updatedAt: now
})
CREATE (team:JCIEntity:GraphObject:RoFTeam {
  id: randomUUID(), entityType: 'RoFTeam', name: 'JCI Bootstrap',
  teamType: 'SERVICE', validFrom: now, status: 'ACTIVE',
  revision: 1, createdAt: now, updatedAt: now
})
CREATE (member:JCIEntity:GraphObject:RoFTeamMember {
  id: randomUUID(), entityType: 'RoFTeamMember', name: 'JCI System',
  displayName: 'JCI System', memberType: 'TECHNICAL', status: 'ACTIVE',
  revision: 1, createdAt: now, updatedAt: now
})
CREATE (role:JCIEntity:GraphObject:RoFRole {
  id: randomUUID(), entityType: 'RoFRole', name: 'JCI Bootstrap Administrator',
  roleName: 'JCI Bootstrap Administrator',
  responsibility: 'One-time initialization of the JCI graph', status: 'ACTIVE',
  revision: 1, createdAt: now, updatedAt: now
})
CREATE (root:JCIEntity:GraphObject:RoleAssignment {
  id: randomUUID(), entityType: 'RoleAssignment', name: 'JCI Root Assignment',
  bootstrapKey: 'ROOT', validFrom: now, status: 'ACTIVE',
  revision: 1, createdAt: now, updatedAt: now
})
CREATE (definition:JCIEntity:JCIElementInstance:SYNC {
  id: randomUUID(), entityType: 'SYNC', name: 'Initial JCI SYNC definition',
  version: $syncVersion, definitionJson: $definitionJson,
  validFrom: now, status: 'ACTIVE', revision: 1,
  createdAt: now, updatedAt: now
})
CREATE (org)-[:HAS_TEAM]->(team)
CREATE (team)-[:HAS_MEMBER {validFrom: now}]->(member)
CREATE (member)-[:HAS_ROLE {validFrom: now}]->(role)
CREATE (member)-[:HAS_ASSIGNMENT]->(root)
CREATE (root)-[:IN_TEAM]->(team)
CREATE (root)-[:ACTIVATES_ROLE]->(role)
FOREACH (created IN [org, team, member, role, definition] |
  CREATE (created)-[:CREATED_BY]->(root)
)
RETURN root.id AS rootRoleAssignmentId, definition.id AS initialSyncDefinitionId;
```

The precondition and every `CREATE` statement must run in the same Neo4j transaction. After commit, the existing root together with the empty-graph check prevents another bootstrap. Every later entity, including a new SYNC definition, is created exclusively through the regular `ChangeEvent`/`SyncEvent` process.

Neo4j constraints do not fully enforce enum values, cardinalities, and graph-wide cycle rules. These rules are checked by `SYNC` before writing and by validation queries after writing.

## Validation queries

Each subsequent query must return zero rows for a valid graph.

### CiV dimensions, value holder, and PiF2 scope

```cypher
MATCH (value:JCIEntity:CiV)
OPTIONAL MATCH (value)-[:HELD_BY]->(holder:JCIEntity)
WITH value, collect(DISTINCT holder) AS holders
WHERE value.notCiV IS NULL OR trim(value.notCiV) = ''
   OR value.selfCiV IS NULL OR trim(value.selfCiV) = ''
   OR value.toServeCiV IS NULL OR trim(value.toServeCiV) = ''
   OR value.purpose IS NOT NULL OR value.values IS NOT NULL OR value.scope IS NOT NULL
   OR size(holders) <> 1
   OR (size(holders) = 1 AND
       NOT ('RoFOrg' IN labels(holders[0]) OR
            'RoFTeam' IN labels(holders[0]) OR
            ('RoFTeamMember' IN labels(holders[0]) AND holders[0].memberType = 'HUMAN')))
RETURN value.id AS valueId, [holder IN holders | holder.id] AS holderIds;
```

```cypher
MATCH (value:CiV)-[:INFORMED_BY]->(source:JCIEntity)
WHERE value = source OR NOT source:CiV
RETURN value.id AS valueId, source.id AS invalidSourceId;
```

```cypher
MATCH (future:JCIEntity:PiF2)
OPTIONAL MATCH (value:CiV)-[:INSCRIBES_PURPOSE_IN]->(future)
OPTIONAL MATCH (value)-[:HELD_BY]->(holder:JCIEntity)
WITH future, collect(DISTINCT value) AS values, collect(DISTINCT holder) AS holders
WHERE size(values) < 1 OR size(holders) <> 1
RETURN future.id AS futureId,
       [value IN values | value.id] AS valueIds,
       [holder IN holders | holder.id] AS holderIds;
```

These queries validate structure, not the domain decision itself. `SYNC` must not infer `INFORMED_BY` or value dimensions from names, memberships, or organizational affiliations. An existing bundled CiV with `purpose`, `values`, or `scope` is not migrated automatically: the list must be split into individual CiV, every three-dimensional description must be confirmed by a human, and all relationships must be reconnected under control.

### Invalid enum values

```cypher
MATCH (t:Task)
WHERE NOT t.taskKind IN ['ATOMIC', 'COMPOSITE']
   OR NOT t.status IN ['DRAFT', 'ACTIVE', 'BLOCKED', 'COMPLETED', 'REPLACED', 'REVOKED']
RETURN t.id AS taskId, t.taskKind, t.status;
```

### Missing or multiple PiF1o and team context

```cypher
MATCH (t:Task)
OPTIONAL MATCH (p:PiF1o)-[:DECOMPOSES_INTO]->(t)
OPTIONAL MATCH (t)-[:RESPONSIBLE_TEAM]->(team:RoFTeam)
WITH t, count(DISTINCT p) AS pifCount, count(DISTINCT team) AS teamCount
WHERE pifCount <> 1 OR teamCount <> 1
RETURN t.id AS taskId, pifCount, teamCount;
```

### Invalid Task type structure

```cypher
MATCH (t:Task)
OPTIONAL MATCH (t)-[:DECOMPOSES_INTO]->(child:Task)
OPTIONAL MATCH (t)-[:EXECUTED_BY]->(executor:RoleAssignment)
OPTIONAL MATCH (t)-[:USES]->(environment:ERoFObject)
OPTIONAL MATCH (t)-[:PRODUCES]->(result:Result)
WITH t, count(DISTINCT child) AS childCount,
     count(DISTINCT executor) AS executorCount,
     count(DISTINCT environment) AS environmentCount,
     count(DISTINCT result) AS resultCount
WHERE (t.taskKind = 'ATOMIC' AND childCount > 0)
   OR (t.taskKind = 'COMPOSITE' AND
       (childCount = 0 OR executorCount > 0 OR environmentCount > 0 OR resultCount > 0))
   OR (t.taskKind = 'ATOMIC' AND t.status IN ['ACTIVE', 'COMPLETED'] AND executorCount = 0)
RETURN t.id AS taskId, childCount, executorCount, environmentCount, resultCount;
```

### Multiple direct parent tasks or different PiF1o context

```cypher
MATCH (child:Task)
OPTIONAL MATCH (parent:Task)-[:DECOMPOSES_INTO]->(child)
WITH child, collect(DISTINCT parent) AS parents
WHERE size(parents) > 1
   OR any(parent IN parents WHERE NOT EXISTS {
        MATCH (p:PiF1o)-[:DECOMPOSES_INTO]->(parent)
        MATCH (p)-[:DECOMPOSES_INTO]->(child)
      })
RETURN child.id AS taskId, [parent IN parents | parent.id] AS parentIds;
```

### Cycles in hierarchy or dependencies

```cypher
MATCH (t:Task)-[:DECOMPOSES_INTO*1..]->(t)
RETURN DISTINCT t.id AS taskHierarchyCycle;
```

```cypher
MATCH (t:Task)-[:DEPENDS_ON*1..]->(t)
RETURN DISTINCT t.id AS dependencyCycle;
```

### Unmet dependency without BLOCKED

```cypher
MATCH (t:Task)-[:DEPENDS_ON]->(required:Task)
WHERE required.status <> 'COMPLETED' AND t.status <> 'BLOCKED'
RETURN t.id AS taskId, required.id AS unmetDependencyId, t.status AS actualStatus;
```

### Execution outside the responsible team

```cypher
MATCH (t:Task {taskKind: 'ATOMIC'})-[:RESPONSIBLE_TEAM]->(team:RoFTeam)
WHERE t.status IN ['ACTIVE', 'COMPLETED']
  AND NOT EXISTS {
    MATCH (t)-[:EXECUTED_BY]->(:RoleAssignment)-[:IN_TEAM]->(team)
  }
RETURN t.id AS taskId, team.id AS responsibleTeamId;
```

## RaN priority and conflicts

`RaN.priority` is a mandatory integer. A larger number means higher priority in an actual contradiction; `ruleType` has no technical ranking. A conflict that cannot be resolved automatically is stored as a node with the labels `JCIEntity`, `GraphObject`, and `RaNConflict`.

```cypher
CREATE CONSTRAINT ran_id_unique IF NOT EXISTS
FOR (r:RaN) REQUIRE r.id IS UNIQUE;

CREATE CONSTRAINT ran_priority_exists IF NOT EXISTS
FOR (r:RaN) REQUIRE r.priority IS NOT NULL;

CREATE INDEX ran_priority_index IF NOT EXISTS
FOR (r:RaN) ON (r.priority);

CREATE CONSTRAINT ran_conflict_id_unique IF NOT EXISTS
FOR (c:RaNConflict) REQUIRE c.id IS UNIQUE;

CREATE CONSTRAINT ran_conflict_key_unique IF NOT EXISTS
FOR (c:RaNConflict) REQUIRE c.conflictKey IS UNIQUE;

CREATE CONSTRAINT ran_conflict_type_exists IF NOT EXISTS
FOR (c:RaNConflict) REQUIRE c.conflictType IS NOT NULL;

CREATE CONSTRAINT ran_conflict_detected_at_exists IF NOT EXISTS
FOR (c:RaNConflict) REQUIRE c.detectedAt IS NOT NULL;
```

### Invalid RaNConflict properties or cardinalities

```cypher
MATCH (c:RaNConflict)
OPTIONAL MATCH (c)-[:CONFLICTING_RULE]->(rule:RaN)
OPTIONAL MATCH (c)-[:AFFECTS]->(affected:JCIEntity)
OPTIONAL MATCH (c)-[:DETECTED_BY]->(event:SyncEvent)
OPTIONAL MATCH (c)-[:RESOLVED_BY]->(actor:RoleAssignment)
OPTIONAL MATCH (c)-[:RESOLVED_THROUGH]->(change:ChangeEvent)
WITH c,
     count(DISTINCT rule) AS ruleCount,
     count(DISTINCT affected) AS affectedCount,
     count(DISTINCT event) AS eventCount,
     count(DISTINCT actor) AS actorCount,
     count(DISTINCT change) AS changeCount
WHERE c.conflictKey IS NULL
   OR NOT c.conflictType IN ['PRIORITY_TIE', 'UNEVALUABLE']
   OR NOT c.status IN ['OPEN', 'RESOLVED']
   OR ruleCount < 1 OR affectedCount < 1 OR eventCount <> 1
   OR (c.conflictType = 'PRIORITY_TIE' AND ruleCount < 2)
   OR (c.status = 'OPEN' AND (actorCount <> 0 OR changeCount <> 0))
   OR (c.status = 'RESOLVED' AND
       (actorCount <> 1 OR changeCount <> 1 OR c.resolvedAt IS NULL OR c.resolution IS NULL))
RETURN c.id AS conflictId, ruleCount, affectedCount, eventCount, actorCount, changeCount;
```

### PRIORITY_TIE without the same highest priority value

```cypher
MATCH (c:RaNConflict {conflictType: 'PRIORITY_TIE'})-[:CONFLICTING_RULE]->(r:RaN)
WITH c, count(DISTINCT r) AS ruleCount, collect(DISTINCT r.priority) AS priorities
WHERE ruleCount < 2 OR size(priorities) <> 1
RETURN c.id AS conflictId, ruleCount, priorities;
```

The detection of a content contradiction cannot be done using Neo4j constraints alone. It is part of the technical rule evaluation of `SYNC`. The database then validates that conflict nodes, priorities, and resolution relationships have been completely saved.

## Complete validation of the remaining model areas

### Concrete type label and abstract class

```cypher
MATCH (e:JCIEntity)
WITH e,
     [label IN labels(e) WHERE label IN [
       'PiH','CiV','RaN','SYNC','PiF2','PiF1s','PiF1t','PiF1o',
       'RoFOrg','RoFOrgRelationship','RoFTeam','RoFTeamMember','RoFRole','RoleAssignment',
       'Task','SuccessCriterion','Result','Verification','Evidence','ERoFObject',
       'ChangeEvent','SyncEvent','RaNConflict','HistoricalCorrection'
     ]] AS concrete,
     [label IN labels(e) WHERE label IN ['JCIElementInstance','GraphObject']] AS abstract
WHERE size(concrete) <> 1 OR size(abstract) <> 1 OR e.entityType <> concrete[0]
RETURN e.id AS entityId, e.entityType, concrete, abstract;
```

### Common mandatory values ​​and immutable documents

```cypher
MATCH (e:JCIEntity)
WHERE e.revision IS NULL OR e.revision < 1
   OR e.createdAt IS NULL OR e.updatedAt IS NULL OR e.updatedAt < e.createdAt
   OR e.name IS NULL OR trim(e.name) = ''
   OR (e.entityType IN ['PiH','ChangeEvent','SyncEvent','HistoricalCorrection']
       AND (e.revision <> 1 OR e.status <> 'RECORDED' OR e.updatedAt <> e.createdAt))
RETURN e.id AS entityId, e.entityType, e.revision, e.status;
```

### Closed bootstrap and creation responsibility

An initialized graph has exactly one root assignment with `bootstrapKey = 'ROOT'` and at least one active SYNC definition. No other `bootstrapKey` value is permitted. The following query finds a missing, duplicate, or incomplete bootstrap:

```cypher
MATCH (entity:JCIEntity)
WITH count(entity) AS entityCount,
     COUNT {
       MATCH (:JCIEntity:GraphObject:RoleAssignment {bootstrapKey: 'ROOT'})
     } AS rootCount,
     COUNT {
       MATCH (:JCIEntity:JCIElementInstance:SYNC {status: 'ACTIVE'})
     } AS activeDefinitionCount,
     COUNT {
       MATCH (assignment:JCIEntity:GraphObject:RoleAssignment)
       WHERE assignment.bootstrapKey IS NOT NULL
          AND assignment.bootstrapKey <> 'ROOT'
     } AS invalidBootstrapKeyCount
WHERE entityCount > 0
  AND (rootCount <> 1 OR activeDefinitionCount < 1 OR invalidBootstrapKeyCount > 0)
RETURN entityCount, rootCount, activeDefinitionCount, invalidBootstrapKeyCount;
```

The root assignment is the only permitted exception to `CREATED_BY`. Every other domain or documentation node must have exactly one creating actor after the atomic bootstrap:

```cypher
MATCH (entity:JCIEntity)
OPTIONAL MATCH (entity)-[:CREATED_BY]->(actor:JCIEntity:GraphObject:RoleAssignment)
WITH entity, count(DISTINCT actor) AS actorCount,
     ('RoleAssignment' IN labels(entity) AND entity.bootstrapKey = 'ROOT') AS isRoot
WHERE actorCount > 1
   OR (isRoot AND actorCount <> 0)
   OR (NOT isRoot AND entity.status <> 'DRAFT' AND actorCount <> 1)
RETURN entity.id AS entityId, entity.entityType, isRoot, actorCount;
```

An imported node in `DRAFT` may temporarily have no creating actor; more than one `CREATED_BY` edge is prohibited even there. Exactly one creating actor must exist before activation or completion.

**Short example:** During the first deployment, the bootstrap transaction creates the `JCI Root Assignment` and the initial SYNC definition together. The very next regularly created domain node requires `CREATED_BY`; a second assignment with `bootstrapKey = 'ROOT'` fails the uniqueness constraint.

### ChangeEvent target, revision, and lifecycle

The target properties on `ChangeEvent` remain available even when an attempt fails before a node is created. `HISTORICAL_CORRECTION` may target only a `PiH` at revision `1`. Every other change type may target only historizable types.

```cypher
MATCH (change:JCIEntity:GraphObject:ChangeEvent)
WITH change,
     ['CiV','RaN','SYNC','PiF2','PiF1s','PiF1t','PiF1o',
      'RoFOrg','RoFOrgRelationship','RoFTeam','RoFTeamMember','RoFRole',
      'RoleAssignment','Task','SuccessCriterion','Result','Verification',
      'Evidence','ERoFObject','RaNConflict'] AS mutableTargetTypes,
     ['CREATED','CHANGED','ACHIEVED','COMPLETED','REPLACED',
      'REVOKED','RESOLVED','HISTORICAL_CORRECTION'] AS changeTypes
WHERE change.changeType IS NULL OR NOT change.changeType IN changeTypes
   OR change.idempotencyKey IS NULL
   OR valueType(change.idempotencyKey) <> 'STRING NOT NULL'
   OR trim(toString(change.idempotencyKey)) = ''
   OR change.targetEntityId IS NULL
   OR valueType(change.targetEntityId) <> 'STRING NOT NULL'
   OR NOT (toLower(toString(change.targetEntityId)) =~
      '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$')
   OR change.targetEntityType IS NULL
   OR valueType(change.targetEntityType) <> 'STRING NOT NULL'
   OR (change.requestedRevision IS NOT NULL
       AND valueType(change.requestedRevision) <> 'INTEGER NOT NULL')
   OR (change.changeType = 'CREATED' AND change.requestedRevision IS NOT NULL)
   OR (change.changeType <> 'CREATED'
       AND (change.requestedRevision IS NULL
            OR toIntegerOrNull(change.requestedRevision) < 1))
   OR (change.changeType = 'HISTORICAL_CORRECTION'
       AND (change.targetEntityType <> 'PiH' OR change.requestedRevision <> 1))
   OR (change.changeType <> 'HISTORICAL_CORRECTION'
       AND NOT change.targetEntityType IN mutableTargetTypes)
RETURN change.id AS changeEventId, change.changeType, change.targetEntityId,
       change.targetEntityType, change.requestedRevision;
```

`CHANGED_BY` depends on the request type and outcome. A normal request has exactly one matching source entity. An unfinished or unsuccessful `CREATED` request has none; after exactly one successful run, the newly created entity points to it. A historical correction has exactly one `TARGETS_HISTORY` instead of `CHANGED_BY`.

```cypher
MATCH (change:JCIEntity:GraphObject:ChangeEvent)
WITH change,
     COUNT {
       MATCH (source:JCIEntity)-[:CHANGED_BY]->(change)
     } AS sourceCount,
     COUNT {
       MATCH (source:JCIEntity)-[:CHANGED_BY]->(change)
       WHERE source.id = change.targetEntityId
         AND source.entityType = change.targetEntityType
     } AS matchingSourceCount,
     COUNT {
       MATCH (change)-[:TARGETS_HISTORY]->(history:JCIEntity:PiH)
     } AS historyTargetCount,
     COUNT {
       MATCH (change)-[:TARGETS_HISTORY]->(history:JCIEntity:PiH)
       WHERE history.id = change.targetEntityId
         AND history.entityType = change.targetEntityType
         AND history.revision = change.requestedRevision
     } AS matchingHistoryTargetCount,
     COUNT {
       MATCH (change)-[:TRIGGERS]->(:JCIEntity:GraphObject:SyncEvent)
     } AS completedRunCount,
     COUNT {
       MATCH (change)-[:TRIGGERS]->(:JCIEntity:GraphObject:SyncEvent {outcome: 'SUCCESS'})
     } AS successfulRunCount
WHERE (change.changeType = 'CREATED' AND
       (historyTargetCount <> 0 OR successfulRunCount > 1
        OR (successfulRunCount = 0 AND sourceCount <> 0)
        OR (successfulRunCount = 1 AND
            (sourceCount <> 1 OR matchingSourceCount <> 1))))
   OR (change.changeType = 'HISTORICAL_CORRECTION' AND
       (sourceCount <> 0 OR historyTargetCount <> 1
        OR matchingHistoryTargetCount <> 1))
   OR (NOT change.changeType IN ['CREATED','HISTORICAL_CORRECTION'] AND
       (sourceCount <> 1 OR matchingSourceCount <> 1 OR historyTargetCount <> 0))
RETURN change.id AS changeEventId, change.changeType,
       sourceCount, matchingSourceCount, historyTargetCount,
       matchingHistoryTargetCount, completedRunCount, successfulRunCount;
```

```cypher
MATCH (source)-[relationship:TARGETS_HISTORY]->(target)
WHERE NOT ('JCIEntity' IN labels(source)) OR NOT ('GraphObject' IN labels(source))
   OR NOT ('ChangeEvent' IN labels(source))
   OR NOT ('JCIEntity' IN labels(target)) OR NOT ('PiH' IN labels(target))
RETURN elementId(relationship) AS relationshipId,
       labels(source) AS sourceLabels, labels(target) AS targetLabels;
```

```cypher
MATCH (source)-[relationship:TRIGGERS]->(target)
WHERE NOT ('JCIEntity' IN labels(source)) OR NOT ('GraphObject' IN labels(source))
   OR NOT ('ChangeEvent' IN labels(source))
   OR NOT ('JCIEntity' IN labels(target)) OR NOT ('GraphObject' IN labels(target))
   OR NOT ('SyncEvent' IN labels(target))
RETURN elementId(relationship) AS relationshipId,
       labels(source) AS sourceLabels, labels(target) AS targetLabels;
```

Parallel duplicate edges must not bypass a cardinality check through `DISTINCT` on the target node:

```cypher
MATCH (source:JCIEntity)-[relationship]->(target:JCIEntity)
WHERE type(relationship) IN [
  'CREATED_BY','REQUESTED_BY','CORRECTED_BY','CHANGED_BY',
  'TARGETS_HISTORY','TRIGGERS','EXECUTES','AFFECTS',
  'HAS_HISTORICAL_STATE','CREATES_HISTORY','CREATES_CORRECTION',
  'CORRECTS','CAUSED_BY','SUPERSEDES'
]
WITH source, type(relationship) AS relationshipType, target,
     count(relationship) AS relationshipCount
WHERE relationshipCount > 1
RETURN source.id AS sourceId, relationshipType,
       target.id AS targetId, relationshipCount;
```

For a normal change, the target can already be resolved at acceptance and must therefore be named through `AFFECTS` by every completed run. For `CREATED`, this is mandatory for the successful run; an earlier failed attempt may remain documented without a target reference:

```cypher
MATCH (target:JCIEntity)-[:CHANGED_BY]->(change:JCIEntity:GraphObject:ChangeEvent)
MATCH (change)-[:TRIGGERS]->(event:JCIEntity:GraphObject:SyncEvent)
WHERE (change.changeType <> 'CREATED' OR event.outcome = 'SUCCESS')
  AND NOT EXISTS { MATCH (event)-[:AFFECTS]->(target) }
RETURN change.id AS changeEventId, event.id AS syncEventId, target.id AS missingAffectedId;
```

```cypher
MATCH (change:JCIEntity:GraphObject:ChangeEvent)-[:TARGETS_HISTORY]->(history:JCIEntity:PiH)
MATCH (change)-[:TRIGGERS]->(event:JCIEntity:GraphObject:SyncEvent)
WHERE NOT EXISTS { MATCH (event)-[:AFFECTS]->(history) }
RETURN change.id AS changeEventId, event.id AS syncEventId, history.id AS missingAffectedId;
```

Zero completed runs is a permitted **pending** state. Every completed technical run is appended exactly once as a new immutable `SyncEvent`. Graph-wide uniqueness of `runId`, `revision = 1`, `status = 'RECORDED'`, and `updatedAt = createdAt` protects the stored result. Whether every terminal `SyncRun` outside the graph already has an event must additionally be checked by technical run/outbox reconciliation; this fact cannot be derived from Neo4j alone.

Regardless of the number of completed attempts, a domain change request may be committed successfully at most once:

```cypher
MATCH (change:JCIEntity:GraphObject:ChangeEvent)
WITH change, COUNT {
  MATCH (change)-[:TRIGGERS]
        ->(:JCIEntity:GraphObject:SyncEvent {outcome: 'SUCCESS'})
} AS successfulRunCount
WHERE successfulRunCount > 1
RETURN change.id AS changeEventId, successfulRunCount;
```

An unsuccessful run must create neither a historical state nor a historical correction:

```cypher
MATCH (change:JCIEntity:GraphObject:ChangeEvent)-[:TRIGGERS]
      ->(event:JCIEntity:GraphObject:SyncEvent)
WITH change, event,
     COUNT {
       MATCH (event)-[:CREATES_HISTORY]->(:JCIEntity:PiH)
     } AS historyCount,
     COUNT {
       MATCH (event)-[:CREATES_CORRECTION]
             ->(:JCIEntity:GraphObject:HistoricalCorrection)
     } AS correctionCount
WHERE event.outcome IN ['FAILED','CONFLICT']
  AND (historyCount <> 0 OR correctionCount <> 0)
RETURN change.id AS changeEventId, event.id AS syncEventId,
       event.outcome, historyCount, correctionCount;
```

A successful normal change request creates exactly the `PiH` of the requested source revision for its existing target entity. Additional domain entities that actually change may receive their own additional `PiH` nodes:

```cypher
MATCH (target:JCIEntity)-[:CHANGED_BY]
      ->(change:JCIEntity:GraphObject:ChangeEvent)-[:TRIGGERS]
      ->(event:JCIEntity:GraphObject:SyncEvent {outcome: 'SUCCESS'})
WHERE NOT change.changeType IN ['CREATED','HISTORICAL_CORRECTION']
WITH target, change, event, COUNT {
  MATCH (event)-[:CREATES_HISTORY]->(history:JCIEntity:PiH)
  WHERE history.originalEntityId = target.id
    AND history.originalEntityType = target.entityType
    AND history.originalRevision = change.requestedRevision
} AS targetHistoryCount
WHERE targetHistoryCount <> 1
RETURN change.id AS changeEventId, event.id AS syncEventId,
       target.id AS targetEntityId, change.requestedRevision,
       targetHistoryCount;
```

A successful historical correction request creates exactly one correction whose `CORRECTS` and `CAUSED_BY` paths lead back to the same `PiH` and the same `ChangeEvent`:

```cypher
MATCH (change:JCIEntity:GraphObject:ChangeEvent {changeType: 'HISTORICAL_CORRECTION'})
      -[:TARGETS_HISTORY]->(history:JCIEntity:PiH)
MATCH (change)-[:TRIGGERS]
      ->(event:JCIEntity:GraphObject:SyncEvent {outcome: 'SUCCESS'})
WITH change, history, event,
     COUNT {
       MATCH (event)-[:CREATES_CORRECTION]
             ->(:JCIEntity:GraphObject:HistoricalCorrection)
     } AS totalCorrectionCount,
     COUNT {
       MATCH (event)-[:CREATES_CORRECTION]
             ->(correction:JCIEntity:GraphObject:HistoricalCorrection)
             -[:CORRECTS]->(history)
       MATCH (correction)-[:CAUSED_BY]->(change)
     } AS matchingCorrectionCount
WHERE totalCorrectionCount <> 1 OR matchingCorrectionCount <> 1
RETURN change.id AS changeEventId, event.id AS syncEventId,
       history.id AS historyId, totalCorrectionCount, matchingCorrectionCount;
```

A successful `CREATED` run must atomically create the new entity at revision `1`, name it through `AFFECTS`, and create no `PiH` for that new identity:

```cypher
MATCH (change:JCIEntity:GraphObject:ChangeEvent {changeType: 'CREATED'})
WITH change,
     COUNT {
       MATCH (change)-[:TRIGGERS]->(event:JCIEntity:GraphObject:SyncEvent {outcome: 'SUCCESS'})
     } AS successCount,
     COUNT {
       MATCH (change)-[:TRIGGERS]->(event:JCIEntity:GraphObject:SyncEvent {outcome: 'SUCCESS'})
             -[:AFFECTS]->(target:JCIEntity)
       WHERE target.id = change.targetEntityId
         AND target.entityType = change.targetEntityType
         AND target.createdAt >= event.startedAt
         AND target.createdAt <= event.completedAt
      } AS atomicTargetCount,
     COUNT {
       MATCH (change)-[:TRIGGERS]->(event:JCIEntity:GraphObject:SyncEvent {outcome: 'SUCCESS'})
             -[:AFFECTS]->(target:JCIEntity)
       WHERE target.id = change.targetEntityId
         AND target.entityType = change.targetEntityType
         AND EXISTS {
           MATCH (target)-[:CREATED_BY]
                 ->(:JCIEntity:GraphObject:RoleAssignment)
         }
         AND (target.revision = 1 OR EXISTS {
           MATCH (target)-[:HAS_HISTORICAL_STATE]->(initialHistory:JCIEntity:PiH)
           WHERE initialHistory.originalEntityId = target.id
             AND initialHistory.originalEntityType = target.entityType
             AND initialHistory.originalRevision = 1
         })
     } AS attributableInitialRevisionCount,
     COUNT {
       MATCH (change)-[:TRIGGERS]->(event:JCIEntity:GraphObject:SyncEvent {outcome: 'SUCCESS'})
             -[:CREATES_HISTORY]->(history:JCIEntity:PiH)
       WHERE history.originalEntityId = change.targetEntityId
     } AS invalidCreationHistoryCount
WHERE successCount > 1
   OR (successCount = 1 AND
       (atomicTargetCount <> 1 OR attributableInitialRevisionCount <> 1
        OR invalidCreationHistoryCount <> 0))
RETURN change.id AS changeEventId, successCount,
       atomicTargetCount, attributableInitialRevisionCount,
       invalidCreationHistoryCount;
```

Revision `1` is checked in the successful write transaction before commit. A later permitted change may increment the target node's current revision; a downstream stock validation must therefore not incorrectly require that the entity stay at revision `1` forever.

**Short example:** A request to create a Task has `requestedRevision = null`. If acceptance fails before creation, the ChangeEvent and final FAILED SyncEvent remain without `CHANGED_BY` and may have `affectedCount = 0`. On success, the Task at revision `1`, `Task ──CHANGED_BY──► ChangeEvent`, and `SyncEvent ──AFFECTS──► Task` are created, but no PiH exists for this new Task.

**Short example for a historical correction:** A request names `targetEntityId = <PiH-ID>`, `targetEntityType = 'PiH'`, and `requestedRevision = 1`. The ChangeEvent points through `TARGETS_HISTORY` to this PiH, but the PiH receives no `CHANGED_BY`. Only a successful run creates the `HistoricalCorrection`, whose `CORRECTS` points to exactly the same PiH.

### Succession relationships

```cypher
MATCH (e:JCIEntity)
OPTIONAL MATCH (e)-[:REPLACED_BY]->(next:JCIEntity)
WITH e, collect(DISTINCT next) AS successors
WHERE (e.status = 'REPLACED' AND size(successors) <> 1)
   OR (e.status <> 'REPLACED' AND size(successors) <> 0)
   OR any(next IN successors WHERE next.id = e.id OR next.entityType <> e.entityType)
RETURN e.id AS entityId, e.status, [next IN successors | next.id] AS successorIds;
```

```cypher
MATCH (e:JCIEntity)-[:REPLACED_BY*1..]->(e)
RETURN DISTINCT e.id AS replacementCycle;
```

### Future Chain and Achievement

```cypher
MATCH (p:JCIEntity)
WHERE p.entityType IN ['PiF2','PiF1s','PiF1t']
  AND (p.contributionMode IS NULL OR NOT p.contributionMode IN ['ALL','ANY'])
RETURN p.id AS futureId, p.entityType, p.contributionMode;
```

```cypher
MATCH (parent:JCIEntity {status: 'ACHIEVED'})
WHERE parent.entityType IN ['PiF2','PiF1s','PiF1t']
OPTIONAL MATCH (child:JCIEntity)-[:CONTRIBUTES_TO]->(parent)
WHERE NOT child.status IN ['REPLACED','REVOKED']
WITH parent, collect(DISTINCT child) AS children
WHERE size(children) = 0
   OR (parent.contributionMode = 'ALL' AND any(child IN children WHERE child.status <> 'ACHIEVED'))
   OR (parent.contributionMode = 'ANY' AND none(child IN children WHERE child.status = 'ACHIEVED'))
RETURN parent.id AS invalidAchievedFuture, parent.contributionMode,
       [child IN children | {id: child.id, status: child.status}] AS contributions;
```

### Success criteria and verifications

```cypher
MATCH (c:SuccessCriterion)
WHERE NOT c.measurementType IN ['BOOLEAN','NUMERIC','TEXTUAL']
   OR NOT c.requirementLevel IN ['REQUIRED','OPTIONAL']
   OR NOT c.evaluationMode IN ['ALL','ANY']
   OR c.operator IS NULL OR c.targetValue IS NULL
   OR (c.measurementType = 'BOOLEAN' AND NOT c.operator IN ['EQUALS','NOT_EQUALS'])
   OR (c.measurementType = 'NUMERIC' AND NOT c.operator IN
       ['EQUALS','NOT_EQUALS','LESS_THAN','LESS_OR_EQUAL','GREATER_THAN','GREATER_OR_EQUAL'])
   OR (c.measurementType = 'TEXTUAL' AND NOT c.operator IN
       ['EQUALS','NOT_EQUALS','CONTAINS','MATCHES'])
RETURN c.id AS criterionId, c.measurementType, c.operator, c.targetValue;
```

```cypher
MATCH (v:JCIEntity:GraphObject:Verification)
WITH v,
     COUNT {
       MATCH (v)-[:EVALUATES]->(:JCIEntity:GraphObject:Result)
     } AS resultCount,
     COUNT {
       MATCH (v)-[:CHECKS]->(:JCIEntity:GraphObject:SuccessCriterion)
     } AS criterionCount,
     COUNT {
       MATCH (goal:JCIEntity:JCIElementInstance:PiF1o)-[:DECOMPOSES_INTO]
             ->(:JCIEntity:GraphObject:Task)-[:PRODUCES]
             ->(result:JCIEntity:GraphObject:Result)<-[:EVALUATES]-(v)
       MATCH (goal)-[:HAS_SUCCESS_CRITERIA]
             ->(criterion:JCIEntity:GraphObject:SuccessCriterion)<-[:CHECKS]-(v)
     } AS commonGoalCount
WHERE v.status <> 'COMPLETED'
   OR NOT v.outcome IN ['VALID','INVALID','INCONCLUSIVE']
   OR v.verifiedAt IS NULL
   OR v.evaluatedResultRevision IS NULL
   OR valueType(v.evaluatedResultRevision) <> 'INTEGER NOT NULL'
   OR toIntegerOrNull(v.evaluatedResultRevision) < 1
   OR v.checkedCriterionRevision IS NULL
   OR valueType(v.checkedCriterionRevision) <> 'INTEGER NOT NULL'
   OR toIntegerOrNull(v.checkedCriterionRevision) < 1
   OR resultCount <> 1 OR criterionCount <> 1
   OR commonGoalCount <> 1
   OR NOT EXISTS {
        MATCH (v)-[:EVALUATES]->(result:JCIEntity:GraphObject:Result {status: 'COMPLETED'})
      }
   OR NOT EXISTS {
        MATCH (v)-[:CHECKS]->(criterion:JCIEntity:GraphObject:SuccessCriterion {status: 'ACTIVE'})
      }
RETURN v.id AS verificationId, resultCount, criterionCount, commonGoalCount,
       v.evaluatedResultRevision, v.checkedCriterionRevision,
       v.status, v.outcome;
```

The bound revisions must resolve either to the current state or to exactly one historical state of the same entity. The verification timestamp must fall within the validity interval of that revision:

```cypher
MATCH (v:JCIEntity:GraphObject:Verification)-[:EVALUATES]->(result:JCIEntity:GraphObject:Result)
MATCH (v)-[:CHECKS]->(criterion:JCIEntity:GraphObject:SuccessCriterion)
WITH v, result, criterion,
     CASE
       WHEN v.evaluatedResultRevision = result.revision
        AND v.verifiedAt >= result.updatedAt THEN 1 ELSE 0
     END AS currentResultMatch,
     CASE
       WHEN v.checkedCriterionRevision = criterion.revision
        AND v.verifiedAt >= criterion.updatedAt THEN 1 ELSE 0
     END AS currentCriterionMatch,
     COUNT {
       MATCH (result)-[:HAS_HISTORICAL_STATE]->(history:JCIEntity:PiH)
       WHERE history.originalEntityId = result.id
         AND history.originalEntityType = 'Result'
         AND history.originalRevision = v.evaluatedResultRevision
         AND history.validFrom <= v.verifiedAt
         AND v.verifiedAt < history.validUntil
     } AS resultHistoryCount,
     COUNT {
       MATCH (criterion)-[:HAS_HISTORICAL_STATE]->(history:JCIEntity:PiH)
       WHERE history.originalEntityId = criterion.id
         AND history.originalEntityType = 'SuccessCriterion'
         AND history.originalRevision = v.checkedCriterionRevision
         AND history.validFrom <= v.verifiedAt
         AND v.verifiedAt < history.validUntil
     } AS criterionHistoryCount
WHERE currentResultMatch + resultHistoryCount <> 1
   OR currentCriterionMatch + criterionHistoryCount <> 1
RETURN v.id AS verificationId,
       result.id AS resultId, v.evaluatedResultRevision, result.revision AS currentResultRevision,
       criterion.id AS criterionId, v.checkedCriterionRevision,
       criterion.revision AS currentCriterionRevision,
       currentResultMatch, resultHistoryCount,
       currentCriterionMatch, criterionHistoryCount;
```

Before creating a Verification, `SYNC` reads both current revisions and checks them again immediately before commit. A later change to the Result or criterion does not modify the Verification; it merely makes it inapplicable to the current success evaluation. The following **selection query** is therefore not an error query. It returns only currently applicable, non-superseded Verifications:

```cypher
MATCH (v:JCIEntity:GraphObject:Verification)-[:EVALUATES]->(result:JCIEntity:GraphObject:Result)
MATCH (v)-[:CHECKS]->(criterion:JCIEntity:GraphObject:SuccessCriterion)
MATCH (goal:JCIEntity:JCIElementInstance:PiF1o)-[:DECOMPOSES_INTO]
      ->(:JCIEntity:GraphObject:Task)-[:PRODUCES]->(result)
MATCH (goal)-[:HAS_SUCCESS_CRITERIA]->(criterion)
WHERE v.status = 'COMPLETED'
  AND result.status = 'COMPLETED'
  AND criterion.status = 'ACTIVE'
  AND v.evaluatedResultRevision = result.revision
  AND v.checkedCriterionRevision = criterion.revision
  AND NOT EXISTS {
    MATCH (:JCIEntity:GraphObject:Verification)-[:SUPERSEDES]->(v)
  }
RETURN DISTINCT v.id AS applicableVerificationId,
       result.id AS resultId, result.revision AS resultRevision,
       criterion.id AS criterionId, criterion.revision AS criterionRevision,
       goal.id AS pif1oId;
```

The `PiF1o` aggregation may use only this applicable set. If a bound revision is no longer current, a new Verification is required; it may supersede the earlier Verification through `SUPERSEDES` without changing the earlier stored revision binding.

```cypher
MATCH (newer:JCIEntity:GraphObject:Verification)-[:SUPERSEDES]->(older:JCIEntity:GraphObject:Verification)
MATCH (newer)-[:EVALUATES]->(newResult:JCIEntity:GraphObject:Result)
MATCH (older)-[:EVALUATES]->(oldResult:JCIEntity:GraphObject:Result)
MATCH (newer)-[:CHECKS]->(newCriterion:JCIEntity:GraphObject:SuccessCriterion)
MATCH (older)-[:CHECKS]->(oldCriterion:JCIEntity:GraphObject:SuccessCriterion)
WHERE newResult.id <> oldResult.id
   OR newCriterion.id <> oldCriterion.id
   OR newer.verifiedAt <= older.verifiedAt
   OR newer.evaluatedResultRevision < older.evaluatedResultRevision
   OR newer.checkedCriterionRevision < older.checkedCriterionRevision
RETURN newer.id AS newerVerificationId, older.id AS olderVerificationId,
       newResult.id AS newResultId, oldResult.id AS oldResultId,
       newCriterion.id AS newCriterionId, oldCriterion.id AS oldCriterionId,
       newer.evaluatedResultRevision, older.evaluatedResultRevision,
       newer.checkedCriterionRevision, older.checkedCriterionRevision;
```

```cypher
MATCH (verification:JCIEntity:GraphObject:Verification)
WITH verification,
     COUNT {
       MATCH (verification)-[:SUPERSEDES]
             ->(:JCIEntity:GraphObject:Verification)
     } AS predecessorCount,
     COUNT {
       MATCH (:JCIEntity:GraphObject:Verification)-[:SUPERSEDES]
             ->(verification)
     } AS successorCount
WHERE predecessorCount > 1 OR successorCount > 1
RETURN verification.id AS verificationId, predecessorCount, successorCount;
```

```cypher
MATCH (verification:JCIEntity:GraphObject:Verification)
      -[:SUPERSEDES*1..]->(verification)
RETURN DISTINCT verification.id AS verificationCycle;
```

**Short example:** A Verification binds Result revision `3` and criterion revision `2`. If the criterion changes to revision `3`, the old verification remains traceable but no longer counts toward `ACHIEVED`; only a new Verification with `checkedCriterionRevision = 3` can be applied again.

### RoF validity, capacity and organizational relationships

```cypher
MATCH (entity:JCIEntity)
WHERE (entity:RoFOrg AND NOT entity.orgType IN
       ['COMPANY','PUBLIC_ORGANIZATION','NONPROFIT','ASSOCIATION','COOPERATIVE','NETWORK','OTHER'])
   OR (entity:RoFTeam AND NOT entity.teamType IN
       ['FUNCTIONAL','PROJECT','MANAGEMENT','SERVICE','TEMPORARY','OTHER'])
   OR ((entity:RoFOrg AND entity.orgType = 'OTHER'
        OR entity:RoFTeam AND entity.teamType = 'OTHER')
       AND (entity.description IS NULL OR trim(entity.description) = ''))
RETURN entity.id AS entityId, entity.entityType;
```

```cypher
MATCH (team:RoFTeam)-[membership:HAS_MEMBER]->(member:RoFTeamMember)
WHERE membership.validFrom IS NULL
   OR (membership.validUntil IS NOT NULL AND membership.validUntil < membership.validFrom)
RETURN team.id AS teamId, member.id AS memberId;
```

```cypher
MATCH (member:RoFTeamMember)-[ownership:HAS_ROLE]->(role:RoFRole)
WHERE ownership.validFrom IS NULL
   OR (ownership.validUntil IS NOT NULL AND ownership.validUntil < ownership.validFrom)
RETURN member.id AS memberId, role.id AS roleId;
```

```cypher
MATCH (member:RoFTeamMember)-[:HAS_ASSIGNMENT]->(assignment:RoleAssignment)
MATCH (assignment)-[:IN_TEAM]->(team:RoFTeam)
MATCH (assignment)-[:ACTIVATES_ROLE]->(role:RoFRole)
OPTIONAL MATCH (team)-[membership:HAS_MEMBER]->(member)
OPTIONAL MATCH (member)-[ownership:HAS_ROLE]->(role)
WITH member, assignment, team, role,
     collect(DISTINCT membership) AS memberships,
     collect(DISTINCT ownership) AS ownerships
WHERE size(memberships) = 0 OR size(ownerships) = 0
   OR none(m IN memberships WHERE m.validFrom <= assignment.validFrom AND
      ((assignment.validUntil IS NULL AND m.validUntil IS NULL) OR
       (assignment.validUntil IS NOT NULL AND (m.validUntil IS NULL OR m.validUntil >= assignment.validUntil))))
   OR none(o IN ownerships WHERE o.validFrom <= assignment.validFrom AND
      ((assignment.validUntil IS NULL AND o.validUntil IS NULL) OR
       (assignment.validUntil IS NOT NULL AND (o.validUntil IS NULL OR o.validUntil >= assignment.validUntil))))
RETURN assignment.id AS assignmentId, member.id AS memberId, team.id AS teamId, role.id AS roleId;
```

The checking of overlapping `allocation` intervals is carried out by SYNC with interval decomposition; Neo4j has no declarative constraint for this. At any given time, a member's total must not exceed `1`.

```cypher
MATCH (rel:RoFOrgRelationship)-[:SOURCE_ORG]->(source:RoFOrg)
MATCH (rel)-[:TARGET_ORG]->(target:RoFOrg)
WHERE source.id = target.id
   OR (rel.type = 'PARTNERSHIP' AND source.id > target.id)
RETURN rel.id AS relationshipId, rel.type, source.id AS sourceId, target.id AS targetId;
```

```cypher
MATCH (org:RoFOrg)<-[:TARGET_ORG]-(rel:RoFOrgRelationship {type: 'SUBSIDIARY', status: 'ACTIVE'})
WITH org, count(rel) AS parentCount
WHERE parentCount > 1
RETURN org.id AS subsidiaryId, parentCount;
```

```cypher
MATCH (org:RoFOrg)
      ((parent:RoFOrg)<-[:SOURCE_ORG]-(:RoFOrgRelationship {type: 'SUBSIDIARY', status: 'ACTIVE'})
       -[:TARGET_ORG]->(child:RoFOrg)){1,}
      (org)
RETURN DISTINCT org.id AS subsidiaryCycle;
```

### ERoF ownership and personal use

```cypher
MATCH (environment:ERoFObject {status: 'ACTIVE'})
WHERE NOT environment.objectType IN
      ['SYSTEM','APPLICATION','DATA','DOCUMENT','TOOL','FACILITY','CONTRACT','SERVICE','OTHER']
   OR NOT EXISTS { MATCH (:RoleAssignment)-[:USES]->(environment) }
RETURN environment.id AS environmentId, environment.objectType;
```

```cypher
MATCH (task:Task {taskKind: 'ATOMIC'})-[:USES]->(environment:ERoFObject)
WHERE NOT EXISTS {
  MATCH (task)-[:EXECUTED_BY]->(:RoleAssignment)-[:USES]->(environment)
}
RETURN task.id AS taskId, environment.id AS environmentId;
```

### RaN scope and structured conditions

```cypher
MATCH (r:RaN)
OPTIONAL MATCH (r)-[:APPLIES_IN]->(scope:JCIEntity)
WITH r, collect(DISTINCT scope) AS scopes
WHERE NOT r.effect IN ['REQUIRE','PROHIBIT','PERMIT']
   OR NOT r.scopeType IN ['GLOBAL','ORGANIZATION','TEAM','ENTITY']
   OR r.decisionKey IS NULL OR trim(r.decisionKey) = ''
   OR r.conditionJson IS NULL OR size(r.governedTypes) = 0
   OR (r.scopeType IN ['GLOBAL','ENTITY'] AND size(scopes) <> 0)
   OR (r.scopeType = 'ORGANIZATION' AND
       (size(scopes) <> 1 OR NOT 'RoFOrg' IN labels(scopes[0])))
   OR (r.scopeType = 'TEAM' AND
       (size(scopes) <> 1 OR NOT 'RoFTeam' IN labels(scopes[0])))
RETURN r.id AS ruleId, r.effect, r.scopeType, [scope IN scopes | scope.id] AS scopeIds;
```

An active RaN protects at least one CiV and one PiF2 and governs at least one concrete implementation element. The following queries validate target types, minimum cardinalities, and CiV-PiF2 coherence. The versioned SYNC rules package validates organizational scope compatibility across time-dependent memberships and WHY paths.

```cypher
MATCH (rule:RaN)-[:PROTECTS]->(target)
WHERE NOT (target:CiV OR target:PiF2)
RETURN rule.id AS ruleId, target.id AS invalidProtectedTargetId, labels(target) AS targetLabels;
```

```cypher
MATCH (rule:RaN)-[:GOVERNS]->(target:JCIEntity)
WHERE none(label IN labels(target) WHERE label IN [
  'PiF1s','PiF1t','PiF1o','Task','SuccessCriterion','Result','Verification','Evidence',
  'RoFOrg','RoFOrgRelationship','RoFTeam','RoFTeamMember','RoFRole','RoleAssignment','ERoFObject'
])
RETURN rule.id AS ruleId, target.id AS invalidGovernedTargetId, labels(target) AS targetLabels;
```

```cypher
MATCH (rule:RaN {status: 'ACTIVE'})
OPTIONAL MATCH (rule)-[:PROTECTS]->(protected:JCIEntity)
OPTIONAL MATCH (rule)-[:GOVERNS]->(governed:JCIEntity)
WITH rule, collect(DISTINCT protected) AS protected, collect(DISTINCT governed) AS governed
WHERE size([target IN protected WHERE 'CiV' IN labels(target)]) < 1
   OR size([target IN protected WHERE 'PiF2' IN labels(target)]) < 1
   OR size(governed) < 1
RETURN rule.id AS ruleId,
       [target IN protected | target.id] AS protectedTargetIds,
       [target IN governed | target.id] AS governedTargetIds;
```

```cypher
MATCH (rule:RaN {status: 'ACTIVE'})-[:PROTECTS]->(target:JCIEntity)
WHERE (target:CiV AND NOT EXISTS {
  MATCH (target)-[:INSCRIBES_PURPOSE_IN]->(future:PiF2)
  WHERE EXISTS { MATCH (rule)-[:PROTECTS]->(future) }
})
OR (target:PiF2 AND NOT EXISTS {
  MATCH (value:CiV)-[:INSCRIBES_PURPOSE_IN]->(target)
  WHERE EXISTS { MATCH (rule)-[:PROTECTS]->(value) }
})
RETURN rule.id AS ruleId, target.id AS incoherentProtectedTargetId, labels(target) AS targetLabels;
```

### PiH, corrections and SyncEvent

```cypher
MATCH (history:JCIEntity:PiH)
WITH history,
     COUNT {
       MATCH (:JCIEntity)-[:HAS_HISTORICAL_STATE]->(history)
     } AS originCount,
     COUNT {
       MATCH (:JCIEntity:GraphObject:SyncEvent)-[:CREATES_HISTORY]->(history)
     } AS eventCount
WHERE originCount <> 1 OR eventCount <> 1
   OR history.originalEntityId IS NULL
   OR history.originalEntityType IS NULL
   OR history.originalRevision IS NULL OR history.originalRevision < 1
   OR history.recordedAt IS NULL
   OR history.validFrom IS NULL OR history.validUntil IS NULL
   OR history.validUntil <= history.validFrom
   OR history.snapshotSchemaVersion IS NULL
   OR history.stateDataJson IS NULL OR history.relationshipDataJson IS NULL
   OR history.contentHash IS NULL
   OR NOT (history.contentHash =~ '^[0-9a-f]{64}$')
RETURN history.id AS historyId, history.originalEntityId,
       history.originalEntityType, history.originalRevision,
       originCount, eventCount;
```

```cypher
MATCH (correction:HistoricalCorrection)
OPTIONAL MATCH (correction)-[:CORRECTS]->(history:PiH)
OPTIONAL MATCH (event:SyncEvent)-[:CREATES_CORRECTION]->(correction)
OPTIONAL MATCH (correction)-[:CAUSED_BY]->(change:ChangeEvent)
OPTIONAL MATCH (correction)-[:CORRECTED_BY]->(actor:RoleAssignment)
WITH correction, count(DISTINCT history) AS historyCount,
     count(DISTINCT event) AS eventCount, count(DISTINCT change) AS changeCount,
     count(DISTINCT actor) AS actorCount
WHERE historyCount <> 1 OR eventCount <> 1 OR changeCount <> 1 OR actorCount <> 1
   OR correction.valueSchemaVersion IS NULL
   OR correction.previousValueJson IS NULL OR correction.correctedValueJson IS NULL
   OR correction.baseHistoryViewHash IS NULL
   OR NOT (correction.baseHistoryViewHash =~ '^[0-9a-f]{64}$')
   OR correction.correctedFields IS NULL OR size(correction.correctedFields) = 0
   OR size(correction.correctedFields) <>
      size(reduce(uniqueFields = [], field IN correction.correctedFields |
        CASE WHEN field IN uniqueFields THEN uniqueFields ELSE uniqueFields + field END))
   OR any(index IN range(0, size(correction.correctedFields) - 2)
          WHERE correction.correctedFields[index] >= correction.correctedFields[index + 1])
   OR any(field IN correction.correctedFields
          WHERE field IS NULL OR trim(field) = '' OR NOT (field STARTS WITH '/'))
   OR NOT EXISTS {
        MATCH (correction)-[:CAUSED_BY]->(sameChange:JCIEntity:GraphObject:ChangeEvent)
              -[:TARGETS_HISTORY]->(sameHistory:JCIEntity:PiH)
        MATCH (correction)-[:CORRECTS]->(sameHistory)
        MATCH (sameChange)-[:TRIGGERS]->(sameEvent:JCIEntity:GraphObject:SyncEvent)
              -[:CREATES_CORRECTION]->(correction)
        MATCH (sameEvent)-[:AFFECTS]->(sameHistory)
      }
RETURN correction.id AS correctionId, historyCount, eventCount, changeCount, actorCount,
       correction.baseHistoryViewHash, correction.correctedFields;
```

A `HistoricalCorrection` may fully supersede at most one older correction of the same `PiH` and may itself be superseded by at most one newer correction. Branches, target changes, and cycles are invalid:

```cypher
MATCH (correction:JCIEntity:GraphObject:HistoricalCorrection)
OPTIONAL MATCH (correction)-[:SUPERSEDES]->(older:JCIEntity:GraphObject:HistoricalCorrection)
OPTIONAL MATCH (newer:JCIEntity:GraphObject:HistoricalCorrection)-[:SUPERSEDES]->(correction)
WITH correction, collect(DISTINCT older) AS olderCorrections,
     collect(DISTINCT newer) AS newerCorrections
WHERE size(olderCorrections) > 1 OR size(newerCorrections) > 1
   OR any(older IN olderCorrections WHERE NOT EXISTS {
        MATCH (correction)-[:CORRECTS]->(history:JCIEntity:PiH)
        MATCH (older)-[:CORRECTS]->(history)
      })
   OR any(older IN olderCorrections
          WHERE any(field IN older.correctedFields
                    WHERE NOT field IN correction.correctedFields))
   OR any(older IN olderCorrections
          WHERE correction.correctedAt <= older.correctedAt)
RETURN correction.id AS correctionId,
       [older IN olderCorrections | older.id] AS supersededIds,
       [newer IN newerCorrections | newer.id] AS supersedingIds;
```

```cypher
MATCH (correction:JCIEntity:GraphObject:HistoricalCorrection)
      -[:SUPERSEDES*1..]->(correction)
RETURN DISTINCT correction.id AS correctionCycle;
```

Multiple non-superseded corrections for the same `PiH` may apply in parallel when their `correctedFields` are disjoint. If two current corrections touch the same path, one must fully supersede the other through `SUPERSEDES` and contain at least the predecessor's complete field set; otherwise the effective historical state would be ambiguous.

```cypher
MATCH (left:JCIEntity:GraphObject:HistoricalCorrection)-[:CORRECTS]->(history:JCIEntity:PiH)
MATCH (right:JCIEntity:GraphObject:HistoricalCorrection)-[:CORRECTS]->(history)
WHERE left.id < right.id
  AND NOT EXISTS {
    MATCH (:JCIEntity:GraphObject:HistoricalCorrection)-[:SUPERSEDES]->(left)
  }
  AND NOT EXISTS {
    MATCH (:JCIEntity:GraphObject:HistoricalCorrection)-[:SUPERSEDES]->(right)
  }
  AND any(field IN left.correctedFields WHERE field IN right.correctedFields)
RETURN history.id AS historyId, left.id AS leftCorrectionId,
       right.id AS rightCorrectionId,
       [field IN left.correctedFields WHERE field IN right.correctedFields] AS overlappingFields;
```

Before every new correction, `SYNC` rereads the `PiH` and every non-superseded correction. The canonical hash input contains the `historyId`, `PiH.contentHash`, and the IDs, field lists, and values of all current corrections sorted by correction ID. The view hash therefore changes after every successful addition or supersession, even if the resulting domain value later equals an earlier value. The request must name exactly this SHA-256 as `baseHistoryViewHash`.

The following **selection query** returns the source set to serialize canonically; SHA-256 calculation and overlay of the JSON values take place in the SYNC rules package:

```cypher
MATCH (history:JCIEntity:PiH)
OPTIONAL MATCH (correction:JCIEntity:GraphObject:HistoricalCorrection)-[:CORRECTS]->(history)
WHERE correction IS NULL OR NOT EXISTS {
  MATCH (:JCIEntity:GraphObject:HistoricalCorrection)-[:SUPERSEDES]->(correction)
}
WITH history, correction
ORDER BY correction.id
WITH history, collect(correction{
       .id, .correctionType, .correctedFields,
       .previousValueJson, .correctedValueJson
     }) AS activeCorrections
RETURN history.id AS historyId, history.contentHash AS pihContentHash,
       activeCorrections;
```

Immediately before commit, `SYNC` recalculates the hash and compares it with `baseHistoryViewHash`. The SYNC write layer serializes correction transactions by target `PiH.id`: only the first write attempt from the same base view may commit; each later attempt rereads the now changed historical state and produces `CONFLICT` if its request is unchanged. `baseHistoryViewHash` is deliberately not graph-wide unique because different `PiH` nodes may have the same effective view. Serialization and the pre-commit check cannot be replaced by a later pure Cypher query because Neo4j deliberately stores the canonical JSON values only as strings.

**Short example:** One current correction adds `/relationshipData/HAS_MEMBER:OUT:team-7/validUntil`. A second current correction may simultaneously change `/stateData/name`. If it also wants to change the same `validUntil` path, it must supersede the first correction through `SUPERSEDES` and use the `baseHistoryViewHash` recalculated immediately beforehand.

```cypher
MATCH (event:JCIEntity:GraphObject:SyncEvent)
WITH event,
     COUNT {
       MATCH (:JCIEntity:GraphObject:ChangeEvent)-[:TRIGGERS]->(event)
     } AS triggerCount,
     COUNT {
       MATCH (event)-[:EXECUTES]->(:JCIEntity:JCIElementInstance:SYNC)
     } AS definitionCount,
     COUNT {
       MATCH (event)-[:AFFECTS]->(:JCIEntity)
     } AS actualAffectedCount,
     COUNT {
       MATCH (event)-[:CREATES_HISTORY]->(:JCIEntity:PiH)
     } AS actualHistoryCount,
     COUNT {
       MATCH (event)-[:CREATES_CORRECTION]
             ->(:JCIEntity:GraphObject:HistoricalCorrection)
     } AS actualCorrectionCount,
     COUNT {
       MATCH (:JCIEntity:GraphObject:RaNConflict)-[:DETECTED_BY]->(event)
     } AS actualConflictCount
WHERE triggerCount <> 1 OR definitionCount <> 1
   OR event.runId IS NULL
   OR valueType(event.runId) <> 'STRING NOT NULL'
   OR NOT (toLower(toString(event.runId)) =~
      '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$')
   OR event.startedAt IS NULL OR event.completedAt IS NULL
   OR event.completedAt < event.startedAt
   OR event.outcome IS NULL
   OR NOT event.outcome IN ['SUCCESS','CONFLICT','FAILED']
   OR (event.outcome IN ['SUCCESS','CONFLICT'] AND actualAffectedCount < 1)
   OR event.affectedCount IS NULL OR event.affectedCount < 0
   OR event.changedCount IS NULL OR event.changedCount < 0
   OR event.historyCount IS NULL OR event.historyCount < 0
   OR event.correctionCount IS NULL OR event.correctionCount < 0
   OR event.conflictCount IS NULL OR event.conflictCount < 0
   OR event.affectedCount <> actualAffectedCount
   OR event.historyCount <> actualHistoryCount
   OR event.correctionCount <> actualCorrectionCount
   OR event.conflictCount <> actualConflictCount
RETURN event.id AS syncEventId, triggerCount, definitionCount,
       event.affectedCount, actualAffectedCount,
       event.changedCount,
       event.historyCount, actualHistoryCount,
       event.correctionCount, actualCorrectionCount,
       event.conflictCount, actualConflictCount;
```

`AFFECTS` therefore depends on the outcome: a run with `SUCCESS` or `CONFLICT` names at least one affected `JCIEntity`. Only a `FAILED` run that ends early before target resolution may document zero targets and `affectedCount = 0`. Once a target has actually been resolved, it must be stored through `AFFECTS` and counted even for a failed run.

**Short example:** Two technical retries of the same request have the same triggering `ChangeEvent`, but different `runId` values and two separate `SyncEvent` nodes. At most one successful attempt may commit the domain change; both events remain traceable append-only.

`affectedCount`, `historyCount`, `correctionCount`, and `conflictCount` are fully verifiable from the stored relationships. In contrast, `changedCount` denotes the number of domain target changes actually adopted in the same transaction. Because the model deliberately stores no additional `CHANGES` relationship for this purpose, `SYNC` calculates this value from the deduplicated transaction write set immediately before commit. Each existing mutable `JCIEntity` in that set must receive exactly one revision increment and exactly one corresponding `PiH`. A domain target entity newly created by the change request counts as an adopted change but does not yet receive a `PiH`. Newly generated process and documentation objects such as `PiH`, `SyncEvent`, `HistoricalCorrection`, or a `RaNConflict` documented by `SYNC` do not count toward `changedCount`. With `CONFLICT` or `FAILED`, rolled-back write operations do not count either. The calculated value is adopted atomically together with the graph state and the final `SyncEvent`.

## Transaction rule for SYNC

`SYNC` checks hierarchy, dependencies, Task type rules, and applicable `RaN` before adoption. Derived Task statuses are aggregated from the atomic tasks up the parent chain and only then to the affected `PiF1o`. Current states, required `PiH`, new or resolved `RaNConflict` objects, relationships, the deduplicated transaction write set, and the final `SyncEvent` are adopted atomically. Before commit, all five count values are calculated from this write set and the relationships to be stored. A conflict or error must not leave a partially updated graph.

The following additional rules apply to the clarified processes: A `CREATED` target is created atomically with revision `1`, its `CHANGED_BY` edge, and the final successful event. Before a Verification is stored, both bound revisions are compared again with the current target revisions. Before a HistoricalCorrection is stored, the target PiH, the current correction set, and `baseHistoryViewHash` are checked again within the same transaction; only then are `HistoricalCorrection`, `CORRECTS`, `CAUSED_BY`, and `CREATES_CORRECTION` created together. `SyncEvent` nodes are never updated or reused for another run; exactly one new node is appended for each `runId`.

## Limits of declarative enforcement

Neo4j constraints and subsequent Cypher queries cover the stored graph state, but they cannot guarantee four runtime properties on their own:

1. A `SyncRun` completed outside the graph can only be recognized as a missing `SyncEvent` after reconciliation with the technical run/outbox log.
2. Preventing later changes to or deletion of immutable nodes and their relationships requires restricted write roles or exclusively approved SYNC write transactions; a property constraint is not an append-only mechanism.
3. The canonical overlay of `stateDataJson`, `relationshipDataJson`, and correction values, as well as SHA-256 calculation, takes place in the versioned SYNC rules package. Cypher validates structure, uniqueness, and the stored hash format, but not the JSON semantics themselves.
4. Revision `1` of a newly created target and the Verification and history revisions rechecked immediately before commit are transaction preconditions. A later snapshot of the graph after further development can reconstruct this temporal fact only from the fully stored history.

## Migration and versioning

Schema changes are stored as forward, immutable migrations with increasing numbers. Each migration includes:

1. expected initial version,
2. Pre-validations,
3. Constraints, indices and necessary data adjustments,
4. post-validations,
5. new target version.

A restoreable database backup is created before a migration. A migration is only completed if all post-validations return zero errors. The active `SYNC.definition` names the appropriate ontology, graph rule and schema target version; an incompatible combination may not be activated.

The following migration-compatible order applies to the fields clarified in this document:

1. First write new properties without existence or unique constraints and classify all legacy data.
2. Derive `ChangeEvent.targetEntityId`, `targetEntityType`, and `requestedRevision` from the unique `CHANGED_BY` source or, for historical corrections, from `CORRECTS` and `CAUSED_BY`. An old failed request without a target edge may be supplemented only from an unchanged request record.
3. Take `SyncEvent.runId` exclusively from the technical run/outbox log. A newly generated random ID would falsify the historical run identity and is therefore not a valid backfill.
4. Determine the revision bindings of existing Verifications from `verifiedAt`, the current revision, and unambiguous `PiH` validity intervals. Zero or multiple candidates stop the migration.
5. Mark a root assignment with `bootstrapKey = 'ROOT'` only if it and its initial SYNC definition are unambiguously proven. An ambiguous, non-empty legacy data set is not automatically reinterpreted as the closed bootstrap.
6. For existing HistoricalCorrections, calculate the original `baseHistoryViewHash` only when the correction sequence can be reconstructed completely. Overlapping, non-superseded field corrections require prior domain resolution.
7. Record every existing `GOVERNS` edge to a `PiF2` as an unconfirmed migration candidate; it must not be renamed blindly.
8. An authorized `RoleAssignment` confirms the PiF2 as a `PROTECTS` target, selects at least one CiV grounding that PiF2 through `INSCRIBES_PURPOSE_IN`, and confirms it as a `PROTECTS` target as well. `SYNC` must not infer this selection.
9. Connect the implementation elements actually governed through `GOVERNS`. Remove the former `GOVERNS` edge to PiF2 only after successful coherence, scope, and type validation.
10. Do not activate an existing RaN under the new rules version without fully confirmed protection and implementation targets; stop migration for domain clarification.
11. Create all existence, type, and uniqueness constraints only after a successful backfill, and then execute all validation queries again.

For a completely empty database, the backfills are omitted. In that case, the constraints are created first and the atomic bootstrap transaction is then executed exactly once. This documentation change does not itself run a migration or bootstrap against a live database.

**Short example:** A RaN migration finds `RaN A ── GOVERNS ──► PiF2 X`. It prepares `PROTECTS` to PiF2 X only as a candidate. Only after an authorized human confirms grounding CiV Y and the implementation elements actually governed does `SYNC` atomically commit both `PROTECTS` edges, the new `GOVERNS` edges, and removal of the former PiF2 governance edge.

## Demarcation of client separation

`RoFOrg` is a business organization in the JCI graph and not a technical client key. Multiple organizations may deliberately be connected in a common model graph. Technical database, access or deployment isolation is implemented outside the JCI ontology and must not change the technical organizational relationships.

## Automated testing

The technology-independent invariants are additionally checked by [`tests/test_model_rules.py`](../../../../tests/test_model_rules.py). [`tests/test_spec_consistency.py`](../../../../tests/test_spec_consistency.py) ensures that entity and relationship catalogs, structured data types and subsequent documents remain in sync. GitHub Actions runs both tests on every push to `main` and on every pull request.

The Cypher queries in this document remain additionally mandatory for a real Neo4j instance. Every validation query must return zero rows after migration and business transaction.
