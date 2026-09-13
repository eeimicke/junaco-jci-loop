"""Executable reference for selected JCI invariants.

Functions consume complete candidate data supplied by a caller. They do not
implement SYNC persistence, the complete RaN evaluator or Neo4j transactions.
The separate jci_approval module implements the fail-closed approval profile;
these lower-level primitives grant no authority. Domain changes and write
locking remain caller responsibilities. A RuleViolation is never success.
"""

from copy import deepcopy
from dataclasses import dataclass, field, replace
from datetime import datetime
import hashlib
import json
import re
from typing import Any, Callable, Mapping
from uuid import UUID

PROFILE = "2.0"
RETIRED = frozenset({"REPLACED", "REVOKED"})
ENTITY_TYPES = frozenset({
    "PiH", "CiV", "RaN", "SYNC", "PiF2", "PiF1s", "PiF1t", "PiF1o",
    "RoFOrg", "RoFOrgRelationship", "RoFTeam", "RoFTeamMember", "RoFRole",
    "RoleAssignment", "Task", "SuccessCriterion", "Result", "Verification",
    "Evidence", "ERoFObject", "ChangeEvent", "SyncEvent", "RaNConflict",
    "HistoricalCorrection",
})
IMMUTABLE = frozenset({"PiH", "ChangeEvent", "SyncEvent", "HistoricalCorrection"})
HISTORIZABLE = ENTITY_TYPES - IMMUTABLE
REPLACEABLE = HISTORIZABLE - {"Verification", "RaNConflict"}


class RuleViolation(ValueError):
    """A candidate is invalid; no domain commit is authorized."""


class LegacyProfileRequired(RuleViolation):
    """An old profile needs an explicit, independently reviewed resolver."""


# (source entityType, relationshipType, target entityType) -> owner endpoint(s).
# Every legal context is classified, including overloaded edge names. There is
# deliberately no fallback for an unknown relationship or endpoint combination.
RELATIONSHIP_OWNERS: dict[tuple[str, str, str], frozenset[str]] = {}


def _edges(sources, relationship, targets, owners):
    for source in sources.split() if isinstance(sources, str) else sources:
        for target in targets.split() if isinstance(targets, str) else targets:
            key = source, relationship, target
            if key in RELATIONSHIP_OWNERS:
                raise RuntimeError(f"duplicate ownership context: {key}")
            RELATIONSHIP_OWNERS[key] = frozenset(owners.split())


for _source, _relation, _targets in (
    ("CiV", "HELD_BY", "RoFOrg RoFTeam RoFTeamMember"),
    ("CiV", "INFORMED_BY", "CiV"),
    ("CiV", "INSCRIBES_PURPOSE_IN", "PiF2"),
    ("PiF1s", "CONTRIBUTES_TO", "PiF2"),
    ("PiF1t", "CONTRIBUTES_TO", "PiF1s"),
    ("PiF1o", "CONTRIBUTES_TO", "PiF1t"),
    ("PiF1o", "HAS_SUCCESS_CRITERIA", "SuccessCriterion"),
    ("PiF2 PiF1s PiF1t PiF1o", "ACCOUNTABLE_MEMBER", "RoFTeamMember"),
    ("PiF1o Task", "DECOMPOSES_INTO", "Task"),
    ("Task", "DEPENDS_ON", "Task"),
    ("Task", "RESPONSIBLE_TEAM", "RoFTeam"),
    ("Task", "EXECUTED_BY", "RoleAssignment"),
    ("Task RoleAssignment", "USES", "ERoFObject"),
    ("Task", "PRODUCES", "Result"),
    ("ERoFObject", "OWNED_BY", "RoFOrg"),
    ("RoFOrg", "HAS_TEAM", "RoFTeam"),
    ("RoFTeam", "HAS_MEMBER", "RoFTeamMember"),
    ("RoFTeamMember", "HAS_ROLE", "RoFRole"),
    ("RoFTeamMember", "HAS_ASSIGNMENT", "RoleAssignment"),
    ("RoleAssignment", "IN_TEAM", "RoFTeam"),
    ("RoleAssignment", "ACTIVATES_ROLE", "RoFRole"),
    ("RoFOrgRelationship", "SOURCE_ORG", "RoFOrg"),
    ("RoFOrgRelationship", "TARGET_ORG", "RoFOrg"),
    ("RoFOrgRelationship", "REPRESENTED_BY", "RoleAssignment"),
    ("RaN", "PROTECTS", "CiV PiF2"),
    ("RaN", "GOVERNS", "PiF1s PiF1t PiF1o Task SuccessCriterion Result "
     "Verification Evidence RoFOrg RoFOrgRelationship RoFTeam RoFTeamMember "
     "RoFRole RoleAssignment ERoFObject"),
    ("RaN", "APPLIES_IN", "RoFOrg RoFTeam"),
):
    _edges(_source, _relation, _targets, "source target")
for _kind in REPLACEABLE:
    _edges(_kind, "REPLACED_BY", _kind, "source target")
for _source, _relation, _targets in (
    ("Verification", "EVALUATES", "Result"),
    ("Verification", "CHECKS", "SuccessCriterion"),
    ("Verification", "USES_EVIDENCE", "Evidence"),
    ("Verification", "SUPERSEDES", "Verification"),
    ("HistoricalCorrection", "CORRECTS", "PiH"),
    ("HistoricalCorrection", "CAUSED_BY", "ChangeEvent"),
    ("HistoricalCorrection", "CORRECTED_BY", "RoleAssignment"),
    ("HistoricalCorrection", "USES_EVIDENCE", "Evidence"),
    ("HistoricalCorrection", "SUPERSEDES", "HistoricalCorrection"),
    ("ChangeEvent", "REQUESTED_BY", "RoleAssignment"),
    ("ChangeEvent", "APPROVED_BY", "RoleAssignment"),
    ("ChangeEvent", "TARGETS_HISTORY", "PiH"),
    ("ChangeEvent", "USES_EVIDENCE", "Evidence"),
    ("SyncEvent", "EXECUTES", "SYNC"),
    ("SyncEvent", "AFFECTS", ENTITY_TYPES),
    ("SyncEvent", "CREATES_HISTORY", "PiH"),
    ("SyncEvent", "CREATES_CORRECTION", "HistoricalCorrection"),
    ("RaNConflict", "CONFLICTING_RULE", "RaN"),
    ("RaNConflict", "AFFECTS", ENTITY_TYPES),
    ("RaNConflict", "DETECTED_BY", "SyncEvent"),
    ("RaNConflict", "USES_EVIDENCE", "Evidence"),
    ("RaNConflict", "RESOLVED_BY", "RoleAssignment"),
    ("RaNConflict", "RESOLVED_THROUGH", "ChangeEvent"),
):
    _edges(_source, _relation, _targets, "source")
_edges(ENTITY_TYPES, "CREATED_BY", "RoleAssignment", "source")
_edges("PiH", "PROVIDES_CONTEXT_TO", "CiV", "target")
_edges(HISTORIZABLE, "CHANGED_BY", "ChangeEvent", "target")
_edges("ChangeEvent", "TRIGGERS", "SyncEvent", "target")
_edges(HISTORIZABLE, "HAS_HISTORICAL_STATE", "PiH", "target")


def revision_owners(source_type: str, relationship: str, target_type: str):
    """Return the explicit owner endpoints; this does not authorize an edit."""
    try:
        return RELATIONSHIP_OWNERS[source_type, relationship, target_type]
    except KeyError:
        raise RuleViolation("unknown relationship context") from None


@dataclass(frozen=True)
class RelationshipChange:
    source: str
    relationship: str
    target: str
    operation: str = "CONNECT"


def revision_plan(entities: Mapping[str, Mapping], edges=(), changed_properties=(),
                  new_ids=(), existing_changed_by=()) -> dict[str, int]:
    """Deduplicate actual owner changes and return their next revisions.

    Existing entities contain their pre-change state. Inputs are the actual
    transaction delta (no unchanged/net-zero edges). New entities receive
    revision 1 but no history. Existing immutable/terminal owners cannot change,
    except the explicitly one-time CREATED CHANGED_BY append to an accepted
    ChangeEvent. existing_changed_by lists events already having that edge.
    """
    new_ids = set(new_ids)
    if not new_ids <= entities.keys():
        raise RuleViolation("unknown new entity")
    owners = set(changed_properties)
    linked_events = set(existing_changed_by)
    for edge in edges:
        if edge.operation not in {"CONNECT", "DISCONNECT", "CHANGE"}:
            raise RuleViolation("unknown relationship mutation")
        try:
            source, target = entities[edge.source], entities[edge.target]
        except KeyError:
            raise RuleViolation("unresolved relationship endpoint") from None
        for side in revision_owners(source["entityType"], edge.relationship,
                                    target["entityType"]):
            if (edge.relationship == "CHANGED_BY" and edge.target not in new_ids
                    and side == "target"):
                if (edge.operation != "CONNECT" or edge.source not in new_ids
                        or target.get("changeType") != "CREATED"
                        or target.get("targetEntityId") != edge.source
                        or target.get("status") != "RECORDED"
                        or target.get("revision") != 1
                        or edge.target in linked_events):
                    raise RuleViolation("invalid/repeated CREATED provenance append")
                linked_events.add(edge.target)
                continue
            owners.add(edge.source if side == "source" else edge.target)
    result = {}
    for identity in owners | new_ids:
        if identity not in entities:
            raise RuleViolation("unresolved changed entity")
        entity = entities[identity]
        if entity["entityType"] not in ENTITY_TYPES:
            raise RuleViolation("unknown entity type")
        if identity in new_ids:
            result[identity] = 1
        elif entity["entityType"] in IMMUTABLE or entity["status"] in TERMINAL:
            raise RuleViolation("cannot change immutable or terminal owner")
        else:
            revision = entity["revision"]
            if type(revision) is not int or revision < 1:
                raise RuleViolation("invalid revision")
            result[identity] = revision + 1
    return result


TERMINAL = {"ACHIEVED", "COMPLETED", "REPLACED", "REVOKED", "RECORDED", "RESOLVED"}


def may_transition(entity_type: str, source: str | None, target: str) -> bool:
    """Check only the canonical transition matrix; authorization and domain prerequisites remain caller checks."""
    if entity_type not in ENTITY_TYPES or source in TERMINAL:
        return False

    if entity_type in {"PiH", "ChangeEvent", "SyncEvent", "HistoricalCorrection"}:
        return source is None and target == "RECORDED"

    if entity_type == "Verification":
        return source is None and target == "COMPLETED"

    if entity_type == "RaNConflict":
        return (source, target) in {(None, "OPEN"), ("OPEN", "RESOLVED")}

    if entity_type == "Task":
        return (source, target) in {
            (None, "DRAFT"), ("DRAFT", "ACTIVE"), ("DRAFT", "BLOCKED"),
            ("DRAFT", "REVOKED"), ("ACTIVE", "BLOCKED"),
            ("ACTIVE", "COMPLETED"), ("ACTIVE", "REPLACED"),
            ("ACTIVE", "REVOKED"), ("BLOCKED", "ACTIVE"),
            ("BLOCKED", "COMPLETED"), ("BLOCKED", "REPLACED"),
            ("BLOCKED", "REVOKED"),
        }
    if entity_type == "Result" and (source, target) == ("ACTIVE", "COMPLETED"):
        return True

    if entity_type in {"PiF2", "PiF1s", "PiF1t", "PiF1o"} and (
        source, target
    ) == ("ACTIVE", "ACHIEVED"):
        return True

    return (source, target) in {
        (None, "DRAFT"), ("DRAFT", "ACTIVE"), ("DRAFT", "REVOKED"),
        ("ACTIVE", "REPLACED"), ("ACTIVE", "REVOKED"),
    }


def aggregate_contributions(mode: str, statuses: list[str]) -> bool:
    """Aggregate direct future contributions, excluding retired items and requiring a nonempty current scope."""
    current = [s for s in statuses if s not in {"REPLACED", "REVOKED"}]

    if not current:
        return False

    if mode == "ALL":
        return all(s == "ACHIEVED" for s in current)

    if mode == "ANY":
        return any(s == "ACHIEVED" for s in current)

    raise ValueError("unknown contributionMode")




def ran_decision(effect: str, condition: bool) -> str:
    """Evaluate one normalized RaN effect; conflict resolution and rule precedence belong to the full SYNC evaluator."""
    if effect == "REQUIRE":
        return "ALLOW" if condition else "DENY"

    if effect == "PROHIBIT":
        return "DENY" if condition else "NO_DECISION"

    if effect == "PERMIT":
        return "ALLOW" if condition else "NO_DECISION"

    raise ValueError("unknown RaN effect")


def valid_sync_lifecycle(
    scheduled_run_ids: list[str],
    completed_run_ids: list[str],
    sync_event_run_ids: list[str],
) -> bool:
    """Require exactly one immutable SyncEvent per completed scheduled run; unfinished runs have no event."""
    if len(set(scheduled_run_ids)) != len(scheduled_run_ids):
        return False
    if len(set(completed_run_ids)) != len(completed_run_ids):
        return False
    if not set(completed_run_ids).issubset(scheduled_run_ids):
        return False

    return (
        len(set(sync_event_run_ids)) == len(sync_event_run_ids)
        and set(sync_event_run_ids) == set(completed_run_ids)
    )


def valid_created_outcome(
    *,
    target_existed_before: bool,
    requested_revision: int | None,
    outcome: str,
    target_exists_after: bool,
    target_revision_after: int | None,
    changed_by_count: int,
    target_history_count: int,
) -> bool:
    """Check CREATED for the new target only. target_history_count excludes snapshots of changed existing structural endpoints."""
    if target_existed_before or requested_revision is not None or target_history_count != 0:
        return False
    if outcome == "SUCCESS":
        return (
            target_exists_after
            and target_revision_after == 1
            and changed_by_count == 1
        )
    if outcome in {"CONFLICT", "FAILED"}:
        return (
            not target_exists_after
            and target_revision_after is None
            and changed_by_count == 0
        )
    return False


def valid_historical_target(
    *,
    change_type: str,
    changed_by_count: int,
    target_history_ids: list[str],
    corrected_history_id: str | None,
    requested_revision: int | None,
) -> bool:
    """Bind a historical correction to exactly one immutable PiH without changing its source entity."""
    if change_type != "HISTORICAL_CORRECTION":
        return not target_history_ids
    return (
        changed_by_count == 0
        and requested_revision == 1
        and len(target_history_ids) == 1
        and corrected_history_id == target_history_ids[0]
    )


def verification_is_applicable(
    *,
    result_status: str,
    criterion_status: str,
    same_pif1o: bool,
    result_revision: int,
    criterion_revision: int,
    evaluated_result_revision: int,
    checked_criterion_revision: int,
    superseded: bool,
) -> bool:
    """Require completed results and active criteria at the exact revisions bound by an unsuperseded verification."""
    return (
        result_status == "COMPLETED"
        and criterion_status == "ACTIVE"
        and same_pif1o
        and not superseded
        and evaluated_result_revision == result_revision
        and checked_criterion_revision == criterion_revision
    )


def valid_bootstrap(
    *,
    graph_was_empty: bool,
    root_keys: list[str],
    required_types: set[str],
    created_types: set[str],
    created_statuses: dict[str, str],
    revisions: dict[str, int],
    created_at_values: set[str],
    valid_from_values: set[str],
    entities_without_creator: list[str],
) -> bool:
    """Check the one-time empty-graph trust root with revision-one entities and a sole creator exception."""
    return (
        graph_was_empty
        and root_keys == ["ROOT"]
        and required_types.issubset(created_types)
        and set(created_statuses) == required_types
        and all(status == "ACTIVE" for status in created_statuses.values())
        and set(revisions) == required_types
        and all(revision == 1 for revision in revisions.values())
        and len(created_at_values) == 1
        and len(valid_from_values) == 1
        and created_at_values == valid_from_values
        and entities_without_creator == ["RoleAssignment:ROOT"]
    )


def valid_historical_correction_commit(
    *,
    expected_hash: str,
    current_hash: str,
    corrected_fields: list[str],
    active_field_sets: list[set[str]],
    superseded_indexes: list[int],
    entity_type: str = "Task",
) -> bool:
    """Check base hash, decoded path overlap and complete supersession of at most one active correction."""
    if expected_hash != current_hash or not re.fullmatch("[0-9a-f]{64}", expected_hash):
        return False
    try:
        _field_set(corrected_fields, entity_type)
        for fields in active_field_sets:
            _field_set(sorted(fields), entity_type)
    except RuleViolation:
        return False

    new_fields = set(corrected_fields)
    overlaps = [
        index for index, active_fields in enumerate(active_field_sets)
        if any(paths_overlap(p, q) for p in new_fields for q in active_fields)
    ]
    if not overlaps:
        return not superseded_indexes

    return (
        len(overlaps) == 1
        and superseded_indexes == overlaps
        and new_fields.issuperset(active_field_sets[overlaps[0]])
    )


def valid_correction_value_maps(
    *,
    correction_type: str,
    corrected_fields: list[str],
    previous_values: dict[str, dict[str, object]],
    corrected_values: dict[str, dict[str, object]],
) -> bool:
    """Check exact field binding and TypedValues; actual path absence for ADDITION requires snapshot resolution."""
    try:
        for field_path in corrected_fields:
            parse_pointer(field_path)
        for value in list(previous_values.values()) + list(corrected_values.values()):
            validate_typed_value(value)
    except RuleViolation:
        return False
    field_set = set(corrected_fields)
    if set(previous_values) != field_set or set(corrected_values) != field_set:
        return False
    if correction_type == "ADDITION":
        return all(
            value.get("valueType") == "NULL" and value.get("value") is None
            for value in previous_values.values()
        )
    return correction_type in {"CORRECTION", "CLARIFICATION"}


def valid_civ_model(
    *,
    value_id: str,
    not_civ: str,
    self_civ: str,
    to_serve_civ: str,
    holder_id: str,
    holder_type: str,
    holder_member_type: str | None = None,
    informed_by_ids: list[str] | None = None,
    pif2_holder_sets: list[list[str]] | None = None,
) -> bool:
    """Check the three CiV dimensions and holder-derived scope."""
    if not all(part.strip() for part in (not_civ, self_civ, to_serve_civ)):
        return False
    if not holder_id or holder_type not in {"RoFOrg", "RoFTeam", "RoFTeamMember"}:
        return False
    if holder_type == "RoFTeamMember" and holder_member_type != "HUMAN":
        return False
    if value_id in (informed_by_ids or []):
        return False
    return all(set(holders) == {holder_id} for holders in (pif2_holder_sets or []))


RAN_GOVERNED_TYPES = {
    "PiF1s", "PiF1t", "PiF1o", "Task", "SuccessCriterion", "Result",
    "Verification", "Evidence", "RoFOrg", "RoFOrgRelationship", "RoFTeam",
    "RoFTeamMember", "RoFRole", "RoleAssignment", "ERoFObject",
}


@dataclass(frozen=True)
class TaskRecord:
    """Candidate facts; ID tuples represent supplied edges, not stored fields."""
    id: str
    pif1o: str
    status: str = "DRAFT"
    kind: str = "ATOMIC"
    children: tuple[str, ...] = ()
    depends_on: tuple[str, ...] = ()
    replaced_by: str | None = None


@dataclass(frozen=True)
class CriterionRecord:
    id: str
    pif1o: str
    status: str = "ACTIVE"
    requirement: str = "REQUIRED"
    mode: str = "ALL"
    revision: int = 1


@dataclass(frozen=True)
class ResultRecord:
    id: str
    task: str
    revision: int = 1
    status: str = "COMPLETED"


@dataclass(frozen=True)
class VerificationRecord:
    id: str
    result: str
    criterion: str
    result_revision: int
    criterion_revision: int
    outcome: str = "VALID"
    supersedes: str | None = None


def current_task_scope(tasks: Mapping[str, TaskRecord]) -> frozenset[str]:
    """Validate explicit current hierarchy; never infer replacement/revocation."""
    current = frozenset(k for k, task in tasks.items() if task.status not in RETIRED)
    parents, retired_parents, stored_parents = {}, {}, {}
    for identity, task in tasks.items():
        if identity != task.id or task.kind not in {"ATOMIC", "COMPOSITE"}:
            raise RuleViolation("invalid task identity/kind")
        if task.status not in {"DRAFT", "ACTIVE", "BLOCKED", "COMPLETED"} | RETIRED:
            raise RuleViolation("invalid task status")
        if task.kind == "ATOMIC" and task.children:
            raise RuleViolation("atomic task has children")
        if len(set(task.children)) != len(task.children):
            raise RuleViolation("duplicate task child")
        if task.status == "REPLACED":
            if task.replaced_by not in tasks or task.replaced_by == identity:
                raise RuleViolation("missing task replacement")
            if tasks[task.replaced_by].pif1o != task.pif1o:
                raise RuleViolation("replacement has another PiF1o")
        elif task.replaced_by is not None:
            raise RuleViolation("non-replaced task has successor")
        for child in task.children:
            if child not in tasks or tasks[child].pif1o != task.pif1o:
                raise RuleViolation("child must keep the same PiF1o")
            stored_parents.setdefault(child, []).append(identity)
            if child in current:
                collection = parents if identity in current else retired_parents
                collection.setdefault(child, []).append(identity)
            elif identity in current and tasks[child].status == "REPLACED":
                if tasks[child].replaced_by not in task.children:
                    raise RuleViolation("replacement not explicitly connected to parent")
        if identity in current and task.kind == "COMPOSITE":
            if not current.intersection(task.children):
                raise RuleViolation("current composite has no current children")
    if any(len(value) > 1 for value in stored_parents.values()):
        raise RuleViolation("multiple stored parents")
    if any(child not in parents for child in retired_parents):
        raise RuleViolation("retired composite leaves unresolved current descendants")
    for identity in tasks:
        seen, node = set(), identity
        while node is not None:
            if node in seen:
                raise RuleViolation("replacement cycle")
            seen.add(node)
            node = tasks[node].replaced_by
    # Historical retention does not waive the stored hierarchy/dependency DAGs.
    for relationship, attr in (("DECOMPOSES_INTO", "children"), ("DEPENDS_ON", "depends_on")):
        colors = {}
        for start in sorted(tasks):
            if colors.get(start) == 2:
                continue
            colors[start] = 1
            stack = [(start, iter(getattr(tasks[start], attr)))]
            path = []
            while stack:
                node, neighbors = stack[-1]
                target = next(neighbors, None)
                if target is None:
                    stack.pop()
                    colors[node] = 2
                    if path:
                        path.pop()
                    continue
                if target not in tasks:
                    raise RuleViolation("unresolved stored task edge")
                if colors.get(target) == 1:
                    first = [entry[0] for entry in stack].index(target)
                    raise CompletionCycle(path[first:] + [(node, relationship, target)])
                if colors.get(target) != 2:
                    colors[target] = 1
                    path.append((node, relationship, target))
                    stack.append((target, iter(getattr(tasks[target], attr))))
    return current


class CompletionCycle(RuleViolation):
    def __init__(self, cycle):
        self.cycle = tuple(cycle)  # (source, original relationshipType, target)
        super().__init__("completion cycle: " + repr(self.cycle))


def completion_order(tasks: Mapping[str, TaskRecord]) -> tuple[str, ...]:
    """Topologically order the UNION of child and dependency edges.

    Supply all candidate tasks in reached PiF1o scopes. Retired prerequisites
    remain visible and unfulfilled. Iterative DFS handles long chains.
    """
    current = current_task_scope(tasks)
    edges = {identity: [] for identity in current}
    for identity in sorted(current):
        task = tasks[identity]
        for dependency in task.depends_on:
            if dependency not in tasks or dependency == identity:
                raise RuleViolation("missing/self task dependency")
            edges.setdefault(dependency, [])
            edges[identity].append(("DEPENDS_ON", dependency))
        for child in task.children:
            if child in current:
                edges[identity].append(("DECOMPOSES_INTO", child))
        edges[identity].sort()
    colors, ordered = {}, []
    for start in sorted(edges):
        if colors.get(start) == 2:
            continue
        colors[start] = 1
        stack, path_edges = [(start, iter(edges[start]))], []
        while stack:
            node, neighbors = stack[-1]
            edge = next(neighbors, None)
            if edge is None:
                stack.pop()
                colors[node] = 2
                ordered.append(node)
                if path_edges:
                    path_edges.pop()
                continue
            kind, target = edge
            if colors.get(target) == 1:
                first = [entry[0] for entry in stack].index(target)
                raise CompletionCycle(path_edges[first:] + [(node, kind, target)])
            if colors.get(target) != 2:
                colors[target] = 1
                path_edges.append((node, kind, target))
                stack.append((target, iter(edges[target])))
    return tuple(ordered)


def composite_status(source: str, child_statuses, dependency_statuses=(),
                     *, release=False) -> str:
    """Own prerequisites precede child aggregation; DRAFT needs explicit release."""
    children = [status for status in child_statuses if status not in RETIRED]
    if not children:
        raise RuleViolation("empty current composite")
    if any(s not in {"DRAFT", "ACTIVE", "BLOCKED", "COMPLETED"} for s in children):
        raise RuleViolation("invalid child status")
    met = all(s == "COMPLETED" for s in dependency_statuses)
    if source in RETIRED:
        return source
    if source == "COMPLETED":
        if not met or any(s != "COMPLETED" for s in children):
            raise RuleViolation("candidate contradicts terminal composite completion")
        return source
    if source == "DRAFT":
        if not release:
            return "DRAFT"
        child_blocked = "ACTIVE" not in children and "BLOCKED" in children
        return "BLOCKED" if not met or child_blocked else "ACTIVE"
    if source not in {"ACTIVE", "BLOCKED"}:
        raise RuleViolation("invalid composite source")
    if not met:
        return "BLOCKED"
    if all(s == "COMPLETED" for s in children):
        return "COMPLETED"
    if "ACTIVE" in children:
        return "ACTIVE"
    return "BLOCKED" if "BLOCKED" in children else "ACTIVE"


def derive_task_states(tasks: Mapping[str, TaskRecord], *, releases=(),
                       confirmed_completions=(), validated_tasks=()) -> dict[str, str]:
    """Pure derivation; caller explicitly supplies passed WHY/WHO/RaN validation."""
    releases, completions, validated = map(set, (
        releases, confirmed_completions, validated_tasks))
    if not (releases | completions | validated) <= tasks.keys():
        raise RuleViolation("unknown task in transition request")
    output = {}
    for identity in completion_order(tasks):
        task = tasks[identity]
        if task.status in RETIRED:
            output[identity] = task.status
            continue
        dependency_states = [output[d] for d in task.depends_on]
        met = all(s == "COMPLETED" for s in dependency_states)
        if task.kind == "COMPOSITE":
            if task.status == "DRAFT" and identity in completions:
                raise RuleViolation("DRAFT cannot complete directly")
            state = composite_status(
                task.status, [output[c] for c in task.children if c in output],
                dependency_states, release=identity in releases)
        elif task.status == "COMPLETED":
            if not met:
                raise RuleViolation("candidate contradicts terminal atomic completion")
            state = "COMPLETED"
        elif task.status == "DRAFT":
            if identity in completions:
                raise RuleViolation("DRAFT cannot complete directly")
            state = ("ACTIVE" if met else "BLOCKED") if identity in releases else "DRAFT"
        elif not met:
            state = "BLOCKED"
        else:
            state = "COMPLETED" if identity in completions else "ACTIVE"
        if state != task.status:
            if not may_transition("Task", task.status, state):
                raise RuleViolation("illegal derived task transition")
            if identity not in validated:
                raise RuleViolation("transition lacks complete domain validation")
        output[identity] = state
    return output


def pif1o_achievable(goal: str, tasks: Mapping[str, TaskRecord], criteria,
                    results: Mapping[str, ResultRecord], verifications,
                    *, model_valid: bool) -> bool:
    """Conservative current-work-only aggregation preserving all historical edges."""
    current = current_task_scope(tasks)
    completion_order(tasks)
    scope = {identity for identity in current if tasks[identity].pif1o == goal}
    if not model_valid or not scope or any(tasks[t].status != "COMPLETED" for t in scope):
        return False
    if any(tasks[d].status != "COMPLETED" for t in scope for d in tasks[t].depends_on):
        return False
    criteria = list(criteria)
    if len({c.id for c in criteria}) != len(criteria):
        raise RuleViolation("duplicate criterion")
    for c in criteria:
        if c.requirement not in {"REQUIRED", "OPTIONAL"} or c.mode not in {"ALL", "ANY"}:
            raise RuleViolation("invalid criterion enum")
    required = [c for c in criteria if c.pif1o == goal and c.status not in RETIRED
                and c.requirement == "REQUIRED"]
    if not required:
        return False
    checks = list(verifications)
    if len({v.id for v in checks}) != len(checks):
        raise RuleViolation("duplicate verification")
    by_id, superseded = {v.id: v for v in checks}, set()
    for v in checks:
        if v.outcome not in {"VALID", "INVALID", "INCONCLUSIVE"}:
            raise RuleViolation("invalid verification outcome")
        if v.supersedes is not None:
            old = by_id.get(v.supersedes)
            if old is None or old.id in superseded or (old.result, old.criterion) != (v.result, v.criterion):
                raise RuleViolation("invalid or branching verification supersession")
            if old.result_revision > v.result_revision or old.criterion_revision > v.criterion_revision:
                raise RuleViolation("verification revisions move backwards")
            superseded.add(old.id)
    for v in checks:
        seen = set()
        while v is not None:
            if v.id in seen:
                raise RuleViolation("verification supersession cycle")
            seen.add(v.id)
            v = by_id.get(v.supersedes)
    active_pairs = set()
    for v in checks:
        if v.id not in superseded:
            pair = v.result, v.criterion, v.result_revision, v.criterion_revision
            if pair in active_pairs:
                raise RuleViolation("duplicate current verification for bound revisions")
            active_pairs.add(pair)
    for criterion in required:
        if criterion.status != "ACTIVE":
            return False
        outcomes = []
        for v in checks:
            result = results.get(v.result)
            if (v.criterion == criterion.id and v.id not in superseded
                    and result is not None and result.task in scope
                    and result.status == "COMPLETED"
                    and v.result_revision == result.revision
                    and v.criterion_revision == criterion.revision):
                outcomes.append(v.outcome)
        if not outcomes or (criterion.mode == "ALL" and any(v != "VALID" for v in outcomes)):
            return False
        if criterion.mode == "ANY" and "VALID" not in outcomes:
            return False
    return True


COMMON_SNAPSHOT_PROPERTIES = frozenset({"name", "description", "status"})
TYPE_PROPERTIES = {
    "CiV": "notCiV selfCiV toServeCiV",
    "RaN": "ruleType effect statement decisionKey scopeType governedTypes condition priority validFrom validUntil approvalPolicy",
    "SYNC": "version definition validFrom validUntil",
    "PiF2": "targetState horizonStart horizonEnd targetDate contributionMode",
    "PiF1s": "targetState horizonStart horizonEnd targetDate contributionMode",
    "PiF1t": "targetState horizonStart horizonEnd targetDate contributionMode",
    "PiF1o": "targetState horizonStart horizonEnd targetDate",
    "RoFOrg": "legalName orgType externalReference",
    "RoFOrgRelationship": "type validFrom validUntil",
    "RoFTeam": "teamType validFrom validUntil",
    "RoFTeamMember": "memberType displayName externalReference",
    "RoFRole": "roleName responsibility roleType",
    "RoleAssignment": "validFrom validUntil allocation bootstrapKey",
    "Task": "taskKind taskType plannedStart plannedEnd actualStart actualEnd",
    "SuccessCriterion": "criterion measurementType requirementLevel evaluationMode operator targetValue unit",
    "Result": "resultType value producedAt",
    "Verification": "method outcome verifiedAt evaluatedResultRevision checkedCriterionRevision reason",
    "Evidence": "evidenceType reference capturedAt checksum",
    "ERoFObject": "objectType validFrom validUntil externalReference",
    "RaNConflict": "conflictKey conflictType detectedAt reason resolvedAt resolution",
}
SNAPSHOT_PROPERTIES = {
    kind: COMMON_SNAPSHOT_PROPERTIES | frozenset(fields.split())
    for kind, fields in TYPE_PROPERTIES.items()
}
RELATIONSHIP_PROPERTIES = {"HAS_MEMBER": frozenset({"validFrom", "validUntil"}),
                           "HAS_ROLE": frozenset({"validFrom", "validUntil"}),
                           "APPROVED_BY": frozenset({"receiptId", "decidedAt", "requestHash", "approvalHash"})}
DECIMAL_PATTERN = re.compile(r"-?(?:0|[1-9][0-9]*)(?:\.[0-9]*[1-9])?\Z")
NULL_VALUE = {"valueType": "NULL", "value": None}


def _integer_text(value: int) -> str:
    """Exact integer rendering independent of Python's optional digit limit."""
    if value == 0:
        return "0"
    negative, number, parts = value < 0, abs(value), []
    while number:
        number, part = divmod(number, 10 ** 1000)
        parts.append(str(part))
    return ("-" if negative else "") + parts[-1] + "".join(
        part.zfill(1000) for part in reversed(parts[:-1]))


def canonical_json(value: Any) -> bytes:
    """JCI 2.0 canonical UTF-8 JSON; exact integers, never binary floats.

    Decimal quantities are TypedValue DECIMAL strings. Nested JSON numbers are
    integers only. Object keys use Unicode scalar-value order, not locale or
    UTF-16 order. Strings preserve codepoints; JSON controls use json escaping.
    """
    def serialize(item):
        if item is None:
            return "null"
        if type(item) is bool:
            return "true" if item else "false"
        if type(item) is int:
            return _integer_text(item)
        if isinstance(item, str):
            if any(0xD800 <= ord(char) <= 0xDFFF for char in item):
                raise RuleViolation("unpaired Unicode surrogate")
            return json.dumps(item, ensure_ascii=False)
        if isinstance(item, list):
            return "[" + ",".join(serialize(child) for child in item) + "]"
        if isinstance(item, dict):
            if not all(isinstance(key, str) for key in item):
                raise RuleViolation("non-string JSON key")
            return "{" + ",".join(serialize(key) + ":" + serialize(item[key])
                                  for key in sorted(item)) + "}"
        raise RuleViolation("unsupported JSON value; binary floats are forbidden")
    return serialize(value).encode("utf-8")


def parse_exact_json(text: str) -> Any:
    """Reject duplicates/non-integral numbers without ever rounding a payload."""
    def pairs(items):
        output = {}
        for key, value in items:
            if key in output:
                raise RuleViolation("duplicate JSON key")
            output[key] = value
        return output
    def integer(token):
        sign = -1 if token.startswith("-") else 1
        digits = token.lstrip("-")
        value = 0
        for offset in range(0, len(digits), 1000):
            chunk = digits[offset:offset + 1000]
            value = value * 10 ** len(chunk) + int(chunk)
        return sign * value
    def noninteger(_):
        raise RuleViolation("use TypedValue DECIMAL, not a JSON float")
    try:
        value = json.loads(text, object_pairs_hook=pairs, parse_int=integer,
                           parse_float=noninteger, parse_constant=noninteger)
    except (json.JSONDecodeError, UnicodeError) as error:
        raise RuleViolation("invalid JSON") from error
    canonical_json(value)
    return value


def validate_typed_value(typed: Mapping) -> None:
    if not isinstance(typed, dict) or set(typed) != {"valueType", "value"}:
        raise RuleViolation("invalid TypedValue envelope")
    kind, value = typed["valueType"], typed["value"]
    valid = {
        "NULL": value is None,
        "BOOLEAN": type(value) is bool,
        "INTEGER": type(value) is int,
        "DECIMAL": isinstance(value, str) and bool(DECIMAL_PATTERN.fullmatch(value)) and value != "-0",
        "STRING": isinstance(value, str),
        "DATE": isinstance(value, str) and bool(re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", value)),
        "DATETIME": isinstance(value, str),
        "OBJECT": isinstance(value, dict),
        "ARRAY": isinstance(value, list),
    }
    if not valid.get(kind, False):
        raise RuleViolation("TypedValue type/value mismatch")
    if kind in {"DATE", "DATETIME"}:
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
            if kind == "DATETIME" and (parsed.tzinfo is None or "T" not in value):
                raise ValueError("missing timezone")
        except ValueError as error:
            raise RuleViolation("invalid typed date/time") from error
    canonical_json(value)
    def nested(item):
        if isinstance(item, dict):
            if "valueType" in item and "value" in item:
                validate_typed_value(item)
            else:
                for child in item.values():
                    nested(child)
        elif isinstance(item, list):
            for child in item:
                nested(child)
    if kind in {"OBJECT", "ARRAY"}:
        nested(value)


def parse_pointer(pointer: str) -> tuple[str, ...]:
    """RFC 6901 JSON-string form; decode segments, never percent-decode."""
    if not isinstance(pointer, str) or not pointer.startswith("/"):
        raise RuleViolation("pointer must be an absolute JSON pointer")
    tokens = pointer[1:].split("/")
    decoded = []
    for token in tokens:
        if re.search(r"~(?![01])", token):
            raise RuleViolation("invalid JSON pointer escape")
        decoded.append(token.replace("~1", "/").replace("~0", "~"))
    return tuple(decoded)


def encode_pointer(segments) -> str:
    return "".join("/" + token.replace("~", "~0").replace("/", "~1") for token in segments)


def paths_overlap(left: str, right: str) -> bool:
    a, b = parse_pointer(left), parse_pointer(right)
    return a == b[:len(a)] or b == a[:len(b)]


def relationship_key(snapshot: Mapping) -> str:
    try:
        direction, relation = snapshot["direction"], snapshot["relationshipType"]
        identity = str(UUID(snapshot["otherEntityId"]))
    except (KeyError, ValueError, AttributeError, TypeError) as error:
        raise RuleViolation("invalid relationship key") from error
    if snapshot["otherEntityId"] != identity:
        raise RuleViolation("relationship UUID must use canonical lowercase hyphenated form")
    if direction not in {"INCOMING", "OUTGOING"} or relation not in {
        context[1] for context in RELATIONSHIP_OWNERS
    }:
        raise RuleViolation("unknown relationship direction/type")
    return f"{direction}:{relation}:{identity}"


def parse_correction_path(pointer: str, entity_type: str, *, profile=PROFILE):
    if profile != PROFILE:
        raise LegacyProfileRequired("explicit resolver required for snapshot " + profile)
    parts = parse_pointer(pointer)
    if encode_pointer(parts) != pointer:
        raise RuleViolation("non-canonical pointer")
    if entity_type not in SNAPSHOT_PROPERTIES:
        raise RuleViolation("non-historizable snapshot type")
    if len(parts) == 3 and parts[:2] == ("stateData", "properties"):
        if parts[2] not in SNAPSHOT_PROPERTIES[entity_type]:
            raise RuleViolation("unknown snapshot property")
        return parts
    if len(parts) not in {2, 4} or parts[0] != "relationshipData":
        raise RuleViolation("only complete properties/relationship entries are correctable")
    key = parts[1].split(":")
    if len(key) != 3:
        raise RuleViolation("invalid stable relationship key")
    direction, relation, identity = key
    canonical = relationship_key({"direction": direction, "relationshipType": relation,
                                  "otherEntityId": identity})
    if canonical != parts[1]:
        raise RuleViolation("non-canonical relationship key")
    if len(parts) == 4:
        if parts[2] != "properties" or parts[3] not in RELATIONSHIP_PROPERTIES.get(relation, ()):
            raise RuleViolation("unknown relationship property")
    return parts


def validate_snapshot(snapshot: Mapping, *, profile=PROFILE) -> None:
    if profile != PROFILE:
        raise LegacyProfileRequired("legacy snapshot requires its own resolver")
    if set(snapshot) != {"stateData", "relationshipData"}:
        raise RuleViolation("snapshot payload must have exactly stateData/relationshipData")
    state, relationships = snapshot["stateData"], snapshot["relationshipData"]
    if not isinstance(state, dict) or set(state) != {"entityType", "revision", "properties"}:
        raise RuleViolation("invalid StateSnapshot")
    kind = state["entityType"]
    if kind not in SNAPSHOT_PROPERTIES or type(state["revision"]) is not int or state["revision"] < 1:
        raise RuleViolation("invalid snapshot type/revision")
    if not isinstance(state["properties"], dict):
        raise RuleViolation("invalid snapshot properties")
    for name, value in state["properties"].items():
        if name not in SNAPSHOT_PROPERTIES[kind]:
            raise RuleViolation("unknown snapshot property")
        validate_typed_value(value)
    if not isinstance(relationships, list):
        raise RuleViolation("relationshipData must remain a list")
    keys = set()
    for edge in relationships:
        if not isinstance(edge, dict) or set(edge) != {
            "direction", "relationshipType", "otherEntityId", "otherEntityType", "properties"
        }:
            raise RuleViolation("invalid RelationshipSnapshot")
        key = relationship_key(edge)
        if key in keys:
            raise RuleViolation("duplicate stable relationship key")
        keys.add(key)
        context = ((kind, edge["relationshipType"], edge["otherEntityType"])
                   if edge["direction"] == "OUTGOING"
                   else (edge["otherEntityType"], edge["relationshipType"], kind))
        owned_side = "source" if edge["direction"] == "OUTGOING" else "target"
        if owned_side not in revision_owners(*context):
            raise RuleViolation("reference-only edge is not part of snapshot profile 2.0")
        if not isinstance(edge["properties"], dict):
            raise RuleViolation("invalid relationship properties")
        for name, value in edge["properties"].items():
            if name not in RELATIONSHIP_PROPERTIES.get(edge["relationshipType"], ()):
                raise RuleViolation("unknown relationship property")
            validate_typed_value(value)
            if value["valueType"] != "DATETIME":
                raise RuleViolation("relationship validity must be DATETIME")


def _sorted_snapshot(snapshot):
    output = deepcopy(snapshot)
    output["relationshipData"].sort(
        key=lambda item: (item["relationshipType"], item["direction"], str(UUID(item["otherEntityId"]))))
    return output


def history_hash(snapshot: Mapping, *, profile=PROFILE) -> str:
    validate_snapshot(snapshot, profile=profile)
    return hashlib.sha256(canonical_json(_sorted_snapshot(snapshot))).hexdigest()


@dataclass(frozen=True)
class HistoricalCorrectionRecord:
    """Facts of an immutable correction; no additional graph entity type."""
    id: str
    pih: str
    corrected_at: str
    fields: tuple[str, ...]
    previous: Mapping
    corrected: Mapping
    correction_type: str
    base_hash: str
    supersedes: str | None = None
    value_profile: str = PROFILE


def _field_set(fields, entity_type):
    if not fields or list(fields) != sorted(set(fields)):
        raise RuleViolation("fields must be unique and sorted")
    for index, pointer in enumerate(fields):
        parse_correction_path(pointer, entity_type)
        if any(paths_overlap(pointer, other) for other in fields[index + 1:]):
            raise RuleViolation("overlapping fields within correction")


def _relationship_correction_identity(parts, typed):
    """Resolve all immutable identity fields of a whole relationship value."""
    validate_typed_value(typed)
    if typed["valueType"] != "OBJECT":
        raise RuleViolation("whole relationship correction must contain an OBJECT")
    edge = typed["value"]
    key = relationship_key(edge)
    if key != parts[1]:
        raise RuleViolation("relationship identity cannot change under a stable key")
    other_type = edge.get("otherEntityType")
    if not isinstance(other_type, str) or other_type not in ENTITY_TYPES:
        raise RuleViolation("invalid relationship counterpart type")
    return key, other_type


def _active_corrections(corrections, pih, entity_type):
    records = list(corrections)
    by_id = {record.id: record for record in records}
    if len(by_id) != len(records):
        raise RuleViolation("duplicate correction ID")
    superseded = set()
    for record in records:
        if record.pih != pih or record.value_profile != PROFILE:
            raise LegacyProfileRequired("mixed history/legacy correction profiles")
        validate_typed_value({"valueType": "DATETIME", "value": record.corrected_at})
        if record.correction_type not in {"ADDITION", "CORRECTION", "CLARIFICATION"}:
            raise RuleViolation("unknown stored correction type")
        if not re.fullmatch("[0-9a-f]{64}", record.base_hash):
            raise RuleViolation("invalid stored baseHistoryViewHash")
        _field_set(record.fields, entity_type)
        if set(record.previous) != set(record.fields) or set(record.corrected) != set(record.fields):
            raise RuleViolation("correction map keys differ from correctedFields")
        for value in list(record.previous.values()) + list(record.corrected.values()):
            validate_typed_value(value)
        if record.supersedes is not None:
            predecessor = by_id.get(record.supersedes)
            if predecessor is None or predecessor.id in superseded:
                raise RuleViolation("missing/branching correction predecessor")
            if not set(record.fields) >= set(predecessor.fields):
                raise RuleViolation("partial supersession")
            # Check immutable identities across stored records without replaying
            # previousValue conditions or superseded property changes.
            for pointer in predecessor.fields:
                parts = parse_correction_path(pointer, entity_type)
                if (len(parts) == 2
                        and _relationship_correction_identity(parts, record.corrected.get(pointer))
                        != _relationship_correction_identity(parts, predecessor.corrected.get(pointer))):
                    raise RuleViolation("relationship identity cannot change across supersession")
            try:
                old_time = datetime.fromisoformat(predecessor.corrected_at.replace("Z", "+00:00"))
                new_time = datetime.fromisoformat(record.corrected_at.replace("Z", "+00:00"))
                if old_time.tzinfo is None or new_time.tzinfo is None or new_time <= old_time:
                    raise ValueError("not time-forward")
            except ValueError as error:
                raise RuleViolation("invalid correction time order") from error
            superseded.add(predecessor.id)
    for record in records:
        seen = set()
        while record is not None:
            if record.id in seen:
                raise RuleViolation("correction cycle")
            seen.add(record.id)
            record = by_id.get(record.supersedes)
    active = [record for record in records if record.id not in superseded]
    for index, left in enumerate(active):
        for right in active[index + 1:]:
            if any(paths_overlap(p, q) for p in left.fields for q in right.fields):
                raise RuleViolation("active corrections structurally overlap")
    return sorted(active, key=lambda record: (record.corrected_at, record.id))


def _projection(snapshot):
    return {"stateData": deepcopy(snapshot["stateData"]),
            "relationshipData": {relationship_key(edge): deepcopy(edge)
                                 for edge in snapshot["relationshipData"]}}


def _lookup(view, parts):
    current = view
    for part in parts:
        if not isinstance(current, dict) or part not in current:
            return False, None
        current = current[part]
    return True, current


def _overlay(view, parts, typed):
    parent = view
    for part in parts[:-1]:
        if part not in parent or not isinstance(parent[part], dict):
            raise RuleViolation("missing correction parent")
        parent = parent[part]
    if len(parts) == 2:
        identity = _relationship_correction_identity(parts, typed)
        if (parts[-1] in parent
                and identity != _relationship_correction_identity(
                    parts, {"valueType": "OBJECT", "value": parent[parts[-1]]})):
            raise RuleViolation("relationship identity cannot change")
        parent[parts[-1]] = deepcopy(typed["value"])
    else:
        parent[parts[-1]] = deepcopy(typed)


def build_history_view(snapshot, corrections=(), *, pih, snapshot_profile=PROFILE,
                       legacy_resolvers: Mapping[str, Callable] | None = None):
    """Absolute overlay, never reapply old previousValue to the original PiH.

    Legacy handlers receive copies and MUST implement their original profile.
    No default handler, alias rewrite or hash reinterpretation is supplied.
    """
    corrections = list(corrections)
    if snapshot_profile != PROFILE:
        resolver = (legacy_resolvers or {}).get(snapshot_profile)
        if resolver is None:
            raise LegacyProfileRequired("explicit legacy resolver required")
        return resolver(deepcopy(snapshot), deepcopy(corrections), pih=pih)
    validate_snapshot(snapshot)
    entity_type = snapshot["stateData"]["entityType"]
    active = _active_corrections(corrections, pih, entity_type)
    view = _projection(snapshot)
    for record in active:
        for pointer in record.fields:
            _overlay(view, parse_correction_path(pointer, entity_type), record.corrected[pointer])
    output = {"stateData": view["stateData"],
              "relationshipData": list(view["relationshipData"].values())}
    validate_snapshot(output)
    return _sorted_snapshot(output)


def validate_correction(snapshot, existing, candidate: HistoricalCorrectionRecord,
                        *, pih, expected_hash: str, snapshot_profile=PROFILE):
    """Return proposed effective view; callers must gate validation and commit."""
    if snapshot_profile != PROFILE or candidate.value_profile != PROFILE:
        raise LegacyProfileRequired("new correction requires matching reviewed profile")
    existing = list(existing)
    before = build_history_view(snapshot, existing, pih=pih)
    actual_hash = history_hash(before)
    if actual_hash != expected_hash or candidate.base_hash != actual_hash:
        raise RuleViolation("stale HistoryView hash")
    if candidate.pih != pih or candidate.id in {record.id for record in existing}:
        raise RuleViolation("wrong PiH or reused correction ID")
    entity_type = before["stateData"]["entityType"]
    _field_set(candidate.fields, entity_type)
    if set(candidate.previous) != set(candidate.fields) or set(candidate.corrected) != set(candidate.fields):
        raise RuleViolation("correction map keys differ from fields")
    if candidate.correction_type not in {"ADDITION", "CORRECTION", "CLARIFICATION"}:
        raise RuleViolation("unknown correction type")
    active = _active_corrections(existing, pih, entity_type)
    overlaps = [record for record in active if any(
        paths_overlap(p, q) for p in candidate.fields for q in record.fields)]
    if len(overlaps) > 1:
        raise RuleViolation("correction overlaps multiple active predecessors")
    if overlaps:
        if candidate.supersedes != overlaps[0].id or not set(candidate.fields) >= set(overlaps[0].fields):
            raise RuleViolation("overlap requires complete supersession of exactly one predecessor")
    elif candidate.supersedes is not None:
        raise RuleViolation("supersession without an overlapping active predecessor")
    view = _projection(before)
    for pointer in candidate.fields:
        previous, corrected = candidate.previous[pointer], candidate.corrected[pointer]
        validate_typed_value(previous)
        validate_typed_value(corrected)
        parts = parse_correction_path(pointer, entity_type)
        exists, old = _lookup(view, parts)
        if candidate.correction_type == "ADDITION":
            if exists or previous != NULL_VALUE:
                raise RuleViolation("ADDITION requires absence, not an existing NULL")
        else:
            if not exists:
                raise RuleViolation("correction target must exist")
            old_typed = {"valueType": "OBJECT", "value": old} if len(parts) == 2 else old
            if canonical_json(previous) != canonical_json(old_typed):
                raise RuleViolation("previousValue differs from effective history")
            if (len(parts) == 2
                    and _relationship_correction_identity(parts, corrected)
                    != _relationship_correction_identity(parts, old_typed)):
                raise RuleViolation("relationship identity differs from effective history")
    return build_history_view(snapshot, existing + [candidate], pih=pih)


@dataclass(frozen=True)
class GateState:
    """Pure protocol simulation. This is NOT an actual database lock."""
    epoch: int = 0
    owner: str | None = None
    fence: int = 0
    requests: Mapping[str, bytes] = field(default_factory=dict)
    successes: Mapping[str, tuple[str, Any]] = field(default_factory=dict)


def accept_request(state: GateState, key: str, payload) -> GateState:
    # Represents one atomic acceptance transaction in this state simulation.
    if state.owner is not None:
        raise RuleViolation("acceptance must wait for the common write gate")
    raw = canonical_json(payload)
    if not key:
        raise RuleViolation("empty idempotency key")
    if key in state.requests and state.requests[key] != raw:
        raise RuleViolation("idempotency key reused with another request")
    if key in state.requests:
        return state
    return replace(state, requests={**state.requests, key: raw}, epoch=state.epoch + 1)


def acquire_gate(state: GateState, run_id: str) -> GateState:
    if state.owner is not None or not run_id:
        raise RuleViolation("write gate already owned or invalid run")
    return replace(state, owner=run_id, fence=state.fence + 1)


def gate_commit(state: GateState, *, run_id: str, fence: int, expected_epoch: int,
                request_key: str, outcome, validate_at: Callable[[datetime], bool],
                decision_at: datetime) -> GateState:
    if state.owner != run_id or state.fence != fence:
        raise RuleViolation("lost run ownership")
    if request_key not in state.requests:
        raise RuleViolation("unbound request")
    if request_key in state.successes:
        raise RuleViolation("recover existing success; do not reapply request")
    if state.epoch != expected_epoch:
        raise RuleViolation("changed complete graph basis")
    if decision_at.tzinfo is None or not validate_at(decision_at):
        raise RuleViolation("final decision-time validation failed")
    return replace(state, owner=None, epoch=state.epoch + 1,
                   successes={**state.successes, request_key: (run_id, deepcopy(outcome))})


def gate_audit_append(state: GateState, *, run_id: str, fence: int) -> GateState:
    """Even revisions-neutral committed documentation changes the epoch."""
    if state.owner != run_id or state.fence != fence:
        raise RuleViolation("lost run ownership")
    return replace(state, epoch=state.epoch + 1, owner=None)


def release_gate(state: GateState, *, run_id: str, fence: int) -> GateState:
    if state.owner != run_id or state.fence != fence:
        raise RuleViolation("lost run ownership")
    return replace(state, owner=None)


def valid_ran_protection(
    *,
    status: str,
    protected_civ_ids: list[str],
    protected_pif2_ids: list[str],
    inscriptions: set[tuple[str, str]],
    governed_types: list[str],
    human_confirmed: bool = False,
    scope_compatible: bool = True,
) -> bool:
    """Structural primitive, not proof of human identity or approval authority.

    The final commit must use jci_approval's authenticated immutable receipts.
    An omitted historical human-confirmation input is deliberately fail-closed.
    """
    if status not in {"DRAFT", "ACTIVE"}:
        return False
    if not set(governed_types).issubset(RAN_GOVERNED_TYPES):
        return False
    if status == "DRAFT":
        return True
    if not (
        protected_civ_ids
        and protected_pif2_ids
        and governed_types
        and human_confirmed
        and scope_compatible
    ):
        return False
    return (
        all(
            any((civ_id, pif2_id) in inscriptions for pif2_id in protected_pif2_ids)
            for civ_id in protected_civ_ids
        )
        and all(
            any((civ_id, pif2_id) in inscriptions for civ_id in protected_civ_ids)
            for pif2_id in protected_pif2_ids
        )
    )
