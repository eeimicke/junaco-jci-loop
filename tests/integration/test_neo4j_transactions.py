"""Real transactions, with a deliberately narrow trusted test rules bundle.

These tests verify the persistence coordinator, not full JCI model validation.
Every fixture has fresh UUIDs. No database reset or global deletion is performed.
Set JCI_NEO4J_TEST_URI and JCI_NEO4J_TEST_CONFIRM=isolated to enable the suite.
"""

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from textwrap import dedent
from threading import Event
import time
import unittest
from uuid import uuid4

from reference.jci_rules import canonical_json, history_hash


URI = os.environ.get("JCI_NEO4J_TEST_URI")
CHECKSUM = hashlib.sha256(b"narrow integration-test rules; never deploy").hexdigest()


def uid():
    return str(uuid4())


def iso(value):
    return value.iso_format() if hasattr(value, "iso_format") else value.isoformat()


def native(value):
    return value.to_native() if hasattr(value, "to_native") else value


class FixtureRules:
    """Test-only rename validator; it intentionally grants no production authority."""

    def __init__(self, sync_id, actor_id):
        from jci_runtime.neo4j_store import RulePackage
        self.package = RulePackage(sync_id, 1, CHECKSUM)
        self.actor_id = actor_id
        self.evaluate_calls = 0
        self.entered = Event()
        self.release = None
        self.deadline = None
        self.fail_after_write = False
        self.corrupt_result = False
        self.revision_neutral = False
        self.check_marker = None
        self.write_marker = None

    def accept(self, tx, payload, run_id, accepted_at):
        tx.run(
            "MATCH (actor:JCIEntity {id:$actor}), (target:JCIEntity {id:$target}) "
            "CREATE (e:JCIEntity:ChangeEvent {id:$id, entityType:'ChangeEvent', "
            "name:'Integration request', status:'RECORDED', revision:1, "
            "createdAt:$at, updatedAt:$at, occurredAt:$at, changeType:$kind, "
            "reason:$reason, idempotencyKey:$key, targetEntityId:$target, "
            "targetEntityType:'Task', requestedRevision:$revision}) "
            "CREATE (e)-[:CREATED_BY]->(actor), (e)-[:REQUESTED_BY]->(actor), "
            "(target)-[:CHANGED_BY]->(e)",
            actor=self.actor_id, target=payload["target"]["id"], id=payload["requestId"],
            at=accepted_at, kind=payload["changeType"], reason=payload["reason"],
            key=payload["idempotencyKey"], revision=payload["requestedRevision"],
        ).consume()

    def evaluate(self, tx, payload):
        self.evaluate_calls += 1
        self.entered.set()
        if self.release is not None and not self.release.wait(10):
            raise RuntimeError("test barrier timed out")
        row = tx.run("MATCH (n:JCIEntity {id:$id}) RETURN properties(n) AS node",
                     id=payload["target"]["id"]).single(strict=True)
        old = dict(row["node"])
        blocked = False
        if self.check_marker is not None:
            blocked = tx.run("MATCH (m:JCIRuntimeTestMarker {id:$id}) RETURN count(m) AS n",
                             id=self.check_marker).single(strict=True)["n"] > 0
        return {"readRevisions": {old["id"]: old["revision"]},
                "changedEntityIds": [] if self.revision_neutral else [old["id"]],
                "old": old, "blocked": blocked}

    def validate_at(self, tx, payload, candidate, context):
        return (not candidate["blocked"] and
                (self.deadline is None or native(context.decision_at) < self.deadline))

    def _event(self, tx, payload, context, outcome, history_id=None, errors=()):
        event_id = uid()
        changed = int(outcome == "SUCCESS" and not self.revision_neutral)
        count = int(history_id is not None)
        tx.run(
            "MATCH (request:JCIEntity {id:$request}), (definition:JCIEntity {id:$sync}), "
            "(target:JCIEntity {id:$target}), (actor:JCIEntity {id:$actor}) "
            "CREATE (e:JCIEntity:SyncEvent {id:$id, entityType:'SyncEvent', "
            "name:'Integration outcome', status:'RECORDED', revision:1, "
            "createdAt:$at, updatedAt:$at, runId:$run, startedAt:$started, "
            "completedAt:$at, outcome:$outcome, affectedCount:1, changedCount:$changed, "
            "historyCount:$history, correctionCount:0, conflictCount:0}) "
            "CREATE (request)-[:TRIGGERS]->(e), (e)-[:EXECUTES]->(definition), "
            "(e)-[:AFFECTS]->(target), (e)-[:CREATED_BY]->(actor)",
            request=payload["requestId"], sync=self.package.sync_id,
            target=payload["target"]["id"], actor=self.actor_id, id=event_id,
            at=context.decision_at, run=context.run_id, started=context.started_at,
            outcome=outcome, changed=changed, history=count,
        ).consume()
        if history_id:
            tx.run("MATCH (e:JCIEntity {id:$event}), (h:JCIEntity {id:$history}) "
                   "CREATE (e)-[:CREATES_HISTORY]->(h)", event=event_id, history=history_id).consume()
        return {"schemaVersion": "2.0", "requestId": payload["requestId"],
                "runId": context.run_id, "syncEventId": event_id, "outcome": outcome,
                "completedAt": iso(context.decision_at), "affectedCount": 1,
                "changedCount": changed, "historyCount": count, "correctionCount": 0,
                "conflictCount": 0, "affectedEntityIds": [payload["target"]["id"]],
                "conflictIds": [], "errors": list(errors)}

    def apply(self, tx, payload, candidate, context):
        old = candidate["old"]
        history_id = None
        if not self.revision_neutral:
            history_id = uid()
            snapshot = {"stateData": {"entityType": "Task", "revision": old["revision"],
                         "properties": {name: {"valueType": "STRING", "value": old[name]}
                                        for name in ("name", "status", "taskKind")}},
                        "relationshipData": []}
            tx.run(
                "MATCH (target:JCIEntity {id:$target}), (actor:JCIEntity {id:$actor}) "
                "CREATE (h:JCIEntity:PiH {id:$id, entityType:'PiH', name:'Previous test state', "
                "status:'RECORDED', revision:1, createdAt:$at, updatedAt:$at, "
                "originalEntityId:$target, originalEntityType:'Task', originalRevision:$revision, "
                "recordedAt:$at, validFrom:$previousAt, validUntil:$at, snapshotSchemaVersion:'2.0', "
                "stateDataJson:$state, relationshipDataJson:'[]', contentHash:$hash}) "
                "CREATE (target)-[:HAS_HISTORICAL_STATE]->(h), (h)-[:CREATED_BY]->(actor) "
                "SET target.name=$name, target.revision=target.revision+1, target.updatedAt=$at",
                target=old["id"], actor=self.actor_id, id=history_id, at=context.decision_at,
                revision=old["revision"], previousAt=old["updatedAt"],
                state=canonical_json(snapshot["stateData"]).decode(), hash=history_hash(snapshot),
                name=payload["operations"][0]["value"]["value"],
            ).consume()
        if self.write_marker is not None:
            tx.run("CREATE (:JCIRuntimeTestMarker {id:$id})", id=self.write_marker).consume()
        if self.fail_after_write:
            raise RuntimeError("controlled failure after domain write")
        result = self._event(tx, payload, context, "SUCCESS", history_id)
        if self.corrupt_result:
            result["affectedCount"] = 2
        return result

    def document_failure(self, tx, payload, context, outcome, error_code, error_message):
        return self._event(tx, payload, context, outcome,
                           errors=[{"code": error_code, "message": error_message}])


class LostAckDriver:
    """The server commits normally; only the client acknowledgement is lost."""

    def __init__(self, driver):
        self.driver = driver
        self.armed = False

    def session(self, **kwargs):
        return LostAckSession(self, self.driver.session(**kwargs))


class LostAckSession:
    def __init__(self, owner, session):
        self.owner, self.inner = owner, session

    def __enter__(self):
        self.inner.__enter__()
        return self

    def __exit__(self, *args):
        return self.inner.__exit__(*args)

    def __getattr__(self, name):
        return getattr(self.inner, name)

    def begin_transaction(self, **kwargs):
        return LostAckTransaction(self.owner, self.inner.begin_transaction(**kwargs))


class LostAckTransaction:
    def __init__(self, owner, tx):
        self.owner, self.inner = owner, tx

    def __enter__(self):
        self.inner.__enter__()
        return self

    def __exit__(self, *args):
        return self.inner.__exit__(*args)

    def __getattr__(self, name):
        return getattr(self.inner, name)

    def commit(self):
        self.inner.commit()
        if self.owner.armed:
            self.owner.armed = False
            from neo4j.exceptions import ServiceUnavailable
            raise ServiceUnavailable("controlled lost acknowledgement after real commit")


@unittest.skipUnless(URI, "set JCI_NEO4J_TEST_URI for real transaction tests")
class Neo4jTransactionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if os.environ.get("JCI_NEO4J_TEST_CONFIRM") != "isolated":
            raise RuntimeError("JCI_NEO4J_TEST_CONFIRM=isolated is required; never use production")
        from neo4j import GraphDatabase
        from jci_runtime import neo4j_store
        cls.api = neo4j_store
        user = os.environ.get("JCI_NEO4J_TEST_USER", "neo4j")
        password = os.environ.get("JCI_NEO4J_TEST_PASSWORD")
        cls.auth = (user, password) if password else None
        cls.database = os.environ.get("JCI_NEO4J_TEST_DATABASE", "neo4j")
        # Empty optional history/conflict sets are intentional in these fixtures.
        cls.driver = GraphDatabase.driver(URI, auth=cls.auth,
                                          notifications_disabled_classifications=["UNRECOGNIZED"])
        cls.driver.verify_connectivity()

    @classmethod
    def tearDownClass(cls):
        cls.driver.close()

    def setUp(self):
        self.target, self.actor, self.sync = uid(), uid(), uid()
        self.rules = FixtureRules(self.sync, self.actor)
        self.store = self.api.Neo4jStore(self.driver, database=self.database, rules=self.rules)
        self.store.install()
        definition = {"definitionSchemaVersion": "2.0", "ontologyVersion": "2.0",
                      "graphRulesVersion": "2.0", "syncSpecVersion": "2.0",
                      "implementationChecksum": CHECKSUM, "approvalProfileVersion": "1.0",
                      "implementationReference": "test-only", "handlerSetVersion": "test-only",
                      "supportedEntityTypes": ["Task"], "supportedRelationshipTypes": []}
        # Controlled fixture initialization, before any concurrent test operation.
        with self.driver.session(database=self.database) as session:
            session.run(
                "CREATE (t:JCIEntity:Task {id:$target, entityType:'Task', name:'Before', "
                "status:'DRAFT', taskKind:'ATOMIC', revision:1, createdAt:datetime(), updatedAt:datetime()}) "
                "CREATE (a:JCIEntity:RoleAssignment {id:$actor, entityType:'RoleAssignment', "
                "name:'Test actor', status:'ACTIVE', revision:1, createdAt:datetime(), updatedAt:datetime()}) "
                "CREATE (s:JCIEntity:SYNC {id:$sync, entityType:'SYNC', name:'Test rules', "
                "status:'ACTIVE', revision:1, version:'2.0', definitionJson:$definition, "
                "createdAt:datetime(), updatedAt:datetime(), validFrom:datetime('2020-01-01T00:00:00Z')}) "
                "CREATE (t)-[:CREATED_BY]->(a), (s)-[:CREATED_BY]->(a)",
                target=self.target, actor=self.actor, sync=self.sync,
                definition=canonical_json(definition).decode(),
            ).consume()

    def payload(self, name="After"):
        return {"schemaVersion": "2.0", "requestId": uid(), "idempotencyKey": uid(),
                "requestedAt": datetime.now(timezone.utc).isoformat(), "requestedRevision": 1,
                "changeType": "CHANGED", "target": {"id": self.target, "entityType": "Task"},
                "requestedByRoleAssignmentId": self.actor, "reason": "Isolated adapter test",
                "operations": [{"op": "REPLACE", "path": "/name",
                                "value": {"valueType": "STRING", "value": name}}]}

    def claim(self, payload=None, store=None):
        store = store or self.store
        payload = payload or self.payload()
        run_id = uid()
        store.accept(payload, run_id=run_id)
        return payload, store.claim(run_id, uid())

    def node(self):
        with self.driver.session(database=self.database) as session:
            return dict(session.run("MATCH (n:JCIEntity {id:$id}) RETURN properties(n) AS p",
                                    id=self.target).single(strict=True)["p"])

    def histories(self):
        with self.driver.session(database=self.database) as session:
            return session.run("MATCH (:JCIEntity {id:$id})-[:HAS_HISTORICAL_STATE]->(h) "
                               "RETURN count(h) AS n", id=self.target).single(strict=True)["n"]

    def ledger(self, request_id):
        with self.driver.session(database=self.database) as session:
            return session.run(
                "OPTIONAL MATCH (c:JCITechnicalCommit {requestId:$id}) "
                "WITH collect(properties(c)) AS commits "
                "OPTIONAL MATCH (o:JCITechnicalOutbox {requestId:$id}) "
                "WITH commits, collect(properties(o)) AS outbox "
                "OPTIONAL MATCH (r:JCITechnicalRun {requestId:$id}) "
                "WITH commits, outbox, collect(properties(r)) AS runs "
                "OPTIONAL MATCH (e:JCIEntity:ChangeEvent {id:$id}) "
                "RETURN commits, outbox, runs, collect(e.id) AS requests",
                id=request_id,
            ).single(strict=True).data()

    def test_success_bundle_and_replay_are_durable(self):
        payload, token = self.claim()
        result = self.store.execute(token)
        self.assertEqual(result["outcome"], "SUCCESS")
        self.assertEqual(self.node()["revision"], 2)
        self.assertEqual(self.histories(), 1)
        self.assertEqual(self.store.execute(token), result)
        self.assertEqual(self.rules.evaluate_calls, 1)
        ledger = self.ledger(payload["requestId"])
        self.assertEqual(len(ledger["commits"]), 1)
        self.assertEqual(len(ledger["outbox"]), 1)
        self.assertEqual(json.loads(ledger["commits"][0]["resultJson"]), result)
        self.assertEqual(json.loads(ledger["outbox"][0]["payloadJson"]), result)
        self.assertEqual(ledger["outbox"][0]["eventId"], result["syncEventId"])
        self.assertEqual(ledger["outbox"][0]["state"], "PENDING")
        from neo4j import GraphDatabase
        with GraphDatabase.driver(URI, auth=self.auth,
                                  notifications_disabled_classifications=["UNRECOGNIZED"]) as reopened:
            store = self.api.Neo4jStore(reopened, database=self.database, rules=self.rules)
            recovered = store.recover(token.run_id)
            self.assertEqual(recovered.state, "SUCCESS")
            self.assertEqual(recovered.result, result)

    def test_idempotency_binds_both_identity_and_complete_payload(self):
        payload, token = self.claim()
        altered = {**payload, "reason": "changed content"}
        with self.assertRaises(self.api.RequestConflict):
            self.store.accept(altered, run_id=uid())
        with self.assertRaises(self.api.RequestConflict):
            self.store.accept({**payload, "requestId": uid()}, run_id=uid())
        with self.assertRaises(self.api.RequestConflict):
            self.store.accept({**payload, "idempotencyKey": uid()}, run_id=uid())

    def test_partial_domain_writes_rollback_and_failure_is_separate(self):
        payload, token = self.claim()
        self.rules.fail_after_write = True
        with self.assertRaises(RuntimeError):
            self.store.execute(token)
        self.assertEqual(self.node()["name"], "Before")
        self.assertEqual(self.node()["revision"], 1)
        self.assertEqual(self.histories(), 0)
        self.assertEqual(self.ledger(payload["requestId"])["commits"], [])
        self.assertEqual(self.ledger(payload["requestId"])["outbox"], [])
        result = self.store.finish_failed(token, outcome="FAILED", error_code="CONTROLLED",
                                          error_message="Controlled rollback test")
        self.assertEqual(result["outcome"], "FAILED")
        self.assertEqual(self.store.recover(token.run_id).result, result)
        ledger = self.ledger(payload["requestId"])
        self.assertEqual(ledger["commits"], [])
        self.assertEqual(len(ledger["outbox"]), 1)
        self.assertEqual(json.loads(ledger["outbox"][0]["payloadJson"]), result)

    def test_stale_worker_cannot_commit_after_explicit_takeover(self):
        payload, old = self.claim()
        newer = self.store.claim(old.run_id, uid(), expected_fence=old.fence)
        with self.assertRaises(self.api.RunOwnershipError):
            self.store.execute(old)
        self.assertEqual(self.node()["revision"], 1)
        self.assertEqual(self.store.execute(newer)["outcome"], "SUCCESS")

    def test_two_same_revision_requests_cannot_both_commit(self):
        _, first = self.claim()
        _, second = self.claim()
        with ThreadPoolExecutor(max_workers=2) as pool:
            futures = [pool.submit(self.store.execute, token) for token in (first, second)]
            results, errors = [], []
            for future in futures:
                try:
                    results.append(future.result(timeout=20))
                except self.api.RevisionConflict as error:
                    errors.append(error)
        self.assertEqual(len(results), 1)
        self.assertEqual(len(errors), 1)
        self.assertEqual(self.node()["revision"], 2)
        self.assertEqual(self.histories(), 1)

    def test_global_gate_protects_previously_absent_revision_neutral_data(self):
        marker = uid()
        first_rules, second_rules = FixtureRules(self.sync, self.actor), FixtureRules(self.sync, self.actor)
        first_rules.revision_neutral = True
        first_rules.write_marker, second_rules.check_marker = marker, marker
        first_rules.release = Event()
        first_store = self.api.Neo4jStore(self.driver, database=self.database, rules=first_rules)
        second_store = self.api.Neo4jStore(self.driver, database=self.database, rules=second_rules)
        _, first = self.claim(store=first_store)
        _, second = self.claim(store=second_store)
        second_started = Event()
        def execute_second():
            second_started.set()
            return second_store.execute(second)
        with ThreadPoolExecutor(max_workers=2) as pool:
            a = pool.submit(first_store.execute, first)
            self.assertTrue(first_rules.entered.wait(5))
            b = pool.submit(execute_second)
            try:
                self.assertTrue(second_started.wait(5))
                self.assertFalse(second_rules.entered.wait(0.25), "read occurred before acquiring the gate")
            finally:
                first_rules.release.set()
            self.assertEqual(a.result(timeout=10)["changedCount"], 0)
            with self.assertRaises(self.api.InvalidBundle):
                b.result(timeout=10)
        self.assertEqual(self.node()["revision"], 1)
        self.assertEqual(self.histories(), 0)

    def test_final_database_time_rejects_expiry_during_evaluation(self):
        _, token = self.claim()
        self.rules.release = Event()
        self.rules.deadline = datetime.now(timezone.utc) + timedelta(seconds=0.4)
        with ThreadPoolExecutor(max_workers=1) as pool:
            future = pool.submit(self.store.execute, token)
            try:
                self.assertTrue(self.rules.entered.wait(5))
                time.sleep(0.5)
            finally:
                self.rules.release.set()
            with self.assertRaises(self.api.InvalidBundle):
                future.result(timeout=10)
        self.assertEqual(self.node()["revision"], 1)

    def test_lost_success_ack_recovers_without_reapplying(self):
        driver = LostAckDriver(self.driver)
        store = self.api.Neo4jStore(driver, database=self.database, rules=self.rules)
        _, token = self.claim(store=store)
        driver.armed = True
        with self.assertRaises(self.api.CommitOutcomeUnknown):
            store.execute(token)
        recovery = store.recover(token.run_id)
        self.assertEqual(recovery.state, "SUCCESS")
        self.assertEqual(store.execute(token), recovery.result)
        self.assertEqual(self.rules.evaluate_calls, 1)
        self.assertEqual(self.histories(), 1)

    def test_lost_accept_ack_recovers_the_single_durable_request(self):
        driver = LostAckDriver(self.driver)
        store = self.api.Neo4jStore(driver, database=self.database, rules=self.rules)
        payload, run_id = self.payload(), uid()
        driver.armed = True
        with self.assertRaises(self.api.CommitOutcomeUnknown):
            store.accept(payload, run_id=run_id)
        self.assertEqual(store.recover(run_id).state, "QUEUED")
        self.assertEqual(store.accept(payload, run_id=uid()).run_id, run_id)
        ledger = self.ledger(payload["requestId"])
        self.assertEqual(ledger["requests"], [payload["requestId"]])
        self.assertEqual(len(ledger["runs"]), 1)
        self.assertEqual(store.execute(store.claim(run_id, uid()))["outcome"], "SUCCESS")
        self.assertEqual(self.rules.evaluate_calls, 1)

    def test_explicit_retry_preserves_failed_attempt_and_change_event(self):
        payload, token = self.claim()
        self.rules.fail_after_write = True
        with self.assertRaises(RuntimeError):
            self.store.execute(token)
        failure = self.store.finish_failed(token, outcome="FAILED", error_code="CONTROLLED",
                                           error_message="Known rollback before retry")
        successor = uid()
        accepted = self.store.retry(token.run_id, run_id=successor)
        self.assertEqual(accepted, self.store.retry(token.run_id, run_id=successor))
        with self.assertRaises(self.api.RequestConflict):
            self.store.retry(token.run_id, run_id=uid())
        self.rules.fail_after_write = False
        result = self.store.execute(self.store.claim(successor, uid()))
        self.assertEqual(result["outcome"], "SUCCESS")
        self.assertEqual(self.store.recover(token.run_id).result, failure)
        self.assertEqual(self.store.recover(successor).result, result)
        ledger = self.ledger(payload["requestId"])
        self.assertEqual(ledger["requests"], [payload["requestId"]])
        self.assertEqual(len(ledger["runs"]), 2)
        self.assertEqual(len(ledger["outbox"]), 2)
        self.assertEqual(len(ledger["commits"]), 1)
        self.assertEqual(self.node()["revision"], 2)
        self.assertEqual(self.histories(), 1)

    def test_final_validation_evidence_is_in_the_durable_receipt(self):
        class FinalReadRules(FixtureRules):
            def validate_at(inner, tx, payload, candidate, context):
                candidate["readRevisions"][self.actor] = 1
                return super().validate_at(tx, payload, candidate, context)
        rules = FinalReadRules(self.sync, self.actor)
        store = self.api.Neo4jStore(self.driver, database=self.database, rules=rules)
        payload, token = self.claim(store=store)
        store.execute(token)
        receipt = self.ledger(payload["requestId"])["commits"][0]
        self.assertEqual(json.loads(receipt["readRevisionsJson"]),
                         {self.target: 1, self.actor: 1})

    def test_apply_cannot_change_the_approved_evidence(self):
        class MutatingRules(FixtureRules):
            def apply(inner, tx, payload, candidate, context):
                result = super().apply(tx, payload, candidate, context)
                candidate["readRevisions"][self.actor] = 1
                return result
        rules = MutatingRules(self.sync, self.actor)
        store = self.api.Neo4jStore(self.driver, database=self.database, rules=rules)
        payload, token = self.claim(store=store)
        with self.assertRaises(self.api.InvalidBundle):
            store.execute(token)
        self.assertEqual(self.node()["revision"], 1)
        self.assertEqual(self.histories(), 0)
        self.assertEqual(self.ledger(payload["requestId"])["outbox"], [])

    def test_existing_owner_cannot_be_presented_as_new(self):
        class OmittedReadRules(FixtureRules):
            apply_called = False

            def evaluate(inner, tx, payload):
                candidate = super().evaluate(tx, payload)
                candidate["changedEntityIds"].append(self.actor)
                return candidate

            def apply(inner, tx, payload, candidate, context):
                inner.apply_called = True
                raise AssertionError("an existing owner without its read revision reached apply")
        rules = OmittedReadRules(self.sync, self.actor)
        store = self.api.Neo4jStore(self.driver, database=self.database, rules=rules)
        payload, token = self.claim(store=store)
        with self.assertRaises(self.api.InvalidBundle):
            store.execute(token)
        self.assertFalse(rules.apply_called)
        self.assertEqual(self.node()["revision"], 1)
        self.assertEqual(self.ledger(payload["requestId"])["commits"], [])

    def test_actually_new_owner_starts_at_one_without_history(self):
        new_id = uid()
        class NewOwnerRules(FixtureRules):
            def evaluate(inner, tx, payload):
                candidate = super().evaluate(tx, payload)
                candidate["changedEntityIds"].append(new_id)
                return candidate

            def apply(inner, tx, payload, candidate, context):
                result = super().apply(tx, payload, candidate, context)
                tx.run(
                    "MATCH (actor:JCIEntity {id:$actor}), (e:JCIEntity:SyncEvent {id:$event}) "
                    "CREATE (t:JCIEntity:Task {id:$id, entityType:'Task', name:'New test owner', "
                    "status:'DRAFT', taskKind:'ATOMIC', revision:1, "
                    "createdAt:$at, updatedAt:$at}) "
                    "CREATE (t)-[:CREATED_BY]->(actor), (e)-[:AFFECTS]->(t) "
                    "SET e.affectedCount=2, e.changedCount=2",
                    actor=self.actor, event=result["syncEventId"], id=new_id, at=context.decision_at,
                ).consume()
                result["affectedCount"] = result["changedCount"] = 2
                result["affectedEntityIds"].append(new_id)
                return result
        store = self.api.Neo4jStore(self.driver, database=self.database,
                                   rules=NewOwnerRules(self.sync, self.actor))
        _, token = self.claim(store=store)
        result = store.execute(token)
        self.assertEqual(result["changedCount"], 2)
        self.assertEqual(result["historyCount"], 1)
        with self.driver.session(database=self.database) as session:
            row = session.run(
                "MATCH (n:JCIEntity {id:$id}) "
                "OPTIONAL MATCH (n)-[:HAS_HISTORICAL_STATE]->(h) "
                "RETURN n.revision AS revision, count(h) AS histories", id=new_id,
            ).single(strict=True)
        self.assertEqual((row["revision"], row["histories"]), (1, 0))

    def test_worker_process_exit_rolls_back_before_recovery_and_retry(self):
        from dataclasses import asdict
        payload, token = self.claim()
        # Exit after real domain/event writes but before commit. This bypasses
        # Python cleanup and closes the worker's Bolt socket at process exit.
        worker = dedent('''
            import json, os, sys
            from pathlib import Path
            sys.path.insert(0, str(Path("tests/integration").resolve()))
            from test_neo4j_transactions import FixtureRules, URI
            from neo4j import GraphDatabase
            from jci_runtime.neo4j_store import Neo4jStore, RunToken
            data = json.load(sys.stdin)
            class CrashRules(FixtureRules):
                def apply(self, tx, payload, candidate, context):
                    super().apply(tx, payload, candidate, context)
                    os._exit(23)
            password = os.environ.get("JCI_NEO4J_TEST_PASSWORD")
            auth = (os.environ.get("JCI_NEO4J_TEST_USER", "neo4j"), password) if password else None
            driver = GraphDatabase.driver(URI, auth=auth,
                notifications_disabled_classifications=["UNRECOGNIZED"])
            store = Neo4jStore(driver, database=data["database"],
                rules=CrashRules(data["sync"], data["actor"]))
            store.execute(RunToken(**data["token"]))
        ''')
        process = subprocess.run(
            [sys.executable, "-B", "-c", worker],
            input=json.dumps({"database": self.database, "sync": self.sync,
                              "actor": self.actor, "token": asdict(token)}),
            text=True, capture_output=True, timeout=30,
            cwd=Path(__file__).resolve().parents[2],
        )
        self.assertEqual(process.returncode, 23, process.stderr)
        recovery = self.store.recover(token.run_id)
        self.assertEqual(recovery.state, "RUNNING")
        self.assertEqual(self.node()["revision"], 1)
        self.assertEqual(self.histories(), 0)
        self.assertEqual(self.ledger(payload["requestId"])["outbox"], [])
        owner = self.store.claim(token.run_id, uid(), expected_fence=recovery.token.fence)
        with self.assertRaises(self.api.RunOwnershipError):
            self.store.execute(token)
        failure = self.store.finish_failed(owner, outcome="FAILED", error_code="WORKER_EXIT",
                                           error_message="Worker exited before commit")
        successor = self.store.retry(token.run_id, run_id=uid())
        result = self.store.execute(self.store.claim(successor.run_id, uid()))
        self.assertEqual(result["outcome"], "SUCCESS")
        self.assertEqual(self.store.recover(token.run_id).result, failure)
        self.assertEqual(self.histories(), 1)
        self.assertEqual(len(self.ledger(payload["requestId"])["commits"]), 1)

    def test_false_result_counters_rollback_the_whole_bundle(self):
        _, token = self.claim()
        self.rules.corrupt_result = True
        with self.assertRaises(self.api.InvalidBundle):
            self.store.execute(token)
        self.assertEqual(self.node()["revision"], 1)
        self.assertEqual(self.histories(), 0)

    def test_changed_rules_package_is_rejected_before_domain_execution(self):
        _, token = self.claim()
        with self.driver.session(database=self.database) as session:
            session.run("MATCH (s:JCIEntity {id:$id}) SET s.revision=2", id=self.sync).consume()
        with self.assertRaises(self.api.ProfileMismatch):
            self.store.execute(token)
        self.assertEqual(self.rules.evaluate_calls, 0)


if __name__ == "__main__":
    unittest.main()
