# Die Elemente des JCI Loop

[Dokumentationsübersicht](../README.md) · [English](../en/guides/JCI_ELEMENTS.md)

## Zehn Kernelemente

| Element | Einfache Bedeutung |
|---|---|
| `PiH` | bewahrt einen früheren, abgelösten Zustand |
| `CiV` | beschreibt Zweck und Werte |
| `RaN` | beschreibt Regeln und Normen |
| `RoF` | Modellraum für Organisationen, Teams, Mitglieder und Rollen |
| `ERoF` | Modellraum für die relevante Umwelt handelnder Rollen |
| `SYNC` | gespeicherte Definition der Synchronisationslogik |
| `PiF2` | langfristiger Zukunftszustand über zehn Jahre |
| `PiF1s` | strategischer Zukunftszustand über fünf bis zehn Jahre |
| `PiF1t` | taktischer Zukunftszustand über ein bis fünf Jahre |
| `PiF1o` | operativer Zukunftszustand unter einem Jahr |

`RoF` und `ERoF` sind Kernelemente, aber keine eigenen Knoten. Sie werden aus ihren konkreten Graphobjekten und Beziehungen sichtbar.

## Gespeicherte Entitäten

```mermaid
flowchart TB
    JCIEntity --> JCIElementInstance
    JCIEntity --> GraphObject
    JCIElementInstance --> PiH & CiV & RaN & SYNC & PiF2 & PiF1s & PiF1t & PiF1o
    GraphObject --> RoFOrg & RoFOrgRelationship & RoFTeam & RoFTeamMember & RoFRole & RoleAssignment
    GraphObject --> Task & SuccessCriterion & Result & Verification & Evidence & ERoFObject
    GraphObject --> ChangeEvent & SyncEvent & RaNConflict & HistoricalCorrection
```

`JCIEntity` ist der gemeinsame abstrakte Oberbegriff. Jede gespeicherte Entität besitzt mindestens `id`, `entityType`, `name`, `createdAt`, `updatedAt`, `revision` und `status`.

## Organisation und Rollen

```mermaid
flowchart LR
    Org[RoFOrg] -->|HAS_TEAM| Team[RoFTeam]
    Team -->|HAS_MEMBER| Member[RoFTeamMember]
    Member -->|HAS_ROLE| Role[RoFRole]
    Member -->|HAS_ASSIGNMENT| Assignment[RoleAssignment]
    Assignment -->|IN_TEAM| Team
    Assignment -->|ACTIVATES_ROLE| Role
```

Ein `RoleAssignment` bedeutet: Ein bestimmtes Mitglied aktiviert eine vorhandene Rolle in einem bestimmten Team. Dadurch kann dieselbe Person dieselbe Rolle in mehreren Teams ausüben, ohne die Rolle oder Person zu duplizieren.

### Einmalige Initialisierung

In einem vollständig leeren Graphen gibt es zunächst noch keine Rollenaktivierung, die als Erzeuger dienen kann. Deshalb darf ein einmaliger atomarer Bootstrap eine `RoFOrg`, ein `RoFTeam`, ein technisches `RoFTeamMember`, eine `RoFRole`, genau ein `RoleAssignment` mit `bootstrapKey = "ROOT"` und eine `SYNC`-Definition gemeinsam anlegen. Alle sechs Entitäten entstehen direkt mit `status = ACTIVE`, `revision = 1` sowie demselben `createdAt` und `updatedAt`; vorhandene `validFrom`-Werte entsprechen demselben Bootstrapzeitpunkt. Nur dieses Root-`RoleAssignment` darf dauerhaft ohne `CREATED_BY` bestehen; alle weiteren Bootstrap-Entitäten verweisen mit `CREATED_BY` auf dieses Root-`RoleAssignment`.

Der Bootstrap ist nur bei einem vollständig leeren Graphen zulässig. Er erzeugt weder `ChangeEvent`, `SyncRun`, `SyncEvent` noch `PiH`, und alle erzeugten Entitäten beginnen mit `revision = 1`. Nach erfolgreichem Abschluss sind ein zweiter Bootstrap und ein zweites Root-`RoleAssignment` ausgeschlossen. Ein Datenimport ist kein Bootstrap.

## Arbeit, Ergebnis und Prüfung

```mermaid
flowchart LR
    PiF1o -->|DECOMPOSES_INTO| Task
    Task -->|EXECUTED_BY| Assignment[RoleAssignment]
    Task -->|PRODUCES| Result
    Verification -->|EVALUATES| Result
    Verification -->|USES_EVIDENCE| Evidence
    Verification -->|CHECKS| Criterion[SuccessCriterion]
    PiF1o -->|HAS_SUCCESS_CRITERIA| Criterion
```

- `Task`: Was wird getan?
- `Result`: Was wurde erzeugt?
- `Evidence`: Womit lässt es sich belegen?
- `Verification`: Wie wurde das Ergebnis gegen ein Kriterium bewertet?

Eine `Verification` hält nicht nur die Beziehungen zu genau einem `Result` und genau einem `SuccessCriterion` fest, sondern auch deren tatsächlich geprüfte Revisionen. Beispiel: Eine Prüfung mit `evaluatedResultRevision = 3` und `checkedCriterionRevision = 2` ist nur anwendbar, solange genau diese Revisionen aktuell sind und die Prüfung nicht durch `SUPERSEDES` ersetzt wurde. Wird eines der beiden Ziele später geändert, bleibt die Prüfung als Nachweis erhalten, gilt für den aktuellen Zustand aber als revisionsveraltet.

## Umwelt

```mermaid
flowchart LR
    Task -->|EXECUTED_BY| Assignment[RoleAssignment]
    Task -->|USES| Object[ERoFObject]
    Assignment -->|USES| Object
    Object -->|OWNED_BY| Org[RoFOrg]
```

Ein aktives Umweltobjekt muss von mindestens einer Rollenaktivierung verwendet werden. Eigentum allein belegt keine Interaktion. Ob ein Objekt intern oder extern ist, wird relativ zur betrachteten Organisation aus `OWNED_BY` abgeleitet.

### Beispiel

Der Task `Kundenportal bereitstellen` verwendet das `ERoFObject` `GitHub-Repository`. Anna führt den Task in ihrer aktivierten Rolle `Developer` aus und verwendet dabei ebenfalls dieses Repository. Das Repository gehört der betrachteten `RoFOrg` und ist deshalb aus ihrer Sicht ein internes Umweltobjekt.

```text
Task: Kundenportal bereitstellen
  ├── EXECUTED_BY ──► RoleAssignment: Anna als Developer
  └── USES ─────────► ERoFObject: GitHub-Repository
                           ▲
RoleAssignment ── USES ────┘
ERoFObject ── OWNED_BY ──► RoFOrg: Beispiel GmbH
```

Gehörte das Repository stattdessen einer Partnerorganisation, wäre es aus Sicht der Beispiel GmbH ein externes Umweltobjekt. Entscheidend ist immer die Beziehung `OWNED_BY` zur betrachteten Organisation.

## Veränderungsobjekte

- `ChangeEvent`: Anlass und Auftrag einer Änderung.
- `SyncEvent`: unveränderliches Ergebnis eines beendeten technischen Laufs.
- `PiH`: vorheriger Zustand einer tatsächlich geänderten Entität.
- `RaNConflict`: nicht automatisch entscheidbarer Regelkonflikt.
- `HistoricalCorrection`: Berichtigung eines `PiH`, ohne dieses zu überschreiben.

Ein angenommenes `ChangeEvent` darf zunächst noch keine `TRIGGERS`-Beziehung besitzen: `TRIGGERS = 0` bezeichnet den ausstehenden Zustand, bevor ein technischer Versuch beendet wurde. Jeder abgeschlossene oder kontrolliert abgebrochene `SyncRun` erzeugt genau ein unveränderliches `SyncEvent` mit eigener eindeutiger `runId` und ergänzt genau eine `TRIGGERS`-Beziehung. Ein erneuter Versuch erhält eine neue `runId` und ein eigenes `SyncEvent`.

`CHANGED_BY` und `AFFECTS` gelten deshalb bedingt:

- Bei der Änderung einer vorhandenen Entität verweist diese über `CHANGED_BY` auf das `ChangeEvent`.
- Bei `CREATED` gibt es vor dem erfolgreichen Commit noch keine Quellentität. Nur bei `SUCCESS` entstehen die neue Entität mit `revision = 1`, `CREATED_BY` und `CHANGED_BY`; ein `PiH` entsteht nicht. Bei `CONFLICT` oder `FAILED` entstehen weder Zielknoten noch diese Beziehungen.
- Ein `SyncEvent` mit `SUCCESS` oder `CONFLICT` besitzt mindestens ein `AFFECTS`-Ziel. Nur ein früher `FAILED`-Versuch, der das Ziel noch nicht auflösen konnte, darf kein `AFFECTS` besitzen.

Eine historische Korrektur verändert weder das `PiH` noch erzeugt sie ein neues `PiH`. Das zugehörige `ChangeEvent` verweist stattdessen mit `TARGETS_HISTORY` auf genau das betroffene `PiH`. Vor dem Commit vergleicht `SYNC` den erwarteten Hash der wirksamen `HistoryView` mit dem aktuellen Hash. Aktive Korrekturen dürfen nur unterschiedliche `correctedFields` betreffen; eine überlappende Korrektur muss genau eine aktive Vorgängerkorrektur vollständig über `SUPERSEDES` ersetzen. Andernfalls endet der Versuch mit `CONFLICT`.

Für sämtliche Pflichtfelder und Kardinalitäten ist die [kanonische Spezifikation](../JCI_CONTEXT.md) maßgeblich.

