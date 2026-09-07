"""Adversarial JCI 2.0 regressions against reusable reference functions.

Gate tests simulate the protocol and candidate decisions. They are deliberately
not Neo4j concurrency, crash-recovery, or deployment integration tests.
"""
from copy import deepcopy
from dataclasses import replace
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import unittest

from jsonschema import Draft202012Validator, FormatChecker, ValidationError

from reference import jci_rules as jci


ROOT = Path(__file__).resolve().parents[1]
TEAM = "11111111-1111-4111-8111-111111111111"
OTHER = "22222222-2222-4222-8222-222222222222"
NOW = datetime(2026, 9, 6, 12, tzinfo=timezone.utc)


def typed(value, kind="STRING"):
    return {"valueType": kind, "value": value}


def snapshot():
    return {"stateData": {
        "entityType": "Task", "revision": 1,
        "properties": {"name": typed("API"), "status": typed("ACTIVE"),
                       "taskKind": typed("ATOMIC")}
    }, "relationshipData": []}


def member_snapshot():
    result = {"stateData": {"entityType": "RoFTeamMember", "revision": 1,
                           "properties": {"name": typed("Anna"), "status": typed("ACTIVE"),
                                          "memberType": typed("HUMAN"), "displayName": typed("Anna")}},
              "relationshipData": []}
    result["relationshipData"].append({
        "direction": "INCOMING", "relationshipType": "HAS_MEMBER",
        "otherEntityId": TEAM, "otherEntityType": "RoFTeam",
        "properties": {"validFrom": typed("2026-01-01T00:00:00Z", "DATETIME")},
    })
    return result


def correction(before, *, identity="c1", fields=None, previous=None, corrected=None,
               kind="CORRECTION", supersedes=None, time="2026-09-06T12:00:00Z"):
    path = "/stateData/properties/name"
    return jci.HistoricalCorrectionRecord(
        identity, "history", time, tuple(fields or [path]),
        previous if previous is not None else {path: typed("API")},
        corrected if corrected is not None else {path: typed("New API")},
        kind, jci.history_hash(before), supersedes)


class OwnershipRegressionTests(unittest.TestCase):
    def test_catalog_is_closed_and_every_canonical_relationship_is_classified(self):
        from test_spec_consistency import RELATIONSHIPS
        self.assertEqual(RELATIONSHIPS, {key[1] for key in jci.RELATIONSHIP_OWNERS})
        for source, relation, target in jci.RELATIONSHIP_OWNERS:
            self.assertIn(source, jci.ENTITY_TYPES)
            self.assertIn(target, jci.ENTITY_TYPES)
            self.assertLessEqual(jci.revision_owners(source, relation, target), {"source", "target"})
        for context in [("Task", "INVENTED", "Task"),
                        ("Task", "CHECKS", "SuccessCriterion"),
                        ("RaN", "GOVERNS", "PiF2")]:
            with self.assertRaises(jci.RuleViolation):
                jci.revision_owners(*context)

    def test_overloaded_relationships_have_context_specific_owners(self):
        self.assertEqual(jci.revision_owners("Verification", "SUPERSEDES", "Verification"), {"source"})
        self.assertEqual(jci.revision_owners("HistoricalCorrection", "SUPERSEDES", "HistoricalCorrection"), {"source"})
        self.assertEqual(jci.revision_owners("RaNConflict", "AFFECTS", "Task"), {"source"})
        self.assertEqual(jci.revision_owners("SyncEvent", "AFFECTS", "Task"), {"source"})
        self.assertEqual(jci.revision_owners("PiH", "PROVIDES_CONTEXT_TO", "CiV"), {"target"})

    def test_verification_creation_does_not_stale_its_own_bound_revisions(self):
        entities = {
            "result": {"entityType": "Result", "status": "COMPLETED", "revision": 3},
            "criterion": {"entityType": "SuccessCriterion", "status": "ACTIVE", "revision": 2},
            "verification": {"entityType": "Verification", "status": "COMPLETED", "revision": 1},
            "older": {"entityType": "Verification", "status": "COMPLETED", "revision": 1},
        }
        edges = [jci.RelationshipChange("verification", "EVALUATES", "result"),
                 jci.RelationshipChange("verification", "CHECKS", "criterion"),
                 jci.RelationshipChange("verification", "SUPERSEDES", "older")]
        plan = jci.revision_plan(entities, edges, new_ids={"verification"})
        self.assertEqual(plan, {"verification": 1})
        args = dict(result_status="COMPLETED", criterion_status="ACTIVE",
                    same_pif1o=True, result_revision=3, criterion_revision=2,
                    evaluated_result_revision=3, checked_criterion_revision=2, superseded=False)
        self.assertTrue(jci.verification_is_applicable(**args))
        plan = jci.revision_plan(entities, changed_properties={"criterion"})
        self.assertEqual(plan, {"criterion": 3})
        self.assertFalse(jci.verification_is_applicable(**(args | {"criterion_revision": 3})))

    def test_audit_edges_do_not_recursively_revision_sync_or_roles(self):
        entities = {
            "sync": {"entityType": "SYNC", "status": "ACTIVE", "revision": 7},
            "event": {"entityType": "SyncEvent", "status": "RECORDED", "revision": 1},
            "request": {"entityType": "ChangeEvent", "status": "RECORDED", "revision": 1},
            "task": {"entityType": "Task", "status": "ACTIVE", "revision": 4},
        }
        edges = [jci.RelationshipChange("event", "EXECUTES", "sync"),
                 jci.RelationshipChange("event", "AFFECTS", "task"),
                 jci.RelationshipChange("request", "TRIGGERS", "event")]
        self.assertEqual(jci.revision_plan(entities, edges, new_ids={"event"}), {"event": 1})
        self.assertEqual(jci.revision_plan(
            entities, [jci.RelationshipChange("task", "CHANGED_BY", "request")],
            new_ids={"request"}), {"request": 1})

    def test_created_provenance_append_is_exactly_one_explicit_exception(self):
        entities = {
            "task": {"entityType": "Task", "status": "DRAFT", "revision": 1},
            "request": {"entityType": "ChangeEvent", "status": "RECORDED", "revision": 1,
                        "changeType": "CREATED", "targetEntityId": "task"},
            "role": {"entityType": "RoleAssignment", "status": "ACTIVE", "revision": 9},
        }
        edges = [jci.RelationshipChange("task", "CHANGED_BY", "request"),
                 jci.RelationshipChange("task", "CREATED_BY", "role")]
        self.assertEqual(jci.revision_plan(entities, edges, new_ids={"task"}), {"task": 1})
        with self.assertRaises(jci.RuleViolation):
            jci.revision_plan(entities, edges, new_ids={"task"}, existing_changed_by={"request"})
        with self.assertRaises(jci.RuleViolation):
            jci.revision_plan(entities, edges + edges[:1], new_ids={"task"})
        with self.assertRaises(jci.RuleViolation):
            jci.revision_plan(entities, [replace(edges[0], operation="DISCONNECT")], new_ids={"task"})

    def test_correction_and_import_creator_do_not_revision_referenced_targets(self):
        entities = {
            "correction": {"entityType": "HistoricalCorrection", "status": "RECORDED", "revision": 1},
            "history": {"entityType": "PiH", "status": "RECORDED", "revision": 1},
            "role": {"entityType": "RoleAssignment", "status": "ACTIVE", "revision": 5},
            "import": {"entityType": "Task", "status": "DRAFT", "revision": 2},
        }
        edges = [jci.RelationshipChange("correction", "CORRECTS", "history"),
                 jci.RelationshipChange("correction", "CORRECTED_BY", "role"),
                 jci.RelationshipChange("import", "CREATED_BY", "role")]
        self.assertEqual(jci.revision_plan(entities, edges, new_ids={"correction"}),
                         {"correction": 1, "import": 3})

    def test_new_task_has_no_predecessor_history_but_existing_goal_does(self):
        entities = {
            "task": {"entityType": "Task", "status": "DRAFT", "revision": 1},
            "goal": {"entityType": "PiF1o", "status": "ACTIVE", "revision": 4},
        }
        plan = jci.revision_plan(
            entities, [jci.RelationshipChange("goal", "DECOMPOSES_INTO", "task")],
            new_ids={"task"})
        self.assertEqual(plan, {"task": 1, "goal": 5})
        # Only changed existing entities supply a predecessor snapshot.
        histories = {identity: deepcopy(entities[identity])
                     for identity in plan if identity != "task"}
        self.assertEqual(histories["goal"]["revision"], 4)
        self.assertTrue(jci.valid_created_outcome(
            target_existed_before=False, requested_revision=None, outcome="SUCCESS",
            target_exists_after=True, target_revision_after=plan["task"],
            changed_by_count=1, target_history_count=int("task" in histories)))

    def test_structural_owners_are_deduplicated_and_terminal_edits_are_rejected(self):
        entities = {key: {"entityType": "Task", "status": "ACTIVE", "revision": number}
                    for key, number in [("a", 2), ("b", 3), ("c", 4)]}
        edges = [jci.RelationshipChange("a", "DEPENDS_ON", "b"),
                 jci.RelationshipChange("a", "DEPENDS_ON", "c")]
        self.assertEqual(jci.revision_plan(entities, edges, changed_properties={"a"}),
                         {"a": 3, "b": 4, "c": 5})
        entities["b"]["status"] = "COMPLETED"
        with self.assertRaises(jci.RuleViolation):
            jci.revision_plan(entities, edges)

    def test_snapshot_profile_excludes_incoming_reference_only_edges(self):
        data = snapshot()
        data["relationshipData"] = [{
            "direction": "INCOMING", "relationshipType": "AFFECTS",
            "otherEntityId": OTHER, "otherEntityType": "SyncEvent", "properties": {},
        }]
        with self.assertRaises(jci.RuleViolation):
            jci.validate_snapshot(data)


class CompletionRegressionTests(unittest.TestCase):
    def test_retired_task_stays_assigned_but_current_successor_can_achieve_goal(self):
        tasks = {"old": jci.TaskRecord("old", "g", "REPLACED", replaced_by="new"),
                 "new": jci.TaskRecord("new", "g", "COMPLETED")}
        criteria = [jci.CriterionRecord("k", "g"),
                    jci.CriterionRecord("old-k", "g", "REVOKED")]
        results = {"r": jci.ResultRecord("r", "new")}
        checks = [jci.VerificationRecord("v", "r", "k", 1, 1)]
        before = deepcopy(tasks)
        self.assertTrue(jci.pif1o_achievable("g", tasks, criteria, results, checks, model_valid=True))
        self.assertEqual(tasks, before)
        # Former proof is not silently reassigned from an excluded task.
        results["r"] = jci.ResultRecord("r", "old")
        self.assertFalse(jci.pif1o_achievable("g", tasks, criteria, results, checks, model_valid=True))

    def test_empty_scope_draft_required_and_stale_or_invalid_proof_block_success(self):
        tasks = {"t": jci.TaskRecord("t", "g", "COMPLETED")}
        criterion = jci.CriterionRecord("k", "g")
        results = {"r": jci.ResultRecord("r", "t")}
        valid = jci.VerificationRecord("v", "r", "k", 1, 1)
        self.assertFalse(jci.pif1o_achievable("g", {}, [criterion], {}, [], model_valid=True))
        self.assertFalse(jci.pif1o_achievable("g", tasks, [], results, [valid], model_valid=True))
        for changed in [replace(criterion, status="DRAFT"), replace(criterion, revision=2),
                        replace(criterion, status="REVOKED")]:
            self.assertFalse(jci.pif1o_achievable("g", tasks, [changed], results, [valid], model_valid=True))
        invalid = jci.VerificationRecord("v2", "r", "k", 1, 1, "INVALID", "v")
        self.assertFalse(jci.pif1o_achievable("g", tasks, [criterion], results, [valid, invalid], model_valid=True))
        with self.assertRaises(jci.RuleViolation):
            jci.pif1o_achievable("g", tasks, [criterion], results,
                                 [valid, replace(valid, id="duplicate")], model_valid=True)

    def test_retired_dependency_is_not_replaced_implicitly(self):
        tasks = {"old": jci.TaskRecord("old", "g", "REPLACED", replaced_by="new"),
                 "new": jci.TaskRecord("new", "g", "COMPLETED"),
                 "dependent": jci.TaskRecord("dependent", "g", "ACTIVE", depends_on=("old",))}
        states = jci.derive_task_states(tasks, validated_tasks={"dependent"})
        self.assertEqual(states["dependent"], "BLOCKED")

    def test_retired_parent_cannot_hide_current_descendants_or_empty_current_parent(self):
        tasks = {"c": jci.TaskRecord("c", "g", "REVOKED", "COMPOSITE", ("a",)),
                 "a": jci.TaskRecord("a", "g", "ACTIVE")}
        with self.assertRaises(jci.RuleViolation):
            jci.current_task_scope(tasks)
        tasks["c"] = replace(tasks["c"], status="ACTIVE")
        tasks["a"] = replace(tasks["a"], status="REVOKED")
        with self.assertRaises(jci.RuleViolation):
            jci.current_task_scope(tasks)

    def test_composite_own_dependencies_precede_completed_children(self):
        self.assertEqual(jci.composite_status("ACTIVE", ["COMPLETED"], ["ACTIVE"]), "BLOCKED")
        self.assertEqual(jci.composite_status("BLOCKED", ["COMPLETED"], ["COMPLETED"]), "COMPLETED")
        self.assertEqual(jci.composite_status("BLOCKED", ["DRAFT"]), "ACTIVE")
        self.assertEqual(jci.composite_status("ACTIVE", ["DRAFT", "COMPLETED", "BLOCKED"]), "BLOCKED")
        self.assertEqual(jci.composite_status("ACTIVE", ["ACTIVE", "BLOCKED"]), "ACTIVE")
        tasks = {"c": jci.TaskRecord("c", "g", "ACTIVE", "COMPOSITE", ("a",), ("release",)),
                 "a": jci.TaskRecord("a", "g", "ACTIVE"),
                 "release": jci.TaskRecord("release", "g", "ACTIVE")}
        states = jci.derive_task_states(tasks, confirmed_completions={"a"}, validated_tasks={"a", "c"})
        self.assertEqual(states["a"], "COMPLETED")
        self.assertEqual(states["c"], "BLOCKED")

    def test_stored_parent_limit_and_cycles_also_apply_to_retired_tasks(self):
        tasks = {"old": jci.TaskRecord("old", "g", "REVOKED", "COMPOSITE", ("a",)),
                 "current": jci.TaskRecord("current", "g", "ACTIVE", "COMPOSITE", ("a",)),
                 "a": jci.TaskRecord("a", "g", "ACTIVE")}
        with self.assertRaisesRegex(jci.RuleViolation, "multiple stored parents"):
            jci.current_task_scope(tasks)
        tasks = {"a": jci.TaskRecord("a", "g", "REVOKED", depends_on=("b",)),
                 "b": jci.TaskRecord("b", "g", "REVOKED", depends_on=("a",))}
        with self.assertRaises(jci.CompletionCycle):
            jci.current_task_scope(tasks)
        tasks = {"a": jci.TaskRecord("a", "g", "REVOKED", "COMPOSITE", ("b",)),
                 "b": jci.TaskRecord("b", "g", "REVOKED", "COMPOSITE", ("a",))}
        with self.assertRaises(jci.CompletionCycle):
            jci.current_task_scope(tasks)

    def test_draft_requires_release_and_terminal_facts_are_not_reopened(self):
        self.assertEqual(jci.composite_status("DRAFT", ["COMPLETED"]), "DRAFT")
        self.assertEqual(jci.composite_status("DRAFT", ["COMPLETED"], release=True), "ACTIVE")
        with self.assertRaises(jci.RuleViolation):
            jci.composite_status("COMPLETED", ["DRAFT"])
        with self.assertRaises(jci.RuleViolation):
            jci.composite_status("COMPLETED", ["COMPLETED"], ["REVOKED"])
        tasks = {"c": jci.TaskRecord("c", "g", "DRAFT", "COMPOSITE", ("a",)),
                 "a": jci.TaskRecord("a", "g", "COMPLETED")}
        with self.assertRaises(jci.RuleViolation):
            jci.derive_task_states(tasks, confirmed_completions={"c"}, validated_tasks={"c"})

    def test_mixed_cycle_reports_original_edge_types(self):
        tasks = {"c": jci.TaskRecord("c", "g", "ACTIVE", "COMPOSITE", ("a",)),
                 "a": jci.TaskRecord("a", "g", "ACTIVE", depends_on=("c",))}
        with self.assertRaises(jci.CompletionCycle) as caught:
            jci.completion_order(tasks)
        self.assertEqual({edge[1] for edge in caught.exception.cycle},
                         {"DECOMPOSES_INTO", "DEPENDS_ON"})
        self.assertEqual(len(caught.exception.cycle), 2)

    def test_explicit_composite_release_preserves_child_blocking_without_completing(self):
        self.assertEqual(jci.composite_status("DRAFT", ["BLOCKED"]), "DRAFT")
        self.assertEqual(jci.composite_status("DRAFT", ["BLOCKED"], release=True), "BLOCKED")
        self.assertEqual(jci.composite_status("DRAFT", ["ACTIVE", "BLOCKED"], release=True), "ACTIVE")
        self.assertEqual(jci.composite_status("DRAFT", ["COMPLETED"], release=True), "ACTIVE")
        tasks = {"c": jci.TaskRecord("c", "g", "DRAFT", "COMPOSITE", ("a",)),
                 "a": jci.TaskRecord("a", "g", "ACTIVE", depends_on=("p",)),
                 "p": jci.TaskRecord("p", "g", "DRAFT")}
        states = jci.derive_task_states(tasks, releases={"c"}, validated_tasks={"a", "c"})
        self.assertEqual(states, {"p": "DRAFT", "a": "BLOCKED", "c": "BLOCKED"})

    def test_one_candidate_checks_new_edges_together_across_goals(self):
        tasks = {"a": jci.TaskRecord("a", "one", "ACTIVE", depends_on=("b",)),
                 "b": jci.TaskRecord("b", "two", "ACTIVE", depends_on=("a",))}
        with self.assertRaises(jci.CompletionCycle):
            jci.completion_order(tasks)

    def test_atomic_depending_on_composite_is_evaluated_after_it(self):
        tasks = {"consumer": jci.TaskRecord("consumer", "g2", "BLOCKED", depends_on=("c",)),
                 "c": jci.TaskRecord("c", "g", "ACTIVE", "COMPOSITE", ("a",)),
                 "a": jci.TaskRecord("a", "g", "ACTIVE")}
        order = jci.completion_order(tasks)
        self.assertLess(order.index("a"), order.index("c"))
        self.assertLess(order.index("c"), order.index("consumer"))
        states = jci.derive_task_states(tasks, confirmed_completions={"a", "consumer"},
                                       validated_tasks=tasks.keys())
        self.assertEqual(set(states.values()), {"COMPLETED"})

    def test_long_dependency_chain_does_not_hit_python_recursion_limit(self):
        tasks = {f"t{i}": jci.TaskRecord(f"t{i}", "g", "ACTIVE",
                                       depends_on=((f"t{i+1}",) if i < 1500 else ()))
                 for i in range(1501)}
        self.assertEqual(jci.completion_order(tasks)[0], "t1500")


class CorrectionRegressionTests(unittest.TestCase):
    def test_pointer_escapes_use_decoded_segments_without_false_prefixes(self):
        self.assertEqual(jci.parse_pointer("/a~1b/~01"), ("a/b", "~1"))
        self.assertEqual(jci.encode_pointer(("a/b", "~1")), "/a~1b/~01")
        self.assertFalse(jci.paths_overlap("/a~1b", "/a/b"))
        self.assertFalse(jci.paths_overlap("/name", "/nameLong"))
        self.assertTrue(jci.paths_overlap("/a~1b", "/a~1b/c"))
        for path in ["", "#/name", "/a~", "/a~2"]:
            with self.assertRaises(jci.RuleViolation):
                jci.parse_pointer(path)

    def test_only_schema_properties_and_stable_relationship_keys_are_allowed(self):
        jci.parse_correction_path("/stateData/properties/name", "Task")
        path = f"/relationshipData/INCOMING:HAS_MEMBER:{TEAM}/properties/validUntil"
        jci.parse_correction_path(path, "RoFTeamMember")
        for path in ["/stateData/name", "/stateData/properties/unknown",
                     "/stateData/properties/value/value/0", "/stateData/properties",
                     "/relationshipData/0", "/relationshipData/-",
                     f"/relationshipData/OUT:HAS_MEMBER:{TEAM}",
                     f"/relationshipData/INCOMING:HAS_MEMBER:{TEAM}/properties/unknown"]:
            with self.assertRaises(jci.RuleViolation):
                jci.parse_correction_path(path, "Task")

    def test_parent_and_child_corrections_are_not_disjoint(self):
        base = member_snapshot()
        key = f"/relationshipData/INCOMING:HAS_MEMBER:{TEAM}"
        first = correction(base, fields=[key],
                           previous={key: typed(base["relationshipData"][0], "OBJECT")},
                           corrected={key: typed(base["relationshipData"][0], "OBJECT")})
        view = jci.validate_correction(base, [], first, pih="history", expected_hash=first.base_hash)
        child = key + "/properties/validFrom"
        second = correction(view, identity="c2", fields=[child],
                            previous={child: typed("2026-01-01T00:00:00Z", "DATETIME")},
                            corrected={child: typed("2026-02-01T00:00:00Z", "DATETIME")})
        with self.assertRaises(jci.RuleViolation):
            jci.validate_correction(base, [first], second, pih="history", expected_hash=second.base_hash)
        both = replace(first, fields=(key, child),
                       previous={**first.previous, child: typed("2026-01-01T00:00:00Z", "DATETIME")},
                       corrected={**first.corrected, child: typed("2026-02-01T00:00:00Z", "DATETIME")})
        with self.assertRaises(jci.RuleViolation):
            jci.validate_correction(base, [], both, pih="history", expected_hash=both.base_hash)

    def test_addition_then_supersession_replays_absolute_corrected_values(self):
        base = snapshot()
        original = deepcopy(base)
        path = "/stateData/properties/description"
        first = correction(base, fields=[path], previous={path: jci.NULL_VALUE},
                           corrected={path: typed("First")}, kind="ADDITION")
        view = jci.validate_correction(base, [], first, pih="history", expected_hash=first.base_hash)
        second = correction(view, identity="c2", fields=[path], previous={path: typed("First")},
                            corrected={path: typed("Second")}, supersedes="c1",
                            time="2026-09-06T12:00:01Z")
        final = jci.validate_correction(base, [first], second, pih="history", expected_hash=second.base_hash)
        self.assertEqual(final["stateData"]["properties"]["description"], typed("Second"))
        self.assertEqual(jci.build_history_view(base, [second, first], pih="history"), final)
        self.assertEqual(base, original)

    def test_existing_null_is_not_absence_and_null_is_not_deletion(self):
        base = snapshot()
        path = "/stateData/properties/description"
        base["stateData"]["properties"]["description"] = deepcopy(jci.NULL_VALUE)
        candidate = correction(base, fields=[path], previous={path: jci.NULL_VALUE},
                               corrected={path: typed("Text")}, kind="ADDITION")
        with self.assertRaises(jci.RuleViolation):
            jci.validate_correction(base, [], candidate, pih="history", expected_hash=candidate.base_hash)
        candidate = replace(candidate, correction_type="CORRECTION", corrected={path: jci.NULL_VALUE})
        view = jci.validate_correction(base, [], candidate, pih="history", expected_hash=candidate.base_hash)
        self.assertIn("description", view["stateData"]["properties"])

    def test_multiple_predecessors_partial_supersession_and_stale_hash_conflict(self):
        base = snapshot()
        first = correction(base)
        view1 = jci.validate_correction(base, [], first, pih="history", expected_hash=first.base_hash)
        path = "/stateData/properties/taskType"
        second = correction(view1, identity="c2", fields=[path], previous={path: jci.NULL_VALUE},
                            corrected={path: typed("Deployment")}, kind="ADDITION")
        view2 = jci.validate_correction(base, [first], second, pih="history", expected_hash=second.base_hash)
        fields = ("/stateData/properties/name", path)
        third = correction(view2, identity="c3", fields=fields,
                           previous={fields[0]: typed("New API"), path: typed("Deployment")},
                           corrected={fields[0]: typed("Final"), path: typed("Delivery")},
                           supersedes="c1", time="2026-09-06T12:00:02Z")
        with self.assertRaises(jci.RuleViolation):
            jci.validate_correction(base, [first, second], third, pih="history", expected_hash=third.base_hash)
        with self.assertRaises(jci.RuleViolation):
            jci.validate_correction(base, [first], second, pih="history", expected_hash="0"*64)

    def test_relationship_reordering_is_hash_and_address_stable(self):
        base = member_snapshot()
        another = deepcopy(base["relationshipData"][0])
        another["otherEntityId"] = OTHER
        base["relationshipData"].append(another)
        reversed_base = deepcopy(base)
        reversed_base["relationshipData"].reverse()
        self.assertEqual(jci.history_hash(base), jci.history_hash(reversed_base))
        duplicate = deepcopy(base)
        duplicate["relationshipData"].append(deepcopy(another))
        with self.assertRaises(jci.RuleViolation):
            jci.history_hash(duplicate)
        for bad_id in ["ABCDEFAB-1111-4111-8111-111111111111", TEAM.replace("-", "")]:
            malformed = deepcopy(base)
            malformed["relationshipData"][0]["otherEntityId"] = bad_id
            with self.assertRaises(jci.RuleViolation):
                jci.history_hash(malformed)

    def test_correction_timestamp_is_required_even_without_supersession(self):
        base = snapshot()
        for timestamp in ["not-a-date", "2026-09-06T12:00:00"]:
            bad = correction(base, time=timestamp)
            with self.assertRaises(jci.RuleViolation):
                jci.validate_correction(base, [], bad, pih="history", expected_hash=bad.base_hash)

    def test_array_property_is_replaced_as_one_typed_unit(self):
        base = snapshot()
        base["stateData"] = {"entityType": "RaN", "revision": 1,
                             "properties": {"name": typed("Rule"),
                                            "governedTypes": typed(["Task"], "ARRAY")}}
        path = "/stateData/properties/governedTypes"
        candidate = correction(base, fields=[path], previous={path: typed(["Task"], "ARRAY")},
                               corrected={path: typed(["Task", "Result"], "ARRAY")})
        view = jci.validate_correction(base, [], candidate, pih="history", expected_hash=candidate.base_hash)
        self.assertEqual(view["stateData"]["properties"]["governedTypes"]["value"], ["Task", "Result"])
        with self.assertRaises(jci.RuleViolation):
            jci.parse_correction_path(path + "/value/0", "RaN")

    def test_legacy_profiles_require_explicit_resolvers_and_never_mutate_original(self):
        legacy = {"stateData": {"name": "old shape"}, "relationshipData": []}
        original = deepcopy(legacy)
        with self.assertRaises(jci.LegacyProfileRequired):
            jci.build_history_view(legacy, [], pih="old", snapshot_profile="1.0")
        def original_profile(data, records, *, pih):
            self.assertEqual(pih, "old")
            data["stateData"]["name"] = "legacy-specific view"
            return data
        output = jci.build_history_view(legacy, [], pih="old", snapshot_profile="1.0",
                                       legacy_resolvers={"1.0": original_profile})
        self.assertEqual(output["stateData"]["name"], "legacy-specific view")
        self.assertEqual(legacy, original)
        with self.assertRaises(jci.LegacyProfileRequired):
            jci.parse_correction_path("/stateData/properties/name", "Task", profile="1.0")

    def test_exact_canonical_bytes_preserve_integer_precision_and_unicode(self):
        self.assertEqual(jci.canonical_json({"b": 9007199254740993, "a": "ä/~\n"}),
                         b'{"a":"\xc3\xa4/~\\n","b":9007199254740993}')
        huge = 10**5000 + 1
        raw = jci.canonical_json({"n": huge})
        self.assertEqual(jci.parse_exact_json(raw.decode())["n"], huge)
        for bad in [1.25, {"nested": [1.0]}, float("nan")]:
            with self.assertRaises(jci.RuleViolation):
                jci.canonical_json(bad)
        for bad in ['{"x":1,"x":2}', '{"x":1.0}', '{"x":1e20}', '{"x":NaN}']:
            with self.assertRaises(jci.RuleViolation):
                jci.parse_exact_json(bad)
        for bad in ["-0", "01", "1.0", "1e2"]:
            with self.assertRaises(jci.RuleViolation):
                jci.validate_typed_value(typed(bad, "DECIMAL"))
        jci.validate_typed_value(typed("-0.001", "DECIMAL"))

    def test_history_hash_matches_independently_written_canonical_payload(self):
        expected = (b'{"relationshipData":[],"stateData":{"entityType":"Task","properties":'
                    b'{"name":{"value":"API","valueType":"STRING"},"status":{"value":"ACTIVE","valueType":"STRING"},'
                    b'"taskKind":{"value":"ATOMIC","valueType":"STRING"}},"revision":1}}')
        self.assertEqual(jci.canonical_json(snapshot()), expected)
        self.assertEqual(jci.history_hash(snapshot()), hashlib.sha256(expected).hexdigest())

    def test_shared_history_hash_vectors(self):
        fixture = ROOT / "tests" / "fixtures" / "history-profile-2.0.json"
        vectors = jci.parse_exact_json(fixture.read_text(encoding="utf-8"))
        self.assertEqual(vectors["profile"], "2.0")
        for vector in vectors["vectors"]:
            with self.subTest(vector=vector["name"]):
                expected = vector["canonicalUtf8"].encode("utf-8")
                self.assertEqual(hashlib.sha256(expected).hexdigest(), vector["sha256"])
                output = jci.build_history_view(vector["payload"], [], pih="fixture")
                self.assertEqual(jci.canonical_json(output), expected)
                self.assertEqual(jci.history_hash(vector["payload"]), vector["sha256"])


class WriteGateSimulationTests(unittest.TestCase):
    """State-machine regressions only; no live Neo4j isolation claim."""
    def base(self):
        state = jci.accept_request(jci.GateState(), "a", {"requestId": "a", "operation": "one"})
        return jci.accept_request(state, "b", {"requestId": "b", "operation": "two"})

    def test_two_individually_valid_candidates_cannot_commit_mixed_cycle(self):
        tasks = {"a": jci.TaskRecord("a", "g", "ACTIVE"),
                 "b": jci.TaskRecord("b", "g", "ACTIVE")}
        candidate_a = dict(tasks, a=replace(tasks["a"], depends_on=("b",)))
        candidate_b = dict(tasks, b=replace(tasks["b"], depends_on=("a",)))
        jci.completion_order(candidate_a)
        jci.completion_order(candidate_b)
        state = self.base()
        old_epoch = state.epoch
        first = jci.acquire_gate(state, "run-a")
        committed = jci.gate_commit(first, run_id="run-a", fence=first.fence,
                                   expected_epoch=old_epoch, request_key="a",
                                   outcome={"ok": True}, validate_at=lambda _: True, decision_at=NOW)
        second = jci.acquire_gate(committed, "run-b")
        with self.assertRaises(jci.RuleViolation):
            jci.gate_commit(second, run_id="run-b", fence=second.fence,
                            expected_epoch=old_epoch, request_key="b", outcome={},
                            validate_at=lambda _: True, decision_at=NOW)
        fresh_union = dict(candidate_a, b=candidate_b["b"])
        with self.assertRaises(jci.CompletionCycle):
            jci.completion_order(fresh_union)

    def test_revision_neutral_verification_or_new_rule_invalidates_precomputation(self):
        for reason in ("new prohibiting rule", "VALID superseded by INVALID", "membership allocation"):
            with self.subTest(reason=reason):
                state = self.base()
                expected_epoch = state.epoch
                writer = jci.acquire_gate(state, "documentation-writer")
                after = jci.gate_audit_append(writer, run_id=writer.owner, fence=writer.fence)
                reader = jci.acquire_gate(after, "aggregation")
                with self.assertRaises(jci.RuleViolation):
                    jci.gate_commit(reader, run_id=reader.owner, fence=reader.fence,
                                    expected_epoch=expected_epoch, request_key="b", outcome={},
                                    validate_at=lambda _: True, decision_at=NOW)

    def test_final_decision_time_detects_role_expiry_while_waiting(self):
        state = jci.acquire_gate(self.base(), "run")
        expiry = NOW
        with self.assertRaises(jci.RuleViolation):
            jci.gate_commit(state, run_id="run", fence=state.fence,
                            expected_epoch=state.epoch, request_key="a", outcome={},
                            validate_at=lambda instant: instant < expiry, decision_at=NOW)

    def test_fencing_idempotency_and_unknown_success_response(self):
        state = self.base()
        with self.assertRaises(jci.RuleViolation):
            jci.accept_request(state, "a", {"requestId": "a", "operation": "DIFFERENT"})
        first = jci.acquire_gate(state, "run")
        released = jci.release_gate(first, run_id="run", fence=first.fence)
        recovered = jci.acquire_gate(released, "run")
        with self.assertRaises(jci.RuleViolation):
            jci.gate_commit(recovered, run_id="run", fence=first.fence,
                            expected_epoch=recovered.epoch, request_key="a", outcome={},
                            validate_at=lambda _: True, decision_at=NOW)
        done = jci.gate_commit(recovered, run_id="run", fence=recovered.fence,
                               expected_epoch=recovered.epoch, request_key="a", outcome={"saved": True},
                               validate_at=lambda _: True, decision_at=NOW)
        self.assertEqual(done.successes["a"], ("run", {"saved": True}))
        retry = jci.acquire_gate(done, "retry")
        with self.assertRaises(jci.RuleViolation):
            jci.gate_commit(retry, run_id="retry", fence=retry.fence, expected_epoch=retry.epoch,
                            request_key="a", outcome={}, validate_at=lambda _: True, decision_at=NOW)


class ExchangeProfileRegressionTests(unittest.TestCase):
    def setUp(self):
        folder = ROOT / "docs" / "schemas"
        self.request_schema = json.loads((folder / "jci-change-request.schema.json").read_text(encoding="utf-8"))
        self.validator = Draft202012Validator(self.request_schema, format_checker=FormatChecker())

    def test_schema_is_valid_and_legacy_stays_separate(self):
        for path in (ROOT / "docs" / "schemas").rglob("*.schema.json"):
            schema = json.loads(path.read_text(encoding="utf-8"))
            Draft202012Validator.check_schema(schema)
            if "legacy" in path.parts:
                self.assertEqual(schema["properties"]["schemaVersion"]["const"], "1.1")
            elif "schemaVersion" in schema["properties"]:
                self.assertEqual(schema["properties"]["schemaVersion"]["const"], "2.0")

    def test_typed_values_reject_mismatched_types_and_unsafe_decimal_notation(self):
        schema = {"$ref": "#/$defs/typedValue", "$defs": self.request_schema["$defs"]}
        validator = Draft202012Validator(schema, format_checker=FormatChecker())
        for bad in [typed(True, "INTEGER"), typed("3", "INTEGER"), typed(3, "STRING"),
                    typed(0.1, "DECIMAL"), typed("-0", "DECIMAL"), typed("1.00", "DECIMAL"),
                    typed("2026-09-06T12:00:00", "DATETIME"), typed([0.1], "ARRAY")]:
            with self.subTest(value=bad), self.assertRaises(ValidationError):
                validator.validate(bad)
        validator.validate(typed(9007199254740993, "INTEGER"))
        validator.validate(typed([typed("0.1", "DECIMAL")], "ARRAY"))

    def test_transport_rejects_unknown_entity_relationship_and_old_correction_paths(self):
        validator = Draft202012Validator(
            {"$ref": "#/$defs/correctionPath", "$defs": self.request_schema["$defs"]})
        for bad in ["/stateData/name", "/stateData/properties/madeUp",
                    "/stateData/properties/value/value/0", "/relationshipData/0",
                    f"/relationshipData/INCOMING:MAGIC:{TEAM}"]:
            with self.assertRaises(ValidationError):
                validator.validate(bad)
        validator.validate("/stateData/properties/name")
        entity = self.request_schema["properties"]["target"]["properties"]["entityType"]
        self.assertEqual(set(entity["enum"]), set(jci.ENTITY_TYPES))
        self.assertEqual(set(self.request_schema["$defs"]["operation"]["properties"]["relationshipType"]["enum"]),
                         {key[1] for key in jci.RELATIONSHIP_OWNERS})


if __name__ == "__main__":
    unittest.main()
