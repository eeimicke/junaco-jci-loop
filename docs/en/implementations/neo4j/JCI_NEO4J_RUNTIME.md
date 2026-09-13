# JCI Neo4j runtime

This runtime connects the JCI reference checks to real, explicit Neo4j transactions. The technical coordinator is implemented in [`jci_runtime/neo4j_store.py`](../../../../jci_runtime/neo4j_store.py). The [canonical context](../../JCI_CONTEXT.md), [SYNC specification](../../JCI_SYNC_SPEC.md), and [Neo4j schema](JCI_NEO4J_SCHEMA.md) remain authoritative.

The coordinator provides the technical transaction boundary. A complete, trusted rule bundle must still validate domain decisions, authorization, and all model conditions. The existing reference modules implement selected rules and the approval profile; using them alone does not provide a complete production SYNC engine.

## 1. Technical boundary and domain responsibilities

All JCI write paths in the same model store require the same technical write gate. The lock is acquired before decision-relevant reads and held until commit or rollback. It applies across organizational boundaries. Any additional write path that bypasses this contract would invalidate the guarantee of a consistent decision basis.

Neo4j uses Read Committed by default. Writing and then removing a temporary property on the shared gate acquires the required write lock; the lock remains until the transaction ends. This follows the [official description of concurrent data access](https://neo4j.com/docs/operations-manual/current/database-internals/concurrent-data-access/).

The coordinator uses explicit driver transactions. Errors, particularly an unknown commit outcome, require deliberate recovery; automatically executing a domain callback again would not provide an adequate contract. The driver foundation is documented in [Run your own transactions](https://neo4j.com/docs/python-manual/current/transactions/).

The verified rule bundle must match the active `SYNC` definition being used, its profile versions, and its `implementationChecksum`. Protected operations require support for `approvalProfileVersion = "1.0"`. Neither the mere existence of a definition nor a package identifier asserted by the requester grants execution authority.

Domain validation and write functions run inside the transaction opened by the coordinator. They must freshly read the complete relevant view, including required absences, validate the entire candidate, and evaluate time conditions at the server-provided `decisionAt`. They must not open their own transaction or trigger external side effects. There is no default validator that permits domain changes.

## 2. Concrete API and required rule bundle

`Neo4jStore(driver, *, database, rules, transaction_timeout=30)` accepts a caller-managed Neo4j driver. The database must be supplied explicitly. The constructor opens no connection, installs no structures, and changes no graph. `transaction_timeout` bounds the transaction duration, including time spent waiting for locks.

| Method                                                        | Contract                                                                                                                                                   |
| ------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `install()`                                                   | Idempotently installs technical constraints and the gate. An administrative setup step; no domain bootstrap.                                               |
| `accept(payload, *, run_id)`                                  | Checks the transport profile, active SYNC definition, and target revision; atomically stores the request and first run after a successful acceptance hook. |
| `claim(run_id, worker_id, *, expected_fence=None)`            | Claims an unfinished run with a new fencing token; taking over a running run requires its current token to be supplied explicitly.                         |
| `retry(previous_run_id, *, run_id)`                           | Schedules exactly one new run for the same unchanged request after documented `FAILED` or `CONFLICT`; repeated scheduling is idempotent.                   |
| `execute(token)`                                              | Performs exactly one guarded attempt and returns the confirmed result; no automatic repetition of hooks.                                                   |
| `recover(run_id)`                                             | Reads the durable run state, current token, and any existing result under the gate.                                                                        |
| `finish_failed(token, *, outcome, error_code, error_message)` | Explicitly documents `FAILED` or `CONFLICT` after the outcome has been resolved; does not execute the domain delta again.                                  |

`accept` returns `AcceptedRequest(request_id, idempotency_key, run_id)`. Identical retransmission returns the already scheduled first run; supplying a new run ID does not schedule a second attempt. `claim` returns `RunToken(request_id, run_id, worker_id, fence)`. `recover` returns `Recovery(state, token, result)`; possible states are `QUEUED`, `RUNNING`, `SUCCESS`, `CONFLICT`, and `FAILED`.

The scheduler explicitly decides when a running run should be taken over. It first calls `recover(run_id)` and uses the returned `token.fence` as `expected_fence`. The coordinator implements neither automatic worker-failure detection nor lease renewal. A stale token loses write authority; an already completed result can be read unchanged.

`retry(previous_run_id, *, run_id)` returns `AcceptedRequest` and explicitly schedules exactly one new attempt after an already documented `FAILED` or `CONFLICT`. The payload, `requestedRevision`, `requestId`, `idempotencyKey`, and `ChangeEvent` remain unchanged; only the new run receives a new identity. Repeating the same scheduling request with the same run ID is idempotent. A different second successor ID is rejected. A running attempt or unknown outcome must first be reconciled and completed. An already successful request is not scheduled again; repeating an existing successor scheduling request creates no additional run.

`recover` continues to refer to the specified attempt: the result of an earlier `FAILED` or `CONFLICT` remains readable after a later `SUCCESS` for the same request. Retrying against the unchanged, now stale target revision does not resolve a revision conflict; a different desired starting revision requires a new request.

The `rules` object must provide `package = RulePackage(sync_id, sync_revision, implementation_checksum, schema_version="2.0", approval_profile_version="1.0")` and all of the following methods:

| Hook                                                                         | Required responsibility                                                                                                                               |
| ---------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| `accept(tx, payload, run_id, accepted_at)`                                   | Authenticate the requester, derive approval requirements, verify human receipts, and persist the immutable ChangeEvent and provenance.                |
| `evaluate(tx, payload)`                                                      | Read the complete current basis and build a candidate mapping containing `readRevisions` and unique `changedEntityIds`.                               |
| `validate_at(tx, payload, candidate, context)`                               | Recheck all time-dependent model and approval conditions at `context.decision_at`; only `True` permits writing.                                       |
| `apply(tx, payload, candidate, context)`                                     | Persist the validated owner delta, PiH, required technical approval-enrollment latches, SyncEvent, and provenance; return a complete `JCISyncResult`. |
| `document_failure(tx, payload, context, outcome, error_code, error_message)` | Write only completion and, where applicable, conflict records; return a complete `JCISyncResult`.                                                     |

`ExecutionContext` contains `request_id`, `run_id`, `worker_id`, `fence`, `graph_epoch`, `started_at`, and `decision_at`. Hooks must not modify the coordinator's technical request, run, commit, or outbox records. Their query results must be consumed inside the supplied transaction. Unsupported rules or operations must be rejected.

After `validate_at`, the coordinator freezes `readRevisions` and `changedEntityIds` and checks the declared read revisions against the locked graph. Owners declared as new must actually be absent from the graph before `apply`; existing changed owners require their authoritative read revision. After `apply`, it checks revision `+1` and exactly one associated PiH with matching `originalEntityId` and `originalRevision` for existing changed owners; new owners start at revision 1 without PiH. These limited persistence checks complement the rule bundle's obligation to derive the complete actual domain delta correctly.

The coordinator compares package identity and checksum with the stored active SYNC definition. The trusted installation must first establish that the checksum actually identifies the loaded, reviewed implementation artifact. The coordinator does not hash arbitrary Python objects or supply missing domain validation. In particular, supplied revision and change lists alone do not prove their domain completeness.

The following integration example assumes an initialized gate, a matching active SYNC definition, and the complete trusted rule bundle:

```python
from jci_runtime.neo4j_store import Neo4jStore


def process_request(driver, trusted_rules, payload, run_id, worker_id):
    store = Neo4jStore(driver, database="neo4j", rules=trusted_rules)
    accepted = store.accept(payload, run_id=run_id)
    previous = store.recover(accepted.run_id)
    if previous.result is not None:
        return previous.result
    token = store.claim(accepted.run_id, worker_id)
    return store.execute(token)
```

The caller handles `CommitOutcomeUnknown` by calling `recover` for the same run ID. An ordinary validation error likewise requires reconciliation first and, where appropriate, `finish_failed` afterwards. The function shown is not an automatic retry loop. The UI and storage of pending or rejected approval proposals, authentication, and outbox delivery and acknowledgement require separate integrations.

## 3. Durable requests and guarded completion

Acceptance immutably binds the complete canonical payload to `requestId` and `idempotencyKey`. The target, requested revision, profiles, operations, and any approval receipts remain recoverable. The same request may be retried technically; a different starting revision or content requires a new request.

A technical run has its own `runId` and fencing token. When another worker takes ownership, the previous owner must no longer commit domain changes or conflicting completion records. Recovery also uses the shared gate and first checks the durably recorded outcome.

For `SUCCESS`, the domain delta, associated `PiH`, relationships, historical corrections, exactly one `SyncEvent`, the success receipt, and the outbox belong to the same atomic transaction. The actual domain delta determines revisions and counts. New targets start at revision 1 without their own PiH; changed existing owners receive exactly one new revision and one PiH. A no-op creates no fictitious history and is still durably marked as processed.

A confirmed rollback commits no domain delta. Required `FAILED` or `CONFLICT` completion records are subsequently written under the gate. If the commit outcome is unknown, the receipt for the same `runId` must be read first. The domain change must not run again until the outcome has been resolved. An already stored success is returned unchanged.

The technical `graphEpoch` makes revision-neutral JCI writes visible as well. It replaces neither the gate nor final time validation. `decisionAt` identifies the guarded domain decision time; `completedAt` identifies completion. This does not guarantee validity when a later external action occurs.

Outbox contents are delivered only after commit. The same message may be delivered again after a dispatcher crash. The recipient must deduplicate using the stable event identifier; a successful domain transaction does not automatically imply an external effect executed exactly once.

## 4. Installation and real integration tests

Install the dependencies from the repository root:

```powershell
python -m pip install -r requirements-dev.txt
python -m pip install -r requirements-runtime.txt
```

[`compose.neo4j-test.yml`](../../../../compose.neo4j-test.yml) provides a local test instance. It uses the official Community image `neo4j:2026.08.1`, publishes only Bolt on `127.0.0.1:17687`, and mounts no host data directories. HTTP/HTTPS are disabled. Disabled authentication applies exclusively to this isolated local test service. The Community tag has no edition suffix; see [Neo4j in Docker](https://neo4j.com/docs/operations-manual/current/docker/introduction/).

With Docker running and Docker Compose available, start the instance and wait until it is ready:

```powershell
docker compose -f compose.neo4j-test.yml up -d --wait
```

`--wait` respects the configured healthcheck; see [docker compose up](https://docs.docker.com/reference/cli/docker/compose/up/). If another local test instance already uses port 17687, either use that instance or stop it first.

The integration tests require a Neo4j instance dedicated exclusively to testing. The following invocation uses the default database `neo4j`; adapt the URI to your own isolated instance:

```powershell
$env:JCI_NEO4J_TEST_URI = "bolt://127.0.0.1:17687"
$env:JCI_NEO4J_TEST_CONFIRM = "isolated"
$env:JCI_NEO4J_TEST_DATABASE = "neo4j"
python -B -m unittest discover -s tests/integration -v
```

If the test instance requires authentication, additionally set `JCI_NEO4J_TEST_USER` and `JCI_NEO4J_TEST_PASSWORD` from a protected local configuration. Credentials belong neither in this documentation nor in the repository. The confirmation `isolated` deliberately identifies a disposable test store; production or shared databases are not valid test targets.

`JCI_NEO4J_TEST_DATABASE` is optional and defaults to `neo4j`. The tests create their own objects with fresh UUIDs and perform no database reset or global deletion. Test data remains in the isolated instance for inspection.

After testing, remove only the Compose test service and its associated disposable volumes:

```powershell
docker compose -f compose.neo4j-test.yml down --volumes
```

This discards the local test data belonging to this instance; see [docker compose down](https://docs.docker.com/reference/cli/docker/compose/down/). The `neo4j-integration` job in [GitHub Actions](../../../../.github/workflows/validate.yml) starts the same image tag as an isolated service and runs integration tests for pull requests and pushes to `main`. Bolt is exposed through local port 7687 there.

The suite checks concurrent requests, newly appearing and revision-neutral decision data, target and package revisions, expiry times, rollback, stale fencing tokens, lost responses during `accept` and `execute`, explicit attempts scheduled through `retry`, final read evidence, and attempts to tamper with that evidence. A separate case terminates a real worker process before commit and subsequently checks rollback, recovery, and retry.

These cases use the real transaction coordinator with a limited test rule bundle. They do not establish resilience to server or power failure and replace neither a complete domain-level JCI end-to-end test nor production identity integration. A test run skipped because no database is configured is not evidence of transaction isolation. The pure reference suite remains separately executable:

```powershell
python -B -m unittest discover -s tests -v
```

## 5. Historical corrections and existing data

The reference correction compares complete relationship entries with the immediately preceding effective `HistoryView`. This also applies when an earlier `ADDITION` introduced the relationship. `CORRECTION` and `CLARIFICATION` must not change direction, relationship type, counterpart ID, or counterpart type under the same address. Reconstruction additionally checks identities along the stored `SUPERSEDES` chain.

Valid changes to relationship properties remain possible. The view still overlays only active absolute `correctedValue` values on the unchanged original. Earlier `previousValue` conditions are not checked again against the original PiH. Regressions cover both the prohibited type change and valid successive changes to `validFrom` and `validUntil`.

Setting up technical runtime structures is neither a domain bootstrap nor an automatic data migration. For an existing store, profiles, valid states, revision ownership, Task and criterion scopes, mixed completion cycles, and historical correction chains must be checked before activation. Ambiguous cases require traceable domain decisions.

Old PiH, corrections, and stored hashes remain unchanged. Every legacy profile actually present requires an explicitly reviewed resolver; preserved legacy schemas alone do not implement that resolver. The coordinator invents neither historical approvals nor new identities and does not automatically rewrite old snapshots to profile 2.0. Pre-/post-validation, backup, and a concrete migration remain a separate introduction step when legacy data exists.

## 6. Effects on the loop and remaining integration

All ten core elements retain their domain meaning: `CiV` preserves human value decisions; `PiF2`, `PiF1s`, `PiF1t`, and `PiF1o` retain their future-state and contribution logic; `RaN` provides rules; `RoF` provides verified actors; and `ERoF` provides separate environmental and usage conditions. `SYNC` gains an executable technical transaction boundary. `PiH` is still created only when existing states are actually superseded. WHY traceability remains intact, and technical runtime records do not become additional JCI core elements.

Production introduction requires the complete versioned rule bundle, trusted identity and approval verification, all domain write paths, operational access controls, the outbox recipient, and any required legacy-profile resolver to be available together. A test rule bundle must not be registered as a production model validator. The technical transaction layer does not decide unresolved domain specification questions.
