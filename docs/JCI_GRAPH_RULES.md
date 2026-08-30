# JCI-Graphregeln

## 1. Status und Zweck

Dieses Dokument legt technologieunabhängige Kardinalitäten und Invarianten des JCI-Graphen fest. Die fachliche Bedeutung stammt aus [JCI_CONTEXT.md](JCI_CONTEXT.md), der zulässige Typkatalog aus [JCI_ONTOLOGY.md](JCI_ONTOLOGY.md). Bei einem Konflikt gilt `JCI_CONTEXT.md`.

## 2. Allgemeine Entitätsregeln

1. Jede konkrete `JCIEntity` besitzt genau eine global eindeutige und unveränderliche UUID als `id`.
2. `entityType` stimmt mit dem konkreten Entitätstyp überein.
3. `revision` ist eine positive Ganzzahl und beginnt bei `1`.
4. Bei einer tatsächlichen fachlichen Änderung wird der vorherige Zustand als `PiH` gespeichert und die Revision des aktuellen Elements um genau eins erhöht.
5. Jeder fachliche Statuswechsel ist eine tatsächliche Änderung.
6. `updatedAt` liegt nicht vor `createdAt`; bei unveränderlichen Entitäten sind beide Werte gleich.
7. `PiH`, `ChangeEvent`, `SyncEvent` und `HistoricalCorrection` besitzen dauerhaft `status = RECORDED` und `revision = 1`.
8. Diese vier Entitätstypen werden nicht verändert, gelöscht oder erneut historisiert.
9. Leere Pflichtfelder sind unzulässig.
10. Fachliche Beziehungen werden ausschließlich als Kanten und nicht zusätzlich als ID-Listen gespeichert.

## 3. Statusregeln

| Entitätstypen                                             | Zulässige Statuswerte                                 |
| --------------------------------------------------------- | ----------------------------------------------------- |
| `CiV`, `RaN`, `SYNC`, RoF- und ERoF-Graphobjekte          | `DRAFT`, `ACTIVE`, `REPLACED`, `REVOKED`              |
| `PiF2`, `PiF1s`, `PiF1t`, `PiF1o`                         | `DRAFT`, `ACTIVE`, `ACHIEVED`, `REPLACED`, `REVOKED`  |
| `Task`                                                    | `DRAFT`, `ACTIVE`, `BLOCKED`, `COMPLETED`, `REPLACED`, `REVOKED` |
| `Result`                                                  | `DRAFT`, `ACTIVE`, `COMPLETED`, `REPLACED`, `REVOKED` |
| `SuccessCriterion`, `Evidence`                            | `DRAFT`, `ACTIVE`, `REPLACED`, `REVOKED`              |
| `Verification`                                            | `COMPLETED`                                           |
| `RaNConflict`                                             | `OPEN`, `RESOLVED`                                    |
| `PiH`, `ChangeEvent`, `SyncEvent`, `HistoricalCorrection` | `RECORDED`                                            |

Aus `ACHIEVED`, `REPLACED`, `REVOKED`, `COMPLETED`, `RECORDED` und `RESOLVED` führt kein Übergang zurück in einen veränderbaren Zustand. Eine Fortsetzung wird als neue Entität modelliert.

Verbindliche Übergangsregeln:

1. Veränderliche Fachentitäten werden als `DRAFT` erzeugt und dürfen erst nach vollständiger Validierung `ACTIVE` werden.
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
12. Eine fachliche Beziehungsänderung ändert beide bereits vorhandenen veränderlichen Endpunkte. Beide erhalten eine neue Revision und jeweils ein `PiH`; ein im selben Auftrag neu erzeugter Endpunkt erhält noch kein `PiH`.

## 4. Kardinalitäten

Die Spalte „Ziele je Quelle“ gilt in Pfeilrichtung; „Quellen je Ziel“ gilt in Gegenrichtung.

### 4.1 Zweck und Zukunft

| Quelle  | Beziehung              | Ziel    | Ziele je Quelle | Quellen je Ziel |
| ------- | ---------------------- | ------- | --------------: | --------------: |
| `PiH`   | `PROVIDES_CONTEXT_TO`  | `CiV`   |          `0..n` |          `0..n` |
| `CiV`   | `INSCRIBES_PURPOSE_IN` | `PiF2`  |          `0..n` |          `1..n` |
| `PiF1s` | `CONTRIBUTES_TO`       | `PiF2`  |          `1..n` |          `0..n` |
| `PiF1t` | `CONTRIBUTES_TO`       | `PiF1s` |          `1..n` |          `0..n` |
| `PiF1o` | `CONTRIBUTES_TO`       | `PiF1t` |          `1..n` |          `0..n` |

### 4.2 Operative Umsetzung und Prüfung

| Quelle           | Beziehung              | Ziel               | Ziele je Quelle | Quellen je Ziel |
| ---------------- | ---------------------- | ------------------ | --------------: | --------------: |
| `PiF1o`          | `HAS_SUCCESS_CRITERIA` | `SuccessCriterion` |          `1..n` |             `1` |
| `PiF1o`          | `ACCOUNTABLE_MEMBER`   | `RoFTeamMember`    |             `1` |          `0..n` |
| `PiF1o`          | `DECOMPOSES_INTO`      | `Task`             |          `1..n` |             `1` |
| `Task`           | `DECOMPOSES_INTO`      | `Task`             |          `0..n` |          `0..1` |
| `Task`           | `DEPENDS_ON`           | `Task`             |          `0..n` |          `0..n` |
| `Task`           | `RESPONSIBLE_TEAM`     | `RoFTeam`          |             `1` |          `0..n` |
| `Task`           | `EXECUTED_BY`          | `RoleAssignment`   |          `0..n` |          `0..n` |
| `Task`           | `USES`                 | `ERoFObject`       |          `0..n` |          `0..n` |
| `RoleAssignment` | `USES`                 | `ERoFObject`       |          `0..n` |          `1..n` |
| `ERoFObject`     | `OWNED_BY`             | `RoFOrg`           |          `0..n` |          `0..n` |
| `Task`           | `PRODUCES`             | `Result`           |          `0..n` |             `1` |
| `Verification`   | `EVALUATES`            | `Result`           |             `1` |          `0..n` |
| `Verification`   | `CHECKS`               | `SuccessCriterion` |             `1` |          `0..n` |
| `Verification`   | `USES_EVIDENCE`        | `Evidence`         |          `0..n` |          `0..n` |
| `Verification`   | `SUPERSEDES`           | `Verification`     |          `0..1` |          `0..1` |

### 4.3 Organisation und Rollen

| Quelle               | Beziehung        | Ziel             | Ziele je Quelle | Quellen je Ziel |
| -------------------- | ---------------- | ---------------- | --------------: | --------------: |
| `RoFOrg`             | `HAS_TEAM`       | `RoFTeam`        |          `1..n` |             `1` |
| `RoFTeam`            | `HAS_MEMBER`     | `RoFTeamMember`  |          `1..n` |          `1..n` |
| `RoFTeamMember`      | `HAS_ROLE`       | `RoFRole`        |          `1..n` |          `0..n` |
| `RoFTeamMember`      | `HAS_ASSIGNMENT` | `RoleAssignment` |          `0..n` |             `1` |
| `RoleAssignment`     | `IN_TEAM`        | `RoFTeam`        |             `1` |          `0..n` |
| `RoleAssignment`     | `ACTIVATES_ROLE` | `RoFRole`        |             `1` |          `0..n` |
| `RoFOrgRelationship` | `SOURCE_ORG`     | `RoFOrg`         |             `1` |          `0..n` |
| `RoFOrgRelationship` | `TARGET_ORG`     | `RoFOrg`         |             `1` |          `0..n` |
| `RoFOrgRelationship` | `REPRESENTED_BY` | `RoleAssignment` |          `2..n` |          `0..n` |

### 4.4 Akteure und Nachweise

| Quelle                 | Beziehung       | Ziel             | Ziele je Quelle | Quellen je Ziel |
| ---------------------- | --------------- | ---------------- | --------------: | --------------: |
| `JCIEntity`            | `CREATED_BY`    | `RoleAssignment` |          `0..1` |          `0..n` |
| `ChangeEvent`          | `REQUESTED_BY`  | `RoleAssignment` |             `1` |          `0..n` |
| `HistoricalCorrection` | `CORRECTED_BY`  | `RoleAssignment` |             `1` |          `0..n` |
| `ChangeEvent`          | `USES_EVIDENCE` | `Evidence`       |          `0..n` |          `0..n` |
| `HistoricalCorrection` | `USES_EVIDENCE` | `Evidence`       |          `0..n` |          `0..n` |

### 4.5 Veränderung, Historisierung und Korrektur

| Quelle                      | Beziehung              | Ziel                   | Ziele je Quelle | Quellen je Ziel |
| --------------------------- | ---------------------- | ---------------------- | --------------: | --------------: |
| historisierbare `JCIEntity` | `CHANGED_BY`           | `ChangeEvent`          |          `0..n` |             `1` |
| `ChangeEvent`               | `TRIGGERS`             | `SyncEvent`            |          `1..n` |             `1` |
| `SyncEvent`                 | `EXECUTES`             | `SYNC`                 |             `1` |          `0..n` |
| `SyncEvent`                 | `AFFECTS`              | `JCIEntity`            |          `1..n` |          `0..n` |
| historisierbare `JCIEntity` | `HAS_HISTORICAL_STATE` | `PiH`                  |          `0..n` |             `1` |
| `SyncEvent`                 | `CREATES_HISTORY`      | `PiH`                  |          `0..n` |             `1` |
| `HistoricalCorrection`      | `CORRECTS`             | `PiH`                  |             `1` |          `0..n` |
| `HistoricalCorrection`      | `CAUSED_BY`            | `ChangeEvent`          |             `1` |          `0..n` |
| `SyncEvent`                 | `CREATES_CORRECTION`   | `HistoricalCorrection` |          `0..n` |             `1` |
| `HistoricalCorrection`      | `SUPERSEDES`           | `HistoricalCorrection` |          `0..1` |          `0..1` |
| ersetzbare `JCIEntity`      | `REPLACED_BY`          | gleicher konkreter Typ |          `0..1` |          `0..n` |

`RaN ── GOVERNS ──► zulässige JCIEntity` besitzt in beiden Richtungen `0..n`.

| Quelle | Beziehung | Ziel | Ziele je Quelle | Quellen je Ziel |
| ------ | --------- | ---- | --------------: | --------------: |
| `RaN` | `APPLIES_IN` | `RoFOrg` oder `RoFTeam` | `0..1` | `0..n` |

| Quelle        | Beziehung          | Ziel             | Ziele je Quelle | Quellen je Ziel |
| ------------- | ------------------ | ---------------- | ---------------:| ---------------:|
| `RaNConflict` | `CONFLICTING_RULE` | `RaN`            |          `1..n` |          `0..n` |
| `RaNConflict` | `AFFECTS`          | `JCIEntity`      |          `1..n` |          `0..n` |
| `RaNConflict` | `DETECTED_BY`      | `SyncEvent`      |             `1` |          `0..n` |
| `RaNConflict` | `RESOLVED_BY`      | `RoleAssignment` |          `0..1` |          `0..n` |
| `RaNConflict` | `RESOLVED_THROUGH` | `ChangeEvent`    |          `0..1` |          `0..n` |
| `RaNConflict` | `USES_EVIDENCE`    | `Evidence`       |          `0..n` |          `0..n` |

## 5. Akteurs- und Evidenzregeln

1. Akteure werden als Beziehungen zu `RoleAssignment` gespeichert; Text- oder ID-Duplikate sind unzulässig.
2. Eine fachlich aktive oder abgeschlossene `JCIEntity` besitzt genau eine `CREATED_BY`-Beziehung.
3. `CREATED_BY = 0` ist nur für Bootstrap- und Importzustände vor fachlicher Aktivierung zulässig.
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

1. Jede aktive `RoFOrg` besitzt mindestens ein Team; jedes aktive Team mindestens ein Mitglied.
2. Ein `RoleAssignment` gehört genau zu einem Mitglied, einem Team und einer aktivierten Rolle.
3. Das Mitglied eines `RoleAssignment` muss Mitglied des verbundenen Teams sein und die aktivierte Rolle besitzen.
4. Mindestens ein ausführendes `RoleAssignment` eines aktiven oder abgeschlossenen `ATOMIC`-Tasks gehört zu dessen `RESPONSIBLE_TEAM`.
5. Jedes aktive `ERoFObject` wird von mindestens einem `RoleAssignment` verwendet.
6. Eine direkte `Task ── USES ──► ERoFObject`-Beziehung ist nur für `ATOMIC`-Tasks zulässig und setzt voraus, dass mindestens ein ausführendes `RoleAssignment` dasselbe Objekt verwendet.
7. `SOURCE_ORG` und `TARGET_ORG` einer `RoFOrgRelationship` müssen verschieden sein.
8. `SUBSIDIARY` ist gerichtet und über beliebig viele Ebenen zulässig, muss aber zyklusfrei bleiben.
9. `PARTNERSHIP` ist fachlich wechselseitig; die gespeicherte Richtung dient nur der Eindeutigkeit.
10. Eine aktive Organisationsbeziehung besitzt mindestens ein vertretendes `RoleAssignment` aus jeder beteiligten Organisation.
11. `HAS_MEMBER` und `HAS_ROLE` besitzen `validFrom` und optional `validUntil`; das Ende liegt nicht vor dem Beginn.
12. Der Gültigkeitszeitraum eines `RoleAssignment` liegt vollständig innerhalb einer gleichzeitig gültigen Mitgliedschaft im Team und eines gleichzeitig gültigen Rollenbesitzes.
13. Ist `allocation` angegeben, gilt `0 < allocation <= 1`; die Summe gleichzeitig gültiger Werte eines Mitglieds überschreitet `1` nicht.
14. Eine aktive `PARTNERSHIP` speichert die Organisation mit der lexikografisch kleineren UUID als `SOURCE_ORG`.
15. Aktive Organisationsbeziehungen desselben Typs und Organisationspaars besitzen keine überlappenden Gültigkeitszeiträume.
16. `INTERNAL` beziehungsweise `EXTERNAL` wird je betrachteter Organisation abgeleitet: Eine `OWNED_BY`-Kante zu ihr ergibt `INTERNAL`, ihr Fehlen `EXTERNAL`.

## 7. RaN-Priorität und Konflikte

1. Für eine Entscheidung werden nur `RaN` mit `status = ACTIVE`, gültigem Zeitintervall, passendem `scopeType`, zutreffendem `APPLIES_IN`, passendem `governedTypes` und einschlägiger `GOVERNS`-Beziehung berücksichtigt.
2. `priority` ist eine verpflichtende Ganzzahl; eine größere Zahl bedeutet höheren Vorrang bei einem tatsächlichen Widerspruch.
3. `ruleType` begründet keinen automatischen Vorrang.
4. Vereinbare anwendbare Regeln gelten gemeinsam, unabhängig von ihrer relativen Priorität.
5. Bei widersprüchlichen Regeln unterschiedlicher Priorität gilt für den konkreten Widerspruch die höher priorisierte Regel. Die andere Regel bleibt außerhalb dieses Widerspruchs aktiv.
6. Bei mindestens zwei widersprüchlichen Regeln derselben höchsten einschlägigen Priorität entsteht genau ein `RaNConflict` mit `conflictType = PRIORITY_TIE` für die Konfliktmenge und Entscheidung.
7. Ist Anwendbarkeit oder Vereinbarkeit nicht eindeutig auswertbar, entsteht ein `RaNConflict` mit `conflictType = UNEVALUABLE`; die Priorität darf Unsicherheit nicht übergehen.
8. Ein offener Konflikt besitzt einen nicht leeren und innerhalb des Veränderungsauftrags eindeutigen `conflictKey`, mindestens eine `CONFLICTING_RULE`, mindestens ein `AFFECTS`, genau ein `DETECTED_BY`, kein `RESOLVED_BY` und kein `RESOLVED_THROUGH`. `PRIORITY_TIE` erfordert mindestens zwei Konfliktregeln; für `UNEVALUABLE` genügt mindestens eine nicht eindeutig auswertbare Regel.
9. Ein gelöster Konflikt besitzt genau ein `RESOLVED_BY`, genau ein `RESOLVED_THROUGH` und ein nicht leeres `resolution` sowie `resolvedAt`.
10. `RESOLVED` darf erst gesetzt werden, wenn ein nachfolgender erfolgreicher Synchronisationslauf bestätigt, dass der dokumentierte Widerspruch nicht mehr besteht.
11. Der Wechsel von `OPEN` zu `RESOLVED` ist eine fachliche Änderung; der offene Ausgangszustand wird als `PiH` historisiert. `RESOLVED` ist terminal.
12. Ein offener Konflikt blockiert automatische Änderungen, deren Zulässigkeit von seiner Auflösung abhängt; unabhängige Prüfungen bleiben möglich.
13. `governedTypes` ist nicht leer; jedes `GOVERNS`-Ziel besitzt einen aufgeführten konkreten Typ.
14. `GLOBAL` und `ENTITY` besitzen kein `APPLIES_IN`. `ORGANIZATION` besitzt genau eine Beziehung zu `RoFOrg`; `TEAM` genau eine zu `RoFTeam`.
15. Jede Condition besitzt `combiner = ALL | ANY` und mindestens eine auswertbare Klausel aus `path`, `operator` und gegebenenfalls `value`.
16. `REQUIRE` erlaubt bei wahrer und verweigert bei falscher Bedingung. `PROHIBIT` verweigert bei wahrer Bedingung. `PERMIT` erlaubt bei wahrer Bedingung. Falsches `PROHIBIT` oder `PERMIT` trifft keine eigene Entscheidung.
17. Eine Regelverletzung blockiert die angeforderte Entscheidung, erzeugt allein aber keinen `RaNConflict`.
18. Ein Widerspruch liegt nur vor, wenn Regeln mit gleichem `decisionKey`, überlappendem Scope und gemeinsamem Ziel gleichzeitig erlauben und verweigern.

## 8. Erfolgskriterien und Erreichung

1. Jedes `SuccessCriterion` besitzt genau ein `requirementLevel = REQUIRED | OPTIONAL`, ein `evaluationMode = ALL | ANY`, einen zum `measurementType` passenden `operator` und einen gültigen `targetValue`.
2. Ohne ausdrücklich abweichende Festlegung gelten `requirementLevel = REQUIRED` und `evaluationMode = ALL`.
3. Jedes `PiF1o` besitzt mindestens ein `REQUIRED`-Kriterium.
4. Eine aktuelle `Verification` ist abgeschlossen und wird von keiner anderen Verification über `SUPERSEDES` abgelöst.
5. `SUPERSEDES` verbindet nur Verifications mit demselben `Result` und demselben `SuccessCriterion`.
6. Verification-Ketten sind zeitlich vorwärts gerichtet, besitzen keine Verzweigung und sind zyklusfrei.
7. Bei `evaluationMode = ALL` ist ein Kriterium erfüllt, wenn mindestens eine aktuelle Verification existiert und alle aktuellen Verifications `VALID` sind.
8. Bei `evaluationMode = ANY` ist ein Kriterium erfüllt, wenn mindestens eine aktuelle Verification `VALID` ist.
9. `INVALID`, `INCONCLUSIVE` und eine fehlende aktuelle Verification erfüllen ein Kriterium nicht; bei `ALL` verhindert bereits eine davon die Erfüllung.
10. Berücksichtigt werden ausschließlich Verifications von Results, deren Tasks zum selben `PiF1o` gehören wie das geprüfte Kriterium.
11. Ein `PiF1o` darf `ACHIEVED` erreichen, wenn alle `REQUIRED`-Kriterien erfüllt, alle zugeordneten Tasks `COMPLETED`, alle Task-Abhängigkeiten erfüllt, alle berücksichtigten Verifications abgeschlossen und alle relevanten Modell- und `RaN`-Regeln eingehalten sind.
12. `OPTIONAL`-Kriterien werden ausgewertet und dokumentiert, blockieren `ACHIEVED` aber nicht.
13. `ACHIEVED` ist terminal. Spätere Ziel-, Kriterien- oder Rahmenänderungen werden durch ein neues operatives Zukunftselement abgebildet.
14. Für `BOOLEAN` sind nur `EQUALS` und `NOT_EQUALS`, für `NUMERIC` nur numerische Vergleichsoperatoren und für `TEXTUAL` nur `EQUALS`, `NOT_EQUALS`, `CONTAINS` und `MATCHES` zulässig.
15. Ein höheres Zukunftselement darf `ACHIEVED` nur erreichen, wenn mindestens ein aktueller direkter Beitrag besteht und sein `contributionMode` erfüllt ist: `ALL` verlangt alle, `ANY` mindestens einen direkten Beitrag in `ACHIEVED`.
16. `REPLACED` und `REVOKED` gelten nicht als aktuelle Beiträge. Ein Ersatz zählt erst, wenn er selbst durch `CONTRIBUTES_TO` mit demselben Ziel verbunden ist.

## 9. Task-Hierarchie, Abhängigkeiten und Status

1. Jeder Task besitzt genau ein `taskKind = ATOMIC | COMPOSITE`, genau ein `RESPONSIBLE_TEAM` und über `PiF1o ── DECOMPOSES_INTO ──► Task` genau einen operativen Zielkontext.
2. Ein `ATOMIC`-Task besitzt keine ausgehende `DECOMPOSES_INTO`-Beziehung zu einem Task.
3. Ein `COMPOSITE`-Task besitzt mindestens einen direkten Untertask und keine Beziehungen `EXECUTED_BY`, `USES` oder `PRODUCES`.
4. Ein Task besitzt höchstens einen direkten übergeordneten Task. Übergeordneter Task und Untertask gehören zum selben `PiF1o`.
5. Die durch `Task ── DECOMPOSES_INTO ──► Task` gebildete Hierarchie ist zyklusfrei.
6. `DEPENDS_ON` darf Tasks desselben oder verschiedener `PiF1o` verbinden, bildet aber keine Selbstbezüge oder Zyklen.
7. Eine `DEPENDS_ON`-Voraussetzung ist nur erfüllt, wenn der Ziel-Task `COMPLETED` ist. `REPLACED` und `REVOKED` erfüllen sie nicht.
8. Ein Task mit mindestens einer nicht erfüllten Voraussetzung besitzt `status = BLOCKED`. Sind danach alle Voraussetzungen erfüllt, darf `SYNC` den zulässigen Folgestatus neu bestimmen.
9. Ein `ATOMIC`-Task in `ACTIVE` oder `COMPLETED` besitzt mindestens ein `EXECUTED_BY`; mindestens eines dieser RoleAssignments gehört zum verantwortlichen Team.
10. Ein `ATOMIC`-Task darf `COMPLETED` erreichen, wenn alle Voraussetzungen abgeschlossen, die Ausführungs- und Teamregeln erfüllt, relevante `RaN` eingehalten und der Abschluss bestätigt sind. Ein Result ist keine universelle Abschlussbedingung.
11. Der Status eines `COMPOSITE`-Tasks wird aus den effektiven direkten Untertasks abgeleitet: ausschließlich `DRAFT` ergibt `DRAFT`; alle `COMPLETED` ergeben `COMPLETED`; mindestens ein `ACTIVE` sowie eine Mischung aus `DRAFT` und `COMPLETED` ergeben `ACTIVE`; ohne `ACTIVE`, aber mit mindestens einem `BLOCKED`, ergibt sich `BLOCKED`.
12. Ein `REPLACED`-Untertask wird nur durch einen über `REPLACED_BY` verbundenen Nachfolger ersetzt, der selbst direkter Untertask desselben Parents ist. Ein weiterhin verbundener `REVOKED`-Untertask oder ein Ersatz ohne diese Einbindung erzeugt einen Konflikt.
13. Jeder abgeleitete Statuswechsel ist eine fachliche Änderung und unterliegt Historisierung und Revision.

## 10. Historisierungs- und Korrekturregeln

1. Nur eine tatsächliche Änderung eines vorhandenen Zustands erzeugt ein `PiH`.
2. `CREATED` erzeugt für die neu angelegte Entität kein `PiH`.
3. Jedes `PiH` bildet Eigenschaften und Beziehungen genau einer Revision der ursprünglichen Entität ab.
4. Eine Abweichung in einem `PiH` erzeugt kein `PiH` des `PiH`, sondern eine `HistoricalCorrection`.
5. Der gültige historische Lesestand besteht aus dem unveränderten `PiH` und seinen nicht abgelösten Korrekturen.
6. `SUPERSEDES` darf nur Korrekturen desselben `PiH` verbinden und muss zeitlich vorwärts gerichtet und zyklusfrei sein.
7. Das `CAUSED_BY`-Ereignis einer Korrektur muss dasselbe Ereignis sein, das den über `CREATES_CORRECTION` verbundenen `SyncEvent` ausgelöst hat.
8. Eine historische Korrektur verändert nicht automatisch den aktuellen Zustand der ursprünglichen Entität.
9. Ein `PiH` enthält genau die Eigenschaften und zu diesem Zeitpunkt gültigen ein- und ausgehenden fachlichen Beziehungen der angegebenen `originalRevision`.
10. `contentHash` entspricht SHA-256 der kanonischen Serialisierung aus `StateSnapshot` und sortierten `RelationshipSnapshot`-Einträgen.
11. Jeder `RelationshipSnapshot` besitzt Typ, Richtung, Gegenentitäts-ID, Gegenentitätstyp und eine typisierte Property-Map.
12. `correctedFields`, `previousValue` und `correctedValue` besitzen dieselbe Schlüsselmenge; bei `ADDITION` ist der vorherige Wert des ergänzten Pfads `NULL`.

## 11. SYNC- und Revisionsregeln

1. Ein `SyncRun` ist technischer Zustand und kein Knoten des JCI-Graphen.
2. Ein `SyncEvent` entsteht erst nach Abschluss oder kontrolliertem Abbruch eines `SyncRun`.
3. Ein fehlgeschlagener Versuch erzeugt ein `SyncEvent` mit `outcome = FAILED`.
4. Unvollständige fachliche Änderungen eines fehlgeschlagenen Versuchs werden zurückgerollt.
5. `completedAt` eines `SyncEvent` liegt nicht vor `startedAt`.
6. Alle Zählwerte eines `SyncEvent` sind nicht negativ und stimmen mit den verbundenen Entitäten überein.
7. Wiederholungen dürfen dieselbe fachliche Änderung nicht mehrfach übernehmen.
8. `conflictCount` eines `SyncEvent` entspricht der Anzahl der über `DETECTED_BY` invers zugeordneten `RaNConflict`-Objekte.
9. Eine Entität mit `status = REPLACED` besitzt genau eine ausgehende `REPLACED_BY`-Beziehung zu demselben konkreten Entitätstyp.
10. Eine Entität in einem anderen Status besitzt keine ausgehende `REPLACED_BY`-Beziehung.
11. `REPLACED_BY` besitzt keine Selbstbezüge oder Zyklen; ein Nachfolger darf mehrere Vorgänger zusammenführen.
12. Bei `CONFLICT` oder `FAILED` entstehen für nicht übernommene Zustände weder neue Revisionen noch `PiH`; das abschließende `SyncEvent` und erforderliche `RaNConflict`-Objekte bleiben davon getrennte Versuchsdokumentation.
13. Ist die Speicherung eines abschließenden `SyncEvent` vorübergehend technisch unmöglich, muss sie mit derselben `runId`, demselben `ChangeEvent` und derselben Idempotenzkennung nachgeholt werden, ohne die Fachänderung erneut auszuführen.

## 12. Geschlossener Regelstand

Die Statusvorbedingungen, Kardinalitäten, Rückverfolgbarkeits-, Zukunfts-, Task-, RoF-, ERoF-, RaN-, Historisierungs- und SYNC-Regeln dieser Version sind verbindlich abgeschlossen. Neue domänenspezifische Untertypen dürfen nur über eine versionierte Modelländerung ergänzt werden und müssen vor Aktivierung eigene Statusvorbedingungen sowie automatisierte Tests erhalten.
