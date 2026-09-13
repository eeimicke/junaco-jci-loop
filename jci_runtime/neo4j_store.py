"""Explicit, driver-backed JCI transaction coordinator.

This is a persistence adapter, not a complete JCI evaluator or authentication
service. A trusted, version-bound rules integration is mandatory. Its hooks may
use only the supplied transaction, must consume query results, and must not
commit, open transactions, change technical ledger records, or perform external
effects. Deployment must deny bypass writes. Outbox delivery is intentionally
outside this module; consumers must deduplicate by eventId.

Lock/transaction API sources:
https://neo4j.com/docs/operations-manual/current/database-internals/concurrent-data-access/
https://neo4j.com/docs/python-manual/current/transactions/
"""

from contextlib import contextmanager
from copy import deepcopy
from dataclasses import asdict, dataclass
from datetime import datetime
from hashlib import sha256
from pathlib import Path
import re
from typing import Any, Mapping, Protocol
from uuid import UUID

from jsonschema import Draft202012Validator, FormatChecker

from reference.jci_rules import canonical_json, parse_exact_json


class StoreError(RuntimeError):
    """The requested persistence operation did not return confirmed success."""


class StoreNotInitialized(StoreError):
    pass


class ProfileMismatch(StoreError):
    pass


class RequestConflict(StoreError):
    pass


class RunNotFound(StoreError):
    pass


class RunOwnershipError(StoreError):
    pass


class RunCompleted(StoreError):
    pass


class RevisionConflict(StoreError):
    pass


class InvalidBundle(StoreError):
    pass


class CommitOutcomeUnknown(StoreError):
    """Inspect durable state before further action; no hook is retried here."""

    def __init__(self, operation, run_id=None):
        self.operation, self.run_id = operation, run_id
        super().__init__(f"{operation} commit not confirmed; recover run {run_id!r}")


@dataclass(frozen=True)
class RulePackage:
    sync_id: str
    sync_revision: int
    implementation_checksum: str
    schema_version: str = "2.0"
    approval_profile_version: str = "1.0"


@dataclass(frozen=True)
class AcceptedRequest:
    request_id: str
    idempotency_key: str
    run_id: str


@dataclass(frozen=True)
class RunToken:
    request_id: str
    run_id: str
    worker_id: str
    fence: int


@dataclass(frozen=True)
class Recovery:
    state: str
    token: RunToken | None
    result: Mapping | None


@dataclass(frozen=True)
class ExecutionContext:
    request_id: str
    run_id: str
    worker_id: str
    fence: int
    graph_epoch: int
    started_at: Any
    decision_at: Any


class Rules(Protocol):
    """Trusted integration: all domain/authorization checks remain mandatory.

accept must authenticate the requester, classify approval requirements from
both graph states, verify human receipts/route/time, and persist the immutable
ChangeEvent and provenance. evaluate reads the complete current graph basis and
returns a candidate mapping containing readRevisions and changedEntityIds.
validate_at repeats time-dependent and approval checks at context.decision_at;
only literal True authorizes apply. apply persists the fully validated owned
delta, PiH, enrollment latches, SyncEvent and provenance and returns a complete
JCISyncResult. document_failure writes only failure/conflict documentation.
Every unsupported rule/operation must raise. No supplied default approves work.
"""

    package: RulePackage

    def accept(self, tx, payload, run_id, accepted_at): ...
    def evaluate(self, tx, payload) -> Mapping: ...
    def validate_at(self, tx, payload, candidate, context) -> bool: ...
    def apply(self, tx, payload, candidate, context) -> Mapping: ...
    def document_failure(self, tx, payload, context, outcome, error_code,
                         error_message) -> Mapping: ...


LOCK = """// jci:lock
MATCH (gate:JCITechnicalGate {key: 'MODEL_WRITE'})
SET gate._lock = true REMOVE gate._lock
RETURN gate.graphEpoch AS graphEpoch"""

TERMINAL = frozenset({"SUCCESS", "CONFLICT", "FAILED"})
COUNTERS = ("affectedCount", "changedCount", "historyCount", "correctionCount", "conflictCount")


def _uuid(value):
    try:
        valid = isinstance(value, str) and str(UUID(value)) == value
    except (ValueError, TypeError, AttributeError):
        valid = False
    if not valid:
        raise InvalidBundle("identity must be a canonical UUID")
    return value


def _json(value):
    return canonical_json(value).decode("utf-8")


def _instant(value):
    if hasattr(value, "to_native"):
        value = value.to_native()
    if isinstance(value, str):
        value = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if not isinstance(value, datetime) or value.tzinfo is None:
        raise InvalidBundle("timezone-aware persisted timestamp required")
    return value


def _one(tx, query, **parameters):
    rows = list(tx.run(query, **parameters))
    if len(rows) != 1:
        raise InvalidBundle("expected exactly one database record")
    return rows[0]


class Neo4jStore:
    """Use a caller-owned neo4j.Driver; never creates credentials/connections.

Every method uses a fresh WRITE session and explicit transaction. install is
an explicit administrative schema step, never performed by the constructor.
The transaction timeout bounds waiting and execution, not the domain decision
time, which is always obtained from the server after locking.
"""

    def __init__(self, driver, *, database, rules: Rules, transaction_timeout=30):
        if not isinstance(database, str) or not database.strip():
            raise ValueError("explicit database is required")
        if not isinstance(transaction_timeout, (int, float)) or transaction_timeout <= 0:
            raise ValueError("positive transaction timeout required")
        package = getattr(rules, "package", None)
        if not isinstance(package, RulePackage):
            raise ProfileMismatch("a trusted RulePackage is required")
        if (package.schema_version != "2.0" or package.approval_profile_version != "1.0"
                or type(package.sync_revision) is not int or package.sync_revision < 1
                or not re.fullmatch(r"[0-9a-f]{64}", package.implementation_checksum)):
            raise ProfileMismatch("unsupported or incomplete rule package")
        _uuid(package.sync_id)
        for method in ("accept", "evaluate", "validate_at", "apply", "document_failure"):
            if not callable(getattr(rules, method, None)):
                raise InvalidBundle("mandatory rule hook missing: " + method)
        self.driver, self.database, self.rules = driver, database, rules
        self.package, self.transaction_timeout = package, transaction_timeout
        self.package_json = _json(asdict(package))
        folder = Path(__file__).resolve().parents[1] / "docs" / "schemas"
        request = parse_exact_json((folder / "jci-change-request.schema.json").read_text(encoding="utf-8"))
        envelope = parse_exact_json((folder / "jci-approval-envelope.schema.json").read_text(encoding="utf-8"))
        # Inline the known relative schema; runtime validation never fetches URLs.
        envelope["properties"]["proposal"] = request
        result = parse_exact_json((folder / "jci-sync-result.schema.json").read_text(encoding="utf-8"))
        self.validators = {"request": Draft202012Validator(request, format_checker=FormatChecker()),
                           "envelope": Draft202012Validator(envelope, format_checker=FormatChecker()),
                           "result": Draft202012Validator(result, format_checker=FormatChecker())}

    @contextmanager
    def _transaction(self, *, lock=True):
        with self.driver.session(database=self.database, default_access_mode="WRITE") as session:
            with session.begin_transaction(timeout=self.transaction_timeout) as tx:
                epoch = None
                if lock:
                    rows = list(tx.run(LOCK))
                    if len(rows) != 1 or type(rows[0]["graphEpoch"]) is not int:
                        raise StoreNotInitialized("exactly one initialized MODEL_WRITE gate is required")
                    epoch = rows[0]["graphEpoch"]
                yield tx, epoch

    @staticmethod
    def _commit(tx, operation, run_id=None):
        try:
            tx.commit()
        except Exception as error:
            raise CommitOutcomeUnknown(operation, run_id) from error

    @staticmethod
    def _advance(tx):
        tx.run("""// jci:epoch
MATCH (g:JCITechnicalGate {key: 'MODEL_WRITE'})
SET g.graphEpoch = g.graphEpoch + 1""").consume()

    @staticmethod
    def _now(tx):
        return _one(tx, "// jci:clock\nRETURN datetime.realtime() AS now")["now"]

    def install(self):
        """Idempotent technical installation. No bootstrap or domain writes."""
        constraints = (
            ("jci_technical_gate_key_unique", "JCITechnicalGate", "key"),
            ("jci_technical_request_key_unique", "JCITechnicalRequest", "idempotencyKey"),
            ("jci_technical_request_id_unique", "JCITechnicalRequest", "requestId"),
            ("jci_technical_run_id_unique", "JCITechnicalRun", "runId"),
            ("jci_technical_commit_request_unique", "JCITechnicalCommit", "idempotencyKey"),
            ("jci_technical_commit_run_unique", "JCITechnicalCommit", "runId"),
            ("jci_technical_outbox_event_unique", "JCITechnicalOutbox", "eventId"),
            ("jci_entity_id_unique", "JCIEntity", "id"),
            ("jci_sync_event_run_unique", "SyncEvent", "runId"),
        )
        # Schema and data operations cannot share a Neo4j transaction. Each
        # schema statement is independently resumable after an unknown reply.
        for name, label, property_name in constraints:
            with self._transaction(lock=False) as (tx, _):
                tx.run(f"CREATE CONSTRAINT {name} IF NOT EXISTS FOR (n:{label}) REQUIRE n.{property_name} IS UNIQUE").consume()
                self._commit(tx, "install constraint")
        with self._transaction(lock=False) as (tx, _):
            tx.run("""// jci:install
MERGE (g:JCITechnicalGate {key: 'MODEL_WRITE'})
ON CREATE SET g.graphEpoch = 0""").consume()
            self._commit(tx, "install gate")

    def _payload(self, payload):
        frozen = parse_exact_json(_json(payload))
        envelope = "proposal" in frozen
        if (envelope and frozen.get("approvalProfileVersion") != "1.0"
                or not envelope and frozen.get("schemaVersion") != "2.0"):
            raise ProfileMismatch("unsupported request profile")
        try:
            self.validators["envelope" if envelope else "request"].validate(frozen)
        except Exception as error:
            raise InvalidBundle("invalid request schema") from error
        proposal = frozen["proposal"] if envelope else frozen
        _uuid(proposal["requestId"])
        _uuid(proposal["target"]["id"])
        if envelope and frozen["requestHash"] != sha256(canonical_json(proposal)).hexdigest():
            raise RequestConflict("approval request hash differs from proposal")
        if any(op.get("relationshipType") == "APPROVED_BY" for op in proposal.get("operations", [])):
            raise InvalidBundle("approval provenance cannot be a generic operation")
        return frozen, proposal

    def _package(self, tx):
        row = _one(tx, """// jci:package
MATCH (s:JCIEntity:SYNC {id: $id})
RETURN s.status AS status, s.revision AS revision, s.definitionJson AS definitionJson""", id=self.package.sync_id)
        if row["status"] != "ACTIVE" or row["revision"] != self.package.sync_revision:
            raise ProfileMismatch("SYNC is not active at the bound revision")
        try:
            definition = parse_exact_json(row["definitionJson"])
        except Exception as error:
            raise ProfileMismatch("invalid persisted SYNC definition") from error
        if (any(definition.get(key) != "2.0" for key in (
                "definitionSchemaVersion", "ontologyVersion", "graphRulesVersion", "syncSpecVersion"))
                or definition.get("approvalProfileVersion") != "1.0"
                or definition.get("implementationChecksum") != self.package.implementation_checksum):
            raise ProfileMismatch("persisted SYNC/package profile mismatch")

    @staticmethod
    def _revision(tx, proposal):
        rows = list(tx.run("""// jci:revision
MATCH (e:JCIEntity {id: $id}) RETURN e.entityType AS entityType, e.revision AS revision""", id=proposal["target"]["id"]))
        if proposal["changeType"] == "CREATED":
            if rows:
                raise RevisionConflict("CREATED target already exists")
        elif (len(rows) != 1 or rows[0]["revision"] != proposal["requestedRevision"]
              or rows[0]["entityType"] != proposal["target"]["entityType"]):
            raise RevisionConflict("requested target type/revision differs")

    def _acceptance_bundle(self, tx, proposal, payload):
        row = _one(tx, """// jci:acceptance-bundle
MATCH (e:JCIEntity:ChangeEvent {id: $id})
RETURN properties(e) AS event,
 [(e)-[:REQUESTED_BY]->(a:JCIEntity:RoleAssignment) | a.id] AS requesters,
 [(e)-[r:APPROVED_BY]->(a:JCIEntity:RoleAssignment) |
  {roleAssignmentId: a.id, receiptId: r.receiptId, decidedAt: r.decidedAt,
   requestHash: r.requestHash, approvalHash: r.approvalHash}] AS approvals""", id=proposal["requestId"])
        event = row["event"]
        expected = {"entityType": "ChangeEvent", "status": "RECORDED", "revision": 1,
                    "idempotencyKey": proposal["idempotencyKey"], "changeType": proposal["changeType"],
                    "targetEntityId": proposal["target"]["id"], "targetEntityType": proposal["target"]["entityType"]}
        if (any(event.get(key) != value for key, value in expected.items())
                or event.get("requestedRevision") != proposal["requestedRevision"]
                or row["requesters"] != [proposal["requestedByRoleAssignmentId"]]):
            raise InvalidBundle("acceptance did not persist the bound ChangeEvent/requester")
        if "proposal" in payload:
            receipts = payload["receipts"]
            if (len({r["roleAssignmentId"] for r in receipts}) != len(receipts)
                    or len({r["receiptId"] for r in receipts}) != len(receipts)
                    or any(r["outcome"] != "APPROVED" or r["requestHash"] != payload["requestHash"]
                           or r["contextHash"] != payload["contextHash"] for r in receipts)):
                raise InvalidBundle("approval receipts are rejected, duplicated or differently bound")
            expected_approvals = {
                r["roleAssignmentId"]: (r["receiptId"], _instant(r["decidedAt"]),
                    r["requestHash"], sha256(canonical_json(r)).hexdigest()) for r in receipts}
            actual = row.get("approvals", [])
            try:
                actual_approvals = {r["roleAssignmentId"]: (
                    r["receiptId"], _instant(r["decidedAt"]), r["requestHash"], r["approvalHash"])
                    for r in actual}
            except (KeyError, TypeError, ValueError) as error:
                raise InvalidBundle("incomplete persisted approval provenance") from error
            if len(actual) != len(receipts) or actual_approvals != expected_approvals:
                raise InvalidBundle("persisted APPROVED_BY differs from immutable receipts")

    def accept(self, payload, *, run_id):
        """Atomically accept a validated request and schedule its first run.

The same immutable payload returns its existing first run. A new run ID in an
idempotent retransmission does not schedule a duplicate execution.
"""
        _uuid(run_id)
        payload, proposal = self._payload(payload)
        request_id, key = proposal["requestId"], proposal["idempotencyKey"]
        raw = _json(payload)
        with self._transaction() as (tx, _):
            existing = list(tx.run("""// jci:request-existing
MATCH (r:JCITechnicalRequest)
WHERE r.requestId = $request_id OR r.idempotencyKey = $key
RETURN properties(r) AS request""", request_id=request_id, key=key))
            if existing:
                row = existing[0]["request"]
                if (len(existing) != 1 or row["requestId"] != request_id
                        or row["idempotencyKey"] != key or row["payloadJson"] != raw
                        or row["packageJson"] != self.package_json):
                    raise RequestConflict("request identity/idempotency payload collision")
                return AcceptedRequest(request_id, key, row["firstRunId"])
            self._package(tx)
            self._revision(tx, proposal)
            accepted_at = self._now(tx)
            self.rules.accept(tx, deepcopy(payload), run_id, accepted_at)
            self._acceptance_bundle(tx, proposal, payload)
            tx.run("""// jci:accept
CREATE (r:JCITechnicalRequest {
 requestId: $request_id, idempotencyKey: $key, payloadJson: $payload,
 proposalJson: $proposal, approvalEnvelopeJson: $envelope,
 packageJson: $package, firstRunId: $run_id, acceptedAt: $now})
CREATE (:JCITechnicalRun {runId: $run_id, requestId: $request_id,
 idempotencyKey: $key, state: 'QUEUED', fence: 0, scheduledAt: $now})""",
                   request_id=request_id, key=key, payload=raw, proposal=_json(proposal),
                   envelope=raw if "proposal" in payload else None, package=self.package_json,
                   run_id=run_id, now=accepted_at).consume()
            self._advance(tx)
            self._commit(tx, "accept", run_id)
            return AcceptedRequest(request_id, key, run_id)

    @staticmethod
    def _run(tx, run_id):
        rows = list(tx.run("// jci:run\nMATCH (r:JCITechnicalRun {runId: $id}) RETURN properties(r) AS run", id=run_id))
        if len(rows) != 1:
            raise RunNotFound(run_id)
        return rows[0]["run"]

    @staticmethod
    def _token(run):
        return RunToken(run["requestId"], run["runId"], run["workerId"], run["fence"])

    def _completed(self, tx, run):
        # Each failed attempt remains its own immutable fact even when a later
        # explicitly scheduled attempt of the same request succeeds.
        if run["state"] in {"CONFLICT", "FAILED"}:
            return parse_exact_json(run["resultJson"])
        rows = list(tx.run("""// jci:receipt
MATCH (c:JCITechnicalCommit {idempotencyKey: $key})
RETURN properties(c) AS receipt""", key=run["idempotencyKey"]))
        if rows:
            if len(rows) != 1 or rows[0]["receipt"]["runId"] != run["runId"]:
                raise RunCompleted("another run already committed this request")
            receipt = rows[0]["receipt"]
            if run["state"] != "SUCCESS" or receipt["resultJson"] != run.get("resultJson"):
                raise InvalidBundle("success receipt and run disagree")
            return parse_exact_json(receipt["resultJson"])
        if run["state"] == "SUCCESS":
            raise InvalidBundle("successful run has no atomic receipt")
        if run["state"] not in {"QUEUED", "RUNNING"}:
            raise InvalidBundle("unknown persisted run state")
        return None

    def claim(self, run_id, worker_id, *, expected_fence=None):
        _uuid(run_id)
        if not isinstance(worker_id, str) or not worker_id.strip():
            raise RunOwnershipError("worker identity required")
        with self._transaction() as (tx, _):
            run = self._run(tx, run_id)
            if self._completed(tx, run) is not None:
                raise RunCompleted("recover the existing terminal result")
            if run["state"] == "RUNNING":
                if type(expected_fence) is not int or expected_fence != run["fence"]:
                    raise RunOwnershipError("recover and supply the current fence for takeover")
            elif expected_fence is not None and expected_fence != run["fence"]:
                raise RunOwnershipError("stale claim fence")
            fence = run["fence"] + 1
            tx.run("""// jci:claim
MATCH (r:JCITechnicalRun {runId: $id})
SET r.state = 'RUNNING', r.workerId = $worker, r.fence = $fence,
 r.startedAt = coalesce(r.startedAt, datetime.realtime())""",
                   id=run_id, worker=worker_id, fence=fence).consume()
            self._commit(tx, "claim", run_id)
            return RunToken(run["requestId"], run_id, worker_id, fence)

    def retry(self, previous_run_id, *, run_id):
        """Explicitly schedule one successor to a documented FAILED/CONFLICT.

This never changes payload, requestedRevision or ChangeEvent. A running or
unknown attempt must first be recovered and documented; no automatic retry is
inferred from a timeout. Retransmitting the same scheduling identity is safe.
"""
        _uuid(previous_run_id)
        _uuid(run_id)
        if previous_run_id == run_id:
            raise RequestConflict("a new attempt needs a new run identity")
        with self._transaction() as (tx, _):
            previous = self._run(tx, previous_run_id)
            if previous["state"] not in {"FAILED", "CONFLICT"}:
                raise RunOwnershipError("only a documented unsuccessful attempt can be retried")
            existing = previous.get("retryRunId")
            if existing is not None:
                if existing != run_id:
                    raise RequestConflict("this attempt already has an explicit successor")
                return AcceptedRequest(previous["requestId"], previous["idempotencyKey"], run_id)
            receipts = list(tx.run("""// jci:receipt
MATCH (c:JCITechnicalCommit {idempotencyKey: $key})
RETURN properties(c) AS receipt""", key=previous["idempotencyKey"]))
            if receipts:
                raise RunCompleted("the immutable request already succeeded")
            tx.run("""// jci:retry
MATCH (previous:JCITechnicalRun {runId: $previous_run_id})
SET previous.retryRunId = $run_id
CREATE (:JCITechnicalRun {runId: $run_id, previousRunId: $previous_run_id,
 requestId: $request_id, idempotencyKey: $key, state: 'QUEUED', fence: 0,
 scheduledAt: datetime.realtime()})""", previous_run_id=previous_run_id, run_id=run_id,
                   request_id=previous["requestId"], key=previous["idempotencyKey"]).consume()
            self._commit(tx, "retry", run_id)
            return AcceptedRequest(previous["requestId"], previous["idempotencyKey"], run_id)

    def recover(self, run_id):
        """Gate acquisition waits for an in-flight former transaction to end."""
        _uuid(run_id)
        with self._transaction() as (tx, _):
            run = self._run(tx, run_id)
            result = self._completed(tx, run)
            token = self._token(run) if run["state"] == "RUNNING" else None
            return Recovery(run["state"], token, result)

    def _load_owned(self, tx, token):
        if not isinstance(token, RunToken):
            raise RunOwnershipError("RunToken required")
        run = self._run(tx, token.run_id)
        if run["requestId"] != token.request_id:
            raise RunOwnershipError("token belongs to another request")
        completed = self._completed(tx, run)
        if completed is not None:
            return run, None, None, completed
        if run["state"] != "RUNNING" or self._token(run) != token:
            raise RunOwnershipError("lost run ownership/fence")
        request = _one(tx, """// jci:request
MATCH (r:JCITechnicalRequest {requestId: $id}) RETURN properties(r) AS request""", id=token.request_id)["request"]
        if request["packageJson"] != self.package_json or request["idempotencyKey"] != run["idempotencyKey"]:
            raise ProfileMismatch("accepted request belongs to a different rule package")
        payload, proposal = self._payload(parse_exact_json(request["payloadJson"]))
        if proposal["requestId"] != token.request_id or _json(proposal) != request["proposalJson"]:
            raise InvalidBundle("durable request identity differs")
        return run, payload, proposal, None

    @staticmethod
    def _candidate(candidate):
        if not isinstance(candidate, Mapping):
            raise InvalidBundle("candidate must include explicit read/write evidence")
        reads, changed = candidate.get("readRevisions"), candidate.get("changedEntityIds")
        if (not isinstance(reads, Mapping) or not isinstance(changed, list)
                or len(changed) != len(set(changed))):
            raise InvalidBundle("missing/duplicate candidate read/write evidence")
        for identity, revision in reads.items():
            _uuid(identity)
            if type(revision) is not int or revision < 1:
                raise InvalidBundle("read revisions must be positive integers")
        for identity in changed:
            _uuid(identity)
        return dict(reads), changed

    @staticmethod
    def _read_evidence(tx, reads):
        rows = list(tx.run("""// jci:read-evidence
UNWIND $ids AS id
MATCH (e:JCIEntity {id: id}) RETURN e.id AS id, e.revision AS revision""", ids=list(reads)))
        actual = {row["id"]: row["revision"] for row in rows}
        if len(rows) != len(reads) or actual != reads:
            raise RevisionConflict("candidate read evidence differs from the locked graph")

    @staticmethod
    def _new_owner_absence(tx, reads, changed):
        proposed_new_ids = [identity for identity in changed if identity not in reads]
        if not proposed_new_ids:
            return
        existing = list(tx.run("""// jci:new-owner-absence
UNWIND $ids AS id
MATCH (e:JCIEntity {id: id}) RETURN e.id AS id""", ids=proposed_new_ids))
        if existing:
            raise InvalidBundle("existing changed owner is missing its authoritative read revision")

    @staticmethod
    def _delta_evidence(tx, reads, changed, event_id):
        rows = list(tx.run("""// jci:delta-evidence
UNWIND $ids AS id
MATCH (e:JCIEntity {id: id})
RETURN e.id AS id, e.revision AS revision,
 [(e)-[:HAS_HISTORICAL_STATE]->(h:JCIEntity:PiH)<-[:CREATES_HISTORY]-(:SyncEvent {id: $event_id})
  | {id: h.id, originalRevision: h.originalRevision, originalEntityId: h.originalEntityId}] AS histories""",
                           ids=changed, event_id=event_id))
        if len(rows) != len(changed):
            raise InvalidBundle("changed owners are not all persisted")
        for row in rows:
            identity, histories = row["id"], row["histories"]
            if identity in reads:
                if (row["revision"] != reads[identity] + 1 or len(histories) != 1
                        or histories[0]["originalRevision"] != reads[identity]
                        or histories[0]["originalEntityId"] != identity):
                    raise InvalidBundle("existing changed owner needs one next revision and one PiH")
            elif row["revision"] != 1 or histories:
                raise InvalidBundle("new changed owner starts at revision one without PiH")

    def _result(self, tx, result, context, changed, expected_outcome):
        try:
            result = parse_exact_json(_json(result))
            self.validators["result"].validate(result)
        except Exception as error:
            raise InvalidBundle("invalid JCISyncResult") from error
        if (result["requestId"] != context.request_id or result["runId"] != context.run_id
                or result["outcome"] != expected_outcome or result["changedCount"] != len(changed)
                or result["affectedCount"] != len(result["affectedEntityIds"])
                or result["conflictCount"] != len(result["conflictIds"])
                or not set(changed) <= set(result["affectedEntityIds"])):
            raise InvalidBundle("result identity/counts disagree with candidate")
        if expected_outcome != "SUCCESS" and any(result[key] for key in ("changedCount", "historyCount", "correctionCount")):
            raise InvalidBundle("failed/conflicting run must not have a domain delta")
        row = _one(tx, """// jci:result-bundle
MATCH (e:JCIEntity:SyncEvent {id: $event_id})
RETURN properties(e) AS event,
 [(c:JCIEntity:ChangeEvent)-[:TRIGGERS]->(e) | c.id] AS requests,
 [(e)-[:EXECUTES]->(s:JCIEntity:SYNC) | s.id] AS definitions,
 [(e)-[:AFFECTS]->(a:JCIEntity) | a.id] AS affected,
 [(e)-[:CREATES_HISTORY]->(h:JCIEntity:PiH) | h.id] AS histories,
 [(e)-[:CREATES_CORRECTION]->(c:JCIEntity:HistoricalCorrection) | c.id] AS corrections,
 [(c:JCIEntity:RaNConflict)-[:DETECTED_BY]->(e) | c.id] AS conflicts""", event_id=result["syncEventId"])
        event = row["event"]
        if (event.get("entityType") != "SyncEvent" or event.get("status") != "RECORDED"
                or event.get("revision") != 1 or event.get("runId") != context.run_id
                or event.get("outcome") != expected_outcome
                or any(event.get(key) != result[key] for key in COUNTERS)
                or row["requests"] != [context.request_id]
                or row["definitions"] != [self.package.sync_id]
                or sorted(row["affected"]) != sorted(result["affectedEntityIds"])
                or sorted(row["conflicts"]) != sorted(result["conflictIds"])
                or len(row["histories"]) != result["historyCount"]
                or len(row["corrections"]) != result["correctionCount"]):
            raise InvalidBundle("persisted completion bundle disagrees with result")
        try:
            completed_at = _instant(result["completedAt"])
            if (_instant(event.get("startedAt")) != _instant(context.started_at)
                    or _instant(event.get("completedAt")) != completed_at
                    or completed_at < _instant(context.decision_at)
                    or completed_at < _instant(context.started_at)):
                raise InvalidBundle("completion times disagree with the protected decision")
        except (ValueError, TypeError) as error:
            raise InvalidBundle("invalid completion timestamps") from error
        return result

    def _finish(self, tx, run, context, result, reads, changed):
        raw = _json(result)
        params = dict(run_id=context.run_id, request_id=context.request_id,
                      key=run["idempotencyKey"], result=raw, outcome=result["outcome"],
                      event_id=result["syncEventId"], now=context.decision_at,
                      epoch=context.graph_epoch + 1, package=self.package_json,
                      reads=_json(reads), changed=changed)
        tx.run("""// jci:finish
MATCH (r:JCITechnicalRun {runId: $run_id})
SET r.state = $outcome, r.resultJson = $result, r.completedAt = datetime.realtime()
CREATE (:JCITechnicalOutbox {eventId: $event_id, runId: $run_id,
 requestId: $request_id, payloadJson: $result, createdAt: $now, state: 'PENDING'})""", **params).consume()
        if result["outcome"] == "SUCCESS":
            tx.run("""// jci:success
CREATE (:JCITechnicalCommit {idempotencyKey: $key, runId: $run_id,
 requestId: $request_id, eventId: $event_id, resultJson: $result,
 decisionAt: $now, graphEpoch: $epoch, packageJson: $package,
 readRevisionsJson: $reads, changedEntityIds: $changed})""", **params).consume()
        self._advance(tx)

    def execute(self, token):
        """One explicit attempt. All exceptions roll back; no automatic retry."""
        with self._transaction() as (tx, epoch):
            run, payload, proposal, completed = self._load_owned(tx, token)
            if completed is not None:
                return completed
            self._package(tx)
            self._revision(tx, proposal)
            candidate = self.rules.evaluate(tx, deepcopy(payload))
            context = ExecutionContext(token.request_id, token.run_id, token.worker_id,
                                       token.fence, epoch, run["startedAt"], self._now(tx))
            if self.rules.validate_at(tx, deepcopy(payload), candidate, context) is not True:
                raise InvalidBundle("final domain/approval validation did not approve")
            # Temporal validation may legitimately rederive the candidate. Bind
            # evidence only after that step, then prohibit mutation by apply.
            candidate = deepcopy(candidate)
            reads, changed = self._candidate(candidate)
            reads, changed = deepcopy(reads), list(changed)
            if proposal["changeType"] != "CREATED" and reads.get(proposal["target"]["id"]) != proposal["requestedRevision"]:
                raise InvalidBundle("candidate omits its authoritative target revision")
            self._read_evidence(tx, reads)
            self._new_owner_absence(tx, reads, changed)
            applied_candidate = deepcopy(candidate)
            result = self.rules.apply(tx, deepcopy(payload), applied_candidate, context)
            if self._candidate(applied_candidate) != (reads, changed):
                raise InvalidBundle("apply mutated the approved read/write evidence")
            result = self._result(tx, result, context, changed, "SUCCESS")
            self._delta_evidence(tx, reads, changed, result["syncEventId"])
            self._finish(tx, run, context, result, reads, changed)
            self._commit(tx, "execute", token.run_id)
            return result

    def finish_failed(self, token, *, outcome, error_code, error_message):
        """Recovery transaction; never calls evaluate/apply or repeats the delta."""
        if outcome not in {"FAILED", "CONFLICT"} or not error_code or not error_message:
            raise InvalidBundle("explicit failure/conflict reason required")
        with self._transaction() as (tx, epoch):
            run, payload, _, completed = self._load_owned(tx, token)
            if completed is not None:
                return completed
            context = ExecutionContext(token.request_id, token.run_id, token.worker_id,
                                       token.fence, epoch, run["startedAt"], self._now(tx))
            result = self.rules.document_failure(tx, deepcopy(payload), context,
                                                 outcome, error_code, error_message)
            result = self._result(tx, result, context, [], outcome)
            self._finish(tx, run, context, result, {}, [])
            self._commit(tx, "finish_failed", token.run_id)
            return result
