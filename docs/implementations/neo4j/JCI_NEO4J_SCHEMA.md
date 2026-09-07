# JCI-Neo4j-Schema

## Status und Zweck

Dieses Dokument konkretisiert die technische Abbildung des JCI-Modells in Neo4j. Es implementiert [`JCI_CONTEXT.md`](../../JCI_CONTEXT.md), [`JCI_ONTOLOGY.md`](../../JCI_ONTOLOGY.md), [`JCI_GRAPH_RULES.md`](../../JCI_GRAPH_RULES.md) und [`JCI_SYNC_SPEC.md`](../../JCI_SYNC_SPEC.md). Bei einem Konflikt gilt die fachliche Spezifikation; das Schema darf ihre Semantik nicht verändern.

## Regel- und Snapshotprofil 2.0

Neue SYNC-Vorgänge verwenden Regelpaket, Ontologie, Graphregeln, SYNC-Spezifikation, snapshotSchemaVersion, valueSchemaVersion und AustauschschemaVersion 2.0. JSON-LD bleibt 1.1; die bestehenden Namespace-IRIs /1.0# sind Identitäten und keine Regelversion. Alte Profile werden ausdrücklich über ihre Resolver gelesen. Bestehende PiH, HistoricalCorrections, SyncEvents und Hashes werden nicht nachträglich umgeschrieben oder neu berechnet.

Die Revision gehört zum fachlichen Zustand nach der Endpunkt-Eigentumsmatrix in Abschnitt 2.2.8 von [`JCI_CONTEXT.md`](../../JCI_CONTEXT.md). Neue Prüf-, Ereignis- und Korrekturbezüge revisionieren nicht ihre Referenzziele. TRIGGERS, CHANGED_BY, HAS_HISTORICAL_STATE und neue CREATED_BY-Bezüge erzeugen keine Historisierungsschleifen. Ein zulässiges Nachtragen von CREATED_BY am Importentwurf ändert dessen Zustand; RaNConflict-Auflösung nur den Konflikt. PROVIDES_CONTEXT_TO gehört dem CiV-Kontext. Übrige katalogisierte Strukturbeziehungen ändern beide veränderlichen Eigentümer. Neue PiH projizieren nur den ihnen zugeordneten revisionierten Beziehungszustand. Revisionsneutrale Bezüge unterliegen dennoch vollständig Gate/graphEpoch und ihren eigenen unveränderlichen Provenienzregeln.

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

CREATE CONSTRAINT civ_not_dimension_exists IF NOT EXISTS
FOR (v:CiV) REQUIRE v.notCiV IS NOT NULL;

CREATE CONSTRAINT civ_self_dimension_exists IF NOT EXISTS
FOR (v:CiV) REQUIRE v.selfCiV IS NOT NULL;

CREATE CONSTRAINT civ_to_serve_dimension_exists IF NOT EXISTS
FOR (v:CiV) REQUIRE v.toServeCiV IS NOT NULL;
```

Die global eindeutige `JCIEntity.id` macht zusätzliche ID-Constraints je konkretem Label technisch redundant. Spezifische Constraints werden nur für fachlich weitere eindeutige Schlüssel angelegt.

### Komplexe strukturierte Werte

Neo4j-Properties speichern keine verschachtelten JSON-Objekte. Die kanonischen Strukturen aus [`JCI_CONTEXT.md`](../../JCI_CONTEXT.md) werden deshalb ohne Semantikverlust als kanonische JSON-Zeichenketten projiziert:

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

| Knoten                 | Property                   | Bedeutung                                                                                    |
| ---------------------- | -------------------------- | -------------------------------------------------------------------------------------------- |
| `ChangeEvent`          | `idempotencyKey`           | unveränderliche, graphweit eindeutige Kennung des fachlichen Veränderungsauftrags            |
| `ChangeEvent`          | `targetEntityId`           | UUID der angeforderten Zielentität, auch wenn ein `CREATED`-Versuch vor der Anlage scheitert |
| `ChangeEvent`          | `targetEntityType`         | konkreter Typ der angeforderten Zielentität                                                  |
| `ChangeEvent`          | `requestedRevision`        | erwartete positive Ausgangsrevision; bei `CREATED` nicht gesetzt                             |
| `SyncEvent`            | `runId`                    | unveränderliche, graphweit eindeutige Kennung des abgeschlossenen technischen Laufs          |
| `RoleAssignment`       | `bootstrapKey`             | ausschließlich am initialen Root-Assignment gesetzter Wert `ROOT`                            |
| `Verification`         | `evaluatedResultRevision`  | exakt die Revision des über `EVALUATES` verbundenen `Result`, die bewertet wurde             |
| `Verification`         | `checkedCriterionRevision` | exakt die Revision des über `CHECKS` verbundenen `SuccessCriterion`, die geprüft wurde       |
| `HistoricalCorrection` | `baseHistoryViewHash`      | SHA-256 des vor der Korrektur erneut gelesenen effektiven historischen Stands                |

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

## Technische Schreibsperre

Die folgenden technischen Labels sind keine JCIEntity, GraphObject oder zusätzliche fachliche Typen und werden nicht als JCI-Ontologie exportiert. Genau ein Gate schützt den gesamten gemeinsamen JCI-Datenbankbestand, einschließlich aller RoFOrg und fachlich revisionsneutraler Auditappend-Transaktionen. Technische Request-/Runbelege enthalten den vollständigen unveränderlichen Request, Run-Besitz/Fencing, verwendete SYNC-Revision/Prüfsumme und Entscheidungsausgang. Erfolgsbelege existieren höchstens einmal je Auftrag; Outboxeinträge verweisen auf genau ein Abschlussereignis.

```cypher
CREATE CONSTRAINT jci_technical_gate_key_unique IF NOT EXISTS
FOR (gate:JCITechnicalGate) REQUIRE gate.key IS UNIQUE;
CREATE CONSTRAINT jci_technical_request_key_unique IF NOT EXISTS
FOR (request:JCITechnicalRequest) REQUIRE request.idempotencyKey IS UNIQUE;
CREATE CONSTRAINT jci_technical_run_id_unique IF NOT EXISTS
FOR (run:JCITechnicalRun) REQUIRE run.runId IS UNIQUE;
CREATE CONSTRAINT jci_technical_commit_request_unique IF NOT EXISTS
FOR (commit:JCITechnicalCommit) REQUIRE commit.idempotencyKey IS UNIQUE;
CREATE CONSTRAINT jci_technical_commit_run_unique IF NOT EXISTS
FOR (commit:JCITechnicalCommit) REQUIRE commit.runId IS UNIQUE;
CREATE CONSTRAINT jci_technical_outbox_event_unique IF NOT EXISTS
FOR (entry:JCITechnicalOutbox) REQUIRE entry.eventId IS UNIQUE;
```

```cypher
MERGE (gate:JCITechnicalGate {key: 'MODEL_WRITE'})
ON CREATE SET gate.graphEpoch = 0;
```

Die Gate-Initialisierung ist ein kontrollierter technischer Installationsschritt vor dem fachlichen Bootstrap; sie erzeugt keine JCIEntity. Jeder reguläre Schreibvorgang erwartet das vorhandene Gate und scheitert bei Fehlen. Er nimmt den Lock in einer expliziten Transaktion vor jeder maßgeblichen Lesesicht. Der Lock wird durch Commit/Rollback freigegeben; reine technische Lockberührung ändert keine Fachrevision und keine graphEpoch.

```cypher
MATCH (gate:JCITechnicalGate {key: 'MODEL_WRITE'})
SET gate._lock = true
REMOVE gate._lock
RETURN gate.graphEpoch AS graphEpoch;
```

Jede tatsächlich übernommene JCI-Schreibtransaktion erhöht graphEpoch genau einmal, einschließlich Annahme, Korrekturen, SUPERSEDES und FAILED-/CONFLICT-Abschlussdokumentation. Heartbeats dürfen technisch separat laufen; sie dürfen keinen Run-Besitz oder Commit-Ausgang verändern. Besitzwechsel und Finalisierung verwenden dieselbe gesicherte Reihenfolge. Direkte JCI-Schreibwege, die das Gate umgehen, sind nicht zulässig.

Neo4j verwendet standardmäßig Read Committed. Der dokumentierte SET-/REMOVE-Schreiblock bleibt bis Commit oder Rollback bestehen ([Neo4j-Locking](https://neo4j.com/docs/operations-manual/current/database-internals/concurrent-data-access/)). Die Referenz verwendet eine explizite [Driver-Transaktion](https://neo4j.com/docs/python-manual/current/transactions/).

## Atomarer Bootstrap eines leeren Graphen

Der Bootstrap ist die einzige Erzeugung, die noch kein vorhandenes `RoleAssignment` und keine vorher aktive SYNC-Definition verwenden kann. Er ist ausschließlich zulässig, wenn kein Knoten mit dem Label `JCIEntity` existiert. In einer einzigen Transaktion werden eine minimale Organisation, ein technisches Mitglied, seine Rolle, das Root-Assignment und genau eine erste aktive SYNC-Definition erzeugt. Das Root-Assignment ist dauerhaft durch `bootstrapKey = 'ROOT'` gekennzeichnet und bleibt die einzige aktive `JCIEntity` ohne `CREATED_BY`.

Die folgende parametrisierte Abfrage ist ein ausführbares Bootstrap-Beispiel. Sie liefert genau eine Zeile, wenn sie geschrieben hat. Liefert sie null Zeilen, war der Graph nicht leer; der aufrufende Deployment-Schritt muss dies als Fehler behandeln und darf keinen zweiten Bootstrap versuchen.

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
SET gate.graphEpoch = gate.graphEpoch + 1
RETURN root.id AS rootRoleAssignmentId, definition.id AS initialSyncDefinitionId;
```

Die Vorbedingung und sämtliche `CREATE`-Anweisungen müssen in derselben Neo4j-Transaktion laufen. Nach dem Commit verhindert das vorhandene Root-`RoleAssignment` mit `bootstrapKey = 'ROOT'` zusammen mit der Leerheitsprüfung einen erneuten Bootstrap. Alle späteren Entitäten einschließlich neuer SYNC-Definitionen werden ausschließlich durch den normalen `ChangeEvent`-/`SyncEvent`-Ablauf erzeugt.

Neo4j-Constraints erzwingen Enum-Werte, Kardinalitäten und graphweite Zyklusregeln nicht vollständig. Diese Regeln werden vor dem Schreiben durch `SYNC` und nach dem Schreiben durch Validierungsabfragen geprüft.

## Validierungsabfragen

Jede folgende Abfrage muss für einen gültigen Graphen null Zeilen liefern.

### CiV-Dimensionen, Werteträger und PiF2-Scope

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

Diese Abfragen prüfen Struktur, nicht die fachliche Entscheidung selbst. `SYNC` darf `INFORMED_BY` oder Wertdimensionen nicht aus Namen, Mitgliedschaften oder Organisationszugehörigkeiten ableiten. Ein bestehendes gebündeltes CiV mit `purpose`, `values` oder `scope` wird nicht automatisch migriert: Die Liste muss in einzelne CiV aufgeteilt, jede Dreidimensionalität menschlich bestätigt und alle Beziehungen kontrolliert neu verbunden werden.

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
       (executorCount > 0 OR environmentCount > 0 OR resultCount > 0))
   OR (t.taskKind = 'COMPOSITE' AND NOT t.status IN ['REPLACED','REVOKED']
       AND NOT EXISTS {
         MATCH (t)-[:DECOMPOSES_INTO]->(currentChild:Task)
         WHERE NOT currentChild.status IN ['REPLACED','REVOKED']
       })
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

### Nicht erfüllte Abhängigkeit ohne BLOCKED

```cypher
MATCH (t:Task)-[:DEPENDS_ON]->(required:Task)
WHERE t.status IN ['ACTIVE','BLOCKED','COMPLETED']
  AND required.status <> 'COMPLETED' AND t.status <> 'BLOCKED'
RETURN t.id AS taskId, required.id AS unmetDependencyId, t.status AS actualStatus;
```

Nicht freigegebene DRAFT-Tasks werden von dieser Bestandsprüfung auf Blockade ausgenommen. Ausdrückliche Freigabe und ihr Ausgangsstatus ACTIVE/BLOCKED folgen kanonischem Abschnitt 9.4.2 einschließlich aggregierter Kinderblockade. Ein gerade freigegebener Composite mit ausschließlich abgeschlossenen Kindern bleibt zunächst ACTIVE; seine Unterscheidung vom späteren Abschlussübergang benötigt den Ausgangszustand im Transaktionsadapter.

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

Ein erfolgreicher normaler Auftrag erzeugt für seine Zielentität genau ein PiH nur bei tatsächlicher Änderung ihres zugeordneten Zustands. Ein fachlicher No-op erzeugt keines. Diese Bestandsabfrage findet Duplikate; die exakte Übereinstimmung mit dem deduplizierten Transaktions-Write-Set wird unter der Sperre vor Übernahme geprüft:

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

Ein aktives RaN schützt mindestens ein CiV und ein PiF2 und regelt mindestens ein konkretes Umsetzungselement. Die folgenden Abfragen prüfen Zieltypen, Mindestkardinalitäten und die CiV-PiF2-Kohärenz. Die organisatorische Scope-Kompatibilität über zeitabhängige Mitgliedschaften und WHY-Pfade prüft das versionierte SYNC-Regelpaket.

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

Profil 2.0 erlaubt nur vollständige TypedValue-Eigenschaften unter /stateData/properties/<property>, vollständige historische Beziehungseinträge unter /relationshipData/<key> sowie deren /properties/<property>. Der stabile Schlüssel lautet direction + ":" + relationshipType + ":" + canonicalUUID(otherEntityId). Die gespeicherte relationshipData-Liste bleibt erhalten; der Resolver bildet nur zur Adressierung eine Map und weist doppelte Schlüssel ab. Identität und Originalrevision dürfen nicht umgedeutet werden.

Die folgenden 2.0-Abfragen prüfen Adressform und Segmentpräfix-Überlappung. JSON-Pointer werden vor dem Vergleich in Segmente zerlegt und ~1/~0 dekodiert. Gleichheit und echter Vorfahrenbezug zählen als Überlappung; name und nameLong bleiben disjunkt. Alte Profile werden nicht mit dieser neuen Grammatik umgedeutet. Zulässige Properties, vollständige TypedValues, kanonisches Re-Encoding, Existenz und gemischte Profilmengen prüft der versionierte Resolver unter der Schreibsperre.

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

Ohne Überlappung darf eine neue Korrektur parallel bestehen. Bei genau einer betroffenen aktiven Korrektur muss sie genau diese vollständig über SUPERSEDES ablösen und alle bisherigen kanonischen Pfade samt weiterhin gültigen Werten enthalten. Zusätzliche Pfade dürfen weder innerhalb der neuen Korrektur noch mit anderen aktiven Korrekturen überlappen. Mehrfache Überlappung oder impliziter Wechsel zwischen ganzer Beziehung und Propertykorrektur erzeugt CONFLICT.

ADDITION verlangt tatsächliches Fehlen; ein vorhandener NULL-Wert ist nicht fehlend. CORRECTION und CLARIFICATION benötigen einen vorhandenen Pfad. previousValue wird beim Commit gegen die damalige wirksame Sicht geprüft. Beim späteren Wiederaufbau werden die correctedValue-Werte der nicht abgelösten Korrekturen als absolute Überlagerung des unveränderten PiH verwendet; previousValue wird dabei nicht erneut gegen das Original geprüft. Dadurch bleibt die Korrektur einer zuvor hinzugefügten Angabe nach Ablösung ihrer Ergänzung wirksam.

Die folgende Auswahlabfrage liefert Eingaben für den Resolver, nicht den Hash-Eingang selbst. HistoryView 2.0 ist ausschließlich die wirksame Kombination {stateData, relationshipData}; ihre Beziehungsliste wird nach relationshipType, direction und otherEntityId sortiert. SHA-256 wird über deren kanonische Serialisierung berechnet, ohne historyId, Korrektur-IDs oder technische Adressmap. expectedHistoryViewHash im Request wird mit dieser Sicht verglichen und bei Erfolg unverändert als baseHistoryViewHash gespeichert.

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

Profil 2.0 verwendet UTF-8 ohne BOM/zusätzliche Leerzeichen, Unicode-Codepoint-Schlüsselsortierung und JSON-String-Escaping ohne pauschales ASCII-Escaping. INTEGER bleibt exakt/unbeschränkt; Fließkommazahlen sind auch innerhalb OBJECT/ARRAY verboten. DECIMAL ist eine normalisierte Dezimalzeichenkette ohne Exponent oder unnötige Nullen; verschachtelte Dezimalwerte sind TypedValue DECIMAL. Maßgeblich sind Abschnitt 2.2.9 von [`JCI_CONTEXT.md`](../../JCI_CONTEXT.md) und gemeinsame Hash-Testvektoren.

Alle Korrekturen werden unter dem gemeinsamen Gate aus dem Transaktionsabschnitt geprüft und übernommen. Unmittelbar vor Commit werden Hash, alte Werte, Existenz, Pfade und aktive Korrekturmenge erneut geprüft. Alte Profile benötigen explizite Resolver; unklare Pfade stoppen den neuen Vorgang. Bestehende PiH, Korrekturen und ihre Hashes werden weder neu berechnet noch überschrieben. Der View-Hash ist kein technischer ABA-Schutz: Eine spätere identische wirksame Sicht hat denselben Hash; konkurrierende Bezüge schützt Gate/graphEpoch.

**Kurzes Beispiel:** /stateData/properties/name ist eine vollständige Eigenschaft. /relationshipData/INCOMING:HAS_MEMBER:<Team-UUID> überlappt mit seiner /properties/validUntil. Beide dürfen nicht als getrennte aktive Korrekturen gelten.

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

Der gesamte Kandidat wird unter dem Gate mit aktuellen Mengen geprüft: Task-/Kriterienbeiträge schließen REPLACED und REVOKED aus, Pflichtmengen bleiben nicht leer, Ergebnisse müssen aus aktuellen Tasks stammen. Gemischte Abschlusszyklen werden über DECOMPOSES_INTO und DEPENDS_ON gemeinsam geprüft. Danach erfolgt Auswertung mit Voraussetzungen zuerst, Composite-eigene Voraussetzungen vor der Kindaggregation und kein Rücksprung freigegebener Composites zu DRAFT. Reine Umfangsverkleinerung gibt einen Entwurf nicht frei; DRAFT → COMPLETED bleibt ausgeschlossen. Diese Übergangsvorbedingungen benötigt der Ausgangszustand: Eine reine nachgelagerte Bestandsabfrage ersetzt sie nicht.

Gelesen werden auch negative Mengen und Abhängigkeiten, etwa noch nicht vorhandene RaN, Rollen-/Scopezuordnung und die aktuelle nicht abgelöste Prüfungsmenge. Ein Vergleich allein der Fachrevisionen genügt nicht. Alle Validierungen beziehen sich auf den vollständigen Kandidaten einschließlich aller neuen Kanten und tatsächlichen Folgeänderungen.

Das folgende Driver-Beispiel zeigt die verbindliche Transaktionsgrenze. rules bezeichnet die expliziten Adapter des versionierten geprüften Regelpakets, keine verfügbaren Neo4j-Builtins: read_complete_state muss die vollständige relevante Lesesicht liefern, evaluate_complete_candidate alle Modell-, Zeit-, Pfad- und RaN-Regeln prüfen; apply_owned_domain_delta darf ausschließlich das deduplizierte zugeordnete Fachdelta schreiben. append_success_bundle schreibt in derselben Transaktion PiH, Provenienz, SyncEvent, unveränderlichen Erfolgsbeleg und Outbox. validate_persisted_bundle prüft alle Zähler und Abfragen gegen diesen vollständigen Zustand. Keine Funktion darf eine eigene Transaktion öffnen oder externe Nebenwirkungen auslösen.

```python
def commit_reference(session, request_id, run_id, fencing_token, rules):
    with session.begin_transaction() as tx:
        gate = tx.run(
            "MATCH (g:JCITechnicalGate {key: 'MODEL_WRITE'}) "
            "SET g._lock = true REMOVE g._lock "
            "RETURN g.graphEpoch AS graphEpoch"
        ).single(strict=True)
        request = rules.load_immutable_request(tx, request_id)
        rules.assert_run_owner(tx, run_id, fencing_token)
        previous = rules.find_success(tx, request.idempotency_key)
        if previous is not None:
            return previous
        state = rules.read_complete_state(tx)
        rules.assert_requested_revision(state, request)
        decision_at = tx.run(
            "RETURN datetime.realtime() AS decisionAt"
        ).single(strict=True)["decisionAt"]
        proposal = rules.evaluate_complete_candidate(
            state, request, decision_at=decision_at
        )
        rules.assert_valid(proposal)
        rules.apply_owned_domain_delta(tx, proposal)
        result = rules.append_success_bundle(
            tx, proposal, request, run_id, decision_at,
            graph_epoch=gate["graphEpoch"] + 1,
        )
        rules.validate_persisted_bundle(tx, proposal, result)
        tx.run(
            "MATCH (g:JCITechnicalGate {key: 'MODEL_WRITE'}) "
            "SET g.graphEpoch = g.graphEpoch + 1"
        ).consume()
        tx.commit()
        return result
```

Der technische Commitbeleg speichert decisionAt, tatsächlich verwendete SYNC-Revision/Paketprüfsumme, den deduplizierten geänderten Eigentümersatz und die bei Prüfung gelesenen Revisionen. Ein CREATE-Ziel startet mit Revision 1, erhält aber kein PiH; jede tatsächlich geänderte bestehende Entität genau eine Revisionserhöhung und ein PiH. Reine Auditbezüge und neue Prozessobjekte zählen nicht zum fachlichen Write-Set. Ein No-op hat changedCount = historyCount = 0 und trotzdem genau einen Erfolgsbeleg. Alle fünf Zählwerte werden vor Commit aus Write-Set und Beziehungen berechnet.

Bei Validierungskonflikt oder technischem Fehler wird die Fachtransaktion zurückgerollt; Abschlussdokumentation wird danach unter demselben Gate angelegt. Ein unerreichbarer Datenbankdienst hinterlässt eine Nachholpflicht am dauerhaften Runbeleg. Bei unbekanntem Commit-Ausgang zuerst unter dem Gate das Ergebnis derselben runId prüfen; ein bereits gespeicherter Erfolg wird nicht wiederholt. Ein veralteter Fencing-Token darf keinen Abschluss schreiben. Eine neue Ausgangsrevision benötigt einen neuen Auftrag; requestedRevision bleibt unverändert.

Alle zeitabhängigen Entscheidungen werden für einen festen serverseitigen decisionAt nach Lock-Erwerb abschließend neu ausgewertet. completedAt bleibt Abschlusszeit. Der Vertrag garantiert Fachgültigkeit an decisionAt, nicht an der späteren physischen Commit-Bestätigung oder bei externen Aktionen. Eine neue gültige Regel durch reinen Zeitablauf wird auch ohne neue Fachrevision berücksichtigt. Spätere Optimierung darf eine unter dem Gate gelesene graphEpoch nach externer Berechnung unter erneut erworbenem Gate vergleichen; bei Abweichung neu lesen und vorbereiten, Zeitbedingungen immer erneut auswerten.

Outboxzustellung erfolgt erst nach Commit. Nach Dispatcher-Absturz darf erneut zugestellt werden; Empfänger müssen anhand der stabilen Ereigniskennung deduplizieren. Die Outbox allein garantiert keine einmalige externe Wirkung.

## Grenzen der deklarativen Durchsetzung

Neo4j-Constraints und nachgelagerte Cypher-Abfragen decken den gespeicherten Graphzustand ab, können aber vier Laufzeiteigenschaften nicht allein garantieren:

1. Ein außerhalb des Graphen beendeter `SyncRun` ist erst nach Abgleich mit dem technischen Run-/Outbox-Protokoll als fehlendes `SyncEvent` erkennbar.
2. Das Verbot späterer Änderungen oder Löschungen unveränderlicher Knoten und der ihnen zugeordneten eigenen Beziehungen benötigt eingeschränkte Schreibrollen beziehungsweise ausschließlich freigegebene SYNC-Schreibtransaktionen; ein Property Constraint ist kein Append-only-Mechanismus.
3. Die kanonische Überlagerung von `stateDataJson`, `relationshipDataJson` und Korrekturwerten sowie die SHA-256-Bildung erfolgen im versionierten SYNC-Regelpaket. Cypher validiert Struktur, Eindeutigkeit und gespeicherte Hashform, nicht die JSON-Semantik selbst.
4. Die Revision `1` eines neu erzeugten Ziels und die unmittelbar vor dem Commit erneut geprüften Verification- und History-Revisionen sind Transaktionsvorbedingungen. Ein späterer Snapshot des inzwischen weiterentwickelten Graphen kann diese zeitliche Tatsache nur anhand der vollständig gespeicherten Historie nachvollziehen.

## Migration und Versionsführung

Änderungen werden als vorwärts gerichtete, unveränderliche Migrationen mit Ausgangs-/Zielversion, Vorvalidierung, technischem Schema, Nachvalidierung und wiederherstellbarer Sicherung geführt. Diese Dokumentänderung führt selbst keine Migration, keinen Bootstrap und keine Live-Datenbankaktion aus.

1. Altprofile und ihre benötigten Resolver inventarisieren. Bestehende unveränderliche Dokumente, Snapshotdaten und Hashes bleiben unverändert; keine Zufalls-Backfills historischer Run-IDs, Revisionen oder Prüfsummen.
2. Die neuen technischen Gate-/Request-/Run-/Commit-/Outbox-Strukturen kontrolliert initialisieren. Sämtliche Schreibwege einschließlich Import und Nachholung auf denselben Gate verpflichten.
3. Neue SYNC-Definition mit Regel-, Ontologie-, Graphregel-, SyncSpec-, Snapshot-, Korrektur- und Austauschprofil 2.0 erst aktivieren, wenn alle vorhandenen Typen und Legacy-Leseprofile ausdrücklich unterstützt werden und die Paketprüfsumme stimmt. Namespace-Identitäten und JSON-LD1.1 bleiben unverändert.
4. Alle bestehenden Task-/Kriterienumfänge, Ersatzzuordnungen, aktuellen Parent-Strukturen, Composite-Status und gemischten Abschlusszyklen vorprüfen. Leere aktive Umfänge oder unklare Teilbäume erfordern begründete fachliche Aufträge; keine automatische Aufhebung, Umleitung oder Wiederöffnung terminaler Tatsachen.
5. Neue PiH nach Revisionseigentum und Snapshotprofil 2.0 bilden. Alte PiH behalten ihr ursprüngliches Profil; gespeicherte Beziehungssnapshots werden nicht rückwirkend gefiltert oder re-gehasht.
6. Historische Korrekturen über den expliziten Resolver ihres Profils lesen. Unklare Adressen, kollidierende Beziehungsschlüssel oder überlappende aktive Altkorrekturen stoppen den Übergang für den betroffenen Bestand. Ein neuer 2.0-Vorgang verwendet stabile Adressen und den eindeutig aufgelösten wirksamen View-Hash.
7. Alte GOVERNS-Kanten zu PiF2 nicht blind in PROTECTS umbenennen. Ein berechtigter Mensch bestätigt geschütztes PiF2, kohärentes CiV und tatsächliche Umsetzungselemente. Erst ein regulärer validierter Auftrag übernimmt die neuen Schutz-/Governancebezüge.
8. Constraints nur nach bestandener Prüfung ihrer Voraussetzungen anwenden. Alle einschlägigen Bestandsabfragen müssen null Fehler liefern; Transaktions-, Revisions-, Resolver- und Parallelitätstests müssen zusätzlich bestehen. Eine unverträgliche Mischung wird nicht aktiviert.

Bei leerem fachlichem Bestand werden technische Constraints/Gate zuerst installiert und anschließend genau einmal der atomare fachliche Bootstrap unter dem Gate ausgeführt. Vorhandene technische Belege sind kein zweiter fachlicher Bootstrap.

**Kurzes Beispiel:** Ein altes PiH mit Profil 1.0 behält seinen contentHash. Neue Zustandsänderungen erzeugen neue PiH mit 2.0. Ist eine alte Korrekturadresse nicht eindeutig auflösbar, wird der Übergang für diesen Fall angehalten statt der historische Wert umgedeutet.

## Abgrenzung der Mandantentrennung

`RoFOrg` ist eine fachliche Organisation im JCI-Graphen und kein technischer Mandantenschlüssel. Mehrere Organisationen dürfen bewusst in einem gemeinsamen Modellgraphen verbunden sein. Technische Datenbank-, Zugriffs- oder Deployment-Isolation wird außerhalb der JCI-Ontologie umgesetzt und darf die fachlichen Organisationsbeziehungen nicht verändern.

## Automatisierte Prüfung

Die technologieunabhängigen Invarianten werden durch [`tests/test_model_rules.py`](../../../tests/test_model_rules.py) geprüft. [`reference/jci_rules.py`](../../../reference/jci_rules.py) und [`tests/test_reference_rules.py`](../../../tests/test_reference_rules.py) bilden Eigentümerrevisionen, aktuelle Abschlussmengen, gemeinsame Zyklen, Profil-2.0-Korrekturen und konkurrierende Kandidaten ausführbar ab. [`tests/test_spec_consistency.py`](../../../tests/test_spec_consistency.py) prüft die Konsistenz von Katalogen, Schemas und Dokumenten. GitHub Actions führt die Tests bei jedem Push auf `main` und bei Pull Requests aus. Referenztests ersetzen weder eine produktive SYNC-Engine noch einen realen Neo4j-Isolationstest.

Die Cypher-Abfragen dieses Dokuments bleiben für eine reale Neo4j-Instanz zusätzlich verpflichtend. Jede Validierungsabfrage muss nach Migration und fachlicher Transaktion null Zeilen liefern.
