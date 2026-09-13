"""Protocol tests use an HMAC identity adapter as a test double, not production IAM."""

from copy import deepcopy
from dataclasses import replace
import hashlib
import hmac
import unittest
from uuid import NAMESPACE_URL, uuid5

from reference.jci_approval import (
    APPROVAL_PROFILE, CONFIRM, RELEASE, ApprovalConflict, ApprovalDenied,
    ApprovalRequired, ApprovalContext, ApprovalEdge, ApprovalGraph, ApprovalWorkflow,
    EnrollmentAuthority, accept_approved_request, commit_approved_request,
    enrollment_latches, evaluate_approval_condition, make_approval_context,
    record_approval_receipt, register_proposal, release_with_approval,
    validate_approval_envelope, validate_approval_policy,
)
from reference.jci_rules import (
    GateState, RuleViolation, TaskRecord, acquire_gate, canonical_json,
    revision_owners, revision_plan, valid_ran_protection,
)


def uid(name):
    return str(uuid5(NAMESPACE_URL, "urn:jci:approval-test:" + name))


AT = "2026-09-08T10:00:00Z"
START = "2026-01-01T00:00:00Z"
DECIDED = "2026-09-08T09:30:00Z"
EXPIRES = "2026-09-08T12:00:00Z"


def expression(path="target.entityType", operator="EQUALS", value="Task"):
    clause = {"path": path, "operator": operator}
    if operator not in {"EXISTS", "NOT_EXISTS"}:
        clause["value"] = value
    return {"combiner": "ALL", "clauses": [clause]}


class ApprovalRuleTests(unittest.TestCase):
    def setUp(self):
        self.nodes = {}
        self.edges = []
        self.org = self.node("org", "RoFOrg")
        self.team = self.node("team", "RoFTeam", validFrom=START)
        self.edge(self.org, "HAS_TEAM", self.team)
        self.members, self.roles, self.assignments = [], [], []
        for index in range(4):
            member, role, assignment = self.actor(str(index), self.team)
            self.members.append(member)
            self.roles.append(role)
            self.assignments.append(assignment)
        self.goals = []
        for index, kind in enumerate(("PiF1o", "PiF1t", "PiF1s", "PiF2")):
            goal = self.node(kind, kind, targetState=kind, contributionMode="ALL")
            self.goals.append(goal)
            self.edge(goal, "ACCOUNTABLE_MEMBER", self.members[index])
        for source, target in zip(self.goals, self.goals[1:]):
            self.edge(source, "CONTRIBUTES_TO", target)
        self.value = self.node("value", "CiV", notCiV="No opacity", selfCiV="Clear decisions", toServeCiV="People")
        self.edge(self.value, "HELD_BY", self.org)
        self.edge(self.value, "INSCRIBES_PURPOSE_IN", self.goals[-1])
        self.task = self.node("task", "Task", status="DRAFT", taskKind="ATOMIC")
        self.edge(self.goals[0], "DECOMPOSES_INTO", self.task)
        self.edge(self.task, "RESPONSIBLE_TEAM", self.team)
        self.edge(self.task, "EXECUTED_BY", self.assignments[0])
        self.rule = self.policy("release-rule", RELEASE, "ACCOUNTABLE_CHAIN", [self.roles[0]], ["PiF1o"])
        self.value_rule = self.policy("value-rule", CONFIRM, "VALUE_SCOPE", [self.roles[0]])
        self.proposal = {
            "schemaVersion": "2.0", "requestId": uid("request"), "idempotencyKey": "release-request",
            "requestedAt": "2026-09-08T09:00:00Z", "requestedRevision": 1,
            "changeType": "CHANGED", "target": {"id": self.task, "entityType": "Task"},
            "requestedByRoleAssignmentId": self.assignments[1], "reason": "Release agreed work",
            "operations": [{"op": "REPLACE", "path": "/status", "value": {"valueType": "STRING", "value": "ACTIVE"}}],
        }

    def node(self, name, kind, **properties):
        identity = uid(name)
        self.nodes[identity] = {"id": identity, "entityType": kind, "status": "ACTIVE",
                                "name": name, "revision": 1, **properties}
        return identity

    def edge(self, source, relation, target, **properties):
        self.edges.append(ApprovalEdge(source, relation, target, properties))

    def actor(self, suffix, team):
        member = self.node("member-" + suffix, "RoFTeamMember", memberType="HUMAN")
        role = self.node("role-" + suffix, "RoFRole", roleName="Role " + suffix)
        assignment = self.node("assignment-" + suffix, "RoleAssignment", validFrom=START)
        self.edge(team, "HAS_MEMBER", member, validFrom=START)
        self.edge(member, "HAS_ROLE", role, validFrom=START)
        self.edge(member, "HAS_ASSIGNMENT", assignment)
        self.edge(assignment, "IN_TEAM", team)
        self.edge(assignment, "ACTIVATES_ROLE", role)
        return member, role, assignment

    def policy(self, name, decision, mode, roles, levels=()):
        policy = {"profileVersion": APPROVAL_PROFILE, "mode": mode, "roleIds": list(roles)}
        if levels:
            policy["levels"] = list(levels)
        rule = self.node(name, "RaN", ruleType="POLICY", effect="PERMIT", statement=name,
                         decisionKey=decision, scopeType="GLOBAL", validFrom=START,
                         governedTypes=["Task" if decision == RELEASE else "RoleAssignment"],
                         priority=10, condition=expression(value="Task" if decision == RELEASE else "RoleAssignment"),
                         approvalPolicy=policy)
        self.edge(rule, "PROTECTS", self.value)
        self.edge(rule, "PROTECTS", self.goals[-1])
        self.edge(rule, "GOVERNS", self.task if decision == RELEASE else self.assignments[0])
        return rule

    def graph(self):
        return ApprovalGraph(deepcopy(self.nodes), tuple(deepcopy(self.edges)))

    def sign(self, receipt):
        payload = {key: value for key, value in receipt.items() if key != "attestation"}
        # Per-human keys represent an external authenticated test identity registry.
        key = ("test-only-secret-" + receipt["memberId"]).encode()
        return hmac.new(key, canonical_json(payload), hashlib.sha256).hexdigest()

    def verify(self, receipt):
        return receipt["memberId"] if hmac.compare_digest(receipt["attestation"], self.sign(receipt)) else None

    def receipt(self, context, index=0, outcome="APPROVED", **changes):
        record = {"receiptId": uid("receipt-" + str(index)), "requestHash": context.request_hash,
                  "contextHash": context.context_hash, "decidedAt": DECIDED, "validUntil": EXPIRES,
                  "outcome": outcome, "roleAssignmentId": self.assignments[index],
                  "memberId": self.members[index], **changes}
        record["attestation"] = self.sign(record)
        return record

    def envelope(self, indices=(0,), proposal=None, **context_options):
        proposal = deepcopy(proposal or self.proposal)
        context = make_approval_context(self.graph(), proposal, at=AT, **context_options)
        receipts = [self.receipt(context, i) for i in indices]
        return {"approvalProfileVersion": APPROVAL_PROFILE, "decisionKey": context.decision_key,
                "proposal": proposal, "requestHash": context.request_hash, "contextHash": context.context_hash,
                "receipts": receipts}

    def validate(self, envelope, **changes):
        options = {"at": AT, "verify_attestation": self.verify,
                   "supported_approval_profiles": (APPROVAL_PROFILE,),
                   "durable_receipts": {r["receiptId"]: r for r in envelope["receipts"]}, **changes}
        return validate_approval_envelope(envelope, self.graph(), **options)

    def value_proposal(self):
        return self.proposal | {"target": {"id": self.value, "entityType": "CiV"},
                               "operations": [{"op": "REPLACE", "path": "/selfCiV",
                                               "value": {"valueType": "STRING", "value": "Clearly explain decisions"}}]}

    def registered(self):
        return register_proposal(ApprovalWorkflow(), self.proposal,
                                 authenticated_requester_role_assignment_id=self.proposal["requestedByRoleAssignmentId"])

    def test_human_owner_approves_without_becoming_requester(self):
        envelope = self.envelope()
        proof = self.validate(envelope)
        self.assertEqual(proof.context.decision_key, RELEASE)
        self.assertEqual(proof.approved_by[0].source, self.proposal["requestId"])
        self.assertEqual(proof.approved_by[0].target, self.assignments[0])
        self.assertEqual(envelope["proposal"]["requestedByRoleAssignmentId"], self.assignments[1])
        self.assertEqual(set(proof.approved_by[0].properties), {"receiptId", "decidedAt", "requestHash", "approvalHash"})

    def test_requester_may_also_be_approver_without_invented_four_eyes_rule(self):
        proposal = self.proposal | {"requestedByRoleAssignmentId": self.assignments[0]}
        self.validate(self.envelope(proposal=proposal))

    def test_accountability_does_not_grant_permission(self):
        del self.nodes[self.rule]["approvalPolicy"]
        with self.assertRaises(ApprovalRequired):
            self.envelope()

    def test_escalation_stops_at_first_permitted_higher_level(self):
        self.nodes[self.rule]["approvalPolicy"].update(roleIds=[self.roles[1], self.roles[2]], levels=["PiF1t", "PiF1s"])
        envelope = self.envelope(indices=(1,))
        proof = self.validate(envelope)
        self.assertEqual([r.anchor_id for r in proof.context.requirements], [self.goals[1]])

    def test_two_branches_require_all_approvals_even_with_any_contribution_mode(self):
        second = self.node("tactical-second", "PiF1t", contributionMode="ANY")
        self.edge(second, "ACCOUNTABLE_MEMBER", self.members[2])
        self.edge(second, "CONTRIBUTES_TO", self.goals[2])
        self.edge(self.goals[0], "CONTRIBUTES_TO", second)
        self.nodes[self.rule]["approvalPolicy"].update(roleIds=[self.roles[1], self.roles[2]], levels=["PiF1t"])
        one = self.envelope(indices=(1,))
        with self.assertRaises(ApprovalRequired):
            self.validate(one)
        both = self.envelope(indices=(1, 2))
        self.assertEqual(len(self.validate(both).context.requirements), 2)

    def test_shared_ancestor_is_deduplicated(self):
        second = self.node("tactical-second", "PiF1t")
        self.edge(second, "ACCOUNTABLE_MEMBER", self.members[1])
        self.edge(second, "CONTRIBUTES_TO", self.goals[2])
        self.edge(self.goals[0], "CONTRIBUTES_TO", second)
        self.nodes[self.rule]["approvalPolicy"].update(roleIds=[self.roles[2]], levels=["PiF1s"])
        proof = self.validate(self.envelope(indices=(2,)))
        self.assertEqual(len(proof.context.requirements), 1)
        self.assertEqual(proof.context.requirements[0].anchor_id, self.goals[2])

    def test_missing_higher_accountability_is_not_invented(self):
        self.nodes[self.rule]["approvalPolicy"].update(roleIds=[self.roles[1]], levels=["PiF1t"])
        self.edges = [e for e in self.edges if not (e.source == self.goals[1] and e.relationship == "ACCOUNTABLE_MEMBER")]
        with self.assertRaises(ApprovalConflict):
            self.envelope(indices=(1,))

    def test_explicit_denial_cannot_be_escaped_by_climbing(self):
        self.nodes[self.rule]["effect"] = "PROHIBIT"
        self.nodes[self.rule]["priority"] = 100
        self.policy("higher-grant", RELEASE, "ACCOUNTABLE_CHAIN", [self.roles[1]], ["PiF1t"])
        with self.assertRaises(ApprovalDenied):
            self.envelope(indices=(1,))

    def test_priority_tie_is_not_approval(self):
        conflict = self.policy("denial", RELEASE, "ACCOUNTABLE_CHAIN", [self.roles[0]], ["PiF1o"])
        self.nodes[conflict]["effect"] = "PROHIBIT"
        with self.assertRaisesRegex(ApprovalConflict, "PRIORITY_TIE"):
            self.envelope()

    def test_unknown_condition_is_not_hidden_by_any(self):
        self.nodes[self.rule]["condition"] = {"combiner": "ANY", "clauses": [
            expression()["clauses"][0], {"path": "executingRole.roleName", "operator": "EQUALS", "value": "admin"}]}
        with self.assertRaisesRegex(ApprovalConflict, "UNEVALUABLE"):
            self.envelope()

    def test_pending_and_rejection_do_not_create_event_or_release(self):
        state = self.registered()
        self.assertFalse(state.accepted)
        context = make_approval_context(self.graph(), self.proposal, at=AT)
        rejected = self.receipt(context, outcome="REJECTED")
        state = record_approval_receipt(state, self.proposal["requestId"], rejected, self.graph(), at=AT, verify_attestation=self.verify)
        envelope = self.envelope()
        envelope["receipts"] = [rejected]
        with self.assertRaises(ApprovalDenied):
            accept_approved_request(state, GateState(), envelope, self.graph(), at=AT,
                                    verify_attestation=self.verify, supported_approval_profiles=(APPROVAL_PROFILE,))
        self.assertFalse(state.accepted)
        self.assertEqual(self.nodes[self.task]["status"], "DRAFT")

    def test_client_cannot_omit_durable_rejection(self):
        context = make_approval_context(self.graph(), self.proposal, at=AT)
        rejected = self.receipt(context, outcome="REJECTED")
        envelope = self.envelope()
        with self.assertRaises(ApprovalRequired):
            self.validate(envelope, durable_receipts={rejected["receiptId"]: rejected})

    def test_receipt_cannot_be_rewritten_from_no_to_yes(self):
        context = make_approval_context(self.graph(), self.proposal, at=AT)
        state = self.registered()
        state = record_approval_receipt(state, self.proposal["requestId"], self.receipt(context, outcome="REJECTED"),
                                       self.graph(), at=AT, verify_attestation=self.verify)
        with self.assertRaises(ApprovalConflict):
            record_approval_receipt(state, self.proposal["requestId"], self.receipt(context), self.graph(), at=AT, verify_attestation=self.verify)

    def test_technical_identity_cannot_supply_human_confirmation(self):
        envelope = self.envelope()
        self.nodes[self.members[0]]["memberType"] = "TECHNICAL"
        with self.assertRaises(RuleViolation):
            self.validate(envelope)

    def test_missing_or_forged_attestation_fails_closed(self):
        envelope = self.envelope()
        with self.assertRaises(ApprovalRequired):
            self.validate(envelope, verify_attestation=None)
        with self.assertRaises(ApprovalRequired):
            self.validate(envelope, verify_attestation=lambda _: True)
        envelope["receipts"][0]["attestation"] = "forged"
        with self.assertRaises(ApprovalRequired):
            self.validate(envelope)

    def test_authenticated_member_must_own_assignment(self):
        envelope = self.envelope()
        envelope["receipts"][0]["memberId"] = self.members[1]
        envelope["receipts"][0]["attestation"] = self.sign(envelope["receipts"][0])
        with self.assertRaises(ApprovalRequired):
            self.validate(envelope)

    def test_receipt_expires_at_exact_boundary(self):
        with self.assertRaises(ApprovalRequired):
            self.validate(self.envelope(), at=EXPIRES)

    def test_task_payload_requester_or_revision_change_invalidates_receipt(self):
        for field, value in (("reason", "different reason"), ("requestedByRoleAssignmentId", self.assignments[2]),
                             ("requestedRevision", 2), ("requestId", uid("another-request"))):
            envelope = self.envelope()
            envelope["proposal"][field] = value
            with self.subTest(field=field), self.assertRaises(RuleViolation):
                self.validate(envelope)

    def test_rule_actor_owner_and_graph_changes_invalidate_context(self):
        for identity, field, value in ((self.rule, "priority", 11), (self.roles[0], "roleName", "Renamed"),
                                        (self.task, "revision", 2), (self.team, "status", "REVOKED")):
            envelope = self.envelope()
            previous = self.nodes[identity][field]
            self.nodes[identity][field] = value
            with self.subTest(field=field), self.assertRaises(RuleViolation):
                self.validate(envelope)
            self.nodes[identity][field] = previous

    def test_duplicate_edges_are_not_hidden_by_distinct(self):
        self.edges.append(self.edges[0])
        with self.assertRaises(ApprovalConflict):
            self.envelope()

    def test_undeclared_profile_or_client_action_override_is_rejected(self):
        envelope = self.envelope()
        with self.assertRaises(ApprovalRequired):
            self.validate(envelope, supported_approval_profiles=())
        envelope["decisionKey"] = CONFIRM
        with self.assertRaises(ApprovalConflict):
            self.validate(envelope)

    def test_release_remains_blocked_by_dependency_and_does_not_complete(self):
        prerequisite = self.node("prerequisite", "Task", status="DRAFT", taskKind="ATOMIC")
        self.edge(self.goals[0], "DECOMPOSES_INTO", prerequisite)
        self.edge(prerequisite, "RESPONSIBLE_TEAM", self.team)
        self.edge(self.task, "DEPENDS_ON", prerequisite)
        tasks = {self.task: TaskRecord(self.task, self.goals[0], depends_on=(prerequisite,)),
                 prerequisite: TaskRecord(prerequisite, self.goals[0])}
        envelope = self.envelope()
        states = release_with_approval(
            envelope, self.graph(), tasks, at=AT, verify_attestation=self.verify,
            durable_receipts={r["receiptId"]: r for r in envelope["receipts"]},
            supported_approval_profiles=(APPROVAL_PROFILE,), validate_activation=lambda *_: True)
        self.assertEqual(states[self.task], "BLOCKED")
        self.assertEqual(states[prerequisite], "DRAFT")
        self.assertEqual(self.nodes[self.goals[0]]["status"], "ACTIVE")

    def test_approval_does_not_replace_executor_or_environment_validation(self):
        envelope = self.envelope()
        with self.assertRaises(ApprovalRequired):
            release_with_approval(envelope, self.graph(), {self.task: TaskRecord(self.task, self.goals[0])},
                                  at=AT, verify_attestation=self.verify,
                                  durable_receipts={r["receiptId"]: r for r in envelope["receipts"]},
                                  supported_approval_profiles=(APPROVAL_PROFILE,), validate_activation=lambda *_: False)

    def test_task_projection_cannot_hide_signed_dependencies_or_change_goal(self):
        prerequisite = self.node("prerequisite", "Task", status="DRAFT", taskKind="ATOMIC")
        self.edge(self.goals[0], "DECOMPOSES_INTO", prerequisite)
        self.edge(prerequisite, "RESPONSIBLE_TEAM", self.team)
        self.edge(self.task, "DEPENDS_ON", prerequisite)
        envelope = self.envelope()
        kwargs = {"at": AT, "verify_attestation": self.verify,
                  "durable_receipts": {r["receiptId"]: r for r in envelope["receipts"]},
                  "supported_approval_profiles": (APPROVAL_PROFILE,), "validate_activation": lambda *_: True}
        correct = {self.task: TaskRecord(self.task, self.goals[0], depends_on=(prerequisite,)),
                   prerequisite: TaskRecord(prerequisite, self.goals[0])}
        for wrong in (
            {self.task: correct[self.task]},
            correct | {self.task: replace(correct[self.task], depends_on=())},
            correct | {self.task: replace(correct[self.task], pif1o=self.goals[1])},
            correct | {self.task: replace(correct[self.task], kind="COMPOSITE")},
        ):
            with self.assertRaises(ApprovalConflict):
                release_with_approval(envelope, self.graph(), wrong, **kwargs)
        received = []
        kwargs["validate_activation"] = lambda graph, *_: received.append(graph.entities[self.task]["status"]) or True
        release_with_approval(envelope, self.graph(), correct, **kwargs)
        self.assertEqual(received, ["BLOCKED"])

    def test_future_dated_rule_cannot_retroactively_authorize_receipt(self):
        self.nodes[self.rule]["validFrom"] = "2026-09-08T09:45:00Z"
        envelope = self.envelope()
        with self.assertRaises(RuleViolation):
            self.validate(envelope)  # signed at 09:30, rule only starts at 09:45

    def test_receipt_requires_membership_and_assignment_valid_at_both_times(self):
        envelope = self.envelope()
        self.nodes[self.assignments[0]]["validFrom"] = "2026-09-08T09:45:00Z"
        changed = self.envelope()
        with self.assertRaises(ApprovalRequired):
            self.validate(changed)
        self.nodes[self.assignments[0]]["validFrom"] = START
        membership = next(e for e in self.edges if e.relationship == "HAS_MEMBER" and e.target == self.members[0])
        self.edges.remove(membership)
        with self.assertRaises(ApprovalConflict):
            self.validate(envelope)

    def test_requester_needs_authenticated_identity_and_valid_assignment(self):
        with self.assertRaises(ApprovalRequired):
            register_proposal(ApprovalWorkflow(), self.proposal,
                              authenticated_requester_role_assignment_id=self.assignments[0])
        self.nodes[self.members[1]]["memberType"] = "TECHNICAL"
        self.validate(self.envelope())  # technical requester, human approver
        self.nodes[self.assignments[1]]["status"] = "REVOKED"
        with self.assertRaises(ApprovalRequired):
            self.envelope()

    def test_duplicate_receipts_and_unrecorded_payloads_are_rejected(self):
        envelope = self.envelope()
        envelope["receipts"].append(deepcopy(envelope["receipts"][0]))
        with self.assertRaises(ApprovalConflict):
            self.validate(envelope)
        with self.assertRaises(ApprovalRequired):
            self.validate(self.envelope(), durable_receipts={})

    def test_value_confirmation_uses_authorized_human_in_holder_scope(self):
        proof = self.validate(self.envelope(proposal=self.value_proposal()))
        self.assertEqual(proof.context.decision_key, CONFIRM)
        self.assertEqual(proof.context.requirements[0].anchor_id, self.org)

    def test_inverse_sensitive_edge_cannot_evade_confirmation(self):
        value2 = self.node("value2", "CiV", notCiV="No confusion", selfCiV="Clear", toServeCiV="Clients")
        self.edge(value2, "HELD_BY", self.org)
        proposal = self.proposal | {"target": {"id": self.goals[-1], "entityType": "PiF2"},
                                   "operations": [{"op": "CONNECT", "direction": "INCOMING",
                                                   "relationshipType": "INSCRIBES_PURPOSE_IN", "otherEntityId": value2}]}
        self.assertEqual(self.validate(self.envelope(proposal=proposal)).context.decision_key, CONFIRM)

    def test_value_holder_change_requires_old_and_new_scope_approvals(self):
        other_org = self.node("other-org", "RoFOrg")
        other_team = self.node("other-team", "RoFTeam", validFrom=START)
        self.edge(other_org, "HAS_TEAM", other_team)
        member, role, assignment = self.actor("other", other_team)
        self.members.append(member)
        self.roles.append(role)
        self.assignments.append(assignment)
        other_value = self.node("other-value", "CiV", notCiV="No opacity", selfCiV="Clear", toServeCiV="People")
        other_future = self.node("other-future", "PiF2", targetState="Trusted other organisation")
        self.edge(other_value, "HELD_BY", other_org)
        self.edge(other_value, "INSCRIBES_PURPOSE_IN", other_future)
        other_policy = self.policy("other-value-policy", CONFIRM, "VALUE_SCOPE", [role])
        self.edges = [e for e in self.edges if not (e.source == other_policy and e.relationship in {"PROTECTS", "GOVERNS"})]
        self.edge(other_policy, "PROTECTS", other_value)
        self.edge(other_policy, "PROTECTS", other_future)
        self.edge(other_policy, "GOVERNS", assignment)
        proposal = self.value_proposal() | {"operations": [
            {"op": "DISCONNECT", "relationshipType": "HELD_BY", "direction": "OUTGOING", "otherEntityId": self.org},
            {"op": "CONNECT", "relationshipType": "HELD_BY", "direction": "OUTGOING", "otherEntityId": other_org}]}
        with self.assertRaises(ApprovalRequired):
            self.validate(self.envelope(proposal=proposal))
        proof = self.validate(self.envelope(proposal=proposal, indices=(0, 4)))
        self.assertEqual({r.anchor_id for r in proof.context.requirements}, {self.org, other_org})

    def test_global_value_grant_and_enrollment_latch_have_same_explicit_holder_scope(self):
        team_value = self.node("team-value", "CiV", notCiV="No confusion", selfCiV="Clear", toServeCiV="Team")
        team_future = self.node("team-future", "PiF2", targetState="Reliable team")
        self.edge(team_value, "HELD_BY", self.team)
        self.edge(team_value, "INSCRIBES_PURPOSE_IN", team_future)
        proposal = self.value_proposal() | {"target": {"id": team_value, "entityType": "CiV"}}
        # The same HUMAN and role are in this team, but the existing GLOBAL
        # policy explicitly protects the ORGANIZATION holder, not this holder.
        with self.assertRaises(ApprovalRequired):
            self.envelope(proposal=proposal)
        latched = enrollment_latches(self.graph())
        self.assertIn(self.org, latched)
        self.assertNotIn(self.team, latched)
        initial = (EnrollmentAuthority(self.members[0], self.assignments[0], self.team),)
        envelope = self.envelope(proposal=proposal, enrollment_authorities=initial)
        self.validate(envelope, enrollment_authorities=initial)

        team_policy = self.policy("team-value-policy", CONFIRM, "VALUE_SCOPE", [self.roles[0]])
        self.edges = [e for e in self.edges if not (e.source == team_policy and e.relationship == "PROTECTS")]
        self.edge(team_policy, "PROTECTS", team_value)
        self.edge(team_policy, "PROTECTS", team_future)
        self.validate(self.envelope(proposal=proposal))
        latched = enrollment_latches(self.graph(), latched)
        self.assertIn(self.team, latched)
        self.nodes[team_policy]["status"] = "REVOKED"
        with self.assertRaises(ApprovalRequired):
            self.envelope(proposal=proposal, enrollment_authorities=initial,
                          disabled_enrollment_holders=latched)

    def test_unmatched_value_grant_scope_does_not_waive_applicable_denial(self):
        team_value = self.node("team-value", "CiV", notCiV="No confusion", selfCiV="Clear", toServeCiV="Team")
        self.edge(team_value, "HELD_BY", self.team)
        self.nodes[self.value_rule]["effect"] = "PROHIBIT"
        proposal = self.value_proposal() | {"target": {"id": team_value, "entityType": "CiV"}}
        initial = (EnrollmentAuthority(self.members[0], self.assignments[0], self.team),)
        with self.assertRaises(ApprovalDenied):
            self.envelope(proposal=proposal, enrollment_authorities=initial)

    def test_new_authority_policy_cannot_authorize_its_own_change(self):
        self.nodes[self.value_rule]["approvalPolicy"]["roleIds"] = [self.roles[1]]
        new_policy = self.nodes[self.value_rule]["approvalPolicy"] | {"roleIds": [self.roles[0]]}
        proposal = self.proposal | {"target": {"id": self.value_rule, "entityType": "RaN"},
                                   "operations": [{"op": "REPLACE", "path": "/approvalPolicy",
                                                   "value": {"valueType": "OBJECT", "value": new_policy}}]}
        envelope = self.envelope(proposal=proposal, indices=(0,))
        with self.assertRaises(ApprovalRequired):
            self.validate(envelope)
        self.validate(self.envelope(proposal=proposal, indices=(1,)))

    def test_accountability_change_requires_prior_value_scope_authority(self):
        proposal = self.proposal | {"target": {"id": self.goals[0], "entityType": "PiF1o"}, "operations": [
            {"op": "DISCONNECT", "direction": "OUTGOING", "relationshipType": "ACCOUNTABLE_MEMBER", "otherEntityId": self.members[0]},
            {"op": "CONNECT", "direction": "OUTGOING", "relationshipType": "ACCOUNTABLE_MEMBER", "otherEntityId": self.members[1]}]}
        self.assertEqual(self.validate(self.envelope(proposal=proposal)).context.decision_key, CONFIRM)

    def test_initial_enrollment_has_no_automatic_root_fallback(self):
        self.nodes[self.value_rule]["status"] = "DRAFT"
        proposal = self.value_proposal()
        with self.assertRaises(ApprovalRequired):
            self.envelope(proposal=proposal)
        config = (EnrollmentAuthority(self.members[0], self.assignments[0], self.org),)
        envelope = self.envelope(proposal=proposal, enrollment_authorities=config)
        self.validate(envelope, enrollment_authorities=config)
        self.nodes[self.rule]["status"] = "DRAFT"
        with self.assertRaises(ApprovalRequired):
            self.envelope(enrollment_authorities=config)

    def test_enrollment_latch_is_permanent_after_policy_revocation(self):
        disabled = enrollment_latches(self.graph())
        self.assertIn(self.org, disabled)
        self.nodes[self.value_rule]["status"] = "REVOKED"
        self.assertEqual(enrollment_latches(self.graph(), disabled), disabled)
        config = (EnrollmentAuthority(self.members[0], self.assignments[0], self.org),)
        with self.assertRaises(ApprovalRequired):
            self.envelope(proposal=self.value_proposal(), enrollment_authorities=config, disabled_enrollment_holders=disabled)

    def test_first_policy_activation_commit_persists_enrollment_shutdown(self):
        self.nodes[self.value_rule]["status"] = "DRAFT"
        config = (EnrollmentAuthority(self.members[0], self.assignments[0], self.org),)
        proposal = self.proposal | {"target": {"id": self.value_rule, "entityType": "RaN"}}
        envelope = self.envelope(proposal=proposal, enrollment_authorities=config)
        state = register_proposal(ApprovalWorkflow(), proposal,
                                  authenticated_requester_role_assignment_id=proposal["requestedByRoleAssignmentId"])
        state = record_approval_receipt(state, proposal["requestId"], envelope["receipts"][0], self.graph(),
                                       at=AT, verify_attestation=self.verify, enrollment_authorities=config)
        state, gate, _ = accept_approved_request(
            state, GateState(), envelope, self.graph(), at=AT, verify_attestation=self.verify,
            supported_approval_profiles=(APPROVAL_PROFILE,), enrollment_authorities=config)
        gate = acquire_gate(gate, uid("activation-run"))
        state, _ = commit_approved_request(
            state, gate, self.graph(), proposal_id=proposal["requestId"], run_id=uid("activation-run"),
            fence=gate.fence, expected_epoch=gate.epoch, decision_at=AT, verify_attestation=self.verify,
            supported_approval_profiles=(APPROVAL_PROFILE,), enrollment_authorities=config,
            validate_candidate=lambda *_: True)
        self.assertIn(self.org, state.disabled_enrollment_holders)
        self.nodes[self.value_rule]["status"] = "REVOKED"
        with self.assertRaises(ApprovalRequired):
            self.envelope(proposal=self.value_proposal(), enrollment_authorities=config,
                          disabled_enrollment_holders=state.disabled_enrollment_holders)

    def test_generic_approval_edge_and_mixed_release_changes_are_rejected(self):
        for operation in (
            {"op": "CONNECT", "relationshipType": "APPROVED_BY", "direction": "OUTGOING", "otherEntityId": self.assignments[0]},
            {"op": "REPLACE", "path": "/name", "value": {"valueType": "STRING", "value": "Another task"}},
        ):
            proposal = self.proposal | {"operations": self.proposal["operations"] + [operation]}
            with self.assertRaises(ApprovalConflict):
                self.envelope(proposal=proposal)

    def test_acceptance_then_gate_revalidation_preserves_atomicity_and_idempotency(self):
        envelope = self.envelope()
        state = self.registered()
        state = record_approval_receipt(state, self.proposal["requestId"], envelope["receipts"][0],
                                       self.graph(), at=AT, verify_attestation=self.verify)
        state, gate, proof = accept_approved_request(
            state, GateState(), envelope, self.graph(), at=AT, verify_attestation=self.verify,
            supported_approval_profiles=(APPROVAL_PROFILE,))
        self.assertEqual(proof.approved_by[0].target, self.assignments[0])
        gate = acquire_gate(gate, uid("run"))
        state, committed = commit_approved_request(
            state, gate, self.graph(), proposal_id=self.proposal["requestId"], run_id=uid("run"),
            fence=gate.fence, expected_epoch=gate.epoch, decision_at=AT, verify_attestation=self.verify,
            supported_approval_profiles=(APPROVAL_PROFILE,), validate_candidate=lambda *_: True)
        self.assertIn(self.proposal["idempotencyKey"], committed.successes)
        self.nodes[self.task]["revision"] = 2
        self.nodes[self.task]["status"] = "ACTIVE"
        recovered_state, recovered_gate = commit_approved_request(
            state, committed, self.graph(), proposal_id=self.proposal["requestId"],
            run_id=uid("run"), fence=gate.fence, expected_epoch=committed.epoch,
            decision_at=EXPIRES, verify_attestation=self.verify,
            supported_approval_profiles=(APPROVAL_PROFILE,), validate_candidate=lambda *_: False)
        self.assertEqual(recovered_state, state)
        self.assertEqual(recovered_gate, committed)
        self.assertEqual(accept_approved_request(
            state, committed, envelope, self.graph(), at=EXPIRES, verify_attestation=self.verify,
            supported_approval_profiles=(APPROVAL_PROFILE,)), (state, committed, proof))
        tampered = deepcopy(envelope)
        tampered["receipts"][0]["attestation"] = "changed"
        with self.assertRaises(ApprovalConflict):
            accept_approved_request(state, committed, tampered, self.graph(), at=EXPIRES,
                                    verify_attestation=self.verify, supported_approval_profiles=(APPROVAL_PROFILE,))

    def test_changed_rule_between_acceptance_and_commit_prevents_success(self):
        envelope = self.envelope()
        state = self.registered()
        state = record_approval_receipt(state, self.proposal["requestId"], envelope["receipts"][0],
                                       self.graph(), at=AT, verify_attestation=self.verify)
        state, gate, _ = accept_approved_request(
            state, GateState(), envelope, self.graph(), at=AT, verify_attestation=self.verify,
            supported_approval_profiles=(APPROVAL_PROFILE,))
        gate = acquire_gate(gate, uid("run"))
        self.nodes[self.rule]["priority"] += 1
        with self.assertRaises(ApprovalConflict):
            commit_approved_request(state, gate, self.graph(), proposal_id=self.proposal["requestId"],
                                     run_id=uid("run"), fence=gate.fence, expected_epoch=gate.epoch,
                                     decision_at=AT, verify_attestation=self.verify,
                                     supported_approval_profiles=(APPROVAL_PROFILE,), validate_candidate=lambda *_: True)
        self.assertFalse(gate.successes)

    def test_scalar_grammar_distinguishes_absence_null_and_types(self):
        run = lambda expr, target: evaluate_approval_condition(expr, target=target, actor={}, request={})
        self.assertTrue(run(expression("target.x", "EXISTS"), {"x": None}))
        self.assertTrue(run(expression("target.x", "NOT_EXISTS"), {}))
        self.assertFalse(run(expression("target.x", "EQUALS", 1), {"x": True}))
        self.assertTrue(run(expression("target.x", "LESS_THAN", 2), {"x": 1}))
        for expr, target in ((expression("target.x", "EQUALS", None), {}),
                             (expression("target.x", "LESS_THAN", "2"), {"x": "1"}),
                             (expression("target.x", "MATCHES", ".*"), {"x": "text"}),
                             (expression("target.x.y", "EXISTS"), {"x": {"y": 1}})):
            with self.assertRaises(ApprovalConflict):
                run(expr, target)

    def test_approval_policy_role_and_level_operands_are_explicit(self):
        valid = deepcopy(self.nodes[self.rule]["approvalPolicy"])
        validate_approval_policy(valid)
        for change in ({"roleIds": []}, {"roleIds": ["Administrator"]}, {"levels": []},
                       {"levels": ["PiF1o", "PiF1o"]}, {"profileVersion": "unknown"}, {"mode": "AUTOMATIC"}):
            with self.assertRaises(ApprovalConflict):
                validate_approval_policy(valid | change)

    def test_approval_audit_edges_never_revise_existing_roles(self):
        self.assertEqual(revision_owners("ChangeEvent", "APPROVED_BY", "RoleAssignment"), frozenset({"source"}))
        self.assertEqual(revision_owners("PiF2", "ACCOUNTABLE_MEMBER", "RoFTeamMember"), frozenset({"source", "target"}))
        event = uid("event")
        entities = {event: {"entityType": "ChangeEvent", "status": "RECORDED", "revision": 1},
                    self.assignments[0]: self.nodes[self.assignments[0]]}
        from reference.jci_rules import RelationshipChange
        plan = revision_plan(entities, [RelationshipChange(event, "APPROVED_BY", self.assignments[0])], new_ids=(event,))
        self.assertEqual(plan, {event: 1})
        with self.assertRaises(RuleViolation):
            revision_plan(entities, [RelationshipChange(event, "APPROVED_BY", self.assignments[0])])

    def test_legacy_boolean_primitive_no_longer_defaults_to_confirmed(self):
        self.assertFalse(valid_ran_protection(status="ACTIVE", protected_civ_ids=[self.value],
                                              protected_pif2_ids=[self.goals[-1]],
                                              inscriptions={(self.value, self.goals[-1])}, governed_types=["Task"]))


if __name__ == "__main__":
    unittest.main()
