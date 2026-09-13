"""Coordinator protocol unit tests using fakes; these are NOT Neo4j isolation tests."""

from copy import deepcopy
from datetime import datetime, timezone
from hashlib import sha256
import unittest
from uuid import UUID

from jci_runtime.neo4j_store import (
    CommitOutcomeUnknown, InvalidBundle, Neo4jStore, ProfileMismatch,
    RequestConflict, RevisionConflict, RulePackage, RunCompleted,
    RunOwnershipError, StoreNotInitialized,
)
from reference.jci_rules import canonical_json


def uid(number):
    return str(UUID(int=number))


NOW = datetime(2026, 9, 12, 12, tzinfo=timezone.utc)
TARGET, ROLE, SYNC = uid(1), uid(2), uid(3)


def request(number=10):
    return {"schemaVersion": "2.0", "requestId": uid(number),
            "idempotencyKey": "request-" + str(number),
            "requestedAt": NOW.isoformat(), "requestedRevision": 1,
            "changeType": "CHANGED", "target": {"id": TARGET, "entityType": "Task"},
            "requestedByRoleAssignmentId": ROLE, "reason": "Protocol fixture",
            "operations": [{"op": "REPLACE", "path": "/name",
                            "value": {"valueType": "STRING", "value": "changed"}}]}


class FakeResult(list):
    def consume(self):
        return None


class FakeDriver:
    def __init__(self):
        self.state = {"epoch": None, "requests": {}, "runs": {}, "receipts": {},
                      "outbox": {}, "events": {}, "targetRevision": 1, "extraEntities": {}}
        self.queries = []
        self.fail_commit = None

    def session(self, **kwargs):
        return FakeSession(self)


class FakeSession:
    def __init__(self, driver):
        self.driver = driver

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

    def begin_transaction(self, **kwargs):
        return FakeTransaction(self.driver)


class FakeTransaction:
    def __init__(self, driver):
        self.driver, self.data = driver, deepcopy(driver.state)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass  # Uncommitted working copy is discarded, including callback writes.

    def commit(self):
        failure, self.driver.fail_commit = self.driver.fail_commit, None
        if failure != "before":
            self.driver.state = deepcopy(self.data)
        if failure:
            raise OSError("simulated lost acknowledgement")

    def run(self, query, **p):
        self.driver.queries.append(query)
        marker = query.splitlines()[0]
        d, rows = self.data, []
        if query.startswith("CREATE CONSTRAINT"):
            pass
        elif marker == "// jci:install":
            if d["epoch"] is None:
                d["epoch"] = 0
        elif marker == "// jci:lock":
            rows = [] if d["epoch"] is None else [{"graphEpoch": d["epoch"]}]
        elif marker == "// jci:epoch":
            d["epoch"] += 1
        elif marker == "// jci:clock":
            rows = [{"now": NOW}]
        elif marker == "// jci:package":
            rows = [{"status": "ACTIVE", "revision": 1,
                     "definitionJson": canonical_json({
                         **{key: "2.0" for key in ("definitionSchemaVersion", "ontologyVersion", "graphRulesVersion", "syncSpecVersion")},
                         "approvalProfileVersion": "1.0", "implementationChecksum": "a" * 64}).decode()}]
        elif marker == "// jci:revision":
            rows = [{"entityType": "Task", "revision": d["targetRevision"]}]
        elif marker == "// jci:request-existing":
            rows = [{"request": r} for r in d["requests"].values()
                    if r["requestId"] == p["request_id"] or r["idempotencyKey"] == p["key"]]
        elif marker == "// jci:acceptance-bundle":
            rows = [d["events"][p["id"]]] if p["id"] in d["events"] else []
        elif marker == "// jci:accept":
            d["requests"][p["request_id"]] = {
                "requestId": p["request_id"], "idempotencyKey": p["key"],
                "payloadJson": p["payload"], "proposalJson": p["proposal"],
                "packageJson": p["package"], "firstRunId": p["run_id"]}
            d["runs"][p["run_id"]] = {"runId": p["run_id"], "requestId": p["request_id"],
                "idempotencyKey": p["key"], "state": "QUEUED", "fence": 0}
        elif marker == "// jci:run":
            rows = [{"run": d["runs"][p["id"]]}] if p["id"] in d["runs"] else []
        elif marker == "// jci:receipt":
            rows = [{"receipt": d["receipts"][p["key"]]}] if p["key"] in d["receipts"] else []
        elif marker == "// jci:claim":
            d["runs"][p["id"]].update(state="RUNNING", workerId=p["worker"], fence=p["fence"], startedAt=NOW)
        elif marker == "// jci:retry":
            d["runs"][p["previous_run_id"]]["retryRunId"] = p["run_id"]
            d["runs"][p["run_id"]] = {"runId": p["run_id"], "requestId": p["request_id"],
                "idempotencyKey": p["key"], "state": "QUEUED", "fence": 0}
        elif marker == "// jci:request":
            rows = [{"request": d["requests"][p["id"]]}]
        elif marker == "// jci:read-evidence":
            rows = [{"id": identity, "revision": d["targetRevision"]} for identity in p["ids"]]
        elif marker == "// jci:new-owner-absence":
            existing_ids = {TARGET, *d["extraEntities"]}
            rows = [{"id": identity} for identity in p["ids"] if identity in existing_ids]
        elif marker == "// jci:delta-evidence":
            rows = [{"id": identity,
                     "revision": d["targetRevision"] if identity == TARGET else d["extraEntities"][identity],
                     "histories": [{"id": uid(90), "originalRevision": 1, "originalEntityId": identity}]
                     if identity == TARGET else []} for identity in p["ids"]]
        elif marker == "// jci:result-bundle":
            rows = [d["events"][p["event_id"]]] if p["event_id"] in d["events"] else []
        elif marker == "// jci:finish":
            d["runs"][p["run_id"]].update(state=p["outcome"], resultJson=p["result"])
            d["outbox"][p["event_id"]] = dict(p)
        elif marker == "// jci:success":
            d["receipts"][p["key"]] = {"runId": p["run_id"], "resultJson": p["result"],
                                            "packageJson": p["package"], "readRevisionsJson": p["reads"]}
        else:
            raise AssertionError("Unrecognized protocol query: " + marker)
        return FakeResult(rows)


class FixtureRules:
    """Intentionally narrow fake only; not a production authorization adapter."""
    package = RulePackage(SYNC, 1, "a" * 64)

    def __init__(self):
        self.applies = 0
        self.validation = True
        self.failure = None
        self.omit_event = False

    def accept(self, tx, payload, run_id, accepted_at):
        p = payload.get("proposal", payload)
        tx.data["events"][p["requestId"]] = {"event": {
            "entityType": "ChangeEvent", "status": "RECORDED", "revision": 1,
            "idempotencyKey": p["idempotencyKey"], "changeType": p["changeType"],
            "targetEntityId": p["target"]["id"], "targetEntityType": p["target"]["entityType"],
            "requestedRevision": p["requestedRevision"]}, "requesters": [ROLE]}

    def evaluate(self, tx, payload):
        return {"readRevisions": {TARGET: tx.data["targetRevision"]}, "changedEntityIds": [TARGET]}

    def validate_at(self, tx, payload, candidate, context):
        return self.validation

    def apply(self, tx, payload, candidate, context):
        self.applies += 1
        tx.data["targetRevision"] += 1
        if self.failure:
            raise self.failure
        return self._event(tx, context, "SUCCESS")

    def _event(self, tx, context, outcome):
        success = outcome == "SUCCESS"
        result = {"schemaVersion": "2.0", "requestId": context.request_id,
            "runId": context.run_id, "syncEventId": uid(100), "outcome": outcome,
            "completedAt": NOW.isoformat(), "affectedCount": 1, "changedCount": int(success),
            "historyCount": int(success), "correctionCount": 0, "conflictCount": 0,
            "affectedEntityIds": [TARGET], "conflictIds": [], "errors": []}
        if not self.omit_event:
            tx.data["events"][uid(100)] = {"event": {
                **result, "entityType": "SyncEvent", "status": "RECORDED", "revision": 1,
                "startedAt": context.started_at, "completedAt": NOW},
                "requests": [context.request_id], "definitions": [SYNC], "affected": [TARGET],
                "histories": [uid(90)] if success else [], "corrections": [], "conflicts": []}
        return result

    def document_failure(self, tx, payload, context, outcome, error_code, error_message):
        return self._event(tx, context, outcome)


class Neo4jStoreProtocolTests(unittest.TestCase):
    def setUp(self):
        self.driver, self.rules = FakeDriver(), FixtureRules()
        self.store = Neo4jStore(self.driver, database="neo4j", rules=self.rules)
        self.store.install()
        self.run_id = uid(20)

    def running(self):
        self.store.accept(request(), run_id=self.run_id)
        return self.store.claim(self.run_id, "worker")

    def test_no_default_rules_or_implicit_gate_installation(self):
        with self.assertRaises(ProfileMismatch):
            Neo4jStore(self.driver, database="neo4j", rules=None)
        fresh = Neo4jStore(FakeDriver(), database="neo4j", rules=self.rules)
        with self.assertRaises(StoreNotInitialized):
            fresh.accept(request(), run_id=self.run_id)

    def test_acceptance_is_durable_idempotent_and_rejects_identity_collisions(self):
        first = self.store.accept(request(), run_id=self.run_id)
        self.assertEqual(self.store.accept(request(), run_id=uid(21)), first)
        self.assertEqual(len(self.driver.state["runs"]), 1)
        changed = request()
        changed["reason"] = "different payload"
        with self.assertRaises(RequestConflict):
            self.store.accept(changed, run_id=uid(21))
        changed = request(11)
        changed["idempotencyKey"] = request()["idempotencyKey"]
        with self.assertRaises(RequestConflict):
            self.store.accept(changed, run_id=uid(21))
        self.assertEqual(self.store.recover(self.run_id).state, "QUEUED")

    def test_lost_acceptance_ack_keeps_recoverable_queued_run(self):
        self.driver.fail_commit = "after"
        with self.assertRaises(CommitOutcomeUnknown):
            self.store.accept(request(), run_id=self.run_id)
        self.assertEqual(self.store.recover(self.run_id).state, "QUEUED")
        self.assertEqual(self.store.accept(request(), run_id=uid(21)).run_id, self.run_id)

    def test_gate_precedes_all_authoritative_reads(self):
        self.driver.queries.clear()
        token = self.running()
        self.store.execute(token)
        statements = self.driver.queries
        self.assertTrue(statements[0].startswith("// jci:lock"))
        self.assertEqual(sum(q.startswith("// jci:lock") for q in statements), 3)

    def test_takeover_fences_old_worker_and_failure_documentation(self):
        old = self.running()
        with self.assertRaises(RunOwnershipError):
            self.store.claim(self.run_id, "second")
        recovered = self.store.recover(self.run_id)
        new = self.store.claim(self.run_id, "second", expected_fence=recovered.token.fence)
        self.assertEqual(new.fence, old.fence + 1)
        for operation in (lambda: self.store.execute(old), lambda: self.store.finish_failed(
                old, outcome="FAILED", error_code="old", error_message="old")):
            with self.assertRaises(RunOwnershipError):
                operation()
        self.store.execute(new)
        with self.assertRaises(RunCompleted):
            self.store.claim(self.run_id, "third", expected_fence=new.fence)

    def test_callback_failure_rolls_back_delta_and_can_document_same_run(self):
        token = self.running()
        self.rules.failure = ValueError("invalid candidate application")
        with self.assertRaises(ValueError):
            self.store.execute(token)
        self.assertEqual(self.driver.state["targetRevision"], 1)
        self.assertFalse(self.driver.state["receipts"])
        self.assertFalse(self.driver.state["outbox"])
        result = self.store.finish_failed(token, outcome="FAILED", error_code="BAD", error_message="invalid")
        self.assertEqual(result["outcome"], "FAILED")
        self.assertEqual(self.rules.applies, 1)
        self.assertEqual(self.driver.state["epoch"], 2)

    def test_non_true_final_validation_cannot_write(self):
        token = self.running()
        for verdict in (False, None, 1, "approved"):
            self.rules.validation = verdict
            with self.assertRaises(InvalidBundle):
                self.store.execute(token)
        self.assertEqual(self.rules.applies, 0)

    def test_returned_success_without_persisted_event_rolls_back(self):
        token = self.running()
        self.rules.omit_event = True
        with self.assertRaises(InvalidBundle):
            self.store.execute(token)
        self.assertEqual(self.driver.state["targetRevision"], 1)
        self.assertFalse(self.driver.state["receipts"])

    def test_lost_success_ack_recovers_without_repeating_domain_or_outbox(self):
        token = self.running()
        self.driver.fail_commit = "after"
        with self.assertRaises(CommitOutcomeUnknown):
            self.store.execute(token)
        recovery = self.store.recover(self.run_id)
        self.assertEqual(recovery.state, "SUCCESS")
        self.assertEqual(self.store.execute(token), recovery.result)
        self.assertEqual(self.store.finish_failed(token, outcome="FAILED", error_code="TIMEOUT", error_message="lost ack"), recovery.result)
        self.assertEqual(self.rules.applies, 1)
        self.assertEqual(len(self.driver.state["receipts"]), 1)
        self.assertEqual(len(self.driver.state["outbox"]), 1)
        self.assertEqual(self.driver.state["targetRevision"], 2)

    def test_unknown_rolled_back_commit_is_not_automatically_retried(self):
        token = self.running()
        self.driver.fail_commit = "before"
        with self.assertRaises(CommitOutcomeUnknown):
            self.store.execute(token)
        self.assertEqual(self.store.recover(self.run_id).state, "RUNNING")
        self.assertEqual(self.rules.applies, 1)
        self.assertEqual(self.driver.state["targetRevision"], 1)

    def test_revision_is_checked_again_after_acceptance(self):
        token = self.running()
        self.driver.state["targetRevision"] = 2
        with self.assertRaises(RevisionConflict):
            self.store.execute(token)
        self.assertEqual(self.rules.applies, 0)

    def test_retry_requires_documented_failure_and_preserves_its_own_result(self):
        token = self.running()
        with self.assertRaises(RunOwnershipError):
            self.store.retry(self.run_id, run_id=uid(21))
        failed = self.store.finish_failed(token, outcome="FAILED", error_code="FAIL", error_message="failed")
        scheduled = self.store.retry(self.run_id, run_id=uid(21))
        self.assertEqual(self.store.retry(self.run_id, run_id=uid(21)), scheduled)
        with self.assertRaises(RequestConflict):
            self.store.retry(self.run_id, run_id=uid(22))
        new = self.store.claim(uid(21), "worker-2")
        self.store.execute(new)
        self.assertEqual(self.store.recover(self.run_id).result, failed)
        self.assertEqual(self.store.recover(uid(21)).state, "SUCCESS")
        self.assertEqual(len(self.driver.state["requests"]), 1)

    def test_final_validation_evidence_is_used_and_apply_cannot_change_it(self):
        token = self.running()
        original_apply = self.rules.apply
        def changed_apply(tx, payload, candidate, context):
            result = original_apply(tx, payload, candidate, context)
            candidate["readRevisions"][TARGET] = 99
            return result
        self.rules.apply = changed_apply
        with self.assertRaisesRegex(InvalidBundle, "mutated"):
            self.store.execute(token)
        self.assertEqual(self.driver.state["targetRevision"], 1)

    def test_final_validation_cannot_claim_an_unread_revision(self):
        token = self.running()
        def invalid_final(tx, payload, candidate, context):
            candidate["readRevisions"][uid(888)] = 100
            return True
        self.rules.validate_at = invalid_final
        with self.assertRaises(RevisionConflict):
            self.store.execute(token)
        self.assertEqual(self.rules.applies, 0)

    def test_existing_owner_cannot_be_misdeclared_as_new_without_read_revision(self):
        token = self.running()
        existing = uid(888)
        self.driver.state["extraEntities"][existing] = 1
        self.rules.evaluate = lambda tx, payload: {
            "readRevisions": {TARGET: 1}, "changedEntityIds": [TARGET, existing]}
        with self.assertRaisesRegex(InvalidBundle, "existing changed owner"):
            self.store.execute(token)
        self.assertEqual(self.rules.applies, 0)
        self.assertEqual(self.driver.state["targetRevision"], 1)
        self.assertEqual(self.driver.state["extraEntities"][existing], 1)
        self.assertFalse(self.driver.state["receipts"])

    def test_truly_new_owner_is_checked_absent_then_persisted_at_revision_one(self):
        token = self.running()
        new_id = uid(889)
        self.rules.evaluate = lambda tx, payload: {
            "readRevisions": {TARGET: 1}, "changedEntityIds": [TARGET, new_id]}
        original_apply = self.rules.apply
        def with_new_owner(tx, payload, candidate, context):
            result = original_apply(tx, payload, candidate, context)
            tx.data["extraEntities"][new_id] = 1
            result.update(affectedCount=2, changedCount=2, affectedEntityIds=[TARGET, new_id])
            stored = tx.data["events"][result["syncEventId"]]
            stored["event"].update(affectedCount=2, changedCount=2)
            stored["affected"] = [TARGET, new_id]
            return result
        self.rules.apply = with_new_owner
        result = self.store.execute(token)
        self.assertEqual(result["changedCount"], 2)
        self.assertEqual(result["historyCount"], 1)
        self.assertEqual(self.driver.state["extraEntities"][new_id], 1)
        self.assertEqual(self.rules.applies, 1)

    def test_unsupported_profiles_are_rejected_before_persistence(self):
        invalid = request()
        invalid["schemaVersion"] = "1.1"
        with self.assertRaises(ProfileMismatch):
            self.store.accept(invalid, run_id=self.run_id)
        self.assertFalse(self.driver.state["requests"])

    def test_envelope_needs_exact_persisted_approval_edges(self):
        proposal = request()
        request_hash = sha256(canonical_json(proposal)).hexdigest()
        receipt = {"receiptId": uid(300), "requestHash": request_hash, "contextHash": "b" * 64,
                   "decidedAt": NOW.isoformat(), "validUntil": "2026-09-12T13:00:00Z",
                   "outcome": "APPROVED", "roleAssignmentId": ROLE, "memberId": uid(301),
                   "attestation": "fixture-only-no-real-authentication"}
        envelope = {"approvalProfileVersion": "1.0", "decisionKey": "Task.action.RELEASE",
                    "proposal": proposal, "requestHash": request_hash, "contextHash": "b" * 64,
                    "receipts": [receipt]}
        with self.assertRaisesRegex(InvalidBundle, "APPROVED_BY"):
            self.store.accept(envelope, run_id=self.run_id)
        self.assertFalse(self.driver.state["requests"])
        original_accept = self.rules.accept
        def with_approval(tx, payload, run_id, accepted_at):
            original_accept(tx, payload, run_id, accepted_at)
            tx.data["events"][proposal["requestId"]]["approvals"] = [{
                "roleAssignmentId": ROLE, "receiptId": receipt["receiptId"],
                "decidedAt": NOW, "requestHash": request_hash,
                "approvalHash": sha256(canonical_json(receipt)).hexdigest()}]
        self.rules.accept = with_approval
        self.store.accept(envelope, run_id=self.run_id)
        self.assertEqual(self.store.recover(self.run_id).state, "QUEUED")


if __name__ == "__main__":
    unittest.main()
