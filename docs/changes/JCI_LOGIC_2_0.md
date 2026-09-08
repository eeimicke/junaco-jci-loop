# JCI-Logik 2.0: sechs zusammenhängende Korrekturen

[Deutsch](JCI_LOGIC_2_0.md) · [English](../en/changes/JCI_LOGIC_2_0.md)

Die Änderung behebt sechs Lücken in Revisionierung, Zielerreichung, Task-Auswertung, konkurrierenden Änderungen und historischen Korrekturen. Die zehn Kernelemente und vorhandenen Entitäts- und Beziehungstypen bleiben erhalten. Verbindlich sind [Kontext](../JCI_CONTEXT.md), [Graphregeln](../JCI_GRAPH_RULES.md) und [SYNC-Spezifikation](../JCI_SYNC_SPEC.md).

Regel-, Snapshot-, Werte- und Austauschprofile verwenden Version `2.0`. Die JSON-LD-Syntaxversion `1.1` und der Namensraum `https://eeimicke.github.io/junaco-jci-loop/ns/jci/1.0#` bezeichnen andere Identitäten und bleiben unverändert. Das [Snapshot-Payloadschema](../schemas/jci-history-snapshot.schema.json) beschreibt neue historische Nutzdaten; [Legacy-Schemas](../schemas/legacy/1.1/) bleiben für ältere Profile verfügbar.

## 1. Fachlichen Zustand von neuen Nachweisen trennen

Der versionierte Beziehungskatalog ordnet den fachlichen Beziehungszustand ausdrücklich je Kontext und Endpunkt zu. Bei tatsächlicher Änderung dieses Zustands oder ihrer Eigenschaften erhält eine bestehende veränderliche Entität innerhalb eines erfolgreichen Auftrags genau eine neue Revision und ein PiH.

Die neue Verification trägt `EVALUATES`, `CHECKS`, `USES_EVIDENCE` und `SUPERSEDES`. Ihre Bezugnahmen erhöhen die Revisionen von Result, Kriterium, Evidence oder früherer Verification nicht. Für katalogisierte Ereignis-, Herkunfts-, Konflikt- und Historienbezüge gilt dieselbe ausdrückliche Zuordnung. Unbekannte Beziehungskontexte dürfen nicht stillschweigend als revisionsneutral gelten; fachliche Strukturbeziehungen folgen ihrer Endpunktzuordnung.

Eine Prüfung des Kriteriums auf Revision 2 bleibt beim Anlegen von `CHECKS` anwendbar. Erst eine echte Kriterienänderung erzeugt Revision 3 und macht sie für den neuen Stand unanwendbar. Eine Ablösung kann trotzdem bei unveränderten Zielrevisionen die Prüfungsmenge ändern; diese Menge wird durch Schritt 5 geschützt. Neue PiH enthalten den zugeordneten fachlichen Beziehungszustand. Frühere PiH, Daten und Hashes werden nicht umgeschrieben.

## 2. Historische Zuordnung und aktuellen Zielumfang unterscheiden

Gespeicherte Zuordnungen bleiben erhalten; ausgewertet werden berechnete Teilmengen:

```text
T_all(G) = tasks directly linked from G by DECOMPOSES_INTO
T_current(G) = {t in T_all(G) | t.status not in {REPLACED, REVOKED}}
K_current(G) = {k linked from G by HAS_SUCCESS_CRITERIA
                | k.status not in {REPLACED, REVOKED}}
```

`COMPLETED` bleibt ein aktueller Beitrag. `ACHIEVED` verlangt eine nicht leere aktuelle Task-Menge, vollständig abgeschlossene Tasks mit erfüllten Voraussetzungen sowie mindestens ein aktuelles `REQUIRED`-Kriterium. Jedes aktuelle Pflichtkriterium muss `ACTIVE` und durch anwendbare Prüfungen erfüllt sein. WHY, Verantwortung, Rollen, RaN und übrige Bedingungen gelten zusätzlich. `DRAFT`-Pflichtkriterien blockieren; leere Mengen begründen keinen Erfolg.

Ersatz und Aufhebung brauchen einen begründeten Auftrag und vollständige RaN-/Auswirkungsprüfung. Ein Nachfolger wird ausdrücklich demselben PiF1o und einer gültigen aktuellen Parent-Struktur zugeordnet. `DEPENDS_ON` wird nicht automatisch umgebogen; ein referenzierter ersetzter oder aufgehobener Task bleibt eine unerfüllte Voraussetzung.

Aktuelle Composite-Kinder werden ebenso gefiltert und dürfen nicht leer sein. Die Aufhebung eines Composite hebt seine Nachkommen nicht automatisch auf. Der Auftrag muss deren Hierarchie klären oder sie ausdrücklich gesondert ersetzen beziehungsweise aufheben; sonst entsteht `CONFLICT`. Der letzte aktuelle Task oder das letzte Pflichtkriterium eines weiterhin aktiven Ziels darf nur mit gültigem Ersatzumfang oder einem anderen zulässigen Zielstatus entfallen.

Für aktuelle Zielerreichung zählen Results aktuell berücksichtigter Tasks. Wiederverwendung früherer Arbeit braucht eine ausdrückliche Übernahme durch aktuelle Arbeit mit eigenem Result und nachvollziehbarer Evidence; alte `PRODUCES`-Bezüge werden nicht umgehängt. Historische Nachweise bleiben erhalten. Terminale Tatsachen werden nicht automatisch wieder geöffnet.

## 3. Composite-Voraussetzungen vor Kindaggregation auswerten

`COMPOSITE` bleibt als Quelle von `DEPENDS_ON` zulässig. Eigene Voraussetzungen bestimmen seinen Status bei der Freigabe und sperren bei Nichterfüllung seinen Abschluss. Sie werden nicht automatisch an Nachkommen vererbt; deren Ausführungssperren müssen ausdrücklich modelliert werden.

Für einen bereits freigegebenen Composite mit Ausgangsstatus `ACTIVE` oder `BLOCKED` und gültigem, nicht leerem aktuellen Kinderumfang gilt folgende Reihenfolge:

| Bedingung                                                                            | Folgestatus |
| ------------------------------------------------------------------------------------ | ----------- |
| Eigene Voraussetzung unerfüllt                                                       | `BLOCKED`   |
| Eigene Voraussetzungen erfüllt, alle aktuellen Kinder abgeschlossen                  | `COMPLETED` |
| Eigene Voraussetzungen erfüllt, mindestens ein Kind aktiv                            | `ACTIVE`    |
| Eigene Voraussetzungen erfüllt, kein Kind aktiv, mindestens eines blockiert          | `BLOCKED`   |
| Eigene Voraussetzungen erfüllt, nur Entwürfe oder Entwürfe und abgeschlossene Kinder | `ACTIVE`    |

Ein freigegebener Composite kehrt nicht zu `DRAFT` zurück. Ein Entwurf benötigt reguläre Freigabe samt Aktivierungsprüfung nach `ACTIVE` beziehungsweise `BLOCKED`. Bei ausdrücklicher Composite-Freigabe bestimmt dieselbe Priorität eigener Voraussetzungen und blockierter Kinder den Status `ACTIVE` oder `BLOCKED`; selbst bei vollständig abgeschlossenen Kindern entsteht zunächst `ACTIVE`. Der Abschluss benötigt eine spätere Auswertung dieses freigegebenen Zustands. Reine Umfangsreduktion erzeugt keine Freigabe und kein direktes `DRAFT → COMPLETED`. Terminale Tasks werden nicht wieder geöffnet.

Damit bleibt ein Composite trotz abgeschlossener Kinder bei offener eigener Voraussetzung `BLOCKED`. Entfällt sein letztes blockiertes Kind und bleiben nur Entwürfe, gilt nach früherer Freigabe und bei erfüllten eigenen Voraussetzungen `ACTIVE`.

## 4. Hierarchie und Voraussetzungen gemeinsam auf Abschlusszyklen prüfen

SYNC berechnet einen Abschlussgraphen über aktuelle Tasks aller durch Hierarchie und Voraussetzungen erreichten PiF1o:

```text
C -> K : C is COMPOSITE and K is a current direct child
T -> P : T DEPENDS_ON P
```

Beide Pfeile bedeuten, dass die Quelle vor dem Ziel nicht abschließen kann. Ein gemeinsamer Zyklus führt zu `CONFLICT` mit vollständigem Pfad und ursprünglichen Beziehungstypen. Bestehende Hierarchie- und Nachfolgeprüfungen bleiben bestehen; ersetzte oder aufgehobene Voraussetzungen bleiben sichtbar und unerfüllt. Es entsteht kein neuer gespeicherter Graphobjekttyp.

Atomare und zusammengesetzte Tasks werden gemeinsam mit Voraussetzungen zuerst ausgewertet; danach folgen PiF1o und höhere Zukunftszustände. Der vollständige Kandidat enthält alle neuen Kanten desselben Auftrags. Beispiel: C enthält A, A benötigt C. `C → A → C` wird abgewiesen, obwohl jeder Beziehungstyp für sich azyklisch ist. Der Commit-Schutz verhindert, dass parallele Aufträge die gemeinsame Prüfung umgehen.

## 5. Die vollständige Entscheidungsgrundlage bis zum Commit schützen

Alle JCI-Schreibwege verwenden einen gemeinsamen technischen Datenbank-Schreiblock für den gesamten Modellbestand, auch über Organisationsgrenzen. Dazu gehören revisionsneutrale Nachweise, Ereignisse, Korrekturen und Migrationen. Der Sperrzustand ist keine JCIEntity und erhält keine PiH.

Der vollständige normalisierte Request wird unveränderlich an `requestId` und `idempotencyKey` gebunden; derselbe Schlüssel mit anderem Inhalt wird abgewiesen. Vor allen maßgeblichen Lesezugriffen wird die Sperre innerhalb einer expliziten Transaktion erworben und bis Commit oder Rollback gehalten. Vorberechnungen außerhalb der Sperre sind unverbindlich.

Die geschützte Sicht umfasst Eigenschaften, Beziehungen, aktuelle Mengen und relevante Abwesenheiten: auch neue RaN, Rollen-/Scope-Änderungen und abgelöste Prüfungen bei unveränderten Zielrevisionen. Zuvor gelesene Entitätsrevisionen allein genügen nicht.

Alle Zeitbedingungen und davon abhängige Entscheidungen werden für denselben abschließenden serverseitigen fachlichen Entscheidungszeitpunkt ausgewertet. Der technische Commitbeleg hält ihn fest; `completedAt` bleibt die Abschlusszeit. Gültigkeit gilt an diesem Entscheidungszeitpunkt; sie verspricht kein Anhalten der Uhr bis zur physischen Commitbestätigung.

Fachliches Delta, Revisionen, PiH, Dokumentation, SyncEvent und technischer Erfolgsbeleg werden atomar übernommen. Technischer Run-Besitz verhindert die Übernahme durch überholte Worker. Nach Antwortverlust wird zuerst der gespeicherte Ausgang derselben Run-ID ermittelt. Ein Revisionskonflikt ändert nicht `requestedRevision`; eine neue fachliche Ausgangsbasis braucht einen neuen Request.

## 6. Historische Korrekturen stabil adressieren und eindeutig überlagern

Profil 2.0 erlaubt vollständige typisierte Eigenschaften und vollständige Beziehungseinträge:

```text
/stateData/properties/<property>
/relationshipData/<direction:relationshipType:otherEntityId>
/relationshipData/<direction:relationshipType:otherEntityId>/properties/<property>
```

Beispiel: `/stateData/properties/name`. Ein Beziehungsschlüssel lautet `INCOMING:HAS_MEMBER:00000000-0000-0000-0000-000000000007`. `relationshipData` bleibt gespeichert eine Liste; nur die Adressierung verwendet eine virtuelle eindeutige Schlüsselabbildung. Umsortieren verändert die Adresse nicht.

Wurzelersetzungen, Arrayindizes, Wildcards, Anhängeoperatoren und Abstieg in `TypedValue.value` sind ausgeschlossen. Identität, Revision und Identitätsbestandteile einer Beziehung werden nicht unter derselben Adresse umgedeutet. Das Snapshot-Schema bestimmt zulässige Eigenschaften.

Pfade werden in Segmente zerlegt und nach JSON Pointer dekodiert. Gleichheit oder segmentweise Präfixbeziehung bedeutet Überschneidung. `name` und `nameLong` sind Geschwister; ein ganzer Beziehungseintrag und seine Eigenschaft überlappen. Innerhalb eines neuen Auftrags sind Überschneidungen unzulässig.

| Betroffene aktive Korrekturen | Ergebnis                                       |
| ----------------------------- | ---------------------------------------------- |
| Keine                         | Neue Korrektur ohne `SUPERSEDES`               |
| Genau eine                    | Diese vollständig über `SUPERSEDES` ablösen    |
| Mehr als eine                 | `CONFLICT`, keine automatische Zusammenführung |

Vollständige Ablösung behält mindestens die kanonischen Pfade der Vorgängerin und deren weiterhin gültige Werte. Zusätzliche Pfade dürfen nicht untereinander oder mit anderen aktiven Korrekturen überlappen; ein Wechsel zwischen Eigenschaft und ganzer Beziehung erfolgt nicht stillschweigend.

`ADDITION` verlangt einen fehlenden Pfad. Vorhandenes `NULL` ist vorhanden und bedeutet keine Löschung. `CORRECTION` und `CLARIFICATION` verlangen vorhandene Pfade. `previousValue` wird bei Annahme gegen die damalige wirksame Sicht geprüft. Spätere HistoryViews überlagern unveränderte PiH mit absoluten `correctedValue`-Werten nicht abgelöster Korrekturen; die frühere Vorbedingung wird nicht erneut gegen das Original-PiH geprüft.

Hashing verwendet wirksame `stateData` und die kanonisch sortierte `relationshipData`-Liste gemäß versioniertem Serialisierungsprofil, nicht die virtuelle Schlüsselabbildung. Gemeinsame Testvektoren prüfen Kodierung, Sortierung und exakte Zahlenbehandlung. Ältere Profile behalten eigene Resolver.

## Auswirkungen auf die zehn Kernelemente

| Kernelement | Fachliche Auswirkung                                                                                                                                 |
| ----------- | ---------------------------------------------------------------------------------------------------------------------------------------------------- |
| CiV         | Werte und menschliche Wertentscheidung bleiben maßgeblich; Zustandsverantwortung für ausgewählten historischen Kontext wird ausdrücklich zugeordnet. |
| PiF2        | Zweck und WHY-Pfad bleiben; abgeleitete Zielaussagen verwenden eine konsistente geschützte Basis.                                                    |
| PiF1s       | Strategische Aggregation folgt korrigierter operativer und taktischer Auswertung.                                                                    |
| PiF1t       | Taktische Aggregation folgt gültiger Task- und PiF1o-Auswertung.                                                                                     |
| PiF1o       | Nicht leere aktuelle Task- und Pflichtkriterienmengen trennen Zielerreichung von abgelöster Arbeit.                                                  |
| RaN         | Regeltypen bleiben; neue Regeln, Scope und Zeitgültigkeit werden beim Commit berücksichtigt.                                                         |
| RoF         | Verantwortung, Rollen und Umfangsentscheidungen bleiben zu prüfen; technische Sperren sind kein Organisationsobjekt.                                 |
| ERoF        | Nutzungs- und Eigentumsbeziehungen bleiben Bedingungen; relevanter Umweltkontext gehört zur geschützten Entscheidungsgrundlage.                      |
| SYNC        | Kandidat, Abschlussgraph, Revisionszuordnung und geschützter Commit werden zusammen ausgewertet.                                                     |
| PiH         | Neue Snapshots/Korrekturen verwenden 2.0; bestehende Daten, Identitäten und Hashes bleiben unverändert.                                              |

Kardinalitäten bestehender gespeicherter Beziehungen bleiben erhalten. Hinzu kommen Auswertungsregeln für nicht leere aktuelle Mengen, konsistente aktuelle Teilbäume, gemeinsame Zyklen und überschneidungsfreie Korrekturpfade. Es entstehen keine neuen Kanten oder automatischen Ersatzzuordnungen. Zustandsverantwortung ist Katalogmetadatum; Abschlussgraph und Korrekturschlüsselabbildung sind berechnete Sichten.

## Gemeinsame Reihenfolge und 23 Abnahmefälle

Die sechs Schritte gelten zusammen. Unter der Sperre wird der vollständige Kandidat gebildet, Zustandsverantwortung und aktuelle Mengen bestimmt, der Abschlussgraph geprüft, Voraussetzungen und Composite-Status ausgewertet und Nachweise sowie Zielerreichung geprüft. Betroffene Korrekturen werden gegen die geschützte HistoryView geprüft. Zeitgültigkeit und endgültiger Kandidat werden vor atomarer Übernahme bestätigt.

| Nr. | Abnahmefall                                                    | Erwartetes Ergebnis                                                      |
| --- | -------------------------------------------------------------- | ------------------------------------------------------------------------ |
| 1   | Verification bindet Kriterium 2 und legt `CHECKS` an           | Kriterium bleibt 2, Prüfung anwendbar.                                   |
| 2   | Kriterium wird anschließend fachlich geändert                  | Revision 3; alte Prüfung bleibt und wird unanwendbar.                    |
| 3   | Neue Prüfung löst Prüfung derselben Revisionen ab              | Zielrevisionen gleich; aktuelle Prüfungsmenge ändert sich.               |
| 4   | Ereignis referenziert SYNC und betroffene Entitäten            | Keine Historisierung allein aufgrund der Dokumentation.                  |
| 5   | T1 `REPLACED`, T2 `COMPLETED`, übrige Bedingungen erfüllt      | T1 bleibt zugeordnet und blockiert das Ziel nicht.                       |
| 6   | Alle aktuellen Tasks oder Pflichtkriterien würden entfallen    | Kein automatischer Erfolg; ungültiger aktiver Umfang wird abgewiesen.    |
| 7   | Aufgehobener Composite mit ungeklärten aktuellen Nachkommen    | `CONFLICT`, keine unsichtbare Teilbaumaufhebung.                         |
| 8   | Composite-Kinder abgeschlossen, eigene Voraussetzung offen     | `BLOCKED`.                                                               |
| 9   | Freigegebener Composite hat nur noch `DRAFT`-Kinder            | Bei erfüllten eigenen Voraussetzungen `ACTIVE`.                          |
| 10  | `DRAFT`-Composite verliert durch Aufhebung offene Kinder       | Kein automatisches `COMPLETED`.                                          |
| 11  | C enthält A, A benötigt C                                      | Gemischter Zyklus wird abgewiesen.                                       |
| 12  | Zwei neue Kanten bilden gemeinsam einen Zyklus                 | Gesamter Auftrag wird abgewiesen.                                        |
| 13  | Parallele Aufträge bilden gemeinsam Zyklus oder Überbelegung   | Zweiter Commit berücksichtigt ersten und wird gegebenenfalls abgewiesen. |
| 14  | Relevante RaN, Rolle oder Scope ändert sich nach Vorberechnung | Abschluss verwendet neue Basis oder meldet Konflikt.                     |
| 15  | Neue verbietende RaN entsteht nach Vorberechnung               | Sie wird trotz früherer Abwesenheit berücksichtigt.                      |
| 16  | `VALID` wird durch `INVALID` abgelöst, Zielrevisionen gleich   | Parallele Zielaggregation darf alte Prüfungsmenge nicht verwenden.       |
| 17  | Rolle läuft beim Warten auf Sperre ab                          | Abschließende Zeitprüfung berücksichtigt Ablauf.                         |
| 18  | Erfolg gespeichert, Antwort verloren                           | Wiederaufnahme führt Fachänderung nicht erneut aus.                      |
| 19  | Korrektur betrifft Elternpfad und Unterpfad                    | Überschneidung wird erkannt.                                             |
| 20  | Pointervergleich `name` und `nameLong` (nur Syntax)            | Kein falscher Präfixkonflikt.                                            |
| 21  | Beziehungsliste wird nur umsortiert                            | Stabile Adresse bezeichnet dieselbe Beziehung.                           |
| 22  | Ergänztes Feld wird später vollständig abgelöst                | Wirksame Sicht enthält letzten absoluten Korrekturwert.                  |
| 23  | Bestehende PiH verwenden älteres Snapshotprofil                | Keine rückwirkende Änderung von Daten oder Hashes.                       |

## Migration und Grenzen der Referenzvalidierung

Vor Aktivierung wird der Bestand auf gemischte Zyklen, unklare Ersatzkontexte, leere aktuelle Umfänge, widersprüchliche Composite-Status und problematische Korrekturpfade geprüft. Unklare Fälle benötigen einen nachvollziehbaren Auftrag. Terminale Tatsachen werden nicht automatisch neu berechnet. Alte PiH, Korrekturen und Hashes behalten ihre Profile; unklare Altfälle werden nicht durch stilles Uminterpretieren von Pfaden migriert.

Alte transportierte Daten werden nach ihren [Legacy-Schemas](../schemas/legacy/1.1/) gelesen. Neue Schreibvorgänge verwenden Profile 2.0 und aktuelle [Schemas](../schemas/). Namensraum, JSON-LD-Syntaxversion und fachliche Profilversionen bleiben getrennt.

[Referenzfunktionen](../../reference/jci_rules.py) und [Regeltests](../../tests/test_model_rules.py) prüfen ausführbare Regelteile. [Spezifikationsprüfungen](../../tests/test_spec_consistency.py) prüfen Dokument- und Artefaktkonsistenz. Der Helfer ist keine produktive SYNC-Engine, kein vollständiger Neo4j-Adapter und keine Implementierung aller fachlichen Schreibwege.

Die 23 Fälle beschreiben erforderliche Abnahme, keinen Nachweis einer produktiv getesteten SYNC-Version. Konkurrierende Transaktionen, Sperrbesitz, Worker-Ausfall, Antwortverlust, echte Atomarität und Zeitablauf brauchen zusätzlich Tests mit realen Datenbanktransaktionen und kontrollierten Haltepunkten. Statische Abfragen und reine Funktionsprüfungen belegen diese Eigenschaften nicht.

Die Prüfung dieser Änderung umfasst ausführbare Regel- und Schemaprüfungen, gemeinsame [Hash-Testdaten](../../tests/fixtures/history-profile-2.0.json) und die [Regressionstests](../../tests/test_reference_rules.py). Aufruf im Repository-Stamm: `python -B -m unittest discover -s tests -v`. Deutsche und englische Kapitel-, Tabellen-, Codeblock- und Bezeichnerstrukturen werden gemeinsam geprüft. Die Referenzfunktionen erhalten vollständige Kandidatendaten; Autorisierung und produktiver Datenbankadapter bleiben Aufgabe des Aufrufers.

Prüfstand vom 07.09.2026: **81 Tests bestanden**, darunter 41 neue Referenzregressionen. Alle 18 deutsch-englischen Sprachpaare haben den Strukturabgleich bestanden; lokale Links, ausgerichtete Tabellen, kanonische Bezeichner, Schemas und Mermaid-Beziehungsnamen wurden geprüft. Die früheren Schemainhalte 1.1 bleiben erhalten. Es wurde keine reale Neo4j-Transaktion oder Migration ausgeführt.
