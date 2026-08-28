# JCI-Kontext
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
| `PiF1t`     | ab 1 Jahr bis einschließlich 5 Jahre    |
| `PiF1s`     | mehr als 5 bis einschließlich 10 Jahre |
| `PiF2`      | mehr als 10 Jahre bis zu `n` Jahren      |

`n` bezeichnet einen offenen, nicht fest begrenzten langfristigen Zeithorizont.

### 2.2 Abgrenzung der Kernelemente von den Graphobjekten

Das JCI besteht aus genau zehn Kernelementen:

```text
PiH, CiV, RaN, RoF, ERoF, SYNC,
PiF2, PiF1s, PiF1t und PiF1o
```

Für die konkrete Anwendung und Speicherung im Graphen werden zusätzliche Graphobjekte benötigt. Sie machen die Kernelemente ausführbar, prüfbar und nachvollziehbar, sind aber keine weiteren JCI-Kernelemente.

| Bereich              | Graphobjekt        | Bedeutung                                   |
| -------------------- | ------------------ | ------------------------------------------- |
| Organisation         | `RoFOrg`           | Organisation der operativen Arbeit          |
| Organisation         | `RoFTeam`          | organisatorische oder funktionale Gruppe    |
| Organisation         | `RoFTeamMember`    | menschlicher oder technischer Akteur         |
| Rollen               | `RoFRole`          | Rolle, Funktion und Verantwortung            |
| Rollen               | `RoleAssignment`   | aktive Rolle eines Mitglieds in einem Team   |
| Operative Umsetzung  | `Task`             | Tätigkeit zur Realisierung eines `PiF1o`    |
| Erfolg und Prüfung  | `SuccessCriterion` | erwartetes Erfolgskriterium                  |
| Erfolg und Prüfung  | `Result`           | durch einen Task erzeugtes Ergebnis          |
| Erfolg und Prüfung  | `Verification`     | Prüfung eines Ergebnisses                  |
| Erfolg und Prüfung  | `Evidence`         | eigenständiger prüfbarer Nachweis        |
| Umwelt               | `ERoFObject`       | konkretes Objekt der relevanten Umwelt       |
| Veränderung         | `ChangeEvent`      | dokumentierter Auslöser einer Änderung   |
| Veränderung         | `SyncEvent`        | dokumentierter Synchronisationslauf          |

Die Kernelemente beschreiben die grundlegende fachliche Struktur des JCI. Die zusätzlichen Graphobjekte bilden konkrete Organisationen, Personen, Rollen, Tätigkeiten, Umweltobjekte, Ergebnisse, Prüfungen und Veränderungen innerhalb dieser Struktur ab.

### 2.3 Grundstruktur

Die vereinfachte Grundstruktur des JCI-Modells ist:

```text
                         RaN
                          │ regelt und begrenzt
                          ▼
PiH → CiV → PiF2 → PiF1s → PiF1t → PiF1o → Task → Result ← Verification
                                                │
                                                ├── wird durch RoleAssignments ausgeführt
                                                └── interagiert mit ERoFObjects (ERoF)

JCI-Element → ChangeEvent → SYNC → betroffene JCI-Elemente
      │
      └── bisheriger Zustand → PiH
```

**Kurzes Beispiel:** Eine Organisation möchte ihren Kundenservice verbessern. Aus ihren Werten (`CiV`) entsteht ein langfristiges Zukunftsbild (`PiF2`), das über strategische (`PiF1s`) und taktische Zukunftszustände (`PiF1t`) zu einem konkreten operativen Zielzustand (`PiF1o`) führt. Ein verantwortliches Teammitglied setzt diesen durch Tasks um. Dabei arbeitet es in seiner Rolle (`RoF`) mit Systemen und Informationen aus der Umwelt (`ERoF`). Regeln und Normen (`RaN`) geben den zulässigen Rahmen vor. Die erzeugten Ergebnisse werden anhand festgelegter Erfolgskriterien geprüft. Bei einer relevanten Änderung verfolgt `SYNC` die Auswirkungen. Der durch die Änderung abgelöste Zustand wird als eigener `PiH` festgehalten; danach gilt der neue Zustand als aktuell. Bei weiteren Änderungen entstehen weitere `PiH`, sodass die früheren Zustände in ihrer zeitlichen Reihenfolge nachvollziehbar bleiben.

Die Darstellung beschreibt eine Orientierung und keinen einzigen linearen Ablauf. `RaN`, `ERoF` und `SYNC` sind deshalb nicht als aufeinanderfolgende Stationen in die Zukunftskette eingefügt. Die tatsächlichen Beziehungen zwischen den JCI-Elementen bilden einen Graphen und können Verzweigungen sowie Rückbezüge enthalten.

### 2.4 Beziehungen zwischen JCI-Elementen

Die folgenden Tabellen zeigen die gespeicherten Beziehungen entlang der JCI-Kette und die daraus eindeutig abgeleiteten ERoF-Zuordnungen. Abgeleitete Beziehungen sind ausdrücklich gekennzeichnet und werden nicht als zusätzliche Kanten gespeichert.

#### 2.4.1 Zweck, Werte und Zukunft

Lesebeispiel für `PiF1s ── CONTRIBUTES_TO ──► PiF2`: **Ziele je Quelle `1..n`** bedeutet, dass ein `PiF1s` zu mindestens einem oder mehreren `PiF2` beitragen muss. **Quellen je Ziel `0..n`** bedeutet, dass zu einem `PiF2` vorübergehend noch kein, ein oder mehrere `PiF1s` beitragen können.

| Quelle    | Beziehung                 | Ziel      | Ziele je<br>Quelle | Quellen je<br>Ziel |
| --------- | ------------------------- | --------- | -----------------: | -----------------: |
| `PiH`     | `PROVIDES_CONTEXT_TO`     | `CiV`     | `0..n`             | `0..n`             |
| `CiV`     | `INSCRIBES_PURPOSE_IN`    | `PiF2`    | `0..n`             | `1..n`             |
| `PiF1s`   | `CONTRIBUTES_TO`          | `PiF2`    | `1..n`             | `0..n`             |
| `PiF1t`   | `CONTRIBUTES_TO`          | `PiF1s`   | `1..n`             | `0..n`             |
| `PiF1o`   | `CONTRIBUTES_TO`          | `PiF1t`   | `1..n`             | `0..n`             |

#### 2.4.2 Operative Umsetzung, Rollen und Umwelt

Lesebeispiel für `RoleAssignment ── USES ──► ERoFObject`: **Ziele je Quelle `0..n`** bedeutet, dass ein `RoleAssignment` vorübergehend noch kein, ein oder mehrere `ERoFObjects` verwenden kann. **Quellen je Ziel `1..n`** bedeutet, dass jedes aktive `ERoFObject` von mindestens einem oder mehreren `RoleAssignments` und damit personengebunden verwendet werden muss.

| Quelle             | Beziehung                 | Ziel                 | Ziele je<br>Quelle | Quellen je<br>Ziel |
| ------------------ | ------------------------- | -------------------- | -----------------: | -----------------: |
| `PiF1o`            | `HAS_SUCCESS_CRITERIA`    | `SuccessCriterion`   | `1..n`             | `1`                |
| `PiF1o`            | `ACCOUNTABLE_MEMBER`      | `RoFTeamMember`      | `1`                | `0..n`             |
| `PiF1o`            | `DECOMPOSES_INTO`         | `Task`               | `1..n`             | `1`                |
| `Task`             | `EXECUTED_BY`             | `RoleAssignment`     | `1..n`             | `0..n`             |
| `Task`             | `RESPONSIBLE_TEAM`        | `RoFTeam`            | `1`                | `0..n`             |
| `Task`             | `USES`                    | `ERoFObject`         | `0..n`             | `0..n`             |
| `RoleAssignment`   | `USES`                    | `ERoFObject`         | `0..n`             | `1..n`             |

#### 2.4.3 Abgeleitete ERoF-Zuordnungen

Lesebeispiel für die Ableitung `RoFOrg ── über Teams, Mitglieder und RoleAssignments ──► ERoFObject`: **Ziele je Quelle `0..n`** bedeutet, dass für eine `RoFOrg` kein, ein oder mehrere `ERoFObjects` aus den personengebundenen Umweltbeziehungen abgeleitet werden können. **Quellen je Ziel `1..n`** bedeutet, dass jedes aktive `ERoFObject` dadurch mindestens einer oder mehreren `RoFOrgs` zugeordnet werden kann, ohne eine direkte Beziehung zur Organisation zu speichern.

| Quelle            | Ableitung                                                 | Ziel           | Ziele je<br>Quelle | Quellen je<br>Ziel |
| ----------------- | --------------------------------------------------------- | -------------- | -----------------: | -----------------: |
| `RoFTeamMember`   | über seine `RoleAssignments`                              | `ERoFObject`   | `0..n`             | `1..n`             |
| `RoFTeam`         | über Mitglieder;<br>dann über `RoleAssignments`           | `ERoFObject`   | `0..n`             | `1..n`             |
| `RoFOrg`          | über Teams und Mitglieder;<br>dann über `RoleAssignments` | `ERoFObject`   | `0..n`             | `1..n`             |

#### 2.4.4 Ergebnisse und Prüfung

Lesebeispiel für `Verification ── EVALUATES ──► Result`: **Ziele je Quelle `1`** bedeutet, dass jede `Verification` genau ein `Result` bewertet. **Quellen je Ziel `0..n`** bedeutet, dass ein `Result` noch durch keine, durch eine oder durch mehrere `Verifications` bewertet werden kann.

| Quelle           | Beziehung          | Ziel                 | Ziele je<br>Quelle | Quellen je<br>Ziel |
| ---------------- | ------------------ | -------------------- | -----------------: | -----------------: |
| `Task`           | `PRODUCES`         | `Result`             | `0..n`             | `1`                |
| `Verification`   | `EVALUATES`        | `Result`             | `1`                | `0..n`             |
| `Verification`   | `CHECKS`           | `SuccessCriterion`   | `1`                | `0..n`             |
| `Verification`   | `USES_EVIDENCE`    | `Evidence`           | `0..n`             | `0..n`             |

#### 2.4.5 Veränderung

Lesebeispiel für `ChangeEvent ── TRIGGERS ──► SyncEvent`: **Ziele je Quelle `1..n`** bedeutet, dass jedes `ChangeEvent` mindestens einen und möglicherweise mehrere Synchronisationsläufe auslöst. **Quellen je Ziel `1`** bedeutet, dass jedes `SyncEvent` genau durch ein `ChangeEvent` ausgelöst wird.

| Quelle          | Beziehung      | Ziel          | Ziele je<br>Quelle | Quellen je<br>Ziel |
| --------------- | -------------- | ------------- | -----------------: | -----------------: |
| `ChangeEvent`   | `TRIGGERS`     | `SyncEvent`   | `1..n`             | `1`                |
| `SyncEvent`     | `AFFECTS`      | JCI-Element   | `1..n`             | `0..n`             |

#### 2.4.6 Historisierung

Lesebeispiel für `JCI-Element ── HAS_HISTORICAL_STATE ──► PiH`: **Ziele je Quelle `0..n`** bedeutet, dass ein aktuelles JCI-Element noch keinen, einen oder mehrere frühere Zustände als `PiH` besitzen kann. **Quellen je Ziel `1`** bedeutet, dass jedes `PiH` den abgelösten Zustand genau eines JCI-Elements festhält.

| Quelle          | Beziehung                  | Ziel    | Ziele je<br>Quelle | Quellen je<br>Ziel |
| --------------- | -------------------------- | ------- | -----------------: | -----------------: |
| JCI-Element     | `HAS_HISTORICAL_STATE`     | `PiH`   | `0..n`             | `1`                |
| `ChangeEvent`   | `RECORDED_IN`              | `PiH`   | `1`                | `0..n`             |
| `SyncEvent`     | `RECORDED_IN`              | `PiH`   | `1`                | `0..n`             |

##### 2.4.6.1 Ablauf von Veränderung und Historisierung

Die Änderung eines JCI-Elements wird als `ChangeEvent` erkannt und dokumentiert. Jedes `ChangeEvent` löst mindestens ein `SyncEvent` aus. `SYNC` ermittelt die betroffenen JCI-Elemente und prüft, welcher bestehende Zustand durch die Änderung abgelöst wird.

Bevor der neue Zustand übernommen wird, hält `SYNC` den bisherigen Zustand des betroffenen Elements einschließlich seiner zu diesem Zeitpunkt gültigen Beziehungen als eigenes `PiH` fest. Anschließend gilt der geänderte Zustand als aktueller Zustand. Ein zusätzlicher `HistoricalSnapshot` ist nicht erforderlich.

```text
aktueller Zustand → ChangeEvent → SYNC → neuer aktueller Zustand
       │                         │
       └─ bisheriger Zustand ──┘
                    │
                    └──► PiH
```

Beim erstmaligen Anlegen eines Elements existiert noch kein vorheriger Zustand. Deshalb erzeugt `ANGELEGT` noch kein `PiH` dieses Elements. Das Anlegen wird dennoch als `ChangeEvent` dokumentiert und durch `SYNC` verarbeitet.


## 3. Point in Historie - PiH

### 3.1 Bedeutung

`PiH` steht für **Point in Historie**. Ein `PiH` bewahrt den bisherigen Zustand eines JCI-Elements, wenn dieser durch eine Änderung abgelöst wird.

Das aktuelle JCI-Element wird nicht selbst zu `PiH`. `SYNC` hält unmittelbar vor der Übernahme einer Änderung ein eigenständiges historisches Abbild des bisherigen Zustands fest. Dieses bewahrt:

- Identität und Typ des ursprünglichen Elements,
- die bisherigen Eigenschaften,
- die zuvor gültigen Beziehungen und Verantwortlichkeiten,
- den Zeitpunkt der Historisierung als `recordedAt`,
- den Bezug zu `ChangeEvent` und `SyncEvent`.

### 3.2 Entstehung

1. Eine Änderung wird als `ChangeEvent` erfasst.
2. Das `ChangeEvent` löst mindestens ein `SyncEvent` aus.
3. `SYNC` ermittelt betroffene Elemente und Beziehungen.
4. `SYNC` prüft `RaN` und weitere Modellbedingungen.
5. `SYNC` hält den abgelösten Zustand als `PiH` fest.
6. Der geänderte Zustand wird zum aktuellen Zustand.
7. Das `SyncEvent` dokumentiert die Auswirkungen des Synchronisationslaufs.

```text
JCI-Element ── Änderung ──► ChangeEvent ── TRIGGERS ──► SyncEvent
      │                                                   │
      └── bisheriger Zustand ── durch SYNC ───────────────┘
                              │
                              └──► PiH
```

### 3.3 Objekte und Beziehungen

`ChangeEvent`, `SyncEvent` und `PiH` bleiben getrennte Graphobjekte:

| Objekt        | Bedeutung                                                      |
| ------------- | -------------------------------------------------------------- |
| `ChangeEvent` | Dokumentiert Anlass und Ursache der Änderung.                  |
| `SyncEvent`   | Dokumentiert den Synchronisationslauf und seine Auswirkungen. |
| `PiH`         | Bewahrt den durch die Änderung abgelösten Zustand.             |

Ein `SyncEvent` ist kein `PiH`. Es kann jedoch mehrere `PiH` erzeugen, wenn ein Synchronisationslauf mehrere bestehende Zustände ablöst.

| Quelle        | Beziehung              | Ziel          | Ziele je Quelle | Quellen je Ziel |
| ------------- | ---------------------- | ------------- | ---------------:| ---------------:|
| JCI-Element   | `CHANGED_BY`           | `ChangeEvent` | `0..n`          | `1`             |
| `ChangeEvent` | `TRIGGERS`             | `SyncEvent`   | `1..n`          | `1`             |
| `SyncEvent`   | `AFFECTS`              | JCI-Element   | `1..n`          | `0..n`          |
| JCI-Element   | `HAS_HISTORICAL_STATE` | `PiH`         | `0..n`          | `1`             |
| `SyncEvent`   | `CREATES_HISTORY`      | `PiH`         | `0..n`          | `1`             |

### 3.4 Regeln und Ausnahme

1. Ein `PiH` entsteht nur aus einem bereits vorhandenen Zustand.
2. Jeder durch eine Änderung abgelöste Zustand wird als eigenes `PiH` festgehalten.
3. Jedes `PiH` gehört zu genau einem ursprünglichen JCI-Element.
4. Ein JCI-Element kann mehrere zeitlich über `recordedAt` geordnete `PiH` besitzen.
5. `PiH` wird nicht erneut historisiert.
6. Bei `ANGELEGT` entsteht noch kein `PiH`, weil kein vorheriger Zustand existiert. Das `ChangeEvent` und mindestens ein `SyncEvent` entstehen trotzdem.

### 3.5 Beispiel

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

| Quelle | Beziehung                | Ziel   | Ziele je Quelle | Quellen je Ziel |
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

| Objekt  | Bedeutung                                      |
| ------- | ---------------------------------------------- |
| `CiV`   | Begründet den wertbezogenen Zweck des `PiF2`. |
| `PiF2`  | Beschreibt den langfristigen Zukunftszustand.  |
| `PiF1s` | Leistet einen strategischen Beitrag zum `PiF2`.|

| Quelle  | Beziehung               | Ziel   | Ziele je Quelle | Quellen je Ziel |
| ------- | ----------------------- | ------ | ---------------:| ---------------:|
| `CiV`   | `INSCRIBES_PURPOSE_IN` | `PiF2` | `0..n`          | `1..n`          |
| `PiF1s` | `CONTRIBUTES_TO`       | `PiF2` | `1..n`          | `0..n`          |

### 5.4 Regeln und Ausnahme

1. Jedes `PiF2` muss durch mindestens ein `CiV` wertbezogen begründet sein.
2. Ein `PiF2` kann Beiträge von keinem, einem oder mehreren `PiF1s` erhalten; `0..n` erlaubt einen noch nicht ausformulierten Entwurf.
3. Ein `PiF1s` muss zu mindestens einem `PiF2` beitragen und kann mehrere `PiF2` unterstützen.
4. `PiF2` beschreibt einen Zustand und keine Tätigkeit.
5. Eine Änderung an `PiF2` führt nicht automatisch zur Änderung aller verbundenen Elemente; `SYNC` prüft zunächst die Auswirkungen.

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

Ein `RaN` entsteht durch die ausdrückliche Formulierung einer fachlichen Regel, rechtlichen Vorgabe, internen Norm oder verbindlichen Grenze. Die Regel wird mit den Elementen verbunden, für die sie gilt.

Ein Entwurf darf zunächst ohne Ziel bestehen. Bevor ein `RaN` aktiv wird, muss es mindestens ein geregeltes Ziel besitzen. Wird ein bestehendes `RaN` geändert, prüft `SYNC` alle geregelten Ziele und davon abhängigen Elemente. Der abgelöste RaN-Zustand wird als `PiH` festgehalten.

### 6.3 Objekte und Beziehungen

| Bereich       | Mögliche Ziele                         |
| ------------- | -------------------------------------- |
| Zukunft       | `PiF2`, `PiF1s`, `PiF1t`, `PiF1o`      |
| Arbeit        | `Task`                                 |
| Organisation  | `RoFOrg`, `RoFTeam`, `RoFTeamMember`   |
| Rollen        | `RoFRole`, `RoleAssignment`            |
| Umwelt        | `ERoFObject`                           |

Für alle Zielbereiche wird dieselbe gespeicherte Beziehung verwendet:

```text
RaN ── GOVERNS ──► geregeltes JCI-Element oder Graphobjekt
```

| Quelle | Beziehung  | Ziel                               | Ziele je Quelle | Quellen je Ziel |
| ------ | ---------- | ---------------------------------- | ---------------:| ---------------:|
| `RaN`  | `GOVERNS` | zulässiges Zielelement            | `0..n`          | `0..n`          |

Die Kardinalität `0..n` gilt für die gespeicherte Beziehung. Für ein aktives `RaN` gilt zusätzlich die Invariante, dass es bereichsübergreifend mindestens ein Ziel regeln muss.

### 6.4 Regeln und Ausnahme

1. `RaN` ist ein Querschnittselement und kein Bestandteil der linearen Zukunftskette.
2. Ein RaN-Entwurf darf noch kein geregeltes Ziel besitzen.
3. Ein aktives `RaN` muss mindestens ein zulässiges Zielelement regeln.
4. Ein `RaN` kann mehrere Ziele aus unterschiedlichen Bereichen regeln.
5. Ein Ziel kann gleichzeitig durch keine, eine oder mehrere Regeln und Normen beeinflusst werden.
6. Bei einer Änderung an `RaN` prüft `SYNC` alle direkt geregelten Ziele und deren relevante Abhängigkeiten.
7. Widersprechen sich mehrere aktive `RaN`, wird der Konflikt gemeldet. `SYNC` darf ihn ohne festgelegte Prioritätsregel nicht stillschweigend auflösen.

### 6.5 Beispiel

Eine Regel begrenzt, welche Rollen ein bestimmtes System verändern dürfen:

```text
RaN = Nur autorisierte Rollen dürfen das Produktivsystem verändern.
  │
  ├── GOVERNS ──► RoFRole
  ├── GOVERNS ──► RoleAssignment
  └── GOVERNS ──► ERoFObject: Produktivsystem
```

Wird die Regel geändert, prüft `SYNC` die betroffenen Rollenaktivierungen und Umweltinteraktionen. Nur tatsächlich geänderte Zustände werden als eigene `PiH` festgehalten.

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
| `PiF1t` | Leistet einen taktischen Beitrag zum `PiF1s`. |

| Quelle  | Beziehung         | Ziel    | Ziele je Quelle | Quellen je Ziel |
| ------- | ----------------- | ------- | ---------------:| ---------------:|
| `PiF1s` | `CONTRIBUTES_TO` | `PiF2`  | `1..n`          | `0..n`          |
| `PiF1t` | `CONTRIBUTES_TO` | `PiF1s` | `1..n`          | `0..n`          |

### 7.4 Regeln und Ausnahme

1. Jedes `PiF1s` muss zu mindestens einem `PiF2` beitragen.
2. Ein `PiF1s` kann gleichzeitig zu mehreren `PiF2` beitragen.
3. Ein `PiF1s` kann Beiträge von keinem, einem oder mehreren `PiF1t` erhalten; `0..n` erlaubt einen noch nicht ausformulierten Entwurf.
4. `PiF1s` beschreibt einen strategischen Zustand und keine auszuführende Tätigkeit.
5. Änderungen werden durch `SYNC` in beide Richtungen des verbundenen Zukunftsgraphen auf Auswirkungen geprüft.

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
| `PiF1o` | Leistet einen operativen Beitrag zum `PiF1t`. |

| Quelle  | Beziehung         | Ziel    | Ziele je Quelle | Quellen je Ziel |
| ------- | ----------------- | ------- | ---------------:| ---------------:|
| `PiF1t` | `CONTRIBUTES_TO` | `PiF1s` | `1..n`          | `0..n`          |
| `PiF1o` | `CONTRIBUTES_TO` | `PiF1t` | `1..n`          | `0..n`          |

### 8.4 Regeln und Ausnahme

1. Jedes `PiF1t` muss zu mindestens einem `PiF1s` beitragen.
2. Ein `PiF1t` kann gleichzeitig zu mehreren `PiF1s` beitragen.
3. Ein `PiF1t` kann Beiträge von keinem, einem oder mehreren `PiF1o` erhalten; `0..n` erlaubt einen noch nicht ausformulierten Entwurf.
4. `PiF1t` beschreibt einen taktischen Zustand und keine Tätigkeit.
5. Änderungen werden durch `SYNC` auf strategische und operative Auswirkungen geprüft.

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

Die Tasks werden durch `RoleAssignments` des verantwortlichen Mitglieds ausgeführt. Ein Task kann `ERoFObjects` verwenden und `Results` erzeugen. Eine `Verification` bewertet ein Result gegen ein zum `PiF1o` gehörendes `SuccessCriterion`.

Wird ein `PiF1o` oder ein verbundenes operatives Graphobjekt geändert, prüft `SYNC` die Auswirkungen auf Zukunftsbeiträge, Erfolgskriterien, Verantwortung, Tasks, Rollenaktivierungen, Umweltobjekte, Ergebnisse und Prüfungen. Nur tatsächlich abgelöste Zustände werden als eigene `PiH` festgehalten.

### 9.3 Objekte und Beziehungen

| Objekt             | Bedeutung                                              |
| ------------------ | ------------------------------------------------------ |
| `PiF1t`            | Taktischer Zukunftszustand.                            |
| `PiF1o`            | Operativer Zukunftszustand.                            |
| `SuccessCriterion` | Kriterium für die erfolgreiche Realisierung.         |
| `RoFTeamMember`    | Für den `PiF1o` verantwortliches Mitglied.           |
| `Task`             | Tätigkeit zur Realisierung des `PiF1o`.               |
| `RoleAssignment`   | Aktive Rolle, durch die ein Task ausgeführt wird.     |
| `ERoFObject`       | Konkretes Umweltobjekt, das bei der Arbeit genutzt wird.|
| `Result`           | Durch einen Task erzeugtes Ergebnis.                   |
| `Verification`     | Prüfung eines Results gegen ein Erfolgskriterium.    |
| `Evidence`         | Optionaler, separat verwalteter Nachweis.              |

| Quelle           | Beziehung               | Ziel               | Ziele je Quelle | Quellen je Ziel |
| ---------------- | ----------------------- | ------------------ | ---------------:| ---------------:|
| `PiF1o`          | `CONTRIBUTES_TO`        | `PiF1t`            | `1..n`          | `0..n`          |
| `PiF1o`          | `HAS_SUCCESS_CRITERIA`  | `SuccessCriterion` | `1..n`          | `1`             |
| `PiF1o`          | `ACCOUNTABLE_MEMBER`    | `RoFTeamMember`    | `1`             | `0..n`          |
| `PiF1o`          | `DECOMPOSES_INTO`       | `Task`             | `1..n`          | `1`             |
| `Task`           | `EXECUTED_BY`           | `RoleAssignment`   | `1..n`          | `0..n`          |
| `Task`           | `RESPONSIBLE_TEAM`      | `RoFTeam`          | `1`             | `0..n`          |
| `Task`           | `USES`                  | `ERoFObject`       | `0..n`          | `0..n`          |
| `RoleAssignment` | `USES`                  | `ERoFObject`       | `0..n`          | `1..n`          |
| `Task`           | `PRODUCES`              | `Result`           | `0..n`          | `1`             |
| `Verification`   | `EVALUATES`             | `Result`           | `1`             | `0..n`          |
| `Verification`   | `CHECKS`                | `SuccessCriterion` | `1`             | `0..n`          |
| `Verification`   | `USES_EVIDENCE`         | `Evidence`         | `0..n`          | `0..n`          |

```text
PiF1o
  ├── HAS_SUCCESS_CRITERIA ──► SuccessCriterion ◄── CHECKS ── Verification
  ├── ACCOUNTABLE_MEMBER ──► RoFTeamMember
  └── DECOMPOSES_INTO ──► Task ── PRODUCES ──► Result ◄── EVALUATES ── Verification
                                  ├── EXECUTED_BY ──► RoleAssignment
                                  └── USES ──► ERoFObject
```

### 9.4 Regeln und Ausnahme

1. Jedes `PiF1o` muss zu mindestens einem `PiF1t` beitragen und kann mehrere `PiF1t` unterstützen.
2. Jeder `PiF1o` besitzt mindestens ein `SuccessCriterion`.
3. Jeder `PiF1o` ist genau einem verantwortlichen `RoFTeamMember` zugeordnet.
4. Jeder `PiF1o` wird in mindestens einen `Task` zerlegt; jeder Task gehört genau zu einem `PiF1o`.
5. Jeder Task wird durch mindestens ein `RoleAssignment` des verantwortlichen Mitglieds ausgeführt.
6. Jeder Task besitzt genau ein verantwortliches `RoFTeam`.
7. Ein Task kann keine, eine oder mehrere Beziehungen zu `ERoFObjects` besitzen. Verwendet ein Task ein Umweltobjekt, muss mindestens ein ausführendes `RoleAssignment` dasselbe `ERoFObject` verwenden.
8. Ein Task kann noch kein, ein oder mehrere `Results` erzeugt haben; jedes Result gehört genau zu einem Task.
9. Eine `Verification` bewertet genau ein Result und prüft genau ein `SuccessCriterion`.
10. Das Prüfergebnis wird auf `Verification` als `PASSED`, `FAILED` oder `PARTIAL` gespeichert.
11. `Evidence` wird nur als eigener Knoten verwendet, wenn ein Nachweis separat verwaltet, wiederverwendet oder auditiert werden muss.
12. `PiF1o` ist ein Zustand und niemals selbst ein Task.
13. Ein PiF1o-Entwurf ist erst fachlich vollständig, wenn Zukunftsbeitrag, Erfolgskriterium, Verantwortung und Tasks vorhanden sind.

### 9.5 Beispiel

```text
PiF1o = Mindestens 95 % der Kundenanfragen werden
         innerhalb von 24 Stunden beantwortet.
   │
   ├── CONTRIBUTES_TO ──► PiF1t
   ├── HAS_SUCCESS_CRITERIA ──►
   │      SuccessCriterion = Antwortzeit höchstens 24 Stunden
   ├── ACCOUNTABLE_MEMBER ──► RoFTeamMember
   └── DECOMPOSES_INTO ──► Task
             ├── EXECUTED_BY ──► RoleAssignment
             ├── USES ──► ERoFObject: Ticketsystem
             └── PRODUCES ──► Result: beantwortete Anfrage
                                      ◄── EVALUATES ── Verification
                                               └── CHECKS ──► SuccessCriterion
```

Die `Verification` speichert `PASSED`, `FAILED` oder `PARTIAL`. Ein separater `Evidence`-Knoten wird nur angelegt, wenn der Nachweis eigenständig verwaltet werden muss.

---

## 10. Roles and Functions – RoF

### 10.1 Bedeutung

`RoF` steht für **Roles and Functions** und beschreibt die organisatorische Handlungsfähigkeit im JCI-Modell. Es ordnet Organisationen, Teams, Mitglieder, Rollen und die konkrete Aktivierung einer Rolle in einem Team.

`RoF` beantwortet insbesondere:

- In welcher Organisation findet die Arbeit statt?
- Welches Team trägt die operative Verantwortung?
- Welches Mitglied ist für einen Zukunftszustand verantwortlich?
- Welche Rollen besitzt das Mitglied?
- Welche Rolle ist für das Mitglied in einem bestimmten Team aktiv?

### 10.2 Entstehung

Eine `RoFOrg` bildet den organisatorischen Rahmen der operativen Arbeit. Ihr werden ein oder mehrere `RoFTeams` zugeordnet. Ein Team besitzt mindestens ein `RoFTeamMember`; ein Mitglied kann mehreren Teams angehören.

Die Rollen eines Mitglieds werden unabhängig vom Teamkontext einmalig über `HAS_ROLE` gespeichert. Soll das Mitglied eine seiner Rollen in einem bestimmten Team ausüben, wird dafür ein eigenes `RoleAssignment` angelegt. Dieses verbindet das Mitglied mit genau einem Team und aktiviert genau eine Rolle aus seinem Rollenbestand.

Wird ein RoF-Element oder eine organisatorische Zuordnung geändert, prüft `SYNC` die betroffenen Zukunftszustände, Tasks, Rollenaktivierungen und Umweltbeziehungen. Tatsächlich abgelöste Zustände werden als eigene `PiH` festgehalten.

### 10.3 Objekte und Beziehungen

| Objekt           | Bedeutung                                                   |
| ---------------- | ----------------------------------------------------------- |
| `RoFOrg`         | Organisation, in der die operative Arbeit stattfindet.     |
| `RoFTeam`        | Organisatorische oder funktionale Gruppe.                   |
| `RoFTeamMember`  | Handlungsfähiger menschlicher oder technischer Akteur.      |
| `RoFRole`        | Rolle, Funktion und Verantwortungsbereich eines Mitglieds. |
| `RoleAssignment` | Aktivierung einer Rolle eines Mitglieds in einem Team.      |

| Quelle          | Beziehung            | Ziel             | Ziele je Quelle | Quellen je Ziel |
| --------------- | -------------------- | ---------------- | ---------------:| ---------------:|
| `RoFOrg`        | `HAS_TEAM`           | `RoFTeam`        | `1..n`          | `1`             |
| `RoFTeam`       | `HAS_MEMBER`         | `RoFTeamMember`  | `1..n`          | `1..n`          |
| `RoFTeamMember` | `HAS_ROLE`           | `RoFRole`        | `1..n`          | `0..n`          |
| `RoFTeamMember` | `HAS_ASSIGNMENT`     | `RoleAssignment` | `0..n`          | `1`             |
| `RoleAssignment`| `IN_TEAM`            | `RoFTeam`        | `1`             | `0..n`          |
| `RoleAssignment`| `ACTIVATES_ROLE`     | `RoFRole`        | `1`             | `0..n`          |
| `PiF1o`         | `ACCOUNTABLE_MEMBER` | `RoFTeamMember`  | `1`             | `0..n`          |
| `Task`          | `RESPONSIBLE_TEAM`   | `RoFTeam`        | `1`             | `0..n`          |
| `Task`          | `EXECUTED_BY`        | `RoleAssignment` | `1..n`          | `0..n`          |

```text
RoFOrg ── HAS_TEAM ──► RoFTeam ── HAS_MEMBER ──► RoFTeamMember
                                                        ├── HAS_ROLE ──► RoFRole
                                                        └── HAS_ASSIGNMENT ──► RoleAssignment
                                                                                  ├── IN_TEAM ──► RoFTeam
                                                                                  └── ACTIVATES_ROLE ──► RoFRole
```

### 10.4 Regeln und Ausnahme

1. Operative Arbeit findet innerhalb einer `RoFOrg` statt.
2. Eine `RoFOrg` erreicht Mitglieder und Rollen ausschließlich über `RoFTeam → RoFTeamMember → RoFRole`; direkte Beziehungen von der Organisation zu Mitgliedern oder Rollen werden nicht gespeichert.
3. Jedes `RoFTeam` gehört genau zu einer `RoFOrg` und besitzt mindestens ein Mitglied.
4. Ein `RoFTeamMember` kann Mitglied in mehreren Teams sein.
5. Ein Mitglied besitzt mindestens eine `RoFRole`; dieselbe Rolle wird im Rollenbestand eines Mitglieds nur einmal gespeichert.
6. Ein `RoleAssignment` gehört genau zu einem Mitglied, genau einem Team und aktiviert genau eine Rolle.
7. Ein `RoleAssignment` darf nur eine Rolle aktivieren, die das zugehörige Mitglied über `HAS_ROLE` besitzt.
8. Das Mitglied eines `RoleAssignment` muss über `HAS_MEMBER` dem darin referenzierten Team angehören.
9. Dieselbe Rolle kann für ein Mitglied in mehreren Teams aktiv sein; dafür wird je Team ein eigenes `RoleAssignment` verwendet.
10. Jeder `PiF1o` besitzt genau ein verantwortliches `RoFTeamMember`. Seine Tasks werden durch `RoleAssignments` dieses Mitglieds ausgeführt.

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

---

## 11. Environment of Roles or Functions – ERoF

### 11.1 Bedeutung

`ERoF` steht für **Environment of Roles or Functions** und bezeichnet den fachlichen Modellraum der relevanten Umwelt. Er umfasst die Systeme, Werkzeuge, Dokumente, Daten, Infrastrukturen, Standards, Regelwerke, Partner und weiteren Umweltbestandteile, mit denen Rollen bei ihrer Arbeit interagieren.

`ERoF` ist die konzeptionelle Kategorie. Im Graphen werden konkrete Umweltbestandteile als `ERoFObject` gespeichert.

### 11.2 Entstehung

Ein `ERoFObject` entsteht, wenn ein konkreter Umweltbestandteil für die Arbeit im JCI-Modell relevant wird. Das Objekt wird nach seinem fachlichen Typ und seinem internen oder externen Geltungsbereich beschrieben.

Beispiele für mögliche Typen sind:

```text
API, Documentation, System, Tool, Database,
Infrastructure, Standard, Regulation,
Partner, Customer, Knowledge
```

Der Geltungsbereich wird beschrieben als:

```text
scope = INTERNAL | EXTERNAL
```

Ein aktives `ERoFObject` wird mindestens einem `RoleAssignment` zugeordnet. Dadurch ist jede Umweltinteraktion mit einem Mitglied, einem Team und einer dort aktivierten Rolle verbunden.

Wird ein `ERoFObject` oder seine Verwendung geändert, prüft `SYNC` die betroffenen `RoleAssignments`, Tasks, Teams, Regeln und abhängigen Elemente. Tatsächlich abgelöste Zustände werden als eigene `PiH` festgehalten.

### 11.3 Objekte und Beziehungen

| Objekt             | Bedeutung                                                     |
| ------------------ | ------------------------------------------------------------- |
| `ERoF`             | Fachlicher Modellraum der relevanten Umwelt.                  |
| `ERoFObject`       | Konkret gespeichertes Umweltobjekt.                           |
| `RoleAssignment`   | Aktive Rolle eines Mitglieds in einem Team.                   |
| `Task`             | Tätigkeit, die ein Umweltobjekt unmittelbar verwenden kann.  |
| `RoFTeamMember`    | Mitglied, dessen Umwelt über Rollenaktivierungen ableitbar ist.|
| `RoFTeam`          | Team, dessen Umwelt aus seinen Mitgliedern abgeleitet wird.   |
| `RoFOrg`           | Organisation, deren Umwelt aus ihren Teams abgeleitet wird.   |

#### Gespeicherte Beziehungen

| Quelle           | Beziehung | Ziel         | Ziele je Quelle | Quellen je Ziel |
| ---------------- | --------- | ------------ | ---------------:| ---------------:|
| `RoleAssignment` | `USES`    | `ERoFObject` | `0..n`          | `1..n`          |
| `Task`           | `USES`    | `ERoFObject` | `0..n`          | `0..n`          |

```text
Task ── EXECUTED_BY ──► RoleAssignment ── USES ──► ERoFObject
  └──────────────────────── USES ───────────────────────►
```

#### Abgeleitete Umweltzuordnungen – nicht gespeichert

| Ausgangspunkt    | Ableitung                                               | Ziel         |
| ---------------- | ------------------------------------------------------- | ------------ |
| `RoFTeamMember`  | über seine `RoleAssignments`                            | `ERoFObject` |
| `RoFTeam`        | über Mitglieder und deren `RoleAssignments`             | `ERoFObject` |
| `RoFOrg`         | über Teams, Mitglieder und deren `RoleAssignments`       | `ERoFObject` |

```text
ERoF(RoFTeamMember)
= alle ERoFObjects seiner RoleAssignments

ERoF(RoFTeam)
= Vereinigung der ERoFObjects seiner Mitglieder in diesem Team

ERoF(RoFOrg)
= Vereinigung der ERoFObjects aller Mitglieder aller Teams der Organisation
```

### 11.4 Regeln und Ausnahme

1. `ERoF` ist die fachliche Kategorie; konkrete Graphknoten werden als `ERoFObject` gespeichert.
2. Jedes aktive `ERoFObject` muss von mindestens einem `RoleAssignment` verwendet werden.
3. Ein `RoleAssignment` kann kein, ein oder mehrere `ERoFObjects` verwenden.
4. Ein `ERoFObject` kann von mehreren `RoleAssignments` gemeinsam verwendet werden.
5. Die Umwelt eines Mitglieds, Teams oder einer Organisation wird aus den personengebundenen Rollenaktivierungen abgeleitet.
6. Direkte Umweltbeziehungen von `RoFOrg`, `RoFTeam` oder `RoFTeamMember` werden nicht als Ersatz für diese Ableitung gespeichert.
7. Ein Task darf ein `ERoFObject` direkt verwenden, wenn mindestens ein den Task ausführendes `RoleAssignment` dasselbe Umweltobjekt verwendet.
8. Eine direkte Task-Beziehung präzisiert den arbeitsbezogenen Umweltkontext, ersetzt aber niemals die Zuordnung zu einer handelnden Person.
9. Auch ein organisationsweit relevantes Umweltobjekt benötigt mindestens ein zuständiges Mitglied mit einem passenden `RoleAssignment`.
10. `RaN` kann die Verwendung eines `ERoFObject` regeln. Bei Regelkonflikten meldet `SYNC` den Konflikt, ohne ihn stillschweigend aufzulösen.

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

---

## 12. Synchronisation – SYNC

### 12.1 Bedeutung

`SYNC` bezeichnet die querschnittliche Prozesslogik des JCI-Modells. Sie sorgt dafür, dass eine Änderung nicht isoliert bleibt, sondern entlang der gespeicherten Beziehungen auf ihre Auswirkungen geprüft wird.

`SYNC` ist kein historischer Zustand und wird nicht selbst zu `PiH`. Ein konkreter Synchronisationslauf wird als `SyncEvent` dokumentiert. Wenn ein bestehender Zustand durch eine Änderung abgelöst wird, hält `SYNC` den bisherigen Zustand als eigenes `PiH` fest.

### 12.2 Entstehung

Ein Synchronisationslauf entsteht durch ein `ChangeEvent`:

1. Eine Änderung an einem JCI-Element oder Graphobjekt wird als `ChangeEvent` erfasst.
2. Das `ChangeEvent` löst mindestens ein `SyncEvent` aus.
3. `SYNC` ermittelt alle direkt und indirekt betroffenen Elemente und Beziehungen.
4. `SYNC` prüft `RaN`, Kardinalitäten und weitere Modellbedingungen.
5. `SYNC` unterscheidet zwischen lediglich betroffenen und tatsächlich zu ändernden Elementen.
6. Vor jeder tatsächlichen Änderung hält `SYNC` den bisherigen Zustand als eigenes `PiH` fest.
7. Zulässige Änderungen werden übernommen; Konflikte werden gemeldet.
8. Das `SyncEvent` dokumentiert geprüfte Elemente, erzeugte `PiH`, Änderungen, Konflikte und das Ergebnis des Synchronisationslaufs.

```text
JCI-Element ── CHANGED_BY ──► ChangeEvent ── TRIGGERS ──► SyncEvent
                                                            │
                                                            ├── AFFECTS ──► JCI-Element
                                                            └── CREATES_HISTORY ──► PiH
```

### 12.3 Objekte und Beziehungen

| Objekt        | Bedeutung                                                    |
| ------------- | ------------------------------------------------------------ |
| `ChangeEvent` | Dokumentiert Anlass, Art und Ausgangspunkt einer Änderung.  |
| `SyncEvent`   | Dokumentiert einen konkreten Synchronisationslauf.          |
| `PiH`         | Bewahrt einen durch die Änderung abgelösten Zustand.        |
| `RaN`         | Liefert Regeln, Normen und Grenzen für die Prüfung.          |
| JCI-Element   | Kann Ausgangspunkt, betroffenes oder geändertes Element sein.|

| Quelle        | Beziehung          | Ziel          | Ziele je Quelle | Quellen je Ziel |
| ------------- | ------------------ | ------------- | ---------------:| ---------------:|
| JCI-Element   | `CHANGED_BY`       | `ChangeEvent` | `0..n`          | `1`             |
| `ChangeEvent` | `TRIGGERS`         | `SyncEvent`   | `1..n`          | `1`             |
| `SyncEvent`   | `AFFECTS`          | JCI-Element   | `1..n`          | `0..n`          |
| `SyncEvent`   | `CREATES_HISTORY`  | `PiH`         | `0..n`          | `1`             |

```text
SYNC prüft abhängig vom geänderten Element insbesondere:

CiV und PiF2 bis PiF1o
RaN und geregelte Ziele
RoFOrg, RoFTeam, RoFTeamMember, RoFRole und RoleAssignment
Task, SuccessCriterion, Result, Verification und Evidence
ERoFObject und seine personengebundenen Verwendungen
```

### 12.4 Regeln und Ausnahme

1. Jedes `ChangeEvent` löst mindestens ein `SyncEvent` aus.
2. Jedes `SyncEvent` gehört zu genau einem auslösenden `ChangeEvent`.
3. Jedes `SyncEvent` benennt mindestens ein betroffenes JCI-Element oder Graphobjekt.
4. Betroffenheit allein erzeugt kein `PiH`. Nur ein tatsächlich abgelöster Zustand wird historisiert.
5. Ein `SyncEvent` kann kein, ein oder mehrere `PiH` erzeugen.
6. Bei `ANGELEGT` entsteht kein `PiH` des neu angelegten Elements, weil kein vorheriger Zustand existiert.
7. `SYNC` prüft alle für die Änderung relevanten `RaN` und Modellbedingungen.
8. Eindeutig ableitbare und zulässige Anpassungen können verarbeitet werden. Semantische Konflikte, widersprüchliche `RaN` oder nicht eindeutig entscheidbare Änderungen werden gemeldet und nicht stillschweigend aufgelöst.
9. `SYNC` ist die Prozesslogik; `SyncEvent` ist die Dokumentation eines konkreten Laufs. Beide sind kein `PiH`.
10. Jeder durch `SYNC` erzeugte historische Zustand bleibt über `CREATES_HISTORY` mit genau einem `SyncEvent` und über `HAS_HISTORICAL_STATE` mit seinem ursprünglichen Element verbunden.

### 12.5 Beispiel

Ein operativer Zukunftszustand wird von 48 auf 24 Stunden Antwortzeit geändert:

```text
PiF1o: Antwort innerhalb von 48 Stunden
                  │
                  └── CHANGED_BY ──► ChangeEvent
                                          │
                                          └── TRIGGERS ──► SyncEvent
                                                               ├── AFFECTS ──► PiF1o
                                                               ├── AFFECTS ──► SuccessCriterion
                                                               ├── AFFECTS ──► Task
                                                               └── CREATES_HISTORY ──► PiH
```

`SYNC` prüft den `PiF1o`, seine Erfolgskriterien, Tasks, Verantwortung, Rollenaktivierungen und verwendeten `ERoFObjects`. Der bisherige PiF1o-Zustand wird als `PiH` festgehalten. Abhängige Elemente erhalten nur dann ein eigenes `PiH`, wenn ihr Zustand tatsächlich geändert wird. Das `SyncEvent` dokumentiert alle Prüfungen, Änderungen und Konflikte.

---

## 13. Abschluss

Der JUNACO Continuous Integration Loop verbindet Zweck, Zukunft, Verantwortung, Arbeit, Umwelt, Regeln, Prüfung und historische Entwicklung in einem gemeinsamen fachlichen Graphen.

`CiV` begründet, warum eine Zukunft gewollt ist. `PiF2` bis `PiF1o` beschreiben diese Zukunft auf langfristiger, strategischer, taktischer und operativer Ebene. Die gespeicherten `CONTRIBUTES_TO`-Beziehungen führen dabei vom konkreteren zum übergeordneten Zukunftszustand und erlauben einen gerichteten `n:m`-Graphen.

Ein `PiF1o` beschreibt einen erreichbaren operativen Zustand. Er besitzt Erfolgskriterien und genau ein verantwortliches `RoFTeamMember`. Die daraus abgeleiteten Tasks werden über teambezogene `RoleAssignments` ausgeführt, verwenden konkrete `ERoFObjects` und können `Results` erzeugen. `Verifications` bewerten diese Ergebnisse gegen die festgelegten Erfolgskriterien.

`RoF` stellt den Organisations-, Team-, Mitglieder- und Rollenkontext bereit. `ERoF` beschreibt die relevante Umwelt, wobei konkrete Umweltinteraktionen immer über handelnde Rollenaktivierungen nachvollziehbar bleiben. `RaN` wirkt als regelnder Querschnitt auf die jeweils geregelten Zukunfts-, Arbeits-, Organisations-, Rollen- und Umweltbereiche.

`SYNC` verarbeitet Änderungen entlang der relevanten Beziehungen. Das auslösende `ChangeEvent` führt zu mindestens einem dokumentierten `SyncEvent`. Nur wenn ein vorhandener Zustand tatsächlich abgelöst wird, hält `SYNC` diesen bisherigen Zustand als eigenes `PiH` fest. Betroffenheit allein erzeugt keinen historischen Zustand; Konflikte werden gemeldet und nicht stillschweigend aufgelöst.

```text
PiH ── PROVIDES_CONTEXT_TO ──► CiV ── INSCRIBES_PURPOSE_IN ──► PiF2
                                                                     ▲
PiF1o ── CONTRIBUTES_TO ──► PiF1t ── CONTRIBUTES_TO ──► PiF1s ─────┘
  │
  ├── HAS_SUCCESS_CRITERIA ──► SuccessCriterion
  ├── ACCOUNTABLE_MEMBER ────► RoFTeamMember
  └── DECOMPOSES_INTO ───────► Task ── PRODUCES ──► Result
                                   │                    ▲
                                   ├── EXECUTED_BY      └── EVALUATES ── Verification
                                   │   RoleAssignment                         └── CHECKS ──► SuccessCriterion
                                   └── USES ──► ERoFObject

RaN ── GOVERNS ──► relevante Ziele
ChangeEvent ── TRIGGERS ──► SyncEvent ── AFFECTS ──► JCI-Element
                                      └── CREATES_HISTORY ──► PiH
```

Damit bleibt von einem konkreten Task rückwärts nachvollziehbar, welchem operativen Zustand, welchem Zukunftszusammenhang und welchem wertbezogenen Zweck er dient. Gleichzeitig bleiben Verantwortung, Umweltbezug, Regeln, Prüfergebnisse und abgelöste Zustände eindeutig zugeordnet. Diese durchgängige Nachvollziehbarkeit bildet den Kern des JCI Loops.
