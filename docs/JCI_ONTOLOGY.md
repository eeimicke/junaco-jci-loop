# JCI-Ontologie

## Status und Zweck

Dieses Dokument spezifiziert künftig die formale Ontologie des JUNACO Continuous Integration Model for Organisations. Es übersetzt die fachliche Bedeutung aus [JCI_CONTEXT.md](JCI_CONTEXT.md) in eindeutig benannte Entitätstypen und Beziehungstypen.

`JCI_CONTEXT.md` bleibt die kanonische fachliche Quelle. Dieses Dokument darf keine abweichende Semantik einführen. Bei einem Konflikt gilt `JCI_CONTEXT.md`, und der Konflikt muss vor einer Änderung gemeldet werden.

## Inhalt dieser Spezifikation

Die Ontologie soll verbindlich festlegen:

- den abstrakten Oberbegriff `JCIEntity`,
- die Unterscheidung zwischen `JCIElement` und `GraphObject`,
- alle zulässigen konkreten Entitätstypen,
- alle gespeicherten Beziehungstypen,
- Quell- und Zieltypen jeder Beziehung,
- inverse Lesarten, die nicht zusätzlich gespeichert werden,
- historisierbare und unveränderliche Entitätstypen.

## Abgrenzung

Kardinalitäten und fachliche Invarianten gehören in [JCI_GRAPH_RULES.md](JCI_GRAPH_RULES.md). Der Ablauf von `SYNC` gehört in [JCI_SYNC_SPEC.md](JCI_SYNC_SPEC.md). Datenbankspezifische Labels, Properties, Constraints und Indizes gehören in [implementations/neo4j/JCI_NEO4J_SCHEMA.md](implementations/neo4j/JCI_NEO4J_SCHEMA.md).

## Noch zu spezifizieren

- vollständiger Entitätskatalog,
- vollständiger Beziehungskatalog,
- verbindliche Typzuordnung jeder Beziehung,
- formale Darstellung der Historisierung,
- maschinenlesbare Repräsentation der Ontologie.
