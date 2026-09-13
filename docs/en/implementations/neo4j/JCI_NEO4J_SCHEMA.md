# JCI-Neo4j scheme

## Status and purpose

This document specifies the technical mapping of the JCI model to Neo4j. It implements [`JCI_CONTEXT.md`](../../JCI_CONTEXT.md), [`JCI_ONTOLOGY.md`](../../JCI_ONTOLOGY.md), [`JCI_GRAPH_RULES.md`](../../JCI_GRAPH_RULES.md), and [`JCI_SYNC_SPEC.md`](../../JCI_SYNC_SPEC.md). In the event of a conflict, the domain specification applies; this schema must not change its semantics.

## Versioned rule and snapshot profile 2.0

New SYNC operations use rule package, ontology, graph rules, SYNC specification, snapshotSchemaVersion, valueSchemaVersion, and exchange schemaVersion 2.0. Approval-required operations additionally require the explicit handler capability `approvalProfileVersion = "1.0"`; a handler without that capability rejects them. JSON-LD remains 1.1; existing /1.0# namespace IRIs are identities, not rule versions. Old profiles are explicitly read through their resolvers. Existing PiH, HistoricalCorrections, SyncEvents, approvals, and hashes are not retroactively rewritten or recalculated.

Revision belongs to domain state under the endpoint ownership matrix in section 2.2.8 of [`JCI_CONTEXT.md`](../../JCI_CONTEXT.md). New verification, event, and correction references do not revision their targets. `TRIGGERS`, `CHANGED_BY`, `HAS_HISTORICAL_STATE`, `APPROVED_BY`, and new `CREATED_BY` references create no history recursion. `APPROVED_BY` belongs exclusively to the immutable `ChangeEvent` created at acceptance; it does not revision the referenced `RoleAssignment`. Permitted addition of `CREATED_BY` to an imported draft changes that draft; RaNConflict resolution changes only the conflict. `PROVIDES_CONTEXT_TO` belongs to the CiV context. Other cataloged structure relationships change both mutable owners. New PiH project only their assigned revisioned relationship state. Revision-neutral references nevertheless remain fully subject to gate/graphEpoch and their own immutable provenance rules.

## Common label and property strategy

Each domain node carries `JCIEntity` and exactly one of the abstract labels `JCIElementInstance` or `GraphObject`. In addition, it carries exactly a specific type label that matches `entityType`.

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
| `RaN.approvalPolicy`                  | `approvalPolicyJson`   |
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

An accepted approval-required change additionally uses:

```text
(:ChangeEvent)-[:APPROVED_BY {
  receiptId, decidedAt, requestHash, approvalHash
}]->(:RoleAssignment)
```

`APPROVED_BY` is not created by a generic `CONNECT` operation. The gate derives these edges only from completely verified `JCIApprovalEnvelope` receipts and creates them together with the new `ChangeEvent`. Exactly one edge per `ChangeEvent` and `RoleAssignment` is permitted. A normal request that does not require approval has `0..n`; an accepted approval-required request has `1..n` such edges. They must never be appended, changed, or removed after acceptance.

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

CREATE CONSTRAINT approved_by_receipt_id_exists IF NOT EXISTS
FOR ()-[approval:APPROVED_BY]-() REQUIRE approval.receiptId IS NOT NULL;

CREATE CONSTRAINT approved_by_receipt_id_unique IF NOT EXISTS
FOR ()-[approval:APPROVED_BY]-() REQUIRE approval.receiptId IS UNIQUE;

CREATE CONSTRAINT approved_by_receipt_id_type IF NOT EXISTS
FOR ()-[approval:APPROVED_BY]-() REQUIRE approval.receiptId IS :: STRING;

CREATE CONSTRAINT approved_by_decided_at_exists IF NOT EXISTS
FOR ()-[approval:APPROVED_BY]-() REQUIRE approval.decidedAt IS NOT NULL;

CREATE CONSTRAINT approved_by_decided_at_type IF NOT EXISTS
FOR ()-[approval:APPROVED_BY]-() REQUIRE approval.decidedAt IS :: ZONED DATETIME;

CREATE CONSTRAINT approved_by_request_hash_exists IF NOT EXISTS
FOR ()-[approval:APPROVED_BY]-() REQUIRE approval.requestHash IS NOT NULL;

CREATE CONSTRAINT approved_by_request_hash_type IF NOT EXISTS
FOR ()-[approval:APPROVED_BY]-() REQUIRE approval.requestHash IS :: STRING;

CREATE CONSTRAINT approved_by_approval_hash_exists IF NOT EXISTS
FOR ()-[approval:APPROVED_BY]-() REQUIRE approval.approvalHash IS NOT NULL;

CREATE CONSTRAINT approved_by_approval_hash_type IF NOT EXISTS
FOR ()-[approval:APPROVED_BY]-() REQUIRE approval.approvalHash IS :: STRING;

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

## Technical write gate

The following technical labels are not JCIEntity, GraphObject, or additional domain types and are not exported as JCI ontology. Exactly one gate protects the entire shared JCI database store, including every RoFOrg and domain-revision-neutral audit-append transaction. Technical request/run records contain the complete immutable request, run ownership/fencing, executed SYNC revision/checksum, and decision outcome. `JCITechnicalRequest.proposalJson` retains the exact base request 2.0. For an approval, `approvalEnvelopeJson` retains the closed 1.0 envelope with every receipt, including rejections; both strings are canonical UTF-8 JSON and are never treated as `JCIEntity`. Success records exist at most once per request; outbox entries refer to exactly one completion event.

```cypher
CREATE CONSTRAINT jci_technical_gate_key_unique IF NOT EXISTS
FOR (gate:JCITechnicalGate) REQUIRE gate.key IS UNIQUE;
CREATE CONSTRAINT jci_technical_request_key_unique IF NOT EXISTS
FOR (request:JCITechnicalRequest) REQUIRE request.idempotencyKey IS UNIQUE;
CREATE CONSTRAINT jci_technical_request_proposal_exists IF NOT EXISTS
FOR (request:JCITechnicalRequest) REQUIRE request.proposalJson IS NOT NULL;
CREATE CONSTRAINT jci_technical_request_proposal_type IF NOT EXISTS
FOR (request:JCITechnicalRequest) REQUIRE request.proposalJson IS :: STRING;
CREATE CONSTRAINT jci_technical_run_id_unique IF NOT EXISTS
FOR (run:JCITechnicalRun) REQUIRE run.runId IS UNIQUE;
CREATE CONSTRAINT jci_technical_commit_request_unique IF NOT EXISTS
FOR (commit:JCITechnicalCommit) REQUIRE commit.idempotencyKey IS UNIQUE;
CREATE CONSTRAINT jci_technical_commit_run_unique IF NOT EXISTS
FOR (commit:JCITechnicalCommit) REQUIRE commit.runId IS UNIQUE;
CREATE CONSTRAINT jci_technical_outbox_event_unique IF NOT EXISTS
FOR (entry:JCITechnicalOutbox) REQUIRE entry.eventId IS UNIQUE;
```

An incomplete, rejected, or abandoned approval proposal remains exclusively in this technical ledger. It creates neither a waiting `ChangeEvent` nor a waiting Task status. Only when valid `APPROVED` receipts cover every currently derived requirement are the `ChangeEvent`, `REQUESTED_BY`, all `APPROVED_BY` edges, and scheduling of the first run accepted atomically. `REJECTED`, `DENY`, `UNEVALUABLE`, an expired receipt, or an incomplete route must neither be escalated nor reinterpreted as a missing approval.

```cypher
MERGE (gate:JCITechnicalGate {key: 'MODEL_WRITE'})
ON CREATE SET gate.graphEpoch = 0;
```

Gate initialization is a controlled technical installation step before domain bootstrap; it creates no JCIEntity. Each regular writer expects the existing gate and fails if it is absent. It acquires the lock in an explicit transaction before authoritative reads. Commit/rollback releases the lock; merely touching the technical lock changes neither domain revisions nor graphEpoch.

```cypher
MATCH (gate:JCITechnicalGate {key: 'MODEL_WRITE'})
SET gate._lock = true
REMOVE gate._lock
RETURN gate.graphEpoch AS graphEpoch;
```

Every actually committed JCI write transaction increases graphEpoch exactly once, including acceptance, corrections, SUPERSEDES, and FAILED/CONFLICT completion documentation. Heartbeats may run separately but must not change run ownership or commit outcomes. Ownership changes and finalization use the same protected ordering. Direct JCI write paths bypassing the gate are prohibited.

Neo4j defaults to Read Committed. Its documented SET/REMOVE write lock lasts until commit or rollback ([Neo4j locking](https://neo4j.com/docs/operations-manual/current/database-internals/concurrent-data-access/)). The reference uses an explicit [driver transaction](https://neo4j.com/docs/python-manual/current/transactions/).

## Atomic bootstrap of an empty graph

The bootstrap is the only creation that cannot use an existing `RoleAssignment` and a previously active SYNC definition. It is permitted only while no node with the `JCIEntity` label exists. One transaction creates the minimal organization, one technical member, its role, the root assignment, and exactly one initial active SYNC definition. The root assignment is permanently identified by `bootstrapKey = 'ROOT'` and remains the only active `JCIEntity` without `CREATED_BY`.

The following parameterized query is an executable bootstrap example. It returns exactly one row when it writes. If it returns no row, the graph was not empty; the calling deployment step must treat this as an error and must not attempt a second bootstrap.

```cypher
MATCH (gate:JCITechnicalGate {key: 'MODEL_WRITE'})
SET gate._lock = true
REMOVE gate._lock
WITH gate
OPTIONAL MATCH (existing:JCIEntity)
WITH gate, count(existing) AS existingCount
WHERE existingCount = 0
WITH gate, datetime.realtime() AS now
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
SET gate.graphEpoch = gate.graphEpoch + 1
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
       (executorCount > 0 OR environmentCount > 0 OR resultCount > 0))
   OR (t.taskKind = 'COMPOSITE' AND NOT t.status IN ['REPLACED','REVOKED']
       AND NOT EXISTS {
         MATCH (t)-[:DECOMPOSES_INTO]->(currentChild:Task)
         WHERE NOT currentChild.status IN ['REPLACED','REVOKED']
       })
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

```cypher
MATCH path = (task:Task)-[:DECOMPOSES_INTO|DEPENDS_ON*1..]->(task)
WHERE all(node IN nodes(path) WHERE node:Task AND NOT node.status IN ['REPLACED','REVOKED'])
RETURN DISTINCT task.id AS mixedCompletionCycle,
       [edge IN relationships(path) | type(edge)] AS relationshipTypes,
       [node IN nodes(path) | node.id] AS taskPath;
```

```cypher
MATCH (parent:Task)-[:DECOMPOSES_INTO]->(child:Task)
WHERE parent.status IN ['REPLACED','REVOKED']
  AND NOT child.status IN ['REPLACED','REVOKED']
RETURN parent.id AS retiredParentId, child.id AS unresolvedCurrentChildId;
```

```cypher
MATCH (parent:Task {taskKind: 'COMPOSITE'})
WHERE parent.status IN ['ACTIVE','BLOCKED','COMPLETED']
OPTIONAL MATCH (parent)-[:DECOMPOSES_INTO]->(child:Task)
WHERE NOT child.status IN ['REPLACED','REVOKED']
WITH parent, collect(DISTINCT child) AS children,
     EXISTS {
       MATCH (parent)-[:DEPENDS_ON]->(required:Task)
       WHERE required.status <> 'COMPLETED'
     } AS ownPrerequisiteUnmet
WHERE size(children) = 0
   OR (ownPrerequisiteUnmet AND parent.status <> 'BLOCKED')
   OR (parent.status = 'COMPLETED' AND any(child IN children WHERE child.status <> 'COMPLETED'))
   OR (NOT ownPrerequisiteUnmet AND none(child IN children WHERE child.status = 'ACTIVE')
       AND any(child IN children WHERE child.status = 'BLOCKED') AND parent.status <> 'BLOCKED')
RETURN parent.id AS invalidCompositeId, parent.status, ownPrerequisiteUnmet,
       [child IN children | {id: child.id, status: child.status}] AS currentChildren;
```

### Unmet dependency without BLOCKED

```cypher
MATCH (t:Task)-[:DEPENDS_ON]->(required:Task)
WHERE t.status IN ['ACTIVE','BLOCKED','COMPLETED']
  AND required.status <> 'COMPLETED' AND t.status <> 'BLOCKED'
RETURN t.id AS taskId, required.id AS unmetDependencyId, t.status AS actualStatus;
```

Unreleased DRAFT Tasks are excluded from this stored-state blocking check. Explicit release and its initial ACTIVE/BLOCKED state use canonical section 9.4.2, including aggregated child blocking. A newly released composite with only completed children remains ACTIVE initially; distinguishing it from a later completion transition requires the pre-change state in the transaction adapter.

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

```cypher
MATCH (source)-[approval:APPROVED_BY]->(target)
WHERE NOT ('JCIEntity' IN labels(source)) OR NOT ('GraphObject' IN labels(source))
   OR NOT ('ChangeEvent' IN labels(source))
   OR NOT ('JCIEntity' IN labels(target)) OR NOT ('GraphObject' IN labels(target))
   OR NOT ('RoleAssignment' IN labels(target))
   OR size(keys(approval)) <> 4
   OR any(key IN keys(approval)
          WHERE NOT key IN ['receiptId','decidedAt','requestHash','approvalHash'])
   OR valueType(approval.receiptId) <> 'STRING NOT NULL'
   OR approval.receiptId <> toLower(approval.receiptId)
   OR NOT (approval.receiptId =~
      '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$')
   OR valueType(approval.decidedAt) <> 'ZONED DATETIME NOT NULL'
   OR valueType(approval.requestHash) <> 'STRING NOT NULL'
   OR NOT (approval.requestHash =~ '^[0-9a-f]{64}$')
   OR valueType(approval.approvalHash) <> 'STRING NOT NULL'
   OR NOT (approval.approvalHash =~ '^[0-9a-f]{64}$')
RETURN elementId(approval) AS relationshipId,
       labels(source) AS sourceLabels, labels(target) AS targetLabels,
       properties(approval) AS invalidProperties;
```

Run the following check within the same acceptance transaction after creating the edges and before commit. `$verifiedApprovalProofs` is supplied only by the trusted verification adapter from the durable envelope; each entry additionally carries the `approvalHash` calculated by the adapter. The query requires exactly one matching proof for each edge and vice versa. It counts raw edges, not distinct target nodes:

```cypher
MATCH (change:JCIEntity:GraphObject:ChangeEvent {id: $changeEventId})
CALL {
  WITH change
  OPTIONAL MATCH (change)-[edge:APPROVED_BY]
        ->(assignment:JCIEntity:GraphObject:RoleAssignment)
  RETURN collect(CASE WHEN edge IS NULL THEN null ELSE {
    receiptId: edge.receiptId,
    decidedAt: edge.decidedAt,
    requestHash: edge.requestHash,
    approvalHash: edge.approvalHash,
    roleAssignmentId: assignment.id
  } END) AS storedApprovals
}
WITH change, storedApprovals, $verifiedApprovalProofs AS proofs
WHERE size(storedApprovals) <> size(proofs)
   OR any(proof IN proofs WHERE
        size([stored IN storedApprovals
              WHERE stored.receiptId = proof.receiptId
                AND stored.decidedAt = datetime(proof.decidedAt)
                AND stored.requestHash = proof.requestHash
                AND stored.approvalHash = proof.approvalHash
                AND stored.roleAssignmentId = proof.roleAssignmentId]) <> 1)
   OR any(stored IN storedApprovals WHERE
        size([proof IN proofs
              WHERE stored.receiptId = proof.receiptId
                AND stored.decidedAt = datetime(proof.decidedAt)
                AND stored.requestHash = proof.requestHash
                AND stored.approvalHash = proof.approvalHash
                AND stored.roleAssignmentId = proof.roleAssignmentId]) <> 1)
RETURN change.id AS changeEventId, size(storedApprovals) AS storedCount,
       size(proofs) AS verifiedCount;
```

Before this edge check, the adapter rejects an envelope if a receipt does not carry the same `requestHash` and `contextHash` as the envelope, repeats a `RoleAssignment`, has an outcome other than `APPROVED`, or fails `decidedAt <= decisionAt < validUntil`. Each receipt must resolve exactly one `RoFTeamMember {memberType: 'HUMAN'}` through `HAS_ASSIGNMENT` to the named `RoleAssignment`, and that member's ID must equal `memberId`. Validate role, member, team, and organization validity both at confirmation and at server-side `decisionAt`. An arbitrary string does not prove an attestation: signature, session-key, and identity verification belong in the trusted adapter and cannot be verified by Cypher alone.

Parallel duplicate edges must not bypass a cardinality check through `DISTINCT` on the target node:

```cypher
MATCH (source:JCIEntity)-[relationship]->(target:JCIEntity)
WHERE type(relationship) IN [
  'CREATED_BY','REQUESTED_BY','APPROVED_BY','CORRECTED_BY','CHANGED_BY',
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

A successful ordinary request creates exactly one PiH for its target only when its owned state actually changes. A domain no-op creates none. This stored-state query finds duplicates; exact agreement with the deduplicated transaction write set is checked under the gate before commit:

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
WHERE targetHistoryCount > 1
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

`PiF1o` still has exactly one accountability; each higher future level has `0..1`. Cardinality counts raw edges and therefore cannot be bypassed by parallel edges to the same member:

```cypher
MATCH (source)-[accountability:ACCOUNTABLE_MEMBER]->(target)
WHERE NOT (source:JCIEntity AND source.entityType IN ['PiF1o','PiF1t','PiF1s','PiF2'])
   OR NOT (target:JCIEntity AND target:GraphObject AND target:RoFTeamMember)
RETURN elementId(accountability) AS relationshipId,
       labels(source) AS sourceLabels, labels(target) AS targetLabels;
```

```cypher
MATCH (future:JCIEntity)
WHERE future.entityType IN ['PiF1o','PiF1t','PiF1s','PiF2']
OPTIONAL MATCH (future)-[accountability:ACCOUNTABLE_MEMBER]->(member)
WITH future, count(accountability) AS rawAccountabilityCount,
     collect(member) AS accountableMembers
WHERE (future.entityType = 'PiF1o' AND rawAccountabilityCount <> 1)
   OR (future.entityType IN ['PiF1t','PiF1s','PiF2'] AND rawAccountabilityCount > 1)
RETURN future.id AS futureId, future.entityType, rawAccountabilityCount,
       [member IN accountableMembers | member.id] AS accountableMemberIds;
```

A higher level needed for `Task.action.RELEASE` must actually be uniquely occupied in the current gate state. Only approval validation requires a uniquely assigned human member and a matching human role assignment for the anchor actually used; a technical accountability remains valid outside this route. Missing accountability on a required route is a model error, not implicit authority.

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
      ->(task:JCIEntity:GraphObject:Task)-[:PRODUCES]->(result)
MATCH (goal)-[:HAS_SUCCESS_CRITERIA]->(criterion)
WHERE v.status = 'COMPLETED'
  AND result.status = 'COMPLETED'
  AND criterion.status = 'ACTIVE'
  AND NOT task.status IN ['REPLACED','REVOKED']
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

```cypher
MATCH (verification:Verification)-[:EVALUATES]->(result:Result)
MATCH (verification)-[:CHECKS]->(criterion:SuccessCriterion)
WHERE NOT EXISTS { MATCH (:Verification)-[:SUPERSEDES]->(verification) }
WITH result, criterion, verification.evaluatedResultRevision AS resultRevision,
     verification.checkedCriterionRevision AS criterionRevision,
     collect(verification.id) AS verificationIds
WHERE size(verificationIds) > 1
RETURN result.id AS resultId, criterion.id AS criterionId,
       resultRevision, criterionRevision, verificationIds;
```

```cypher
MATCH (goal:PiF1o)
WHERE goal.status IN ['ACTIVE','ACHIEVED']
WITH goal,
     COUNT {
       MATCH (goal)-[:DECOMPOSES_INTO]->(task:Task)
       WHERE NOT task.status IN ['REPLACED','REVOKED']
     } AS currentTaskCount,
     COUNT {
       MATCH (goal)-[:HAS_SUCCESS_CRITERIA]->(criterion:SuccessCriterion {requirementLevel: 'REQUIRED'})
       WHERE NOT criterion.status IN ['REPLACED','REVOKED']
     } AS currentRequiredCount
WHERE currentTaskCount = 0 OR currentRequiredCount = 0
RETURN goal.id AS emptyCurrentScope, currentTaskCount, currentRequiredCount;
```

```cypher
MATCH (goal:PiF1o {status: 'ACHIEVED'})-[:DECOMPOSES_INTO]->(task:Task)
WHERE NOT task.status IN ['REPLACED','REVOKED']
  AND (task.status <> 'COMPLETED' OR EXISTS {
    MATCH (task)-[:DEPENDS_ON]->(required:Task)
    WHERE required.status <> 'COMPLETED'
  })
RETURN goal.id AS goalId, task.id AS unfinishedCurrentTask;
```

```cypher
MATCH (goal:PiF1o {status: 'ACHIEVED'})-[:HAS_SUCCESS_CRITERIA]
      ->(criterion:SuccessCriterion {requirementLevel: 'REQUIRED'})
WHERE NOT criterion.status IN ['REPLACED','REVOKED']
OPTIONAL MATCH (verification:Verification)-[:CHECKS]->(criterion)
WHERE verification.status = 'COMPLETED'
  AND verification.checkedCriterionRevision = criterion.revision
  AND NOT EXISTS { MATCH (:Verification)-[:SUPERSEDES]->(verification) }
  AND EXISTS {
    MATCH (goal)-[:DECOMPOSES_INTO]->(task:Task)-[:PRODUCES]->(result:Result {status: 'COMPLETED'})
    MATCH (verification)-[:EVALUATES]->(result)
    WHERE NOT task.status IN ['REPLACED','REVOKED']
      AND verification.evaluatedResultRevision = result.revision
  }
WITH goal, criterion, collect(DISTINCT verification) AS applicable
WHERE criterion.status <> 'ACTIVE' OR size(applicable) = 0
   OR (criterion.evaluationMode = 'ALL' AND any(v IN applicable WHERE v.outcome <> 'VALID'))
   OR (criterion.evaluationMode = 'ANY' AND none(v IN applicable WHERE v.outcome = 'VALID'))
RETURN goal.id AS goalId, criterion.id AS unfulfilledCurrentRequiredCriterion;
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

`approvalPolicyJson` is optional. When present, the profile-bound adapter validates the closed structure from [`jci-history-snapshot.schema.json`](../../../schemas/jci-history-snapshot.schema.json) before every candidate evaluation: `profileVersion = "1.0"`, `mode = ACCOUNTABLE_CHAIN | VALUE_SCOPE`, non-empty unique `roleIds`, and non-empty unique `levels` only for `ACCOUNTABLE_CHAIN`. There is no default role, default level, or silent conversion. Without a JSON parser, Cypher can validate only the storage form:

```cypher
MATCH (rule:JCIEntity:RaN)
WHERE rule.approvalPolicyJson IS NOT NULL
  AND (valueType(rule.approvalPolicyJson) <> 'STRING NOT NULL'
       OR trim(rule.approvalPolicyJson) = '')
RETURN rule.id AS ruleId, rule.approvalPolicyJson;
```

Every initial Task release requires an explicit `ACCOUNTABLE_CHAIN` policy in an active matching `PERMIT` RaN for `Task.action.RELEASE`; no policy means no release. The gate starts at the unique direct `PiF1o` and follows **all** current `CONTRIBUTES_TO` branches until each branch reaches its first explicitly authorized accountability. `ANY` does not reduce this set. Only absence of authority permits the next step on the same branch; `REJECTED`, `DENY`, `UNEVALUABLE`, conflict, or missing or ambiguous mappings terminates the entire approval without an alternate role or higher escalation. A RaN or accountability newly introduced by the candidate cannot authorize its own candidate; authority comes from the state already valid before the change.

For `Model.action.CONFIRM`, a `VALUE_SCOPE` RaN governs the approving `RoleAssignment` within the scope of the affected old and new value holders. `CiV`, `HELD_BY`, `INFORMED_BY`, `INSCRIBES_PURPOSE_IN`, and `PROTECTS` remain the protected model decisions; neither a `GOVERNS` target of `CiV`/`PiF2` nor a Task future chain is added as a substitute.

Technical initial authority is bound to one explicitly authenticated human member, that member's concrete `RoleAssignment`, and exactly one value holder. It applies only to `Model.action.CONFIRM`. Before committing the first active `VALUE_SCOPE` policy, the gate derives the exact affected value holders from the policy's `PROTECTS`-related CiV/PiF2 and atomically sets their technical enrollment latch with the domain candidate. This latch is monotonic: removing or revoking the policy must never clear it or reactivate initial authority. A global RaN scope does not grant a mandate for an unrelated value holder.

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

Profile 2.0 permits only complete TypedValue properties under /stateData/properties/<property>, complete historical relationship entries under /relationshipData/<key>, and their /properties/<property>. The stable key is direction + ":" + relationshipType + ":" + canonicalUUID(otherEntityId). The stored relationshipData list is retained; the resolver creates a map for addressing only and rejects duplicate keys. Identity and original revision must not be reinterpreted.

The following 2.0 queries check address shape and segment-prefix overlap. JSON Pointers are split into segments and ~1/~0 decoded before comparison. Equality and a true ancestor relation count as overlap; name and nameLong remain disjoint. Older profiles are not reinterpreted with the new grammar. The versioned resolver checks permitted properties, complete TypedValues, canonical re-encoding, existence, and mixed profile sets under the write gate.

```cypher
MATCH (correction:HistoricalCorrection {valueSchemaVersion: '2.0'})
UNWIND correction.correctedFields AS pointer
WHERE NOT (pointer =~ '^/stateData/properties/([^/~]|~[01])+$'
   OR pointer =~ '^/relationshipData/(INCOMING|OUTGOING):[A-Z][A-Z_]*:[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}(/properties/([^/~]|~[01])+)?$')
RETURN correction.id AS correctionId, pointer AS invalidAddress;
```

```cypher
MATCH (correction:HistoricalCorrection {valueSchemaVersion: '2.0'})
WITH correction, [pointer IN correction.correctedFields |
  [segment IN tail(split(pointer, '/')) |
    replace(replace(segment, '~1', '/'), '~0', '~')]] AS paths
UNWIND range(0, size(paths) - 1) AS leftIndex
UNWIND range(leftIndex + 1, size(paths) - 1) AS rightIndex
WITH correction, paths[leftIndex] AS leftPath, paths[rightIndex] AS rightPath
WHERE leftPath IS NOT NULL AND rightPath IS NOT NULL
  AND ((size(leftPath) <= size(rightPath) AND leftPath = rightPath[..size(leftPath)])
    OR (size(rightPath) <= size(leftPath) AND rightPath = leftPath[..size(rightPath)]))
RETURN correction.id AS internallyOverlappingCorrection, leftPath, rightPath;
```

```cypher
MATCH (left:HistoricalCorrection {valueSchemaVersion: '2.0'})-[:CORRECTS]->(history:PiH)
MATCH (right:HistoricalCorrection {valueSchemaVersion: '2.0'})-[:CORRECTS]->(history)
WHERE left.id < right.id
  AND NOT EXISTS { MATCH (:HistoricalCorrection)-[:SUPERSEDES]->(left) }
  AND NOT EXISTS { MATCH (:HistoricalCorrection)-[:SUPERSEDES]->(right) }
WITH history, left, right,
     [pointer IN left.correctedFields | [segment IN tail(split(pointer, '/')) |
       replace(replace(segment, '~1', '/'), '~0', '~')]] AS leftPaths,
     [pointer IN right.correctedFields | [segment IN tail(split(pointer, '/')) |
       replace(replace(segment, '~1', '/'), '~0', '~')]] AS rightPaths
WHERE any(p IN leftPaths WHERE any(q IN rightPaths WHERE
  (size(p) <= size(q) AND p = q[..size(p)]) OR
  (size(q) <= size(p) AND q = p[..size(q)])))
RETURN history.id AS historyId, left.id AS leftCorrectionId, right.id AS rightCorrectionId;
```

Without overlap a new correction may coexist. If exactly one active correction is affected, completely supersede exactly that correction through SUPERSEDES and retain all previous canonical paths and still-valid values. Additional paths must overlap neither within the new correction nor with other active corrections. Multiple overlaps or implicit switching between whole-relationship and property correction produces CONFLICT.

ADDITION requires actual absence; an existing NULL value is not absent. CORRECTION and CLARIFICATION require an existing path. previousValue is checked at commit against the then-effective view. On later rebuilds, apply correctedValue entries of non-superseded corrections as absolute overlays on the immutable PiH; do not recheck previousValue against the original. This preserves corrections to previously added information after the original addition is superseded.

The following selection query returns resolver inputs, not the hash input itself. HistoryView 2.0 is exclusively the effective combination {stateData, relationshipData}; sort its relationship list by relationshipType, direction, and otherEntityId. Calculate SHA-256 over its canonical serialization, excluding historyId, correction IDs, and the technical address map. Compare expectedHistoryViewHash from the request with this view and store it unchanged as baseHistoryViewHash on success.

```cypher
MATCH (history:JCIEntity:PiH)
OPTIONAL MATCH (correction:HistoricalCorrection)-[:CORRECTS]->(history)
WHERE correction IS NULL OR NOT EXISTS {
  MATCH (:HistoricalCorrection)-[:SUPERSEDES]->(correction)
}
WITH history, correction ORDER BY correction.id
WITH history, collect(correction{
  .id, .correctionType, .correctedFields, .valueSchemaVersion,
  .previousValueJson, .correctedValueJson
}) AS activeCorrections
RETURN history.id AS historyId, history.snapshotSchemaVersion AS snapshotSchemaVersion,
       history.stateDataJson AS stateDataJson,
       history.relationshipDataJson AS relationshipDataJson, activeCorrections;
```

Profile 2.0 uses UTF-8 without BOM/extra whitespace, Unicode-code-point key ordering, and JSON string escaping without blanket ASCII escaping. INTEGER stays exact/unbounded; floating-point values are prohibited even inside OBJECT/ARRAY. DECIMAL is a normalized decimal string without exponent or unnecessary zeros; nested decimal values are TypedValue DECIMAL. Section 2.2.9 of [`JCI_CONTEXT.md`](../../JCI_CONTEXT.md) and shared hash test vectors govern.

All corrections are validated and committed under the common gate from the transaction section. Immediately before commit, recheck hash, previous values, existence, paths, and active correction set. Older profiles require explicit resolvers; ambiguous paths stop the new operation. Existing PiH, corrections, and their hashes are neither recalculated nor overwritten. The view hash is not a technical ABA guard: a later identical effective view has the same hash; the gate/graphEpoch protects competing references.

**Short example:** /stateData/properties/name is a complete property. /relationshipData/INCOMING:HAS_MEMBER:<Team-UUID> overlaps with its /properties/validUntil. They must not coexist as separate active corrections.

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

Validate the entire candidate under the gate using current sets: Task/criterion contributions exclude REPLACED and REVOKED, required sets remain non-empty, and Results must originate from current Tasks. Check mixed completion cycles jointly over DECOMPOSES_INTO and DEPENDS_ON. Then evaluate prerequisites first, a Composite's own prerequisites before child aggregation, and never return released Composites to DRAFT. Scope reduction alone does not release a draft; DRAFT → COMPLETED remains prohibited. These transition preconditions require the initial state: a later stored-state query cannot replace them.

Accepting an approval envelope is already a separate gate transaction. From the unchanged base request and old/new state, the handler classifies whether `Task.action.RELEASE` or `Model.action.CONFIRM` is required; a client-selected `decisionKey` may only confirm, never replace, that derivation. It requires an active SYNC definition with `approvalProfileVersion = "1.0"` and a package checksum binding that exact validator. Before any `ChangeEvent`, it stores the proposal and every response in the technical ledger. Only complete approval creates the `ChangeEvent`, `REQUESTED_BY`, immutable `APPROVED_BY` edges, and run schedule together. On rejection or incomplete approval, only the technical record remains and the Task is unchanged.

Reads include negative sets and dependencies, such as previously absent RaN, role/scope assignments, and the current non-superseded verification set. Comparing domain revisions alone is insufficient. Every validation applies to the complete candidate, including all new edges and actual follow-up changes.

The following driver example shows the mandatory transaction boundary for the run executed after acceptance. `rules` denotes explicit adapters of the versioned validated rule package, not available Neo4j built-ins: `read_complete_state` must provide the complete relevant read view. `revalidate_approval` calculates under the lock the SHA-256 of the exact canonical base request and a new `contextHash` from the approval profile, `decisionKey`, request hash, complete relevant domain graph view, derived requirements, and initial authorities with their permanent latches. It rechecks every current future branch, RaN, accountability, role/scope basis, receipt time, and human attestation. `evaluate_complete_candidate` validates every other model, temporal, path, and RaN rule; `apply_owned_domain_delta` may write only the deduplicated owned domain delta. `persist_enrollment_latches` monotonically sets the technical latches derived from the first active `VALUE_SCOPE` policy in the same transaction; these markers are not domain delta and must never be deleted. `append_success_bundle` writes PiH, provenance, SyncEvent, immutable success record, and outbox. `validate_persisted_bundle` checks every counter, approval edge, and query against that complete state. No function may open its own transaction or perform external side effects.

```python
def commit_reference(session, request_id, run_id, fencing_token, rules):
    with session.begin_transaction() as tx:
        gate = tx.run(
            "MATCH (g:JCITechnicalGate {key: 'MODEL_WRITE'}) "
            "SET g._lock = true REMOVE g._lock "
            "RETURN g.graphEpoch AS graphEpoch"
        ).single(strict=True)
        request = rules.load_immutable_request(tx, request_id)
        approval = rules.load_immutable_approval_if_required(tx, request_id)
        rules.assert_run_owner(tx, run_id, fencing_token)
        previous = rules.find_success(tx, request.idempotency_key)
        if previous is not None:
            return previous
        state = rules.read_complete_state(tx)
        rules.assert_requested_revision(state, request)
        decision_at = tx.run(
            "RETURN datetime.realtime() AS decisionAt"
        ).single(strict=True)["decisionAt"]
        approval_proofs = rules.revalidate_approval(
            tx, state, request, approval, decision_at=decision_at
        )
        proposal = rules.evaluate_complete_candidate(
            state, request, decision_at=decision_at,
            approval_proofs=approval_proofs,
        )
        rules.assert_valid(proposal)
        rules.apply_owned_domain_delta(tx, proposal)
        rules.persist_enrollment_latches(tx, state, proposal)
        result = rules.append_success_bundle(
            tx, proposal, request, run_id, decision_at,
            graph_epoch=gate["graphEpoch"] + 1,
        )
        rules.validate_persisted_bundle(
            tx, proposal, result, approval_proofs=approval_proofs
        )
        tx.run(
            "MATCH (g:JCITechnicalGate {key: 'MODEL_WRITE'}) "
            "SET g.graphEpoch = g.graphEpoch + 1"
        ).consume()
        tx.commit()
        return result
```

The technical commit record stores decisionAt, actually executed SYNC revision/package checksum, the deduplicated changed-owner set, and revisions read during validation. A CREATE target starts at revision 1 without PiH; each existing entity actually changed receives exactly one revision increment and one PiH. Pure audit references and new process objects do not count in the domain write set. A no-op has changedCount = historyCount = 0 and still exactly one success record. Calculate all five counters from the write set and relationships before commit.

Validation conflicts or technical failures roll back the domain transaction; then create completion documentation under the same gate. An unavailable database leaves a recovery obligation in the durable run record. If commit outcome is unknown, first inspect the same runId under the gate; never repeat an already stored success. A stale fencing token must not write completion. A new base revision requires a new request; requestedRevision remains unchanged.

Finally reevaluate all time-dependent decisions for a fixed server-side decisionAt after acquiring the lock. completedAt remains completion time. The contract guarantees domain validity at decisionAt, not later physical commit confirmation or external actions. A rule becoming applicable solely through time is considered without a new domain revision. A later optimization may compare graphEpoch read under the gate after computing externally and reacquiring the gate; on mismatch reread and prepare again, always reevaluating temporal conditions.

Outbox delivery occurs only after commit. A dispatcher crash may cause redelivery; recipients must deduplicate using the stable event identifier. The outbox alone does not guarantee exactly-once external effects.

## Limits of declarative enforcement

Neo4j constraints and subsequent Cypher queries cover the stored graph state, but they cannot guarantee five runtime properties on their own:

1. A `SyncRun` completed outside the graph can only be recognized as a missing `SyncEvent` after reconciliation with the technical run/outbox log.
2. Preventing later changes to or deletion of immutable nodes and their assigned owned relationships requires restricted write roles or exclusively approved SYNC write transactions; a property constraint is not an append-only mechanism.
3. The canonical overlay of `stateDataJson`, `relationshipDataJson`, and correction values, as well as SHA-256 calculation, takes place in the versioned SYNC rules package. Cypher validates structure, uniqueness, and the stored hash format, but not the JSON semantics themselves.
4. Revision `1` of a newly created target and the Verification and history revisions rechecked immediately before commit are transaction preconditions. A later snapshot of the graph after further development can reconstruct this temporal fact only from the fully stored history.
5. Canonical request/context/approval hashes and the cryptographic or session-bound authenticity of a human attestation require the package-bound hash profile and a trusted authentication adapter. Cypher can validate stored form, endpoints, and exact edge-to-proof matching, but cannot turn an arbitrary attestation string into a real human. A `RoleAssignment` expiring or being revoked later does not invalidate an immutable historical receipt that was valid at its `decidedAt`; current validity is required only during acceptance and domain commit.

## Migration and versioning

Changes are forward-only immutable migrations with source/target versions, prevalidation, technical schema, postvalidation, and a restorable backup. This documentation change itself runs no migration, bootstrap, or live database action.

1. Inventory old profiles and their required resolvers. Existing immutable documents, snapshot data, and hashes remain unchanged; no random backfills of historical run IDs, revisions, or checksums.
2. Initialize the new technical gate/request/run/commit/outbox structures in a controlled manner. Require every write path, including import and recovery, to use the same gate.
3. Activate a new SYNC definition with rule, ontology, graph-rule, sync-spec, snapshot, correction, and exchange profile 2.0 only when all existing types and legacy read profiles are explicitly supported and the package checksum matches. Namespace identities and JSON-LD1.1 remain unchanged.
4. Prevalidate every existing Task/criterion scope, replacement assignment, current parent structure, Composite status, and mixed completion cycle. Empty active scopes or unresolved subtrees require reasoned domain requests; no automatic revocation, redirection, or reopening of terminal facts.
5. Create new PiH under revision ownership and snapshot profile 2.0. Existing PiH retain their original profiles; stored relationship snapshots are not retroactively filtered or rehashed.
6. Read historical corrections through their explicit profile resolver. Ambiguous addresses, colliding relationship keys, or overlapping active legacy corrections stop transition for the affected data. A new 2.0 operation uses stable addresses and the unambiguously resolved effective-view hash.
7. Do not blindly rename old GOVERNS edges to PiF2 into PROTECTS. An authorized human confirms protected PiF2, coherent CiV, and actual implementation elements. Only a regular validated request commits the new protection/governance references.
8. Apply constraints only after validating their preconditions. Every applicable stored-state query must return zero errors; transaction, revision, resolver, and concurrency tests must pass additionally. Incompatible combinations are not activated.
9. Activate approval profile 1.0 only when the envelope schema, canonical hashing, complete route derivation, trusted attestation verification, and durable technical receipt storage are available together. Do not invent `APPROVED_BY` edges for existing `ChangeEvent` nodes or terminal domain states. Offer `approvalProfileVersion = "1.0"` only through a new validated SYNC definition whose package checksum binds the verifier.

For an empty domain store, install technical constraints/gate first, then execute the atomic domain bootstrap exactly once under the gate. Existing technical records do not constitute a second domain bootstrap.

**Short example:** An old PiH using profile 1.0 retains its contentHash. New state changes create new PiH using 2.0. If an old correction address cannot be resolved unambiguously, stop transition for that case instead of reinterpreting its historical value.

## Demarcation of client separation

`RoFOrg` is a business organization in the JCI graph and not a technical client key. Multiple organizations may deliberately be connected in a common model graph. Technical database, access or deployment isolation is implemented outside the JCI ontology and must not change the technical organizational relationships.

## Automated testing

Technology-independent invariants are checked by [`tests/test_model_rules.py`](../../../../tests/test_model_rules.py). [`reference/jci_rules.py`](../../../../reference/jci_rules.py) and [`tests/test_reference_rules.py`](../../../../tests/test_reference_rules.py) execute owner revisions, current completion sets, joint cycles, profile-2.0 corrections, and competing candidates. [`tests/test_approval_schema.py`](../../../../tests/test_approval_schema.py) validates the closed envelope, required receipt fields, RaN policy forms, and absence of defaults. [`tests/test_spec_consistency.py`](../../../../tests/test_spec_consistency.py) checks catalog, schema, and document consistency. GitHub Actions runs the tests on every push to `main` and pull request. Reference tests replace neither a production SYNC engine nor an actual Neo4j isolation test.

The Cypher queries in this document remain additionally mandatory for a real Neo4j instance. Every validation query must return zero rows after migration and business transaction.
