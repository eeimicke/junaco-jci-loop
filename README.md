# JUNACO JCI Loop

Dieses Repository enthält die kanonische Spezifikation des **JUNACO Continuous Integration Model for Organisations** und des daraus gebildeten **JCI Loop**.

Der JCI Loop ist ein graphbasiertes Organisationsmodell. Er verbindet Zweck und Werte, Zukunftszustände, Regeln, Rollen, Umweltbeziehungen, operative Umsetzung, Synchronisation und Historisierung in einem nachvollziehbaren Zusammenhang.

## Kanonische Spezifikation

Die aktuelle fachliche Beschreibung befindet sich in:

- [JCI_CONTEXT.md](docs/JCI_CONTEXT.md)

Die daraus abgeleiteten verbindlichen Spezifikationen sind:

- [JCI_ONTOLOGY.md](docs/JCI_ONTOLOGY.md) – Entitäts- und Beziehungskatalog
- [JCI_GRAPH_RULES.md](docs/JCI_GRAPH_RULES.md) – Kardinalitäten und Invarianten
- [JCI_SYNC_SPEC.md](docs/JCI_SYNC_SPEC.md) – Änderungs-, Traversierungs- und Synchronisationslogik
- [JCI_NEO4J_SCHEMA.md](docs/implementations/neo4j/JCI_NEO4J_SCHEMA.md) – Neo4j-Projektion und Validierungsabfragen
- [Maschinenlesbare Schemas](docs/schemas/) – JSON und JSON-LD für Austauschformate

Die automatisierten Modellprüfungen liegen unter `tests/` und werden bei Pull Requests sowie Pushes auf `main` ausgeführt.

Änderungen an dieser Datei können die Semantik des Modells betreffen und werden deshalb kontrolliert geprüft.

## Mitarbeit

Vorschläge und Korrekturen sind möglich. Der reguläre Weg ist:

1. Issue anlegen,
2. eigenen Branch erstellen,
3. Änderung vornehmen,
4. Pull Request vollständig beschreiben,
5. automatische und fachliche Prüfung abschließen,
6. Änderung nach dokumentierter Freigabe in `main` übernehmen.

Einzelheiten stehen in:

- [CONTRIBUTING.md](CONTRIBUTING.md)
- [GOVERNANCE.md](GOVERNANCE.md)
- [AGENTS.md](AGENTS.md)

## Lizenz und Rechte

Die JCI-Modellspezifikation wird unter **CC BY-NC-SA 4.0** bereitgestellt. Kommerzielle Nutzung erfordert grundsätzlich eine gesonderte Vereinbarung mit der JUNACO Organisationsentwicklungs GmbH.

- [Lizenz](LICENSE.md)
- [Rechte- und Quellenhinweise](NOTICE.md)

Software, technische Implementierungen, The Company Brain und DeepJuni sind durch diese Modelllizenz nicht automatisch erfasst.

