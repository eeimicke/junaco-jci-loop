# JCI-SYNC-Spezifikation

## 1. Status und Zweck

Dieses Dokument beschreibt den technologieunabhängigen Ablauf von `SYNC`. Die fachliche Bedeutung richtet sich nach [JCI_CONTEXT.md](JCI_CONTEXT.md), die Typen nach [JCI_ONTOLOGY.md](JCI_ONTOLOGY.md) und die gültigen Graphzustände nach [JCI_GRAPH_RULES.md](JCI_GRAPH_RULES.md).

## 2. Begriffe

```text
SYNC      = gespeicherte und historisierbare Definition der Synchronisationslogik
SyncRun   = veränderbarer technischer Zustand während eines Ausführungsversuchs
SyncEvent = unveränderliche fachliche Dokumentation nach Abschluss oder Abbruch
```

`SyncRun` ist keine `JCIEntity`, kein `GraphObject` und kein JCI-Kernelement. Die Implementierung darf ihn in einer Laufzeit-, Queue- oder Protokollstruktur speichern. Im fachlichen JCI-Graphen wird er nicht als Zwischenknoten angelegt.

## 3. Verbindlicher Zusammenhang

```text
historisierbare JCIEntity ── CHANGED_BY ──► ChangeEvent
ChangeEvent ── startet ──► SyncRun (technisch)
SyncRun ── verwendet ──► SYNC
SyncRun ── Abschluss oder kontrollierter Abbruch ──► SyncEvent

ChangeEvent ── TRIGGERS ──► SyncEvent
SyncEvent ── EXECUTES ──► SYNC
SyncEvent ── AFFECTS ──► JCIEntity
SyncEvent ── CREATES_HISTORY ──► PiH
historisierbare JCIEntity ── HAS_HISTORICAL_STATE ──► PiH
SyncEvent ── CREATES_CORRECTION ──► HistoricalCorrection
HistoricalCorrection ── CORRECTS ──► PiH
```

Die gespeicherten Kanten bilden das abschließende fachliche Ergebnis ab. Die technischen Pfeile zu `SyncRun` sind Prozessschritte und keine Graphbeziehungen.

## 4. Eingaben eines SyncRun

Ein technischer `SyncRun` benötigt mindestens:

| Eingabe             | Bedeutung                                   |
| ------------------- | ------------------------------------------- |
| `runId`             | eindeutige technische Laufkennung           |
| `idempotencyKey`    | Kennung des fachlichen Veränderungsauftrags |
| `changeEventId`     | auslösendes `ChangeEvent`                   |
| `syncDefinitionId`  | zu verwendende aktive `SYNC`-Definition     |
| `startedAt`         | Beginn des Versuchs                         |
| `requestedRevision` | erwartete Revision der Ausgangsentität      |

Das `ChangeEvent` besitzt genau eine `REQUESTED_BY`-Beziehung zu einem `RoleAssignment`. Optionale Nachweise werden über `USES_EVIDENCE` mit `Evidence` verbunden.

## 5. Ablauf

### 5.1 Annahme

1. Prüfen, dass `ChangeEvent`, Ausgangsentität und SYNC-Definition existieren.
2. Prüfen, dass `REQUESTED_BY` vorhanden und die Rollenaktivierung für den Zeitpunkt gültig ist.
3. Prüfen, ob `idempotencyKey` bereits erfolgreich verarbeitet wurde.
4. Prüfen, ob `requestedRevision` der aktuellen Revision entspricht.
5. Technischen `SyncRun` mit Zustand `RUNNING` beginnen.

### 5.2 Ermittlung der Betroffenheit

1. Bei der unmittelbar geänderten Entität beginnen.
2. Gespeicherte Beziehungen gemäß Ontologie und Graphregeln traversieren.
3. Direkte und indirekte Betroffenheit getrennt erfassen.
4. Bereits besuchte Kombinationen aus Entität und Beziehungspfad markieren, um Zyklen zu beenden.
5. Betroffenheit allein noch nicht als Änderung behandeln.

Bei einer Änderung an einem Task traversiert `SYNC` mindestens:

- den unmittelbar geänderten Task,
- seinen direkten und alle übergeordneten Tasks,
- seine direkten und alle untergeordneten Tasks,
- seine Voraussetzungen über `DEPENDS_ON`,
- alle von ihm abhängigen Tasks über die inverse Lesart von `DEPENDS_ON`,
- alle dadurch betroffenen `PiF1o`,
- deren Erfolgskriterien und aktuellen Verifications,
- verantwortliche Teams, ausführende RoleAssignments, verwendete ERoFObjects und relevante `RaN`.

Da `DEPENDS_ON` PiF1o-Grenzen überschreiten darf, kann eine Task-Änderung mehrere operative Zielzustände betreffen.

#### 5.2.1 Verbindliche Traversierungsmatrix

Die folgende Matrix definiert die fachliche Mindesttraversierung. „Aufwärts“ bezeichnet den WHY-Pfad zur übergeordneten Zukunft und zu `CiV`; „abwärts“ bezeichnet beitragende Zukunftselemente bis zur operativen Umsetzung. Inverse Lesarten verwenden dieselbe gespeicherte Kante in Gegenrichtung.

| Geänderter Typ | Direkt prüfen | Indirekt weiterverfolgen |
| -------------- | ------------- | ------------------------ |
| `CiV` | verbundene `PiF2`, Kontext gebende `PiH`, anwendbare `RaN` | abwärts über alle Zukunftsebenen bis Tasks, Result, Verification, RoF und ERoF |
| `PiF2` | begründende `CiV`, beitragende `PiF1s`, `RaN` | abwärts bis `PiF1o` und operative Graphobjekte |
| `PiF1s` | Ziel-`PiF2`, beitragende `PiF1t`, `RaN` | aufwärts bis `CiV`, abwärts bis operative Graphobjekte |
| `PiF1t` | Ziel-`PiF1s`, beitragende `PiF1o`, `RaN` | aufwärts bis `CiV`, abwärts bis Tasks und Prüfung |
| `PiF1o` | Ziel-`PiF1t`, Kriterien, Accountable, alle Tasks, `RaN` | vollständiger WHY-Pfad, Task-Graph, Results, Verifications, Teams, Rollen und ERoF |
| `Task` | Parent, Subtasks, Voraussetzungen, abhängige Tasks, PiF1o, Team, Ausführende, ERoFObjects, Results, `RaN` | alle dadurch erreichten Task- und PiF1o-Graphen sowie deren Zukunfts- und Prüfpfade |
| `SuccessCriterion` | zugehöriges `PiF1o`, prüfende aktuelle Verifications, `RaN` | Results und Tasks der Verifications; anschließend PiF1o-Aggregation und Zukunftskette |
| `Result` | erzeugender Task, aktuelle und abgelöste Verifications, `RaN` | PiF1o, Kriterien, Task-Graph und höhere Zukunftsebenen |
| `Verification` | Result, Kriterium, Vorgänger/Nachfolger, Evidence | erzeugender Task, PiF1o, alle Kriterien und höhere Zukunftsebenen |
| `Evidence` | alle eingehenden `USES_EVIDENCE`, `RaN` | jeweils deren fachliche Zielpfade; Evidence selbst entscheidet keinen Status |
| `RaN` | `GOVERNS`, `APPLIES_IN`, offene Konflikte | alle geregelten Ziele und deren abhängige Pfade gemäß dieser Matrix |
| `RaNConflict` | Konfliktregeln, betroffene Entitäten, erkennendes SyncEvent, Auflösungsbezüge | bei Auflösung alle betroffenen Entitäten und Regeln erneut vollständig prüfen |
| `RoFOrg` | Teams, Organisationsbeziehungen, eigene ERoFObjects, `RaN` | Mitglieder, Rollenaktivierungen, Tasks, PiF1o und fremde Organisationsseite |
| `RoFOrgRelationship` | beide Organisationen, vertretende RoleAssignments, `RaN` | Teams, Mitglieder, ERoF und bei `SUBSIDIARY` gesamte Vorfahren-/Nachfahrenstruktur |
| `RoFTeam` | Organisation, Mitglieder, RoleAssignments, verantwortete Tasks, `RaN` | PiF1o, Task-Graph, ERoFObjects und Organisationsbeziehungen der Beteiligten |
| `RoFTeamMember` | Teams, Rollen, Assignments, accountable PiF1o, `RaN` | ausgeführte Tasks, ERoFObjects, Organisationen und Zukunftspfade |
| `RoFRole` | besitzende Mitglieder, aktivierende Assignments, `RaN` | Teams, Tasks, ERoFObjects und betroffene Organisationen |
| `RoleAssignment` | Mitglied, Team, Rolle, Tasks, ERoFObjects, Organisationsvertretungen, `RaN` | Organisation, PiF1o, Task-Graph und Umwelt aller direkten Verwendungen |
| `ERoFObject` | verwendende Assignments und Tasks, Eigentümer, `RaN` | Teams, Mitglieder, Organisationen, PiF1o und Zukunftspfade der Tasks |
| `SYNC` | verwendende SyncEvents und gültige Vorgängerdefinition | die neue Definition wird durch die bisher aktive Definition geprüft; keine rückwirkende Änderung alter SyncEvents |
| `ChangeEvent` | Ausgangsentität, Requester, Evidence, ausgelöste SyncEvents | nur innerhalb des bestehenden Veränderungsvorgangs; kein rekursives ChangeEvent |
| `SyncEvent` | ChangeEvent, ausgeführte SYNC-Definition, betroffene Entitäten, erzeugte Historie/Korrekturen/Konflikte | unveränderlich; nur Konsistenz seiner gespeicherten Bezüge prüfen |
| `PiH` | ursprüngliche Entität, erzeugendes SyncEvent, Korrekturen, Kontextverwendung | unveränderlich; Abweichungen ausschließlich als HistoricalCorrection behandeln |
| `HistoricalCorrection` | PiH, ChangeEvent, SyncEvent, Korrektor, Evidence, Vorgänger/Nachfolger | unveränderlich; eine aktuelle Modellkorrektur als getrennten Vorgang behandeln |

Bei einer Beziehungsänderung beginnt `SYNC` an beiden Endpunkten und verwendet für beide deren Matrixzeile. Bei `REPLACED_BY`, `SUPERSEDES`, `DEPENDS_ON`, `DECOMPOSES_INTO`, `CONTRIBUTES_TO` und `SUBSIDIARY` wird die jeweilige Kette bis zu ihrem Ende traversiert und auf Zyklen geprüft.

Eine übernommene Beziehungsänderung erhöht die Revision beider bereits vorhandenen veränderlichen Endpunkte und erzeugt für beide ein `PiH`. Ein im selben Auftrag neu erzeugter Endpunkt beginnt mit Revision `1` und erhält noch kein `PiH`. Abgeleitete Folgeänderungen bleiben im selben SyncRun und erzeugen kein weiteres `ChangeEvent`.

Die Traversierung führt eine Besuchsmenge aus `entityId`, gelesener `revision`, Beziehungstyp und Richtung. Ein bereits besuchter Eintrag wird nicht erneut expandiert. Technische Seitengrößen dürfen das Lesen aufteilen, aber niemals die fachliche Ergebnismenge kürzen. Wird eine technische Grenze erreicht und kann die vollständige Menge nicht sicher ermittelt werden, endet der Versuch mit `FAILED`; es werden keine fachlichen Teiländerungen übernommen.

**Kurzes Beispiel:** Wird Annas `RoleAssignment` beendet, prüft SYNC Mitgliedschaft, Rolle und Team, alle von ihr ausgeführten Tasks sowie verwendete Umweltobjekte. Über die Tasks erreicht SYNC die betroffenen `PiF1o` und prüft, ob Ausführung, Erfolgskriterien und höhere Zukunftszustände weiterhin gültig sind.

### 5.3 Prüfung

Vor jeder fachlichen Auswertung prüft `SYNC` den Statusübergang gegen Abschnitt 2.2.4 von `JCI_CONTEXT.md`. Ein nicht aufgeführter Übergang endet mit `outcome = CONFLICT`; der aktuelle Zustand bleibt unverändert. Terminale Zustände werden nicht wieder geöffnet. Eine Fortsetzung wird als neue Entität angelegt.

Vor der Aktivierung oder dem Abschluss eines atomaren Tasks prüft `SYNC` außerdem die Rückverfolgbarkeit: Der WHY-Pfad muss über `PiF1o`, `PiF1t`, `PiF1s` und `PiF2` zu mindestens einem `CiV` führen. Der WHO-Pfad muss ausführendes `RoleAssignment`, Mitglied, Rolle, verantwortliches Team und Organisation eindeutig ergeben. Ein fehlender Pflichtpfad verhindert den Statuswechsel.

Bei `changeType = REPLACED` prüft `SYNC`, dass genau ein typgleicher Nachfolger über `REPLACED_BY` angegeben ist. Bei allen anderen Status darf die zu ändernde Entität keine ausgehende `REPLACED_BY`-Beziehung besitzen. Selbstbezüge und Zyklen werden abgewiesen.

Prozessartefakte erzeugen keine rekursive Ereigniskette. `ChangeEvent`, `SyncEvent`, `PiH`, `HistoricalCorrection` und ein während des Laufs erkannter offener `RaNConflict` werden im bestehenden Veränderungsvorgang erzeugt. Für ihre eigene Erzeugung startet `SYNC` keinen weiteren `SyncRun`.

**Beispiel:** Ein `COMPLETED` Task darf nicht zurück auf `ACTIVE` gesetzt werden. Ist weitere Arbeit erforderlich, wird ein neuer Task erzeugt und durch den regulären JCI-Pfad einem `PiF1o` zugeordnet.

Für jede mögliche Änderung werden mindestens geprüft:

- zulässige Quell- und Zieltypen,
- Kardinalitäten,
- Statusübergang,
- aktuelle Revision,
- relevante `RaN`,
- Rollen- und Teamkontext,
- zeitliche Überdeckung von Teammitgliedschaft, Rollenbesitz und Rollenaktivierung,
- organisationsbezogene Eigentums- und Umweltperspektive,
- personengebundene ERoF-Nutzung,
- Organisationsregeln einschließlich `SUBSIDIARY`-Zyklusfreiheit,
- unveränderliche Entitätstypen,
- erforderliche Evidence und Verantwortlichkeit,
- Task-Typ, Task-Hierarchie und Zyklusfreiheit,
- Task-Abhängigkeiten und deren Zyklusfreiheit,
- typabhängige Ausführungs-, Umwelt- und Ergebnisregeln,
- Anwendbarkeit, Vereinbarkeit und Priorität aller einschlägigen `RaN`.

Nicht eindeutig entscheidbare Semantik und widersprüchliche `RaN` führen zu einem Konflikt. `SYNC` entscheidet sie nicht stillschweigend.

### 5.3.1 Auswertung von Erfolgskriterien

Wird eine `Verification` abgeschlossen oder abgelöst, führt `SYNC` zusätzlich aus:

1. Prüfen, dass `EVALUATES` auf genau ein `Result` und `CHECKS` auf genau ein `SuccessCriterion` verweist.
2. Bei `SUPERSEDES` prüfen, dass Vorgängerin und Nachfolgerin dasselbe Result bewerten und dasselbe Kriterium prüfen.
3. Alle abgeschlossenen, nicht abgelösten Verifications des betroffenen Kriteriums bestimmen.
4. Für jede Verification prüfen, dass Messwert, `measurementType`, `operator`, `targetValue` und optionale Einheit reproduzierbar zusammenpassen; andernfalls ist die Verification `INCONCLUSIVE`.
5. Bei `evaluationMode = ALL` das Kriterium nur dann als erfüllt bewerten, wenn mindestens eine aktuelle Verification existiert und alle `VALID` sind.
6. Bei `evaluationMode = ANY` das Kriterium als erfüllt bewerten, sobald mindestens eine aktuelle Verification `VALID` ist.
7. `INVALID`, `INCONCLUSIVE` und fehlende aktuelle Verifications entsprechend den Graphregeln als nicht erfüllend behandeln.
8. Für den zugehörigen `PiF1o` alle `REQUIRED`-Kriterien aggregieren.
9. Nur Verifications berücksichtigen, deren Results aus Tasks dieses `PiF1o` stammen.
10. Den Statuswechsel zu `ACHIEVED` nur vorbereiten, wenn mindestens ein verpflichtendes Kriterium vorhanden, jedes verpflichtende Kriterium erfüllt, alle zugeordneten Tasks `COMPLETED`, alle Task-Abhängigkeiten erfüllt und keine Modell- oder `RaN`-Verletzung vorhanden ist.

`OPTIONAL`-Kriterien werden im Ergebnis dokumentiert, blockieren `ACHIEVED` aber nicht. Ist die Entscheidung nicht eindeutig, bleibt der Status unverändert und der Versuch dokumentiert `CONFLICT`.

### 5.3.2 Auswertung von Task-Status

Bei einer Task-Änderung wertet `SYNC` zuerst die atomaren Tasks, anschließend die Task-Hierarchie von unten nach oben und zuletzt die betroffenen `PiF1o` aus:

1. Für jeden `ATOMIC`-Task alle Ziele von `DEPENDS_ON` bestimmen.
2. Ist mindestens eine Voraussetzung nicht `COMPLETED`, `BLOCKED` vorbereiten.
3. Sind alle Voraussetzungen erfüllt, Ausführungs-, Team- und `RaN`-Regeln prüfen und den beantragten beziehungsweise bestehenden zulässigen Status bestimmen.
4. Für jeden `COMPOSITE`-Task die effektiven direkten Untertasks bestimmen: Ein ersetzter Untertask wird nur dann durch seinen `REPLACED_BY`-Nachfolger ersetzt, wenn dieser ebenfalls direkter Untertask desselben Parents ist. Danach gilt: nur `DRAFT` → `DRAFT`; nur `COMPLETED` → `COMPLETED`; mindestens ein `ACTIVE` oder eine Mischung aus `DRAFT` und `COMPLETED` → `ACTIVE`; ohne `ACTIVE`, aber mit mindestens einem `BLOCKED` → `BLOCKED`.
5. Die Ableitung bis zu allen Wurzel-Tasks wiederholen.
6. Anschließend für jedes betroffene `PiF1o` Task-Abschluss, Erfolgskriterien und übrige Modellbedingungen gemeinsam auswerten.

Ein nicht korrekt eingebundener `REPLACED`- oder ein weiterhin verbundener `REVOKED`-Untertask sowie eine zyklische oder widersprüchliche Struktur führen zu `CONFLICT`. Jeder tatsächlich übernommene abgeleitete Statuswechsel erzeugt wie jede andere fachliche Änderung Revision und `PiH` des abgelösten Zustands.

### 5.3.3 Aggregation übergeordneter Zukunftszustände

Nach jeder Änderung eines Zukunftselements wertet `SYNC` die Zukunftskette von unten nach oben aus:

1. Für `PiF1t` die aktuellen direkt beitragenden `PiF1o`, für `PiF1s` die aktuellen `PiF1t` und für `PiF2` die aktuellen `PiF1s` bestimmen.
2. `REPLACED` und `REVOKED` nicht als aktuelle Beiträge zählen. Einen Ersatz erst berücksichtigen, wenn er selbst zum selben Ziel beiträgt.
3. Ohne mindestens einen aktuellen direkten Beitrag kein `ACHIEVED` ableiten.
4. Bei `contributionMode = ALL` nur dann `ACHIEVED` vorbereiten, wenn alle aktuellen direkten Beiträge `ACHIEVED` sind.
5. Bei `contributionMode = ANY` `ACHIEVED` vorbereiten, sobald mindestens ein aktueller direkter Beitrag `ACHIEVED` ist.
6. Nach jeder abgeleiteten Änderung die nächsthöhere Ebene erneut prüfen.

**Beispiel:** Zwei operative Zustände tragen zu einem taktischen Zustand mit `contributionMode = ALL` bei. Erst wenn beide `PiF1o` erreicht sind, darf `SYNC` das `PiF1t` als erreicht vorbereiten.

### 5.3.4 Auswertung von RaN

Für jede von Regeln betroffene Entscheidung führt `SYNC` aus:

1. Anhand von `governedTypes`, `scopeType` und gegebenenfalls `APPLIES_IN` alle potenziell einschlägigen aktiven und zeitlich gültigen `RaN` bestimmen; `GOVERNS` für die aktuellen konkreten Ziele abgleichen und erforderliche Zielkanten vorbereiten.
2. Jede normalisierte Condition reproduzierbar auswerten. Nicht katalogisierte oder mehrdeutige Pfade ergeben `UNEVALUABLE`.
3. Aus `effect` und Bedingung pro Regel `ALLOW`, `DENY` oder `NO_DECISION` ableiten.
4. Eine einzelne Regelverletzung als `DENY` behandeln und die Entscheidung blockieren, ohne allein einen `RaNConflict` zu erzeugen.
5. Nur Regeln mit demselben `decisionKey`, überlappendem Scope und gemeinsamem Ziel auf widersprüchliche Ergebnisse vergleichen.
6. Für jeden tatsächlichen Widerspruch aus `ALLOW` und `DENY` die Prioritäten vergleichen.
7. Bei unterschiedlichen Prioritäten ausschließlich im Widerspruch der größeren Zahl Vorrang geben.
8. Bei gleicher höchster einschlägiger Priorität einen offenen `RaNConflict` mit `conflictType = PRIORITY_TIE` und einem aus ChangeEvent, sortierter Konfliktmenge und Entscheidung abgeleiteten `conflictKey` vorbereiten.
9. Bei nicht eindeutig bewertbarer Anwendbarkeit oder Vereinbarkeit einen offenen `RaNConflict` mit `conflictType = UNEVALUABLE` und entsprechendem `conflictKey` vorbereiten.
10. Automatische Änderungen blockieren, deren Zulässigkeit vom offenen Konflikt abhängt.

Ein niedriger priorisiertes `RaN` wird durch den Vorrang nicht aufgehoben und bleibt für vereinbare sowie andere Entscheidungen anwendbar. `ruleType` wird nicht als Rangfolge verwendet.

Vor dem Anlegen prüft `SYNC`, ob für denselben Veränderungsauftrag bereits ein `RaNConflict` mit demselben `conflictKey` besteht. Ein Wiederholungsversuch darf keinen Duplikatknoten erzeugen. Optionale Nachweise werden ausschließlich als `Evidence`-Knoten über `USES_EVIDENCE` verbunden.

Zur Auflösung eines vorhandenen Konflikts prüft ein nachfolgender `SyncRun` die über `CONFLICTING_RULE` verbundenen Regeln und die betroffenen Entitäten erneut. Nur wenn der dokumentierte Widerspruch nicht mehr besteht und der Versuch erfolgreich ist, bereitet `SYNC` `status = RESOLVED`, `resolvedAt`, `resolution`, `RESOLVED_BY` und `RESOLVED_THROUGH` vor. Der offene Ausgangszustand wird als `PiH` vorbereitet.

### 5.4 Vorbereitung der Änderung

Für jede tatsächlich zu ändernde vorhandene Entität:

1. Eigenschaften und gültige Beziehungen des Ausgangszustands vollständig lesen.
2. Daraus einen kanonischen `StateSnapshot` und sortierte `RelationshipSnapshot`-Einträge bilden; anschließend den SHA-256-`contentHash` berechnen.
3. Ein unveränderliches `PiH` mit `originalEntityId`, `originalEntityType`, `originalRevision`, Schema-Versionen und den Snapshots vorbereiten.
4. `HAS_HISTORICAL_STATE` und `CREATES_HISTORY` vorbereiten.
5. Neuen aktuellen Zustand mit `revision + 1` und neuem `updatedAt` vorbereiten.

Bei `changeType = CREATED` wird für die neu angelegte Entität kein `PiH` vorbereitet.

### 5.5 Historische Korrektur

Bei `changeType = HISTORICAL_CORRECTION`:

1. Prüfen, dass das Ziel ein bestehendes `PiH` ist.
2. Prüfen, dass `CORRECTED_BY` auf ein gültiges `RoleAssignment` verweist.
3. Begründung, Korrekturart, betroffene Felder sowie alten und korrigierten Wert prüfen.
4. Optionale `Evidence` über `USES_EVIDENCE` prüfen.
5. Bei `SUPERSEDES` prüfen, dass beide Korrekturen dasselbe `PiH` betreffen und kein Zyklus entsteht.
6. Ein neues unveränderliches `HistoricalCorrection` vorbereiten.
7. Niemals das bestehende `PiH` verändern oder historisieren.

Entsteht zusätzlich Änderungsbedarf am aktuellen Modell, wird dafür ein eigener Veränderungsvorgang angelegt.

### 5.6 Fachliche Atomarität und Abschlussdokumentation

Bei `SUCCESS` werden die folgenden Inhalte gemeinsam atomar übernommen:

- neue aktuelle Zustände,
- vorbereitete `PiH`,
- vorbereitete `HistoricalCorrection`-Objekte,
- aufgelöste `RaNConflict`-Objekte,
- alle zugehörigen Beziehungen,
- das abschließende `SyncEvent`.

Bei `CONFLICT` oder `FAILED` werden die angeforderte fachliche Änderung und alle noch nicht übernommenen Folgeänderungen vollständig zurückgerollt. Für einen nicht übernommenen Zustand entstehen weder eine neue Revision noch ein `PiH`. Nach dem Rollback speichert die Implementierung die Abschlussdokumentation mit dem unveränderlichen `SyncEvent` und gegebenenfalls neu erkannten `RaNConflict`-Objekten. Diese Dokumentation gehört zum Versuch, nicht zum abgewiesenen fachlichen Zustand.

```text
Fachliche Transaktion
├── SUCCESS  → vollständig übernehmen
├── CONFLICT → vollständig zurückrollen
└── FAILED   → vollständig zurückrollen

Abschlussdokumentation
└── SyncEvent immer nach dem beendeten Versuch speichern
    └── bei Bedarf RaNConflict mit dokumentieren
```

Ist die Ereignisspeicherung vorübergehend technisch unmöglich, bleibt eine dauerhafte Nachholpflicht bestehen. Nach Wiederherstellung der Schreibfähigkeit wird genau das fehlende `SyncEvent` mit derselben `runId`, demselben `ChangeEvent` und derselben Idempotenzkennung gespeichert. Dieser Vorgang darf die fehlgeschlagene oder konfliktbehaftete Fachänderung nicht erneut ausführen.

## 6. Erzeugung des SyncEvent

Ein `SyncEvent` wird nicht zu Beginn und nicht während des Versuchs erzeugt. Es entsteht erst, wenn alle Pflichtangaben feststehen.

Pflichtfelder:

```text
id
entityType = SyncEvent
name
createdAt
updatedAt = createdAt
revision = 1
status = RECORDED
startedAt
completedAt
outcome
affectedCount
changedCount
historyCount
correctionCount
conflictCount
```

Zulässige Ergebnisse:

| Ergebnis   | Bedeutung                                                     |
| ---------- | ------------------------------------------------------------- |
| `SUCCESS`  | Prüfung und Übernahme wurden erfolgreich abgeschlossen        |
| `CONFLICT` | fachlicher Konflikt verhindert eine automatische Entscheidung |
| `FAILED`   | technischer oder formaler Fehler beendete den Versuch         |

Ein fachlich oder kontrolliert technisch beendeter `SyncRun` erzeugt genau ein `SyncEvent`. War dessen Speicherung vorübergehend unmöglich, wird sie nachgeholt. Jedes `SyncEvent` verweist über `EXECUTES` auf die verwendete SYNC-Definition und über `TRIGGERS` invers gelesen auf genau ein `ChangeEvent`.

## 7. Zählwerte

Die Zählwerte müssen den gespeicherten Beziehungen und Änderungen entsprechen:

```text
affectedCount   = Anzahl verschiedener Ziele von AFFECTS
changedCount    = Anzahl tatsächlich übernommener aktueller Zustandsänderungen
historyCount    = Anzahl Ziele von CREATES_HISTORY
correctionCount = Anzahl Ziele von CREATES_CORRECTION
conflictCount   = Anzahl der über DETECTED_BY invers zugeordneten RaNConflict-Objekte
```

Alle Werte sind nicht negativ. Bei `SUCCESS` müssen die Zählwerte exakt mit dem übernommenen Graphzustand übereinstimmen. Bei `CONFLICT` oder `FAILED` beschreiben sie ausschließlich abschließend festgestellte beziehungsweise atomar übernommene Ergebnisse.

Ein neu erkannter offener `RaNConflict` wird in derselben atomaren Übernahme über `DETECTED_BY` mit dem abschließenden `SyncEvent` verbunden. Das `SyncEvent` erhält `outcome = CONFLICT`, wenn mindestens eine angeforderte Entscheidung wegen eines offenen Konflikts nicht übernommen werden konnte. Der durch ein `ChangeEvent` bezeichnete fachliche Veränderungsauftrag bildet genau eine atomare Transaktionsgrenze: Entweder werden alle zu diesem Auftrag gehörenden fachlichen Änderungen übernommen oder keine. Unabhängige Änderungen benötigen ein eigenes `ChangeEvent` und einen eigenen Synchronisationsvorgang.

## 8. Idempotenz und Wiederholung

1. Derselbe `idempotencyKey` darf dieselbe fachliche Änderung höchstens einmal erfolgreich übernehmen.
2. Ein erneuter technischer Versuch erhält eine neue `runId`.
3. Jeder tatsächlich beendete Versuch erzeugt ein eigenes `SyncEvent`.
4. Ein Wiederholungsversuch prüft die erwartete Revision erneut.
5. Wurde die Änderung bereits erfolgreich übernommen, darf die Wiederholung keine weiteren `PiH`, Revisionen oder Korrekturen erzeugen.

## 9. Parallelität

Vor der atomaren Übernahme wird die aktuelle Revision jeder zu ändernden Entität erneut geprüft. Weicht sie von der beim Start gelesenen Revision ab, wird keine Änderung übernommen. Der Versuch endet mit `CONFLICT` oder wird mit neuer Ausgangsrevision als neuer Versuch gestartet.

## 10. Ausfall und Wiederaufnahme

Der technische `SyncRun` darf Laufzeitinformationen wie `heartbeatAt`, technischen Status und Diagnosedaten führen. Nach einem Absturz erkennt die Implementierung verwaiste Läufe und beendet sie kontrolliert als fehlgeschlagen oder startet einen neuen Versuch mit derselben Idempotenzkennung.

Technische Diagnosedaten sind kein Ersatz für das abschließende `SyncEvent`. Ein nicht mehr fortsetzbarer Versuch soll nach Wiederherstellung der technischen Schreibfähigkeit ein `SyncEvent` mit `outcome = FAILED` erhalten.

## 11. Austauschformat

`JCIChangeRequest` und `JCISyncResult` verwenden die in Abschnitt 12.6 von `JCI_CONTEXT.md` festgelegten JSON-Formate. Die verbindlichen JSON-Schemas liegen unter `docs/schemas/`. Ein SyncRun lehnt Dokumente mit unbekannter `schemaVersion`, zusätzlichen nicht erlaubten Feldern oder ungültigen Operationen vor jeder Graphänderung ab.

**Kurzes Beispiel:** Ein `CONNECT` darf nur einen katalogisierten Beziehungstyp, Richtung und Gegenentitäts-ID enthalten. Ein unbekanntes `LINKS_TO` wird abgewiesen und nicht als neue Kante interpretiert.
