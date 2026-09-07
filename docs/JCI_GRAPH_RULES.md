# JCI-Graphregeln

## 1. Status und Zweck

Dieses Dokument legt technologieunabhängige Kardinalitäten und Invarianten des JCI-Graphen fest. Die fachliche Bedeutung stammt aus [`JCI_CONTEXT.md`](JCI_CONTEXT.md), der zulässige Typkatalog aus [`JCI_ONTOLOGY.md`](JCI_ONTOLOGY.md). Bei einem Konflikt gilt [`JCI_CONTEXT.md`](JCI_CONTEXT.md).

**Regelpaket 2.0:** Ontologie, Graphregeln, SYNC, neue Snapshots, Korrekturwerte und das Austauschformat verwenden Version `2.0`. JSON-LD bleibt `1.1`; bestehende Namespace-IRIs mit `/1.0#` bleiben stabile Vokabularidentitäten und bezeichnen nicht die Regelversion. Frühere Datensätze werden ausschließlich nach ihren ausdrücklich angegebenen Versionsprofilen gelesen.

## 2. Allgemeine Entitätsregeln

1. Jede konkrete `JCIEntity` besitzt genau eine global eindeutige und unveränderliche UUID als `id`.
2. `entityType` stimmt mit dem konkreten Entitätstyp überein.
3. `revision` ist eine positive Ganzzahl und beginnt bei `1`.
4. Bei einer tatsächlichen fachlichen Änderung wird der vorherige Zustand als `PiH` gespeichert und die Revision des aktuellen Elements um genau eins erhöht.
5. Jeder fachliche Statuswechsel ist eine tatsächliche Änderung.
6. `updatedAt` liegt nicht vor `createdAt`; bei unveränderlichen Entitäten sind beide Werte gleich.
7. `PiH`, `ChangeEvent`, `SyncEvent` und `HistoricalCorrection` besitzen dauerhaft `status = RECORDED` und `revision = 1`.
8. Diese vier Typen behalten unveränderliche Eigenschaften und eigene Provenienz und werden weder gelöscht noch erneut historisiert. Einem anderen neuen Objekt zugeordnete Bezugnahmen folgen Abschnitt 2.2.8 von `JCI_CONTEXT`. Append-only `TRIGGERS` und die erfolgreiche Erstellungsverknüpfung `CHANGED_BY` verändern Revision und Zeitstempel des bestehenden `ChangeEvent` nicht.
9. Leere Pflichtfelder sind unzulässig.
10. Fachliche Beziehungen werden ausschließlich als Kanten und nicht zusätzlich als ID-Listen gespeichert.
11. `ChangeEvent.targetEntityId` und `targetEntityType` sind unveränderliche Audit-Koordinaten des angenommenen Auftrags. Sie ersetzen keine Kante. Sobald eine kanonische Zielbeziehung vorhanden ist, muss sie dieselbe Entität bezeichnen; bei einem noch nicht erfolgreichen oder gescheiterten `CREATED` darf der Zielknoten fehlen.

## 3. Statusregeln

| Entitätstypen                                             | Zulässige Statuswerte                                            |
| --------------------------------------------------------- | ---------------------------------------------------------------- |
| `CiV`, `RaN`, `SYNC`, RoF- und ERoF-Graphobjekte          | `DRAFT`, `ACTIVE`, `REPLACED`, `REVOKED`                         |
| `PiF2`, `PiF1s`, `PiF1t`, `PiF1o`                         | `DRAFT`, `ACTIVE`, `ACHIEVED`, `REPLACED`, `REVOKED`             |
| `Task`                                                    | `DRAFT`, `ACTIVE`, `BLOCKED`, `COMPLETED`, `REPLACED`, `REVOKED` |
| `Result`                                                  | `DRAFT`, `ACTIVE`, `COMPLETED`, `REPLACED`, `REVOKED`            |
| `SuccessCriterion`, `Evidence`                            | `DRAFT`, `ACTIVE`, `REPLACED`, `REVOKED`                         |
| `Verification`                                            | `COMPLETED`                                                      |
| `RaNConflict`                                             | `OPEN`, `RESOLVED`                                               |
| `PiH`, `ChangeEvent`, `SyncEvent`, `HistoricalCorrection` | `RECORDED`                                                       |

Aus `ACHIEVED`, `REPLACED`, `REVOKED`, `COMPLETED`, `RECORDED` und `RESOLVED` führt kein Übergang zurück in einen veränderbaren Zustand. Eine Fortsetzung wird als neue Entität modelliert.

Verbindliche Übergangsregeln:

1. Veränderliche Fachentitäten werden als `DRAFT` erzeugt und dürfen erst nach vollständiger Validierung `ACTIVE` werden. Ausschließlich die sechs Entitäten des initialen Bootstraps nach Abschnitt 12 entstehen atomar direkt als `ACTIVE`.
2. `DRAFT` darf zu `ACTIVE` oder `REVOKED` wechseln.
3. `ACTIVE` darf allgemein zu `REPLACED` oder `REVOKED` wechseln.
4. Ein aktives Zukunftselement darf bei erfüllten Zielbedingungen `ACHIEVED` werden.
5. Ein Task darf von `DRAFT` oder `ACTIVE` zu `BLOCKED` wechseln. Von `BLOCKED` darf er bei erfüllten Voraussetzungen zu `ACTIVE` oder bei gleichzeitig erfüllten Abschlussbedingungen zu `COMPLETED` wechseln.
6. Ein aktiver Task oder ein aktives Result darf bei erfüllten Abschlussbedingungen `COMPLETED` werden.
7. Ein `RaNConflict` wird als `OPEN` erzeugt und darf ausschließlich nach bestätigter Auflösung zu `RESOLVED` wechseln.
8. Eine `Verification` wird nach vollständiger Prüfung unmittelbar als `COMPLETED` erzeugt.
9. `PiH`, `ChangeEvent`, `SyncEvent` und `HistoricalCorrection` werden unmittelbar als `RECORDED` erzeugt.
10. Prozessartefakte und ein durch SYNC erzeugter offener `RaNConflict` lösen für ihre eigene Erzeugung kein rekursives `ChangeEvent` aus.
11. Deterministisch aus einem Veränderungsauftrag abgeleitete Folgeänderungen erzeugen kein eigenes rekursives `ChangeEvent`; sie bleiben über das gemeinsame `SyncEvent`, `AFFECTS`, Revision und `PiH` nachvollziehbar.
12. Beziehungsänderungen folgen der Endpunktzuordnung aus Abschnitt 2.2.8 von `JCI_CONTEXT`: Nur vorhandene veränderliche Eigentümer mit tatsächlichem Delta erhalten je Auftrag genau eine Revision und ein `PiH`. Prüf- und Auditbezüge revisionieren ihre Ziele nicht; jeder Graphschreibvorgang bleibt durch den technischen Commit-Gate geschützt.

## 4. Kardinalitäten

Die Spalte „Ziele je Quelle“ gilt in Pfeilrichtung; „Quellen je Ziel“ gilt in Gegenrichtung.

### 4.1 Zweck und Zukunft

| Quelle  | Beziehung              | Ziel                                                     | Ziele je Quelle | Quellen je Ziel |
| ------- | ---------------------- | -------------------------------------------------------- | --------------: | --------------: |
| `PiH`   | `PROVIDES_CONTEXT_TO`  | `CiV`                                                    | `0..n`          | `0..n`          |
| `CiV`   | `HELD_BY`              | `RoFOrg`, `RoFTeam` oder<br>menschliches `RoFTeamMember` | `1`             | `0..n`          |
| `CiV`   | `INFORMED_BY`          | `CiV`                                                    | `0..n`          | `0..n`          |
| `CiV`   | `INSCRIBES_PURPOSE_IN` | `PiF2`                                                   | `0..n`          | `1..n`          |
| `PiF1s` | `CONTRIBUTES_TO`       | `PiF2`                                                   | `1..n`          | `0..n`          |
| `PiF1t` | `CONTRIBUTES_TO`       | `PiF1s`                                                  | `1..n`          | `0..n`          |
| `PiF1o` | `CONTRIBUTES_TO`       | `PiF1t`                                                  | `1..n`          | `0..n`          |

### 4.2 Operative Umsetzung und Prüfung

| Quelle           | Beziehung              | Ziel               | Ziele je Quelle | Quellen je Ziel |
| ---------------- | ---------------------- | ------------------ | --------------: | --------------: |
| `PiF1o`          | `HAS_SUCCESS_CRITERIA` | `SuccessCriterion` | `1..n`          | `1`             |
| `PiF1o`          | `ACCOUNTABLE_MEMBER`   | `RoFTeamMember`    | `1`             | `0..n`          |
| `PiF1o`          | `DECOMPOSES_INTO`      | `Task`             | `1..n`          | `1`             |
| `Task`           | `DECOMPOSES_INTO`      | `Task`             | `0..n`          | `0..1`          |
| `Task`           | `DEPENDS_ON`           | `Task`             | `0..n`          | `0..n`          |
| `Task`           | `RESPONSIBLE_TEAM`     | `RoFTeam`          | `1`             | `0..n`          |
| `Task`           | `EXECUTED_BY`          | `RoleAssignment`   | `0..n`          | `0..n`          |
| `Task`           | `USES`                 | `ERoFObject`       | `0..n`          | `0..n`          |
| `RoleAssignment` | `USES`                 | `ERoFObject`       | `0..n`          | `1..n`          |
| `ERoFObject`     | `OWNED_BY`             | `RoFOrg`           | `0..n`          | `0..n`          |
| `Task`           | `PRODUCES`             | `Result`           | `0..n`          | `1`             |
| `Verification`   | `EVALUATES`            | `Result`           | `1`             | `0..n`          |
| `Verification`   | `CHECKS`               | `SuccessCriterion` | `1`             | `0..n`          |
| `Verification`   | `USES_EVIDENCE`        | `Evidence`         | `0..n`          | `0..n`          |
| `Verification`   | `SUPERSEDES`           | `Verification`     | `0..1`          | `0..1`          |

### 4.3 Organisation und Rollen

| Quelle               | Beziehung        | Ziel             | Ziele je Quelle | Quellen je Ziel |
| -------------------- | ---------------- | ---------------- | --------------: | --------------: |
| `RoFOrg`             | `HAS_TEAM`       | `RoFTeam`        | `1..n`          | `1`             |
| `RoFTeam`            | `HAS_MEMBER`     | `RoFTeamMember`  | `1..n`          | `1..n`          |
| `RoFTeamMember`      | `HAS_ROLE`       | `RoFRole`        | `1..n`          | `0..n`          |
| `RoFTeamMember`      | `HAS_ASSIGNMENT` | `RoleAssignment` | `0..n`          | `1`             |
| `RoleAssignment`     | `IN_TEAM`        | `RoFTeam`        | `1`             | `0..n`          |
| `RoleAssignment`     | `ACTIVATES_ROLE` | `RoFRole`        | `1`             | `0..n`          |
| `RoFOrgRelationship` | `SOURCE_ORG`     | `RoFOrg`         | `1`             | `0..n`          |
| `RoFOrgRelationship` | `TARGET_ORG`     | `RoFOrg`         | `1`             | `0..n`          |
| `RoFOrgRelationship` | `REPRESENTED_BY` | `RoleAssignment` | `2..n`          | `0..n`          |

### 4.4 Akteure und Nachweise

| Quelle                 | Beziehung       | Ziel             | Ziele je Quelle | Quellen je Ziel |
| ---------------------- | --------------- | ---------------- | --------------: | --------------: |
| `JCIEntity`            | `CREATED_BY`    | `RoleAssignment` | `0..1`          | `0..n`          |
| `ChangeEvent`          | `REQUESTED_BY`  | `RoleAssignment` | `1`             | `0..n`          |
| `HistoricalCorrection` | `CORRECTED_BY`  | `RoleAssignment` | `1`             | `0..n`          |
| `ChangeEvent`          | `USES_EVIDENCE` | `Evidence`       | `0..n`          | `0..n`          |
| `HistoricalCorrection` | `USES_EVIDENCE` | `Evidence`       | `0..n`          | `0..n`          |

### 4.5 Veränderung, Historisierung und Korrektur

| Quelle                      | Beziehung              | Ziel                   | Ziele je Quelle | Quellen je Ziel |
| --------------------------- | ---------------------- | ---------------------- | --------------: | --------------: |
| historisierbare `JCIEntity` | `CHANGED_BY`           | `ChangeEvent`          | `0..n`          | `0..1`          |
| `ChangeEvent`               | `TRIGGERS`             | `SyncEvent`            | `0..n`          | `1`             |
| `ChangeEvent`               | `TARGETS_HISTORY`      | `PiH`                  | `0..1`          | `0..n`          |
| `SyncEvent`                 | `EXECUTES`             | `SYNC`                 | `1`             | `0..n`          |
| `SyncEvent`                 | `AFFECTS`              | `JCIEntity`            | `0..n`          | `0..n`          |
| historisierbare `JCIEntity` | `HAS_HISTORICAL_STATE` | `PiH`                  | `0..n`          | `1`             |
| `SyncEvent`                 | `CREATES_HISTORY`      | `PiH`                  | `0..n`          | `1`             |
| `HistoricalCorrection`      | `CORRECTS`             | `PiH`                  | `1`             | `0..n`          |
| `HistoricalCorrection`      | `CAUSED_BY`            | `ChangeEvent`          | `1`             | `0..n`          |
| `SyncEvent`                 | `CREATES_CORRECTION`   | `HistoricalCorrection` | `0..n`          | `1`             |
| `HistoricalCorrection`      | `SUPERSEDES`           | `HistoricalCorrection` | `0..1`          | `0..1`          |
| ersetzbare `JCIEntity`      | `REPLACED_BY`          | gleicher konkreter Typ | `0..1`          | `0..n`          |

Bedingte Invarianten:

1. Eine normale Änderung einer vorhandenen historisierbaren Entität besitzt genau eine `CHANGED_BY`-Quelle.
2. Bei `CREATED` besitzt das `ChangeEvent` vor dem erfolgreichen Commit keine `CHANGED_BY`-Quelle. Nur bei `SUCCESS` entstehen die neue Entität mit `revision = 1`, `CREATED_BY` und genau einer `CHANGED_BY`-Kante atomar; bei `CONFLICT` oder `FAILED` entsteht nichts davon und auch kein `PiH`.
3. Ein `ChangeEvent` mit `changeType = HISTORICAL_CORRECTION` besitzt genau ein `TARGETS_HISTORY`, keine `CHANGED_BY`-Quelle und `requestedRevision = 1`. Alle anderen Änderungstypen besitzen kein `TARGETS_HISTORY`.
4. Ein angenommenes `ChangeEvent` darf `TRIGGERS = 0` besitzen, solange noch kein Versuch beendet wurde. Jeder beendete oder kontrolliert abgebrochene `SyncRun` ergänzt genau eine Kante append-only; jedes `SyncEvent` besitzt genau ein auslösendes `ChangeEvent`.
5. Ein `SyncEvent` mit `SUCCESS` oder `CONFLICT` besitzt mindestens ein `AFFECTS`-Ziel. Nur ein `FAILED`-Versuch, der vor erfolgreicher Zielauflösung endet, darf kein `AFFECTS`-Ziel besitzen.

**Kurzes Beispiel:** Ein abgewiesener `CREATED`-Auftrag behält sein `ChangeEvent` und erhält nach dem beendeten Versuch ein `SyncEvent`, erzeugt aber weder den angeforderten Zielknoten noch `CHANGED_BY` oder `PiH`.

`RaN ── PROTECTS ──► CiV | PiF2` und `RaN ── GOVERNS ──► zulässiges Umsetzungselement` besitzen in beiden Richtungen `0..n`. Für aktive RaN gelten zusätzlich die Mindestkardinalitäten und Kohärenzregeln aus Abschnitt 7.

| Quelle | Beziehung    | Ziel                         | Ziele je Quelle | Quellen je Ziel |
| ------ | ------------ | ---------------------------- | --------------: | --------------: |
| `RaN`  | `PROTECTS`   | `CiV` oder `PiF2`            | `0..n`          | `0..n`          |
| `RaN`  | `GOVERNS`    | zulässiges Umsetzungselement | `0..n`          | `0..n`          |
| `RaN`  | `APPLIES_IN` | `RoFOrg` oder `RoFTeam`      | `0..1`          | `0..n`          |

| Quelle        | Beziehung          | Ziel             | Ziele je Quelle | Quellen je Ziel |
| ------------- | ------------------ | ---------------- | --------------: | --------------: |
| `RaNConflict` | `CONFLICTING_RULE` | `RaN`            | `1..n`          | `0..n`          |
| `RaNConflict` | `AFFECTS`          | `JCIEntity`      | `1..n`          | `0..n`          |
| `RaNConflict` | `DETECTED_BY`      | `SyncEvent`      | `1`             | `0..n`          |
| `RaNConflict` | `RESOLVED_BY`      | `RoleAssignment` | `0..1`          | `0..n`          |
| `RaNConflict` | `RESOLVED_THROUGH` | `ChangeEvent`    | `0..1`          | `0..n`          |
| `RaNConflict` | `USES_EVIDENCE`    | `Evidence`       | `0..n`          | `0..n`          |

## 5. Akteurs- und Evidenzregeln

1. Akteure werden als Beziehungen zu `RoleAssignment` gespeichert; Text- oder ID-Duplikate sind unzulässig.
2. Eine fachlich aktive oder abgeschlossene `JCIEntity` besitzt genau eine `CREATED_BY`-Beziehung, ausgenommen das einmalige Root-`RoleAssignment` des initialen Bootstraps.
3. Nur genau ein Root-`RoleAssignment` mit `bootstrapKey = "ROOT"` darf dauerhaft `CREATED_BY = 0` besitzen. Bei importierten Entitäten ist das Fehlen ausschließlich vorübergehend im Status `DRAFT` zulässig.
4. Jedes `ChangeEvent` besitzt genau ein `REQUESTED_BY`.
5. Jede `HistoricalCorrection` besitzt genau ein `CORRECTED_BY`.
6. Nachweise werden ausschließlich als `Evidence`-Knoten gespeichert und über `USES_EVIDENCE` verbunden.
7. Eine `HistoricalCorrection` darf ohne `Evidence` bestehen, benötigt jedoch immer eine nicht leere Begründung.

### 5.1 Rückverfolgbarkeitsregeln

1. Jeder `ACTIVE` oder `COMPLETED` atomare Task gehört über genau einen `PiF1o` zu mindestens einem vollständigen Pfad über `PiF1t`, `PiF1s` und `PiF2` zu mindestens einem `CiV`.
2. Jeder solche Task besitzt genau ein `RESPONSIBLE_TEAM` und mindestens ein gültiges `EXECUTED_BY` zu einem `RoleAssignment` dieses Teams.
3. Jedes ausführende `RoleAssignment` ist eindeutig mit genau einem Team, einer aktivierten Rolle und genau einem Teammitglied verbunden; das Team gehört genau zu einer Organisation.
4. Umweltbeziehungen eines Tasks müssen über seine ausführenden Rollenaktivierungen zu mindestens einer handelnden menschlichen oder technischen Identität zurückverfolgbar sein.
5. Anwendbare `RaN` werden aus `GOVERNS`, Gültigkeit, Status und Scope bestimmt; ein fehlender Regelpfad ist nur zulässig, wenn tatsächlich keine Regel anwendbar ist.
6. Ein `DRAFT` darf unvollständige Pfade besitzen. Der Übergang zu `ACTIVE` ist bei einem unvollständigen WHY- oder WHO-Pfad unzulässig.

## 6. Organisations- und Umweltregeln

1. Jedes `CiV` beschreibt genau einen Wert und besitzt nicht leere Strings für `notCiV`, `selfCiV` und `toServeCiV`; die alten Felder `purpose`, `values` und `scope` sind für CiV unzulässig.
2. Jedes `CiV` besitzt genau ein `HELD_BY` zu einer `RoFOrg`, einem `RoFTeam` oder einem menschlichen `RoFTeamMember`. Ein technisches Mitglied ist als Werteträger unzulässig.
3. `INFORMED_BY` verbindet ausschließlich unterschiedliche CiV nach ausdrücklicher fachlicher Bestätigung. Gleicher Name, Mitgliedschaft oder Zugehörigkeit erzeugen weder eine Kante noch eine automatische Übernahme von Dimensionen.
4. Alle CiV, die dasselbe `PiF2` unmittelbar über `INSCRIBES_PURPOSE_IN` begründen, besitzen denselben `HELD_BY`-Zielknoten. Dieser bestimmt den Scope des `PiF2`; ein redundantes CiV-Zweck- oder Scope-Feld ist unzulässig.
5. Ein organisationsbezogenes CiV bleibt mit der `RoFOrg` verbunden, auch wenn ein beauftragtes Team es erarbeitet. Die menschliche Entscheidung bleibt über `CREATED_BY`, `ChangeEvent`, `REQUESTED_BY` und die beteiligten `RoleAssignments` nachvollziehbar.
6. Jede aktive `RoFOrg` besitzt mindestens ein Team; jedes aktive Team mindestens ein Mitglied.
7. Ein `RoleAssignment` gehört genau zu einem Mitglied, einem Team und einer aktivierten Rolle.
8. Das Mitglied eines `RoleAssignment` muss Mitglied des verbundenen Teams sein und die aktivierte Rolle besitzen.
9. Mindestens ein ausführendes `RoleAssignment` eines aktiven oder abgeschlossenen `ATOMIC`-Tasks gehört zu dessen `RESPONSIBLE_TEAM`.
10. Jedes aktive `ERoFObject` wird von mindestens einem `RoleAssignment` verwendet.
11. Eine direkte `Task ── USES ──► ERoFObject`-Beziehung ist nur für `ATOMIC`-Tasks zulässig und setzt voraus, dass mindestens ein ausführendes `RoleAssignment` dasselbe Objekt verwendet.
12. `SOURCE_ORG` und `TARGET_ORG` einer `RoFOrgRelationship` müssen verschieden sein.
13. `SUBSIDIARY` ist gerichtet und über beliebig viele Ebenen zulässig, muss aber zyklusfrei bleiben.
14. `PARTNERSHIP` ist fachlich wechselseitig; die gespeicherte Richtung dient nur der Eindeutigkeit.
15. Eine aktive Organisationsbeziehung besitzt mindestens ein vertretendes `RoleAssignment` aus jeder beteiligten Organisation.
16. `HAS_MEMBER` und `HAS_ROLE` besitzen `validFrom` und optional `validUntil`; das Ende liegt nicht vor dem Beginn.
17. Der Gültigkeitszeitraum eines `RoleAssignment` liegt vollständig innerhalb einer gleichzeitig gültigen Mitgliedschaft im Team und eines gleichzeitig gültigen Rollenbesitzes.
18. Ist `allocation` angegeben, gilt `0 < allocation <= 1`; die Summe gleichzeitig gültiger Werte eines Mitglieds überschreitet `1` nicht.
19. Eine aktive `PARTNERSHIP` speichert die Organisation mit der lexikografisch kleineren UUID als `SOURCE_ORG`.
20. Aktive Organisationsbeziehungen desselben Typs und Organisationspaars besitzen keine überlappenden Gültigkeitszeiträume.
21. `INTERNAL` beziehungsweise `EXTERNAL` wird je betrachteter Organisation abgeleitet: Eine `OWNED_BY`-Kante zu ihr ergibt `INTERNAL`, ihr Fehlen `EXTERNAL`.

## 7. RaN-Schutz, Priorität und Konflikte

1. Ein aktives `RaN` besitzt mindestens ein `PROTECTS` zu `CiV`, mindestens ein `PROTECTS` zu `PiF2` und mindestens ein `GOVERNS` zu einem zulässigen Umsetzungselement.
2. Jedes geschützte CiV begründet mindestens ein durch dasselbe RaN geschütztes PiF2; jedes geschützte PiF2 wird von mindestens einem durch dasselbe RaN geschützten CiV begründet. Weitere CiV desselben PiF2 müssen nicht geschützt werden.
3. `PROTECTS` besitzt nur `CiV` oder `PiF2` als Ziel. `GOVERNS` besitzt nur `PiF1s`, `PiF1t`, `PiF1o`, `Task`, `SuccessCriterion`, `Result`, `Verification`, `Evidence`, `RoFOrg`, `RoFOrgRelationship`, `RoFTeam`, `RoFTeamMember`, `RoFRole`, `RoleAssignment` oder `ERoFObject` als Ziel.
4. `PROTECTS` wird ausschließlich durch eine ausdrückliche, menschlich bestätigte und auf ein `RoleAssignment` zurückführbare Änderung erzeugt. `SYNC` leitet keine Schutzbeziehung automatisch ab.
5. Schutzobjekte sind gemäß `GLOBAL`, `ORGANIZATION`, `TEAM` oder `ENTITY` organisatorisch mit Scope und WHY-Pfaden des RaN vereinbar.
6. Für eine Entscheidung werden nur `RaN` mit `status = ACTIVE`, gültigem Zeitintervall, passendem `scopeType`, zutreffendem `APPLIES_IN`, passendem `governedTypes` und einschlägiger `GOVERNS`-Beziehung berücksichtigt.
7. `priority` ist eine verpflichtende Ganzzahl; eine größere Zahl bedeutet höheren Vorrang bei einem tatsächlichen Widerspruch.
8. `ruleType` begründet keinen automatischen Vorrang.
9. Vereinbare anwendbare Regeln gelten gemeinsam, unabhängig von ihrer relativen Priorität.
10. Bei widersprüchlichen Regeln unterschiedlicher Priorität gilt für den konkreten Widerspruch die höher priorisierte Regel. Die andere Regel bleibt außerhalb dieses Widerspruchs aktiv.
11. Bei mindestens zwei widersprüchlichen Regeln derselben höchsten einschlägigen Priorität entsteht genau ein `RaNConflict` mit `conflictType = PRIORITY_TIE` für die Konfliktmenge und Entscheidung.
12. Ist Anwendbarkeit oder Vereinbarkeit nicht eindeutig auswertbar, entsteht ein `RaNConflict` mit `conflictType = UNEVALUABLE`; die Priorität darf Unsicherheit nicht übergehen.
13. Ein offener Konflikt besitzt einen nicht leeren und innerhalb des Veränderungsauftrags eindeutigen `conflictKey`, mindestens eine `CONFLICTING_RULE`, mindestens ein `AFFECTS`, genau ein `DETECTED_BY`, kein `RESOLVED_BY` und kein `RESOLVED_THROUGH`. `PRIORITY_TIE` erfordert mindestens zwei Konfliktregeln; für `UNEVALUABLE` genügt mindestens eine nicht eindeutig auswertbare Regel.
14. Ein gelöster Konflikt besitzt genau ein `RESOLVED_BY`, genau ein `RESOLVED_THROUGH` und ein nicht leeres `resolution` sowie `resolvedAt`.
15. `RESOLVED` darf erst gesetzt werden, wenn ein nachfolgender erfolgreicher Synchronisationslauf bestätigt, dass der dokumentierte Widerspruch nicht mehr besteht.
16. Der Wechsel von `OPEN` zu `RESOLVED` ist eine fachliche Änderung; der offene Ausgangszustand wird als `PiH` historisiert. `RESOLVED` ist terminal.
17. Ein offener Konflikt blockiert automatische Änderungen, deren Zulässigkeit von seiner Auflösung abhängt; unabhängige Prüfungen bleiben möglich.
18. `governedTypes` ist nicht leer; jedes `GOVERNS`-Ziel besitzt einen aufgeführten konkreten Typ.
19. `GLOBAL` und `ENTITY` besitzen kein `APPLIES_IN`. `ORGANIZATION` besitzt genau eine Beziehung zu `RoFOrg`; `TEAM` genau eine zu `RoFTeam`.
20. Jede Condition besitzt `combiner = ALL | ANY` und mindestens eine auswertbare Klausel aus `path`, `operator` und gegebenenfalls `value`.
21. `REQUIRE` erlaubt bei wahrer und verweigert bei falscher Bedingung. `PROHIBIT` verweigert bei wahrer Bedingung. `PERMIT` erlaubt bei wahrer Bedingung. Falsches `PROHIBIT` oder `PERMIT` trifft keine eigene Entscheidung.
22. Eine Regelverletzung blockiert die angeforderte Entscheidung, erzeugt allein aber keinen `RaNConflict`.
23. Ein Widerspruch liegt nur vor, wenn Regeln mit gleichem `decisionKey`, überlappendem Scope und gemeinsamem Ziel gleichzeitig erlauben und verweigern.

## 8. Erfolgskriterien und Erreichung

1. Jedes `SuccessCriterion` besitzt genau ein `requirementLevel = REQUIRED | OPTIONAL`, ein `evaluationMode = ALL | ANY`, einen zum `measurementType` passenden `operator` und einen gültigen `targetValue`.
2. Ohne ausdrücklich abweichende Festlegung gelten `requirementLevel = REQUIRED` und `evaluationMode = ALL`.
3. Jedes fachlich vollständige `PiF1o` besitzt mindestens ein aktuelles `SuccessCriterion` mit `requirementLevel = REQUIRED`. Ausgeschiedene Pflichtkriterien erfüllen diese Mindestmenge nicht.
4. Jede `Verification` besitzt positive Ganzzahlen `evaluatedResultRevision` und `checkedCriterionRevision`.
5. Eine `Verification` bewertet genau ein `COMPLETED`-Result und prüft genau ein `ACTIVE`-SuccessCriterion. Bei ihrer Erzeugung und für die aktuelle Zielauswertung gehören der erzeugende Task und das Kriterium zum aktuellen Umfang desselben `PiF1o`.
6. Bei der Erzeugung entsprechen `evaluatedResultRevision` und `checkedCriterionRevision` exakt den unter dem Commit-Gate nach Abschnitt 12.8 geprüften Zielrevisionen. Jede Abweichung erzeugt `CONFLICT`. `EVALUATES`, `CHECKS` und eigene Prüfungsprovenienz verändern diese Zielrevisionen nach Abschnitt 2.2.8 nicht.
7. Eine anwendbare aktuelle `Verification` ist `COMPLETED`, nicht über `SUPERSEDES` abgelöst und bindet weiterhin die aktuellen Revisionen ihres `COMPLETED`-Results und `ACTIVE`-Kriteriums. Für die Zielauswertung müssen erzeugender Task und Kriterium zusätzlich zum aktuellen Umfang desselben `PiF1o` gehören.
8. `SUPERSEDES` verbindet nur Verifications mit demselben `Result` und demselben `SuccessCriterion`.
9. Verification-Ketten sind zeitlich vorwärts gerichtet, besitzen keine Verzweigung und sind zyklusfrei.
10. Bei `evaluationMode = ALL` ist ein Kriterium erfüllt, wenn mindestens eine anwendbare aktuelle Verification existiert und alle anwendbaren aktuellen Verifications `VALID` sind.
11. Bei `evaluationMode = ANY` ist ein Kriterium erfüllt, wenn mindestens eine anwendbare aktuelle Verification `VALID` ist.
12. `INVALID`, `INCONCLUSIVE` und eine fehlende anwendbare aktuelle Verification erfüllen ein Kriterium nicht; bei `ALL` verhindert bereits eine davon die Erfüllung.
13. Es zählen nur Results aktueller Tasks desselben `PiF1o` wie das aktuelle Kriterium. Ausgeschiedene Tasks und Kriterien behalten ihre gespeicherten Zuordnungen, ohne zur aktuellen Erreichung zu zählen.
14. Ein `PiF1o` darf `ACHIEVED` nur erreichen, wenn seine aktuelle Taskmenge nicht leer und vollständig `COMPLETED` ist, mindestens ein aktuelles `REQUIRED`-Kriterium besteht, jedes aktuelle Pflichtkriterium `ACTIVE` und durch anwendbare aktuelle Verifications erfüllt ist und alle relevanten Abhängigkeits-, WHY-, WHO-, Modell- und `RaN`-Bedingungen eingehalten sind.
15. `OPTIONAL`-Kriterien werden ausgewertet und dokumentiert, blockieren `ACHIEVED` aber nicht.
16. `ACHIEVED` ist terminal. Spätere Ziel-, Kriterien- oder Rahmenänderungen werden durch ein neues operatives Zukunftselement abgebildet.
17. Für `BOOLEAN` sind nur `EQUALS` und `NOT_EQUALS`, für `NUMERIC` nur numerische Vergleichsoperatoren und für `TEXTUAL` nur `EQUALS`, `NOT_EQUALS`, `CONTAINS` und `MATCHES` zulässig.
18. Ein höheres Zukunftselement darf `ACHIEVED` nur erreichen, wenn mindestens ein aktueller direkter Beitrag besteht und sein `contributionMode` erfüllt ist: `ALL` verlangt alle, `ANY` mindestens einen direkten Beitrag in `ACHIEVED`.
19. `REPLACED` und `REVOKED` gelten nicht als aktuelle Beiträge. Ein Ersatz zählt erst, wenn er selbst durch `CONTRIBUTES_TO` mit demselben Ziel verbunden ist.

**Kurzes Beispiel:** Eine Verification bindet Revision 4 eines Results und Revision 2 eines Kriteriums. Wird das Kriterium vor dem Commit auf Revision 3 geändert, endet der Versuch mit `CONFLICT`. Wird es erst später geändert, bleibt die Verification erhalten, zählt aber nicht mehr für die aktuelle Aggregation.

## 9. Task-Hierarchie, Abhängigkeiten und Status

1. Jeder Task besitzt genau ein `taskKind = ATOMIC | COMPOSITE`, genau ein `RESPONSIBLE_TEAM` und über `PiF1o ── DECOMPOSES_INTO ──► Task` genau einen gespeicherten operativen Zielkontext; die Zuordnung bleibt für ausgeschiedene Tasks erhalten.
2. Ein `ATOMIC`-Task besitzt keine ausgehende `DECOMPOSES_INTO`-Beziehung zu einem Task.
3. Ein `COMPOSITE`-Task besitzt mindestens einen direkten Untertask und keine Beziehungen `EXECUTED_BY`, `USES` oder `PRODUCES`. Ein aktueller Composite besitzt mindestens einen aktuellen direkten Untertask.
4. Ein Task besitzt höchstens einen direkten übergeordneten Task. Parent und Untertask gehören zum selben `PiF1o`; ein aktueller Untertask benötigt einen aktuellen Parent oder eine ausdrückliche gültige Neuzuordnung.
5. Die gespeicherte Task-Hierarchie bleibt zyklusfrei.
6. `DEPENDS_ON` darf Tasks verschiedener `PiF1o` verbinden, bildet aber weder Selbstbezüge noch Zyklen. Zusätzlich ist die gemeinsame Abschlussprüfsicht aus aktuellen Hierarchiebeziehungen und ausdrücklichen Voraussetzungen über alle erreichbaren Ziele zyklusfrei; ein gemischter Zyklus erzeugt `CONFLICT` mit Zykluspfad.
7. Eine `DEPENDS_ON`-Voraussetzung ist nur erfüllt, wenn ihr Ziel `COMPLETED` ist. `REPLACED` und `REVOKED` bleiben unerfüllte Voraussetzungen; kein automatisches Umhängen auf einen Nachfolger.
8. Ein freigegebener Task in `ACTIVE` oder `BLOCKED` mit einer eigenen unerfüllten Voraussetzung wird `BLOCKED`. `DRAFT` erfordert reguläre ausdrückliche Freigabe; terminale Tasks werden nicht wieder geöffnet.
9. Ein `ATOMIC`-Task in `ACTIVE` oder `COMPLETED` besitzt mindestens ein gültiges `EXECUTED_BY`; mindestens eines dieser RoleAssignments gehört zum verantwortlichen Team.
10. Ein atomarer Abschluss verlangt erfüllte Voraussetzungen, gültige Ausführungs- und Teamregeln, einschlägige `RaN` und ausdrückliche Abschlussbestätigung. Ein Result ist keine universelle Abschlussbedingung.
11. Für freigegebene Composites hat eine eigene unerfüllte Voraussetzung Vorrang und ergibt `BLOCKED`. Danach gilt für aktuelle direkte Untertasks: alle `COMPLETED` ergeben `COMPLETED`; mindestens ein `ACTIVE` ergibt `ACTIVE`; ohne `ACTIVE`, aber mit `BLOCKED`, ergibt sich `BLOCKED`; nur `DRAFT` oder `DRAFT`/`COMPLETED` ergeben `ACTIVE`.
12. Aktuell bedeutet weder `REPLACED` noch `REVOKED`; `COMPLETED` bleibt aktuell. Ersatz und Widerruf benötigen ausdrückliche Autorisierung, gültige aktuelle Ziel-/Parent-Zuordnung und nicht leere aktuelle Mengen. Ein ausgeschiedener Composite verbirgt keine aktuellen Nachfahren.
13. Jeder tatsächliche abgeleitete Statuswechsel wird je Auftrag einmal historisiert und revisioniert. Atomare und zusammengesetzte Tasks werden gemeinsam in Voraussetzung-vor-Nachfolger-Reihenfolge ausgewertet.
14. Eine Composite-Voraussetzung wird nicht automatisch auf Untertasks vererbt. Eine zusätzliche Ausführungssperre wird durch ausdrückliche Voraussetzungen der betroffenen Tasks modelliert.
15. Alle Operationen eines Auftrags bilden einen gemeinsamen Kandidatengraphen. Die Zyklusprüfung und Commit-Validierung erfolgen geschützt nach Abschnitt 12.8 des kanonischen Kontextdokuments.

## 10. Historisierungs- und Korrekturregeln

1. Nur eine tatsächliche Änderung eines vorhandenen Zustands erzeugt ein `PiH`.
2. `CREATED` erzeugt für die neu angelegte Entität kein `PiH`.
3. Jedes `PiH` bildet Eigenschaften und nach der Eigentümermatrix zugeordnete Beziehungen genau einer Revision ab; neue Snapshots verwenden Profil `2.0`.
4. Eine Abweichung in einem `PiH` erzeugt kein `PiH` des `PiH`, sondern eine `HistoricalCorrection`.
5. Die gültige `HistoryView` setzt ausschließlich aktive `correctedValue` als absolute Überlagerung auf den unveränderten Ursprung. Abgelöste Operationen werden nicht wieder abgespielt; ihre früheren `previousValue` werden beim Neuaufbau nicht gegen den Ursprung geprüft. Dadurch bleibt eine später berichtigte Ergänzung erhalten.
6. `correctedFields` folgt der geschlossenen Pointergrammatik aus Abschnitt 2.2.9 des kanonischen Kontextdokuments. Die Pointer sind eindeutig, kanonisch und nach Unicode-Codepunkten sortiert; beide Wertmaps besitzen exakt dieselben Schlüssel.
7. Nicht abgelöste Korrekturen eines `PiH` besitzen untereinander und jeweils intern überlappungsfreie kanonische Pfade nach Abschnitt 2.2.9. Gleichheit sowie Vorfahr-/Nachfahrbeziehungen zählen als Überlappung.
8. Keine Überlappung erlaubt kein `SUPERSEDES`. Genau eine überlappte aktive Korrektur muss vollständig abgelöst werden. Mehr als eine überlappte aktive Korrektur erzeugt wegen `SUPERSEDES = 0..1` einen `CONFLICT`. Eine ablösende Korrektur gehört zum selben `PiH` und enthält alle kanonischen Feldpfade der aktiven Vorgängerin unverändert mit ihren erneut angegebenen wirksamen Werten. Zusätzliche Pfade sind intern und gegenüber allen anderen aktiven Korrekturen überlappungsfrei. `SUPERSEDES` bleibt zeitlich vorwärts gerichtet und zyklusfrei.
9. `SUPERSEDES` verbindet nur Korrekturen desselben `PiH`, ist zeitlich vorwärts gerichtet und zyklusfrei.
10. Snapshot und wirksame Sicht hashen dasselbe kanonische `{stateData, relationshipData}`-Objekt nach Profil 2.0. `baseHistoryViewHash` bindet die Sicht vor Annahme und entspricht dem angeforderten `expectedHistoryViewHash`.
11. `SYNC` serialisiert alle JCI-Schreibwege nach Abschnitt 12.8 und berechnet die aktuelle `HistoryView` unter dem Gate erneut. Ein abweichender `expectedHistoryViewHash`, ein Profilfehler oder eine Pfadüberlappung außerhalb der Ablöseregel erzeugt `CONFLICT` ohne Korrektur.
12. Das `CAUSED_BY`-Ereignis einer Korrektur muss dasselbe Ereignis sein, das den über `CREATES_CORRECTION` verbundenen `SyncEvent` ausgelöst hat. Dieses `ChangeEvent` besitzt genau ein `TARGETS_HISTORY` zu demselben `PiH` und keine `CHANGED_BY`-Quelle.
13. Eine historische Korrektur verändert nicht automatisch den aktuellen Zustand der ursprünglichen Entität.
14. Ein `PiH` enthält genau den eigenen fachlichen Zustand der `originalRevision` gemäß Snapshotprofil und Revisionszuordnung. Fremde revisionsneutrale Dokumentationsbezüge schreiben diesen Zustand nicht rückwirkend um.
15. `contentHash` verwendet das kanonische Inhaltsobjekt und den exakten Unicode-/Zahlvertrag aus Abschnitt 2.2.9. Frühere Profile und Hashes bleiben unverändert; unbekannte oder inkompatible Profile werden abgewiesen.
16. Jeder `RelationshipSnapshot` besitzt Typ, Richtung, Gegenentitäts-ID, Gegenentitätstyp und typisierte Properties. Die stabile Schlüsselprojektion ist eindeutig; Korrekturen ändern unter einem vorhandenen Schlüssel keine Beziehungsidentität. Ganzbeziehung und Property überlappen.

**Kurzes Beispiel:** `/stateData/properties/name` und `/stateData/properties/description` sind unabhängig. Eine ganze Beziehung und ihre `/properties/validFrom` überlappen. Eine solche Überlappung verlangt die vollständige Ablösung genau einer aktiven Vorgängerin gegen die aktuelle Sicht; Überschneidung mit mehreren Vorgängerinnen wird abgewiesen.

## 11. SYNC- und Revisionsregeln

1. Ein `SyncRun` ist technischer Zustand und kein Knoten des JCI-Graphen.
2. Ein angenommenes `ChangeEvent` besitzt unveränderlich `idempotencyKey`, `targetEntityId`, `targetEntityType` und `requestedRevision` und plant mindestens einen technischen `SyncRun`.
3. Solange noch kein Versuch beendet wurde, ist `TRIGGERS = 0` zulässig. Jeder beendete oder kontrolliert abgebrochene `SyncRun` erzeugt genau ein `SyncEvent` mit eindeutiger `runId` und ergänzt genau eine `TRIGGERS`-Kante append-only.
4. Bei `CREATED` müssen Ziel-ID frei und `requestedRevision = null` sein. Nur `SUCCESS` erzeugt das neue Ziel mit `revision = 1`, `CREATED_BY` und genau einem `CHANGED_BY`. Für dieses neue Ziel entsteht kein `PiH`; vorhandene veränderliche Eigentümer, deren fachliche Beziehungen sich dabei ändern, erhalten nach Abschnitt 2.2.8 ein eigenes `PiH`. `CONFLICT` oder `FAILED` übernimmt weder das Ziel noch ein Fachdelta oder Historie.
5. Bei allen normalen Änderungen muss das Ziel vorhanden und `requestedRevision` gleich seiner aktuellen Revision sein.
6. Bei `HISTORICAL_CORRECTION` muss das Ziel ein vorhandenes `PiH`, `requestedRevision = 1`, `TARGETS_HISTORY = 1` und `CHANGED_BY = 0` sein.
7. Ein fehlgeschlagener Versuch erzeugt ein `SyncEvent` mit `outcome = FAILED`.
8. Unvollständige fachliche Änderungen eines fehlgeschlagenen Versuchs werden zurückgerollt.
9. `completedAt` eines `SyncEvent` liegt nicht vor `startedAt`.
10. Alle Zählwerte eines `SyncEvent` sind nicht negativ und stimmen mit den verbundenen Entitäten überein. `SUCCESS` und `CONFLICT` erfordern `affectedCount >= 1`; nur ein frühes `FAILED` vor Zielauflösung erlaubt `affectedCount = 0`.
11. Wiederholungen dürfen dieselbe fachliche Änderung nicht mehrfach übernehmen; jeder tatsächlich ausgeführte Versuch besitzt eine eigene `runId` und ein eigenes `SyncEvent`.
12. `conflictCount` eines `SyncEvent` entspricht der Anzahl der über `DETECTED_BY` invers zugeordneten `RaNConflict`-Objekte.
13. Eine Entität mit `status = REPLACED` besitzt genau eine ausgehende `REPLACED_BY`-Beziehung zu demselben konkreten Entitätstyp.
14. Eine Entität in einem anderen Status besitzt keine ausgehende `REPLACED_BY`-Beziehung.
15. `REPLACED_BY` besitzt keine Selbstbezüge oder Zyklen; ein Nachfolger darf mehrere Vorgänger zusammenführen.
16. Bei `CONFLICT` oder `FAILED` entstehen für nicht übernommene Zustände weder neue Revisionen noch `PiH`; das abschließende `SyncEvent` und erforderliche `RaNConflict`-Objekte bleiben davon getrennte Versuchsdokumentation.
17. Ist die Speicherung eines abschließenden `SyncEvent` vorübergehend technisch unmöglich, muss sie mit derselben `runId`, demselben `ChangeEvent` und derselben `idempotencyKey` nachgeholt werden, ohne die Fachänderung erneut auszuführen.
18. Das technologieunabhängige Austauschformat verwendet `schemaVersion = "2.0"`. `HISTORICAL_CORRECTION` verwendet einen strukturierten Payload mit `expectedHistoryViewHash` statt generischer `operations`.
19. Alle JCI-Schreibwege verwenden einen gemeinsamen technischen Commit-Gate je Datenbank-/Modellbestand und erhöhen bei Übernahme die `graphEpoch`, auch bei revisionsneutralen Nachweisen. Der Gate ist kein JCI-Knoten.
20. Die Sperre wird vor dem Lesen der vollständigen relevanten Graphsicht erworben. Neue Regeln, Nachweise, Kanten, Abwesenheiten und Zeitgültigkeiten werden mitgeprüft; eine bloße Revisionsprüfung der Schreibmenge genügt nicht.
21. Der vollständige normalisierte Payload und seine unveränderliche Identitätsbindung werden dauerhaft gespeichert. Gleiche Kennung mit anderem Payload ist unzulässig; geänderte Ausgangsrevision verlangt einen neuen Auftrag.
22. Run-Eigentümerschaft, Fencing und idempotenter Commitbeleg verhindern Doppelübernahme. Bei `SUCCESS` werden Fachdelta, `PiH`, Beziehungen und `SyncEvent` zusammen mit dem Commitbeleg atomar gespeichert. Unbekannter Commit-Ausgang wird vor Wiederholung geklärt.
23. Alle zeitabhängigen Prüfungen gelten für den dokumentierten Datenbank-Entscheidungszeitpunkt unmittelbar vor Übernahme unter der Sperre. Ein No-op darf `SUCCESS` mit `changedCount = 0` ohne neue Revision und ohne `PiH` liefern.

## 12. Initialer Bootstrap

1. Der Bootstrap ist nur in einem vollständig leeren Graphen und genau einmal zulässig.
2. Er läuft in einer atomaren Transaktion unter dem eindeutigen vorab eingerichteten technischen Gate; bei Fehler bleibt kein fachlicher Teilgraph bestehen. Ein technischer Gate verletzt die Leerheitsbedingung für `JCIEntity` nicht.
3. Der Minimalgraph enthält eine `RoFOrg`, ein `RoFTeam`, ein technisches `RoFTeamMember`, eine `RoFRole`, genau ein Root-`RoleAssignment` mit `bootstrapKey = "ROOT"` und eine `SYNC`-Definition samt erforderlichen RoF-Beziehungen.
4. Alle sechs Bootstrap-Entitäten entstehen unmittelbar mit `status = ACTIVE`, `revision = 1` sowie demselben `createdAt` und `updatedAt`. Vorhandene `validFrom`-Werte der Typen und Beziehungen entsprechen demselben Bootstrapzeitpunkt. Dies ist die einzige Ausnahme vom regulären `DRAFT`-Start.
5. Nur das Root-`RoleAssignment` darf dauerhaft ohne `CREATED_BY` bestehen. Alle übrigen Bootstrap-Entitäten besitzen genau ein `CREATED_BY` zum Root-`RoleAssignment`.
6. Der Bootstrap erzeugt weder `ChangeEvent`, `SyncRun`, `SyncEvent` noch `PiH`.
7. Nach erfolgreichem Commit sind Wiederholung und ein zweites Root-`RoleAssignment` verboten. Alle weiteren Änderungen verwenden den normalen SYNC-Prozess.
8. Ein Import ist kein Bootstrap. Importierte Entitäten ohne vollständige Provenienz bleiben `DRAFT`, bis sie regulär validiert wurden.

**Kurzes Beispiel:** Das Deployment erzeugt in der leeren Datenbank Organisation, Administrationsteam, technisches Mitglied, Rolle, Root-Zuordnung und aktive SYNC-Definition gemeinsam. Erst danach fordert das Root-`RoleAssignment` regulär die erste fachliche Entität an.

## 13. Geschlossener Regelstand

Die Statusvorbedingungen, Kardinalitäten, Rückverfolgbarkeits-, Zukunfts-, Task-, RoF-, ERoF-, RaN-, Historisierungs- und SYNC-Regeln dieser Version sind verbindlich abgeschlossen. Neue domänenspezifische Untertypen dürfen nur über eine versionierte Modelländerung ergänzt werden und müssen vor Aktivierung eigene Statusvorbedingungen sowie automatisierte Tests erhalten.
