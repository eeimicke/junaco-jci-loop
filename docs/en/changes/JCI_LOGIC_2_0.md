# JCI logic 2.0: six coordinated corrections

[Deutsch](../../changes/JCI_LOGIC_2_0.md) · [English](JCI_LOGIC_2_0.md)

This change closes six gaps in revision handling, goal achievement, Task evaluation, concurrent changes and historical corrections. The ten core elements and existing entity and relationship types remain. The [context](../JCI_CONTEXT.md), [graph rules](../JCI_GRAPH_RULES.md) and [SYNC specification](../JCI_SYNC_SPEC.md) are authoritative.

The rule, snapshot, value and exchange profiles use version `2.0`. JSON-LD syntax version `1.1` and namespace `https://eeimicke.github.io/junaco-jci-loop/ns/jci/1.0#` identify different things and remain unchanged. The [snapshot payload schema](../../schemas/jci-history-snapshot.schema.json) describes new historical payloads; [legacy schemas](../../schemas/legacy/1.1/) remain available for older profiles.

## 1. Separate domain state from new proof records

The versioned relationship catalogue explicitly assigns domain relationship state by context and endpoint. An existing mutable entity receives exactly one new revision and one PiH within a successful request when this state or its properties actually change.

The new Verification owns `EVALUATES`, `CHECKS`, `USES_EVIDENCE` and `SUPERSEDES`. Its references do not increment revisions of the Result, criterion, Evidence or earlier Verification. Catalogued event, provenance, conflict and history references follow the same explicit assignment. Unknown relationship contexts must not silently be treated as revision-neutral; domain structure relationships follow their endpoint assignment.

A check of criterion revision 2 remains applicable when `CHECKS` is created. Only an actual criterion change produces revision 3 and makes it inapplicable to the new state. Supersession can nevertheless change the verification set while target revisions remain unchanged; step 5 protects this set. New PiH contain the assigned domain relationship state. Earlier PiH, data and hashes are not rewritten.

## 2. Distinguish historical assignment from current goal scope

Stored assignments remain; computed subsets are evaluated:

```text
T_all(G) = Tasks directly linked from G by DECOMPOSES_INTO
T_current(G) = {t in T_all(G) | t.status not in {REPLACED, REVOKED}}
K_current(G) = {k linked from G by HAS_SUCCESS_CRITERIA
                | k.status not in {REPLACED, REVOKED}}
```

`COMPLETED` remains a current contribution. `ACHIEVED` requires a nonempty current Task set, fully completed Tasks with satisfied prerequisites and at least one current `REQUIRED` criterion. Every current mandatory criterion must be `ACTIVE` and satisfied by applicable verifications. WHY, responsibility, roles, RaN and other conditions also apply. `DRAFT` mandatory criteria block achievement; empty sets do not establish success.

Replacement and revocation need a justified request and full RaN/impact evaluation. A successor is explicitly assigned to the same PiF1o and a valid current parent structure. `DEPENDS_ON` is not automatically redirected; a referenced replaced or revoked Task remains an unmet prerequisite.

Current Composite children are filtered likewise and must be nonempty. Revoking a Composite does not automatically revoke descendants. The request must resolve their hierarchy or explicitly replace or revoke them separately; otherwise the outcome is `CONFLICT`. The last current Task or mandatory criterion of a still-active goal may disappear only with valid replacement scope or another permitted goal status.

Only Results of currently included Tasks count towards current goal achievement. Reusing earlier work needs explicit adoption by current work with its own Result and traceable Evidence; old `PRODUCES` references are not reassigned. Historical proof remains. Terminal facts are not automatically reopened.

## 3. Evaluate Composite prerequisites before child aggregation

`COMPOSITE` remains a permitted source of `DEPENDS_ON`. Own prerequisites determine its status on release and block its completion while unmet. They are not automatically inherited by descendants; restrictions on their execution must be explicitly modelled.

For an already released Composite with initial status `ACTIVE` or `BLOCKED` and valid, nonempty current child scope, the following order applies:

| Condition                                                                 | Next status |
| ------------------------------------------------------------------------- | ----------- |
| Own prerequisite unmet                                                    | `BLOCKED`   |
| Own prerequisites satisfied, all current children completed               | `COMPLETED` |
| Own prerequisites satisfied, at least one child active                    | `ACTIVE`    |
| Own prerequisites satisfied, no child active, at least one blocked        | `BLOCKED`   |
| Own prerequisites satisfied, only drafts or drafts and completed children | `ACTIVE`    |

A released Composite does not return to `DRAFT`. A draft needs regular release with activation checks to `ACTIVE` or `BLOCKED`. At explicit composite release, the same prerequisite and child-blocking priority determines `ACTIVE` or `BLOCKED`; even if every child is completed, release first produces `ACTIVE`. Completion requires a later evaluation of that released state. Scope reduction alone produces neither release nor direct `DRAFT → COMPLETED`. Terminal Tasks are not reopened.

A Composite thus remains `BLOCKED` with an open own prerequisite despite completed children. If its last blocked child disappears and only drafts remain, `ACTIVE` applies after previous release and with own prerequisites satisfied.

## 4. Check hierarchy and prerequisites together for completion cycles

SYNC computes a completion graph over current Tasks of all PiF1o reached through hierarchy and prerequisites:

```text
C -> K : C is COMPOSITE and K is a current direct child
T -> P : T DEPENDS_ON P
```

Both arrows mean that the source cannot complete before the target. A combined cycle causes `CONFLICT` with the full path and original relationship types. Existing hierarchy and succession checks remain; replaced or revoked prerequisites remain visible and unmet. No new stored graph object type is created.

Atomic and composite Tasks are evaluated together with prerequisites first, followed by PiF1o and higher future states. The full candidate includes all new edges of the same request. Example: C contains A, A requires C. `C → A → C` is rejected although each relationship type is acyclic in isolation. Commit protection prevents concurrent requests from bypassing the combined check.

## 5. Protect the complete decision basis until commit

All JCI write paths use one shared technical database write lock for the entire model store, including across organisations. This includes revision-neutral proof records, events, corrections and migrations. The lock state is not a JCIEntity and receives no PiH.

The complete normalised request is immutably bound to `requestId` and `idempotencyKey`; the same key with different content is rejected. Before all authoritative reads, the lock is acquired within an explicit transaction and held until commit or rollback. Precomputation outside the lock is nonbinding.

The protected view includes properties, relationships, current sets and relevant absences: also new RaN, role/scope changes and superseded verifications with unchanged target revisions. Previously read entity revisions alone are insufficient.

All temporal conditions and dependent decisions are evaluated for the same final server-side domain decision time. The technical commit receipt records it; `completedAt` remains the completion time. Validity applies at this decision time; it does not promise a stopped clock until physical commit confirmation.

The domain delta, revisions, PiH, documentation, SyncEvent and technical success receipt are committed atomically. Technical run ownership prevents stale workers from committing. After response loss, the stored outcome of the same run ID is retrieved first. A revision conflict does not change `requestedRevision`; a new domain starting point needs a new request.

## 6. Address historical corrections stably and overlay them unambiguously

Profile 2.0 permits complete typed properties and complete relationship entries:

```text
/stateData/properties/<property>
/relationshipData/<direction:relationshipType:otherEntityId>
/relationshipData/<direction:relationshipType:otherEntityId>/properties/<property>
```

Example: `/stateData/properties/name`. A relationship key is `INCOMING:HAS_MEMBER:00000000-0000-0000-0000-000000000007`. Stored `relationshipData` remains a list; only addressing uses a virtual unique key map. Reordering does not change the address.

Root replacements, array indices, wildcards, append operators and descent into `TypedValue.value` are excluded. Identity, revision and relationship identity components are not reinterpreted under the same address. The snapshot schema determines permitted properties.

Paths are split into segments and decoded according to JSON Pointer. Equality or a segment prefix relation means overlap. `name` and `nameLong` are siblings; a whole relationship entry and its property overlap. Overlap within a new request is invalid.

| Affected active corrections | Outcome                                                   |
| --------------------------- | --------------------------------------------------------- |
| None                        | New correction without `SUPERSEDES`                       |
| Exactly one                 | Supersede that correction completely through `SUPERSEDES` |
| More than one               | `CONFLICT`, no automatic merge                            |

Complete supersession retains at least the predecessor's canonical paths and their still-valid values. Additional paths must not overlap each other or other active corrections; switching between a property and a whole relationship does not happen implicitly.

`ADDITION` requires a missing path. Existing `NULL` is present and does not mean deletion. `CORRECTION` and `CLARIFICATION` require existing paths. `previousValue` is checked at acceptance against the effective view at that time. Later HistoryViews overlay unchanged PiH with absolute `correctedValue` values of corrections that have not been superseded; the earlier precondition is not rechecked against the original PiH.

Hashing uses effective `stateData` and the canonically sorted `relationshipData` list according to the versioned serialisation profile, not the virtual key map. Shared test vectors check encoding, sorting and exact number handling. Older profiles retain their own resolvers.

## Effects on the ten core elements

| Core element | Domain effect                                                                                                                  |
| ------------ | ------------------------------------------------------------------------------------------------------------------------------ |
| CiV          | Values and human value decisions remain authoritative; state ownership for selected historical context is explicitly assigned. |
| PiF2         | Purpose and the WHY path remain; derived goal statements use a consistent protected basis.                                     |
| PiF1s        | Strategic aggregation follows corrected operational and tactical evaluation.                                                   |
| PiF1t        | Tactical aggregation follows valid Task and PiF1o evaluation.                                                                  |
| PiF1o        | Nonempty current Task and mandatory-criterion sets separate goal achievement from superseded work.                             |
| RaN          | Rule types remain; new rules, scope and temporal validity are considered at commit.                                            |
| RoF          | Responsibility, roles and scope decisions remain subject to checks; technical locks are not organisation objects.              |
| ERoF         | Usage and ownership relationships remain conditions; relevant environmental context belongs to the protected decision basis.   |
| SYNC         | The candidate, completion graph, revision assignment and protected commit are evaluated together.                              |
| PiH          | New snapshots/corrections use 2.0; existing data, identities and hashes remain unchanged.                                      |

Cardinalities of existing stored relationships remain. Additional evaluation rules cover nonempty current sets, consistent current subtrees, combined cycles and correction paths without overlap. No new edges or automatic successor assignments are created. State ownership is catalogue metadata; the completion graph and correction key map are computed views.

## Shared sequence and 23 acceptance cases

The six steps apply together. Under the lock, the full candidate is formed, state ownership and current sets determined, the completion graph checked, prerequisites and Composite status evaluated, and proof and goal achievement checked. Relevant corrections are checked against the protected HistoryView. Temporal validity and the final candidate are confirmed before atomic commit.

| No. | Acceptance case                                                | Expected outcome                                               |
| --- | -------------------------------------------------------------- | -------------------------------------------------------------- |
| 1   | Verification binds criterion 2 and creates `CHECKS`            | Criterion stays at 2; verification applicable.                 |
| 2   | Criterion subsequently changes in domain state                 | Revision 3; old verification remains and becomes inapplicable. |
| 3   | New verification supersedes one for the same revisions         | Target revisions unchanged; current verification set changes.  |
| 4   | Event references SYNC and affected entities                    | No history creation solely because of documentation.           |
| 5   | T1 `REPLACED`, T2 `COMPLETED`, remaining conditions satisfied  | T1 remains assigned and does not block the goal.               |
| 6   | All current Tasks or mandatory criteria would disappear        | No automatic success; invalid active scope is rejected.        |
| 7   | Revoked Composite with unresolved current descendants          | `CONFLICT`, no invisible subtree revocation.                   |
| 8   | Composite children completed, own prerequisite open            | `BLOCKED`.                                                     |
| 9   | Released Composite has only `DRAFT` children left              | With own prerequisites satisfied, `ACTIVE`.                    |
| 10  | `DRAFT` Composite loses open children through revocation       | No automatic `COMPLETED`.                                      |
| 11  | C contains A, A requires C                                     | Mixed cycle is rejected.                                       |
| 12  | Two new edges jointly form a cycle                             | Entire request is rejected.                                    |
| 13  | Concurrent requests jointly form a cycle or over-allocation    | Second commit considers first and is rejected where necessary. |
| 14  | Relevant RaN, role or scope changes after precomputation       | Completion uses new basis or reports conflict.                 |
| 15  | New prohibiting RaN appears after precomputation               | It is considered despite earlier absence.                      |
| 16  | `VALID` is superseded by `INVALID`, target revisions unchanged | Concurrent goal aggregation must not use old verification set. |
| 17  | Role expires while waiting for lock                            | Final temporal check considers expiry.                         |
| 18  | Success stored, response lost                                  | Recovery does not execute domain change again.                 |
| 19  | Correction targets parent path and descendant path             | Overlap is detected.                                           |
| 20  | Pointer comparison of `name` and `nameLong` (syntax only)      | No false prefix conflict.                                      |
| 21  | Relationship list is only reordered                            | Stable address denotes the same relationship.                  |
| 22  | Added field is later completely superseded                     | Effective view contains latest absolute correction value.      |
| 23  | Existing PiH use older snapshot profile                        | No retroactive change to data or hashes.                       |

## Migration and limits of reference validation

Before activation, existing data are checked for mixed cycles, unclear replacement contexts, empty current scope, inconsistent Composite statuses and problematic correction paths. Unclear cases need a traceable request. Terminal facts are not automatically recalculated. Old PiH, corrections and hashes retain their profiles; unclear legacy cases are not migrated by silently reinterpreting paths.

Old exchanged data are read against their [legacy schemas](../../schemas/legacy/1.1/). New writes use profiles 2.0 and current [schemas](../../schemas/). The namespace, JSON-LD syntax version and domain profile versions remain separate.

The [reference functions](../../../reference/jci_rules.py) and [rule tests](../../../tests/test_model_rules.py) check executable rule portions. The [specification checks](../../../tests/test_spec_consistency.py) check document and artifact consistency. The helper is not a production SYNC engine, a complete Neo4j adapter or an implementation of all domain write paths.

The 23 cases describe required acceptance, not evidence of a production-tested SYNC version. Concurrent transactions, lock ownership, worker failure, response loss, actual atomicity and temporal expiry additionally need tests with real database transactions and controlled pause points. Static queries and pure function checks do not establish these properties.

Validation for this change covers executable rule and schema checks, the shared [hash fixtures](../../../tests/fixtures/history-profile-2.0.json), and the [regression tests](../../../tests/test_reference_rules.py). Run from the repository root with `python -B -m unittest discover -s tests -v`. German and English chapter, table, code-block, and identifier structures are checked together. The reference functions receive complete candidate data; authorization and a production database adapter remain caller responsibilities.

Validation recorded on 2026-09-07: **81 tests passed**, including 41 new reference regressions. All 18 German/English pairs passed structural comparison; local links, aligned tables, canonical identifiers, schemas, and Mermaid relationship names were checked. The earlier 1.1 schema contents remain preserved. No live Neo4j transaction or migration was run.

## Additional implementation on 2026-09-12

The subsequently identified identity defect in whole-relationship corrections is fixed. `CORRECTION` and `CLARIFICATION` compare the relationship with the immediately preceding effective view, including after an earlier `ADDITION`. Direction, relationship type, other-entity ID and other-entity type remain unchanged, including within stored supersession chains. New regressions check forbidden identity changes and valid relationship-property changes; original PiH and hashes remain unchanged.

The new [Neo4j transaction coordinator](../implementations/neo4j/JCI_NEO4J_RUNTIME.md) implements the shared gate, durable requests and runs, fencing, explicit retry scheduling, and atomic success receipts and outbox records. Finally validated read and change evidence is bound to the decision; existing owners cannot be treated as new entities. A confirmed worker exit is first resolved and documented under the same lock before a new attempt is scheduled.

The [integration tests](../../../tests/integration/test_neo4j_transactions.py) use an isolated local Neo4j instance and an explicitly limited test rules package. They check real concurrency, revision-neutral and previously absent decision data, revision and package conflicts, temporal expiry, rollback, lost acknowledgements, retries, and a worker process exiting before commit. [Docker Compose](../../../compose.neo4j-test.yml) and a separate [CI job](../../../.github/workflows/validate.yml) make this test path reproducible. The historical validation record above is preserved.

This establishes the technical transaction framework. The complete domain rules package, trusted identity and approval checks, integration of all write paths, and outbox delivery remain integration work. Existing data additionally require verified legacy-profile resolvers and a concrete migration; no such migration was performed here.

Additional validation recorded on 2026-09-12: **175 tests passed**, including **17 real Neo4j transaction tests** and 18 coordinator unit tests. The local run uses Neo4j Community 2026.08.1, Python driver 6.3.0, and portable Java 21. All 20 German/English pairs pass structural checks; identifiers, tables, and local links are checked. The new GitHub Actions job is configured but has not yet run on GitHub for this working state. Server or power failure was not tested.
