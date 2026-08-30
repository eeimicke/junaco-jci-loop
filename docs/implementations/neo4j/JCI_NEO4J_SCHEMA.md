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

### Technische Pflichtfelder für Veränderung, Prüfung und Korrektur

Die folgenden Felder präzisieren die Speicherung der bereits definierten fachlichen Vorgänge. Alle genannten Knoten tragen zusätzlich das Label `JCIEntity` und ihr abstraktes sowie konkretes Typ-Label.

| Knoten | Property | Bedeutung |
| ------ | -------- | --------- |
| `ChangeEvent` | `idempotencyKey` | unveränderliche, graphweit eindeutige Kennung des fachlichen Veränderungsauftrags |
| `ChangeEvent` | `targetEntityId` | UUID der angeforderten Zielentität, auch wenn ein `CREATED`-Versuch vor der Anlage scheitert |
| `ChangeEvent` | `targetEntityType` | konkreter Typ der angeforderten Zielentität |
| `ChangeEvent` | `requestedRevision` | erwartete positive Ausgangsrevision; bei `CREATED` nicht gesetzt |
| `SyncEvent` | `runId` | unveränderliche, graphweit eindeutige Kennung des abgeschlossenen technischen Laufs |
| `RoleAssignment` | `bootstrapKey` | ausschließlich am initialen Root-Assignment gesetzter Wert `ROOT` |
| `Verification` | `evaluatedResultRevision` | exakt die Revision des über `EVALUATES` verbundenen `Result`, die bewertet wurde |
| `Verification` | `checkedCriterionRevision` | exakt die Revision des über `CHECKS` verbundenen `SuccessCriterion`, die geprüft wurde |
| `HistoricalCorrection` | `baseHistoryViewHash` | SHA-256 des vor der Korrektur erneut gelesenen effektiven historischen Stands |

Neo4j speichert `null` nicht als Property. `requestedRevision` fehlt deshalb genau dann, wenn `changeType = 'CREATED'` gilt. Für alle anderen Veränderungstypen muss die Property vorhanden und eine positive Ganzzahl sein.

Ein historischer Korrekturauftrag verwendet zusätzlich die kanonische Beziehung:

```text
(:ChangeEvent)-[:TARGETS_HISTORY]->(:PiH)
```

Sie benennt das unveränderliche `PiH`, auf das sich der Auftrag bezieht. Sie ersetzt weder `CHANGED_BY` noch `CORRECTS`: Ein `PiH` erhält niemals `CHANGED_BY`; die erst nach erfolgreicher Prüfung erzeugte `HistoricalCorrection` verweist weiterhin über `CORRECTS` auf dasselbe `PiH`.

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

## Atomarer Bootstrap eines leeren Graphen

Der Bootstrap ist die einzige Erzeugung, die noch kein vorhandenes `RoleAssignment` und keine vorher aktive SYNC-Definition verwenden kann. Er ist ausschließlich zulässig, wenn kein Knoten mit dem Label `JCIEntity` existiert. In einer einzigen Transaktion werden eine minimale Organisation, ein technisches Mitglied, seine Rolle, das Root-Assignment und genau eine erste aktive SYNC-Definition erzeugt. Das Root-Assignment ist dauerhaft durch `bootstrapKey = 'ROOT'` gekennzeichnet und bleibt die einzige aktive `JCIEntity` ohne `CREATED_BY`.

Die folgende parametrisierte Abfrage ist ein ausführbares Bootstrap-Beispiel. Sie liefert genau eine Zeile, wenn sie geschrieben hat. Liefert sie null Zeilen, war der Graph nicht leer; der aufrufende Deployment-Schritt muss dies als Fehler behandeln und darf keinen zweiten Bootstrap versuchen.

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
  responsibility: 'Einmalige Initialisierung des JCI-Graphen', status: 'ACTIVE',
  revision: 1, createdAt: now, updatedAt: now
})
CREATE (root:JCIEntity:GraphObject:RoleAssignment {
  id: randomUUID(), entityType: 'RoleAssignment', name: 'JCI Root Assignment',
  bootstrapKey: 'ROOT', validFrom: now, status: 'ACTIVE',
  revision: 1, createdAt: now, updatedAt: now
})
CREATE (definition:JCIEntity:JCIElementInstance:SYNC {
  id: randomUUID(), entityType: 'SYNC', name: 'Initiale JCI-SYNC-Definition',
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

Die Vorbedingung und sämtliche `CREATE`-Anweisungen müssen in derselben Neo4j-Transaktion laufen. Nach dem Commit verhindert das vorhandene Root-`RoleAssignment` mit `bootstrapKey = 'ROOT'` zusammen mit der Leerheitsprüfung einen erneuten Bootstrap. Alle späteren Entitäten einschließlich neuer SYNC-Definitionen werden ausschließlich durch den normalen `ChangeEvent`-/`SyncEvent`-Ablauf erzeugt.

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

### Geschlossener Bootstrap und Erzeugungsverantwortung

Ein initialisierter Graph besitzt genau ein Root-Assignment mit `bootstrapKey = 'ROOT'` und mindestens eine aktive SYNC-Definition. Andere Werte für `bootstrapKey` sind unzulässig. Die folgende Abfrage findet einen fehlenden, mehrfachen oder unvollständigen Bootstrap:

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

Das Root-Assignment ist die einzige zulässige Ausnahme von `CREATED_BY`. Alle anderen fachlichen und dokumentierenden Knoten müssen nach dem atomaren Bootstrap genau einen Erzeugungsakteur besitzen:

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

Ein importierter Knoten im Status `DRAFT` darf vorübergehend noch keinen Erzeugungsakteur besitzen; mehr als eine `CREATED_BY`-Kante ist auch dort unzulässig. Vor der Aktivierung oder dem Abschluss muss genau ein Erzeugungsakteur zugeordnet sein.

**Kurzes Beispiel:** Beim ersten Deployment erzeugt die Bootstrap-Transaktion `JCI Root Assignment` und die initiale SYNC-Definition gemeinsam. Schon der nächste regulär erzeugte fachliche Knoten benötigt `CREATED_BY`; ein zweites Assignment mit `bootstrapKey = 'ROOT'` scheitert am Unique Constraint.

### ChangeEvent-Ziel, Revision und Lebenszyklus

Die Zielangaben am `ChangeEvent` bleiben auch dann erhalten, wenn ein Versuch vor dem Anlegen eines Knotens scheitert. `HISTORICAL_CORRECTION` darf ausschließlich auf `PiH` mit Revision `1` zielen. Alle übrigen Veränderungstypen dürfen ausschließlich historisierbare Typen adressieren.

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

`CHANGED_BY` ist abhängig von der Art und dem Ergebnis des Auftrags. Ein normaler Auftrag besitzt genau eine passende Ausgangsentität. Ein noch nicht erfolgreich abgeschlossenes `CREATED` besitzt keine; nach genau einem erfolgreichen Lauf verweist die neu angelegte Entität darauf. Eine historische Korrektur besitzt statt `CHANGED_BY` genau ein `TARGETS_HISTORY`.

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

Parallele Duplikatkanten dürfen keine Kardinalitätsprüfung durch ein `DISTINCT` auf den Zielknoten umgehen:

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

Bei normalen Änderungen ist das Ziel bereits bei Annahme auflösbar und muss deshalb von jedem abgeschlossenen Lauf über `AFFECTS` genannt werden. Bei `CREATED` gilt dies zwingend für den erfolgreichen Lauf; ein vorher beendeter Fehlversuch darf ohne Zielbezug dokumentiert bleiben:

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

Null abgeschlossene Läufe sind ein zulässiger **pending** Zustand. Jeder beendete technische Lauf wird dagegen genau einmal als neuer, unveränderlicher `SyncEvent` angehängt. Die graphweite Eindeutigkeit von `runId`, `revision = 1`, `status = 'RECORDED'` und `updatedAt = createdAt` schützt das gespeicherte Ergebnis. Ob zu jedem außerhalb des Graphen terminalen `SyncRun` bereits ein Ereignis existiert, muss zusätzlich die technische Run-/Outbox-Reconciliation prüfen; diese Tatsache ist aus Neo4j allein nicht ableitbar.

Unabhängig von der Zahl beendeter Versuche darf ein fachlicher Veränderungsauftrag höchstens einmal erfolgreich übernommen werden:

```cypher
MATCH (change:JCIEntity:GraphObject:ChangeEvent)
WITH change, COUNT {
  MATCH (change)-[:TRIGGERS]
        ->(:JCIEntity:GraphObject:SyncEvent {outcome: 'SUCCESS'})
} AS successfulRunCount
WHERE successfulRunCount > 1
RETURN change.id AS changeEventId, successfulRunCount;
```

Ein erfolgloser Lauf darf weder einen historischen Zustand noch eine historische Korrektur erzeugen:

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

Ein erfolgreicher normaler Änderungsauftrag erzeugt für seine vorhandene Zielentität genau das `PiH` der angeforderten Ausgangsrevision. Weitere tatsächlich geänderte Folgeentitäten dürfen zusätzliche eigene `PiH` erhalten:

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

Ein erfolgreicher historischer Korrekturauftrag erzeugt genau eine Korrektur, deren `CORRECTS` und `CAUSED_BY` auf dasselbe `PiH` beziehungsweise dasselbe `ChangeEvent` zurückführen:

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

Ein erfolgreicher `CREATED`-Lauf muss die neue Entität atomar mit Revision `1` anlegen, über `AFFECTS` nennen und darf für genau diese neue Identität kein `PiH` erzeugen:

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

Die Revision `1` wird in der erfolgreichen Schreibtransaktion vor dem Commit geprüft. Eine spätere zulässige Änderung kann die aktuelle Revision des Zielknotens erhöhen; deshalb darf eine nachgelagerte Bestandsprüfung nicht fälschlich verlangen, dass die Entität für immer bei Revision `1` bleibt.

**Kurzes Beispiel:** Ein Auftrag zum Anlegen eines Tasks besitzt `requestedRevision = null`. Scheitert die Annahme vor der Anlage, bleiben ChangeEvent und abschließendes FAILED-SyncEvent ohne `CHANGED_BY` und dürfen `affectedCount = 0` haben. Bei Erfolg entstehen der Task mit Revision `1`, `Task ──CHANGED_BY──► ChangeEvent` und `SyncEvent ──AFFECTS──► Task`, aber kein PiH dieses neuen Tasks.

**Kurzes Beispiel für eine historische Korrektur:** Ein Auftrag nennt `targetEntityId = <PiH-ID>`, `targetEntityType = 'PiH'` und `requestedRevision = 1`. Das ChangeEvent verweist über `TARGETS_HISTORY` auf dieses PiH, aber das PiH erhält kein `CHANGED_BY`. Erst ein erfolgreicher Lauf erzeugt die `HistoricalCorrection`, deren `CORRECTS` auf genau dasselbe PiH zeigt.

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

Die gebundenen Revisionen müssen als aktueller Zustand oder als genau ein historischer Zustand derselben Entität auflösbar sein. Der Zeitpunkt der Verification muss in das Gültigkeitsintervall dieser Revision fallen:

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

Vor dem Erzeugen einer Verification liest `SYNC` beide aktuellen Revisionen und prüft sie unmittelbar vor dem Commit erneut. Eine spätere Änderung von Result oder Erfolgskriterium verändert die Verification nicht; sie macht sie lediglich für die aktuelle Erfolgsauswertung unanwendbar. Die folgende **Auswahlabfrage** ist deshalb keine Fehlerabfrage. Sie liefert ausschließlich die derzeit anwendbaren, nicht abgelösten Verifications:

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

Die `PiF1o`-Aggregation darf ausschließlich diese anwendbare Menge verwenden. Ist eine gebundene Revision nicht mehr aktuell, ist eine neue Verification erforderlich; sie darf die frühere Verification über `SUPERSEDES` ablösen, ohne deren gespeicherte Revisionsbindung zu verändern.

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

**Kurzes Beispiel:** Eine Verification bindet `Result`-Revision `3` und Kriterienrevision `2`. Wird das Kriterium auf Revision `3` geändert, bleibt die alte Prüfung nachvollziehbar, zählt aber nicht mehr für `ACHIEVED`; erst eine neue Verification mit `checkedCriterionRevision = 3` kann wieder angewendet werden.

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

Eine `HistoricalCorrection` darf höchstens eine ältere Korrektur desselben `PiH` vollständig ablösen und höchstens von einer neueren Korrektur abgelöst werden. Verzweigungen, Zielwechsel und Zyklen sind ungültig:

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

Mehrere nicht abgelöste Korrekturen desselben `PiH` dürfen parallel gelten, wenn ihre `correctedFields` disjunkt sind. Berühren zwei aktuelle Korrekturen denselben Pfad, muss eine die andere vollständig über `SUPERSEDES` ablösen und mindestens deren vollständige Feldmenge übernehmen; andernfalls wäre der effektive historische Stand mehrdeutig.

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

Vor jeder neuen Korrektur liest `SYNC` das `PiH` und alle nicht abgelösten Korrekturen erneut. Der kanonische Hash-Eingang enthält die `historyId`, `PiH.contentHash` sowie die nach Korrektur-ID sortierten IDs, Feldlisten und Werte aller aktuellen Korrekturen. Dadurch ändert sich der View-Hash bei jedem erfolgreichen Ergänzen oder Ablösen, selbst wenn der resultierende Fachwert später wieder einem früheren Wert entspricht. Der Antrag muss genau diesen SHA-256 als `baseHistoryViewHash` nennen.

Die folgende **Auswahlabfrage** liefert den kanonisch zu serialisierenden Ausgangssatz; die SHA-256-Bildung und die Überlagerung der JSON-Werte erfolgen im SYNC-Regelpaket:

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

Unmittelbar vor dem Commit berechnet `SYNC` den Hash erneut und vergleicht ihn mit `baseHistoryViewHash`. Die SYNC-Schreibschicht serialisiert Korrekturtransaktionen anhand der Ziel-`PiH.id`: Nur der erste Schreibversuch auf derselben Basissicht kann committen; jeder weitere Versuch liest danach den inzwischen geänderten historischen Stand und endet bei unverändertem Auftrag mit `CONFLICT`. `baseHistoryViewHash` ist bewusst nicht graphweit eindeutig, weil unterschiedliche `PiH` dieselbe wirksame Sicht besitzen können. Die Serialisierung und Vor-Commit-Prüfung sind nicht durch eine nachträgliche reine Cypher-Abfrage ersetzbar, weil Neo4j die kanonischen JSON-Werte bewusst nur als Zeichenketten speichert.

**Kurzes Beispiel:** Eine aktuelle Korrektur ergänzt `/relationshipData/HAS_MEMBER:OUT:team-7/validUntil`. Eine zweite aktuelle Korrektur darf gleichzeitig `/stateData/name` berichtigen. Will sie ebenfalls denselben `validUntil`-Pfad ändern, muss sie die erste Korrektur über `SUPERSEDES` ablösen und auf dem unmittelbar zuvor neu berechneten `baseHistoryViewHash` beruhen.

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

`AFFECTS` ist damit ergebnisabhängig: Ein Lauf mit `SUCCESS` oder `CONFLICT` nennt mindestens eine betroffene `JCIEntity`. Nur ein früh vor der Zielauflösung beendeter `FAILED`-Lauf darf null Ziele und `affectedCount = 0` dokumentieren. Sobald ein Ziel tatsächlich ermittelt wurde, muss es auch bei einem fehlgeschlagenen Lauf über `AFFECTS` gespeichert und mitgezählt werden.

**Kurzes Beispiel:** Zwei technische Wiederholungen desselben Auftrags besitzen dasselbe auslösende `ChangeEvent`, aber verschiedene `runId` und zwei getrennte `SyncEvent`-Knoten. Nur ein erfolgreicher Versuch darf die Fachänderung übernehmen; beide Ereignisse bleiben append-only nachvollziehbar.

`affectedCount`, `historyCount`, `correctionCount` und `conflictCount` sind aus den gespeicherten Beziehungen vollständig nachprüfbar. `changedCount` bezeichnet dagegen die Anzahl der in derselben Transaktion tatsächlich übernommenen fachlichen Zieländerungen. Da das Modell dafür bewusst keine zusätzliche `CHANGES`-Beziehung speichert, berechnet `SYNC` diesen Wert aus dem deduplizierten Transaktions-Write-Set unmittelbar vor dem Commit. Jede darin enthaltene bestehende veränderliche `JCIEntity` muss genau eine Revisionserhöhung und genau ein zugehöriges `PiH` erhalten. Eine durch den Veränderungsauftrag neu angelegte fachliche Zielentität zählt als übernommene Änderung, erhält aber noch kein `PiH`. Neu erzeugte Prozess- und Dokumentationsobjekte wie `PiH`, `SyncEvent`, `HistoricalCorrection` oder ein durch `SYNC` dokumentierter `RaNConflict` zählen nicht zu `changedCount`. Bei `CONFLICT` oder `FAILED` zählen zurückgerollte Schreiboperationen ebenfalls nicht. Der berechnete Wert wird zusammen mit dem Graphzustand und dem abschließenden `SyncEvent` atomar übernommen.

## Transaktionsregel für SYNC

`SYNC` prüft Hierarchie, Abhängigkeiten, Task-Typregeln sowie anwendbare `RaN` vor der Übernahme. Abgeleitete Task-Status werden von den atomaren Tasks über die Parent-Kette nach oben und erst danach zu den betroffenen `PiF1o` aggregiert. Aktuelle Zustände, erforderliche `PiH`, neue oder aufgelöste `RaNConflict`-Objekte, Beziehungen, das deduplizierte Transaktions-Write-Set und das abschließende `SyncEvent` werden atomar übernommen. Vor dem Commit werden alle fünf Zählwerte aus diesem Write-Set und den zu speichernden Beziehungen berechnet. Ein Konflikt oder Fehler darf keinen teilweise aktualisierten Graphen hinterlassen.

Zusätzlich gilt für die präzisierten Vorgänge: Ein `CREATED`-Ziel wird mit Revision `1`, seiner `CHANGED_BY`-Kante und dem abschließenden erfolgreichen Ereignis atomar erzeugt. Vor dem Speichern einer Verification werden beide gebundenen Revisionen erneut mit den aktuellen Zielrevisionen verglichen. Vor einer HistoricalCorrection werden Ziel-PiH, aktuelle Korrekturmenge und `baseHistoryViewHash` innerhalb derselben Transaktion erneut geprüft; erst danach werden `HistoricalCorrection`, `CORRECTS`, `CAUSED_BY` und `CREATES_CORRECTION` gemeinsam angelegt. `SyncEvent`-Knoten werden niemals aktualisiert oder für einen neuen Lauf wiederverwendet, sondern je `runId` ausschließlich neu angehängt.

## Grenzen der deklarativen Durchsetzung

Neo4j-Constraints und nachgelagerte Cypher-Abfragen decken den gespeicherten Graphzustand ab, können aber vier Laufzeiteigenschaften nicht allein garantieren:

1. Ein außerhalb des Graphen beendeter `SyncRun` ist erst nach Abgleich mit dem technischen Run-/Outbox-Protokoll als fehlendes `SyncEvent` erkennbar.
2. Das Verbot späterer Änderungen oder Löschungen unveränderlicher Knoten und ihrer Beziehungen benötigt eingeschränkte Schreibrollen beziehungsweise ausschließlich freigegebene SYNC-Schreibtransaktionen; ein Property Constraint ist kein Append-only-Mechanismus.
3. Die kanonische Überlagerung von `stateDataJson`, `relationshipDataJson` und Korrekturwerten sowie die SHA-256-Bildung erfolgen im versionierten SYNC-Regelpaket. Cypher validiert Struktur, Eindeutigkeit und gespeicherte Hashform, nicht die JSON-Semantik selbst.
4. Die Revision `1` eines neu erzeugten Ziels und die unmittelbar vor dem Commit erneut geprüften Verification- und History-Revisionen sind Transaktionsvorbedingungen. Ein späterer Snapshot des inzwischen weiterentwickelten Graphen kann diese zeitliche Tatsache nur anhand der vollständig gespeicherten Historie nachvollziehen.

## Migration und Versionsführung

Schemaänderungen werden als vorwärts gerichtete, unveränderliche Migrationen mit aufsteigender Nummer gespeichert. Jede Migration enthält:

1. erwartete Ausgangsversion,
2. Vorabvalidierungen,
3. Constraints, Indizes und notwendige Datenanpassungen,
4. Nachvalidierungen,
5. neue Zielversion.

Vor einer Migration wird eine wiederherstellbare Datenbanksicherung erzeugt. Eine Migration wird nur abgeschlossen, wenn alle Nachvalidierungen null Fehler liefern. Die aktive `SYNC.definition` nennt die dazu passende Ontologie-, Graphregel- und Schemazielversion; eine inkompatible Kombination darf nicht aktiviert werden.

Für die in diesem Dokument präzisierten Felder gilt folgende migrationsverträgliche Reihenfolge:

1. Neue Properties zunächst ohne Existenz- oder Unique Constraint schreiben und sämtliche Altbestände klassifizieren.
2. `ChangeEvent.targetEntityId`, `targetEntityType` und `requestedRevision` aus der eindeutigen `CHANGED_BY`-Quelle beziehungsweise bei historischen Korrekturen aus `CORRECTS` und `CAUSED_BY` ableiten. Fehlgeschlagene alte Aufträge ohne Zielkante dürfen nur aus einem unveränderten Request-Nachweis ergänzt werden.
3. `SyncEvent.runId` ausschließlich aus dem technischen Run-/Outbox-Protokoll übernehmen. Eine neue Zufalls-ID würde die historische Laufidentität verfälschen und ist deshalb kein zulässiger Backfill.
4. Revisionsbindungen vorhandener Verifications anhand `verifiedAt`, aktueller Revision und eindeutiger `PiH`-Gültigkeitsintervalle bestimmen. Null oder mehrere Kandidaten stoppen die Migration.
5. Ein Root-Assignment nur dann mit `bootstrapKey = 'ROOT'` markieren, wenn es und seine initiale SYNC-Definition eindeutig nachgewiesen sind. Ein mehrdeutiger nichtleerer Altbestand wird nicht automatisch zum geschlossenen Bootstrap umgedeutet.
6. Für vorhandene HistoricalCorrections den damaligen `baseHistoryViewHash` nur bei vollständig rekonstruierbarer Korrekturfolge bilden. Überlappende nicht abgelöste Feldkorrekturen erfordern vorher eine fachliche Auflösung.
7. Erst nach erfolgreichem Backfill alle Existenz-, Typ- und Eindeutigkeitsconstraints anlegen und sämtliche Abfragen erneut ausführen.

Bei einer noch vollständig leeren Datenbank entfallen die Backfills. Dort werden zuerst die Constraints und anschließend genau einmal die atomare Bootstrap-Transaktion ausgeführt. Diese Dokumentänderung führt selbst keine Migration und keinen Bootstrap gegen eine Live-Datenbank aus.

**Kurzes Beispiel:** Migration `V002` ergänzt `REPLACED_BY`. Sie prüft zuerst alle vorhandenen `REPLACED`-Entitäten, legt benötigte Nachfolgekanten innerhalb einer kontrollierten Datenmigration an und aktiviert den neuen Constraint erst, wenn keine ersetzte Entität ohne Nachfolger verbleibt.

## Abgrenzung der Mandantentrennung

`RoFOrg` ist eine fachliche Organisation im JCI-Graphen und kein technischer Mandantenschlüssel. Mehrere Organisationen dürfen bewusst in einem gemeinsamen Modellgraphen verbunden sein. Technische Datenbank-, Zugriffs- oder Deployment-Isolation wird außerhalb der JCI-Ontologie umgesetzt und darf die fachlichen Organisationsbeziehungen nicht verändern.

## Automatisierte Prüfung

Die technologieunabhängigen Invarianten werden zusätzlich durch `tests/test_model_rules.py` geprüft. `tests/test_spec_consistency.py` stellt sicher, dass Entitäts- und Beziehungskatalog, strukturierte Datentypen sowie die Folgedokumente synchron bleiben. GitHub Actions führt beide Tests bei jedem Push auf `main` und bei jedem Pull Request aus.

Die Cypher-Abfragen dieses Dokuments bleiben für eine reale Neo4j-Instanz zusätzlich verpflichtend. Jede Validierungsabfrage muss nach Migration und fachlicher Transaktion null Zeilen liefern.
