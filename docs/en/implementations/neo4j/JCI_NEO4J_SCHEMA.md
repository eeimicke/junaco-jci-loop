# JCI-Neo4j scheme

## Status and purpose

This document concretizes the technical mapping of the JCI model in Neo4j. It implements [JCI_CONTEXT.md](../../JCI_CONTEXT.md), [JCI_ONTOLOGY.md](../../JCI_ONTOLOGY.md), [JCI_GRAPH_RULES.md](../../JCI_GRAPH_RULES.md) and [JCI_SYNC_SPEC.md](../../JCI_SYNC_SPEC.md). In the event of a conflict, the technical specification applies; the schema must not change their semantics.

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
```

The globally unique `JCIEntity.id` makes additional ID constraints for each specific label technically redundant. Specific constraints are only created for other technically unique keys.

### Complex structured values

Neo4j properties do not store nested JSON objects. The canonical structures from `JCI_CONTEXT.md` are therefore projected as canonical JSON character strings without loss of semantics:

| Technical field | Neo4j Property |
| --------------- | -------------- |
| `RaN.condition` | `conditionJson` |
| `SYNC.definition` | `definitionJson` |
| `Result.value` | `valueJson` |
| `PiH.stateData` | `stateDataJson` |
| `PiH.relationshipData` | `relationshipDataJson` |
| `HistoricalCorrection.previousValue` | `previousValueJson` |
| `HistoricalCorrection.correctedValue` | `correctedValueJson` |

The JSON strings use UTF-8, lexicographically sorted object keys, and the canonical data type rules from Section 2.2.7. `PiH.contentHash` is calculated from the technical structures before this Neo4j projection.

## Labels and properties for tasks

Each Task carries at least the labels `JCIEntity`, `GraphObject` and `Task`. In addition to the common mandatory fields, it is mandatory to have:

```text
taskKind = ATOMIC | COMPOSITE
status   = DRAFT | ACTIVE | BLOCKED | COMPLETED | REPLACED | REVOKED
```

`PiF1o` is a desired state. `Task` is an activity. “Develop customer portal” is therefore modeled as `COMPOSITE`-Task; For example, the associated `PiF1o` reads “The customer portal can be used productively”.

## Relationship types for tasks

| Source | Relationship | Target | Meaning |
| ------- | ------------------ | ---------------- | ---------------------------------------------- |
| `PiF1o` | `DECOMPOSES_INTO` | `Task` | direct operational target context of each task |
| `Task` | `DECOMPOSES_INTO` | `Task` | direct parent/subtask structure |
| `Task` | `DEPENDS_ON` | `Task` | technical execution requirements |
| `Task` | `RESPONSIBLE_TEAM` | `RoFTeam` | exactly one responsible team |
| `Task` | `EXECUTED_BY` | `RoleAssignment` | Execution of exclusively atomic tasks |
| `Task` | `USES` | `ERoFObject` | Environmental use of exclusively atomic tasks |
| `Task` | `PRODUCES` | `Result` | Result of exclusively atomic tasks |

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
```

Neo4j constraints do not fully enforce enum values, cardinalities, and graph-wide cycle rules. These rules are checked by `SYNC` before writing and by validation queries after writing.

## Validation queries

Each subsequent query must return zero rows for a valid graph.

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
MATCH (v:Verification)
OPTIONAL MATCH (v)-[:EVALUATES]->(result:Result)
OPTIONAL MATCH (v)-[:CHECKS]->(criterion:SuccessCriterion)
WITH v, count(DISTINCT result) AS resultCount, count(DISTINCT criterion) AS criterionCount
WHERE v.status <> 'COMPLETED'
   OR NOT v.outcome IN ['VALID','INVALID','INCONCLUSIVE']
   OR resultCount <> 1 OR criterionCount <> 1
RETURN v.id AS verificationId, resultCount, criterionCount, v.status, v.outcome;
```

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

### PiH, corrections and SyncEvent

```cypher
MATCH (history:PiH)
OPTIONAL MATCH (origin:JCIEntity)-[:HAS_HISTORICAL_STATE]->(history)
OPTIONAL MATCH (event:SyncEvent)-[:CREATES_HISTORY]->(history)
WITH history, count(DISTINCT origin) AS originCount, count(DISTINCT event) AS eventCount
WHERE originCount <> 1 OR eventCount <> 1
   OR history.snapshotSchemaVersion IS NULL
   OR history.stateDataJson IS NULL OR history.relationshipDataJson IS NULL
   OR history.contentHash IS NULL OR history.originalRevision < 1
RETURN history.id AS historyId, originCount, eventCount;
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
RETURN correction.id AS correctionId, historyCount, eventCount, changeCount, actorCount;
```

```cypher
MATCH (event:SyncEvent)
OPTIONAL MATCH (change:ChangeEvent)-[:TRIGGERS]->(event)
OPTIONAL MATCH (event)-[:EXECUTES]->(definition:SYNC)
OPTIONAL MATCH (event)-[:AFFECTS]->(affected:JCIEntity)
WITH event, count(DISTINCT change) AS changeCount,
     count(DISTINCT definition) AS definitionCount,
     count(DISTINCT affected) AS actualAffectedCount
WHERE changeCount <> 1 OR definitionCount <> 1 OR actualAffectedCount < 1
   OR event.completedAt < event.startedAt
   OR NOT event.outcome IN ['SUCCESS','CONFLICT','FAILED']
   OR event.affectedCount <> actualAffectedCount
RETURN event.id AS syncEventId, changeCount, definitionCount,
       event.affectedCount, actualAffectedCount;
```

## Transaction rule for SYNC

`SYNC` checks hierarchy, dependencies, Task type rules, and applicable `RaN` before adoption. Derived Task statuses are aggregated from the atomic tasks up the parent chain and only then to the affected `PiF1o`. Current states, required `PiH`, new or resolved `RaNConflict` objects, relationships and the final `SyncEvent` are inherited atomically. A conflict or error must not leave a partially updated graph.

## Migration and versioning

Schema changes are stored as forward, immutable migrations with increasing numbers. Each migration includes:

1. expected initial version,
2. Pre-validations,
3. Constraints, indices and necessary data adjustments,
4. post-validations,
5. new target version.

A restoreable database backup is created before a migration. A migration is only completed if all post-validations return zero errors. The active `SYNC.definition` names the appropriate ontology, graph rule and schema target version; an incompatible combination may not be activated.

**Short example:** Migration `V002` complements `REPLACED_BY`. It first checks all existing `REPLACED` entities, creates the required successor edges within a controlled data migration and only activates the new constraint when no replaced entity remains without a successor.

## Demarcation of client separation

`RoFOrg` is a business organization in the JCI graph and not a technical client key. Multiple organizations may deliberately be connected in a common model graph. Technical database, access or deployment isolation is implemented outside the JCI ontology and must not change the technical organizational relationships.

## Automated testing

The technology-independent invariants are additionally checked by `tests/test_model_rules.py`. `tests/test_spec_consistency.py` ensures that entity and relationship catalogs, structured data types and subsequent documents remain in sync. GitHub Actions runs both tests on every push to `main` and on every pull request.

The Cypher queries in this document remain additionally mandatory for a real Neo4j instance. Every validation query must return zero rows after migration and business transaction.
