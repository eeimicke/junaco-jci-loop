# JCI-Neo4j-Schema

## Status und Zweck

Dieses Dokument konkretisiert die technische Abbildung des JCI-Modells in Neo4j. Es implementiert [JCI_CONTEXT.md](../../JCI_CONTEXT.md), [JCI_ONTOLOGY.md](../../JCI_ONTOLOGY.md), [JCI_GRAPH_RULES.md](../../JCI_GRAPH_RULES.md) und [JCI_SYNC_SPEC.md](../../JCI_SYNC_SPEC.md). Bei einem Konflikt gilt die fachliche Spezifikation; das Schema darf ihre Semantik nicht verändern.

## Gemeinsame Label- und Eigenschaftsstrategie

Jeder fachliche Knoten trägt `JCIEntity` und genau eines der abstrakten Labels `JCIElementInstance` oder `GraphObject`. Zusätzlich trägt er genau ein konkretes Typ-Label, das mit `entityType` übereinstimmt.

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

Die global eindeutige `JCIEntity.id` macht zusätzliche ID-Constraints je konkretem Label technisch redundant. Spezifische Constraints werden nur für fachlich weitere eindeutige Schlüssel angelegt.

### Komplexe strukturierte Werte

Neo4j-Properties speichern keine verschachtelten JSON-Objekte. Die kanonischen Strukturen aus `JCI_CONTEXT.md` werden deshalb ohne Semantikverlust als kanonische JSON-Zeichenketten projiziert:

| Fachliches Feld                       | Neo4j-Property         |
| ------------------------------------- | ---------------------- |
| `RaN.condition`                       | `conditionJson`        |
| `SYNC.definition`                     | `definitionJson`       |
| `Result.value`                        | `valueJson`            |
| `PiH.stateData`                       | `stateDataJson`        |
| `PiH.relationshipData`                | `relationshipDataJson` |
| `HistoricalCorrection.previousValue`  | `previousValueJson`    |
| `HistoricalCorrection.correctedValue` | `correctedValueJson`   |

Die JSON-Zeichenketten verwenden UTF-8, lexikografisch sortierte Objektschlüssel und die kanonischen Datentypregeln aus Abschnitt 2.2.7. `PiH.contentHash` wird aus den fachlichen Strukturen vor dieser Neo4j-Projektion berechnet.

## Labels und Eigenschaften für Tasks

Jeder Task trägt mindestens die Labels `JCIEntity`, `GraphObject` und `Task`. Zusätzlich zu den gemeinsamen Pflichtfeldern besitzt er verpflichtend:

```text
taskKind = ATOMIC | COMPOSITE
status   = DRAFT | ACTIVE | BLOCKED | COMPLETED | REPLACED | REVOKED
```

`PiF1o` ist ein gewünschter Zustand. `Task` ist eine Tätigkeit. „Kundenportal entwickeln“ wird daher als `COMPOSITE`-Task modelliert; der zugehörige `PiF1o` lautet beispielsweise „Das Kundenportal ist produktiv nutzbar“.

## Relationship-Typen für Tasks

| Quelle  | Relationship       | Ziel             | Bedeutung                                      |
| ------- | ------------------ | ---------------- | ---------------------------------------------- |
| `PiF1o` | `DECOMPOSES_INTO`  | `Task`           | direkter operativer Zielkontext jedes Tasks    |
| `Task`  | `DECOMPOSES_INTO`  | `Task`           | direkte Parent-/Subtask-Struktur               |
| `Task`  | `DEPENDS_ON`       | `Task`           | fachliche Ausführungsvoraussetzung             |
| `Task`  | `RESPONSIBLE_TEAM` | `RoFTeam`        | genau ein verantwortliches Team                |
| `Task`  | `EXECUTED_BY`      | `RoleAssignment` | Ausführung ausschließlich atomarer Tasks       |
| `Task`  | `USES`             | `ERoFObject`     | Umweltverwendung ausschließlich atomarer Tasks |
| `Task`  | `PRODUCES`         | `Result`         | Ergebnis ausschließlich atomarer Tasks         |

## Direkt erzwingbare Constraints

Die folgenden Cypher-Anweisungen setzen Neo4j 5 voraus:

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

Neo4j-Constraints erzwingen Enum-Werte, Kardinalitäten und graphweite Zyklusregeln nicht vollständig. Diese Regeln werden vor dem Schreiben durch `SYNC` und nach dem Schreiben durch Validierungsabfragen geprüft.

## Validierungsabfragen

Jede folgende Abfrage muss für einen gültigen Graphen null Zeilen liefern.

### Ungültige Enum-Werte

```cypher
MATCH (t:Task)
WHERE NOT t.taskKind IN ['ATOMIC', 'COMPOSITE']
   OR NOT t.status IN ['DRAFT', 'ACTIVE', 'BLOCKED', 'COMPLETED', 'REPLACED', 'REVOKED']
RETURN t.id AS taskId, t.taskKind, t.status;
```

### Fehlender oder mehrfacher PiF1o- und Teamkontext

```cypher
MATCH (t:Task)
OPTIONAL MATCH (p:PiF1o)-[:DECOMPOSES_INTO]->(t)
OPTIONAL MATCH (t)-[:RESPONSIBLE_TEAM]->(team:RoFTeam)
WITH t, count(DISTINCT p) AS pifCount, count(DISTINCT team) AS teamCount
WHERE pifCount <> 1 OR teamCount <> 1
RETURN t.id AS taskId, pifCount, teamCount;
```

### Ungültige Task-Typenstruktur

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

### Mehrere direkte Parent-Tasks oder verschiedener PiF1o-Kontext

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

### Zyklen in Hierarchie oder Abhängigkeiten

```cypher
MATCH (t:Task)-[:DECOMPOSES_INTO*1..]->(t)
RETURN DISTINCT t.id AS taskHierarchyCycle;
```

```cypher
MATCH (t:Task)-[:DEPENDS_ON*1..]->(t)
RETURN DISTINCT t.id AS dependencyCycle;
```

### Nicht erfüllte Abhängigkeit ohne BLOCKED

```cypher
MATCH (t:Task)-[:DEPENDS_ON]->(required:Task)
WHERE required.status <> 'COMPLETED' AND t.status <> 'BLOCKED'
RETURN t.id AS taskId, required.id AS unmetDependencyId, t.status AS actualStatus;
```

### Ausführung außerhalb des verantwortlichen Teams

```cypher
MATCH (t:Task {taskKind: 'ATOMIC'})-[:RESPONSIBLE_TEAM]->(team:RoFTeam)
WHERE t.status IN ['ACTIVE', 'COMPLETED']
  AND NOT EXISTS {
    MATCH (t)-[:EXECUTED_BY]->(:RoleAssignment)-[:IN_TEAM]->(team)
  }
RETURN t.id AS taskId, team.id AS responsibleTeamId;
```

## RaN-Priorität und Konflikte

`RaN.priority` ist eine verpflichtende Ganzzahl. Eine größere Zahl bedeutet höheren Vorrang bei einem tatsächlichen Widerspruch; `ruleType` besitzt keine technische Rangfolge. Ein nicht automatisch entscheidbarer Konflikt wird als Knoten mit den Labels `JCIEntity`, `GraphObject` und `RaNConflict` gespeichert.

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

### Ungültige RaNConflict-Eigenschaften oder Kardinalitäten

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

### PRIORITY_TIE ohne gleichen höchsten Prioritätswert

```cypher
MATCH (c:RaNConflict {conflictType: 'PRIORITY_TIE'})-[:CONFLICTING_RULE]->(r:RaN)
WITH c, count(DISTINCT r) AS ruleCount, collect(DISTINCT r.priority) AS priorities
WHERE ruleCount < 2 OR size(priorities) <> 1
RETURN c.id AS conflictId, ruleCount, priorities;
```

Die Erkennung eines inhaltlichen Widerspruchs kann nicht allein durch Neo4j-Constraints erfolgen. Sie gehört zur fachlichen Regelauswertung von `SYNC`. Die Datenbank validiert anschließend, dass Konfliktknoten, Prioritäten und Auflösungsbeziehungen vollständig gespeichert wurden.

## Vollständige Validierung der übrigen Modellbereiche

### Konkretes Typ-Label und abstrakte Klasse

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

### Gemeinsame Pflichtwerte und unveränderliche Dokumente

```cypher
MATCH (e:JCIEntity)
WHERE e.revision IS NULL OR e.revision < 1
   OR e.createdAt IS NULL OR e.updatedAt IS NULL OR e.updatedAt < e.createdAt
   OR e.name IS NULL OR trim(e.name) = ''
   OR (e.entityType IN ['PiH','ChangeEvent','SyncEvent','HistoricalCorrection']
       AND (e.revision <> 1 OR e.status <> 'RECORDED' OR e.updatedAt <> e.createdAt))
RETURN e.id AS entityId, e.entityType, e.revision, e.status;
```

### Nachfolgebeziehungen

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

### Zukunftskette und Erreichung

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

### Erfolgskriterien und Verifications

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

### RoF-Gültigkeit, Kapazität und Organisationsbeziehungen

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

Die Prüfung überlappender `allocation`-Intervalle wird durch SYNC mit Intervallzerlegung ausgeführt; Neo4j besitzt dafür keinen deklarativen Constraint. Für jeden Zeitpunkt darf die Summe eines Mitglieds höchstens `1` betragen.

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

### ERoF-Eigentum und personengebundene Verwendung

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

### RaN-Scope und strukturierte Bedingungen

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

### PiH, Korrekturen und SyncEvent

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
OPTIONAL MATCH (event)-[:CREATES_HISTORY]->(history:PiH)
OPTIONAL MATCH (event)-[:CREATES_CORRECTION]->(correction:HistoricalCorrection)
OPTIONAL MATCH (conflict:RaNConflict)-[:DETECTED_BY]->(event)
WITH event, count(DISTINCT change) AS triggerCount,
     count(DISTINCT definition) AS definitionCount,
     count(DISTINCT affected) AS actualAffectedCount,
     count(DISTINCT history) AS actualHistoryCount,
     count(DISTINCT correction) AS actualCorrectionCount,
     count(DISTINCT conflict) AS actualConflictCount
WHERE triggerCount <> 1 OR definitionCount <> 1 OR actualAffectedCount < 1
   OR event.startedAt IS NULL OR event.completedAt IS NULL
   OR event.completedAt < event.startedAt
   OR event.outcome IS NULL
   OR NOT event.outcome IN ['SUCCESS','CONFLICT','FAILED']
   OR event.affectedCount IS NULL OR event.affectedCount < 1
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

`affectedCount`, `historyCount`, `correctionCount` und `conflictCount` sind aus den gespeicherten Beziehungen vollständig nachprüfbar. `changedCount` bezeichnet dagegen die Anzahl der in derselben Transaktion tatsächlich übernommenen fachlichen Zieländerungen. Da das Modell dafür bewusst keine zusätzliche `CHANGES`-Beziehung speichert, berechnet `SYNC` diesen Wert aus dem deduplizierten Transaktions-Write-Set unmittelbar vor dem Commit. Jede darin enthaltene bestehende veränderliche `JCIEntity` muss genau eine Revisionserhöhung und genau ein zugehöriges `PiH` erhalten. Eine durch den Veränderungsauftrag neu angelegte fachliche Zielentität zählt als übernommene Änderung, erhält aber noch kein `PiH`. Neu erzeugte Prozess- und Dokumentationsobjekte wie `PiH`, `SyncEvent`, `HistoricalCorrection` oder ein durch `SYNC` dokumentierter `RaNConflict` zählen nicht zu `changedCount`. Bei `CONFLICT` oder `FAILED` zählen zurückgerollte Schreiboperationen ebenfalls nicht. Der berechnete Wert wird zusammen mit dem Graphzustand und dem abschließenden `SyncEvent` atomar übernommen.

## Transaktionsregel für SYNC

`SYNC` prüft Hierarchie, Abhängigkeiten, Task-Typregeln sowie anwendbare `RaN` vor der Übernahme. Abgeleitete Task-Status werden von den atomaren Tasks über die Parent-Kette nach oben und erst danach zu den betroffenen `PiF1o` aggregiert. Aktuelle Zustände, erforderliche `PiH`, neue oder aufgelöste `RaNConflict`-Objekte, Beziehungen, das deduplizierte Transaktions-Write-Set und das abschließende `SyncEvent` werden atomar übernommen. Vor dem Commit werden alle fünf Zählwerte aus diesem Write-Set und den zu speichernden Beziehungen berechnet. Ein Konflikt oder Fehler darf keinen teilweise aktualisierten Graphen hinterlassen.

## Migration und Versionsführung

Schemaänderungen werden als vorwärts gerichtete, unveränderliche Migrationen mit aufsteigender Nummer gespeichert. Jede Migration enthält:

1. erwartete Ausgangsversion,
2. Vorabvalidierungen,
3. Constraints, Indizes und notwendige Datenanpassungen,
4. Nachvalidierungen,
5. neue Zielversion.

Vor einer Migration wird eine wiederherstellbare Datenbanksicherung erzeugt. Eine Migration wird nur abgeschlossen, wenn alle Nachvalidierungen null Fehler liefern. Die aktive `SYNC.definition` nennt die dazu passende Ontologie-, Graphregel- und Schemazielversion; eine inkompatible Kombination darf nicht aktiviert werden.

**Kurzes Beispiel:** Migration `V002` ergänzt `REPLACED_BY`. Sie prüft zuerst alle vorhandenen `REPLACED`-Entitäten, legt benötigte Nachfolgekanten innerhalb einer kontrollierten Datenmigration an und aktiviert den neuen Constraint erst, wenn keine ersetzte Entität ohne Nachfolger verbleibt.

## Abgrenzung der Mandantentrennung

`RoFOrg` ist eine fachliche Organisation im JCI-Graphen und kein technischer Mandantenschlüssel. Mehrere Organisationen dürfen bewusst in einem gemeinsamen Modellgraphen verbunden sein. Technische Datenbank-, Zugriffs- oder Deployment-Isolation wird außerhalb der JCI-Ontologie umgesetzt und darf die fachlichen Organisationsbeziehungen nicht verändern.

## Automatisierte Prüfung

Die technologieunabhängigen Invarianten werden zusätzlich durch `tests/test_model_rules.py` geprüft. `tests/test_spec_consistency.py` stellt sicher, dass Entitäts- und Beziehungskatalog, strukturierte Datentypen sowie die Folgedokumente synchron bleiben. GitHub Actions führt beide Tests bei jedem Push auf `main` und bei jedem Pull Request aus.

Die Cypher-Abfragen dieses Dokuments bleiben für eine reale Neo4j-Instanz zusätzlich verpflichtend. Jede Validierungsabfrage muss nach Migration und fachlicher Transaktion null Zeilen liefern.
