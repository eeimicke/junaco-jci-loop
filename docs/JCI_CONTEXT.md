# JUNACO Continuous Integration for Organisations
## 1. JUNACO Continuous Integration for Organisations

### 1.1 Herkunft und Zweck

Dieses Dokument beschreibt das **JUNACO Continuous Integration Model for Organisations** und den daraus gebildeten **JCI Loop**. Das Modell baut auf dem Viable System Model (VSM) von Stafford Beer und dem von Ernst Rother, heute Ernst Eimicke, in seiner Masterarbeit ausgearbeiteten Intrinsic Value Based System Model auf. In der Praxis der Junaco Organisationsentwicklung GmbH wurde es von Jana Eimicke und Julian Ulbricht zum heutigen JCI-Modell weiterentwickelt.

Die Masterarbeit und die praktische Weiterentwicklung bilden historische Bezugspunkte für die Entstehung des JCI-Modells.

### 1.2 Quellen und beteiligte Personen

- [Masterarbeit von Ernst Rother, heute Ernst Eimicke](https://monami.hs-mittweida.de/frontdoor/deliver/index/docId/6494/file/Masterarbeit_komplett.pdf)
- [Ernst Eimicke auf LinkedIn](https://www.linkedin.com/in/eeimicke/)
- [Junaco Organisationsentwicklung GmbH](https://junaco.de/)
- [Julian Ulbricht auf LinkedIn](https://www.linkedin.com/in/junaco/), beteiligt an der praktischen Weiterentwicklung des JCI-Modells
- [Jana Eimicke auf LinkedIn](https://www.linkedin.com/in/janaeimicke/)

### 1.3 Ziel und Umfang

JCI ist ein graphbasiertes Organisationsmodell zur Beschreibung von:

- Zielen und Zukunftszuständen,
- Rollen und Verantwortlichkeiten,
- Aufgaben und Ergebnissen,
- Regeln und Leitplanken,
- Umweltbeziehungen,
- historischer Entwicklung und Veränderung.

Die zentrale Frage lautet:

> Warum handeln wir so, mit welchen Zielen, in welchen Rollen, unter welchen Bedingungen und mit welchem historischen Kontext?

Die Modell-Logik ist graphorientiert. Einzelne Elemente sind nicht nur hierarchisch miteinander verbunden, sondern können über mehrere Pfade und Beziehungen zusammenhängen.

### 1.4 Vom Modell zum JCI Loop

Der JCI Loop entsteht, wenn die Elemente des Organisationsmodells fortlaufend miteinander abgeglichen werden. Eine Veränderung wird durch `SYNC` auf ihre Auswirkungen im Graphen geprüft. Abgelöste Zustände bleiben als `PiH` nachvollziehbar und können erneut als historischer Kontext für Werte, Ziele und Entscheidungen wirken. Dadurch schließt sich der Zusammenhang zwischen Vergangenheit, Gegenwart und Zukunft zu einem kontinuierlichen Loop.

Das folgende Kapitel beschreibt die Elemente, Graphobjekte und Beziehungen dieses JCI Loops.

---

## 2. Der JCI Loop

### 2.1 Zeitliche Einordnung

#### 2.1.1 Vergangenheit

- historische Schicht (`PiH` – **Point in Historie**)

#### 2.1.2 Gegenwart

- Werte und Zweck (`CiV` – **Core Influential Values**)
- Regeln und Normen (`RaN` – **Rules and Norms**)
- Rollen und Organisationsstruktur (`RoF` – **Roles and Functions**)
- Umweltbeziehungen (`ERoF` – **Environment of Roles or Functions**)
- Synchronisationsprozess (`SYNC` – **Synchronization**)

#### 2.1.3 Zukunft

- langfristiger Zukunftshorizont (`PiF2` – **Point in Future, Second Order**)
- strategischer Zukunftshorizont (`PiF1s` – **Point in Future, First Order – Strategic**)
- taktischer Zukunftshorizont (`PiF1t` – **Point in Future, First Order – Tactical**)
- operativer Zukunftshorizont (`PiF1o` – **Point in Future, First Order – Operational**)

| JCI-Element | Zeithorizont                             |
| ----------- | ---------------------------------------- |
| `PiF1o`     | weniger als 1 Jahr                       |
| `PiF1t`     | ab 1 Jahr bis einschließlich 5 Jahre     |
| `PiF1s`     | mehr als 5 bis einschließlich 10 Jahre   |
| `PiF2`      | mehr als 10 Jahre bis zu `n` Jahren      |

`n` bezeichnet einen offenen, nicht fest begrenzten langfristigen Zeithorizont.

### 2.2 Abgrenzung der Kernelemente von den Graphobjekten

Das JCI besteht aus genau zehn Kernelementen:

```text
PiH, CiV, RaN, RoF, ERoF, SYNC,
PiF2, PiF1s, PiF1t und PiF1o
```

Ein JCI-Kernelement bezeichnet einen grundlegenden fachlichen Bestandteil des Modells. Die Zugehörigkeit zu den zehn Kernelementen bedeutet nicht automatisch, dass das Kernelement selbst als Knoten gespeichert wird. Fachliche Bedeutung und technische Speicherung werden deshalb getrennt beschrieben.

| JCI-Kernelement | Speicherstatus      | Gespeicherte Bedeutung                                                    |
| --------------- | ------------------- | ------------------------------------------------------------------------- |
| `PiH`           | eigener Elementtyp  | unveränderlicher historischer Zustand                                     |
| `CiV`           | eigener Elementtyp  | konkrete Werte- und Zweckbeschreibung                                     |
| `RaN`           | eigener Elementtyp  | konkrete Regel oder Norm                                                  |
| `RoF`           | kein eigener Knoten | konzeptioneller Modellraum für Organisation, Teams, Mitglieder und Rollen |
| `ERoF`          | kein eigener Knoten | konzeptioneller und abgeleiteter Modellraum der relevanten Umwelt         |
| `SYNC`          | eigener Elementtyp  | gespeicherte Definition der Synchronisationslogik                         |
| `PiF2`          | eigener Elementtyp  | konkreter langfristiger Zukunftszustand                                   |
| `PiF1s`         | eigener Elementtyp  | konkreter strategischer Zukunftszustand                                   |
| `PiF1t`         | eigener Elementtyp  | konkreter taktischer Zukunftszustand                                      |
| `PiF1o`         | eigener Elementtyp  | konkreter operativer Zukunftszustand                                      |

Für die konkrete Anwendung und Speicherung im Graphen werden zusätzlich Graphobjekte benötigt. Sie machen die Kernelemente ausführbar, prüfbar und nachvollziehbar, sind aber keine weiteren JCI-Kernelemente.

| Bereich                   | Graphobjekt             | Bedeutung                                                        |
| ------------------------- | ----------------------- | ---------------------------------------------------------------- |
| Organisation              | `RoFOrg`                | eigenständig handlungsfähige Organisation                        |
| Organisationsbeziehungen  | `RoFOrgRelationship`    | typisierte Beziehung zwischen zwei eigenständigen Organisationen |
| Organisation              | `RoFTeam`               | organisatorische oder funktionale Gruppe                         |
| Organisation              | `RoFTeamMember`         | menschlicher oder technischer Akteur                             |
| Rollen                    | `RoFRole`               | Rolle, Funktion und Verantwortung                                |
| Rollen                    | `RoleAssignment`        | aktive Rolle eines Mitglieds in einem Team                       |
| Operative Umsetzung       | `Task`                  | Tätigkeit zur Realisierung eines `PiF1o`                         |
| Erfolg und Prüfung        | `SuccessCriterion`      | erwartetes Erfolgskriterium                                      |
| Erfolg und Prüfung        | `Result`                | durch einen Task erzeugtes Ergebnis                              |
| Erfolg und Prüfung        | `Verification`          | Prüfung eines Ergebnisses                                        |
| Erfolg und Prüfung        | `Evidence`              | eigenständiger prüfbarer Nachweis                                |
| Umwelt                    | `ERoFObject`            | konkretes Objekt der relevanten Umwelt                           |
| Veränderung               | `ChangeEvent`           | dokumentierter Auslöser einer Änderung                           |
| Veränderung               | `SyncEvent`             | dokumentierter Synchronisationslauf                              |
| Regelkonflikt             | `RaNConflict`           | nachvollziehbarer Konflikt zwischen anwendbaren Regeln           |
| Historische Korrektur     | `HistoricalCorrection`  | unveränderliche Berichtigung oder Ergänzung eines `PiH`          |

Die Kernelemente beschreiben die grundlegende fachliche Struktur des JCI. Die zusätzlichen Graphobjekte bilden konkrete Organisationen, Personen, Rollen, Tätigkeiten, Umweltobjekte, Ergebnisse, Prüfungen und Veränderungen innerhalb dieser Struktur ab.

Ein laufender technischer Synchronisationsprozess wird als `SyncRun` bezeichnet. `SyncRun` gehört zur Implementierung, ist keine `JCIEntity`, kein `GraphObject` und kein zusätzliches JCI-Kernelement. Erst der Abschluss oder kontrollierte Abbruch eines `SyncRun` erzeugt das unveränderliche fachliche `SyncEvent`.

#### 2.2.1 JCIEntity als gemeinsamer Oberbegriff

`JCIEntity` ist der abstrakte Oberbegriff für jede konkrete und eindeutig identifizierbare Instanz, die im JCI-Graphen als Knoten gespeichert wird. `JCIEntity` ist kein elftes Kernelement und kein zusätzlicher Knoten neben der konkreten Instanz.

Eine `JCIElementInstance` ist eine gespeicherte Ausprägung eines speicherbaren JCI-Kernelements. Ein `GraphObject` konkretisiert die praktische Anwendung der Kernelemente. `JCIElementInstance` und `GraphObject` sind abstrakte Typen zur Einordnung gespeicherter Knoten und keine zusätzlichen fachlichen Kernelemente.

```text
JCIEntity
├── JCIElementInstance
│   ├── PiH
│   ├── CiV
│   ├── RaN
│   ├── SYNC
│   ├── PiF2
│   ├── PiF1s
│   ├── PiF1t
│   └── PiF1o
│
└── GraphObject
    ├── RoFOrg
    ├── RoFOrgRelationship
    ├── RoFTeam
    ├── RoFTeamMember
    ├── RoFRole
    ├── RoleAssignment
    ├── Task
    ├── SuccessCriterion
    ├── Result
    ├── Verification
    ├── Evidence
    ├── ERoFObject
    ├── ChangeEvent
    ├── SyncEvent
    ├── RaNConflict
    └── HistoricalCorrection
```

`RoF` und `ERoF` fehlen in dieser Baumstruktur nicht: Beide bleiben JCI-Kernelemente, sind aber konzeptionelle Modellräume ohne eigenen Knoten. `RoF` wird durch seine Organisations- und Rollenobjekte konkretisiert. `ERoF` wird aus Umweltobjekten, Organisationsbeziehungen und ihrer Verwendung durch handelnde Rollen abgeleitet.

Beispiel für die Unterscheidung:

```text
Kernelement: CiV
└── gespeicherte JCIElementInstance:
    CiV „Wir handeln transparent und verbindlich.“

Kernelement: RoF
└── kein eigener RoF-Knoten
    ├── RoFOrg „Junaco“
    ├── RoFTeam „Entwicklung“
    └── RoleAssignment „Anna als Developer in Entwicklung“
```

Grundsätzlich ist jede bereits vorhandene `JCIEntity` historisierbar. Ausgenommen sind `PiH`, `ChangeEvent`, `SyncEvent` und `HistoricalCorrection`: Ein `PiH` ist nach seiner Erzeugung unveränderlich und wird nicht erneut historisiert. Ein `ChangeEvent` dokumentiert einen angenommenen Veränderungsauftrag; `SyncEvent` und `HistoricalCorrection` dokumentieren abgeschlossene Tatsachen. Ihre gespeicherten Inhalte und bestehenden Provenienzbeziehungen werden nicht nachträglich verändert. Die beim Abschluss eines technischen `SyncRun` entstehende Beziehung `TRIGGERS` wird ausschließlich append-only ergänzt. Beim erfolgreichen erstmaligen Anlegen darf außerdem genau einmal die Beziehung `CHANGED_BY` von der neu erzeugten Entität zum bereits bestehenden `ChangeEvent` hergestellt werden. Diese Ergänzungen ändern weder `revision` noch `updatedAt` des `ChangeEvent`. Das erstmalige Anlegen einer `JCIEntity` erzeugt noch kein `PiH`, weil kein vorheriger Zustand existiert.

#### 2.2.2 Gemeinsame Eigenschaften aller JCI-Entitäten

Jede gespeicherte `JCIEntity` besitzt eine unveränderliche Identität, einen konkreten Typ und nachvollziehbare Zeit- und Revisionsangaben. Eigenschaftsnamen werden in `camelCase`, Aufzählungswerte in Großbuchstaben und Zeitangaben nach ISO 8601 mit Zeitzone gespeichert.

| Eigenschaft   | Datentyp   | Pflicht | Bedeutung                                      |
| ------------- | ---------- | ------: | ---------------------------------------------- |
| `id`          | UUID       |      ja | global eindeutige, unveränderliche Identität   |
| `entityType`  | Enum       |      ja | konkreter Entitätstyp                          |
| `name`        | String     |      ja | kurze fachlich verständliche Bezeichnung       |
| `description` | String     |    nein | ausführliche fachliche Beschreibung            |
| `createdAt`   | DateTime   |      ja | Zeitpunkt der Erzeugung                        |
| `updatedAt`   | DateTime   |      ja | Zeitpunkt der letzten zulässigen Änderung      |
| `revision`    | Integer    |      ja | positive Revision des aktuellen Zustands       |
| `status`      | Enum       |      ja | typabhängiger fachlicher Zustand               |

Bei der Erzeugung gilt `revision = 1` und `updatedAt = createdAt`. Jede unabhängig angeforderte oder beobachtete fachliche Änderung einschließlich eines Statuswechsels erzeugt ein `ChangeEvent` und einen Synchronisationslauf. Deterministisch durch diesen Lauf abgeleitete Folgeänderungen bleiben Bestandteil desselben Veränderungsvorgangs und erzeugen kein rekursives `ChangeEvent`; sie werden durch `SyncEvent`, `AFFECTS`, Revision und Historisierung dokumentiert. Besteht bereits ein Ausgangszustand, wird dieser vor der Übernahme der Änderung als `PiH` festgehalten; anschließend wird `revision` des aktuellen Elements um genau eins erhöht. Rein technische Lesevorgänge verändern weder `updatedAt` noch `revision`.

`PiH`, `ChangeEvent`, `SyncEvent` und `HistoricalCorrection` bleiben dauerhaft bei `revision = 1` und `updatedAt = createdAt`. Ihre Eigenschaften werden nach der Erzeugung nicht verändert. Für `ChangeEvent` gelten ausschließlich die in Abschnitt 2.2.1 beschriebenen append-only Provenienzergänzungen.

Die Verantwortung für die Erzeugung wird als Beziehung zu einem konkreten `RoleAssignment` gespeichert und nicht zusätzlich als Akteurs-ID oder Freitext dupliziert:

```text
JCIEntity ── CREATED_BY ──► RoleAssignment
```

Für importierte Daten darf `CREATED_BY` vorübergehend fehlen. Bevor eine solche Entität den Status `ACTIVE` oder einen typabhängigen abgeschlossenen Status erhält, muss die verantwortliche Rollenaktivierung nachgetragen sein. Die einzige dauerhafte Ausnahme ist das in Abschnitt 12.7 definierte Root-`RoleAssignment` mit `bootstrapKey = "ROOT"`. Eine technische Systemidentität wird als reguläres `RoleAssignment` eines technischen `RoFTeamMember` modelliert.

#### 2.2.3 Statusmodell

Die folgenden Statuswerte bilden den gemeinsamen Vorrat. Jeder konkrete Entitätstyp verwendet nur die für ihn angegebenen Werte.

| Status         | Bedeutung                                                   |
| -------------- | ----------------------------------------------------------- |
| `DRAFT`        | fachlich noch nicht vollständig                             |
| `ACTIVE`       | gültig und im Modell verwendbar                             |
| `BLOCKED`      | Task wartet auf mindestens eine noch nicht erfüllte Abhängigkeit |
| `ACHIEVED`     | beschriebener Zukunftszustand wurde erreicht                |
| `COMPLETED`    | zeitlich begrenzte Tätigkeit oder Prüfung ist abgeschlossen |
| `REPLACED`     | durch einen anderen aktuellen Zustand ersetzt               |
| `REVOKED`      | fachlich aufgehoben                                         |
| `RECORDED`     | unveränderlich dokumentiert                                 |
| `OPEN`         | erkannter Regelkonflikt ist noch nicht aufgelöst            |
| `RESOLVED`     | Regelkonflikt wurde durch eine bestätigte Modelländerung aufgelöst |

| Entitätstypen                                             | Zulässige Statuswerte                                      |
| --------------------------------------------------------- | ---------------------------------------------------------- |
| `CiV`, `RaN`, `SYNC`, `RoFOrg`, `RoFOrgRelationship`,<br>`RoFTeam`, `RoFTeamMember`, `RoFRole`, `RoleAssignment`, `ERoFObject` | `DRAFT`, `ACTIVE`, `REPLACED`, `REVOKED` |
| `PiF2`, `PiF1s`, `PiF1t`, `PiF1o`                         | `DRAFT`, `ACTIVE`, `ACHIEVED`, `REPLACED`, `REVOKED`       |
| `Task`                                                    | `DRAFT`, `ACTIVE`, `BLOCKED`, `COMPLETED`, `REPLACED`, `REVOKED` |
| `Result`                                                  | `DRAFT`, `ACTIVE`, `COMPLETED`, `REPLACED`, `REVOKED`      |
| `SuccessCriterion`, `Evidence`                            | `DRAFT`, `ACTIVE`, `REPLACED`, `REVOKED`                   |
| `Verification`                                            | `COMPLETED`                                                |
| `RaNConflict`                                             | `OPEN`, `RESOLVED`                                        |
| `PiH`, `ChangeEvent`, `SyncEvent`, `HistoricalCorrection` | `RECORDED`                                                 |

Jeder zulässige Statuswechsel ist eine fachliche Änderung. Ein Status darf nur übernommen werden, wenn die für den Zielstatus geltenden Kardinalitäten und Modellbedingungen erfüllt sind. Ein Übergang aus `ACHIEVED`, `REPLACED`, `REVOKED`, `RECORDED`, `RESOLVED` oder `COMPLETED` zurück in einen veränderbaren Status ist nicht zulässig; eine notwendige Fortsetzung wird als neue Entität modelliert.

#### 2.2.4 Verbindliche Statusübergänge

Ein Statuswechsel ist nur zulässig, wenn er in der folgenden Tabelle aufgeführt ist. `SYNC` prüft zusätzlich alle typspezifischen Bedingungen, Beziehungen und anwendbaren `RaN`. Der Eintrag `Erzeugung` bezeichnet den erstmaligen Zustand einer neuen Entität; dabei entsteht noch kein `PiH`.

| Entitätstyp oder Gruppe | Erlaubter Übergang | `ChangeEvent.changeType` | Zentrale Bedingung |
| ----------------------- | ------------------ | ------------------------ | ------------------ |
| sechs Bootstrap-Entitäten nach Abschnitt 12.7 | Bootstrap → `ACTIVE` | – | vollständig leerer Graph; atomarer und vollständig validierter Minimalgraph |
| veränderliche Fachentität | Erzeugung → `DRAFT` | `CREATED` | Pflichtfelder für einen Entwurf sind vorhanden |
| veränderliche Fachentität | `DRAFT` → `ACTIVE` | `CHANGED` | alle Pflichtfelder, Akteure und aktiven Kardinalitäten sind erfüllt |
| veränderliche Fachentität | `DRAFT` → `REVOKED` | `REVOKED` | Entwurf wird verworfen |
| veränderliche Fachentität | `ACTIVE` → `REPLACED` | `REPLACED` | ein fachlich gültiger Nachfolger übernimmt die Funktion |
| veränderliche Fachentität | `ACTIVE` → `REVOKED` | `REVOKED` | Gültigkeit wird ohne Nachfolger beendet |
| `PiF2`, `PiF1s`, `PiF1t`, `PiF1o` | `ACTIVE` → `ACHIEVED` | `ACHIEVED` | typspezifische Ziel- und Beitragsbedingungen sind erfüllt |
| `Task` | `DRAFT` → `BLOCKED` | `CHANGED` | mindestens eine notwendige Abhängigkeit ist nicht erfüllt |
| `Task` | `ACTIVE` → `BLOCKED` | `CHANGED` | mindestens eine notwendige Abhängigkeit wird unerfüllt |
| `Task` | `BLOCKED` → `ACTIVE` | `CHANGED` | alle notwendigen Abhängigkeiten sind wieder erfüllt |
| `Task` | `BLOCKED` → `COMPLETED` | `COMPLETED` | alle Abhängigkeiten und Abschlussbedingungen werden im selben SyncRun erfüllt |
| `Task` | `ACTIVE` → `COMPLETED` | `COMPLETED` | Ausführungs-, Abhängigkeits- und Abschlussbedingungen sind erfüllt |
| `Task` | `BLOCKED` → `REPLACED` oder `REVOKED` | `REPLACED` oder `REVOKED` | blockierter Task wird ersetzt oder aufgehoben |
| `Result` | `ACTIVE` → `COMPLETED` | `COMPLETED` | Ergebnis ist vollständig erzeugt und unveränderlich zur Prüfung bereit |
| `RaNConflict` | Erzeugung → `OPEN` | – | Konflikt wird innerhalb des auslösenden Veränderungsvorgangs bestätigt |
| `RaNConflict` | `OPEN` → `RESOLVED` | `RESOLVED` | ausdrückliche Modelländerung und erfolgreicher nachfolgender SyncRun beseitigen den Konflikt |
| `Verification` | Erzeugung → `COMPLETED` | `CREATED` | Methode, Ergebnis, Zeitpunkt, Result und SuccessCriterion stehen fest |
| `PiH`, `ChangeEvent`, `SyncEvent`, `HistoricalCorrection` | Erzeugung → `RECORDED` | – | alle Pflichtangaben des unveränderlichen Dokuments stehen fest |

Für `CiV`, `RaN`, `SYNC`, `RoFOrg`, `RoFOrgRelationship`, `RoFTeam`, `RoFTeamMember`, `RoFRole`, `RoleAssignment`, `SuccessCriterion`, `Evidence` und `ERoFObject` gelten die Übergänge der veränderlichen Fachentitäten. `Result` darf zusätzlich abgeschlossen werden. Zukunftselemente dürfen zusätzlich erreicht und Tasks abhängigkeitsbedingt blockiert oder abgeschlossen werden.

Die Bootstrap-Zeile ist eine einmalige technische Vertrauenswurzel und kein `ChangeEvent`. Außer dieser ausdrücklich begrenzten Ausnahme sind direkte Abkürzungen nur dort erlaubt, wo die Tabelle eine Erzeugung in einen unveränderlichen Zielstatus vorsieht. Insbesondere dürfen aktive Fachentitäten nicht durch eine Änderung wieder zu Entwürfen werden. Eine inhaltliche Fortsetzung eines terminalen Zustands wird als neue Entität angelegt und über die dafür vorgesehene Nachfolgebeziehung verbunden.

Prozessartefakte erzeugen keine rekursive Ereigniskette: `ChangeEvent`, `SyncEvent`, `PiH`, `HistoricalCorrection` und ein durch SYNC erkannter offener `RaNConflict` werden innerhalb des bereits laufenden Veränderungsvorgangs erzeugt und lösen für ihre eigene Erzeugung kein weiteres `ChangeEvent` aus. Eine spätere zulässige Änderung eines `RaNConflict` von `OPEN` zu `RESOLVED` ist dagegen ein neuer fachlicher Veränderungsvorgang.

**Kurzes Beispiel:** Ein Task wird als `DRAFT` angelegt. Sind Team, ausführende Rollenaktivierung und Voraussetzungen gültig, wechselt er zu `ACTIVE`. Fällt eine Voraussetzung weg, setzt `SYNC` ihn auf `BLOCKED`. Sobald die Voraussetzung wieder erfüllt ist, darf er erneut `ACTIVE` werden. Nach bestätigter Ausführung wird er `COMPLETED`; dieser Zustand wird nicht wieder geöffnet.

#### 2.2.5 Typspezifische Pflichtfelder

Zusätzlich zu den gemeinsamen Eigenschaften gelten folgende typspezifische Felder. Beziehungen wie `CREATED_BY`, `REQUESTED_BY`, `CORRECTED_BY` und `USES_EVIDENCE` werden ausschließlich als Kanten gespeichert und erscheinen deshalb nicht als ID- oder Referenzfelder in dieser Tabelle.

| Entitätstyp                       | Zusätzliche Pflichtfelder                                                                                                                                                                                            | Optionale Felder                                                                                                           |
| --------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------- |
| `PiH`                             | `originalEntityId: UUID`, `originalEntityType: Enum`,<br>`originalRevision: Integer`, `recordedAt: DateTime`,<br>`validFrom: DateTime`, `validUntil: DateTime`,<br>`snapshotSchemaVersion: String`, `stateData: StateSnapshot`,<br>`relationshipData: RelationshipSnapshot[]`, `contentHash: String` | –                                                                                                                          |
| `CiV`                             | `purpose: String`, `values: String[]`, `scope: String`                                                                                                                                                               | –                                                                                                                          |
| `RaN`                             | `ruleType: Enum`, `effect: Enum`, `statement: String`,<br>`decisionKey: String`, `scopeType: Enum`,<br>`governedTypes: Enum[]`, `condition: RuleExpression`,<br>`priority: Integer`, `validFrom: DateTime`                                                 | `validUntil: DateTime`                                                                                                     |
| `RaNConflict`                     | `conflictKey: String`, `conflictType: Enum`,<br>`detectedAt: DateTime`, `reason: String`                                                                                                                             | `resolvedAt: DateTime`, `resolution: String`                                                                               |
| `SYNC`                            | `version: String`, `definition: SyncDefinition`, `validFrom: DateTime`                                                                                                                                               | `validUntil: DateTime`                                                                                                     |
| `PiF2`, `PiF1s`, `PiF1t`          | `targetState: String`, `horizonStart: Date`,<br>`contributionMode: Enum`                                                                                                                                              | `horizonEnd: Date`, `targetDate: Date`                                                                                     |
| `PiF1o`                            | `targetState: String`, `horizonStart: Date`                                                                                                                                                                           | `horizonEnd: Date`, `targetDate: Date`                                                                                     |
| `RoFOrg`                          | `legalName: String`, `orgType: Enum`                                                                                                                                                                                 | `externalReference: String`                                                                                                |
| `RoFOrgRelationship`              | `type: Enum`, `validFrom: DateTime`                                                                                                                                                                                  | `validUntil: DateTime`                                                                                                     |
| `RoFTeam`                         | `teamType: Enum`, `validFrom: DateTime`                                                                                                                                                                              | `validUntil: DateTime`                                                                                                     |
| `RoFTeamMember`                   | `memberType: Enum`, `displayName: String`                                                                                                                                                                            | `externalReference: String`                                                                                                |
| `RoFRole`                         | `roleName: String`, `responsibility: String`                                                                                                                                                                         | `roleType: String`                                                                                                         |
| `RoleAssignment`                  | `validFrom: DateTime`                                                                                                                                                                                                | `validUntil: DateTime`, `allocation: Decimal`,<br>`bootstrapKey: String`                                                    |
| `Task`                            | `taskKind: Enum`                                                                                                                                                                                                     | `taskType: String`, `plannedStart: DateTime`,<br>`plannedEnd: DateTime`, `actualStart: DateTime`,<br>`actualEnd: DateTime` |
| `SuccessCriterion`                | `criterion: String`, `measurementType: Enum`,<br>`requirementLevel: Enum`, `evaluationMode: Enum`,<br>`operator: Enum`, `targetValue: String`                                                                         | `unit: String`                                                                                                             |
| `Result`                          | `resultType: String`, `value: TypedValue`, `producedAt: DateTime`                                                                                                                                                    | –                                                                                                                          |
| `Verification`                    | `method: String`, `outcome: Enum`, `verifiedAt: DateTime`,<br>`evaluatedResultRevision: Integer`,<br>`checkedCriterionRevision: Integer`                                                                             | `reason: String`                                                                                                           |
| `Evidence`                        | `evidenceType: String`, `reference: String`, `capturedAt: DateTime`                                                                                                                                                  | `checksum: String`                                                                                                         |
| `ERoFObject`                      | `objectType: Enum`, `validFrom: DateTime`                                                                                                                                                                             | `validUntil: DateTime`, `externalReference: String`                                                                        |
| `ChangeEvent`                     | `changeType: Enum`, `occurredAt: DateTime`, `reason: String`,<br>`idempotencyKey: String`, `targetEntityId: UUID`,<br>`targetEntityType: Enum`, `requestedRevision: Integer oder null`                                                                                                   | –                                                                                                                          |
| `SyncEvent`                       | `runId: UUID`, `startedAt: DateTime`, `completedAt: DateTime`,<br>`outcome: Enum`, `affectedCount: Integer`, `changedCount: Integer`,<br>`historyCount: Integer`, `correctionCount: Integer`,<br>`conflictCount: Integer` | `errorCode: String`, `errorMessage: String`                                                                                |
| `HistoricalCorrection`            | `correctionType: Enum`, `reason: String`, `correctedAt: DateTime`,<br>`valueSchemaVersion: String`, `baseHistoryViewHash: String`,<br>`correctedFields: String[]`, `previousValue: TypedValueMap`,<br>`correctedValue: TypedValueMap`                                                    | –                                                                                                                          |

Verbindliche Aufzählungswerte sind:

```text
JCIEntity.entityType       = PiH | CiV | RaN | SYNC | PiF2 | PiF1s | PiF1t | PiF1o |
                             RoFOrg | RoFOrgRelationship | RoFTeam | RoFTeamMember |
                             RoFRole | RoleAssignment | Task | SuccessCriterion |
                             Result | Verification | Evidence | ERoFObject |
                             ChangeEvent | SyncEvent | RaNConflict | HistoricalCorrection
RaN.ruleType              = RULE | NORM | POLICY | CONSTRAINT | LAW
RaN.effect                = REQUIRE | PROHIBIT | PERMIT
RaN.scopeType             = GLOBAL | ORGANIZATION | TEAM | ENTITY
RaN.condition.combiner    = ALL | ANY
RaN.condition.clause.operator = EXISTS | NOT_EXISTS | EQUALS | NOT_EQUALS |
                                LESS_THAN | LESS_OR_EQUAL | GREATER_THAN |
                                GREATER_OR_EQUAL | IN | NOT_IN | CONTAINS | MATCHES
RaNConflict.conflictType  = PRIORITY_TIE | UNEVALUABLE
RoFOrgRelationship.type  = SUBSIDIARY | PARTNERSHIP
RoFOrg.orgType           = COMPANY | PUBLIC_ORGANIZATION | NONPROFIT |
                           ASSOCIATION | COOPERATIVE | NETWORK | OTHER
RoFTeam.teamType         = FUNCTIONAL | PROJECT | MANAGEMENT | SERVICE |
                           TEMPORARY | OTHER
RoFTeamMember.memberType = HUMAN | TECHNICAL
ERoFObject.objectType    = SYSTEM | APPLICATION | DATA | DOCUMENT | TOOL |
                           FACILITY | CONTRACT | SERVICE | OTHER
SuccessCriterion.measurementType = BOOLEAN | NUMERIC | TEXTUAL
SuccessCriterion.requirementLevel = REQUIRED | OPTIONAL
SuccessCriterion.evaluationMode   = ALL | ANY
SuccessCriterion.operator         = EQUALS | NOT_EQUALS | LESS_THAN | LESS_OR_EQUAL |
                                    GREATER_THAN | GREATER_OR_EQUAL | CONTAINS | MATCHES
PiF2.contributionMode             = ALL | ANY
PiF1s.contributionMode            = ALL | ANY
PiF1t.contributionMode            = ALL | ANY
Verification.outcome    = VALID | INVALID | INCONCLUSIVE
Task.taskKind           = ATOMIC | COMPOSITE
ChangeEvent.changeType  = CREATED | CHANGED | ACHIEVED | COMPLETED |
                          REPLACED | REVOKED | RESOLVED | HISTORICAL_CORRECTION
SyncEvent.outcome        = SUCCESS | CONFLICT | FAILED
HistoricalCorrection.correctionType = ADDITION | CORRECTION | CLARIFICATION
```

`allocation` liegt, sofern angegeben, zwischen `0` und `1`. `bootstrapKey` ist ausschließlich für genau ein Root-`RoleAssignment` zulässig und besitzt dort den unveränderlichen Wert `ROOT`. Die gebundenen Revisionen einer `Verification` sind positive Ganzzahlen. `ChangeEvent.id` entspricht der `requestId` des angenommenen Änderungsauftrags; `idempotencyKey` ist je fachlichem Veränderungsauftrag eindeutig. `SyncEvent.runId` ist je technischem Versuch eindeutig. Zählwerte eines `SyncEvent` sind nicht negativ, `completedAt` liegt nicht vor `startedAt`, und `validUntil` liegt nicht vor `validFrom`. Für neue Erfolgskriterien gelten standardmäßig `requirementLevel = REQUIRED` und `evaluationMode = ALL`. Für übergeordnete Zukunftselemente gilt standardmäßig `contributionMode = ALL`. Für `RaN.priority` gilt: Eine größere Ganzzahl bedeutet höhere Priorität. Der `ruleType` erzeugt keinen automatischen Vorrang.

Für `SuccessCriterion.operator` gelten abhängig vom Messungstyp folgende Kombinationen:

| `measurementType` | Zulässige Operatoren | Regel für `targetValue` |
| ----------------- | -------------------- | ---------------------- |
| `BOOLEAN` | `EQUALS`, `NOT_EQUALS` | exakt `true` oder `false` |
| `NUMERIC` | `EQUALS`, `NOT_EQUALS`, `LESS_THAN`, `LESS_OR_EQUAL`, `GREATER_THAN`, `GREATER_OR_EQUAL` | als Dezimalzahl interpretierbar |
| `TEXTUAL` | `EQUALS`, `NOT_EQUALS`, `CONTAINS`, `MATCHES` | nicht leer; bei `MATCHES` gültiger regulärer Ausdruck |

**Kurzes Beispiel:** „Antwortzeit höchstens 24 Stunden“ wird als `measurementType = NUMERIC`, `operator = LESS_OR_EQUAL`, `targetValue = "24"` und `unit = "hours"` gespeichert. Dadurch kann jede Implementierung dieselbe Bedingung auswerten.

Wird für `RoFOrg.orgType`, `RoFTeam.teamType` oder `ERoFObject.objectType` der Wert `OTHER` verwendet, muss `description` den fachlichen Typ eindeutig erläutern. `OTHER` darf nicht eingesetzt werden, wenn bereits ein passender katalogisierter Wert existiert.

#### 2.2.6 Akteure und Nachweise

Akteure werden ausschließlich über aktive Rollen im konkreten Teamkontext zugeordnet:

| Quelle                  | Beziehung       | Ziel             |  Ziele je Quelle |  Quellen je Ziel |
| ----------------------- | --------------- | ---------------- | ---------------: | ---------------: |
| `JCIEntity`             | `CREATED_BY`    | `RoleAssignment` |           `0..1` |           `0..n` |
| `ChangeEvent`           | `REQUESTED_BY`  | `RoleAssignment` |              `1` |           `0..n` |
| `HistoricalCorrection`  | `CORRECTED_BY`  | `RoleAssignment` |              `1` |           `0..n` |
| `RaNConflict`           | `RESOLVED_BY`   | `RoleAssignment` |           `0..1` |           `0..n` |

`CREATED_BY = 0..1` erlaubt ausschließlich unvollständige Importentwürfe und das eine Root-`RoleAssignment` des initialen Bootstraps. Für alle anderen fachlich aktiven oder abgeschlossenen Entitäten gilt durch zusätzliche Invariante genau ein Erzeuger. `REQUESTED_BY` bezeichnet die Rollenaktivierung, die eine Änderung veranlasst hat. `CORRECTED_BY` bezeichnet die Rollenaktivierung, die für eine historische Korrektur verantwortlich ist.

Nachweise werden ausschließlich als eigenständige `Evidence`-Knoten gespeichert:

| Quelle                  | Beziehung       | Ziel       |  Ziele je Quelle |  Quellen je Ziel |
| ----------------------- | --------------- | ---------- | ---------------: | ---------------: |
| `Verification`          | `USES_EVIDENCE` | `Evidence` |           `0..n` |           `0..n` |
| `ChangeEvent`           | `USES_EVIDENCE` | `Evidence` |           `0..n` |           `0..n` |
| `HistoricalCorrection`  | `USES_EVIDENCE` | `Evidence` |           `0..n` |           `0..n` |
| `RaNConflict`           | `USES_EVIDENCE` | `Evidence` |           `0..n` |           `0..n` |

Eine `HistoricalCorrection` darf ohne Evidence entstehen, wenn kein eigenständiger Nachweis verfügbar ist; die Begründung bleibt dennoch verpflichtend. Zeichenketten, Dateipfade oder URLs zu Nachweisen werden im `reference`-Feld des zugehörigen `Evidence`-Knotens gespeichert und nicht in der belegten Entität dupliziert.

#### 2.2.7 Strukturierte Datenformate

Alle komplexen Werte verwenden ein technologieunabhängiges, JSON-kompatibles Format. Objekte besitzen keine bedeutungstragende Feldreihenfolge; Listen behalten ihre Reihenfolge nur, wenn dies fachlich erforderlich ist.

Ein `TypedValue` besteht aus:

```text
valueType = NULL | BOOLEAN | INTEGER | DECIMAL | STRING |
            DATE | DATETIME | OBJECT | ARRAY
value     = zum valueType passender JSON-kompatibler Wert
```

Dezimalzahlen werden ohne binäre Rundung als kanonische Dezimalzeichenkette gespeichert. `DATE` und `DATETIME` verwenden ISO 8601; `DATETIME` enthält eine Zeitzone.

Ein `StateSnapshot` enthält:

```text
entityType
revision
properties = Map<String, TypedValue>
```

`properties` enthält alle zum abgelösten Zustand gehörenden gemeinsamen und typspezifischen Eigenschaften mit Ausnahme der separat am `PiH` gespeicherten Identitäts- und Zeitfelder. Flüchtige technische Laufzeitdaten sind ausgeschlossen.

Ein `RelationshipSnapshot` enthält:

```text
relationshipType
direction = OUTGOING | INCOMING
otherEntityId
otherEntityType
properties = Map<String, TypedValue>
```

Für jede zum Gültigkeitsende bestehende fachliche Kante wird genau ein Snapshot aus Sicht der historisierten Entität gespeichert. Die Liste wird für die Hashbildung nach `relationshipType`, `direction` und `otherEntityId` sortiert. `contentHash` ist der hexadezimale SHA-256-Wert der kanonisch serialisierten Kombination aus `StateSnapshot` und sortierten `RelationshipSnapshots`.

Ein `TypedValueMap` ordnet jedem Eintrag in `correctedFields` genau einen typisierten alten und korrigierten Wert zu. `correctedFields` enthält eindeutige, lexikografisch sortierte kanonische JSON-Pointer. Eine historische Beziehung wird darin über einen stabilen Schlüssel aus `direction`, `relationshipType` und `otherEntityId` und niemals über einen veränderlichen Arrayindex adressiert. Bei `ADDITION` ist der alte Wert `NULL`. Eine Korrektur darf nur die aufgeführten Pfade verändern; andere Snapshot-Inhalte bleiben wirksam unverändert.

Eine `HistoryView` ist die deterministisch berechnete wirksame historische Sicht aus dem unveränderten `PiH` und allen für dieses `PiH` nicht abgelösten `HistoricalCorrections`. `baseHistoryViewHash` ist der hexadezimale SHA-256-Wert ihrer kanonischen Serialisierung unmittelbar vor der geprüften neuen Korrektur. Dadurch kann `SYNC` feststellen, ob sich die historische Basissicht zwischen Lesen und Commit verändert hat.

**Kurzes Beispiel:** Wird Annas Teambeziehung historisiert, enthält `relationshipData` eine ausgehende oder eingehende Kante mit Typ `HAS_MEMBER`, der Team-ID sowie `validFrom` und `validUntil`. Eine spätere Korrektur benennt genau diesen Beziehungspfad und ersetzt nicht den gesamten Snapshot.

### 2.3 Grundstruktur

Die vereinfachte Grundstruktur des JCI-Modells ist:

```text
                         RaN
                          │ regelt und begrenzt
                          ▼
PiH → CiV → PiF2 → PiF1s → PiF1t → PiF1o → COMPOSITE Task → ATOMIC Task → Result ← Verification
                                                │
                                                                  ├── wird durch RoleAssignments ausgeführt
                                                                  └── interagiert mit ERoFObjects (ERoF)

RoF-Modellraum:  RoFOrg → RoFTeam → RoFTeamMember → RoleAssignment
ERoF-Modellraum: RoleAssignment → ERoFObject

JCIEntity → ChangeEvent → technischer SyncRun → SyncEvent
     │                                                │
     │                                                ├── EXECUTES → SYNC-Definition
     │                                                └── AFFECTS → betroffene JCIEntities
     └── bisheriger Zustand → PiH
```

**Kurzes Beispiel:** Eine Organisation möchte ihren Kundenservice verbessern. Aus ihren Werten (`CiV`) entsteht ein langfristiges Zukunftsbild (`PiF2`), das über strategische (`PiF1s`) und taktische Zukunftszustände (`PiF1t`) zu einem konkreten operativen Zielzustand (`PiF1o`) führt. Ein Teammitglied ist für diesen Zustand accountable. Die daraus abgeleiteten Tasks werden von verantwortlichen Teams getragen und durch konkrete Rollenaktivierungen ausgeführt. Dabei interagieren die ausführenden Rollen (`RoF`) mit Systemen und Informationen aus der Umwelt (`ERoF`). Regeln und Normen (`RaN`) geben den zulässigen Rahmen vor. Die erzeugten Ergebnisse werden anhand festgelegter Erfolgskriterien geprüft. Bei einer relevanten Änderung verfolgt `SYNC` die Auswirkungen. Der durch die Änderung abgelöste Zustand wird als eigener `PiH` festgehalten; danach gilt der neue Zustand als aktuell. Bei weiteren Änderungen entstehen weitere `PiH`, sodass die früheren Zustände in ihrer zeitlichen Reihenfolge nachvollziehbar bleiben.

Die Darstellung beschreibt eine Orientierung und keinen einzigen linearen Ablauf. `RaN`, `RoF`, `ERoF` und `SYNC` sind deshalb nicht als aufeinanderfolgende Stationen in die Zukunftskette eingefügt. `RoF` und `ERoF` bezeichnen Modellräume; `SYNC` bezeichnet die gespeicherte Prozessdefinition. Die tatsächlichen Beziehungen zwischen den gespeicherten `JCIEntities` bilden einen Graphen und können Verzweigungen sowie Rückbezüge enthalten.

### 2.4 Beziehungen zwischen JCI-Entitäten

Die folgenden Tabellen zeigen die gespeicherten Beziehungen entlang der JCI-Kette und die daraus eindeutig abgeleiteten ERoF-Zuordnungen. Abgeleitete Beziehungen sind ausdrücklich gekennzeichnet und werden nicht als zusätzliche Kanten gespeichert.

#### 2.4.1 Zweck, Werte und Zukunft

Lesebeispiel für `PiF1s ── CONTRIBUTES_TO ──► PiF2`: **Ziele je Quelle `1..n`** bedeutet, dass ein `PiF1s` zu mindestens einem oder mehreren `PiF2` beitragen muss. **Quellen je Ziel `0..n`** bedeutet, dass zu einem `PiF2` vorübergehend noch kein, ein oder mehrere `PiF1s` beitragen können.

| Quelle    | Beziehung                 | Ziel      | Ziele je<br>Quelle | Quellen je<br>Ziel |
| --------- | ------------------------- | --------- | -----------------: | -----------------: |
| `PiH`     | `PROVIDES_CONTEXT_TO`     | `CiV`     |             `0..n` |             `0..n` |
| `CiV`     | `INSCRIBES_PURPOSE_IN`    | `PiF2`    |             `0..n` |             `1..n` |
| `PiF1s`   | `CONTRIBUTES_TO`          | `PiF2`    |             `1..n` |             `0..n` |
| `PiF1t`   | `CONTRIBUTES_TO`          | `PiF1s`   |             `1..n` |             `0..n` |
| `PiF1o`   | `CONTRIBUTES_TO`          | `PiF1t`   |             `1..n` |             `0..n` |

#### 2.4.2 Operative Umsetzung, Rollen und Umwelt

Lesebeispiel für `RoleAssignment ── USES ──► ERoFObject`: **Ziele je Quelle `0..n`** bedeutet, dass ein `RoleAssignment` vorübergehend noch kein, ein oder mehrere `ERoFObjects` verwenden kann. **Quellen je Ziel `1..n`** bedeutet, dass jedes aktive `ERoFObject` von mindestens einem oder mehreren `RoleAssignments` und damit personengebunden verwendet werden muss.

| Quelle             | Beziehung                 | Ziel                 | Ziele je<br>Quelle | Quellen je<br>Ziel |
| ------------------ | ------------------------- | -------------------- | -----------------: | -----------------: |
| `PiF1o`            | `HAS_SUCCESS_CRITERIA`    | `SuccessCriterion`   |             `1..n` |                `1` |
| `PiF1o`            | `ACCOUNTABLE_MEMBER`      | `RoFTeamMember`      |                `1` |             `0..n` |
| `PiF1o`            | `DECOMPOSES_INTO`         | `Task`               |             `1..n` |                `1` |
| `Task`             | `DECOMPOSES_INTO`         | `Task`               |             `0..n` |             `0..1` |
| `Task`             | `DEPENDS_ON`              | `Task`               |             `0..n` |             `0..n` |
| `Task`             | `EXECUTED_BY`             | `RoleAssignment`     |             `0..n` |             `0..n` |
| `Task`             | `RESPONSIBLE_TEAM`        | `RoFTeam`            |                `1` |             `0..n` |
| `Task`             | `USES`                    | `ERoFObject`         |             `0..n` |             `0..n` |
| `RoleAssignment`   | `USES`                    | `ERoFObject`         |             `0..n` |             `1..n` |
| `ERoFObject`       | `OWNED_BY`                | `RoFOrg`             |             `0..n` |             `0..n` |

`HAS_MEMBER` und `HAS_ROLE` besitzen auf der Beziehung ein verpflichtendes `validFrom: DateTime` und ein optionales `validUntil: DateTime`. Ein `RoleAssignment` darf nur innerhalb der zeitlichen Schnittmenge seiner Teammitgliedschaft und seines Rollenbesitzes gültig sein. `validUntil` liegt niemals vor `validFrom`.

`OWNED_BY` beschreibt fachliches Eigentum oder gemeinsame Trägerschaft. Es ersetzt nicht die personengebundene Verwendung: Jedes aktive `ERoFObject` muss weiterhin von mindestens einem `RoleAssignment` verwendet werden.

#### 2.4.3 Beziehungen zwischen eigenständigen Organisationen

Mutterunternehmen, Tochterunternehmen und Partnerunternehmen werden jeweils als eigenständige `RoFOrg` gespeichert. Ihre unterschiedliche Bedeutung entsteht durch eine `RoFOrgRelationship`, nicht durch unterschiedliche Organisationstypen oder eine zusätzliche Speicherung als `ERoFObject`.

| Quelle                   | Beziehung         | Ziel              | Ziele je<br>Quelle | Quellen je<br>Ziel |
| ------------------------ | ----------------- | ----------------- | -----------------: | -----------------: |
| `RoFOrgRelationship`     | `SOURCE_ORG`      | `RoFOrg`          |                `1` |             `0..n` |
| `RoFOrgRelationship`     | `TARGET_ORG`      | `RoFOrg`          |                `1` |             `0..n` |
| `RoFOrgRelationship`     | `REPRESENTED_BY`  | `RoleAssignment`  |             `2..n` |             `0..n` |

`type = SUBSIDIARY` beschreibt eine gerichtete Mutter-Tochter-Beziehung von `SOURCE_ORG` zu `TARGET_ORG`. Eine Tochterorganisation kann selbst Quelle weiterer `SUBSIDIARY`-Beziehungen sein. `type = PARTNERSHIP` beschreibt eine fachlich wechselseitige Beziehung zwischen unabhängigen Organisationen; `SOURCE_ORG` und `TARGET_ORG` dienen dabei nur der eindeutigen Speicherung. `2..n` bedeutet, dass eine aktive Organisationsbeziehung insgesamt mindestens zwei vertretende `RoleAssignments` benötigt: mindestens eines aus jeder beteiligten Organisation.

#### 2.4.4 Abgeleitete ERoF-Zuordnungen

Lesebeispiel für die Ableitung `RoFOrg ── über Teams, Mitglieder und RoleAssignments ──► ERoFObject`: **Ziele je Quelle `0..n`** bedeutet, dass für eine `RoFOrg` kein, ein oder mehrere `ERoFObjects` aus den personengebundenen Umweltbeziehungen abgeleitet werden können. **Quellen je Ziel `1..n`** bedeutet, dass jedes aktive `ERoFObject` dadurch mindestens einer oder mehreren `RoFOrgs` zugeordnet werden kann, ohne eine direkte Beziehung zur Organisation zu speichern.

| Quelle            | Ableitung                                                 | Ziel           | Ziele je<br>Quelle | Quellen je<br>Ziel |
| ----------------- | --------------------------------------------------------- | -------------- | -----------------: | -----------------: |
| `RoFTeamMember`   | über seine `RoleAssignments`                              | `ERoFObject`   |             `0..n` |             `1..n` |
| `RoFTeam`         | über Mitglieder;<br>dann über `RoleAssignments`           | `ERoFObject`   |             `0..n` |             `1..n` |
| `RoFOrg`          | über Teams und Mitglieder;<br>dann über `RoleAssignments` | `ERoFObject`   |             `0..n` |             `1..n` |

#### 2.4.5 Ergebnisse und Prüfung

Lesebeispiel für `Verification ── EVALUATES ──► Result`: **Ziele je Quelle `1`** bedeutet, dass jede `Verification` genau ein `Result` bewertet. **Quellen je Ziel `0..n`** bedeutet, dass ein `Result` noch durch keine, durch eine oder durch mehrere `Verifications` bewertet werden kann.

Die `Verification` speichert mit `evaluatedResultRevision` und `checkedCriterionRevision` unveränderlich, welche Revisionen der beiden Ziele tatsächlich geprüft wurden. Diese Angaben sind Eigenschaften der Prüfung und keine zusätzlichen Beziehungen.

| Quelle           | Beziehung          | Ziel                 | Ziele je<br>Quelle | Quellen je<br>Ziel |
| ---------------- | ------------------ | -------------------- | -----------------: | -----------------: |
| `Task`           | `PRODUCES`         | `Result`             |             `0..n` |                `1` |
| `Verification`   | `EVALUATES`        | `Result`             |                `1` |             `0..n` |
| `Verification`   | `CHECKS`           | `SuccessCriterion`   |                `1` |             `0..n` |
| `Verification`   | `USES_EVIDENCE`    | `Evidence`           |             `0..n` |             `0..n` |
| `Verification`   | `SUPERSEDES`       | `Verification`       |             `0..1` |             `0..1` |

#### 2.4.6 Regeln, Priorität und Konflikte

Lesebeispiel für `RaNConflict ── CONFLICTING_RULE ──► RaN`: **Ziele je Quelle `1..n`** bedeutet, dass jeder Regelkonflikt mindestens eine betroffene Regel benennt. Ein Prioritätsgleichstand erfordert mindestens zwei Regeln; bei nicht auswertbarer Anwendbarkeit kann bereits eine Regel genügen. **Quellen je Ziel `0..n`** bedeutet, dass ein `RaN` an keinem, einem oder mehreren Konflikten beteiligt sein kann.

| Quelle          | Beziehung           | Ziel                  | Ziele je<br>Quelle | Quellen je<br>Ziel |
| --------------- | ------------------- | --------------------- | -----------------: | -----------------: |
| `RaN`           | `GOVERNS`           | zulässige `JCIEntity` |             `0..n` |             `0..n` |
| `RaN`           | `APPLIES_IN`        | `RoFOrg` oder `RoFTeam` |           `0..1` |             `0..n` |
| `RaNConflict`   | `CONFLICTING_RULE`  | `RaN`                 |             `1..n` |             `0..n` |
| `RaNConflict`   | `AFFECTS`           | `JCIEntity`           |             `1..n` |             `0..n` |
| `RaNConflict`   | `DETECTED_BY`       | `SyncEvent`           |                `1` |             `0..n` |
| `RaNConflict`   | `RESOLVED_BY`       | `RoleAssignment`      |             `0..1` |             `0..n` |
| `RaNConflict`   | `RESOLVED_THROUGH`  | `ChangeEvent`         |             `0..1` |             `0..n` |
| `RaNConflict`   | `USES_EVIDENCE`     | `Evidence`            |             `0..n` |             `0..n` |

#### 2.4.7 Veränderung

Lesebeispiel für `ChangeEvent ── TRIGGERS ──► SyncEvent`: **Ziele je Quelle `0..n`** bedeutet, dass ein angenommener Veränderungsauftrag bis zum Abschluss seines ersten technischen Versuchs noch kein `SyncEvent` und nach abgeschlossenen Wiederholungsversuchen mehrere `SyncEvents` besitzen kann. **Quellen je Ziel `1`** bedeutet, dass jedes abschließend erzeugte `SyncEvent` genau auf ein auslösendes `ChangeEvent` zurückgeht.

`SYNC`, `SyncRun` und `SyncEvent` haben unterschiedliche Aufgaben: `SYNC` ist die gespeicherte Definition der Synchronisationslogik. `SyncRun` ist der veränderbare technische Laufzustand während der Ausführung. Ein `SyncEvent` wird erst nach Abschluss oder kontrolliertem Abbruch erzeugt, dokumentiert das unveränderliche Ergebnis dieses Versuchs und verweist über `EXECUTES` auf die verwendete Definition. `SyncRun` wird nicht im fachlichen JCI-Graphen gespeichert.

| Quelle                      | Beziehung       | Ziel             | Ziele je<br>Quelle | Quellen je<br>Ziel |
| --------------------------- | --------------- | ---------------- | -----------------: | -----------------: |
| historisierbare `JCIEntity` | `CHANGED_BY`    | `ChangeEvent`    |             `0..n` |             `0..1` |
| `ChangeEvent`               | `TRIGGERS`      | `SyncEvent`      |             `0..n` |                `1` |
| `ChangeEvent`               | `REQUESTED_BY`  | `RoleAssignment` |                `1` |             `0..n` |
| `ChangeEvent`               | `USES_EVIDENCE` | `Evidence`       |             `0..n` |             `0..n` |
| `ChangeEvent`               | `TARGETS_HISTORY` | `PiH`           |             `0..1` |             `0..n` |
| `SyncEvent`                 | `EXECUTES`      | `SYNC`           |                `1` |             `0..n` |
| `SyncEvent`                 | `AFFECTS`       | `JCIEntity`      |             `0..n` |             `0..n` |
| ersetzbare `JCIEntity`      | `REPLACED_BY`   | gleicher konkreter Entitätstyp |       `0..1` |             `0..n` |

Lesebeispiel für `SyncEvent ── EXECUTES ──► SYNC`: **Ziele je Quelle `1`** bedeutet, dass jedes `SyncEvent` genau eine verwendete SYNC-Definition dokumentiert. **Quellen je Ziel `0..n`** bedeutet, dass eine SYNC-Definition noch in keinem, einem oder mehreren abgeschlossenen Synchronisationsversuchen verwendet worden sein kann.

`REPLACED_BY` verbindet eine ersetzte Entität mit ihrem fachlichen Nachfolger. Quelle und Ziel besitzen denselben konkreten `entityType`. Eine Entität mit `status = REPLACED` besitzt genau einen Nachfolger; in allen anderen Status besitzt sie keine ausgehende `REPLACED_BY`-Beziehung. Ein Nachfolger darf mehrere bisherige Entitäten zusammenführen. Die Beziehung darf keine Selbstbezüge oder Zyklen bilden.

Für `CHANGED_BY`, `TARGETS_HISTORY` und `AFFECTS` gelten bedingte Invarianten: Eine normale Änderung besitzt genau eine `CHANGED_BY`-Quelle. Bei `CREATED` fehlt sie bis zum erfolgreichen Anlegen; danach verweist die neue Entität genau einmal auf das `ChangeEvent`. Ein fehlgeschlagener oder konfliktbehafteter Erzeugungsversuch besitzt keine `CHANGED_BY`-Quelle. Ein `ChangeEvent` mit `changeType = HISTORICAL_CORRECTION` besitzt keine `CHANGED_BY`-Quelle, aber genau ein `TARGETS_HISTORY` zu dem unverändert bleibenden `PiH`; alle anderen Änderungstypen besitzen diese Beziehung nicht. Ein `SyncEvent` mit `outcome = SUCCESS` oder `CONFLICT` betrifft mindestens eine bestehende oder neu übernommene Entität. Nur ein `FAILED`-Versuch, der vor erfolgreicher Zielauflösung endet, darf kein `AFFECTS`-Ziel besitzen.

Jedes angenommene `ChangeEvent` muss mindestens einen technischen `SyncRun` einplanen. Solange noch kein Versuch beendet wurde, ist `TRIGGERS = 0` der korrekte gespeicherte Zwischenstand. Jeder beendete oder kontrolliert abgebrochene Versuch ergänzt genau eine `TRIGGERS`-Beziehung append-only; sie wird niemals entfernt oder auf ein anderes `SyncEvent` umgebogen.

**Kurzes Beispiel:** Wird die Regel „Freigabe ab 5.000 Euro“ durch „Freigabe ab 3.000 Euro“ ersetzt, erhält die alte `RaN` den Status `REPLACED` und verweist über `REPLACED_BY` auf die neue `RaN`. Beide bleiben unterschiedliche Entitäten; der frühere Zustand der alten Regel wird zusätzlich als `PiH` festgehalten.

#### 2.4.8 Historisierung

Lesebeispiel für `JCIEntity ── HAS_HISTORICAL_STATE ──► PiH`: **Ziele je Quelle `0..n`** bedeutet, dass eine historisierbare `JCIEntity` noch keinen, einen oder mehrere frühere Zustände als `PiH` besitzen kann. **Quellen je Ziel `1`** bedeutet, dass jedes `PiH` den abgelösten Zustand genau einer `JCIEntity` festhält.

| Quelle                      | Beziehung                  | Ziel    | Ziele je<br>Quelle | Quellen je<br>Ziel |
| --------------------------- | -------------------------- | ------- | -----------------: | -----------------: |
| historisierbare `JCIEntity` | `HAS_HISTORICAL_STATE`     | `PiH`   |             `0..n` |                `1` |
| `SyncEvent`                 | `CREATES_HISTORY`          | `PiH`   |             `0..n` |                `1` |

Ein bestehendes `PiH` wird niemals überschrieben. Wird später eine fehlende, falsche oder mehrdeutige historische Angabe festgestellt, dokumentiert ein eigenständiges `HistoricalCorrection`-Objekt die Berichtigung. Das ursprüngliche `PiH` bleibt dabei vollständig erhalten.

| Quelle                  | Beziehung             | Ziel                   | Ziele je<br>Quelle | Quellen je<br>Ziel |
| ----------------------- | --------------------- | ---------------------- | -----------------: | -----------------: |
| `HistoricalCorrection`  | `CORRECTS`            | `PiH`                  |                `1` |             `0..n` |
| `HistoricalCorrection`  | `CAUSED_BY`           | `ChangeEvent`          |                `1` |             `0..n` |
| `SyncEvent`             | `CREATES_CORRECTION`  | `HistoricalCorrection` |             `0..n` |                `1` |
| `HistoricalCorrection`  | `SUPERSEDES`          | `HistoricalCorrection` |             `0..1` |             `0..1` |

`CORRECTS` bezeichnet das berichtigte `PiH`; `CAUSED_BY` hält den Anlass fest. `CREATES_CORRECTION` ordnet die Korrektur genau dem Synchronisationslauf zu, der sie geprüft und erzeugt hat. `SUPERSEDES` wird nur verwendet, wenn eine spätere Korrektur eine frühere Korrektur desselben `PiH` ablöst. Korrekturketten müssen zeitlich vorwärts gerichtet und zyklusfrei sein.

##### 2.4.8.1 Ablauf von Veränderung und Historisierung

Ein angenommener Veränderungsauftrag wird vor seinem ersten technischen Versuch als unveränderliches `ChangeEvent` dokumentiert. Seine `id` entspricht der `requestId`; Ziel-ID, Zieltyp, erwartete Revision und Idempotenzkennung bleiben dadurch auch dann nachvollziehbar, wenn noch keine Zielentität existiert oder der Versuch scheitert. Jedes `ChangeEvent` plant mindestens einen technischen `SyncRun`, der genau eine SYNC-Definition ausführt. Diese ermittelt die betroffenen `JCIEntity`-Instanzen und prüft, welcher bestehende Zustand durch die Änderung abgelöst wird. Nach Abschluss oder kontrolliertem Abbruch wird das unveränderliche `SyncEvent` mit der eindeutigen `runId` und dem Ergebnis des Versuchs erzeugt. Erst dabei wird die gespeicherte Beziehung `ChangeEvent ── TRIGGERS ──► SyncEvent` append-only ergänzt. Der technische `SyncRun` wird nicht als JCI-Knoten gespeichert.

Bevor der neue Zustand übernommen wird, hält der Synchronisationslauf den bisherigen Zustand des betroffenen Elements einschließlich seiner zu diesem Zeitpunkt gültigen Beziehungen als eigenes `PiH` fest. Anschließend gilt der geänderte Zustand als aktueller Zustand. Ein zusätzlicher `HistoricalSnapshot` ist nicht erforderlich.

```text
aktueller Zustand → ChangeEvent → technischer SyncRun → neuer aktueller Zustand
       │                                      │
       └── bisheriger Zustand ──► PiH         └── Abschluss/Abbruch ──► SyncEvent
                                                                         └── EXECUTES ──► SYNC
```

Beim erstmaligen Anlegen einer `JCIEntity` existiert noch kein vorheriger Zustand. Deshalb erzeugt `changeType = CREATED` noch kein `PiH` dieser Entität. Bei der Annahme muss die angeforderte Ziel-ID noch frei und `requestedRevision = null` sein. Erst bei `SUCCESS` wird die neue Entität atomar mit `revision = 1`, `CREATED_BY` und ihrer `CHANGED_BY`-Beziehung angelegt. Bei `CONFLICT` oder `FAILED` bleiben Zielknoten, `CHANGED_BY` und Historie aus; das `ChangeEvent` und das abschließende `SyncEvent` dokumentieren den Versuch trotzdem.

Wird eine Abweichung in einem bestehenden `PiH` festgestellt, verarbeitet `SYNC` sie als eigenen Korrekturvorgang. Das `ChangeEvent` besitzt dafür `changeType = HISTORICAL_CORRECTION`, genau ein `TARGETS_HISTORY` und keine `CHANGED_BY`-Quelle. Dabei wird weder das `PiH` verändert noch ein `PiH` des `PiH` erzeugt. Bei erfolgreicher Prüfung entsteht ein unveränderliches `HistoricalCorrection`-Objekt, dessen `CORRECTS` dasselbe `PiH` bezeichnet. Ergibt sich daraus zusätzlich eine Änderung am aktuellen Modell, wird diese als getrennter Veränderungsvorgang verarbeitet.

#### 2.4.9 Verbindliche Rückverfolgbarkeit

Die Tabellen in den Abschnitten 2.2.6 und 2.4 bilden gemeinsam den vollständigen fachlichen Beziehungskatalog. Andere Beziehungsnamen sind erst nach einer ausdrücklichen Modelländerung zulässig. Inverse Formulierungen dienen nur zum Lesen und werden nicht als zweite Kante gespeichert.

Für jede aktive operative Arbeit müssen vier Pfade nachvollziehbar sein:

| Pfad | Ausgangspunkt | Verbindliches Ziel | Zweck |
| ---- | ------------- | ------------------ | ----- |
| WHY | `Task` | mindestens ein `CiV` | begründet, warum die Arbeit erfolgt |
| WHO | `Task` | `RoleAssignment`, `RoFTeamMember`, `RoFTeam` und `RoFOrg` | zeigt Ausführung und organisatorische Verantwortung |
| WHERE | `Task` oder ausführendes `RoleAssignment` | verwendete `ERoFObject` und relevante `RoFOrgRelationship` | beschreibt die berührte Umwelt |
| UNDER WHICH RULES | betroffene `JCIEntity` | alle anwendbaren `RaN` | zeigt Regeln, Normen und Konflikte |

Der WHY-Pfad wird rückwärts über die gespeicherten Pfeile gelesen:

```text
Task
  ◄── DECOMPOSES_INTO ── PiF1o
  ── CONTRIBUTES_TO ──► PiF1t
  ── CONTRIBUTES_TO ──► PiF1s
  ── CONTRIBUTES_TO ──► PiF2
  ◄── INSCRIBES_PURPOSE_IN ── CiV
```

Der WHO-Pfad verbindet Ausführung und Organisation:

```text
Task ── EXECUTED_BY ──► RoleAssignment
                           ├── ACTIVATES_ROLE ──► RoFRole
                           └── IN_TEAM ─────────► RoFTeam ◄── HAS_TEAM ── RoFOrg
RoFTeamMember ── HAS_ASSIGNMENT ──► RoleAssignment
```

Für einen `ACTIVE` oder `COMPLETED` atomaren Task müssen WHY und WHO vollständig sein. Ein Entwurf darf vorübergehend unvollständig sein. `SYNC` darf ihn erst aktivieren, wenn jeder Schritt eindeutig navigierbar ist. Umwelt- und Regelpfade dürfen leer sein, wenn fachlich tatsächlich weder Umweltobjekt noch anwendbares `RaN` existiert; sie dürfen aber nicht wegen fehlender Modellierung leer erscheinen.

Das Hinzufügen, Entfernen oder fachliche Ändern einer gespeicherten Beziehung verändert den Beziehungszustand beider Endpunkte. Für jeden bereits vorhandenen, veränderlichen Endpunkt werden deshalb Revision und `updatedAt` erhöht und der vorherige Zustand als eigenes `PiH` festgehalten. Ein im selben Auftrag neu erzeugter Endpunkt besitzt noch keinen vorherigen Zustand. Das `ChangeEvent` bleibt mit dem unmittelbar angeforderten Ausgangspunkt verbunden; alle weiteren Endpunkte erscheinen über `SyncEvent ── AFFECTS`.

**Kurzes Beispiel:** Der Task „API bereitstellen“ gehört zum operativen Ziel „Antwortzeit unter 24 Stunden“. Dieses trägt über taktische und strategische Zustände zum langfristigen Ziel bei, in das der CiV-Zweck „verlässlicher Kundenservice“ eingeschrieben ist. Ausgeführt wird der Task durch Annas Developer-Rollenaktivierung im verantwortlichen Team. Dadurch sind Zweck und Verantwortung vom Task aus vollständig nachvollziehbar.


## 3. Point in Historie - PiH

### 3.1 Bedeutung

`PiH` steht für **Point in Historie**. Ein `PiH` bewahrt den bisherigen Zustand einer historisierbaren `JCIEntity`, wenn dieser durch eine Änderung abgelöst wird.

Die aktuelle `JCIEntity` wird nicht selbst zu `PiH`. Der durch ein `SyncEvent` dokumentierte Synchronisationslauf hält unmittelbar vor der Übernahme einer Änderung ein eigenständiges historisches Abbild des bisherigen Zustands fest. Dieses bewahrt:

- Identität und Typ des ursprünglichen Elements,
- die bisherigen Eigenschaften,
- die zuvor gültigen Beziehungen und Verantwortlichkeiten,
- den Zeitpunkt der Historisierung als `recordedAt`,
- den Bezug zu `ChangeEvent` und `SyncEvent`.

### 3.2 Entstehung

1. Ein angenommener Veränderungsauftrag wird als `ChangeEvent` erfasst.
2. Das `ChangeEvent` startet mindestens einen technischen `SyncRun`.
3. Der `SyncRun` führt genau eine gespeicherte SYNC-Definition aus.
4. Die SYNC-Definition ermittelt betroffene Elemente und Beziehungen.
5. Sie prüft `RaN` und weitere Modellbedingungen.
6. Vor jeder tatsächlichen Änderung eines vorhandenen Zustands hält der Synchronisationslauf diesen als `PiH` fest.
7. Der geänderte Zustand wird zum aktuellen Zustand.
8. Nach Abschluss oder kontrolliertem Abbruch wird genau ein unveränderliches `SyncEvent` für den `SyncRun` erzeugt und über `TRIGGERS` append-only mit dem `ChangeEvent` verbunden.
9. Das `SyncEvent` dokumentiert Zeiten, Ergebnis, verwendete SYNC-Definition und Auswirkungen des Synchronisationsversuchs.

```text
JCIEntity ── CHANGED_BY ──► ChangeEvent ── startet ──► technischer SyncRun
                                                             │
                                                             └── Abschluss/Abbruch ──► SyncEvent
                                                                                         ├── EXECUTES ──► SYNC
                                                                                         ├── AFFECTS ──► JCIEntity
                                                                                         └── CREATES_HISTORY ──► PiH

JCIEntity ── HAS_HISTORICAL_STATE ──► PiH
```

### 3.3 Objekte und Beziehungen

`PiH`, `ChangeEvent`, `SyncEvent` und `HistoricalCorrection` bleiben getrennte `JCIEntity`-Instanzen. `PiH` ist eine `JCIElementInstance`; die drei anderen Typen sind `GraphObjects`.

| Objekt                 | Bedeutung                                                      |
| ---------------------- | -------------------------------------------------------------- |
| `ChangeEvent`          | Dokumentiert Anlass und Ursache der Änderung.                  |
| `SyncEvent`            | Dokumentiert den Synchronisationslauf und seine Auswirkungen.  |
| `PiH`                  | Bewahrt den durch die Änderung abgelösten Zustand.             |
| `HistoricalCorrection` | Berichtigt oder ergänzt ein `PiH`, ohne es zu verändern.       |

Ein `SyncEvent` ist kein `PiH`. Es kann jedoch mehrere `PiH` erzeugen, wenn ein Synchronisationslauf mehrere bestehende Zustände ablöst.

| Quelle                      | Beziehung              | Ziel                   |  Ziele je Quelle |  Quellen je Ziel |
| --------------------------- | ---------------------- | ---------------------- | ---------------: | ---------------: |
| historisierbare `JCIEntity` | `CHANGED_BY`           | `ChangeEvent`          |           `0..n` |           `0..1` |
| `ChangeEvent`               | `TRIGGERS`             | `SyncEvent`            |           `0..n` |              `1` |
| `ChangeEvent`               | `TARGETS_HISTORY`      | `PiH`                  |           `0..1` |           `0..n` |
| `SyncEvent`                 | `EXECUTES`             | `SYNC`                 |              `1` |           `0..n` |
| `SyncEvent`                 | `AFFECTS`              | `JCIEntity`            |           `0..n` |           `0..n` |
| historisierbare `JCIEntity` | `HAS_HISTORICAL_STATE` | `PiH`                  |           `0..n` |              `1` |
| `SyncEvent`                 | `CREATES_HISTORY`      | `PiH`                  |           `0..n` |              `1` |
| `HistoricalCorrection`      | `CORRECTS`             | `PiH`                  |              `1` |           `0..n` |
| `HistoricalCorrection`      | `CAUSED_BY`            | `ChangeEvent`          |              `1` |           `0..n` |
| `SyncEvent`                 | `CREATES_CORRECTION`   | `HistoricalCorrection` |           `0..n` |              `1` |
| `HistoricalCorrection`      | `SUPERSEDES`           | `HistoricalCorrection` |           `0..1` |           `0..1` |
| `HistoricalCorrection`      | `CORRECTED_BY`         | `RoleAssignment`       |              `1` |           `0..n` |
| `HistoricalCorrection`      | `USES_EVIDENCE`        | `Evidence`             |           `0..n` |           `0..n` |

### 3.4 Regeln und Ausnahme

1. Ein `PiH` entsteht nur aus dem bereits vorhandenen Zustand einer historisierbaren `JCIEntity`.
2. Jeder durch eine tatsächliche Änderung abgelöste Zustand wird als eigenes `PiH` festgehalten.
3. Jedes `PiH` gehört zu genau einer ursprünglichen `JCIEntity`.
4. Eine historisierbare `JCIEntity` kann mehrere zeitlich über `recordedAt` geordnete `PiH` besitzen.
5. Ein `PiH` ist nach seiner Erzeugung unveränderlich, wird nicht ergänzt und nicht erneut historisiert.
6. Eigenschaften und bestehende Provenienzbeziehungen von `ChangeEvent`, `SyncEvent` und `HistoricalCorrection` werden nach ihrer Erzeugung nicht verändert; die ausdrücklich erlaubten append-only Ergänzungen am `ChangeEvent` lösen keine Revision oder Historisierung aus.
7. Bei `changeType = CREATED` entsteht noch kein `PiH`, weil kein vorheriger Zustand existiert. Das `ChangeEvent` und nach jedem beendeten Synchronisationsversuch ein `SyncEvent` entstehen trotzdem. Nur bei `SUCCESS` entsteht außerdem die neue Entität mit `revision = 1` und genau einer `CHANGED_BY`-Beziehung.
8. Eine spätere Erläuterung oder Korrektur wird als neues `HistoricalCorrection`-Objekt gespeichert und darf das bestehende `PiH` nicht überschreiben.
9. Jede `HistoricalCorrection` berichtigt über `CORRECTS` genau ein `PiH` und gehört über `CREATES_CORRECTION` genau zu einem `SyncEvent`.
10. Jede `HistoricalCorrection` benötigt über `CAUSED_BY` genau ein `ChangeEvent`. Dieses besitzt `changeType = HISTORICAL_CORRECTION`, genau ein `TARGETS_HISTORY` zu demselben `PiH` und keine `CHANGED_BY`-Quelle. `ChangeEvent.reason` dokumentiert die gemeldete Abweichung; `HistoricalCorrection.reason` dokumentiert die nach Prüfung bestätigte Berichtigung.
11. Mehrere nicht abgelöste Korrekturen eines `PiH` sind nur zulässig, wenn ihre Mengen `correctedFields` paarweise disjunkt sind. Dadurch besitzt jeder historische Pfad höchstens einen wirksamen korrigierten Wert.
12. Überschneidet eine neue Korrektur die Felder einer wirksamen Korrektur, muss sie genau diese über `SUPERSEDES` ablösen. Wegen der Kardinalität `0..1` darf sie höchstens eine wirksame Korrektur überlappen; andernfalls wird der Auftrag in getrennte Korrekturen aufgeteilt oder endet mit `CONFLICT`.
13. Eine ablösende Korrektur gehört zum selben `PiH`, übernimmt die vollständige Menge `correctedFields` ihrer Vorgängerin und enthält für weiterhin gültige Felder erneut deren wirksame Werte. `SUPERSEDES`-Ketten sind zeitlich vorwärts gerichtet und zyklusfrei.
14. `previousValue` entspricht für jeden Pfad exakt der vor der neuen Korrektur wirksamen `HistoryView`; bei `ADDITION` ist dieser Wert `NULL`. `baseHistoryViewHash` entspricht dieser Basissicht.
15. `SYNC` serialisiert Korrektur-Commits je `PiH` und berechnet die `HistoryView` unmittelbar vor dem Commit erneut. Weicht ihr Hash vom angeforderten `expectedHistoryViewHash` beziehungsweise gespeicherten `baseHistoryViewHash` ab, endet der Versuch mit `CONFLICT`; es entsteht keine `HistoricalCorrection`.
16. Der fachlich gültige historische Stand ergibt sich deterministisch aus dem unveränderten `PiH` und seinen nicht abgelösten, feldweise disjunkten `HistoricalCorrections`.
17. Eine historische Korrektur verändert nicht automatisch den aktuellen Zustand der ursprünglichen `JCIEntity`. Ein daraus entstehender aktueller Änderungsbedarf wird als eigener Veränderungsvorgang verarbeitet.
18. Das über `CAUSED_BY` verbundene `ChangeEvent` muss dasselbe `ChangeEvent` sein, das den über `CREATES_CORRECTION` verbundenen Synchronisationslauf ausgelöst hat.

### 3.5 Nachträgliche Korrektur

Eine `HistoricalCorrection` wird verwendet, wenn sich eine inhaltliche Abweichung nicht aus einer damaligen Zustandsänderung, sondern aus einer später erkannten fehlerhaften, unvollständigen oder mehrdeutigen historischen Dokumentation ergibt.

```text
Festgestellte historische Abweichung
                  │
                  ▼
             ChangeEvent ── TARGETS_HISTORY ──► PiH
                  │
              startet
                  ▼
          SyncRun (technisch)
                  │
         Abschluss oder Abbruch
                  ▼
              SyncEvent ── EXECUTES ──► SYNC
                  │
          CREATES_CORRECTION
                  ▼
       HistoricalCorrection
                  │
                CORRECTS
                  ▼
                 PiH
```

Eine `HistoricalCorrection` enthält mindestens:

| Eigenschaft       | Bedeutung                                                        |
| ----------------- | ---------------------------------------------------------------- |
| `id`              | eindeutige Identität der Korrektur                               |
| `correctionType`  | Art der Korrektur                                                |
| `reason`          | fachliche Begründung                                             |
| `correctedAt`     | Zeitpunkt der Erfassung                                          |
| `baseHistoryViewHash` | SHA-256 der vor der Korrektur wirksamen historischen Sicht  |
| `correctedFields` | betroffene Eigenschaften oder Beziehungen                        |
| `previousValue`   | vor der Korrektur wirksame Angabe                                |
| `correctedValue`  | nachträglich als richtig festgestellte Angabe                    |

Zulässige Korrekturarten sind:

```text
ADDITION      = fehlende historische Angabe ergänzen
CORRECTION    = fehlerhafte historische Angabe berichtigen
CLARIFICATION = mehrdeutige historische Angabe erläutern
```

Die Eigenschaften eines `HistoricalCorrection`-Objekts beschreiben ausschließlich die Abweichung und ihre Berichtigung. Sie ersetzen weder das korrigierte `PiH` noch bilden sie ungeprüft einen vollständigen neuen historischen Zustand. Der im Auftrag übermittelte `expectedHistoryViewHash` muss dem beim Start und unmittelbar vor dem Commit berechneten Hash entsprechen. Damit kann nicht unbemerkt eine zweite Korrektur auf derselben veralteten Basissicht übernommen werden.

Die verantwortliche Person wird über `CORRECTED_BY` mit ihrem konkreten `RoleAssignment` verbunden. Optionale Nachweise werden über `USES_EVIDENCE` als eigenständige `Evidence`-Knoten zugeordnet. Weder Akteurs-IDs noch Nachweisreferenzen werden zusätzlich im Korrekturobjekt gespeichert.

### 3.6 Beispiele

Ein `PiF1o` lautet zunächst:

> Kundenanfragen werden innerhalb von 48 Stunden beantwortet.

Der Zielwert wird anschließend auf 24 Stunden geändert:

```text
PiF1o: Antwort innerhalb von 48 Stunden
                  │
                  │ ChangeEvent
                  ▼
                 SYNC
                  ├── bisheriger Zustand wird PiH
                  └── neuer aktueller Zustand:
                      Antwort innerhalb von 24 Stunden
```

Das aktuelle `PiF1o` enthält danach den Zielwert von 24 Stunden. Der vorherige Zustand mit 48 Stunden bleibt als `PiH` erhalten.

Wird später durch einen prüfbaren Nachweis festgestellt, dass ein `PiH` die damalige Teamzuordnung von Anna unvollständig wiedergibt, bleibt das `PiH` unverändert. Die fehlende Angabe wird durch ein separates `HistoricalCorrection`-Objekt dokumentiert:

```text
PiH: Anna am 10.08.2026
  ├── dokumentierte Rolle: Developer
  └── dokumentiertes Team: Team A

HistoricalCorrection
  ├── correctionType: ADDITION
  ├── reason: damalige Teamzuordnung war unvollständig dokumentiert
  ├── baseHistoryViewHash: SHA-256 der bisher wirksamen HistoryView
  ├── correctedFields: Beziehung HAS_MEMBER zu Team B
  ├── previousValue: NULL
  ├── correctedValue: damalige Beziehung zu Team B
  ├── CORRECTED_BY ──► RoleAssignment: zuständige Prüferin
  ├── USES_EVIDENCE ──► Evidence: damalige Teamzuordnung
  └── CORRECTS ──► PiH: Anna am 10.08.2026
```

Das ursprüngliche `PiH` zeigt weiterhin die zuerst gespeicherte historische Dokumentation. Für die fachliche Auswertung wird es gemeinsam mit der nicht abgelösten `HistoricalCorrection` gelesen. Eine weitere wirksame Korrektur darf dasselbe Beziehungsfeld nicht parallel mit einem anderen Wert belegen; sie muss die bestehende Korrektur ausdrücklich ablösen und gegen die inzwischen neue `HistoryView` geprüft werden. Ergibt sich daraus eine notwendige Änderung an Annas aktuellem Zustand, wird diese unabhängig davon durch ein neues `ChangeEvent` und `SyncEvent` verarbeitet.

---

## 4. Core Influential Values – CiV

### 4.1 Bedeutung

`CiV` steht für **Core Influential Values** und beschreibt den wertbezogenen Zweck einer Organisation. Es beantwortet die Frage:

> Warum ist eine bestimmte Zukunft überhaupt gewollt?

`CiV` gibt den Zukunftszuständen eine begründete Richtung. Es ist selbst weder ein Zukunftszustand noch eine Aufgabe, Regel oder Rolle.

### 4.2 Entstehung

Ein `CiV` entsteht durch die ausdrückliche Beschreibung der grundlegenden Werte und des Zwecks einer Organisation. Typischerweise werden dabei drei Perspektiven unterschieden:

```text
NICHT   = Grenzen und Integrität
SELBST  = Identität und Haltung
DIENEN  = Nutzen und Beitrag
```

Diese Perspektiven beschreiben gemeinsam, was die Organisation ausschließt, wofür sie steht und wem oder was sie dienen will. Aus diesem wertbezogenen Zweck werden langfristige Zukunftszustände (`PiF2`) begründet.

Wird ein bestehendes `CiV` geändert, erfasst das Modell die Änderung als `ChangeEvent`. `SYNC` prüft die Auswirkungen auf verbundene `PiF2` und weitere abhängige Elemente. Der abgelöste CiV-Zustand bleibt als `PiH` erhalten.

### 4.3 Objekte und Beziehungen

| Objekt | Bedeutung                                                                             |
| ------ | ------------------------------------------------------------------------------------- |
| `CiV`  | Beschreibt Werte und Zweck der Organisation.                                          |
| `PiF2` | Beschreibt einen langfristigen Zukunftszustand, in den der Zweck eingeschrieben wird. |
| `PiH`  | Bewahrt einen abgelösten CiV-Zustand oder stellt historischen Kontext bereit.         |

| Quelle | Beziehung                | Ziel   |  Ziele je Quelle |  Quellen je Ziel |
| ------ | ------------------------ | ------ | ---------------: | ---------------: |
| `PiH`  | `PROVIDES_CONTEXT_TO`    | `CiV`  |           `0..n` |           `0..n` |
| `CiV`  | `INSCRIBES_PURPOSE_IN`   | `PiF2` |           `0..n` |           `1..n` |

```text
PiH ── PROVIDES_CONTEXT_TO ──► CiV ── INSCRIBES_PURPOSE_IN ──► PiF2
```

### 4.4 Regeln und Ausnahme

1. `CiV` beschreibt den wertbezogenen Zweck und keinen auszuführenden Zustand.
2. Ein `CiV` kann seinen Zweck in keinen, einen oder mehrere `PiF2` einschreiben. Dadurch kann ein `CiV` bereits als Entwurf bestehen, bevor ein Zukunftszustand formuliert wurde.
3. Jedes `PiF2` muss durch mindestens ein `CiV` wertbezogen begründet sein.
4. Mehrere `CiV` können gemeinsam denselben langfristigen Zukunftszustand begründen.
5. Historische `PiH` können Kontext für die Bildung oder Änderung eines `CiV` bereitstellen.
6. Wird ein `CiV` geändert, muss `SYNC` die Auswirkungen auf alle verbundenen `PiF2` prüfen. Nur tatsächlich geänderte Zustände erhalten ein eigenes `PiH`.

### 4.5 Beispiel

Eine Organisation beschreibt ihren wertbezogenen Zweck für einen verlässlichen Kundenservice:

```text
NICHT   = Kundenanfragen bleiben nicht unbeantwortet.
SELBST  = Wir handeln transparent und verbindlich.
DIENEN  = Kunden erhalten rechtzeitig eine hilfreiche Antwort.
```

Aus diesem `CiV` wird ein langfristiger Zukunftszustand begründet:

```text
CiV ── INSCRIBES_PURPOSE_IN ──► PiF2

PiF2 = Die Organisation bietet langfristig einen verlässlichen,
       transparenten und kundenorientierten Service.
```

Ändert sich der wertbezogene Zweck, prüft `SYNC` die Auswirkungen auf dieses `PiF2`. Der bisherige CiV-Zustand wird vor der Änderung als `PiH` festgehalten.

---

## 5. Point in Future, Second Order – PiF2

### 5.1 Bedeutung

`PiF2` beschreibt einen langfristigen Zukunftszustand mit einem Zeithorizont von mehr als zehn Jahren bis zu einem offenen Zeitpunkt `n`. Er formuliert, welche langfristige Zukunft aus dem wertbezogenen Zweck (`CiV`) heraus gewollt ist.

`PiF2` ist ein Zukunftszustand zweiter Ordnung. Er ist weder eine Strategie noch eine Aufgabe und wird nicht unmittelbar operativ ausgeführt.

### 5.2 Entstehung

Ein `PiF2` entsteht, indem der in einem oder mehreren `CiV` beschriebene Zweck in einen langfristigen Zukunftszustand übersetzt wird. Strategische Zukunftszustände (`PiF1s`) konkretisieren ihre Beiträge zu diesem langfristigen Zustand.

Wird ein `PiF2` geändert, prüft `SYNC` die verbundenen `CiV`, beitragenden `PiF1s` und davon abhängigen Zukunftszustände. Der abgelöste Zustand wird als `PiH` festgehalten.

### 5.3 Objekte und Beziehungen

| Objekt  | Bedeutung                                       |
| ------- | ----------------------------------------------- |
| `CiV`   | Begründet den wertbezogenen Zweck des `PiF2`.   |
| `PiF2`  | Beschreibt den langfristigen Zukunftszustand.   |
| `PiF1s` | Leistet einen strategischen Beitrag zum `PiF2`. |

| Quelle  | Beziehung               | Ziel   |  Ziele je Quelle |  Quellen je Ziel |
| ------- | ----------------------- | ------ | ---------------: | ---------------: |
| `CiV`   | `INSCRIBES_PURPOSE_IN`  | `PiF2` |           `0..n` |           `1..n` |
| `PiF1s` | `CONTRIBUTES_TO`        | `PiF2` |           `1..n` |           `0..n` |

### 5.4 Regeln und Ausnahme

1. Jedes `PiF2` muss durch mindestens ein `CiV` wertbezogen begründet sein.
2. Ein `PiF2` kann Beiträge von keinem, einem oder mehreren `PiF1s` erhalten; `0..n` erlaubt einen noch nicht ausformulierten Entwurf.
3. Ein `PiF1s` muss zu mindestens einem `PiF2` beitragen und kann mehrere `PiF2` unterstützen.
4. `PiF2` beschreibt einen Zustand und keine Tätigkeit.
5. Eine Änderung an `PiF2` führt nicht automatisch zur Änderung aller verbundenen Elemente; `SYNC` prüft zunächst die Auswirkungen.
6. Ein `PiF2` darf `ACHIEVED` nur erreichen, wenn mindestens ein aktuelles `PiF1s` beiträgt. Bei `contributionMode = ALL` müssen alle aktuellen direkten Beiträge `ACHIEVED` sein; bei `ANY` muss mindestens ein aktueller direkter Beitrag `ACHIEVED` sein.
7. Als aktuell gelten beitragende Elemente, die nicht `REPLACED` oder `REVOKED` sind. Ersetzte Beiträge werden über ihren `REPLACED_BY`-Nachfolger berücksichtigt, sobald dieser zum selben Ziel beiträgt.

### 5.5 Beispiel

```text
CiV = Wir dienen Kunden langfristig verlässlich und transparent.
  │
  └── INSCRIBES_PURPOSE_IN ──► PiF2
                                = Die Organisation ist langfristig
                                  für verlässlichen und transparenten
                                  Kundenservice etabliert.
```

---

## 6. Rules and Norms – RaN

### 6.1 Bedeutung

`RaN` steht für **Rules and Norms** und beschreibt Regeln, Normen, Grenzen und Leitplanken des JCI-Modells. `RaN` bestimmt, unter welchen Bedingungen Zukunftszustände, Aufgaben, Organisation, Rollen und Umweltinteraktionen zulässig sind.

`RaN` ist kein linearer Schritt der Zukunftskette. Es wirkt als Querschnittselement auf die jeweils geregelten Ziele.

### 6.2 Entstehung

Ein `RaN` entsteht durch die ausdrückliche Formulierung einer fachlichen Regel, rechtlichen Vorgabe, internen Norm oder verbindlichen Grenze. Die Regel benennt ihre Wirkung, die geregelte Entscheidung, ihren Geltungsbereich, die betroffenen Entitätstypen und eine maschinenlesbare Bedingung. Sie wird mit den aktuell betroffenen Elementen verbunden.

Ein Entwurf darf zunächst ohne Ziel bestehen. Bevor ein `RaN` aktiv wird, muss es mindestens ein geregeltes Ziel besitzen. Wird ein bestehendes `RaN` geändert, prüft `SYNC` alle geregelten Ziele und davon abhängigen Elemente. Der abgelöste RaN-Zustand wird als `PiH` festgehalten.

Jedes `RaN` erhält ausdrücklich eine ganzzahlige Priorität. Eine größere Zahl bedeutet höhere Priorität. Der Wert beschreibt den fachlich beschlossenen Vorrang bei einem tatsächlichen Widerspruch; er wird weder aus `ruleType` noch aus dem Namen oder der Position im Graphen abgeleitet.

`decisionKey` bezeichnet stabil die geregelte Entscheidung, beispielsweise `Task.status.COMPLETED` oder `ERoFObject.action.MODIFY`. Nur Regeln mit demselben `decisionKey`, überlappendem Scope und mindestens einem gemeinsamen Ziel können für diese Entscheidung miteinander kollidieren.

Die maschinenlesbare `condition` besitzt genau einen `combiner = ALL | ANY` und mindestens eine Klausel. Jede Klausel enthält:

| Feld | Bedeutung |
| ---- | --------- |
| `path` | eindeutiger Eigenschafts- oder Beziehungspfad vom geregelten Ziel |
| `operator` | verbindlicher Vergleichsoperator |
| `value` | Vergleichswert; nur bei `EXISTS` und `NOT_EXISTS` nicht erforderlich |

Pfade dürfen Eigenschaften direkt oder ausdrücklich benannte Beziehungen aus dem kanonischen Beziehungskatalog traversieren. Unbegrenzte oder nicht katalogisierte Traversierungen sind unzulässig. Kann ein Pfad nicht eindeutig ausgewertet werden, ist die Regel `UNEVALUABLE`.

Die Wirkung wird so gelesen:

| `effect` | Bedingung wahr | Bedingung falsch |
| -------- | -------------- | ---------------- |
| `REQUIRE` | Entscheidung erlaubt | Entscheidung verweigert |
| `PROHIBIT` | Entscheidung verweigert | keine eigene Entscheidung |
| `PERMIT` | Entscheidung erlaubt | keine eigene Entscheidung |

Eine einzelne Verweigerung ist eine Regelverletzung und kein `RaNConflict`. Ein tatsächlicher Widerspruch entsteht erst, wenn anwendbare Regeln mit demselben `decisionKey` dieselbe konkrete Entscheidung zugleich erlauben und verweigern.

### 6.3 Objekte und Beziehungen

| Bereich                  | Mögliche Ziele                                                   |
| ------------------------ | ---------------------------------------------------------------- |
| Zukunft                  | `PiF2`, `PiF1s`, `PiF1t`, `PiF1o`                                |
| Arbeit                   | `Task`                                                           |
| Organisation             | `RoFOrg`, `RoFTeam`, `RoFTeamMember`                             |
| Organisationsbeziehung   | `RoFOrgRelationship`                                             |
| Rollen                   | `RoFRole`, `RoleAssignment`                                      |
| Umwelt                   | `ERoFObject`                                                     |

Für alle Zielbereiche wird dieselbe gespeicherte Beziehung verwendet:

```text
RaN ── GOVERNS ──► geregeltes JCI-Element oder Graphobjekt
RaN ── APPLIES_IN ──► RoFOrg oder RoFTeam
```

| Quelle | Beziehung  | Ziel                               |  Ziele je Quelle |  Quellen je Ziel |
| ------ | ---------- | ---------------------------------- | ---------------: | ---------------: |
| `RaN`  | `GOVERNS`  | zulässiges Zielelement             |           `0..n` |           `0..n` |
| `RaN`  | `APPLIES_IN` | `RoFOrg` oder `RoFTeam`           |           `0..1` |           `0..n` |

Die Kardinalität `0..n` gilt für die gespeicherte Beziehung. Für ein aktives `RaN` gilt zusätzlich die Invariante, dass es mindestens ein aktuelles Ziel über `GOVERNS` regelt. `SYNC` hält diese Zielmenge bei neuen, geänderten oder aus dem Scope ausscheidenden Entitäten aktuell.

Für den Scope gelten folgende Regeln:

| `scopeType` | `APPLIES_IN` | Bedeutung |
| ----------- | ------------ | --------- |
| `GLOBAL` | keine Beziehung | gilt modellweit für passende `governedTypes` |
| `ORGANIZATION` | genau eine `RoFOrg` | gilt innerhalb der über Teams und Rollen ableitbaren Organisation |
| `TEAM` | genau ein `RoFTeam` | gilt im angegebenen Teamkontext |
| `ENTITY` | keine Beziehung | gilt ausschließlich für die direkt über `GOVERNS` verbundenen Entitäten |

Treffen mehrere aktive und zeitlich gültige `RaN` auf dasselbe Ziel oder dieselbe Entscheidung, prüft `SYNC` zunächst ihre Anwendbarkeit und anschließend ihre Vereinbarkeit:

```text
anwendbare RaN bestimmen
        │
        ├── vereinbar ──► alle Regeln gemeinsam anwenden
        │
        └── widersprüchlich
                ├── unterschiedliche priority ──► höhere priority hat Vorrang
                └── gleiche priority ───────────► RaNConflict mit status = OPEN
```

Eine niedriger priorisierte Regel bleibt bei einem Vorrangfall aktiv und gilt weiterhin überall dort, wo kein Widerspruch zur höher priorisierten Regel besteht. Kann `SYNC` die Anwendbarkeit oder Vereinbarkeit nicht eindeutig bestimmen, entsteht ebenfalls ein offener `RaNConflict` mit `conflictType = UNEVALUABLE`; eine bloße Unsicherheit darf nicht durch die Priorität übergangen werden.

Ein `RaNConflict` dokumentiert die beteiligten Regeln, betroffenen Entitäten und den erkennenden Synchronisationslauf. Er wird nicht automatisch durch `SYNC` entschieden. Zur Auflösung muss ein berechtigtes `RoleAssignment` eine ausdrückliche fachliche Änderung veranlassen, beispielsweise eine Regel präzisieren, ihren Scope oder ihre Priorität ändern oder eine Regel ersetzen beziehungsweise aufheben. Erst ein nachfolgender erfolgreicher Synchronisationslauf, der keinen fortbestehenden Widerspruch mehr feststellt, darf den Konflikt über `RESOLVED_BY` und `RESOLVED_THROUGH` auf `RESOLVED` setzen. Der bisherige offene Zustand wird dabei als `PiH` festgehalten.

### 6.4 Regeln und Ausnahme

1. `RaN` ist ein Querschnittselement und kein Bestandteil der linearen Zukunftskette.
2. Ein RaN-Entwurf darf noch kein geregeltes Ziel besitzen.
3. Ein aktives `RaN` muss mindestens ein zulässiges Zielelement regeln.
4. Ein `RaN` kann mehrere Ziele aus unterschiedlichen Bereichen regeln.
5. Ein Ziel kann gleichzeitig durch keine, eine oder mehrere Regeln und Normen beeinflusst werden.
6. Bei einer Änderung an `RaN` prüft `SYNC` alle direkt geregelten Ziele und deren relevante Abhängigkeiten.
7. Vor einem Vergleich werden ausschließlich aktive, zeitlich gültige und für die betroffene Entität beziehungsweise Entscheidung anwendbare `RaN` berücksichtigt.
8. Vereinbare anwendbare Regeln gelten gemeinsam und werden nicht allein aufgrund einer niedrigeren Priorität ignoriert.
9. Widersprechen sich anwendbare Regeln mit unterschiedlicher `priority`, gilt für genau diesen Widerspruch die größere Zahl. Der `ruleType` erzeugt keinen automatischen Vorrang.
10. Widersprechen sich mindestens zwei anwendbare Regeln mit derselben höchsten einschlägigen Priorität, erzeugt `SYNC` genau einen offenen `RaNConflict` für diese Konfliktmenge und Entscheidung.
11. Kann die Vereinbarkeit oder Anwendbarkeit nicht eindeutig bewertet werden, erzeugt `SYNC` einen offenen `RaNConflict` mit `conflictType = UNEVALUABLE` und trifft keine automatische Entscheidung.
12. Ein offener `RaNConflict` besitzt einen für Veränderungsauftrag, Regelmenge und Entscheidung deterministischen `conflictKey`, benennt mindestens eine `CONFLICTING_RULE`, mindestens eine betroffene `JCIEntity` und genau das erkennende `SyncEvent`. Bei `PRIORITY_TIE` sind mindestens zwei Regeln erforderlich; bei `UNEVALUABLE` kann bereits eine nicht eindeutig auswertbare Regel genügen. Derselbe Synchronisationsauftrag darf denselben Konflikt nicht mehrfach anlegen.
13. Ein Konflikt darf nur durch eine ausdrückliche fachliche Änderung und einen nachfolgenden erfolgreichen Synchronisationslauf auf `RESOLVED` gesetzt werden. Er besitzt dann genau ein `RESOLVED_BY` und ein `RESOLVED_THROUGH`.
14. Die Auflösung verändert nicht rückwirkend das protokollierte `SyncEvent`; der Statuswechsel des Konflikts wird wie jede andere fachliche Änderung historisiert.
15. `governedTypes` ist nicht leer. Jedes Ziel von `GOVERNS` besitzt einen darin aufgeführten konkreten `entityType`.
16. `GLOBAL` und `ENTITY` besitzen kein `APPLIES_IN`; `ORGANIZATION` und `TEAM` besitzen genau eine typgerechte `APPLIES_IN`-Beziehung.
17. Eine nicht erfüllte anwendbare `REQUIRE`-Regel oder eine erfüllte `PROHIBIT`-Regel blockiert die Entscheidung als Regelverletzung, auch wenn keine andere Regel widerspricht.
18. Priorität wird ausschließlich bei gleichzeitigem Erlauben und Verweigern derselben Entscheidung verwendet. Zwei verweigernde oder zwei erlaubende Regeln sind kein Prioritätskonflikt.

### 6.5 Beispiel

Eine Regel begrenzt, welche Rollen ein bestimmtes System verändern dürfen:

```text
RaN = Nur autorisierte Rollen dürfen das Produktivsystem verändern.
  effect = PROHIBIT
  decisionKey = ERoFObject.action.MODIFY
  scopeType = ORGANIZATION
  governedTypes = [ERoFObject]
  condition = ALL(
    path = executingRole.roleName,
    operator = NOT_IN,
    value = [Security, Administrator]
  )
  │
  ├── GOVERNS ──► RoFRole
  ├── GOVERNS ──► RoleAssignment
  └── GOVERNS ──► ERoFObject: Produktivsystem
```

Wird die Regel geändert, prüft `SYNC` die betroffenen Rollenaktivierungen und Umweltinteraktionen. Nur tatsächlich geänderte Zustände werden als eigene `PiH` festgehalten.

Treffen zusätzlich zwei Regeln auf dasselbe Produktivsystem, gilt beispielsweise:

```text
RaN A: Änderungen nur durch Security-Rolle, priority = 80
RaN B: Änderungen durch alle Developer,      priority = 50
```

Im Widerspruch hat `RaN A` Vorrang; `RaN B` bleibt außerhalb dieses Widerspruchs anwendbar. Besitzen beide Regeln `priority = 80`, erzeugt `SYNC` einen offenen `RaNConflict` und nimmt keine automatisch auf diesem Konflikt beruhende Änderung vor.

---

## 7. Point in Future, First Order – Strategic – PiF1s

### 7.1 Bedeutung

`PiF1s` beschreibt einen strategischen Zukunftszustand mit einem Zeithorizont von mehr als fünf bis einschließlich zehn Jahren. Er formuliert, welcher strategische Zustand zu einem oder mehreren `PiF2` beiträgt.

`PiF1s` ist ein Zustand erster Ordnung und keine Strategieaktivität oder Aufgabe.

### 7.2 Entstehung

Ein `PiF1s` entsteht durch die strategische Konkretisierung eines oder mehrerer langfristiger `PiF2`. Taktische Zukunftszustände (`PiF1t`) beschreiben anschließend ihre Beiträge zu diesem strategischen Zustand.

Wird ein `PiF1s` geändert, prüft `SYNC` die verbundenen `PiF2`, beitragenden `PiF1t` und weiteren abhängigen Elemente. Der abgelöste Zustand wird als `PiH` festgehalten.

### 7.3 Objekte und Beziehungen

| Objekt  | Bedeutung                                      |
| ------- | ---------------------------------------------- |
| `PiF2`  | Langfristiger Zukunftszustand.                 |
| `PiF1s` | Strategischer Zukunftszustand.                 |
| `PiF1t` | Leistet einen taktischen Beitrag zum `PiF1s`.  |

| Quelle  | Beziehung         | Ziel    |  Ziele je Quelle |  Quellen je Ziel |
| ------- | ----------------- | ------- | ---------------: | ---------------: |
| `PiF1s` | `CONTRIBUTES_TO`  | `PiF2`  |           `1..n` |           `0..n` |
| `PiF1t` | `CONTRIBUTES_TO`  | `PiF1s` |           `1..n` |           `0..n` |

### 7.4 Regeln und Ausnahme

1. Jedes `PiF1s` muss zu mindestens einem `PiF2` beitragen.
2. Ein `PiF1s` kann gleichzeitig zu mehreren `PiF2` beitragen.
3. Ein `PiF1s` kann Beiträge von keinem, einem oder mehreren `PiF1t` erhalten; `0..n` erlaubt einen noch nicht ausformulierten Entwurf.
4. `PiF1s` beschreibt einen strategischen Zustand und keine auszuführende Tätigkeit.
5. Änderungen werden durch `SYNC` in beide Richtungen des verbundenen Zukunftsgraphen auf Auswirkungen geprüft.
6. Ein `PiF1s` darf `ACHIEVED` nur erreichen, wenn mindestens ein aktuelles `PiF1t` beiträgt. `ALL` verlangt alle aktuellen direkten Beiträge in `ACHIEVED`; `ANY` verlangt mindestens einen.

### 7.5 Beispiel

```text
PiF1s = Eine organisationsweit einheitliche und skalierbare
         Serviceorganisation ist etabliert.
   │
   └── CONTRIBUTES_TO ──► PiF2
```

---

## 8. Point in Future, First Order – Tactical – PiF1t

### 8.1 Bedeutung

`PiF1t` beschreibt einen taktischen Zukunftszustand mit einem Zeithorizont ab einem Jahr bis einschließlich fünf Jahre. Er formuliert, welcher taktische Zustand zu einem oder mehreren strategischen `PiF1s` beiträgt.

`PiF1t` ist ein Zustand und kein Maßnahmenplan oder Task.

### 8.2 Entstehung

Ein `PiF1t` entsteht durch die taktische Konkretisierung eines oder mehrerer `PiF1s`. Operative Zukunftszustände (`PiF1o`) beschreiben anschließend ihre Beiträge zu diesem taktischen Zustand.

Wird ein `PiF1t` geändert, prüft `SYNC` die verbundenen `PiF1s`, beitragenden `PiF1o` und weiteren abhängigen Elemente. Der abgelöste Zustand wird als `PiH` festgehalten.

### 8.3 Objekte und Beziehungen

| Objekt  | Bedeutung                                      |
| ------- | ---------------------------------------------- |
| `PiF1s` | Strategischer Zukunftszustand.                 |
| `PiF1t` | Taktischer Zukunftszustand.                    |
| `PiF1o` | Leistet einen operativen Beitrag zum `PiF1t`.  |

| Quelle  | Beziehung         | Ziel    |  Ziele je Quelle |  Quellen je Ziel |
| ------- | ----------------- | ------- | ---------------: | ---------------: |
| `PiF1t` | `CONTRIBUTES_TO`  | `PiF1s` |           `1..n` |           `0..n` |
| `PiF1o` | `CONTRIBUTES_TO`  | `PiF1t` |           `1..n` |           `0..n` |

### 8.4 Regeln und Ausnahme

1. Jedes `PiF1t` muss zu mindestens einem `PiF1s` beitragen.
2. Ein `PiF1t` kann gleichzeitig zu mehreren `PiF1s` beitragen.
3. Ein `PiF1t` kann Beiträge von keinem, einem oder mehreren `PiF1o` erhalten; `0..n` erlaubt einen noch nicht ausformulierten Entwurf.
4. `PiF1t` beschreibt einen taktischen Zustand und keine Tätigkeit.
5. Änderungen werden durch `SYNC` auf strategische und operative Auswirkungen geprüft.
6. Ein `PiF1t` darf `ACHIEVED` nur erreichen, wenn mindestens ein aktuelles `PiF1o` beiträgt. `ALL` verlangt alle aktuellen direkten Beiträge in `ACHIEVED`; `ANY` verlangt mindestens einen.

### 8.5 Beispiel

```text
PiF1t = Alle Servicebereiche arbeiten mit einem einheitlichen
         Verantwortungs- und Bearbeitungsmodell.
   │
   └── CONTRIBUTES_TO ──► PiF1s
```

---

## 9. Point in Future, First Order – Operational – PiF1o

### 9.1 Bedeutung

`PiF1o` beschreibt einen konkret erreichbaren operativen Zukunftszustand mit einem Zeithorizont von weniger als einem Jahr. Er formuliert, was erreicht sein soll. Die dafür erforderliche Tätigkeit wird getrennt als `Task` modelliert.

```text
PiF1o       = Was soll als Zustand erreicht sein?
Task        = Was muss dafür getan werden?
Result      = Was hat der Task erzeugt?
Verification = Erfüllt das Result das Erfolgskriterium?
```

### 9.2 Entstehung

Ein `PiF1o` entsteht durch die operative Konkretisierung eines oder mehrerer `PiF1t`. Für jeden `PiF1o` werden mindestens ein `SuccessCriterion`, genau ein verantwortliches `RoFTeamMember` und mindestens ein `Task` festgelegt.

Jeder Task wird genau einem verantwortlichen `RoFTeam` zugeordnet und als `ATOMIC` oder `COMPOSITE` typisiert. Ein atomarer Task ist unmittelbar ausführbar und wird in `ACTIVE` oder `COMPLETED` durch mindestens ein `RoleAssignment` ausgeführt. Mindestens eines dieser RoleAssignments gehört zum verantwortlichen Team; weitere RoleAssignments aus anderen Teams können unterstützen. Ein zusammengesetzter Task bündelt dagegen mindestens einen untergeordneten Task und besitzt keine eigene Ausführung, Umweltverwendung oder Ergebnisproduktion. Das dem `PiF1o` über `ACCOUNTABLE_MEMBER` zugeordnete Teammitglied darf atomare Tasks ausführen, muss aber nicht zu deren ausführenden Personen gehören.

Tasks können andere Tasks über `DEPENDS_ON` als Voraussetzung benennen. Solange mindestens eine Voraussetzung nicht `COMPLETED` ist, ist der abhängige Task `BLOCKED`. Ein atomarer Task kann `ERoFObjects` verwenden und `Results` erzeugen. Eine `Verification` bewertet ein abgeschlossenes Result gegen ein aktives, zum selben `PiF1o` gehörendes `SuccessCriterion` und bindet die dabei gelesenen Revisionen beider Ziele. Wird dieselbe Kombination aus Result und Erfolgskriterium erneut geprüft, entsteht eine neue `Verification`, die ihre unmittelbare Vorgängerin über `SUPERSEDES` ablöst.

Wird ein `PiF1o` oder ein verbundenes operatives Graphobjekt geändert, prüft `SYNC` die Auswirkungen auf Zukunftsbeiträge, Erfolgskriterien, Verantwortung, Tasks, Rollenaktivierungen, Umweltobjekte, Ergebnisse und Prüfungen. Nur tatsächlich abgelöste Zustände werden als eigene `PiH` festgehalten.

### 9.3 Objekte und Beziehungen

| Objekt             | Bedeutung                                                |
| ------------------ | -------------------------------------------------------- |
| `PiF1t`            | Taktischer Zukunftszustand.                              |
| `PiF1o`            | Operativer Zukunftszustand.                              |
| `SuccessCriterion` | Kriterium für die erfolgreiche Realisierung.             |
| `RoFTeamMember`    | Für den `PiF1o` verantwortliches Mitglied.               |
| `Task`             | Atomare Tätigkeit oder zusammengesetzte Arbeitsstruktur zur Realisierung des `PiF1o`. |
| `RoleAssignment`   | Aktive Rolle, durch die ein Task ausgeführt wird.        |
| `ERoFObject`       | Konkretes Umweltobjekt, das bei der Arbeit genutzt wird. |
| `Result`           | Durch einen Task erzeugtes Ergebnis.                     |
| `Verification`     | Prüfung eines Results gegen ein Erfolgskriterium.        |
| `Evidence`         | Optionaler, separat verwalteter Nachweis.                |

| Quelle           | Beziehung               | Ziel               |  Ziele je Quelle |  Quellen je Ziel |
| ---------------- | ----------------------- | ------------------ | ---------------: | ---------------: |
| `PiF1o`          | `CONTRIBUTES_TO`        | `PiF1t`            |           `1..n` |           `0..n` |
| `PiF1o`          | `HAS_SUCCESS_CRITERIA`  | `SuccessCriterion` |           `1..n` |              `1` |
| `PiF1o`          | `ACCOUNTABLE_MEMBER`    | `RoFTeamMember`    |              `1` |           `0..n` |
| `PiF1o`          | `DECOMPOSES_INTO`       | `Task`             |           `1..n` |              `1` |
| `Task`           | `DECOMPOSES_INTO`       | `Task`             |           `0..n` |           `0..1` |
| `Task`           | `DEPENDS_ON`            | `Task`             |           `0..n` |           `0..n` |
| `Task`           | `EXECUTED_BY`           | `RoleAssignment`   |           `0..n` |           `0..n` |
| `Task`           | `RESPONSIBLE_TEAM`      | `RoFTeam`          |              `1` |           `0..n` |
| `Task`           | `USES`                  | `ERoFObject`       |           `0..n` |           `0..n` |
| `RoleAssignment` | `USES`                  | `ERoFObject`       |           `0..n` |           `1..n` |
| `Task`           | `PRODUCES`              | `Result`           |           `0..n` |              `1` |
| `Verification`   | `EVALUATES`             | `Result`           |              `1` |           `0..n` |
| `Verification`   | `CHECKS`                | `SuccessCriterion` |              `1` |           `0..n` |
| `Verification`   | `USES_EVIDENCE`         | `Evidence`         |           `0..n` |           `0..n` |
| `Verification`   | `SUPERSEDES`            | `Verification`     |           `0..1` |           `0..1` |

```text
PiF1o
  ├── HAS_SUCCESS_CRITERIA ──► SuccessCriterion ◄── CHECKS ── Verification
  ├── ACCOUNTABLE_MEMBER ──► RoFTeamMember
  └── DECOMPOSES_INTO ──► COMPOSITE Task
                                  ├── RESPONSIBLE_TEAM ──► RoFTeam
                                  └── DECOMPOSES_INTO ──► ATOMIC Task ── PRODUCES ──► Result
                                                               ├── DEPENDS_ON ──► Task
                                                               ├── EXECUTED_BY ──► RoleAssignment
                                                               └── USES ──► ERoFObject
```

### 9.4 Regeln und Ausnahme

1. Jedes `PiF1o` muss zu mindestens einem `PiF1t` beitragen und kann mehrere `PiF1t` unterstützen.
2. Jeder `PiF1o` besitzt mindestens ein `SuccessCriterion`.
3. Jeder `PiF1o` ist genau einem verantwortlichen `RoFTeamMember` zugeordnet.
4. Jeder `PiF1o` wird in mindestens einen `Task` zerlegt; jeder Task ist unabhängig von seiner Hierarchiestufe direkt genau einem `PiF1o` zugeordnet.
5. Jeder Task besitzt genau ein `taskKind = ATOMIC | COMPOSITE` und genau ein verantwortliches `RoFTeam`.
6. Ein `ATOMIC`-Task besitzt keine untergeordneten Tasks. In `ACTIVE` oder `COMPLETED` besitzt er mindestens ein ausführendes `RoleAssignment`; mindestens eines davon gehört über `IN_TEAM` zum verantwortlichen Team.
7. Ein `COMPOSITE`-Task besitzt mindestens einen direkten Untertask und keine Beziehungen `EXECUTED_BY`, `USES` oder `PRODUCES`. Sein Status wird ausschließlich aus den direkten Untertasks abgeleitet.
8. Ein Task kann höchstens einen direkten übergeordneten Task besitzen. Übergeordneter Task und Untertask gehören zum selben `PiF1o`; die Task-Hierarchie ist zyklusfrei.
9. Weitere `RoleAssignments` aus anderen Teams dürfen einen atomaren Task unterstützen.
10. Das `ACCOUNTABLE_MEMBER` eines `PiF1o` darf dessen atomare Tasks ausführen, muss aber keinem ausführenden `RoleAssignment` angehören.
11. Accountability für den `PiF1o`, Verantwortung des Teams für den Task und tatsächliche Ausführung atomarer Tasks durch `RoleAssignments` bleiben fachlich getrennt.
12. Ein atomarer Task kann keine, eine oder mehrere Beziehungen zu `ERoFObjects` besitzen. Verwendet er ein Umweltobjekt, muss mindestens ein ausführendes `RoleAssignment` dasselbe `ERoFObject` verwenden.
13. `DEPENDS_ON` darf zwischen Tasks desselben oder verschiedener `PiF1o` bestehen, aber weder Selbstbezüge noch Zyklen bilden. Eine Voraussetzung ist nur mit `status = COMPLETED` erfüllt.
14. Besitzt ein Task mindestens eine nicht erfüllte Voraussetzung, ist sein Status `BLOCKED`. `REPLACED` oder `REVOKED` erfüllen eine Voraussetzung nicht; eine gültige Nachfolge muss ausdrücklich neu über `DEPENDS_ON` verbunden werden.
15. Ein atomarer Task darf `COMPLETED` nur erreichen, wenn alle Voraussetzungen abgeschlossen sind, mindestens ein gültiges ausführendes RoleAssignment zum verantwortlichen Team gehört, relevante `RaN` erfüllt sind und der Abschluss bestätigt wurde. Ein `Result` ist nicht für jeden Task zwingend.
16. Der Status eines zusammengesetzten Tasks wird aus seinen effektiven direkten Untertasks abgeleitet: ausschließlich `DRAFT` ergibt `DRAFT`; alle `COMPLETED` ergeben `COMPLETED`; mindestens ein `ACTIVE` ergibt `ACTIVE`; eine Mischung aus `DRAFT` und `COMPLETED` ergibt `ACTIVE`; ohne `ACTIVE`, aber mit mindestens einem `BLOCKED`, ergibt sich `BLOCKED`. Ein `REPLACED`-Untertask wird nur dann durch seinen Nachfolger ersetzt, wenn dieser über `REPLACED_BY` verbunden und ebenfalls direkter Untertask desselben Composite-Tasks ist. Ein weiterhin verbundener `REVOKED`-Untertask oder ein `REPLACED`-Untertask ohne so eingebundenen Nachfolger erzeugt einen Konflikt.
17. Ein atomarer Task kann noch kein, ein oder mehrere `Results` erzeugt haben; jedes Result gehört genau zu einem atomaren Task.
18. Eine `Verification` bewertet genau ein Result und prüft genau ein `SuccessCriterion`. Das Result besitzt `status = COMPLETED`; das Kriterium ist `ACTIVE`. Result und Kriterium gehören über den erzeugenden Task beziehungsweise `HAS_SUCCESS_CRITERIA` zu demselben `PiF1o`.
19. Bei der Erzeugung entsprechen `evaluatedResultRevision` und `checkedCriterionRevision` exakt den in derselben konsistenten Lesesicht gelesenen Revisionen von Result und Kriterium. Unmittelbar vor dem Commit liest `SYNC` beide Revisionen erneut; jede Abweichung führt zu `CONFLICT`, und die `Verification` wird nicht gespeichert.
20. Das Prüfergebnis wird auf `Verification` als `VALID`, `INVALID` oder `INCONCLUSIVE` gespeichert.
21. `Evidence` wird nur als eigener Knoten verwendet, wenn ein Nachweis separat verwaltet, wiederverwendet oder auditiert werden muss.
22. `PiF1o` ist ein Zustand und niemals selbst ein Task.
23. Ein PiF1o-Entwurf ist erst fachlich vollständig, wenn Zukunftsbeitrag, Erfolgskriterium, Accountability und Tasks vorhanden sind.
24. Eine anwendbare aktuelle `Verification` ist abgeschlossen, nicht über `SUPERSEDES` abgelöst und ihre beiden gebundenen Revisionen stimmen weiterhin mit den aktuellen Revisionen von Result und Kriterium überein.
25. Eine spätere Änderung des Results oder Kriteriums verändert die unveränderliche `Verification` nicht. Sie bleibt als Prüftatsache erhalten, ist für den neuen Stand aber nicht mehr anwendbar; bis zu einer neuen Prüfung gilt das betroffene Kriterium insoweit als nicht erfüllt.
26. `SUPERSEDES` verbindet nur Verifications, die dasselbe `Result` bewerten und dasselbe `SuccessCriterion` prüfen. Die gebundenen Zielrevisionen einer Nachfolgerin dürfen nicht kleiner als diejenigen ihrer Vorgängerin sein; gleiche Revisionen sind für eine erneute Prüfung mit neuer Methode oder Evidence zulässig. Die Kette ist zeitlich vorwärts gerichtet und zyklusfrei.
27. Für dieselbe Kombination aus Result, SuccessCriterion und den beiden gebundenen Revisionen besteht höchstens eine nicht abgelöste `Verification`.
28. `verifiedAt` liegt nicht vor `updatedAt` der beiden gebundenen Zielrevisionen.
29. Jedes `PiF1o` besitzt mindestens ein `SuccessCriterion` mit `requirementLevel = REQUIRED`.
30. Ein `PiF1o` darf `ACHIEVED` nur erreichen, wenn alle verpflichtenden Erfolgskriterien durch anwendbare aktuelle Verifications erfüllt, alle ihm zugeordneten Tasks `COMPLETED`, alle Task-Abhängigkeiten erfüllt und keine relevante Modell- oder `RaN`-Verletzung besteht.
31. `ACHIEVED` ist terminal. Eine spätere Ziel- oder Kriterienänderung wird als neues operatives Zukunftselement modelliert.

#### 9.4.1 Aggregation der Erfolgskriterien

Für jedes `SuccessCriterion` gelten `requirementLevel = REQUIRED | OPTIONAL` und `evaluationMode = ALL | ANY`. Ohne ausdrücklich abweichende Festlegung gelten `REQUIRED` und `ALL`.

Bei `evaluationMode = ALL` ist das Kriterium erfüllt, wenn mindestens eine anwendbare aktuelle `Verification` existiert und alle anwendbaren aktuellen Verifications `outcome = VALID` besitzen. Bei `evaluationMode = ANY` genügt mindestens eine anwendbare aktuelle Verification mit `outcome = VALID`. `INVALID`, `INCONCLUSIVE`, eine fehlende anwendbare Verification oder ausschließlich revisionsveraltete Verifications erfüllen ein Kriterium nicht; bei `ALL` verhindert bereits ein nicht gültiges anwendbares Ergebnis die Erfüllung.

```text
ALL: VALID + VALID        = erfüllt
ALL: VALID + INVALID      = nicht erfüllt
ALL: VALID + INCONCLUSIVE = nicht erfüllt
ANY: VALID + INVALID      = erfüllt
ANY: INVALID + INVALID    = nicht erfüllt
keine anwendbare aktuelle Verification = nicht erfüllt
nur revisionsveraltete Verifications = nicht erfüllt
```

Die Kriterienbedingung eines `PiF1o` ist erfüllt, wenn alle seine `REQUIRED`-Kriterien erfüllt sind. `OPTIONAL`-Kriterien werden ausgewertet und dokumentiert, blockieren den Status `ACHIEVED` aber nicht. Berücksichtigt werden nur anwendbare aktuelle Verifications, die Ergebnisse von Tasks desselben `PiF1o` bewerten. Für `ACHIEVED` müssen zusätzlich alle Task- und Modellbedingungen erfüllt sein.

Der Messwert einer Verification wird aus dem bewerteten `Result` nach der im Erfolgskriterium festgelegten Methode bestimmt und mit `operator`, `targetValue` und gegebenenfalls `unit` verglichen. `outcome = VALID` ist nur zulässig, wenn dieser Vergleich erfolgreich und durch die angegebene Methode reproduzierbar ist. Ist kein eindeutiger Vergleich möglich, lautet das Ergebnis `INCONCLUSIVE`.

```text
PiF1o.ACHIEVED
= mindestens ein REQUIRED-Kriterium vorhanden
+ alle REQUIRED-Kriterien erfüllt
+ alle zugeordneten Tasks COMPLETED
+ alle Task-Abhängigkeiten erfüllt
+ alle berücksichtigten Verifications abgeschlossen
+ keine relevante Modell- oder RaN-Verletzung
```

### 9.5 Beispiel

„Kundenportal entwickeln“ bezeichnet eine Tätigkeit und wird deshalb als zusammengesetzter Task gespeichert. Der dazugehörige `PiF1o` beschreibt den erreichten Zustand:

```text
PiF1o: Das Kundenportal ist produktiv nutzbar.
  └── DECOMPOSES_INTO ──► COMPOSITE Task: Kundenportal entwickeln
                              ├── DECOMPOSES_INTO ──► ATOMIC Task: Benutzeroberfläche umsetzen
                              ├── DECOMPOSES_INTO ──► ATOMIC Task: API bereitstellen
                              ├── DECOMPOSES_INTO ──► ATOMIC Task: Datenbank einrichten
                              ├── DECOMPOSES_INTO ──► ATOMIC Task: Portal testen
                              │                              └── DEPENDS_ON ──► API bereitstellen
                              └── DECOMPOSES_INTO ──► ATOMIC Task: Portal veröffentlichen
                                                             └── DEPENDS_ON ──► Portal testen
```

Alle Tasks bleiben zusätzlich direkt mit diesem `PiF1o` verbunden. Dadurch bleibt der WHY-Pfad von jedem atomaren Task zum operativen Zustand kurz, während `DECOMPOSES_INTO` zwischen Tasks die Arbeitsstruktur abbildet.

```text
PiF1o = Mindestens 95 % der Kundenanfragen werden
         innerhalb von 24 Stunden beantwortet.
   │
   ├── CONTRIBUTES_TO ──► PiF1t
   ├── HAS_SUCCESS_CRITERIA ──►
   │      SuccessCriterion = Antwortzeit höchstens 24 Stunden
   ├── ACCOUNTABLE_MEMBER ──► RoFTeamMember: Jana
   └── DECOMPOSES_INTO ──► Task
             ├── RESPONSIBLE_TEAM ──► RoFTeam: Entwicklung
             ├── EXECUTED_BY ──► RoleAssignment: Ernst als Developer in Entwicklung
             ├── EXECUTED_BY ──► RoleAssignment: Anna als Testerin in Qualitätssicherung
             ├── USES ──► ERoFObject: Ticketsystem
             └── PRODUCES ──► Result: beantwortete Anfrage
                                      ◄── EVALUATES ── Verification
                                               └── CHECKS ──► SuccessCriterion
```

Jana bleibt für den `PiF1o` accountable, obwohl Ernst und Anna den Task ausführen. Das Team Entwicklung trägt die Verantwortung für den Task; mindestens eines seiner `RoleAssignments` muss an der Ausführung beteiligt sein. Die `Verification` speichert `VALID`, `INVALID` oder `INCONCLUSIVE` sowie die geprüften Revisionen von Result und Erfolgskriterium. Ändert sich danach eines der beiden Ziele, bleibt die Prüfung erhalten, zählt aber bis zu einer neuen Verification nicht mehr für die Zielerreichung. Ein separater `Evidence`-Knoten wird nur angelegt, wenn der Nachweis eigenständig verwaltet werden muss. `SYNC` setzt den `PiF1o` erst dann auf `ACHIEVED`, wenn alle verpflichtenden Erfolgskriterien nach der festgelegten Auswertungsart erfüllt sind.

---

## 10. Roles and Functions – RoF

### 10.1 Bedeutung

`RoF` steht für **Roles and Functions** und beschreibt die organisatorische Handlungsfähigkeit im JCI-Modell. Es ordnet eigenständige Organisationen, ihre Beziehungen, Teams, Mitglieder, Rollen und die konkrete Aktivierung einer Rolle in einem Team.

`RoF` ist eines der zehn fachlichen JCI-Kernelemente, wird aber nicht als eigener Knoten gespeichert. Der RoF-Modellraum wird vollständig durch `RoFOrg`, `RoFOrgRelationship`, `RoFTeam`, `RoFTeamMember`, `RoFRole`, `RoleAssignment` und ihre Beziehungen konkretisiert. Ein zusätzlicher `RoF`-Knoten würde dieselben Zusammenhänge nur redundant zusammenfassen.

Eine `RoFOrg` ist immer eine eigenständig handlungsfähige Organisation. Mutterunternehmen, Tochterunternehmen und Partnerunternehmen werden daher jeweils als eigene `RoFOrg` modelliert. Ihre Stellung zueinander wird durch eine typisierte `RoFOrgRelationship` beschrieben.

`RoF` beantwortet insbesondere:

- In welcher Organisation findet die Arbeit statt?
- Welches Team trägt die operative Verantwortung?
- Welches Mitglied ist für einen Zukunftszustand verantwortlich?
- Welche Rollen besitzt das Mitglied?
- Welche Rolle ist für das Mitglied in einem bestimmten Team aktiv?
- Welche eigenständigen Organisationen stehen als Mutter, Tochter oder Partner miteinander in Beziehung?

### 10.2 Entstehung

Eine `RoFOrg` bildet den organisatorischen Rahmen der operativen Arbeit. Ihr werden ein oder mehrere `RoFTeams` zugeordnet. Ein Team besitzt mindestens ein `RoFTeamMember`; ein Mitglied kann mehreren Teams angehören.

Eine `RoFOrgRelationship` entsteht, wenn zwei eigenständige `RoFOrg` in einer fachlich relevanten Organisationsbeziehung stehen. `SUBSIDIARY` beschreibt eine gerichtete Mutter-Tochter-Beziehung. `PARTNERSHIP` beschreibt eine wechselseitige Partnerschaft zwischen unabhängigen Organisationen. Eine Tochterorganisation kann selbst weitere Tochterorganisationen besitzen und eigene Partnerschaften eingehen.

Jede aktive Organisationsbeziehung wird durch mindestens ein `RoleAssignment` aus jeder beteiligten Organisation personengebunden getragen. Teams, Mitglieder und Rollen werden über diese `RoleAssignments` abgeleitet und nicht zusätzlich direkt an der Organisationsbeziehung gespeichert.

Die Rollen eines Mitglieds werden unabhängig vom Teamkontext einmalig über `HAS_ROLE` gespeichert. Soll das Mitglied eine seiner Rollen in einem bestimmten Team ausüben, wird dafür ein eigenes `RoleAssignment` angelegt. Dieses verbindet das Mitglied mit genau einem Team und aktiviert genau eine Rolle aus seinem Rollenbestand.

Wird ein RoF-Element, eine organisatorische Zuordnung oder eine `RoFOrgRelationship` geändert, prüft `SYNC` beide beteiligten Organisationen, ihre vertretenden Rollenaktivierungen, betroffene Zukunftszustände, Tasks, Regeln und Umweltbeziehungen. Tatsächlich abgelöste Zustände werden als eigene `PiH` festgehalten.

### 10.3 Objekte und Beziehungen

| Objekt                 | Bedeutung                                                                  |
| ---------------------- | -------------------------------------------------------------------------- |
| `RoFOrg`               | Eigenständig handlungsfähige Organisation.                                 |
| `RoFOrgRelationship`   | Typisierte und personengebundene Beziehung zwischen zwei `RoFOrg`.         |
| `RoFTeam`              | Organisatorische oder funktionale Gruppe.                                  |
| `RoFTeamMember`        | Handlungsfähiger menschlicher oder technischer Akteur.                     |
| `RoFRole`              | Rolle, Funktion und Verantwortungsbereich eines Mitglieds.                 |
| `RoleAssignment`       | Aktivierung einer Rolle eines Mitglieds in einem Team.                     |

Lesebeispiel für `RoFOrg ── HAS_TEAM ──► RoFTeam`: **Ziele je Quelle `1..n`** bedeutet, dass jede `RoFOrg` mindestens ein Team besitzt; **Quellen je Ziel `1`** bedeutet, dass jedes `RoFTeam` genau einer `RoFOrg` zugeordnet ist.

| Quelle           | Beziehung            | Ziel             | Ziele je Quelle | Quellen je Ziel |
| ---------------- | -------------------- | ---------------- | --------------: | --------------: |
| `RoFOrg`         | `HAS_TEAM`           | `RoFTeam`        |          `1..n` |             `1` |
| `RoFTeam`        | `HAS_MEMBER`         | `RoFTeamMember`  |          `1..n` |          `1..n` |
| `RoFTeamMember`  | `HAS_ROLE`           | `RoFRole`        |          `1..n` |          `0..n` |
| `RoFTeamMember`  | `HAS_ASSIGNMENT`     | `RoleAssignment` |          `0..n` |             `1` |
| `RoleAssignment` | `IN_TEAM`            | `RoFTeam`        |             `1` |          `0..n` |
| `RoleAssignment` | `ACTIVATES_ROLE`     | `RoFRole`        |             `1` |          `0..n` |
| `PiF1o`          | `ACCOUNTABLE_MEMBER` | `RoFTeamMember`  |             `1` |          `0..n` |
| `Task`           | `RESPONSIBLE_TEAM`   | `RoFTeam`        |             `1` |          `0..n` |
| `Task`           | `EXECUTED_BY`        | `RoleAssignment` |          `0..n` |          `0..n` |

Lesebeispiel für `RoFOrgRelationship ── SOURCE_ORG ──► RoFOrg`: **Ziele je Quelle `1`** bedeutet, dass jede Organisationsbeziehung genau eine Quellorganisation besitzt; **Quellen je Ziel `0..n`** bedeutet, dass eine `RoFOrg` Quelle keiner, einer oder mehrerer Organisationsbeziehungen sein kann.

| Quelle               | Beziehung        | Ziel             | Ziele je Quelle | Quellen je Ziel |
| -------------------- | ---------------- | ---------------- | --------------: | --------------: |
| `RoFOrgRelationship` | `SOURCE_ORG`     | `RoFOrg`         |             `1` |          `0..n` |
| `RoFOrgRelationship` | `TARGET_ORG`     | `RoFOrg`         |             `1` |          `0..n` |
| `RoFOrgRelationship` | `REPRESENTED_BY` | `RoleAssignment` |          `2..n` |          `0..n` |

```text
RoFOrg ── HAS_TEAM ──► RoFTeam ── HAS_MEMBER ──► RoFTeamMember
                                                        ├── HAS_ROLE ──► RoFRole
                                                        └── HAS_ASSIGNMENT ──► RoleAssignment
                                                                                  ├── IN_TEAM ──► RoFTeam
                                                                                  └── ACTIVATES_ROLE ──► RoFRole

RoFOrg ◄── SOURCE_ORG ── RoFOrgRelationship ── TARGET_ORG ──► RoFOrg
                              └── REPRESENTED_BY ──► RoleAssignment
```

### 10.4 Regeln und Ausnahme

1. Operative Arbeit findet innerhalb einer `RoFOrg` statt.
2. Mutterunternehmen, Tochterunternehmen und Partnerunternehmen sind jeweils eigenständige `RoFOrg`.
3. Eine `RoFOrg` erreicht Mitglieder und Rollen ausschließlich über `RoFTeam → RoFTeamMember → RoFRole`; direkte Beziehungen von der Organisation zu Mitgliedern oder Rollen werden nicht gespeichert.
4. Jedes `RoFTeam` gehört genau zu einer `RoFOrg` und besitzt mindestens ein Mitglied.
5. Ein `RoFTeamMember` kann Mitglied in mehreren Teams sein.
6. Ein Mitglied besitzt mindestens eine `RoFRole`; dieselbe Rolle wird im Rollenbestand eines Mitglieds nur einmal gespeichert.
7. Ein `RoleAssignment` gehört genau zu einem Mitglied, genau einem Team und aktiviert genau eine Rolle.
8. Ein `RoleAssignment` darf nur eine Rolle aktivieren, die das zugehörige Mitglied über `HAS_ROLE` besitzt.
9. Das Mitglied eines `RoleAssignment` muss über `HAS_MEMBER` dem darin referenzierten Team angehören.
10. Dieselbe Rolle kann für ein Mitglied in mehreren Teams aktiv sein; dafür wird je Team ein eigenes `RoleAssignment` verwendet.
11. Jede `RoFOrgRelationship` verbindet über `SOURCE_ORG` und `TARGET_ORG` genau zwei unterschiedliche `RoFOrg`.
12. `SUBSIDIARY` ist von der Mutterorganisation zur Tochterorganisation gerichtet. Eine Tochterorganisation darf selbst Quelle weiterer `SUBSIDIARY`-Beziehungen sein.
13. Aktive `SUBSIDIARY`-Beziehungen dürfen keine Zyklen bilden. Eine `RoFOrg` darf im aktuellen Modell höchstens eine unmittelbare Mutterorganisation besitzen.
14. `PARTNERSHIP` verbindet unabhängige Organisationen fachlich wechselseitig. Die gespeicherte Quell- und Zielrichtung begründet keine organisatorische Unterordnung.
15. Jede aktive `RoFOrgRelationship` wird durch mindestens ein gültiges `RoleAssignment` aus jeder beteiligten Organisation vertreten.
16. Ein `RoFTeamMember` beschreibt dieselbe menschliche oder technische Identität auch dann, wenn sie über mehrere Teams oder Organisationen tätig ist. Die jeweiligen Kontexte entstehen durch getrennte Mitgliedschaften und `RoleAssignments`, nicht durch das Duplizieren der Person.
17. Jede `HAS_MEMBER`- und `HAS_ROLE`-Beziehung besitzt einen Gültigkeitszeitraum. Der Zeitraum eines `RoleAssignment` muss vollständig innerhalb einer gleichzeitig gültigen Teammitgliedschaft und eines gleichzeitig gültigen Rollenbesitzes liegen.
18. Ist `allocation` gesetzt, liegt der Wert größer als `0` und höchstens bei `1`. Die Summe gleichzeitig gültiger `allocation`-Werte eines `RoFTeamMember` darf `1` nicht überschreiten. Fehlt der Wert, wird Kapazität für diese Rollenaktivierung nicht quantitativ ausgewertet.
19. Für eine aktive `PARTNERSHIP` wird die technisch gespeicherte Richtung deterministisch gewählt: Die lexikografisch kleinere Organisations-UUID ist `SOURCE_ORG`. Das verändert nicht die fachliche Wechselseitigkeit.
20. Zwei aktive `RoFOrgRelationship`-Objekte mit demselben Typ und demselben Organisationspaar dürfen keine überlappenden Gültigkeitszeiträume besitzen.
16. Das Team jedes vertretenden `RoleAssignment` muss zur jeweils vertretenen `RoFOrg` gehören.
17. Eine beteiligte Organisation wird nicht zusätzlich als `ERoFObject` dupliziert.
18. Jeder `PiF1o` besitzt genau ein accountable `RoFTeamMember`. Jeder seiner Tasks besitzt genau ein verantwortliches `RoFTeam`; nur aktive oder abgeschlossene atomare Tasks benötigen mindestens ein ausführendes `RoleAssignment`. Das accountable Mitglied muss den Task nicht selbst ausführen.

### 10.5 Beispiel

Anna besitzt die Rolle `Developer` genau einmal. Sie ist Mitglied in Team A und Team B. Weil sie die Rolle in beiden Teams ausübt, werden zwei getrennte Rollenaktivierungen benötigt:

```text
RoFTeamMember: Anna
  ├── HAS_ROLE ──► RoFRole: Developer
  ├── HAS_ASSIGNMENT ──► RoleAssignment A
  │                          ├── IN_TEAM ──► Team A
  │                          └── ACTIVATES_ROLE ──► Developer
  └── HAS_ASSIGNMENT ──► RoleAssignment B
                             ├── IN_TEAM ──► Team B
                             └── ACTIVATES_ROLE ──► Developer
```

Die Rolle `Developer` wird nicht doppelt am Mitglied gespeichert. Nur ihre teambezogene Aktivierung wird für jedes Team getrennt modelliert. Dadurch bleibt eindeutig, in welchem Team Anna welche Tasks in welcher Rolle ausführt.

Ein Konzern A besitzt ein eigenständiges Tochterunternehmen B. B besitzt wiederum das eigenständige Tochterunternehmen C und unterhält eine Partnerschaft mit dem unabhängigen Unternehmen D:

```text
RoFOrgRelationship: A zu B
  ├── type = SUBSIDIARY
  ├── SOURCE_ORG ──► RoFOrg A
  ├── TARGET_ORG ──► RoFOrg B
  └── REPRESENTED_BY ──► RoleAssignments aus A und B

RoFOrgRelationship: B zu C
  ├── type = SUBSIDIARY
  ├── SOURCE_ORG ──► RoFOrg B
  ├── TARGET_ORG ──► RoFOrg C
  └── REPRESENTED_BY ──► RoleAssignments aus B und C

RoFOrgRelationship: B und D
  ├── type = PARTNERSHIP
  ├── SOURCE_ORG ──► RoFOrg B
  ├── TARGET_ORG ──► RoFOrg D
  └── REPRESENTED_BY ──► RoleAssignments aus B und D
```

Alle vier Unternehmen bleiben eigenständig handlungsfähig und behalten ihre jeweils eigenen Teams, Mitglieder und Rollen. Die Organisationsbeziehungen führen nicht dazu, dass ihre weiteren Modellkontexte automatisch zusammengeführt werden; die Beziehungstypen beschreiben ausschließlich ihre Stellung zueinander.

---

## 11. Environment of Roles or Functions – ERoF

### 11.1 Bedeutung

`ERoF` steht für **Environment of Roles or Functions** und bezeichnet den fachlichen Modellraum der relevanten Umwelt. Er umfasst die Systeme, Werkzeuge, Dokumente, Daten, Infrastrukturen, Standards, Regelwerke, Organisationsbeziehungen und weiteren Umweltbestandteile, mit denen Rollen bei ihrer Arbeit interagieren.

`ERoF` ist eines der zehn fachlichen JCI-Kernelemente, wird aber nicht als eigener Knoten gespeichert. Der ERoF-Modellraum wird aus konkreten `ERoFObjects`, `RoFOrgRelationships` und ihrer Verwendung durch handelnde `RoleAssignments` abgeleitet. Eine andere Organisation bleibt eine eigenständige `RoFOrg`. Ihre Bedeutung als relevante Umwelt entsteht durch eine `RoFOrgRelationship`; die Organisation wird nicht zusätzlich als `ERoFObject` gespeichert.

Beispiel:

```text
RoleAssignment: Anna als Developer
  ├── USES ──► ERoFObject: Repository
  └── USES ──► ERoFObject: API

ERoF von Anna
= Repository + API
```

Der ERoF-Modellraum ist damit fachlich vorhanden, ohne dass ein zusätzlicher `ERoF`-Knoten angelegt wird.

Aus Sicht einer Mutterorganisation ist ihre Tochterorganisation über eine aktive `RoFOrgRelationship` mit `type = SUBSIDIARY` als Bestandteil der relevanten `ERoF` erkennbar. Die Zuordnung wird aus der Mutter als `SOURCE_ORG` und der Tochter als `TARGET_ORG` abgeleitet:

```text
ERoF der RoFOrg: Mutter
  └── umfasst ──► RoFOrgRelationship: SUBSIDIARY
                       ├── SOURCE_ORG ──► RoFOrg: Mutter
                       └── TARGET_ORG ──► RoFOrg: Tochter
```

Die Tochterorganisation bleibt dabei ausschließlich eine eigenständige `RoFOrg`. Sie wird nicht zusätzlich als `ERoFObject` gespeichert. Nur konkrete Gegenstände der Mutter-Tochter-Beziehung, beispielsweise ein Vertrag, ein gemeinsames System oder ein Datenraum, können als eigene `ERoFObjects` modelliert werden.

### 11.2 Entstehung

Ein `ERoFObject` entsteht, wenn ein konkreter Umweltbestandteil für die Arbeit im JCI-Modell relevant wird. Das Objekt wird nach seinem fachlichen Typ beschrieben. Ob es aus Sicht einer Organisation intern oder extern ist, wird nicht absolut am Objekt gespeichert, sondern aus Eigentum und Organisationsperspektive abgeleitet.

Beispiele für mögliche Typen sind:

```text
SYSTEM, APPLICATION, DATA, DOCUMENT, TOOL,
FACILITY, CONTRACT, SERVICE, OTHER
```

Besitzt eine Organisation das Objekt über `OWNED_BY`, ist es aus ihrer Sicht intern. Wird es von Rollen dieser Organisation verwendet, ohne dass diese Organisation zu den Eigentümern gehört, ist es aus ihrer Sicht extern. Gemeinsames Eigentum mehrerer Organisationen ist zulässig.

Ein aktives `ERoFObject` wird mindestens einem `RoleAssignment` zugeordnet. Dadurch ist jede Umweltinteraktion mit einem Mitglied, einem Team und einer dort aktivierten Rolle verbunden.

Eine `RoFOrgRelationship` vom Typ `PARTNERSHIP` gehört zur ERoF-Perspektive beider beteiligter Organisationen. Eine `SUBSIDIARY`-Beziehung beschreibt strukturell ihre RoF-Einordnung und zugleich die für Mutter und Tochter relevante Umweltbeziehung. Die konkrete Interaktion wird in beiden Fällen über `REPRESENTED_BY` an `RoleAssignments` der beteiligten Organisationen gebunden.

Wird ein `ERoFObject` oder seine Verwendung geändert, prüft `SYNC` die betroffenen `RoleAssignments`, Tasks, Teams, Regeln und abhängigen Elemente. Tatsächlich abgelöste Zustände werden als eigene `PiH` festgehalten.

### 11.3 Objekte und Beziehungen

| Begriff oder Graphobjekt | Bedeutung                                                                               |
| ------------------------ | --------------------------------------------------------------------------------------- |
| `ERoF`                   | Fachlicher und abgeleiteter Modellraum ohne eigenen Knoten.                             |
| `ERoFObject`             | Konkret gespeichertes Umweltobjekt.                                                     |
| `RoFOrgRelationship`     | Umweltbezogene oder strukturelle Beziehung zwischen zwei eigenständigen Organisationen. |
| `RoleAssignment`         | Aktive Rolle eines Mitglieds in einem Team.                                             |
| `Task`                   | Tätigkeit, die ein Umweltobjekt unmittelbar verwenden kann.                             |
| `RoFTeamMember`          | Mitglied, dessen Umwelt über Rollenaktivierungen ableitbar ist.                         |
| `RoFTeam`                | Team, dessen Umwelt aus seinen Mitgliedern abgeleitet wird.                             |
| `RoFOrg`                 | Organisation, deren Umwelt aus ihren Teams abgeleitet wird.                             |

#### Gespeicherte Beziehungen

| Quelle           | Beziehung | Ziel         |  Ziele je Quelle |  Quellen je Ziel |
| ---------------- | --------- | ------------ | ---------------: | ---------------: |
| `RoleAssignment` | `USES`    | `ERoFObject` |           `0..n` |           `1..n` |
| `Task`           | `USES`    | `ERoFObject` |           `0..n` |           `0..n` |
| `ERoFObject`     | `OWNED_BY`| `RoFOrg`     |           `0..n` |           `0..n` |

| Quelle                   | Beziehung         | Ziel              |  Ziele je Quelle |  Quellen je Ziel |
| ------------------------ | ----------------- | ----------------- | ---------------: | ---------------: |
| `RoFOrgRelationship`     | `SOURCE_ORG`      | `RoFOrg`          |              `1` |           `0..n` |
| `RoFOrgRelationship`     | `TARGET_ORG`      | `RoFOrg`          |              `1` |           `0..n` |
| `RoFOrgRelationship`     | `REPRESENTED_BY`  | `RoleAssignment`  |           `2..n` |           `0..n` |

```text
Task ── EXECUTED_BY ──► RoleAssignment ── USES ──► ERoFObject
  └──────────────────────── USES ───────────────────────►
```

#### Abgeleitete Umweltzuordnungen – nicht gespeichert

| Ausgangspunkt    | Ableitung                                               | Ziel         |
| ---------------- | ------------------------------------------------------- | ------------ |
| `RoFTeamMember`  | über seine `RoleAssignments`                            | `ERoFObject` |
| `RoFTeam`        | über Mitglieder und deren `RoleAssignments`             | `ERoFObject` |
| `RoFOrg`         | über Teams, Mitglieder und deren `RoleAssignments`      | `ERoFObject` |

```text
ERoF(RoFTeamMember)
= alle ERoFObjects seiner RoleAssignments

ERoF(RoFTeam)
= Vereinigung der ERoFObjects seiner Mitglieder in diesem Team

ERoF(RoFOrg)
= Vereinigung der ERoFObjects aller Mitglieder aller Teams der Organisation
  sowie ihrer aktiven RoFOrgRelationships
```

### 11.4 Regeln und Ausnahme

1. `ERoF` ist die fachliche Kategorie; konkrete Umweltobjekte werden als `ERoFObject` gespeichert.
2. Jedes aktive `ERoFObject` muss von mindestens einem `RoleAssignment` verwendet werden.
3. Ein `RoleAssignment` kann kein, ein oder mehrere `ERoFObjects` verwenden.
4. Ein `ERoFObject` kann von mehreren `RoleAssignments` gemeinsam verwendet werden.
5. Die Umwelt eines Mitglieds, Teams oder einer Organisation wird aus den personengebundenen Rollenaktivierungen abgeleitet.
6. Direkte Umweltbeziehungen von `RoFOrg`, `RoFTeam` oder `RoFTeamMember` werden nicht als Ersatz für diese Ableitung gespeichert.
7. Ein atomarer Task darf ein `ERoFObject` direkt verwenden, wenn mindestens ein den Task ausführendes `RoleAssignment` dasselbe Umweltobjekt verwendet. Ein zusammengesetzter Task besitzt keine direkte Umweltverwendung.
8. Eine direkte Task-Beziehung präzisiert den arbeitsbezogenen Umweltkontext, ersetzt aber niemals die Zuordnung zu einer handelnden Person.
9. Auch ein organisationsweit relevantes Umweltobjekt benötigt mindestens ein zuständiges Mitglied mit einem passenden `RoleAssignment`.
10. `RaN` kann die Verwendung eines `ERoFObject` regeln. Bei Regelkonflikten meldet `SYNC` den Konflikt, ohne ihn stillschweigend aufzulösen.
11. Eine Mutter-, Tochter- oder Partnerorganisation bleibt ausschließlich eine eigenständige `RoFOrg` und wird nicht als `ERoFObject` dupliziert.
12. Eine aktive `RoFOrgRelationship` gehört zur ERoF-Perspektive beider beteiligter Organisationen und wird durch mindestens ein `RoleAssignment` jeder Seite getragen.
13. Verträge, gemeinsame Systeme, Datenräume, Richtlinien oder andere Gegenstände einer Organisationsbeziehung können zusätzlich als eigene `ERoFObjects` modelliert werden.
14. `INTERNAL` und `EXTERNAL` werden immer für eine betrachtete `RoFOrg` abgeleitet: `INTERNAL`, wenn eine `OWNED_BY`-Beziehung zu dieser Organisation besteht, andernfalls `EXTERNAL`.
15. Ein `ERoFObject` darf keine Eigentümerbeziehung besitzen, wenn der Eigentümer außerhalb des modellierten Organisationsgraphen liegt. Es bleibt dann für verwendende modellierte Organisationen extern; der externe Eigentümer kann über `externalReference` dokumentiert werden.
16. `OWNED_BY` ersetzt keine `USES`-Beziehung. Eigentum allein belegt keine tatsächliche Umweltinteraktion.

**Kurzes Beispiel:** Eine gemeinsam betriebene Plattform verweist über `OWNED_BY` auf Organisation A und B. Für beide ist sie intern. Verwendet eine Rollenaktivierung aus Organisation C dieselbe Plattform, ist sie für C extern, obwohl nur ein `ERoFObject` gespeichert wird.

### 11.5 Beispiel

Anna arbeitet als `Developer` in Team A. Ihre aktive Rolle verwendet ein Repository und eine API. Ein konkreter Task verwendet dieselben Umweltobjekte:

```text
RoFTeamMember: Anna
  └── HAS_ASSIGNMENT ──► RoleAssignment: Developer in Team A
                              ├── USES ──► ERoFObject: Repository
                              └── USES ──► ERoFObject: API

Task: Schnittstelle erweitern
  ├── EXECUTED_BY ──► RoleAssignment: Developer in Team A
  ├── USES ─────────► ERoFObject: Repository
  └── USES ─────────► ERoFObject: API
```

Die Umwelt von Anna enthält Repository und API. Die Umwelt von Team A und der zugehörigen `RoFOrg` enthält diese Objekte ebenfalls, weil sie über Annas teambezogenes `RoleAssignment` ableitbar sind. Dafür werden keine zusätzlichen direkten Umweltbeziehungen zum Team oder zur Organisation gespeichert.

Steht Annas `RoFOrg` in einer Partnerschaft mit einer anderen `RoFOrg`, gehört die `RoFOrgRelationship` zur relevanten Umwelt beider Organisationen. Die Partnerorganisation bleibt eine `RoFOrg`. Ein gemeinsamer Vertrag, ein Datenaustauschsystem oder eine gemeinsam verwendete Plattform werden dagegen als `ERoFObjects` gespeichert und über die beteiligten `RoleAssignments` verwendet.

---

## 12. Synchronisation – SYNC

### 12.1 Bedeutung

`SYNC` ist die gespeicherte und historisierbare Definition der Synchronisationslogik des JCI-Modells. Sie legt fest, wie eine Änderung erkannt, entlang der gespeicherten Beziehungen auf Auswirkungen geprüft und bei einer tatsächlichen Zustandsänderung historisiert wird.

Ein `SyncEvent` ist davon klar getrennt: Es dokumentiert das unveränderliche Ergebnis eines abgeschlossenen oder kontrolliert abgebrochenen Synchronisationsversuchs. Über `EXECUTES` verweist es auf genau die SYNC-Definition, die dabei verwendet wurde. Während der Ausführung hält ein technischer `SyncRun` den veränderbaren Laufzustand. `SyncRun` gehört zur Implementierung und wird nicht als JCI-Knoten gespeichert.

```text
SYNC      = Welche Synchronisationslogik gilt?
SyncRun   = Was passiert technisch während der Ausführung?
SyncEvent = Wann und mit welchem Ergebnis wurde der Versuch abgeschlossen?
```

`SYNC` ist kein historischer Zustand. Wird die gespeicherte SYNC-Definition geändert, hält der dafür ausgeführte Synchronisationslauf ihren bisherigen Zustand als eigenes `PiH` fest. Die bloße Verwendung einer SYNC-Definition durch einen `SyncRun` und ihre Dokumentation im `SyncEvent` verändern die Definition dagegen nicht.

Eine `SyncDefinition` enthält mindestens:

```text
definitionSchemaVersion
ontologyVersion
graphRulesVersion
syncSpecVersion
supportedEntityTypes[]
supportedRelationshipTypes[]
handlerSetVersion
implementationReference
implementationChecksum
```

Die Versionsangaben bestimmen exakt, gegen welche Ontologie, Graphregeln und SYNC-Spezifikation geprüft wird. `implementationReference` bezeichnet das ausführbare Regelpaket oder Artefakt; `implementationChecksum` ist dessen SHA-256-Wert. Eine SYNC-Definition darf nur `ACTIVE` werden, wenn alle im Modell vorhandenen konkreten Entitäts- und Beziehungstypen unterstützt werden und der Prüfsummenvergleich erfolgreich ist.

**Kurzes Beispiel:** `SYNC 1.0` verweist auf Ontologie 1.0, Graphregeln 1.0 und das Handler-Paket `jci-sync-1.0` mit dessen Prüfsumme. Ein `SyncEvent` hält dadurch nicht nur „SYNC 1.0“, sondern die exakt ausgeführte Definition nachvollziehbar fest.

### 12.2 Entstehung

Ein Synchronisationsversuch entsteht aus einem angenommenen Veränderungsauftrag:

1. Der Auftrag wird vor seiner Ausführung als unveränderliches `ChangeEvent` erfasst. Das gilt für Änderungen vorhandener Entitäten, `CREATED` und `HISTORICAL_CORRECTION`.
2. Das `ChangeEvent` plant mindestens einen technischen `SyncRun` ein.
3. Der `SyncRun` verwendet genau eine gespeicherte SYNC-Definition.
4. Die verwendete `SYNC`-Definition ermittelt alle direkt und indirekt betroffenen Elemente und Beziehungen.
5. Sie prüft `RaN`, Kardinalitäten und weitere Modellbedingungen.
6. Sie bestimmt anwendbare `RaN`, prüft ihre Vereinbarkeit und wendet bei einem erkannten Widerspruch die ausdrücklich gespeicherte Priorität an. Gleichstand oder nicht auswertbare Semantik erzeugen einen offenen `RaNConflict`.
7. Sie unterscheidet zwischen lediglich betroffenen und tatsächlich zu ändernden Elementen.
8. Bei Task-Änderungen traversiert sie Parent-, Subtask- und Abhängigkeitsbeziehungen, ermittelt betroffene `PiF1o` und leitet Task-Status von den atomaren Tasks nach oben ab.
9. Bei einer abgeschlossenen `Verification` bestimmt sie die anwendbaren aktuellen Verifications, prüft deren gebundene Zielrevisionen und aggregiert alle `REQUIRED`-Kriterien des zugehörigen `PiF1o`.
10. Unmittelbar vor dem Commit prüft sie erneut, ob die von einer `Verification` gebundenen Revisionen von `Result` und `SuccessCriterion` noch aktuell sind.
11. Vor jeder tatsächlichen Änderung einer bereits vorhandenen historisierbaren Entität wird der bisherige Zustand als eigenes `PiH` vorbereitet.
12. Bei `SUCCESS` werden die angeforderte fachliche Änderung, zulässige Folgeänderungen, zugehörige `PiH`, Korrekturen, Konfliktauflösungen und Beziehungen gemeinsam atomar übernommen.
13. Bei `CONFLICT` oder `FAILED` werden die angeforderte fachliche Änderung und alle noch nicht übernommenen Folgeänderungen vollständig zurückgerollt. Dadurch entstehen aus einem nicht übernommenen Zustand weder eine neue Revision noch ein `PiH`.
14. Nach Abschluss oder kontrolliertem Abbruch wird genau ein unveränderliches `SyncEvent` mit eindeutiger `runId` erzeugt und die Beziehung `TRIGGERS` append-only ergänzt. Ein neu erkannter `RaNConflict` wird ebenfalls als Abschlussdokumentation festgehalten.
15. Das `SyncEvent` dokumentiert Beginn, Ende, Ergebnis, verwendete SYNC-Definition, geprüfte Elemente, tatsächlich übernommene Änderungen, erzeugte `PiH`, Korrekturen, Regelkonflikte und Fehler.

Die Atomarität bezieht sich auf die angeforderte fachliche Änderung und ihre zulässigen Folgeänderungen. Das abschließende `SyncEvent` und erforderliche Konfliktdokumente bilden dagegen die dauerhafte Dokumentation des Versuchs. Bei `SUCCESS` können Fachänderung und Abschlussdokumentation in derselben Transaktion gespeichert werden. Bei `CONFLICT` oder `FAILED` wird zuerst die fachliche Transaktion zurückgerollt und anschließend die Abschlussdokumentation dauerhaft gespeichert.

```text
Fachliche Transaktion
├── SUCCESS  → Änderung, Folgeänderungen und zugehörige PiH werden übernommen
├── CONFLICT → fachliche Änderungen werden nicht übernommen
└── FAILED   → fachliche Änderungen werden nicht übernommen

Abschlussdokumentation
└── jeder beendete oder kontrolliert abgebrochene SyncRun
    └── erzeugt genau ein unveränderliches SyncEvent
        └── dokumentiert bei Bedarf einen RaNConflict
```

Bei `changeType = CREATED` gibt es vor dem erfolgreichen Commit noch keine Quellentität für `CHANGED_BY`. Bei `SUCCESS` entstehen die neue Entität mit `revision = 1`, ihre Erstellungsprovenienz und genau eine `CHANGED_BY`-Beziehung gemeinsam. Bei `CONFLICT` oder `FAILED` bleiben Zielknoten, `CHANGED_BY` und Historie aus.

Bei einer festgestellten Abweichung in einem `PiH` verwendet `SYNC` denselben kontrollierten Ereignisrahmen, erzeugt aber keinen neuen historischen Zustand des `PiH`. Das `ChangeEvent` verweist über `TARGETS_HISTORY` auf genau dieses `PiH` und besitzt keine `CHANGED_BY`-Quelle. Nach erfolgreicher Prüfung erzeugt das `SyncEvent` stattdessen ein `HistoricalCorrection`-Objekt. Dessen `CORRECTS` verweist auf dasselbe unveränderte `PiH`.

```text
JCIEntity ── CHANGED_BY ──► ChangeEvent ── plant ──► SyncRun (technisch)
                                                         │
                                                         └── Abschluss/Abbruch ──► SyncEvent
                                                                                     ├── EXECUTES ──► SYNC
                                                                                     ├── AFFECTS ──► JCIEntity
                                                                                     └── CREATES_HISTORY ──► PiH

ChangeEvent:HISTORICAL_CORRECTION ── TARGETS_HISTORY ──► PiH
              │
              └── abgeschlossener SyncRun ──► SyncEvent
                                                   └── CREATES_CORRECTION ──► HistoricalCorrection
                                                                                  └── CORRECTS ─────► dasselbe PiH
```

### 12.3 Objekte und Beziehungen

| Objekt                 | Bedeutung                                                              |
| ---------------------- | ---------------------------------------------------------------------- |
| `SYNC`                 | Gespeicherte und historisierbare Definition der Synchronisationslogik. |
| `ChangeEvent`          | Dokumentiert Anlass, Art und Ausgangspunkt einer Änderung.             |
| `SyncRun`              | Veränderbarer technischer Laufzustand; keine `JCIEntity`.              |
| `SyncEvent`            | Unveränderliches Ergebnis eines beendeten Synchronisationsversuchs.    |
| `PiH`                  | Bewahrt einen durch die Änderung abgelösten Zustand.                   |
| `HistoricalCorrection` | Berichtigt ein `PiH`, ohne dessen Inhalt zu verändern.                 |
| `RaN`                  | Liefert Regeln, Normen und Grenzen für die Prüfung.                    |
| `RaNConflict`          | Dokumentiert einen nicht automatisch entscheidbaren Regelkonflikt.    |
| `JCIEntity`            | Kann Ausgangspunkt, betroffene oder geänderte Entität sein.            |

| Quelle                      | Beziehung            | Ziel                   |  Ziele je Quelle |  Quellen je Ziel |
| --------------------------- | -------------------- | ---------------------- | ---------------: | ---------------: |
| historisierbare `JCIEntity` | `CHANGED_BY`         | `ChangeEvent`          |           `0..n` |           `0..1` |
| `ChangeEvent`               | `TRIGGERS`           | `SyncEvent`            |           `0..n` |              `1` |
| `ChangeEvent`               | `TARGETS_HISTORY`    | `PiH`                  |           `0..1` |           `0..n` |
| `SyncEvent`                 | `EXECUTES`           | `SYNC`                 |              `1` |           `0..n` |
| `SyncEvent`                 | `AFFECTS`            | `JCIEntity`            |           `0..n` |           `0..n` |
| `SyncEvent`                 | `CREATES_HISTORY`    | `PiH`                  |           `0..n` |              `1` |
| `SyncEvent`                 | `CREATES_CORRECTION` | `HistoricalCorrection` |           `0..n` |              `1` |
| `HistoricalCorrection`      | `CORRECTS`           | `PiH`                  |              `1` |           `0..n` |
| `HistoricalCorrection`      | `CAUSED_BY`          | `ChangeEvent`          |              `1` |           `0..n` |
| `HistoricalCorrection`      | `SUPERSEDES`         | `HistoricalCorrection` |           `0..1` |           `0..1` |
| `RaNConflict`               | `DETECTED_BY`        | `SyncEvent`            |              `1` |           `0..n` |
| `RaNConflict`               | `RESOLVED_THROUGH`   | `ChangeEvent`          |           `0..1` |           `0..n` |

```text
Die ausgeführte SYNC-Definition prüft abhängig vom geänderten Element insbesondere:

CiV und PiF2 bis PiF1o
RaN und geregelte Ziele
RoFOrg, RoFTeam, RoFTeamMember, RoFRole und RoleAssignment
RoFOrgRelationship mit beiden beteiligten RoFOrg und ihren vertretenden RoleAssignments
Task, SuccessCriterion, Result, Verification und Evidence
ERoFObject und seine personengebundenen Verwendungen
PiH und zugehörige HistoricalCorrections bei historischen Abweichungen
```

### 12.4 Regeln und Ausnahme

1. Jedes angenommene `ChangeEvent` plant mindestens einen technischen `SyncRun` ein.
2. Solange noch kein Versuch beendet wurde, besitzt das `ChangeEvent` noch kein `SyncEvent`; `TRIGGERS = 0` ist dann der korrekte Zwischenstand.
3. Jeder beendete oder kontrolliert abgebrochene `SyncRun` erzeugt genau ein unveränderliches `SyncEvent` und ergänzt genau eine `TRIGGERS`-Beziehung append-only.
4. Jedes `SyncEvent` gehört zu genau einem auslösenden `ChangeEvent`, besitzt eine eindeutige `runId` und verweist über `EXECUTES` auf genau die verwendete SYNC-Definition.
5. Eine SYNC-Definition kann von keinem, einem oder mehreren `SyncEvents` als verwendete Definition dokumentiert werden.
6. Ein `SyncEvent` mit `SUCCESS` oder `CONFLICT` benennt mindestens eine betroffene `JCIEntity`. Nur ein `FAILED`-Versuch, der vor erfolgreicher Zielauflösung endet, darf kein `AFFECTS`-Ziel besitzen.
7. Betroffenheit allein erzeugt kein `PiH`. Nur ein tatsächlich abgelöster Zustand wird historisiert.
8. Ein `SyncEvent` kann kein, ein oder mehrere `PiH` erzeugen. Jedes erzeugte `PiH` bleibt über `CREATES_HISTORY` mit genau diesem `SyncEvent` und über `HAS_HISTORICAL_STATE` mit seiner ursprünglichen `JCIEntity` verbunden.
9. Bei `changeType = CREATED` müssen die Ziel-ID noch frei und `requestedRevision = null` sein. Nur bei `SUCCESS` entstehen die neue Entität mit `revision = 1`, `CREATED_BY` und genau einer `CHANGED_BY`-Beziehung; ein `PiH` entsteht nicht. Bei `CONFLICT` oder `FAILED` entstehen weder Zielknoten noch `CHANGED_BY` oder Historie.
10. Die ausgeführte SYNC-Definition prüft alle für die Änderung relevanten `RaN` und Modellbedingungen.
11. Eindeutig ableitbare und zulässige Anpassungen können verarbeitet werden. Bei widersprüchlichen anwendbaren `RaN` entscheidet die größere `priority` ausschließlich den konkreten Widerspruch. Gleichstand oder nicht auswertbare Semantik erzeugen einen offenen `RaNConflict` und werden nicht stillschweigend aufgelöst.
12. `SYNC` ist die gespeicherte Prozessdefinition; `SyncRun` ist der veränderbare technische Laufzustand; `SyncEvent` ist die unveränderliche Abschlussdokumentation. Wird die SYNC-Definition selbst geändert, wird ihr bisheriger Zustand wie bei jeder anderen historisierbaren `JCIEntity` als `PiH` festgehalten.
13. Bei Änderungen einer `RoFOrgRelationship` prüft die ausgeführte SYNC-Definition beide beteiligten `RoFOrg`, die Gültigkeit ihrer vertretenden `RoleAssignments`, relevante `RaN`, verbundene `ERoFObjects` und bei `SUBSIDIARY` die Zyklusfreiheit der Organisationsstruktur.
14. Ein `ChangeEvent` für `HISTORICAL_CORRECTION` besitzt genau ein `TARGETS_HISTORY`, keine `CHANGED_BY`-Quelle und `requestedRevision = 1`. Das später über `CORRECTS` verbundene `PiH` muss mit diesem Ziel identisch sein.
15. Eine festgestellte historische Abweichung erzeugt nach erfolgreicher Prüfung ein `HistoricalCorrection`-Objekt und niemals ein neues `PiH` des bestehenden `PiH`.
16. Jedes durch einen Synchronisationslauf erzeugte `HistoricalCorrection` bleibt über `CREATES_CORRECTION` mit genau einem `SyncEvent`, über `CAUSED_BY` mit dessen auslösendem `ChangeEvent` und über `CORRECTS` mit genau einem unveränderten `PiH` verbunden.
17. Vor einer historischen Korrektur berechnet `SYNC` die wirksame `HistoryView`, vergleicht ihren Hash mit `expectedHistoryViewHash` und serialisiert den Commit je `PiH`. Ein veralteter Hash erzeugt `CONFLICT` und keine Korrektur.
18. Mehrere aktive Korrekturen desselben `PiH` dürfen nur disjunkte `correctedFields` besitzen. Eine überlappende Korrektur muss genau eine aktive Vorgängerkorrektur vollständig über `SUPERSEDES` ersetzen; unklare oder mehrfache Überlappungen erzeugen `CONFLICT`.
19. Eine Korrektur des aktuellen Modells wird getrennt von der historischen Korrektur verarbeitet und besitzt einen eigenen Veränderungsvorgang.
20. Ein `SyncEvent` wird erst erzeugt, wenn der technische Versuch abgeschlossen oder kontrolliert abgebrochen wurde und alle Pflichtangaben feststehen.
21. Ist die Speicherung des abschließenden `SyncEvent` vorübergehend technisch unmöglich, wird sie mit derselben `runId`, demselben `ChangeEvent` und derselben Idempotenzkennung nachgeholt.
22. Ein fehlgeschlagener Versuch erzeugt ein `SyncEvent` mit `outcome = FAILED`; unvollständige fachliche Änderungen dürfen nicht als aktueller Modellzustand verbleiben. Die nachgeholte Speicherung des Ereignisses darf die fehlgeschlagene Fachänderung nicht erneut ausführen.
23. Wiederholungen desselben Veränderungsauftrags müssen über die unveränderliche `idempotencyKey` erkannt werden. Jeder tatsächlich ausgeführte Versuch erhält eine eigene `runId` und ein eigenes `SyncEvent`, darf aber dieselbe fachliche Änderung nicht mehrfach übernehmen.
24. Eine neue `Verification` bindet über `evaluatedResultRevision` und `checkedCriterionRevision` genau die geprüften Revisionen. `SYNC` prüft diese Werte zunächst in einer konsistenten Sicht und unmittelbar vor dem Commit erneut.
25. Eine `Verification` ist nur anwendbar, wenn sie nicht ersetzt wurde und die aktuellen Revisionen ihres `Result` und `SuccessCriterion` weiterhin den gebundenen Revisionen entsprechen. Eine spätere Änderung eines Prüfziels macht die frühere Verification revisionsveraltet.
26. Bei einer neuen `Verification` prüft `SYNC` die `SUPERSEDES`-Kette, bestimmt alle anwendbaren aktuellen Verifications des Erfolgskriteriums und wertet dessen `evaluationMode` aus.
27. `SYNC` setzt ein `PiF1o` nur auf `ACHIEVED`, wenn mindestens ein verpflichtendes Kriterium vorhanden, jedes `REQUIRED`-Kriterium erfüllt, alle zugeordneten Tasks `COMPLETED`, alle Task-Abhängigkeiten erfüllt und keine Modell- oder `RaN`-Verletzung vorhanden ist. Optionale Kriterien blockieren den Übergang nicht.
28. Fehlende, revisionsveraltete oder nicht anwendbare Verifications, `INVALID`, `INCONCLUSIVE` oder ein Regelkonflikt verhindern die automatische Erreichung. `SYNC` meldet den Grund und ändert den Status nicht.
29. Bei Task-Änderungen prüft `SYNC` Task-Typ, Hierarchie, Parent, Subtasks, Voraussetzungen, abhängige Tasks und alle dadurch betroffenen `PiF1o`. Abgeleitete Task-Status werden von unten nach oben bestimmt und wie jede fachliche Änderung historisiert.
30. Ein offener `RaNConflict` blockiert alle automatischen Änderungen, deren Zulässigkeit von seiner Auflösung abhängt. Ein gelöster Konflikt bleibt mit dem erkennenden `SyncEvent`, dem auflösenden `ChangeEvent` und dem verantwortlichen `RoleAssignment` nachvollziehbar.

### 12.5 Beispiel

Ein operativer Zukunftszustand wird von 48 auf 24 Stunden Antwortzeit geändert:

```text
PiF1o: Antwort innerhalb von 48 Stunden
                  │
                  └── CHANGED_BY ──► ChangeEvent
                                          │
                                          └── startet ──► SyncRun (technisch)
                                                               │
                                                               └── Abschluss ──► SyncEvent
                                                                                     ├── EXECUTES ──► SYNC: JCI-Standardprozess 1.0
                                                                                     ├── AFFECTS ──► PiF1o
                                                                                     ├── AFFECTS ──► SuccessCriterion
                                                                                     ├── AFFECTS ──► Task
                                                                                     └── CREATES_HISTORY ──► PiH
```

Der technische `SyncRun` verwendet die SYNC-Definition `JCI-Standardprozess 1.0`. Diese prüft den `PiF1o`, seine Erfolgskriterien, Tasks, Verantwortung, Rollenaktivierungen und verwendeten `ERoFObjects`. Der bisherige PiF1o-Zustand wird als `PiH` festgehalten. Abhängige Elemente erhalten nur dann ein eigenes `PiH`, wenn ihr Zustand tatsächlich geändert wird. Erst nach dem atomaren Abschluss wird das unveränderliche `SyncEvent` erzeugt; es dokumentiert die verwendete Definition sowie alle Prüfungen, Änderungen und Konflikte.

---

### 12.6 Technologieunabhängiges Austauschformat

JCI verwendet UTF-8-kodierte JSON-Dokumente für Änderungsaufträge und SYNC-Ergebnisse. Die hier beschriebene, gegenüber Version 1.0 inkompatibel präzisierte Form besitzt `schemaVersion = "1.1"`. UUIDs werden als Zeichenketten, Zeitpunkte nach ISO 8601 mit Zeitzone und fachliche Werte als `TypedValue` übertragen.

Ein `JCIChangeRequest` enthält mindestens:

```text
schemaVersion
requestId
idempotencyKey
requestedAt
requestedRevision = null bei CREATED | Integer >= 1 bei allen anderen Typen
changeType
target = {id, entityType}
requestedByRoleAssignmentId
reason
```

Für alle Änderungstypen außer `HISTORICAL_CORRECTION` ist zusätzlich `operations[]` mit mindestens einer Operation verpflichtend. Eine Operation verwendet `op = ADD | REPLACE | REMOVE | CONNECT | DISCONNECT`. Eigenschaftsoperationen besitzen einen eindeutigen `path` und gegebenenfalls `value: TypedValue`. Beziehungsoperationen besitzen `relationshipType`, `direction`, `otherEntityId` und optional eine typisierte Property-Map. `CONNECT` und `DISCONNECT` dürfen ausschließlich Beziehungen aus dem kanonischen Katalog verwenden.

Für `changeType = HISTORICAL_CORRECTION` bezeichnet `target` genau das unveränderliche `PiH`, `requestedRevision` ist `1` und an die Stelle von `operations[]` tritt genau ein strukturiertes `historicalCorrection`-Objekt:

```text
historicalCorrection = {
  correctionType = ADDITION | CORRECTION | CLARIFICATION,
  reason,
  valueSchemaVersion,
  expectedHistoryViewHash,
  correctedFields[],
  previousValue,
  correctedValue
}
```

`correctedFields` enthält eindeutige, lexikografisch sortierte kanonische JSON-Pointer. `previousValue` und `correctedValue` sind `TypedValueMaps` mit genau derselben Schlüsselmenge. `expectedHistoryViewHash` bindet den Auftrag an die wirksame historische Sicht, die vor dem Commit erneut geprüft wird. Eine historische Korrektur darf keine generischen Operationen enthalten, weil das adressierte `PiH` selbst niemals verändert wird.

Beim Speichern wird `requestId` zur `ChangeEvent.id`, während `idempotencyKey`, Ziel-ID, Zieltyp und `requestedRevision` unverändert in das `ChangeEvent` übernommen werden. Dadurch bleibt auch ein gescheiterter oder noch nicht abgeschlossener Auftrag eindeutig adressierbar.

Ein `JCISyncResult` enthält mindestens:

```text
schemaVersion
requestId
runId
syncEventId
outcome = SUCCESS | CONFLICT | FAILED
completedAt
affectedCount
changedCount
historyCount
correctionCount
conflictCount
affectedEntityIds[]
conflictIds[]
errors[]
```

Transportreferenzen wie `requestedByRoleAssignmentId` werden beim Speichern in die kanonische Beziehung `REQUESTED_BY` überführt und nicht als zusätzliches Fachfeld am Knoten behalten. Das JSON-Dokument bleibt als Eingabenachweis über ein `Evidence` referenzierbar.

Für `JCISyncResult` gilt: Bei `SUCCESS` oder `CONFLICT` ist `affectedCount >= 1`. Nur ein `FAILED`-Ergebnis, dessen Lauf vor erfolgreicher Zielauflösung endet, darf `affectedCount = 0` und eine leere `affectedEntityIds`-Liste besitzen. Die Zähler müssen jeweils exakt der Länge beziehungsweise der Zahl der im Graphen erzeugten Beziehungen und Objekte entsprechen.

Vollständige Graph- oder Ontologieexporte verwenden JSON-LD 1.1. Jede Entität besitzt `@id = "urn:jci:<UUID>"` und ihren konkreten Typ in `@type`. Beziehungen verwenden ausschließlich die kanonischen Beziehungsnamen; Beziehungseigenschaften werden als eigenständige JSON-LD-Beziehungsobjekte übertragen. Der Export enthält die verwendeten Versionen von Kontext, Ontologie und Graphregeln.

Die verbindlichen maschinenlesbaren Schemas liegen unter `docs/schemas/`.

**Kurzes Beispiel:** Eine Änderung der Task-Bezeichnung wird als `REPLACE` auf dem Pfad `/name` übertragen. Die Rollen-ID im Transport wird zu `REQUESTED_BY`; nach erfolgreicher Verarbeitung nennt das Ergebnis das erzeugte `SyncEvent` und den historischen Zustand des vorherigen Task-Namens.

### 12.7 Initialer Bootstrap

Der initiale Bootstrap löst ausschließlich das Vertrauenswurzelproblem eines vollständig leeren Graphen. Er ist kein normaler Veränderungsauftrag und darf genau einmal in einer atomaren Transaktion ausgeführt werden.

Der Bootstrap erzeugt mindestens:

```text
RoFOrg
└── RoFTeam
    └── technisches RoFTeamMember
        ├── RoFRole
        └── RoleAssignment mit bootstrapKey = "ROOT"

aktive SYNC-Definition
```

Alle erforderlichen RoF-Beziehungen werden in derselben Transaktion angelegt. Die sechs Bootstrap-Entitäten `RoFOrg`, `RoFTeam`, technisches `RoFTeamMember`, `RoFRole`, Root-`RoleAssignment` und `SYNC` werden unmittelbar mit `status = ACTIVE`, `revision = 1` sowie demselben Wert für `createdAt` und `updatedAt` erzeugt. Wo der konkrete Typ oder eine Bootstrap-Beziehung `validFrom` besitzt, entspricht auch dieser Wert demselben Bootstrapzeitpunkt. Dies ist die einzige Ausnahme von der Regel, dass veränderliche Fachentitäten zunächst als `DRAFT` entstehen: Ohne aktive Organisation, Rolle, Rollenaktivierung und SYNC-Definition könnte die Vertrauenswurzel keinen ersten regulären Auftrag ausführen.

Nur dieses eine Root-`RoleAssignment` darf dauerhaft ohne `CREATED_BY` bestehen, weil vor ihm noch kein handelnder Akteur existiert. Alle weiteren Bootstrap-Entitäten verweisen mit `CREATED_BY` auf das Root-`RoleAssignment`. Für den Bootstrap entstehen weder `ChangeEvent`, technischer `SyncRun`, `SyncEvent` noch `PiH`.

Der Bootstrap ist nur zulässig, wenn noch keine `JCIEntity` vorhanden ist. Die Eindeutigkeit von `bootstrapKey = "ROOT"`, die Vollständigkeit des Minimalgraphen und die Aktivierbarkeit der SYNC-Definition werden vor dem Commit geprüft. Bei einem Fehler wird die gesamte Transaktion zurückgerollt; ein unvollständiger Bootstrap darf nicht sichtbar bleiben. Nach erfolgreichem Commit sind Wiederholung und ein zweites Root-`RoleAssignment` verboten und alle weiteren Änderungen laufen ausschließlich über den normalen SYNC-Prozess.

Ein Datenimport ist kein Bootstrap. Importierte Entitäten ohne belegbare Erstellungsprovenienz bleiben `DRAFT`, bis ein regulärer, durch ein `RoleAssignment` angeforderter Synchronisationslauf ihre Provenienz und Modellgültigkeit bestätigt.

**Kurzes Beispiel:** In einer leeren Datenbank legt das Deployment einmalig die Organisation „Junaco“, ein technisches Administrationsteam, ein technisches Mitglied, seine Administrationsrolle, das Root-`RoleAssignment` und die aktive SYNC-Definition gemeinsam an. Erst danach kann dieses Root-`RoleAssignment` einen normalen `CREATED`-Auftrag für die erste fachliche Entität stellen.

## 13. Abschluss

Der JUNACO Continuous Integration Loop verbindet Zweck, Zukunft, Verantwortung, Arbeit, Umwelt, Regeln, Prüfung und historische Entwicklung in einem gemeinsamen fachlichen Graphen.

`JCIEntity` bildet den abstrakten Oberbegriff aller gespeicherten Instanzen. Acht der zehn Kernelemente besitzen eigene gespeicherte `JCIElementInstances`. `RoF` und `ERoF` bleiben fachliche Modellräume ohne eigenen Knoten und werden durch ihre konkreten Graphobjekte und Beziehungen sichtbar. `PiH`, `ChangeEvent`, `SyncEvent` und `HistoricalCorrection` bleiben inhaltlich unveränderlich und werden nicht erneut historisiert. Nur klar definierte Provenienzbeziehungen werden beim erfolgreichen Anlegen beziehungsweise beim Abschluss eines technischen Laufs append-only ergänzt.

`CiV` begründet, warum eine Zukunft gewollt ist. `PiF2` bis `PiF1o` beschreiben diese Zukunft auf langfristiger, strategischer, taktischer und operativer Ebene. Die gespeicherten `CONTRIBUTES_TO`-Beziehungen führen dabei vom konkreteren zum übergeordneten Zukunftszustand und erlauben einen gerichteten `n:m`-Graphen.

Ein `PiF1o` beschreibt einen erreichbaren operativen Zustand. Er besitzt mindestens ein verpflichtendes Erfolgskriterium und genau ein verantwortliches `RoFTeamMember`. Zusammengesetzte Tasks strukturieren die Arbeit; atomare Tasks werden über teambezogene `RoleAssignments` ausgeführt, verwenden konkrete `ERoFObjects` und können `Results` erzeugen. Task-Abhängigkeiten bestimmen die zulässige Ausführungsreihenfolge. Anwendbare aktuelle `Verifications` bewerten dabei ausdrücklich gebundene Revisionen von Ergebnissen und Erfolgskriterien. Erst wenn alle `REQUIRED`-Kriterien erfüllt, alle Tasks abgeschlossen und alle Abhängigkeiten erfüllt sind, darf `SYNC` den terminalen Status `ACHIEVED` setzen.

Der RoF-Modellraum stellt den Organisations-, Team-, Mitglieder- und Rollenkontext bereit. Mutter-, Tochter- und Partnerunternehmen bleiben jeweils eigenständige `RoFOrg`; ihre Stellung zueinander wird durch eine personengebundene `RoFOrgRelationship` beschrieben. `SUBSIDIARY` kann rekursive, aber zyklusfreie Mutter-Tochter-Strukturen bilden. `PARTNERSHIP` verbindet unabhängige Organisationen und gehört zur ERoF-Perspektive beider Seiten. Der ERoF-Modellraum beschreibt darüber hinaus die relevante Umwelt, wobei konkrete Umweltinteraktionen immer über handelnde Rollenaktivierungen nachvollziehbar bleiben. `RaN` wirkt als regelnder Querschnitt auf die jeweils geregelten Zukunfts-, Arbeits-, Organisations-, Rollen- und Umweltbereiche. Bei einem tatsächlichen Regelwiderspruch hat die größere ausdrücklich gespeicherte Priorität Vorrang; Gleichstände und nicht auswertbare Semantik bleiben als `RaNConflict` bis zu einer menschlich veranlassten und durch `SYNC` bestätigten Auflösung nachvollziehbar.

`SYNC` ist die gespeicherte Definition der Synchronisationslogik. Ein angenommenes `ChangeEvent` plant mindestens einen technischen `SyncRun`; bis zum Abschluss des ersten Versuchs darf es noch kein `SyncEvent` besitzen. Erst Abschluss oder kontrollierter Abbruch erzeugen ein unveränderliches `SyncEvent` mit eigener `runId`, das über `EXECUTES` auf die verwendete SYNC-Definition verweist. Nur wenn ein vorhandener Zustand tatsächlich abgelöst wird, hält der Synchronisationslauf diesen bisherigen Zustand als eigenes `PiH` fest. Betroffenheit allein erzeugt keinen historischen Zustand; Konflikte werden gemeldet und nicht stillschweigend aufgelöst. Eine später festgestellte Abweichung in einem `PiH` wird über `TARGETS_HISTORY` adressiert und als unveränderliches `HistoricalCorrection`-Objekt ergänzt. Das ursprüngliche `PiH` bleibt unverändert, und eine daraus folgende Änderung am aktuellen Modell wird getrennt verarbeitet. Der einmalige atomare Bootstrap schafft in einem leeren Graphen ausschließlich die Vertrauenswurzel; danach gilt ausnahmslos der normale SYNC-Prozess.

```text
PiH ── PROVIDES_CONTEXT_TO ──► CiV ── INSCRIBES_PURPOSE_IN ──► PiF2
                                                                     ▲
PiF1o ── CONTRIBUTES_TO ──► PiF1t ── CONTRIBUTES_TO ──► PiF1s ─────┘
  │
  ├── HAS_SUCCESS_CRITERIA ──► SuccessCriterion
  ├── ACCOUNTABLE_MEMBER ────► RoFTeamMember
  └── DECOMPOSES_INTO ───────► COMPOSITE Task
                                   └── DECOMPOSES_INTO ──► ATOMIC Task
                                                                  ├── DEPENDS_ON ──► Task
                                                                  ├── EXECUTED_BY ──► RoleAssignment
                                                                  ├── USES ──► ERoFObject
                                                                  └── PRODUCES ──► Result ◄── EVALUATES ── Verification
                                                                                                             └── CHECKS ──► SuccessCriterion

RaN ── GOVERNS ──► relevante Ziele
RaNConflict ── CONFLICTING_RULE ──► RaN
      ├── DETECTED_BY ──► SyncEvent
      └── RESOLVED_BY ──► RoleAssignment
RoFOrg ◄── SOURCE_ORG ── RoFOrgRelationship ── TARGET_ORG ──► RoFOrg
                              └── REPRESENTED_BY ──► RoleAssignment
ChangeEvent ── TRIGGERS ──► SyncEvent ── AFFECTS ──► JCIEntity
                                      ├── EXECUTES ──► SYNC
                                      └── CREATES_HISTORY ──► PiH

ChangeEvent:HISTORICAL_CORRECTION ── TARGETS_HISTORY ──► PiH
SyncEvent ── CREATES_CORRECTION ──► HistoricalCorrection ── CORRECTS ──► dasselbe PiH
                                                └── SUPERSEDES ──► frühere HistoricalCorrection
```

Damit bleibt von einem konkreten Task rückwärts nachvollziehbar, welchem operativen Zustand, welchem Zukunftszusammenhang und welchem wertbezogenen Zweck er dient. Gleichzeitig bleiben Verantwortung, Umweltbezug, Regeln, Prüfergebnisse und abgelöste Zustände eindeutig zugeordnet. Diese durchgängige Nachvollziehbarkeit bildet den Kern des JCI Loops.
