# JCI Neo4j schema

[Documentation overview](../../README.md) · [Deutsche Fassung](../../../implementations/neo4j/JCI_NEO4J_SCHEMA.md)

> Controlled English companion to the canonical German Neo4j projection. Cypher identifiers remain language-neutral. The full executable constraint and validation query catalogue is maintained once in the German source file linked above.

## 1. Projection

Every stored node carries `:JCIEntity` and exactly one concrete entity label matching `entityType`. Stored core-element instances additionally carry `:JCIElementInstance`; supporting objects carry `:GraphObject`. `RoF`, `ERoF`, and technical `SyncRun` are not nodes.

```cypher
CREATE CONSTRAINT jci_entity_id IF NOT EXISTS
FOR (e:JCIEntity) REQUIRE e.id IS UNIQUE;
```

Common required properties are `id`, `entityType`, `name`, `createdAt`, `updatedAt`, `revision`, and `status`. Concrete type labels, property enums, relationship endpoint types, and cardinalities are validated against `JCI_CONTEXT.md` and `JCI_GRAPH_RULES.md`.

## 2. Complex properties

Neo4j scalar properties cannot directly store nested JSON values. Implementations therefore project canonical JSON strings:

| Domain value | Neo4j property |
|---|---|
| `RaN.condition` | `conditionJson` |
| `SYNC.definition` | `definitionJson` |
| `Result.value` | `valueJson` |
| `PiH.stateData` | `stateDataJson` |
| `PiH.relationshipData` | `relationshipDataJson` |
| correction maps | `previousValueJson`, `correctedValueJson` |

The application validates each value against its structured type before writing. Canonical serialisation is required for deterministic hashes.

## 3. Constraint groups

The canonical German schema contains executable Cypher for:

- global and type-specific identity and required-property constraints,
- legal entity labels, enum values, status values, and terminal immutability,
- `REPLACED_BY` type equality and cycle detection,
- future contribution modes and achieved-state aggregation,
- SuccessCriterion operator compatibility and current Verification chains,
- Task hierarchy, dependency, execution, environment, and composite aggregation,
- membership, role ownership, RoleAssignment validity, and allocation,
- partnership canonical direction and subsidiary parent/cycle rules,
- ERoF ownership and person-bound use,
- RaN scope, condition, priority, and RaNConflict cardinalities,
- PiH, ChangeEvent, SyncEvent, and HistoricalCorrection integrity.

## 4. Transaction boundary

SYNC evaluates the model outside partial domain mutation, rechecks revisions, and commits one ChangeEvent's successful domain change atomically. On conflict or failure, domain mutation rolls back; the final SyncEvent and required conflict documentation are stored separately as attempt documentation.

Neo4j constraints cannot express every temporal, aggregate, path, or conditional invariant. Such rules remain mandatory SYNC validations and automated integration tests.

## 5. Migrations

Every schema change uses a monotonically versioned migration. A migration first validates existing data, performs controlled transformations, installs new constraints, records the model and schema versions, and is never edited after release.

Tenant isolation is not part of the JCI ontology. If an implementation is multi-tenant, it must add its own security boundary without using `RoFOrg` as an implicit tenant key.

## 6. Verification

Run the repository's Python tests for model and documentation consistency. A production Neo4j implementation additionally requires integration tests that execute every constraint, validation query, migration, rollback, concurrency, and recovery scenario against its supported Neo4j version.
