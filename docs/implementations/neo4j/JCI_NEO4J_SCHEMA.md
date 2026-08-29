# JCI-Neo4j-Schema

## Status und Zweck

Dieses Dokument spezifiziert künftig die technische Abbildung des JCI-Modells in Neo4j. Es implementiert die fachliche Spezifikation aus [JCI_CONTEXT.md](../../JCI_CONTEXT.md), die Ontologie aus [JCI_ONTOLOGY.md](../../JCI_ONTOLOGY.md), die Invarianten aus [JCI_GRAPH_RULES.md](../../JCI_GRAPH_RULES.md) und den Ablauf aus [JCI_SYNC_SPEC.md](../../JCI_SYNC_SPEC.md).

Bei einem Konflikt darf das Neo4j-Schema die fachliche Semantik nicht verändern. Der Konflikt muss stattdessen dokumentiert und vor der Implementierung entschieden werden.

## Inhalt dieser Spezifikation

Das Neo4j-Schema soll verbindlich festlegen:

- Labels für `JCIEntity`, `JCIElement` und `GraphObject`,
- konkrete Labels für alle JCI-Typen,
- Relationship-Typen und ihre Richtungen,
- Pflicht- und optionale Properties,
- Identität und Mandantentrennung,
- Unique-, Existence- und Type-Constraints,
- Indizes und Zugriffspfade,
- Speicherung unveränderlicher `PiH`, `ChangeEvent` und `SyncEvent`,
- technische Validierung nicht direkt erzwingbarer Invarianten,
- Migrations- und Versionsstrategie.

## Noch zu spezifizieren

- verbindliche Properties wie Identität, Mandant, Zeit und Status,
- zusammengesetzte Eindeutigkeit pro Mandant,
- vollständige Cypher-Constraints und Indizes,
- Transaktionsgrenzen für `SYNC`,
- Abbildung historischer Eigenschaften und Beziehungen,
- Testabfragen für jede Invariante.

In diesem Dokument sind noch keine ausführbaren Cypher-Anweisungen festgelegt.
