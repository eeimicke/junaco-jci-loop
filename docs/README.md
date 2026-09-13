# JCI-Dokumentation

[Deutsch](README.md) · [English](en/README.md)

Diese Seite führt vom verständlichen Einstieg zur formalen und technischen Spezifikation des **JUNACO Continuous Integration Model for Organisations (JCI Loop)**.

## Empfohlener Lesepfad

1. [Einführung](guides/JCI_INTRODUCTION.md) – Problem, Grundidee und Nutzen.
2. [JCI-Elemente](guides/JCI_ELEMENTS.md) – Kernelemente und unterstützende Graphobjekte.
3. [Durchgängiges Beispiel](guides/JCI_EXAMPLE.md) – ein vollständiger Weg durch den Loop.
4. [Kanonische Spezifikation](JCI_CONTEXT.md) – verbindliche deutsche Modellbeschreibung.
5. [Ontologie](JCI_ONTOLOGY.md) und [Graphregeln](JCI_GRAPH_RULES.md) – formale Typen, Beziehungen und Invarianten.
6. [SYNC-Spezifikation](JCI_SYNC_SPEC.md) – Verarbeitung, Historisierung und Konflikte.
7. [Implementierungsleitfaden](guides/JCI_IMPLEMENTATION_GUIDE.md) und [Neo4j-Schema](implementations/neo4j/JCI_NEO4J_SCHEMA.md).

8. [Logikänderungen 2.0](changes/JCI_LOGIC_2_0.md) – sechs Korrekturen, Auswirkungen, Migration und 23 Abnahmefälle.
9. [Freigabeprofil 1.0](changes/JCI_APPROVAL_1_0.md) – menschliche Genehmigung, Accountability, Eskalation und geschützte SYNC-Übernahme.
10. [Neo4j-Laufzeit](implementations/neo4j/JCI_NEO4J_RUNTIME.md) – ausführbarer Transaktionsadapter, Wiederaufnahme und echte Datenbanktests.

Neue Regel-, Snapshot-, Werte- und Austauschprofile verwenden `2.0`. JSON-LD `1.1` und der bestehende Vokabularnamensraum bleiben unverändert. Das [Snapshot-Payloadschema](schemas/jci-history-snapshot.schema.json) beschreibt historische Nutzdaten; [Legacy-Schemas](schemas/legacy/1.1/) erhalten ältere Profile.

## Sprachregel

[`docs/JCI_CONTEXT.md`](JCI_CONTEXT.md) ist die kanonische Spezifikation. Die englischen Dokumente sind kontrollierte Übersetzungen. Bei einer Abweichung gilt vorläufig die deutsche Fassung, bis die Übersetzung korrigiert und erneut geprüft wurde.

Technische Artefakte wie JSON-Schemas, JSON-LD-Kontext, Tests und Workflows existieren nur einmal. Ihre IDs und kanonischen JCI-Begriffe sind sprachunabhängig.

## Grafiken

Die Dokumentation verwendet Mermaid-Diagramme, die GitHub direkt darstellt. Die Quellfassungen liegen unter [`diagrams/sources`](diagrams/sources/README.md). Entitätstypen und Beziehungsnamen bleiben in beiden Sprachen unverändert; nur erläuternde Texte werden übersetzt.

