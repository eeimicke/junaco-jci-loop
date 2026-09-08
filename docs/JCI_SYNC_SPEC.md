# JCI-SYNC-Spezifikation

## 1. Status und Zweck

Dieses Dokument beschreibt den technologieunabhängigen Ablauf von `SYNC`. Die fachliche Bedeutung richtet sich nach [`JCI_CONTEXT.md`](JCI_CONTEXT.md), die Typen nach [`JCI_ONTOLOGY.md`](JCI_ONTOLOGY.md) und die gültigen Graphzustände nach [`JCI_GRAPH_RULES.md`](JCI_GRAPH_RULES.md).

Regelpaket, `ontologyVersion`, `graphRulesVersion`, `syncSpecVersion`, `snapshotSchemaVersion`, `valueSchemaVersion` und Austausch-`schemaVersion` verwenden für neue Vorgänge `2.0`. JSON-LD bleibt `1.1`; Namespace-IRIs mit `/1.0#` sind stabile Identitäten und keine Regelversion. Alte Profile bleiben durch explizit versionierte Resolver lesbar; bestehende PiH, Korrekturen und Hashes werden nicht umgeschrieben oder neu berechnet.

## 2. Begriffe

```text
SYNC      = gespeicherte und historisierbare Definition der Synchronisationslogik
SyncRun   = veränderbarer technischer Zustand während eines Ausführungsversuchs
SyncEvent = unveränderliche fachliche Dokumentation nach Abschluss oder Abbruch
ChangeEvent = unveränderliche Dokumentation eines angenommenen Veränderungsauftrags
```

`SyncRun` ist keine `JCIEntity`, kein `GraphObject` und kein JCI-Kernelement. Die Implementierung darf ihn in einer Laufzeit-, Queue- oder Protokollstruktur speichern. Im fachlichen JCI-Graphen wird er nicht als Zwischenknoten angelegt.

## 3. Verbindlicher Zusammenhang

```text
vorhandene historisierbare JCIEntity ── CHANGED_BY ──► ChangeEvent
ChangeEvent ── plant ──► SyncRun (technisch)
SyncRun ── verwendet ──► SYNC
SyncRun ── Abschluss oder kontrollierter Abbruch ──► SyncEvent

ChangeEvent ── TRIGGERS ──► SyncEvent
SyncEvent ── EXECUTES ──► SYNC
SyncEvent ── AFFECTS ──► JCIEntity
SyncEvent ── CREATES_HISTORY ──► PiH
historisierbare JCIEntity ── HAS_HISTORICAL_STATE ──► PiH

ChangeEvent:HISTORICAL_CORRECTION ── TARGETS_HISTORY ──► PiH
SyncEvent ── CREATES_CORRECTION ──► HistoricalCorrection
HistoricalCorrection ── CORRECTS ──► dasselbe PiH
```

Die gespeicherten Kanten bilden die fachliche Provenienz ab. Die technischen Pfeile zu `SyncRun` sind Prozessschritte und keine Graphbeziehungen; ein `SyncRun` wird niemals als JCI-Knoten angelegt. Ein angenommenes `ChangeEvent` darf zunächst kein `TRIGGERS`-Ziel besitzen. Erst jeder beendete oder kontrolliert abgebrochene Versuch ergänzt genau eine solche Kante append-only.

## 4. Eingaben eines SyncRun

Ein technischer `SyncRun` benötigt mindestens:

| Eingabe             | Bedeutung                                    |
| ------------------- | -------------------------------------------- |
| `runId`             | eindeutige technische Laufkennung            |
| `idempotencyKey`    | Kennung des fachlichen Veränderungsauftrags  |
| `changeEventId`     | auslösendes `ChangeEvent`                    |
| `syncDefinitionId`  | zu verwendende aktive `SYNC`-Definition      |
| `startedAt`         | Beginn des Versuchs                          |
| `requestedRevision` | erwartete Revision oder `null` bei `CREATED` |

Der technische Request-/Runbeleg enthält außerdem den vollständigen unveränderlichen Payload oder eine dauerhaft auflösbare Referenz darauf, Run-Eigentümerschaft mit Fencing-Token und die tatsächlich verwendete SYNC-Revision samt Paketprüfsumme. decisionAt und graphEpoch werden am geschützten Entscheidungspunkt beziehungsweise Commit ergänzt. Diese technischen Felder gehören nicht zum ChangeEvent-Entitätskatalog.

Das bereits vor dem Lauf gespeicherte `ChangeEvent` besitzt mindestens:

```text
id = requestId
idempotencyKey
targetEntityId
targetEntityType
requestedRevision
changeType
occurredAt
reason
status = RECORDED
revision = 1
```

Es besitzt genau eine `REQUESTED_BY`-Beziehung zu einem `RoleAssignment`. Optionale Nachweise werden über `USES_EVIDENCE` mit `Evidence` verbunden. Seine Eigenschaften werden nach der Annahme nicht verändert.

## 5. Ablauf

### 5.1 Annahme

1. Den vollständigen normalisierten JCIChangeRequest einschließlich operations oder historicalCorrection dauerhaft technisch speichern und unveränderlich an requestId und idempotencyKey binden. Gleicher Schlüssel mit anderem Inhalt wird vor erneuter Annahme abgewiesen. Ein identischer bereits erfolgreicher Auftrag liefert sein gespeichertes Ergebnis ohne neuen Run.
2. ChangeEvent und dauerhafte Einplanung seines Versuchs gemeinsam unter der Schreibsperre aus Abschnitt 9 speichern. Request-, Run- und Outbox-Belege sind keine JCIEntity und ersetzen keine fachliche Provenienz.
3. Vor der entscheidenden Lesesicht dieselbe Sperre erwerben. Auftrag, gültiges REQUESTED_BY, Run-Besitz samt Fencing-Token, Idempotenzstatus und aktive SYNC-Definition erneut prüfen. Ihre tatsächlich verwendete Revision und Paketprüfsumme technisch binden.
4. Bei CREATED müssen Ziel-ID frei und requestedRevision = null sein. Historische Korrektur erfordert Zieltyp PiH, Revision 1, genau ein TARGETS_HISTORY und keine CHANGED_BY-Quelle. Sonst muss die historisierbare Zielentität genau eine passende CHANGED_BY-Quelle bilden und weiterhin exakt die unveränderlich angeforderte Revision besitzen.
5. Den geplanten SyncRun mit eindeutiger runId starten. Ein alter Worker darf nach Verlust seines Fencing-Tokens nicht übernehmen. Bis zum Abschluss bleibt TRIGGERS = 0 zulässig.

Ein Scheitern vor erfolgreicher Zielauflösung endet mit FAILED; ausschließlich dann darf AFFECTS leer sein. SUCCESS und CONFLICT dokumentieren mindestens eine tatsächlich bestehende oder erfolgreich neu übernommene betroffene Entität. Ein CREATED-Kandidat wird nicht allein für Fehlerdokumentation gespeichert.

**Kurzes Beispiel:** Derselbe Request trifft zweimal ein. Die zweite Annahme nutzt den bestehenden Auftrag und liefert nach dessen Erfolg das gespeicherte Ergebnis. Eine neue Zielrevision unter derselben Idempotenzkennung ist kein Retry.

### 5.2 Ermittlung der Betroffenheit

1. Bei der durch `targetEntityId` und `targetEntityType` bezeichneten Entität oder dem validierten `CREATED`-Kandidaten beginnen.
2. Gespeicherte Beziehungen gemäß Ontologie und Graphregeln traversieren.
3. Direkte und indirekte Betroffenheit getrennt erfassen.
4. Bereits besuchte Kombinationen aus Entität und Beziehungspfad markieren, um Zyklen zu beenden.
5. Betroffenheit allein noch nicht als Änderung behandeln.
6. Für `SUCCESS` und `CONFLICT` mindestens eine betroffene `JCIEntity` bestimmen. `AFFECTS = 0` ist ausschließlich bei frühem `FAILED` vor Zielauflösung zulässig.

Bei einer Änderung an einem Task traversiert `SYNC` mindestens:

- den unmittelbar geänderten Task,
- seinen direkten und alle übergeordneten Tasks,
- seine direkten und alle untergeordneten Tasks,
- seine Voraussetzungen über `DEPENDS_ON`,
- alle von ihm abhängigen Tasks über die inverse Lesart von `DEPENDS_ON`,
- alle dadurch betroffenen `PiF1o`,
- deren Erfolgskriterien und anwendbaren aktuellen Verifications,
- verantwortliche Teams, ausführende RoleAssignments, verwendete ERoFObjects und relevante `RaN`.

Da `DEPENDS_ON` PiF1o-Grenzen überschreiten darf, kann eine Task-Änderung mehrere operative Zielzustände betreffen.

#### 5.2.1 Verbindliche Traversierungsmatrix

Die folgende Matrix definiert die fachliche Mindesttraversierung. „Aufwärts“ bezeichnet den WHY-Pfad zur übergeordneten Zukunft und zu `CiV`; „abwärts“ bezeichnet beitragende Zukunftselemente bis zur operativen Umsetzung. Inverse Lesarten verwenden dieselbe gespeicherte Kante in Gegenrichtung.

| Geänderter Typ         | Direkt prüfen                                                                                                 | Indirekt weiterverfolgen                                                                                            |
| ---------------------- | ------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------- |
| `CiV`                  | drei Dimensionen, `HELD_BY`, `INFORMED_BY`, schützende `RaN`, verbundene `PiF2`, Kontext gebende `PiH`        | zu Herkunfts-CiV, Werteträger und geschützten PiF2; abwärts bis zu allen geregelten Umsetzungselementen             |
| `PiF2`                 | begründende `CiV`, gemeinsamer Werteträger, schützende `RaN`, beitragende `PiF1s`                             | zu geschützten CiV; abwärts bis `PiF1o` und allen geregelten Umsetzungselementen                                    |
| `PiF1s`                | Ziel-`PiF2`, beitragende `PiF1t`, `RaN`                                                                       | aufwärts bis `CiV`, abwärts bis operative Graphobjekte                                                              |
| `PiF1t`                | Ziel-`PiF1s`, beitragende `PiF1o`, `RaN`                                                                      | aufwärts bis `CiV`, abwärts bis Tasks und Prüfung                                                                   |
| `PiF1o`                | Ziel-`PiF1t`, Kriterien, Accountable, alle Tasks, `RaN`                                                       | vollständiger WHY-Pfad, Task-Graph, Results, Verifications, Teams, Rollen und ERoF                                  |
| `Task`                 | Parent, Subtasks, Voraussetzungen, abhängige Tasks, PiF1o, Team, Ausführende, ERoFObjects, Results, `RaN`     | alle dadurch erreichten Task- und PiF1o-Graphen sowie deren Zukunfts- und Prüfpfade                                 |
| `SuccessCriterion`     | zugehöriges `PiF1o`, prüfende anwendbare aktuelle Verifications, `RaN`                                        | Results und Tasks der Verifications; anschließend PiF1o-Aggregation und Zukunftskette                               |
| `Result`               | erzeugender Task, aktuelle und abgelöste Verifications, `RaN`                                                 | PiF1o, Kriterien, Task-Graph und höhere Zukunftsebenen                                                              |
| `Verification`         | Result, Kriterium, deren gebundene Revisionen, Vorgänger/Nachfolger, Evidence                                 | erzeugender Task, PiF1o, alle anwendbaren aktuellen Verifications, Kriterien und höhere Zukunftsebenen              |
| `Evidence`             | alle eingehenden `USES_EVIDENCE`, `RaN`                                                                       | jeweils deren fachliche Zielpfade; Evidence selbst entscheidet keinen Status                                        |
| `RaN`                  | `PROTECTS`, `GOVERNS`, `APPLIES_IN`, offene Konflikte                                                         | alle geschützten CiV und PiF2, alle geregelten Umsetzungselemente und deren abhängige Pfade gemäß dieser Matrix     |
| `RaNConflict`          | Konfliktregeln, betroffene Entitäten, erkennendes SyncEvent, Auflösungsbezüge                                 | bei Auflösung alle betroffenen Entitäten und Regeln erneut vollständig prüfen                                       |
| `RoFOrg`               | Teams, Organisationsbeziehungen, eigene ERoFObjects, `RaN`                                                    | Mitglieder, Rollenaktivierungen, Tasks, PiF1o und fremde Organisationsseite                                         |
| `RoFOrgRelationship`   | beide Organisationen, vertretende RoleAssignments, `RaN`                                                      | Teams, Mitglieder, ERoF und bei `SUBSIDIARY` gesamte Vorfahren-/Nachfahrenstruktur                                  |
| `RoFTeam`              | Organisation, Mitglieder, RoleAssignments, verantwortete Tasks, `RaN`                                         | PiF1o, Task-Graph, ERoFObjects und Organisationsbeziehungen der Beteiligten                                         |
| `RoFTeamMember`        | Teams, Rollen, Assignments, accountable PiF1o, `RaN`                                                          | ausgeführte Tasks, ERoFObjects, Organisationen und Zukunftspfade                                                    |
| `RoFRole`              | besitzende Mitglieder, aktivierende Assignments, `RaN`                                                        | Teams, Tasks, ERoFObjects und betroffene Organisationen                                                             |
| `RoleAssignment`       | Mitglied, Team, Rolle, Tasks, ERoFObjects, Organisationsvertretungen, `RaN`                                   | Organisation, PiF1o, Task-Graph und Umwelt aller direkten Verwendungen                                              |
| `ERoFObject`           | verwendende Assignments und Tasks, Eigentümer, `RaN`                                                          | Teams, Mitglieder, Organisationen, PiF1o und Zukunftspfade der Tasks                                                |
| `SYNC`                 | verwendende SyncEvents und gültige Vorgängerdefinition                                                        | die neue Definition wird durch die bisher aktive Definition geprüft; keine rückwirkende Änderung alter SyncEvents   |
| `ChangeEvent`          | Zielkoordinaten, optionale `CHANGED_BY`-Quelle, `TARGETS_HISTORY`, Requester, Evidence, ausgelöste SyncEvents | nur innerhalb des bestehenden Veränderungsvorgangs; kein rekursives ChangeEvent                                     |
| `SyncEvent`            | ChangeEvent, ausgeführte SYNC-Definition, betroffene Entitäten, erzeugte Historie/Korrekturen/Konflikte       | unveränderlich; nur Konsistenz seiner gespeicherten Bezüge prüfen                                                   |
| `PiH`                  | ursprüngliche Entität, erzeugendes SyncEvent, Korrekturen, Kontextverwendung                                  | unveränderlich; Abweichungen ausschließlich als HistoricalCorrection behandeln                                      |
| `HistoricalCorrection` | PiH, ChangeEvent, SyncEvent, Korrektor, Evidence, `baseHistoryViewHash`, Vorgänger/Nachfolger                 | unveränderlich; wirksame `HistoryView` bestimmen und eine aktuelle Modellkorrektur als getrennten Vorgang behandeln |

Bei einer Beziehungsänderung beginnt `SYNC` an beiden Endpunkten und verwendet für beide deren Matrixzeile. Bei `REPLACED_BY`, `SUPERSEDES`, `DEPENDS_ON`, `DECOMPOSES_INTO`, `CONTRIBUTES_TO` und `SUBSIDIARY` wird die jeweilige Kette bis zu ihrem Ende traversiert und auf Zyklen geprüft.

Revision und Historisierung folgen dem versionierten Revisionseigentum aus [`JCI_CONTEXT.md`](JCI_CONTEXT.md). Neue Verification-, HistoricalCorrection-, ChangeEvent- und SyncEvent-Bezüge ändern den referenzierten Bestand nicht allein durch die Bezugnahme. TRIGGERS, CHANGED_BY und HAS_HISTORICAL_STATE erzeugen keine Historisierungsschleife. CREATED_BY gehört zum Erstellungszustand der Quelle; zulässiges Nachtragen an einem bestehenden Importentwurf ändert nur dessen eigenen Zustand. Eine RaNConflict-Auflösung revisioniert den Konflikt genau einmal, nicht seine referenzierten Regeln und Akteure. PiH PROVIDES_CONTEXT_TO CiV gehört zum Kontextzustand des CiV. Für die übrigen ausdrücklich katalogisierten fachlichen Strukturbeziehungen gelten beide veränderlichen Endpunkte als Eigentümer.

Jeder vorhandene Eigentümer mit tatsächlicher Änderung erhält pro Auftrag genau eine neue Revision und ein PiH; neue Entitäten beginnen bei Revision 1. Neue Prüf- oder Ereignisbezüge erlauben keine Änderung abgeschlossener Dokumentinhalte. Alle Beziehungen bleiben Teil der Betroffenheits- und Parallelitätsprüfung, auch ohne Fachrevision. Folgeänderungen bleiben im selben SyncRun ohne weiteres ChangeEvent.

Die Traversierung führt eine Besuchsmenge aus `entityId`, gelesener `revision`, Beziehungstyp und Richtung. Ein bereits besuchter Eintrag wird nicht erneut expandiert. Technische Seitengrößen dürfen das Lesen aufteilen, aber niemals die fachliche Ergebnismenge kürzen. Wird eine technische Grenze erreicht und kann die vollständige Menge nicht sicher ermittelt werden, endet der Versuch mit `FAILED`; es werden keine fachlichen Teiländerungen übernommen.

**Kurzes Beispiel:** Wird Annas `RoleAssignment` beendet, prüft SYNC Mitgliedschaft, Rolle und Team, alle von ihr ausgeführten Tasks sowie verwendete Umweltobjekte. Über die Tasks erreicht SYNC die betroffenen `PiF1o` und prüft, ob Ausführung, Erfolgskriterien und höhere Zukunftszustände weiterhin gültig sind.

### 5.3 Prüfung

Vor jeder fachlichen Auswertung prüft `SYNC` den Statusübergang gegen Abschnitt 2.2.4 von [`JCI_CONTEXT.md`](JCI_CONTEXT.md). Ein nicht aufgeführter Übergang endet mit `outcome = CONFLICT`; der aktuelle Zustand bleibt unverändert. Terminale Zustände werden nicht wieder geöffnet. Eine Fortsetzung wird als neue Entität angelegt.

Vor der Aktivierung oder dem Abschluss eines atomaren Tasks prüft `SYNC` außerdem die Rückverfolgbarkeit: Der WHY-Pfad muss über `PiF1o`, `PiF1t`, `PiF1s` und `PiF2` zu mindestens einem `CiV` führen. Der WHO-Pfad muss ausführendes `RoleAssignment`, Mitglied, Rolle, verantwortliches Team und Organisation eindeutig ergeben. Ein fehlender Pflichtpfad verhindert den Statuswechsel.

Bei jeder Erzeugung oder Änderung eines CiV prüft `SYNC`, dass genau ein Wert mit den drei nicht leeren Dimensionen `notCiV`, `selfCiV` und `toServeCiV` vorliegt, genau ein zulässiger `HELD_BY`-Werteträger existiert und kein technisches Mitglied als persönlicher Scope dient. `INFORMED_BY` darf keine Selbstbeziehung bilden und wird niemals aus Namen, Mitgliedschaften oder Zugehörigkeiten abgeleitet. Für jedes verbundene `PiF2` müssen alle unmittelbar begründenden CiV denselben Werteträger besitzen. Eine Wertentscheidung oder Dimensionsübernahme erfordert menschliche Bestätigung und wird von `SYNC` nicht selbst erzeugt.

Bei jeder Erzeugung, Aktivierung oder Änderung eines RaN prüft `SYNC` `PROTECTS` getrennt von `GOVERNS`: Ein aktives RaN schützt mindestens ein CiV und ein PiF2, regelt mindestens ein zulässiges Umsetzungselement und erfüllt die beidseitige Kohärenz über `INSCRIBES_PURPOSE_IN`. Die Schutzobjekte müssen organisatorisch zu `scopeType`, `APPLIES_IN` und bei `ENTITY` zu den WHY-Pfaden der geregelten Ziele passen. Ein `GOVERNS` zu `PiF2` ist unzulässig. `SYNC` prüft menschlich beantragte Schutzkanten, erzeugt oder errät sie aber nicht selbst.

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
- CiV-Dimensionen, eindeutiger Werteträger, ausdrückliche `INFORMED_BY`-Herkunft und gemeinsamer PiF2-Scope,
- RaN-Schutzkanten, geschützte CiV-PiF2-Kohärenz, zulässige `GOVERNS`-Umsetzungstypen und Schutzscope,
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

T_current(G) enthält alle direkt zum PiF1o G gehörenden Tasks außer REPLACED und REVOKED; K_current(G) enthält dessen Kriterien mit derselben Statusausnahme. COMPLETED-Tasks bleiben aktuelle Beiträge. Historische Zuordnungen werden nicht gelöscht. Ein aktuelles REQUIRED-Kriterium in DRAFT blockiert.

1. Eine neue Verification verbindet genau ein COMPLETED-Result und ein ACTIVE-SuccessCriterion desselben PiF1o. Für aktuelle Aggregation muss der erzeugende Task zu T_current(G) gehören; Ergebnisse ausgeschiedener Tasks werden nicht automatisch übernommen.
2. Result- und Kriterienrevision aus dem abschließend geschützten Kandidatenzustand als positive evaluatedResultRevision und checkedCriterionRevision binden. EVALUATES und CHECKS verändern diese Revisionen nicht. Eine echte Änderung eines Prüfziels im selben Auftrag erfordert Bewertung seines endgültigen Zustands; andernfalls CONFLICT.
3. Für dieselbe Kombination aus Result, Kriterium und beiden Revisionen höchstens eine nicht abgelöste Verification zulassen. Eine weitere Prüfung muss die bestehende über SUPERSEDES ablösen. Nachfolge bleibt unverzweigt, zeitlich vorwärts, revisionsmonoton und auf dasselbe Result/Kriterium begrenzt.
4. Vor Übernahme Zielrevisionen und vollständige aktuelle Prüfungsmenge unter der Schreibsperre erneut prüfen. Eine Ablösung kann diese Menge ohne neue Zielrevision ändern.
5. Nur COMPLETED, nicht abgelöste Prüfungen aktueller Results/Kriterien mit passenden Revisionen aggregieren. Frühere Prüfungen bleiben unveränderte Tatsachen; spätere Kriterienaufhebung macht sie unanwendbar und ist kein Grund, historische Dokumentation zu löschen.
6. Messwert, measurementType, operator, targetValue und optionale Einheit müssen methodisch reproduzierbar zusammenpassen; andernfalls INCONCLUSIVE.
7. ALL erfordert mindestens eine anwendbare Prüfung und ausschließlich VALID; ANY mindestens eine anwendbare VALID-Prüfung. Fehlende, veraltete, INVALID oder INCONCLUSIVE-Prüfungen erfüllen das Kriterium nicht; bei ALL verhindert jede nicht gültige anwendbare Prüfung die Erfüllung.
8. ACHIEVED nur vorbereiten, wenn T_current(G) nicht leer ist und ausschließlich COMPLETED-Tasks mit erfüllten Voraussetzungen enthält, mindestens ein aktuelles REQUIRED-Kriterium existiert, alle aktuellen Pflichtkriterien ACTIVE und erfüllt sind sowie WHY-, WHO-, Modell- und RaN-Regeln gelten. OPTIONAL wird dokumentiert, blockiert aber nicht.
9. SYNC darf Tasks oder Pflichtkriterien nicht selbst aufheben, um Erfolg zu ermöglichen. Beantragte Umfangsänderungen brauchen gültigen Ersatzumfang oder einen zulässigen anderen Zielstatus; leerer aktueller Umfang eines weiterhin aktiven Ziels erzeugt CONFLICT.

Frühere Arbeit wird nur durch ausdrücklich übernommene aktuelle Arbeit mit nachvollziehbarer Evidence wiederverwendet; der alte PRODUCES-Bezug wird nicht umgehängt. ACHIEVED bleibt terminal.

**Kurzes Beispiel:** T1 bleibt REPLACED mit G verbunden; sein ausdrücklich eingebundener Nachfolger T2 ist COMPLETED. T1 blockiert G nicht. Eine neue Verification von T2 bindet Kriterienrevision 2, ohne sie durch CHECKS zu erhöhen. Erst eine echte Kriterienänderung auf 3 macht die Prüfung veraltet.

### 5.3.2 Auswertung von Task-Status

SYNC bildet aus dem vollständigen Kandidaten einen berechneten Abschlussgraphen: COMPOSITE → aktuelles direktes Kind und Task → DEPENDS_ON-Voraussetzung bedeuten jeweils, dass die Quelle vor dem Ziel nicht abschließen kann. Alle im Auftrag neuen Kanten und alle über PiF1o-Grenzen erreichten Voraussetzungen werden gemeinsam betrachtet. Ersetzte oder aufgehobene Voraussetzungstargets bleiben sichtbar und unerfüllt; keine automatische Umleitung auf Nachfolger.

1. Gespeicherte Hierarchie, Abhängigkeiten und Nachfolgeketten weiterhin separat prüfen. Zusätzlich jeden gemischten Zyklus vor Übernahme mit vollständigem Pfad und ursprünglichen Beziehungstypen als CONFLICT melden.
2. Aktuelle direkte Composite-Kinder schließen REPLACED und REVOKED aus. Ein aktueller Composite braucht mindestens ein aktuelles Kind. Ein Ersatz muss ausdrücklich zum selben PiF1o und gegebenenfalls aktuellen Parent gehören. Ausscheiden eines Parents hebt aktuelle Nachkommen nicht automatisch auf; ungeklärte Teilbäume erzeugen CONFLICT.
3. Den gemeinsamen Abschlussgraphen mit Voraussetzungen zuerst auswerten. Atomare und zusammengesetzte Tasks werden gemeinsam geordnet; pauschal alle atomaren vor allen Composites auszuwerten ist unzulässig.
4. Bei jedem aktuellen Task eigene DEPENDS_ON prüfen. Eine eigene unerfüllte Composite-Voraussetzung bewirkt bei Freigabe BLOCKED und verhindert seinen Abschluss und hat Vorrang vor der Kindaggregation. Sie wird nicht automatisch an Nachkommen vererbt.
5. DRAFT bleibt ohne ausdrückliche reguläre Freigabe Entwurf. DRAFT → BLOCKED erfordert diese Freigabe, vollständige Aktivierungsprüfungen und eine eigene oder aggregierte Blockade nach kanonischem Abschnitt 9.4.2. Bei ausdrücklicher Composite-Freigabe bestimmt dieselbe Priorität eigener Voraussetzungen und blockierter Kinder den Status `ACTIVE` oder `BLOCKED`; selbst bei vollständig abgeschlossenen Kindern entsteht zunächst `ACTIVE`. Der Abschluss benötigt eine spätere Auswertung dieses freigegebenen Zustands. Umfangsverkleinerung ist keine Freigabe. DRAFT → COMPLETED ist ausgeschlossen; auch ein Entwurf mit nur abgeschlossenen Kindern braucht einen eigenen regulären Freigabevorgang vor späterem Abschluss.
6. Für freigegebene Composites in ACTIVE oder BLOCKED gilt die geordnete Tabelle. Kinderumfang und Statusvorbedingungen müssen vorher gültig sein.
7. Anschließend aktuelle PiF1o-Umfänge, Kriterien und höhere Zukunftsebenen gemeinsam prüfen. Terminale Tasks werden nicht wieder geöffnet; ein Kandidat, der ihren dokumentierten Abschluss widerlegen würde, wird abgewiesen.

| Bedingung                                                                       | Abgeleiteter Status |
| ------------------------------------------------------------------------------- | ------------------- |
| Mindestens eine eigene Voraussetzung unerfüllt                                  | BLOCKED             |
| Eigene Voraussetzungen erfüllt, alle aktuellen Kinder COMPLETED                 | COMPLETED           |
| Eigene Voraussetzungen erfüllt, mindestens ein aktuelles Kind ACTIVE            | ACTIVE              |
| Eigene Voraussetzungen erfüllt, kein ACTIVE, mindestens ein BLOCKED-Kind        | BLOCKED             |
| Eigene Voraussetzungen erfüllt, nur DRAFT oder Mischung aus DRAFT und COMPLETED | ACTIVE              |

Ein freigegebener Composite kehrt nicht zu DRAFT zurück. Atomare Tasks benötigen weiterhin Ausführungs-, Team-, RaN- und bestätigte Abschlussbedingungen. Jeder tatsächlich übernommene Statuswechsel wird genau einmal historisiert.

**Kurzes Beispiel:** C enthält A und A benötigt C: C → A → C ist ein gemischter Zyklus. Sind alle Kinder von C abgeschlossen, aber seine eigene Voraussetzung B offen, bleibt C BLOCKED.

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

1. Für jedes aktive RaN mindestens ein geschütztes CiV, ein geschütztes PiF2, ihre Kohärenz über `INSCRIBES_PURPOSE_IN` und die organisatorische Vereinbarkeit mit dem Scope prüfen. Fehlende oder widersprüchliche Schutzbeziehungen blockieren die Aktivierung oder Entscheidung; `SYNC` ergänzt sie nicht automatisch.
2. Anhand von `governedTypes`, `scopeType` und gegebenenfalls `APPLIES_IN` alle potenziell einschlägigen aktiven und zeitlich gültigen `RaN` bestimmen; `GOVERNS` für die aktuellen konkreten Umsetzungselemente abgleichen und erforderliche Zielkanten vorbereiten.
3. Jede normalisierte Condition reproduzierbar auswerten. Nicht katalogisierte oder mehrdeutige Pfade ergeben `UNEVALUABLE`.
4. Aus `effect` und Bedingung pro Regel `ALLOW`, `DENY` oder `NO_DECISION` ableiten.
5. Eine einzelne Regelverletzung als `DENY` behandeln und die Entscheidung blockieren, ohne allein einen `RaNConflict` zu erzeugen.
6. Nur Regeln mit demselben `decisionKey`, überlappendem Scope und gemeinsamem Ziel auf widersprüchliche Ergebnisse vergleichen.
7. Für jeden tatsächlichen Widerspruch aus `ALLOW` und `DENY` die Prioritäten vergleichen.
8. Bei unterschiedlichen Prioritäten ausschließlich im Widerspruch der größeren Zahl Vorrang geben.
9. Bei gleicher höchster einschlägiger Priorität einen offenen `RaNConflict` mit `conflictType = PRIORITY_TIE` und einem aus ChangeEvent, sortierter Konfliktmenge und Entscheidung abgeleiteten `conflictKey` vorbereiten.
10. Bei nicht eindeutig bewertbarer Anwendbarkeit oder Vereinbarkeit einen offenen `RaNConflict` mit `conflictType = UNEVALUABLE` und entsprechendem `conflictKey` vorbereiten.
11. Automatische Änderungen blockieren, deren Zulässigkeit vom offenen Konflikt abhängt.

Ein niedriger priorisiertes `RaN` wird durch den Vorrang nicht aufgehoben und bleibt für vereinbare sowie andere Entscheidungen anwendbar. `ruleType` wird nicht als Rangfolge verwendet.

Vor dem Anlegen prüft `SYNC`, ob für denselben Veränderungsauftrag bereits ein `RaNConflict` mit demselben `conflictKey` besteht. Ein Wiederholungsversuch darf keinen Duplikatknoten erzeugen. Optionale Nachweise werden ausschließlich als `Evidence`-Knoten über `USES_EVIDENCE` verbunden.

Zur Auflösung eines vorhandenen Konflikts prüft ein nachfolgender `SyncRun` die über `CONFLICTING_RULE` verbundenen Regeln und die betroffenen Entitäten erneut. Nur wenn der dokumentierte Widerspruch nicht mehr besteht und der Versuch erfolgreich ist, bereitet `SYNC` `status = RESOLVED`, `resolvedAt`, `resolution`, `RESOLVED_BY` und `RESOLVED_THROUGH` vor. Der offene Ausgangszustand wird als `PiH` vorbereitet.

### 5.4 Vorbereitung der Änderung

1. Vollständigen geprüften Kandidaten mit dem Ausgangszustand vergleichen; Entitäten mit tatsächlichen Eigenschafts- oder ihnen zugeordneten Beziehungsänderungen deduplizieren. Reine neue Prüf-, Audit- und Historienbezüge ändern ihre Referenzziele nicht.
2. Je vorhandenem veränderlichem Eigentümer den vorherigen fachlichen Zustand und seine nach Snapshotprofil zugeordneten Beziehungen lesen. Neue PiH verwenden `snapshotSchemaVersion = "2.0"`; später angehängte fremde Prüftatsachen gehören nicht rückwirkend dazu.
3. StateSnapshot und sortierte RelationshipSnapshot-Einträge nach kanonischem Profil 2.0 bilden und SHA-256-contentHash berechnen. Genau ein PiH, HAS_HISTORICAL_STATE und CREATES_HISTORY je tatsächlich geänderter vorhandener Entität vorbereiten.
4. Aktuellen Zustand mit genau revision + 1 und neuem updatedAt vorbereiten. Bestehende PiH und Hashes bleiben unverändert und werden mit ihrem eigenen alten Profil gelesen.
5. Ein gültiger Auftrag ohne tatsächliche Änderung darf SUCCESS mit changedCount = historyCount = 0 dokumentieren. Auditverknüpfungen erzeugen keine fingierte Historie; der technische Erfolgsbeleg markiert trotzdem den Auftrag als verarbeitet.

Bei CREATED wird zunächst nur ein Kandidat gebildet. Nur SUCCESS erzeugt Zielknoten mit Revision 1, CREATED_BY und genau einer CHANGED_BY-Kante zum bestehenden ChangeEvent atomar. Die neue Entität erhält kein PiH; tatsächlich geänderte vorhandene Eigentümer können eigene PiH erhalten. CONFLICT oder FAILED erzeugt weder Zielknoten noch seine Erstellungsbezüge.

### 5.5 Historische Korrektur

1. Vorhandenes Ziel-PiH, requestedRevision = 1, genau ein passendes TARGETS_HISTORY und keine CHANGED_BY-Quelle prüfen. Austauschschema und neues valueSchemaVersion verwenden 2.0; ausschließlich strukturierter historicalCorrection-Payload ist zulässig.
2. Gültiges CORRECTED_BY, Begründung und optionales Evidence prüfen. Für ältere Snapshot-/Korrekturprofile explizit registrierte Resolver verwenden. Unklare Altpfade erzeugen CONFLICT; keine automatische Umdeutung oder Neuberechnung gespeicherter Hashes.
3. relationshipData bleibt eine Liste. Nur zur Adressierung eine Map mit Schlüssel direction + ":" + relationshipType + ":" + canonicalUUID(otherEntityId) bilden. Doppelte Schlüssel sind ungültig.
4. Nur die unten aufgeführten Pfadformen erlauben. Propertykorrekturen ersetzen eine vollständige TypedValue-Eigenschaft; Abstieg in value, Arrayindizes, Wildcards, Wurzelaustausch und Arrayanhänge sind verboten. Zulässige Properties bestimmt das referenzierte Snapshotprofil. Identität, Originalrevision und Identitätsbestandteile einer Beziehung werden nicht unter derselben Adresse umgedeutet.
5. JSON-Pointer in Segmente zerlegen, ~1 und ~0 nach RFC 6901 dekodieren und kanonisches Re-Encoding verlangen. correctedFields ist eindeutig, lexikografisch sortiert und schon im Request frei von gleichen oder verschachtelten Pfaden. previousValue und correctedValue haben exakt dieselbe Schlüsselmenge.
6. HistoryView aus unverändertem PiH und absoluten correctedValue-Überlagerungen nicht abgelöster Korrekturen bilden. Frühere previousValue werden nicht bei jedem Aufbau erneut gegen das Original-PiH geprüft.
7. SHA-256 einheitlich über {stateData, relationshipData} der wirksamen Sicht nach kanonischem Profil 2.0 berechnen. relationshipData ist nach relationshipType, direction und otherEntityId sortiert. Technische Adressmap, PiH-ID und Korrektur-IDs gehören nicht zum Hash-Eingang. Mit expectedHistoryViewHash vergleichen.
8. Existenz und bisherigen wirksamen Wert je neuem Pfad prüfen. ADDITION verlangt tatsächliches Fehlen und typisiertes NULL als previousValue; vorhandenes NULL ist nicht fehlend. CORRECTION und CLARIFICATION verlangen Existenz. NULL ist kein Löschbefehl.
9. Überlappung liegt vor, wenn dekodierte Segmente eines Pfades Präfix des anderen sind, einschließlich Gleichheit. Ohne Überlappung darf eine Korrektur parallel bestehen. Bei genau einer betroffenen aktiven Korrektur genau diese vollständig über SUPERSEDES ablösen: alle bisherigen kanonischen Pfade und weiterhin gültigen Werte übernehmen. Zusätzliche Pfade dürfen weder untereinander noch mit weiteren aktiven Korrekturen überlappen. Mehrfache Überlappung oder stiller Granularitätswechsel erzeugt CONFLICT.
10. Korrekturketten auf dasselbe PiH, zeitliche Vorwärtsrichtung und Zyklusfreiheit prüfen. Unter der gemeinsamen Schreibsperre Sicht, Hash, alte Werte, Existenz, Pfade und Ablösung unmittelbar vor Übernahme nochmals prüfen. Veralteter Hash erzeugt keine Korrektur.
11. Neue unveränderliche HistoricalCorrection mit baseHistoryViewHash = expectedHistoryViewHash, passenden CORRECTS, CAUSED_BY und CREATES_CORRECTION erzeugen. PiH bleibt unverändert; aktueller Modelländerungsbedarf bleibt ein eigener Auftrag.

```text
/stateData/properties/<property>
/relationshipData/<relationship-key>
/relationshipData/<relationship-key>/properties/<property>
```

Ein vollständiger Beziehungseintrag wird als TypedValue OBJECT übertragen. Richtung, Typ und Gegenentitäts-ID müssen zur Adresse passen. Die gespeicherte Beziehungsliste wird nicht zur Map.

Profil 2.0 verwendet UTF-8 ohne BOM oder zusätzliche Leerzeichen, nach Unicode-Codepoints sortierte Objektschlüssel und JSON-String-Escaping ohne pauschales ASCII-Escaping. INTEGER bleibt exakt und unbeschränkt; binäre Fließkommazahlen sind auch in OBJECT/ARRAY unzulässig. DECIMAL ist eine kanonische Dezimalzeichenkette ohne Exponent, führende Nullen, unnötige abschließende Nachkommanullen oder -0; verschachtelte Dezimalwerte werden als TypedValue DECIMAL dargestellt. Der Resolver folgt Abschnitt 2.2.9 von [`JCI_CONTEXT.md`](JCI_CONTEXT.md) und gemeinsamen Hash-Testvektoren.

**Kurzes Beispiel:** /stateData/properties/name und /stateData/properties/nameLong sind disjunkt. Ein ganzer Beziehungseintrag und seine /properties/validUntil überlappen. Nach vollständiger Ablösung einer früheren Ergänzung bleibt ihr absolut korrigierter Wert in der HistoryView erhalten.

### 5.6 Fachliche Atomarität und Abschlussdokumentation

Bei `SUCCESS` werden die folgenden Inhalte gemeinsam atomar übernommen:

- neue aktuelle Zustände,
- bei `CREATED` der neue Zielknoten mit `revision = 1`, `CREATED_BY` und `CHANGED_BY`,
- vorbereitete `PiH`,
- vorbereitete `HistoricalCorrection`-Objekte,
- aufgelöste `RaNConflict`-Objekte,
- alle zugehörigen Beziehungen,
- das abschließende `SyncEvent` mit seiner `runId`,
- die neue append-only `TRIGGERS`-Beziehung,
- technischer Erfolgsbeleg, Outbox und erhöhte graphEpoch nach Abschnitt 9.

Bei `CONFLICT` oder `FAILED` werden die angeforderte fachliche Änderung und alle noch nicht übernommenen Folgeänderungen vollständig zurückgerollt. Für einen nicht übernommenen Zustand entstehen weder eine neue Revision noch ein `PiH`. Nach dem Rollback speichert die Implementierung die Abschlussdokumentation mit dem unveränderlichen `SyncEvent` und gegebenenfalls neu erkannten `RaNConflict`-Objekten. Diese Dokumentation gehört zum Versuch, nicht zum abgewiesenen fachlichen Zustand.

```text
Fachliche Transaktion
├── SUCCESS  → Fachdelta, SyncEvent, Erfolgsbeleg und Outbox atomar übernehmen
├── CONFLICT → vollständig zurückrollen
└── FAILED   → vollständig zurückrollen

Abschlussdokumentation nach zurückgerolltem FAILED/CONFLICT
└── fehlendes SyncEvent genau einmal speichern
    └── bei Bedarf RaNConflict mit dokumentieren
```

Ist die FAILED-/CONFLICT-Ereignisspeicherung nach bestätigtem Rollback vorübergehend technisch unmöglich, bleibt eine dauerhafte Nachholpflicht bestehen. Nach Wiederherstellung der Schreibfähigkeit wird genau das fehlende `SyncEvent` mit derselben `runId`, demselben `ChangeEvent` und derselben `idempotencyKey` gespeichert und `TRIGGERS` einmalig ergänzt. Dieser Vorgang darf die fehlgeschlagene oder konfliktbehaftete Fachänderung nicht erneut ausführen.

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
runId
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

Ein fachlich oder kontrolliert technisch beendeter `SyncRun` erzeugt genau ein `SyncEvent` mit derselben eindeutigen `runId`. War dessen Speicherung vorübergehend unmöglich, wird sie nachgeholt. Jedes `SyncEvent` verweist über `EXECUTES` auf die verwendete SYNC-Definition und über `TRIGGERS` invers gelesen auf genau ein `ChangeEvent`. Eine zweite Abschlussdokumentation derselben `runId` ist unzulässig.

## 7. Zählwerte

Die Zählwerte müssen den gespeicherten Beziehungen und Änderungen entsprechen:

```text
affectedCount   = Anzahl verschiedener Ziele von AFFECTS
changedCount    = Anzahl tatsächlich übernommener aktueller Zustandsänderungen
historyCount    = Anzahl Ziele von CREATES_HISTORY
correctionCount = Anzahl Ziele von CREATES_CORRECTION
conflictCount   = Anzahl der über DETECTED_BY invers zugeordneten RaNConflict-Objekte
```

Alle Werte sind nicht negativ. Bei `SUCCESS` müssen die Zählwerte exakt mit dem übernommenen Graphzustand übereinstimmen. Bei `CONFLICT` oder `FAILED` beschreiben sie ausschließlich abschließend festgestellte beziehungsweise atomar übernommene Ergebnisse. Für `SUCCESS` und `CONFLICT` gilt `affectedCount >= 1`. Nur ein `FAILED`-Versuch, der vor erfolgreicher Zielauflösung endet, darf `affectedCount = 0` besitzen.

Ein neu erkannter offener `RaNConflict` wird in derselben atomaren Übernahme über `DETECTED_BY` mit dem abschließenden `SyncEvent` verbunden. Das `SyncEvent` erhält `outcome = CONFLICT`, wenn mindestens eine angeforderte Entscheidung wegen eines offenen Konflikts nicht übernommen werden konnte. Der durch ein `ChangeEvent` bezeichnete fachliche Veränderungsauftrag bildet genau eine atomare Transaktionsgrenze: Entweder werden alle zu diesem Auftrag gehörenden fachlichen Änderungen übernommen oder keine. Unabhängige Änderungen benötigen ein eigenes `ChangeEvent` und einen eigenen Synchronisationsvorgang.

## 8. Idempotenz und Wiederholung

1. Vollständigen normalisierten Request dauerhaft an Identität und Idempotenzkennung binden; gleiche Kennung mit anderem Inhalt abweisen.
2. Vor einem weiteren technischen Versuch unter der Sperre prüfen, ob der Auftrag bereits erfolgreich verarbeitet wurde. Dann vorhandenes Ergebnis liefern, keine neue Fachausführung beginnen.
3. Jeder tatsächlich ausgeführte und beendete Versuch besitzt eigene runId und genau ein unveränderliches SyncEvent. Technischer Retry ändert niemals requestedRevision im ChangeEvent.
4. Revisionskonflikt beendet den Versuch mit CONFLICT. Neubewertung auf anderer Ausgangsrevision benötigt neuen Request und neues ChangeEvent.
5. Bei SUCCESS Erfolgsbeleg, Delta, PiH, Korrekturen, SyncEvent und Outbox zwingend gemeinsam atomar speichern. Auch erfolgreicher fachlicher No-op wird als verarbeitet markiert.
6. Bei unbekanntem Commit-Ausgang zuerst unter der Sperre anhand derselben runId gespeicherten Erfolg und Ereignis prüfen. Verlorene Antwort ist kein Grund für erneute Fachänderung.

## 9. Parallelität

Die Referenz verwendet genau eine technische Schreibsperre pro gemeinsamem JCI-Modellbestand beziehungsweise Datenbank, vor entscheidungsrelevanten Lesezugriffen bis Commit/Rollback. Nicht je RoFOrg oder dynamisch verbundener Teilkomponente: grenzüberschreitende Regeln und Abhängigkeiten teilen denselben Schutzbereich.

Unter der Sperre alle Eigenschaften, Beziehungen, Mengen und relevanten Abwesenheiten frisch lesen und den vollständigen Kandidaten prüfen. Dies schützt neu hinzukommende RaN, Mitgliedschaften, Scopeänderungen, gemeinsam zyklische Kanten und konkurrierende Kapazitätsbelegungen. Alle JCI-Schreibwege einschließlich Bootstrap, Migration, Auditappend, Verifications, SUPERSEDES, Korrekturen und nachgeholter Ereignisse verwenden dieselbe Sperre. Technische Locks sind keine JCIEntity und erzeugen keine Fachrevisionen/PiH.

Vor Übernahme serverseitigen fachlichen Entscheidungszeitpunkt festlegen und im technischen Commitbeleg speichern. Alle Zeitbedingungen und davon abhängigen Entscheidungen für genau diesen Zeitpunkt abschließend neu auswerten, einschließlich inzwischen gültiger Regeln und abgelaufener Rollen. completedAt bleibt Abschlusszeit. Garantiert wird Gültigkeit am Entscheidungszeitpunkt, nicht an späterer physischer Commit-Bestätigung oder externer Ausführung.

Spätere Optimierung darf unter der Sperre einen Snapshot mit technischer graphEpoch lesen, außerhalb rechnen und unter erneut erworbener Sperre prüfen. Jede übernommene JCI-Schreibtransaktion erhöht die Epoch, auch reine revisionsneutrale Prüf-/Auditbezüge. Abweichung verwirft die Vorbereitung; frisch lesen, ohne angeforderte Zielrevision zu ändern. Zeitbedingungen unabhängig von Epoch erneut prüfen. Nur Fachrevisionen zu vergleichen oder bekannte Entitäten zu sperren genügt nicht.

## 10. Ausfall und Wiederaufnahme

Vollständiger technischer Request-/Runbeleg bleibt dauerhaft verfügbar. Run-Besitz verwendet Fencing-Token: Ein nach Claim-Verlust wieder aktiver Worker darf keine Fachänderung oder Abschlussdokumentation übernehmen. Heartbeats dürfen getrennt laufen; Besitzwechsel und Abschluss müssen mit der geschützten Commitentscheidung abgestimmt sein.

Datenbankfehler rollen die gesamte Fachtransaktion zurück. Nach wiederhergestellter Schreibfähigkeit prüft Recovery unter derselben Sperre zuerst den tatsächlichen Ausgang. Bereits vorhandener Erfolg wird nicht erneut ausgeführt. Fehlt nach gesicherter Beendigung der ursprünglichen Transaktion das Ereignis, wird die FAILED-/CONFLICT-Abschlussdokumentation mit derselben runId genau einmal nachgeholt. SUCCESS besitzt schon atomar seinen Erfolgsbeleg und sein SyncEvent.

Die technische Outbox wird mit dem Abschlussereignis gespeichert. Wiederholte Zustellung nach Dispatcher-Absturz ist möglich; Empfänger benötigen stabilen Deduplizierungsschlüssel. Outbox-/Laufbelege sind keine fachlichen Graphobjekte und ändern keine fachlichen Zählwerte.

## 11. Austauschformat

`JCIChangeRequest` und `JCISyncResult` verwenden das in Abschnitt 12.6 von [`JCI_CONTEXT.md`](JCI_CONTEXT.md) festgelegte, gegenüber 1.1 inkompatibel präzisierte Austauschformat mit `schemaVersion = "2.0"`. Die verbindlichen JSON-Schemas liegen unter `docs/schemas/`. Ein SyncRun lehnt Dokumente mit unbekannter `schemaVersion`, zusätzlichen nicht erlaubten Feldern oder ungültigen Inhalten vor jeder Graphänderung ab.

Ein angenommener `JCIChangeRequest` enthält mindestens `requestId`, `idempotencyKey`, `requestedAt`, `requestedRevision`, `changeType`, `target`, `requestedByRoleAssignmentId` und `reason`. Beim Speichern gilt:

```text
ChangeEvent.id                = requestId
ChangeEvent.idempotencyKey    = idempotencyKey
ChangeEvent.targetEntityId    = target.id
ChangeEvent.targetEntityType  = target.entityType
ChangeEvent.requestedRevision = requestedRevision
```

Bei `CREATED` ist `requestedRevision = null`; bei allen anderen Änderungstypen ist es eine positive Ganzzahl. Allgemeine Änderungen verwenden mindestens eine Operation aus `ADD | REPLACE | REMOVE | CONNECT | DISCONNECT`.

`HISTORICAL_CORRECTION` verwendet keine generischen `operations`, sondern genau einen strukturierten Payload:

```text
historicalCorrection = {
  correctionType,
  reason,
  valueSchemaVersion,
  expectedHistoryViewHash,
  correctedFields[],
  previousValue,
  correctedValue
}
```

`valueSchemaVersion = "2.0"`; correctedFields ist eindeutig, lexikografisch sortiert und frei von Segmentpräfix-Überlappungen gemäß Abschnitt 5.5. `previousValue` und `correctedValue` besitzen genau dieselbe Schlüsselmenge. Der Auftrag adressiert über `target` dasselbe `PiH`, das im Graphen über `TARGETS_HISTORY` verbunden ist.

Ein `JCISyncResult` enthält neben `requestId` und `syncEventId` verpflichtend die `runId`, `outcome`, `completedAt`, alle fünf Zählwerte sowie Listen der betroffenen Entitäten, Konflikte und Fehler. Bei `SUCCESS` oder `CONFLICT` ist `affectedCount >= 1`; nur ein frühes `FAILED` vor Zielauflösung erlaubt den Wert `0`.

**Kurzes Beispiel:** Ein `CONNECT` darf nur einen katalogisierten Beziehungstyp, Richtung und Gegenentitäts-ID enthalten. Ein unbekanntes `LINKS_TO` wird abgewiesen und nicht als neue Kante interpretiert.

## 12. Initialer Bootstrap

Der initiale Bootstrap ist kein `SyncRun`, kein Veränderungsauftrag und kein Import. Er löst ausschließlich einmalig das Vertrauenswurzelproblem eines vollständig leeren Graphen.

1. Vor Beginn muss der fachliche Graph vollständig leer sein; technische Gate-/Runbelege sind keine JCIEntity. Auch Bootstrap hält die gemeinsame Schreibsperre bis zum Commit.
2. In einer einzigen atomaren Transaktion werden eine `RoFOrg`, ein `RoFTeam`, ein technisches `RoFTeamMember`, eine `RoFRole`, genau ein Root-`RoleAssignment` mit `bootstrapKey = "ROOT"`, eine `SYNC`-Definition und alle erforderlichen RoF-Beziehungen erzeugt.
3. Alle sechs Bootstrap-Entitäten erhalten unmittelbar `status = ACTIVE`, `revision = 1` sowie denselben Wert für `createdAt` und `updatedAt`. Vorhandene `validFrom`-Werte der Typen und Beziehungen entsprechen demselben Bootstrapzeitpunkt. Dies ist die einzige Ausnahme vom regulären `DRAFT`-Start.
4. Nur das Root-`RoleAssignment` besitzt dauerhaft kein `CREATED_BY`. Alle anderen Bootstrap-Entitäten besitzen genau ein `CREATED_BY` zum Root-`RoleAssignment`.
5. Für den Bootstrap entstehen weder `ChangeEvent`, technischer `SyncRun`, `SyncEvent` noch `PiH`.
6. Vor dem Commit werden Eindeutigkeit der Vertrauenswurzel, Vollständigkeit des Minimalgraphen, `ACTIVE`-Status aller sechs Entitäten und Ausführbarkeit der SYNC-Definition geprüft. Bei einem Fehler wird alles zurückgerollt.
7. Nach erfolgreichem Commit sind Wiederholung und ein zweites Root-`RoleAssignment` verboten. Alle weiteren Änderungen verwenden ausschließlich den normalen SYNC-Ablauf.
8. Importierte Entitäten ohne vollständige Erstellungsprovenienz bleiben `DRAFT`; ein Import darf die Bootstrap-Ausnahme nicht beanspruchen.

**Kurzes Beispiel:** Das Deployment legt Organisation, Administrationsteam, technisches Mitglied, Rolle, Root-Zuordnung und aktive SYNC-Definition gemeinsam an. Danach fordert dieses Root-`RoleAssignment` den ersten regulären `CREATED`-Vorgang an.
