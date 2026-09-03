# JCI documentation

[Deutsch](../README.md) · [English](README.md)

This page leads from an accessible introduction to the formal and technical specification of the **JUNACO Continuous Integration Model for Organisations (JCI Loop)**.

## Recommended reading path

1. [Introduction](guides/JCI_INTRODUCTION.md) – problem, core idea, and value.
2. [JCI elements](guides/JCI_ELEMENTS.md) – core elements and supporting graph objects.
3. [End-to-end example](guides/JCI_EXAMPLE.md) – one complete journey through the loop.
4. [English model specification](JCI_CONTEXT.md) – controlled translation of the canonical German specification.
5. [Ontology](JCI_ONTOLOGY.md) and [graph rules](JCI_GRAPH_RULES.md) – formal types, relationships, and invariants.
6. [SYNC specification](JCI_SYNC_SPEC.md) – processing, history, and conflicts.
7. [Implementation guide](guides/JCI_IMPLEMENTATION_GUIDE.md) and [Neo4j schema](implementations/neo4j/JCI_NEO4J_SCHEMA.md).

## Language policy

[`docs/JCI_CONTEXT.md`](../JCI_CONTEXT.md) is the canonical specification. The English documents are controlled translations. If the versions differ, the German version temporarily prevails until the translation has been corrected and reviewed again.

Technical artifacts such as JSON Schemas, the JSON-LD context, tests, and workflows exist only once. Their identifiers and canonical JCI terms are language-neutral.

## Diagrams

The documentation uses Mermaid diagrams rendered directly by GitHub. Their sources are stored in [`../diagrams/sources`](../diagrams/sources/README.md). Entity types and relationship names remain identical in both languages; only explanatory text is translated.

