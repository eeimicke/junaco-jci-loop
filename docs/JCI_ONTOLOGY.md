# JCI-Ontologie

## 1. Status und Zweck

Dieses Dokument übersetzt die fachliche Bedeutung aus [JCI_CONTEXT.md](JCI_CONTEXT.md) in eindeutig benannte Entitäts- und Beziehungstypen. `JCI_CONTEXT.md` bleibt die kanonische fachliche Quelle. Bei einem Konflikt gilt der dort dokumentierte Stand; der Konflikt muss vor einer Modelländerung gemeldet werden.

Kardinalitäten und Invarianten stehen in [JCI_GRAPH_RULES.md](JCI_GRAPH_RULES.md). Der Ablauf von `SYNC` steht in [JCI_SYNC_SPEC.md](JCI_SYNC_SPEC.md). Datenbankspezifische Labels, Properties, Constraints und Indizes gehören in [implementations/neo4j/JCI_NEO4J_SCHEMA.md](implementations/neo4j/JCI_NEO4J_SCHEMA.md).

## 2. Abstrakte Typen

`JCIEntity` ist der abstrakte Oberbegriff aller als Knoten gespeicherten Instanzen. Die abstrakten Untertypen werden nicht als zusätzliche fachliche Knoten gespeichert:

```text
JCIEntity
├── JCIElementInstance
└── GraphObject
```

`JCIElementInstance` ist die gespeicherte Ausprägung eines speicherbaren JCI-Kernelements. `GraphObject` konkretisiert dessen operative, organisatorische, prüfende oder dokumentierende Anwendung.

`RoF` und `ERoF` bleiben Kernelemente, sind jedoch Modellräume ohne eigenen Knoten. `SyncRun` ist ausschließlich technischer Laufzustand und weder `JCIEntity` noch `GraphObject`.

## 3. Konkrete Entitätstypen

### 3.1 JCIElementInstance

```text
PiH
CiV
RaN
SYNC
PiF2
PiF1s
PiF1t
PiF1o
```

### 3.2 GraphObject

```text
RoFOrg
RoFOrgRelationship
RoFTeam
RoFTeamMember
RoFRole
RoleAssignment
Task
SuccessCriterion
Result
Verification
Evidence
ERoFObject
ChangeEvent
SyncEvent
RaNConflict
HistoricalCorrection
```

## 4. Gemeinsame Eigenschaften

Jede konkrete `JCIEntity` besitzt:

| Eigenschaft   | Datentyp | Pflicht | Regel                                      |
| ------------- | -------- | ------: | ------------------------------------------ |
| `id`          | UUID     |      ja | global eindeutig und unveränderlich        |
| `entityType`  | Enum     |      ja | entspricht genau dem konkreten Entitätstyp |
| `name`        | String   |      ja | nicht leer                                 |
| `description` | String   |    nein | fachliche Beschreibung                     |
| `createdAt`   | DateTime |      ja | ISO 8601 mit Zeitzone                      |
| `updatedAt`   | DateTime |      ja | nicht vor `createdAt`                      |
| `revision`    | Integer  |      ja | mindestens `1`                             |
| `status`      | Enum     |      ja | typabhängiger zulässiger Status            |

`PiH`, `ChangeEvent`, `SyncEvent` und `HistoricalCorrection` sind inhaltlich unveränderlich. Für sie gelten dauerhaft `revision = 1` und `updatedAt = createdAt`. Ein `ChangeEvent` dokumentiert einen angenommenen Veränderungsauftrag, während ein `SyncEvent` das Ergebnis genau eines beendeten oder kontrolliert abgebrochenen technischen `SyncRun` dokumentiert. Die beim Laufabschluss entstehende Beziehung `TRIGGERS` darf ausschließlich append-only ergänzt werden. Beim erfolgreichen `CREATED` darf außerdem genau einmal `CHANGED_BY` von der neu erzeugten Entität zum bereits bestehenden `ChangeEvent` hergestellt werden. Diese Provenienzergänzungen verändern keine Eigenschaft des `ChangeEvent`.

Für die hier präzisierten Entitätstypen gelten insbesondere folgende typspezifischen Pflichtfelder:

| Entitätstyp            | Zusätzliche Pflichtfelder |
| ---------------------- | ------------------------- |
| `ChangeEvent`          | `idempotencyKey`, `targetEntityId`, `targetEntityType`, `requestedRevision` |
| `SyncEvent`            | `runId` |
| `Verification`         | `evaluatedResultRevision`, `checkedCriterionRevision` |
| `HistoricalCorrection` | `baseHistoryViewHash` |

`requestedRevision` ist ausschließlich bei `changeType = CREATED` `null`; andernfalls ist es eine positive Ganzzahl. Die Zielangaben des `ChangeEvent` sind unveränderliche Audit-Koordinaten des Auftrags und ersetzen keine fachliche Beziehung. `runId` identifiziert genau einen technischen Versuch. `baseHistoryViewHash` bindet eine historische Korrektur an die vor ihr wirksame historische Sicht.

Typspezifische Pflichtfelder und Aufzählungswerte sind in Abschnitt 2.2.5 von [JCI_CONTEXT.md](JCI_CONTEXT.md) kanonisch beschrieben. Die verbindlichen Statusübergänge stehen in Abschnitt 2.2.4. Eine Datenbankimplementierung darf sie technisch konkretisieren, aber nicht abschwächen oder semantisch umdeuten.

Komplexe Werte verwenden ausschließlich die in Abschnitt 2.2.7 definierten Typen `TypedValue`, `StateSnapshot`, `RelationshipSnapshot`, `TypedValueMap`, `RuleExpression` und `SyncDefinition`. Unstrukturierte, implementierungsabhängige Objektinhalte sind nicht zulässig.

## 5. Beziehungskatalog

### 5.1 Zweck und Zukunft

```text
PiH PROVIDES_CONTEXT_TO CiV
CiV INSCRIBES_PURPOSE_IN PiF2
PiF1s CONTRIBUTES_TO PiF2
PiF1t CONTRIBUTES_TO PiF1s
PiF1o CONTRIBUTES_TO PiF1t
```

### 5.2 Operative Umsetzung und Prüfung

```text
PiF1o HAS_SUCCESS_CRITERIA SuccessCriterion
PiF1o ACCOUNTABLE_MEMBER RoFTeamMember
PiF1o DECOMPOSES_INTO Task
Task DECOMPOSES_INTO Task
Task DEPENDS_ON Task
Task RESPONSIBLE_TEAM RoFTeam
Task EXECUTED_BY RoleAssignment
Task USES ERoFObject
RoleAssignment USES ERoFObject
ERoFObject OWNED_BY RoFOrg
Task PRODUCES Result
Verification EVALUATES Result
Verification CHECKS SuccessCriterion
Verification USES_EVIDENCE Evidence
Verification SUPERSEDES Verification
```

Eine `Verification` bindet mit `evaluatedResultRevision` und `checkedCriterionRevision` genau die Revisionen, die geprüft wurden. Ihr `Result` ist `COMPLETED`, ihr `SuccessCriterion` ist `ACTIVE`, und beide gehören zum selben `PiF1o`. Anwendbar ist nur eine nicht abgelöste Verification, deren gebundene Revisionen weiterhin den aktuellen Revisionen ihrer beiden Ziele entsprechen.

**Kurzes Beispiel:** Eine Verification prüft Revision 3 eines abgeschlossenen Results gegen Revision 2 eines aktiven Erfolgskriteriums. Wird das Kriterium später zu Revision 3 geändert, bleibt die Verification dokumentiert, ist für die aktuelle Aggregation aber nicht mehr anwendbar.

### 5.3 Organisation und Rollen

```text
RoFOrg HAS_TEAM RoFTeam
RoFTeam HAS_MEMBER RoFTeamMember
RoFTeamMember HAS_ROLE RoFRole
RoFTeamMember HAS_ASSIGNMENT RoleAssignment
RoleAssignment IN_TEAM RoFTeam
RoleAssignment ACTIVATES_ROLE RoFRole
RoFOrgRelationship SOURCE_ORG RoFOrg
RoFOrgRelationship TARGET_ORG RoFOrg
RoFOrgRelationship REPRESENTED_BY RoleAssignment
```

### 5.4 Regeln

```text
RaN GOVERNS zulässige JCIEntity
RaN APPLIES_IN RoFOrg oder RoFTeam
RaNConflict CONFLICTING_RULE RaN
RaNConflict AFFECTS JCIEntity
RaNConflict DETECTED_BY SyncEvent
RaNConflict RESOLVED_BY RoleAssignment
RaNConflict RESOLVED_THROUGH ChangeEvent
RaNConflict USES_EVIDENCE Evidence
```

Zulässige Zieltypen sind `PiF2`, `PiF1s`, `PiF1t`, `PiF1o`, `Task`, `RoFOrg`, `RoFOrgRelationship`, `RoFTeam`, `RoFTeamMember`, `RoFRole`, `RoleAssignment` und `ERoFObject`.

Ein `RaN` besitzt `effect`, `decisionKey`, `scopeType`, `governedTypes` und eine normalisierte `condition`. `GOVERNS` verbindet die aktuell geregelten konkreten Ziele. `APPLIES_IN` begrenzt einen Organisations- oder Team-Scope. `priority` ist eine ausdrücklich gespeicherte Ganzzahl; eine größere Zahl bedeutet höheren Vorrang bei einem erkannten Widerspruch. `ruleType` besitzt keine implizite Rangfolge. `RaNConflict` ist ein historisierbares Graphobjekt mit `status = OPEN | RESOLVED`. Es ersetzt keine beteiligte Regel, sondern dokumentiert den nicht automatisch entscheidbaren Konflikt und seine spätere Auflösung. Ein `PRIORITY_TIE` verbindet mindestens zwei Regeln; ein `UNEVALUABLE` kann bereits eine einzelne nicht eindeutig auswertbare Regel betreffen.

### 5.5 Akteure und Nachweise

```text
JCIEntity CREATED_BY RoleAssignment
ChangeEvent REQUESTED_BY RoleAssignment
HistoricalCorrection CORRECTED_BY RoleAssignment
RaNConflict RESOLVED_BY RoleAssignment
RaNConflict USES_EVIDENCE Evidence
ChangeEvent USES_EVIDENCE Evidence
HistoricalCorrection USES_EVIDENCE Evidence
```

Der initiale Bootstrap bildet ausschließlich die einmalige Vertrauenswurzel eines vollständig leeren Graphen. Dabei wird genau ein Root-`RoleAssignment` mit `bootstrapKey = "ROOT"` erzeugt. Nur dieses RoleAssignment darf dauerhaft ohne `CREATED_BY` bestehen. Der atomare Minimalgraph enthält eine `RoFOrg`, ein `RoFTeam`, ein technisches `RoFTeamMember`, eine `RoFRole`, das Root-`RoleAssignment` und eine `SYNC`-Definition. Alle sechs Entitäten entstehen unmittelbar mit `status = ACTIVE`, `revision = 1` sowie demselben `createdAt` und `updatedAt`; vorhandene `validFrom`-Werte der Typen und Beziehungen entsprechen demselben Bootstrapzeitpunkt. Dies ist die einzige Ausnahme vom regulären `DRAFT`-Start. Alle Entitäten außer dem Root-`RoleAssignment` verweisen über `CREATED_BY` auf diese Vertrauenswurzel. Der Bootstrap erzeugt weder `ChangeEvent`, `SyncRun`, `SyncEvent` noch `PiH`, ist nicht wiederholbar und ist kein Datenimport.

**Kurzes Beispiel:** Nach dem einmaligen Anlegen des technischen Administrationsteams kann dessen Root-`RoleAssignment` den ersten regulären `CREATED`-Auftrag anfordern. Ein späterer Import darf den Bootstrap nicht erneut ausführen.

### 5.6 Veränderung, Historisierung und Korrektur

```text
historisierbare JCIEntity CHANGED_BY ChangeEvent
ChangeEvent TRIGGERS SyncEvent
ChangeEvent TARGETS_HISTORY PiH
SyncEvent EXECUTES SYNC
SyncEvent AFFECTS JCIEntity
historisierbare JCIEntity HAS_HISTORICAL_STATE PiH
SyncEvent CREATES_HISTORY PiH
HistoricalCorrection CORRECTS PiH
HistoricalCorrection CAUSED_BY ChangeEvent
SyncEvent CREATES_CORRECTION HistoricalCorrection
HistoricalCorrection SUPERSEDES HistoricalCorrection
ersetzbare JCIEntity REPLACED_BY gleicher konkreter JCIEntity-Typ
```

`EXECUTES` dokumentiert im abgeschlossenen `SyncEvent`, welche SYNC-Definition der technische `SyncRun` verwendet hat. Der technische `SyncRun` wird nicht als Zwischenknoten gespeichert. Ein angenommenes `ChangeEvent` darf zunächst kein Ziel über `TRIGGERS` besitzen. Jeder beendete oder kontrolliert abgebrochene Versuch erzeugt genau ein neues `SyncEvent` und ergänzt genau eine `TRIGGERS`-Kante append-only.

`CHANGED_BY` besitzt bedingte Semantik: Eine normale Änderung besitzt genau eine Quellentität. Bei `CREATED` fehlt die Quelle bis zum erfolgreichen Commit; nur bei `SUCCESS` entstehen Zielentität und Kante gemeinsam. Ein `ChangeEvent` für `HISTORICAL_CORRECTION` besitzt dagegen keine `CHANGED_BY`-Quelle, sondern genau ein `TARGETS_HISTORY` zu dem unverändert bleibenden `PiH`. Das später über `CORRECTS` verbundene PiH muss dasselbe Ziel sein.

`AFFECTS` kann leer sein, wenn ein Versuch mit `outcome = FAILED` bereits vor erfolgreicher Zielauflösung endet. Ein `SyncEvent` mit `SUCCESS` oder `CONFLICT` besitzt mindestens ein `AFFECTS`-Ziel.

Eine `HistoricalCorrection` speichert mit `baseHistoryViewHash` den Hash der wirksamen `HistoryView` unmittelbar vor ihrer Erzeugung. Nicht abgelöste Korrekturen desselben `PiH` müssen feldweise disjunkt sein. Eine neue Korrektur mit überlappenden `correctedFields` ersetzt genau eine aktive Vorgängerkorrektur vollständig über `SUPERSEDES`; andernfalls entsteht ein Konflikt.

**Kurzes Beispiel:** Während der erste SyncRun noch läuft, besitzt das `ChangeEvent` noch kein `TRIGGERS`-Ziel. Erst sein Abschluss erzeugt das `SyncEvent`. Eine spätere historische Berichtigung verweist bereits mit `TARGETS_HISTORY` auf das betroffene `PiH`, ohne dieses zu verändern.

`REPLACED_BY` ist die gespeicherte Nachfolgebeziehung einer Entität mit `status = REPLACED`. Quelle und Ziel besitzen denselben konkreten `entityType`; Selbstbezüge und Zyklen sind unzulässig.

## 6. Inverse Lesarten

Inverse Formulierungen dienen nur der Navigation und werden nicht als zusätzliche Kanten gespeichert. Beispiele:

```text
USED_BY           = inverse Lesart von USES
REALIZES          = inverse Lesart von DECOMPOSES_INTO
TRIGGERED_BY      = inverse Lesart von TRIGGERS
CREATED_FROM      = inverse Lesart von CREATES_HISTORY
CORRECTED_THROUGH = inverse Lesart von CORRECTS
SUPERSEDED_BY     = inverse Lesart von SUPERSEDES
```

## 7. Historisierbarkeit

Alle bereits vorhandenen `JCIEntities` sind grundsätzlich historisierbar, ausgenommen:

```text
PiH
ChangeEvent
SyncEvent
HistoricalCorrection
```

Diese vier Typen sind inhaltlich unveränderlich und werden nicht erneut historisiert. Ausschließlich die oben beschriebenen append-only Provenienzergänzungen am `ChangeEvent` sind zulässig. Eine Abweichung in einem `PiH` wird durch ein neues `HistoricalCorrection`-Objekt dokumentiert. Das `PiH` selbst bleibt unverändert. `TARGETS_HISTORY` adressiert nur den Anlass der Korrektur und ist keine Änderung des historischen Zustands.

## 8. Task-Typen und Task-Graph

Jeder `Task` besitzt genau ein `taskKind`:

```text
ATOMIC    = unmittelbar ausführbare Tätigkeit
COMPOSITE = Strukturknoten aus mindestens einem untergeordneten Task
```

`PiF1o DECOMPOSES_INTO Task` ordnet jeden Task unabhängig von seiner Hierarchiestufe genau einem operativen Zukunftszustand zu. `Task DECOMPOSES_INTO Task` bildet eine zyklusfreie Hierarchie ab, in der ein Task höchstens einen direkten übergeordneten Task besitzt. `Task DEPENDS_ON Task` beschreibt eine fachliche Ausführungsvoraussetzung und darf auch über Hierarchie- und PiF1o-Grenzen hinweg verlaufen, bleibt aber selbst- und zyklusfrei.

`HAS_MEMBER` und `HAS_ROLE` besitzen `validFrom` und optional `validUntil`. Der Zeitraum eines `RoleAssignment` liegt vollständig innerhalb der gleichzeitig gültigen Mitgliedschaft und des Rollenbesitzes. `OWNED_BY` ermöglicht die organisationsbezogene Ableitung von internem und externem Umweltkontext; tatsächliche Interaktion bleibt über `USES` personengebunden.

Nur `ATOMIC`-Tasks besitzen `EXECUTED_BY`, `USES` und `PRODUCES`. Ein aktiver oder abgeschlossener atomarer Task besitzt mindestens ein ausführendes `RoleAssignment`. Der Status eines `COMPOSITE`-Tasks wird aus seinen direkten Untertasks abgeleitet.

## 9. Maschinenlesbarer Austausch und Erweiterung

Vollständige Graph- und Ontologieexporte verwenden JSON-LD 1.1 mit dem Kontext `schemas/jci-context.jsonld`. Entitäten werden als `urn:jci:<UUID>` identifiziert; konkrete Typen und Beziehungen verwenden den öffentlichen, versionierten Namensraum `https://eeimicke.github.io/junaco-jci-loop/ns/jci/1.0#`.

`JCIChangeRequest` und `JCISyncResult` verwenden `schemaVersion = "1.1"`. Für `HISTORICAL_CORRECTION` ersetzt ein strukturiertes `historicalCorrection`-Objekt die allgemeinen `operations`; es enthält insbesondere `expectedHistoryViewHash`, eindeutige lexikografisch sortierte `correctedFields`, `previousValue` und `correctedValue`.

Komplexe Eigenschaften verwenden die strukturierten Typen aus `JCI_CONTEXT.md` und werden als JSON-LD-kompatible JSON-Werte übertragen. Die Neo4j-Projektion als kanonische JSON-Zeichenkette verändert das Austauschformat nicht.

Die in dieser Version aufgeführten konkreten Entitäts-, Enum- und Beziehungstypen bilden einen geschlossenen Katalog. Eine neue Unterart oder Beziehung benötigt eine versionierte semantische Modelländerung in `JCI_CONTEXT.md`, die anschließende Aktualisierung aller Folgedokumente, des JSON-LD-Kontexts, der Schemas und der Tests. Implementierungen dürfen unbekannte Typen nicht stillschweigend als bekannte Typen behandeln.

**Kurzes Beispiel:** Eine exportierte Task-Entität besitzt `@id = "urn:jci:<UUID>"`, `@type = "jci:Task"` und Beziehungen wie `jci:RESPONSIBLE_TEAM`. Beim Import entstehen daraus wieder die kanonischen Knoten und Kanten.
