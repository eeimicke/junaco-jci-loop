# JUNACO JCI Loop

🇩🇪 [Deutsch](#deutsch) · 🇬🇧 [English](#english)

## Deutsch

> Eine Organisation bleibt nur dann handlungsfähig, wenn Zweck, Zukunft, Verantwortung, Arbeit, Regeln, Umwelt und Lernen auch nach Veränderungen zusammenpassen.

Der **JUNACO Continuous Integration Loop** ist ein graphbasiertes Organisationsmodell. Er macht sichtbar, warum eine Aufgabe existiert, wer sie in welchem Team und welcher Rolle ausführt, welche Umweltobjekte benötigt werden, welche Regeln gelten, wie Erfolg geprüft wird und welcher frühere Zustand durch eine Änderung abgelöst wurde.

```mermaid
flowchart LR
    PiH -->|PROVIDES_CONTEXT_TO| CiV
    CiV -->|HELD_BY| Holder[RoFOrg, RoFTeam oder Mensch]
    CiV -->|INFORMED_BY| SourceCiV[anderes CiV]
    CiV -->|INSCRIBES_PURPOSE_IN| PiF2
    RaN -->|PROTECTS| CiV
    RaN -->|PROTECTS| PiF2
    RaN -->|GOVERNS| Task
    PiF1s -->|CONTRIBUTES_TO| PiF2
    PiF1t -->|CONTRIBUTES_TO| PiF1s
    PiF1o -->|CONTRIBUTES_TO| PiF1t
    PiF1o -->|DECOMPOSES_INTO| Task
    Task -->|PRODUCES| Result
    Verification -->|EVALUATES| Result
    ChangeEvent -->|TRIGGERS| SyncEvent
    SyncEvent -->|CREATES_HISTORY| PiH
```

### Einstieg

- [Dokumentationsübersicht](docs/README.md)
- [Einführung für neue Leser](docs/guides/JCI_INTRODUCTION.md)
- [Die JCI-Elemente](docs/guides/JCI_ELEMENTS.md)
- [Durchgängiges Beispiel](docs/guides/JCI_EXAMPLE.md)
- [Kanonische Spezifikation](docs/JCI_CONTEXT.md)

### Formale und technische Dokumente

- [Ontologie](docs/JCI_ONTOLOGY.md)
- [Graphregeln](docs/JCI_GRAPH_RULES.md)
- [SYNC-Spezifikation](docs/JCI_SYNC_SPEC.md)
- [Implementierungsleitfaden](docs/guides/JCI_IMPLEMENTATION_GUIDE.md)
- [Neo4j-Schema](docs/implementations/neo4j/JCI_NEO4J_SCHEMA.md)
- [Maschinenlesbare Schemas](docs/schemas/)
- [Öffentliches JCI-Vokabular](docs/ns/jci/1.0/index.html)

## English

> An organisation remains viable only when purpose, future, responsibility, work, rules, environment, and learning continue to fit together after change.

The **JUNACO Continuous Integration Loop** is a graph-based organisational model. It makes it possible to trace why a task exists, who performs it in which team and role, which environmental objects are required, which rules apply, how success is verified, and which former state was superseded by a change.

### Start here

- [Documentation overview](docs/en/README.md)
- [Introduction](docs/en/guides/JCI_INTRODUCTION.md)
- [JCI elements](docs/en/guides/JCI_ELEMENTS.md)
- [End-to-end example](docs/en/guides/JCI_EXAMPLE.md)
- [English model specification](docs/en/JCI_CONTEXT.md)

### Formal and technical documents

- [Ontology](docs/en/JCI_ONTOLOGY.md)
- [Graph rules](docs/en/JCI_GRAPH_RULES.md)
- [SYNC specification](docs/en/JCI_SYNC_SPEC.md)
- [Implementation guide](docs/en/guides/JCI_IMPLEMENTATION_GUIDE.md)
- [Neo4j schema](docs/en/implementations/neo4j/JCI_NEO4J_SCHEMA.md)
- [Machine-readable schemas](docs/schemas/)
- [Public JCI vocabulary](docs/ns/jci/1.0/index.html)

## Contribution and rights

- [Beitragen](CONTRIBUTING.md) · [Contributing](CONTRIBUTING.en.md)
- [Governance](GOVERNANCE.md) · [Governance in English](GOVERNANCE.en.md)
- [Lizenz](LICENSE.md) · [Informal English license translation](LICENSE.en.md)
- [Rechtehinweise](NOTICE.md) · [Rights notice in English](NOTICE.en.md)

The canonical German JCI model specification is licensed under **CC BY-NC-SA 4.0**. Commercial use generally requires a separate agreement with JUNACO Organisationsentwicklungs GmbH. Software and technical implementations require their own explicit software licence.
