"""Fail-closed reference for the explicit JCI approval profile 1.0.

This is a pure protocol/model reference, not an authentication service, database
or complete SYNC engine. The caller supplies a complete authoritative domain
graph, a trusted attestation verifier, and durable storage for the workflow.
The existing low-level jci_rules helpers do not grant approval authority.
"""

from copy import deepcopy
from dataclasses import dataclass, field, replace
from datetime import datetime
import hashlib
import re
from typing import Callable, Mapping
from uuid import UUID

from .jci_rules import (
    GateState, RuleViolation, TaskRecord, accept_request, canonical_json,
    derive_task_states, gate_commit, parse_pointer, ran_decision,
    revision_owners, validate_typed_value,
)


APPROVAL_PROFILE = "1.0"
RELEASE = "Task.action.RELEASE"
CONFIRM = "Model.action.CONFIRM"
FUTURE_TYPES = ("PiF1o", "PiF1t", "PiF1s", "PiF2")
NEXT_FUTURE = dict(zip(FUTURE_TYPES, FUTURE_TYPES[1:]))
SENSITIVE_RELATIONS = frozenset({
    "HELD_BY", "INFORMED_BY", "INSCRIBES_PURPOSE_IN", "PROTECTS",
    "ACCOUNTABLE_MEMBER",
})
AUDIT_RELATIONS = frozenset({
    "CREATED_BY", "REQUESTED_BY", "APPROVED_BY", "CHANGED_BY", "TRIGGERS",
    "HAS_HISTORICAL_STATE", "EXECUTES", "AFFECTS", "CREATES_HISTORY",
    "CREATES_CORRECTION", "TARGETS_HISTORY", "CORRECTS", "CAUSED_BY",
    "CORRECTED_BY", "DETECTED_BY", "RESOLVED_BY", "RESOLVED_THROUGH",
    "CONFLICTING_RULE",
})
PROCESS_TYPES = frozenset({
    "PiH", "ChangeEvent", "SyncEvent", "HistoricalCorrection", "RaNConflict",
})


class ApprovalConflict(RuleViolation):
    """Approval semantics, graph or proof cannot be evaluated safely."""


class ApprovalDenied(RuleViolation):
    """An explicit refusal must not be bypassed by escalation."""


class ApprovalRequired(RuleViolation):
    """No complete, currently authorized human approval exists."""


@dataclass(frozen=True)
class ApprovalEdge:
    source: str
    relationship: str
    target: str
    properties: Mapping = field(default_factory=dict)


@dataclass(frozen=True)
class ApprovalGraph:
    entities: Mapping[str, Mapping]
    edges: tuple[ApprovalEdge, ...] = ()


@dataclass(frozen=True)
class EnrollmentAuthority:
    """Trusted installation configuration, never a request-supplied grant."""
    member_id: str
    role_assignment_id: str
    holder_id: str


@dataclass(frozen=True)
class ApprovalRequirement:
    anchor_id: str
    mode: str
    candidate_role_assignment_ids: tuple[str, ...]


@dataclass(frozen=True)
class ApprovalContext:
    decision_key: str
    request_hash: str
    context_hash: str
    requirements: tuple[ApprovalRequirement, ...]


@dataclass(frozen=True)
class ValidatedApproval:
    context: ApprovalContext
    approved_by: tuple[ApprovalEdge, ...]


def _hash(value):
    return hashlib.sha256(canonical_json(value)).hexdigest()


def _time(value):
    if isinstance(value, datetime):
        parsed = value
    elif isinstance(value, str):
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            raise ApprovalConflict("invalid timestamp") from None
    else:
        raise ApprovalConflict("missing timestamp")
    if parsed.tzinfo is None:
        raise ApprovalConflict("timestamp must include a timezone")
    return parsed


def _uuid(value):
    try:
        return isinstance(value, str) and str(UUID(value)) == value
    except (ValueError, AttributeError, TypeError):
        return False


def _interval(properties, at, *, required=True):
    start = properties.get("validFrom")
    if start is None:
        if required:
            raise ApprovalConflict("missing validity start")
        return True
    start = _time(start)
    end = _time(properties["validUntil"]) if properties.get("validUntil") else None
    if end is not None and end < start:
        raise ApprovalConflict("reversed validity interval")
    return start <= at and (end is None or at < end)


def _entity(graph, identity, kind=None):
    node = graph.entities.get(identity)
    if node is None or (kind and node.get("entityType") != kind):
        raise ApprovalConflict("unresolved or wrong-type graph endpoint")
    return node


def _out(graph, source, relationship):
    return [edge for edge in graph.edges
            if edge.source == source and edge.relationship == relationship]


def _in(graph, target, relationship):
    return [edge for edge in graph.edges
            if edge.target == target and edge.relationship == relationship]


def _one(items, label):
    if len(items) != 1:
        raise ApprovalConflict(f"expected exactly one {label}")
    return items[0]


def _check_graph(graph):
    keys = set()
    for edge in graph.edges:
        key = edge.source, edge.relationship, edge.target
        if key in keys:
            raise ApprovalConflict("parallel duplicate relationship")
        keys.add(key)
        source = _entity(graph, edge.source)
        target = _entity(graph, edge.target)
        revision_owners(source.get("entityType"), edge.relationship, target.get("entityType"))


def _domain_projection(graph):
    """Conservative complete supplied domain view; audit appends do not stale it."""
    entities = {identity: deepcopy(node) for identity, node in graph.entities.items()
                if node.get("entityType") not in PROCESS_TYPES}
    edges = [{"source": e.source, "relationship": e.relationship, "target": e.target,
              "properties": deepcopy(dict(e.properties))}
             for e in graph.edges if e.relationship not in AUDIT_RELATIONS
             and e.source in entities and e.target in entities]
    edges.sort(key=lambda e: (e["source"], e["relationship"], e["target"]))
    return {"entities": entities, "edges": edges}


def _actor(graph, assignment_id, at, *, human_required=True):
    assignment = _entity(graph, assignment_id, "RoleAssignment")
    if assignment.get("status") != "ACTIVE":
        raise ApprovalRequired("approval assignment is not active")
    member_id = _one(_in(graph, assignment_id, "HAS_ASSIGNMENT"), "assignment member").source
    team_id = _one(_out(graph, assignment_id, "IN_TEAM"), "assignment team").target
    role_id = _one(_out(graph, assignment_id, "ACTIVATES_ROLE"), "activated role").target
    organization_id = _one(_in(graph, team_id, "HAS_TEAM"), "team organization").source
    member = _entity(graph, member_id, "RoFTeamMember")
    team = _entity(graph, team_id, "RoFTeam")
    role = _entity(graph, role_id, "RoFRole")
    organization = _entity(graph, organization_id, "RoFOrg")
    if member.get("memberType") not in {"HUMAN", "TECHNICAL"}:
        raise ApprovalConflict("unknown member identity type")
    if human_required and member.get("memberType") != "HUMAN":
        raise ApprovalRequired("a technical member cannot give human approval")
    if any(n.get("status") != "ACTIVE" for n in (assignment, member, team, role, organization)):
        raise ApprovalRequired("approval actor context is not active")
    if not _interval(assignment, at) or not _interval(team, at):
        raise ApprovalRequired("approval actor context has expired")
    membership = _one([e for e in _out(graph, team_id, "HAS_MEMBER")
                       if e.target == member_id], "valid team membership")
    ownership = _one([e for e in _out(graph, member_id, "HAS_ROLE")
                      if e.target == role_id], "role ownership")
    for edge in (membership, ownership):
        if not _interval(edge.properties, at):
            raise ApprovalRequired("membership or role ownership has expired")
        if _time(assignment["validFrom"]) < _time(edge.properties["validFrom"]):
            raise ApprovalConflict("assignment starts outside its membership/role interval")
        if edge.properties.get("validUntil"):
            if not assignment.get("validUntil") or _time(assignment["validUntil"]) > _time(edge.properties["validUntil"]):
                raise ApprovalConflict("assignment ends outside its membership/role interval")
    return {"id": assignment_id, "entityType": "RoleAssignment", "status": "ACTIVE",
            "memberId": member_id, "memberType": member["memberType"], "roleId": role_id,
            "roleName": role.get("roleName"), "teamId": team_id,
            "organizationId": organization_id}


def _scalar(value):
    return value is None or type(value) in {bool, int, str}


def evaluate_approval_condition(expression, *, target, actor, request):
    """Finite scalar profile: root.property; no implicit relationship traversal.

    All clauses are evaluated, even under ANY. Missing is not NULL; comparisons
    with a missing property are UNEVALUABLE. Equality is type-strict. Ordering
    accepts integers only; CONTAINS accepts strings; MATCHES is unsupported.
    """
    if (not isinstance(expression, Mapping) or set(expression) != {"combiner", "clauses"}
            or expression["combiner"] not in {"ALL", "ANY"}
            or not isinstance(expression["clauses"], list) or not expression["clauses"]):
        raise ApprovalConflict("UNEVALUABLE approval expression")
    values = []
    roots = {"target": target, "actor": actor, "request": request}
    for clause in expression["clauses"]:
        if not isinstance(clause, Mapping) or not {"path", "operator"} <= clause.keys():
            raise ApprovalConflict("UNEVALUABLE approval clause")
        operator = clause["operator"]
        existence = operator in {"EXISTS", "NOT_EXISTS"}
        if set(clause) != ({"path", "operator"} if existence else {"path", "operator", "value"}):
            raise ApprovalConflict("UNEVALUABLE approval clause fields")
        path = clause["path"]
        if not isinstance(path, str) or not re.fullmatch(r"(target|actor|request)\.[A-Za-z][A-Za-z0-9]*", path):
            raise ApprovalConflict("UNEVALUABLE approval path")
        root, prop = path.split(".")
        present = prop in roots[root]
        if existence:
            values.append(present if operator == "EXISTS" else not present)
            continue
        if not present or not _scalar(roots[root][prop]):
            raise ApprovalConflict("UNEVALUABLE missing or non-scalar operand")
        left, right = roots[root][prop], clause["value"]
        equal = lambda a, b: type(a) is type(b) and a == b
        if operator in {"EQUALS", "NOT_EQUALS"}:
            if not _scalar(right):
                raise ApprovalConflict("UNEVALUABLE non-scalar comparison")
            value = equal(left, right)
            values.append(value if operator == "EQUALS" else not value)
        elif operator in {"IN", "NOT_IN"}:
            if not isinstance(right, list) or not all(_scalar(v) for v in right):
                raise ApprovalConflict("UNEVALUABLE membership values")
            value = any(equal(left, v) for v in right)
            values.append(value if operator == "IN" else not value)
        elif operator in {"LESS_THAN", "LESS_OR_EQUAL", "GREATER_THAN", "GREATER_OR_EQUAL"}:
            if type(left) is not int or type(right) is not int:
                raise ApprovalConflict("UNEVALUABLE non-integer ordering")
            values.append({"LESS_THAN": left < right, "LESS_OR_EQUAL": left <= right,
                           "GREATER_THAN": left > right, "GREATER_OR_EQUAL": left >= right}[operator])
        elif operator == "CONTAINS" and isinstance(left, str) and isinstance(right, str):
            values.append(right in left)
        else:
            raise ApprovalConflict("UNEVALUABLE unsupported approval operator/type")
    return all(values) if expression["combiner"] == "ALL" else any(values)


def validate_approval_policy(policy):
    if not isinstance(policy, Mapping) or not {"profileVersion", "mode", "roleIds"} <= policy.keys():
        raise ApprovalConflict("invalid approval policy")
    if set(policy) - {"profileVersion", "mode", "roleIds", "levels"}:
        raise ApprovalConflict("unknown approval policy fields")
    if policy["profileVersion"] != APPROVAL_PROFILE or policy["mode"] not in {"ACCOUNTABLE_CHAIN", "VALUE_SCOPE"}:
        raise ApprovalConflict("unsupported approval policy profile/mode")
    roles, levels = policy["roleIds"], policy.get("levels", [])
    if not isinstance(roles, list) or not roles or not all(_uuid(r) for r in roles) or len(set(roles)) != len(roles):
        raise ApprovalConflict("invalid approval role operands")
    if not isinstance(levels, list) or len(set(levels)) != len(levels) or set(levels) - set(FUTURE_TYPES):
        raise ApprovalConflict("invalid accountable levels")
    if (policy["mode"] == "ACCOUNTABLE_CHAIN") != bool(levels):
        raise ApprovalConflict("chain requires levels; value scope forbids levels")


def _holder_contains(graph, holder_id, actor, at):
    holder = _entity(graph, holder_id)
    if holder.get("status") != "ACTIVE":
        return False
    kind = holder.get("entityType")
    if kind == "RoFOrg":
        return actor["organizationId"] == holder_id
    if kind == "RoFTeam":
        return actor["teamId"] == holder_id
    if kind == "RoFTeamMember":
        return holder.get("memberType") == "HUMAN" and actor["memberId"] == holder_id
    raise ApprovalConflict("invalid value holder")


def _task_org(graph, task_id):
    team = _one(_out(graph, task_id, "RESPONSIBLE_TEAM"), "responsible team").target
    org = _one(_in(graph, team, "HAS_TEAM"), "responsible organization").source
    return team, org


def _rule_applies(graph, rule_id, rule, target_id, target, actor):
    types = rule.get("governedTypes")
    if not isinstance(types, list) or not types:
        raise ApprovalConflict("UNEVALUABLE governed types")
    if target.get("entityType") not in types:
        return False
    scope = rule.get("scopeType")
    applies = _out(graph, rule_id, "APPLIES_IN")
    if scope in {"GLOBAL", "ENTITY"}:
        if applies:
            raise ApprovalConflict("invalid unscoped rule")
        return scope == "GLOBAL" or any(e.target == target_id for e in _out(graph, rule_id, "GOVERNS"))
    scope_id = _one(applies, "rule scope").target
    if target.get("entityType") == "Task":
        team_id, org_id = _task_org(graph, target_id)
    elif target.get("entityType") == "RoleAssignment":
        team_id, org_id = actor["teamId"], actor["organizationId"]
    else:
        raise ApprovalConflict("unsupported approval target scope")
    if scope == "TEAM":
        _entity(graph, scope_id, "RoFTeam")
        return scope_id == team_id
    if scope == "ORGANIZATION":
        _entity(graph, scope_id, "RoFOrg")
        return scope_id == org_id
    raise ApprovalConflict("UNEVALUABLE rule scope")


def _permission(graph, proposal, actor, *, mode, level, at, target_id, target, decision_key,
                holder_id=None):
    decisions = []
    authority = False
    for identity, rule in sorted(graph.entities.items()):
        if rule.get("entityType") != "RaN" or rule.get("status") != "ACTIVE" or rule.get("decisionKey") != decision_key:
            continue
        if not _interval(rule, at):
            continue
        if not _rule_applies(graph, identity, rule, target_id, target, actor):
            continue
        policy = rule.get("approvalPolicy")
        eligible = False
        if policy is not None:
            validate_approval_policy(policy)
            eligible = (policy["mode"] == mode and actor["roleId"] in policy["roleIds"]
                        and (mode == "VALUE_SCOPE" or level in policy["levels"]))
            if mode == "VALUE_SCOPE":
                # GLOBAL widens applicability, not the explicitly protected
                # value-holder mandate. Use the SAME set as the durable latch.
                eligible = eligible and holder_id in _policy_holders(graph, identity)
            if rule.get("effect") == "PERMIT" and not eligible:
                continue
        if type(rule.get("priority")) is not int:
            raise ApprovalConflict("UNEVALUABLE rule priority")
        condition = evaluate_approval_condition(rule.get("condition"), target=target, actor=actor, request=proposal)
        if rule.get("effect") not in {"REQUIRE", "PROHIBIT", "PERMIT"}:
            raise ApprovalConflict("UNEVALUABLE rule effect")
        decision = ran_decision(rule["effect"], condition)
        if decision != "NO_DECISION":
            decisions.append((rule["priority"], decision))
        authority |= eligible and rule["effect"] == "PERMIT" and condition
    allows = any(d == "ALLOW" for _, d in decisions)
    denies = any(d == "DENY" for _, d in decisions)
    if allows and denies:
        highest = max(priority for priority, _ in decisions)
        top = {decision for priority, decision in decisions if priority == highest}
        if len(top) > 1:
            raise ApprovalConflict("PRIORITY_TIE in approval decision")
        denies = "DENY" in top
    if denies:
        raise ApprovalDenied("explicit RaN denial cannot be bypassed by escalation")
    return authority


def _apply_proposal(graph, proposal):
    """Small single-target candidate builder; unsupported operations fail closed."""
    required = {"schemaVersion", "requestId", "idempotencyKey", "requestedAt", "requestedRevision",
                "changeType", "target", "requestedByRoleAssignmentId", "reason", "operations"}
    if not isinstance(proposal, Mapping) or set(proposal) != required or proposal.get("schemaVersion") != "2.0":
        raise ApprovalConflict("approval profile requires a complete base 2.0 operation request")
    if (not _uuid(proposal["requestId"]) or not _uuid(proposal["requestedByRoleAssignmentId"])
            or not isinstance(proposal["idempotencyKey"], str) or not proposal["idempotencyKey"]
            or not isinstance(proposal["reason"], str) or not proposal["reason"].strip()):
        raise ApprovalConflict("invalid request identity/reason")
    _time(proposal["requestedAt"])
    target = proposal["target"]
    if not isinstance(target, Mapping) or set(target) != {"id", "entityType"} or not _uuid(target["id"]):
        raise ApprovalConflict("invalid target")
    identity = target["id"]
    entities, edges = deepcopy(dict(graph.entities)), list(deepcopy(graph.edges))
    if proposal["changeType"] == "CREATED":
        if identity in entities or proposal["requestedRevision"] is not None:
            raise ApprovalConflict("creation target occupied or revision not null")
        entities[identity] = {"id": identity, "entityType": target["entityType"], "revision": 1}
    else:
        before = _entity(graph, identity, target["entityType"])
        if type(proposal["requestedRevision"]) is not int or proposal["requestedRevision"] != before.get("revision"):
            raise ApprovalConflict("stale requested revision")
        if before.get("status") in {"ACHIEVED", "COMPLETED", "RECORDED", "RESOLVED", "REPLACED", "REVOKED"}:
            raise ApprovalConflict("terminal target cannot be changed")
    node = entities[identity]
    operations = proposal["operations"]
    if not isinstance(operations, list) or not operations:
        raise ApprovalConflict("empty operations")
    for operation in operations:
        op = operation.get("op")
        if op in {"ADD", "REPLACE", "REMOVE"}:
            expected = {"op", "path"} | ({"value"} if op != "REMOVE" else set())
            if set(operation) != expected:
                raise ApprovalConflict("invalid property operation")
            parts = parse_pointer(operation["path"])
            if len(parts) != 1 or parts[0] in {"id", "entityType", "revision", "createdAt", "updatedAt"}:
                raise ApprovalConflict("unsupported or immutable property path")
            prop = parts[0]
            if (op == "ADD" and prop in node) or (op != "ADD" and prop not in node):
                raise ApprovalConflict("property operation presence mismatch")
            if op == "REMOVE":
                del node[prop]
            else:
                validate_typed_value(operation["value"])
                node[prop] = deepcopy(operation["value"]["value"])
        elif op in {"CONNECT", "DISCONNECT"}:
            required_edge = {"op", "relationshipType", "direction", "otherEntityId"}
            if not required_edge <= operation.keys() or set(operation) - required_edge - {"properties"}:
                raise ApprovalConflict("invalid relationship operation")
            if operation["direction"] not in {"OUTGOING", "INCOMING"}:
                raise ApprovalConflict("invalid relationship direction")
            if operation["relationshipType"] in AUDIT_RELATIONS:
                raise ApprovalConflict("approval provenance cannot be supplied as domain mutation")
            source, other = identity, operation["otherEntityId"]
            if operation["direction"] == "INCOMING":
                source, other = other, source
            key = source, operation["relationshipType"], other
            matches = [e for e in edges if (e.source, e.relationship, e.target) == key]
            if op == "DISCONNECT":
                edge = _one(matches, "relationship to disconnect")
                edges.remove(edge)
            else:
                if matches:
                    raise ApprovalConflict("duplicate connection")
                props = {}
                for name, value in operation.get("properties", {}).items():
                    validate_typed_value(value)
                    props[name] = deepcopy(value["value"])
                edges.append(ApprovalEdge(*key, props))
        else:
            raise ApprovalConflict("unsupported approval operation")
    candidate = ApprovalGraph(entities, tuple(edges))
    _check_graph(candidate)
    return candidate


def _ci_values(graph, identity):
    node = _entity(graph, identity)
    kind = node.get("entityType")
    if kind == "CiV":
        return {identity}
    if kind == "RaN":
        result = set()
        for edge in _out(graph, identity, "PROTECTS"):
            result |= _ci_values(graph, edge.target)
        return result
    if kind == "PiF2":
        return {e.source for e in _in(graph, identity, "INSCRIBES_PURPOSE_IN")}
    if kind in NEXT_FUTURE:
        result = set()
        for edge in _out(graph, identity, "CONTRIBUTES_TO"):
            _entity(graph, edge.target, NEXT_FUTURE[kind])
            result |= _ci_values(graph, edge.target)
        return result
    return set()


def _sensitive_holders(before, after, proposal):
    identity = proposal["target"]["id"]
    old_keys = {(e.source, e.relationship, e.target) for e in before.edges}
    new_keys = {(e.source, e.relationship, e.target) for e in after.edges}
    changed_edges = old_keys ^ new_keys
    related = set()
    if proposal["target"]["entityType"] in {"CiV", "RaN", "PiF2"}:
        related.add(identity)
    for source, relationship, target in changed_edges:
        if relationship in SENSITIVE_RELATIONS:
            related.update((source, target))
    holders = set()
    for graph in (before, after):
        for item in related & graph.entities.keys():
            for value_id in _ci_values(graph, item):
                holder = _one(_out(graph, value_id, "HELD_BY"), "value holder").target
                kind = _entity(graph, holder).get("entityType")
                if kind not in {"RoFOrg", "RoFTeam", "RoFTeamMember"}:
                    raise ApprovalConflict("invalid affected value holder")
                holders.add(holder)
    if related and not holders:
        raise ApprovalConflict("sensitive mutation has no resolvable value scope")
    return holders


def _chain_requirements(graph, candidate, proposal, at):
    task_id = proposal["target"]["id"]
    original_goal = _one([e for e in _in(graph, task_id, "DECOMPOSES_INTO")
                          if _entity(graph, e.source).get("entityType") == "PiF1o"], "task PiF1o").source
    _, task_org = _task_org(graph, task_id)
    target = candidate.entities[task_id]
    requirements, visited = {}, set()

    def visit(identity):
        if identity in visited:
            return
        visited.add(identity)
        node = _entity(graph, identity)
        kind = node.get("entityType")
        if kind not in FUTURE_TYPES or node.get("status") != "ACTIVE":
            raise ApprovalConflict("release requires an active typed future path")
        member_id = _one(_out(graph, identity, "ACCOUNTABLE_MEMBER"), "accountable member").target
        member = _entity(graph, member_id, "RoFTeamMember")
        if member.get("memberType") != "HUMAN":
            raise ApprovalRequired("accountable approval anchor must be human")
        permitted, denied = [], False
        for edge in sorted(_out(graph, member_id, "HAS_ASSIGNMENT"), key=lambda e: e.target):
            try:
                actor = _actor(graph, edge.target, at)
            except ApprovalRequired:
                continue
            if actor["organizationId"] != task_org:
                continue
            try:
                if _permission(graph, proposal, actor, mode="ACCOUNTABLE_CHAIN", level=kind,
                               at=at, target_id=task_id, target=target, decision_key=RELEASE):
                    permitted.append(edge.target)
            except ApprovalDenied:
                denied = True
        if denied:
            raise ApprovalDenied("accountable approver was denied; escalation is not an override")
        if permitted:
            requirements[identity] = ApprovalRequirement(identity, "ACCOUNTABLE_CHAIN", tuple(permitted))
            return
        if kind == "PiF2":
            raise ApprovalRequired("no authorized approver at end of future chain")
        parents = [edge.target for edge in _out(graph, identity, "CONTRIBUTES_TO")
                   if _entity(graph, edge.target).get("status") not in {"REPLACED", "REVOKED"}]
        if not parents:
            raise ApprovalConflict("incomplete escalation path")
        for parent in sorted(parents):
            _entity(graph, parent, NEXT_FUTURE[kind])
            visit(parent)

    visit(original_goal)
    return tuple(requirements[key] for key in sorted(requirements))


def _policy_holders(graph, rule_id):
    return {_one(_out(graph, value_id, "HELD_BY"), "policy value holder").target
            for value_id in _ci_values(graph, rule_id)}


def enrollment_latches(graph, disabled=()):
    """Persist this monotone union on EVERY policy-activation commit."""
    latched = set(disabled)
    for identity, node in graph.entities.items():
        policy = node.get("approvalPolicy")
        if node.get("entityType") != "RaN" or node.get("status") != "ACTIVE" or not policy:
            continue
        validate_approval_policy(policy)
        if policy["mode"] == "VALUE_SCOPE":
            latched.update(_policy_holders(graph, identity))
    return frozenset(latched)


def make_approval_context(graph, proposal, *, at, enrollment_authorities=(), disabled_enrollment_holders=()):
    """Derive the entire request/route contract, never accept client-chosen paths.

    graph is the complete trusted pre-change domain view. The profile's small
    candidate builder applies exactly the supplied single-target operations.
    Cross-organization task approval is deliberately unsupported (fail closed).
    """
    at = _time(at)
    _check_graph(graph)
    candidate = _apply_proposal(graph, proposal)
    _actor(graph, proposal["requestedByRoleAssignmentId"], at, human_required=False)
    if _time(proposal["requestedAt"]) > at:
        raise ApprovalConflict("request is from the future")
    target_id = proposal["target"]["id"]
    old = graph.entities.get(target_id, {})
    new = candidate.entities[target_id]
    release = (new.get("entityType") == "Task" and old.get("status") == "DRAFT"
               and new.get("status") in {"ACTIVE", "BLOCKED"})
    holders = _sensitive_holders(graph, candidate, proposal)
    if release and holders:
        raise ApprovalConflict("release and value decisions require separate requests")
    if release:
        if proposal["changeType"] != "CHANGED" or len(proposal["operations"]) != 1:
            raise ApprovalConflict("release must be a separate status-only request")
        requirements = _chain_requirements(graph, candidate, proposal, at)
        decision_key = RELEASE
    elif holders:
        required = []
        disabled = enrollment_latches(graph, disabled_enrollment_holders)
        for holder in sorted(holders):
            permitted, denied = [], False
            for identity, node in sorted(graph.entities.items()):
                if node.get("entityType") != "RoleAssignment":
                    continue
                try:
                    actor = _actor(graph, identity, at)
                except ApprovalRequired:
                    continue
                if not _holder_contains(graph, holder, actor, at):
                    continue
                try:
                    allowed = _permission(graph, proposal, actor, mode="VALUE_SCOPE", level=None,
                                          at=at, target_id=identity, target=node, decision_key=CONFIRM,
                                          holder_id=holder)
                except ApprovalDenied:
                    denied = True
                    continue
                enrolled = holder not in disabled and any(
                    e.holder_id == holder and e.role_assignment_id == identity and e.member_id == actor["memberId"]
                    for e in enrollment_authorities)
                if allowed or enrolled:
                    permitted.append(identity)
            if denied:
                raise ApprovalDenied("value-scope confirmation is explicitly denied")
            if not permitted:
                raise ApprovalRequired("missing value-scope authority (no automatic root fallback)")
            required.append(ApprovalRequirement(holder, "VALUE_SCOPE", tuple(permitted)))
        requirements = tuple(required)
        decision_key = CONFIRM
    else:
        raise ApprovalConflict("request is not a supported protected decision")
    request_hash = _hash(proposal)
    config = sorted([e.member_id, e.role_assignment_id, e.holder_id] for e in enrollment_authorities)
    context_hash = _hash({
        "approvalProfileVersion": APPROVAL_PROFILE, "decisionKey": decision_key,
        "requestHash": request_hash, "graph": _domain_projection(graph),
        "requirements": [{"anchorId": r.anchor_id, "mode": r.mode,
                          "candidateRoleAssignmentIds": list(r.candidate_role_assignment_ids)} for r in requirements],
        "enrollmentAuthorities": config,
        "disabledEnrollmentHolders": sorted(enrollment_latches(graph, disabled_enrollment_holders)),
    })
    return ApprovalContext(decision_key, request_hash, context_hash, requirements)


def _check_receipt(receipt, graph, context, *, at, verify_attestation):
    fields = {"receiptId", "requestHash", "contextHash", "decidedAt", "validUntil",
              "outcome", "roleAssignmentId", "memberId", "attestation"}
    if not isinstance(receipt, Mapping) or set(receipt) != fields:
        raise ApprovalConflict("invalid approval receipt fields")
    if not all(_uuid(receipt[field]) for field in ("receiptId", "roleAssignmentId", "memberId")):
        raise ApprovalConflict("invalid approval receipt identity")
    if receipt["requestHash"] != context.request_hash or receipt["contextHash"] != context.context_hash:
        raise ApprovalConflict("receipt is bound to another request/context")
    if receipt["outcome"] not in {"APPROVED", "REJECTED"}:
        raise ApprovalConflict("unknown approval outcome")
    decided_at, expires_at = _time(receipt["decidedAt"]), _time(receipt["validUntil"])
    if not decided_at <= at < expires_at:
        raise ApprovalRequired("approval is not yet valid or has expired")
    if not isinstance(receipt["attestation"], str) or not receipt["attestation"]:
        raise ApprovalRequired("missing human authentication attestation")
    if not callable(verify_attestation):
        raise ApprovalRequired("trusted human attestation verifier is mandatory")
    try:
        authenticated_member = verify_attestation(deepcopy(dict(receipt)))
    except Exception as error:
        raise ApprovalRequired("attestation verification failed") from error
    if authenticated_member != receipt["memberId"]:
        raise ApprovalRequired("attestation does not authenticate the approving human")
    actor_then = _actor(graph, receipt["roleAssignmentId"], decided_at)
    actor_now = _actor(graph, receipt["roleAssignmentId"], at)
    if actor_then["memberId"] != receipt["memberId"] or actor_now["memberId"] != receipt["memberId"]:
        raise ApprovalRequired("human identity does not own approval assignment")
    if not any(receipt["roleAssignmentId"] in r.candidate_role_assignment_ids for r in context.requirements):
        raise ApprovalRequired("receipt actor has no required approval authority")


def validate_approval_envelope(envelope, graph, *, at, verify_attestation,
                               durable_receipts, supported_approval_profiles=(),
                               enrollment_authorities=(), disabled_enrollment_holders=()):
    """Validate exact payload, ALL routes, durable refusals and current authority.

    durable_receipts is the trusted complete receipt ledger, not client input.
    A verifier returns authenticated HUMAN member ID, not a Boolean assertion.
    """
    if APPROVAL_PROFILE not in supported_approval_profiles:
        raise ApprovalRequired("SYNC has not declared approval profile 1.0 capability")
    fields = {"approvalProfileVersion", "decisionKey", "proposal", "requestHash", "contextHash", "receipts"}
    if not isinstance(envelope, Mapping) or set(envelope) != fields or envelope["approvalProfileVersion"] != APPROVAL_PROFILE:
        raise ApprovalConflict("unsupported approval envelope/profile")
    at = _time(at)
    context = make_approval_context(graph, envelope["proposal"], at=at,
                                    enrollment_authorities=enrollment_authorities,
                                    disabled_enrollment_holders=disabled_enrollment_holders)
    if (envelope["decisionKey"] != context.decision_key or envelope["requestHash"] != context.request_hash
            or envelope["contextHash"] != context.context_hash):
        raise ApprovalConflict("stale or misclassified approval envelope")
    receipts = envelope["receipts"]
    if not isinstance(receipts, list) or not receipts:
        raise ApprovalRequired("complete human approval is missing")
    ids = [r.get("receiptId") for r in receipts]
    actors = [r.get("roleAssignmentId") for r in receipts]
    if len(set(ids)) != len(ids) or len(set(actors)) != len(actors):
        raise ApprovalConflict("duplicate receipt or approver assignment")
    recorded = {key: value for key, value in durable_receipts.items()
                if value.get("requestHash") == context.request_hash}
    if set(ids) != set(recorded) or any(canonical_json(r) != canonical_json(recorded[r["receiptId"]]) for r in receipts):
        raise ApprovalRequired("envelope must include all exact durable decisions for this proposal")
    for receipt in receipts:
        _check_receipt(receipt, graph, context, at=at, verify_attestation=verify_attestation)
        prior_context = make_approval_context(
            graph, envelope["proposal"], at=receipt["decidedAt"],
            enrollment_authorities=enrollment_authorities,
            disabled_enrollment_holders=disabled_enrollment_holders)
        if prior_context != context:
            raise ApprovalConflict("authority/route was different at the human decision time")
        if receipt["outcome"] == "REJECTED":
            raise ApprovalDenied("a human rejected this proposal; submit a new proposal")
    approved = set(actors)
    if any(not approved.intersection(r.candidate_role_assignment_ids) for r in context.requirements):
        raise ApprovalRequired("not every required contribution branch/value scope is approved")
    edges = tuple(ApprovalEdge(envelope["proposal"]["requestId"], "APPROVED_BY", r["roleAssignmentId"], {
        "receiptId": r["receiptId"], "decidedAt": r["decidedAt"], "requestHash": context.request_hash,
        "approvalHash": _hash(r),
    }) for r in sorted(receipts, key=lambda r: r["roleAssignmentId"]))
    return ValidatedApproval(context, edges)


@dataclass(frozen=True)
class ApprovalWorkflow:
    """Durable-ledger simulation; persist every returned state atomically."""
    proposals: Mapping[str, Mapping] = field(default_factory=dict)
    receipts: Mapping[str, Mapping] = field(default_factory=dict)
    accepted: Mapping[str, Mapping] = field(default_factory=dict)
    accepted_proofs: Mapping[str, ValidatedApproval] = field(default_factory=dict)
    disabled_enrollment_holders: frozenset[str] = frozenset()


def register_proposal(state, proposal, *, authenticated_requester_role_assignment_id):
    """Trusted transport maps its authenticated principal to this assignment ID."""
    if authenticated_requester_role_assignment_id != proposal.get("requestedByRoleAssignmentId"):
        raise ApprovalRequired("authenticated requester does not match proposal provenance")
    identity = proposal["requestId"]
    for known in state.proposals.values():
        if known["requestId"] == identity or known["idempotencyKey"] == proposal["idempotencyKey"]:
            if canonical_json(known) != canonical_json(proposal):
                raise ApprovalConflict("proposal identity reused with another payload")
            return state
    return replace(state, proposals={**state.proposals, identity: deepcopy(proposal)})


def record_approval_receipt(state, proposal_id, receipt, graph, *, at, verify_attestation,
                            enrollment_authorities=()):
    proposal = state.proposals.get(proposal_id)
    if proposal is None or proposal_id in state.accepted:
        raise ApprovalConflict("unknown or already accepted proposal")
    context = make_approval_context(graph, proposal, at=at, enrollment_authorities=enrollment_authorities,
                                    disabled_enrollment_holders=state.disabled_enrollment_holders)
    _check_receipt(receipt, graph, context, at=_time(at), verify_attestation=verify_attestation)
    prior_context = make_approval_context(
        graph, proposal, at=receipt["decidedAt"], enrollment_authorities=enrollment_authorities,
        disabled_enrollment_holders=state.disabled_enrollment_holders)
    if prior_context != context:
        raise ApprovalConflict("receipt authority was different at its decision time")
    for known in state.receipts.values():
        if known["receiptId"] == receipt["receiptId"]:
            if canonical_json(known) != canonical_json(receipt):
                raise ApprovalConflict("receipt identity reused with another decision")
            return state
        if known["requestHash"] == context.request_hash and known["roleAssignmentId"] == receipt["roleAssignmentId"]:
            raise ApprovalConflict("one immutable decision per actor and proposal")
    return replace(state, receipts={**state.receipts, receipt["receiptId"]: deepcopy(receipt)})


def accept_approved_request(state, gate, envelope, graph, *, at, verify_attestation,
                           supported_approval_profiles=(), enrollment_authorities=()):
    """Atomic acceptance simulation: proof, unchanged requester, event, run queue."""
    proposal = envelope["proposal"]
    known = state.proposals.get(proposal["requestId"])
    if known is None or canonical_json(known) != canonical_json(proposal):
        raise ApprovalConflict("proposal is not durably registered")
    accepted = state.accepted.get(proposal["requestId"])
    if accepted is not None and canonical_json(accepted) != canonical_json(envelope):
        raise ApprovalConflict("accepted approval envelope is immutable")
    key = proposal["idempotencyKey"]
    if key in gate.successes:
        if (accepted is None or gate.requests.get(key) != canonical_json(envelope)
                or proposal["requestId"] not in state.accepted_proofs):
            raise ApprovalConflict("success receipt does not match the accepted approval")
        return state, gate, state.accepted_proofs[proposal["requestId"]]
    validated = validate_approval_envelope(
        envelope, graph, at=at, verify_attestation=verify_attestation, durable_receipts=state.receipts,
        supported_approval_profiles=supported_approval_profiles, enrollment_authorities=enrollment_authorities,
        disabled_enrollment_holders=state.disabled_enrollment_holders)
    next_gate = accept_request(gate, proposal["idempotencyKey"], envelope)
    next_state = replace(state, accepted={**state.accepted, proposal["requestId"]: deepcopy(envelope)},
                         accepted_proofs={**state.accepted_proofs, proposal["requestId"]: validated})
    return next_state, next_gate, validated


def release_with_approval(envelope, graph, tasks, *, at, verify_attestation, durable_receipts,
                          validate_activation: Callable, supported_approval_profiles=(),
                          enrollment_authorities=(), disabled_enrollment_holders=()):
    """High-level release: approval AND complete activation validation are required."""
    validated = validate_approval_envelope(
        envelope, graph, at=at, verify_attestation=verify_attestation, durable_receipts=durable_receipts,
        supported_approval_profiles=supported_approval_profiles, enrollment_authorities=enrollment_authorities,
        disabled_enrollment_holders=disabled_enrollment_holders)
    if validated.context.decision_key != RELEASE:
        raise ApprovalConflict("value confirmation does not release tasks")
    identity = envelope["proposal"]["target"]["id"]
    task = tasks.get(identity)
    if task is None or task.status != "DRAFT":
        raise ApprovalConflict("release target is not a draft task")
    graph_task_ids = {key for key, node in graph.entities.items() if node.get("entityType") == "Task"}
    if set(tasks) != graph_task_ids:
        raise ApprovalConflict("task evaluator projection differs from the signed graph")
    for key, record in tasks.items():
        node = graph.entities[key]
        goals = [e.source for e in _in(graph, key, "DECOMPOSES_INTO")
                 if _entity(graph, e.source).get("entityType") == "PiF1o"]
        goal = _one(goals, "task projection PiF1o")
        children = {e.target for e in _out(graph, key, "DECOMPOSES_INTO")}
        dependencies = {e.target for e in _out(graph, key, "DEPENDS_ON")}
        successors = [e.target for e in _out(graph, key, "REPLACED_BY")]
        if (record.id != key or record.status != node.get("status") or record.kind != node.get("taskKind")
                or record.pif1o != goal or set(record.children) != children
                or set(record.depends_on) != dependencies
                or successors != ([] if record.replaced_by is None else [record.replaced_by])):
            raise ApprovalConflict("unbound task kind/state/goal/dependency projection")
    states = derive_task_states(tasks, releases=(identity,), validated_tasks=tuple(tasks))
    candidate = _apply_proposal(graph, envelope["proposal"])
    candidate_nodes = deepcopy(dict(candidate.entities))
    for key, status in states.items():
        candidate_nodes[key]["status"] = status
    candidate = ApprovalGraph(candidate_nodes, candidate.edges)
    # Full activation includes WHY/WHO, executors, RaN and ERoF permissions.
    if not callable(validate_activation) or validate_activation(candidate, identity, _time(at)) is not True:
        raise ApprovalRequired("complete activation validation did not succeed")
    if states[identity] not in {"ACTIVE", "BLOCKED"}:
        raise ApprovalConflict("approval cannot directly complete a task")
    return states


def commit_approved_request(state, gate, graph, *, proposal_id, run_id, fence, expected_epoch,
                            decision_at, verify_attestation, validate_candidate,
                            supported_approval_profiles=(), enrollment_authorities=()):
    """Revalidate proof at the existing gate's final decision time, then commit.

    validate_candidate is the complete trusted SYNC model/operation validator,
    returning True only for the exact proposal. Approval never replaces it.
    """
    envelope = state.accepted.get(proposal_id)
    if envelope is None:
        raise ApprovalRequired("no accepted approved request")
    proposal = envelope["proposal"]
    key = proposal["idempotencyKey"]
    if gate.requests.get(key) != canonical_json(envelope):
        raise ApprovalConflict("gate is bound to another approval payload")
    if key in gate.successes:
        # The durable commit receipt is authoritative even after domain revisions
        # or policy latches changed. Never reapply or revalidate old intent.
        return state, gate

    def revalidate(at):
        validate_approval_envelope(
            envelope, graph, at=at, verify_attestation=verify_attestation, durable_receipts=state.receipts,
            supported_approval_profiles=supported_approval_profiles, enrollment_authorities=enrollment_authorities,
            disabled_enrollment_holders=state.disabled_enrollment_holders)
        return callable(validate_candidate) and validate_candidate(deepcopy(graph), deepcopy(proposal), at) is True

    next_gate = gate_commit(gate, run_id=run_id, fence=fence, expected_epoch=expected_epoch,
                            request_key=key, outcome={"requestId": proposal_id, "approvalProfileVersion": APPROVAL_PROFILE},
                            validate_at=revalidate, decision_at=_time(decision_at))
    candidate = _apply_proposal(graph, proposal)
    next_state = replace(state, disabled_enrollment_holders=enrollment_latches(
        candidate, state.disabled_enrollment_holders))
    return next_state, next_gate
