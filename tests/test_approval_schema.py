"""Approval-profile transport and snapshot-schema regressions.

These tests cover closed JSON shapes. Hash equality, receipt uniqueness by
RoleAssignment, expiry, route completeness, and attestation authenticity remain
semantic gate checks because JSON Schema cannot derive graph state or compare
arbitrary sibling values.
"""

from copy import deepcopy
import json
from pathlib import Path
import unittest

from jsonschema import Draft202012Validator, FormatChecker, ValidationError
from referencing import Registry, Resource


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_DIR = ROOT / "docs" / "schemas"

REQUEST_ID = "11111111-1111-4111-8111-111111111111"
ROLE_ID = "22222222-2222-4222-8222-222222222222"
MEMBER_ID = "33333333-3333-4333-8333-333333333333"
RECEIPT_ID = "44444444-4444-4444-8444-444444444444"
POLICY_ROLE_ID = "55555555-5555-4555-8555-555555555555"
REQUEST_HASH = "a" * 64
CONTEXT_HASH = "b" * 64


def load_schema(name: str) -> dict:
    return json.loads((SCHEMA_DIR / name).read_text(encoding="utf-8"))


def validator_for(schema: dict, *referenced_schemas: dict) -> Draft202012Validator:
    registry = Registry()
    for referenced in referenced_schemas:
        registry = registry.with_resource(
            referenced["$id"], Resource.from_contents(referenced)
        )
    return Draft202012Validator(
        schema, registry=registry, format_checker=FormatChecker()
    )


def proposal() -> dict:
    return {
        "schemaVersion": "2.0",
        "requestId": REQUEST_ID,
        "idempotencyKey": "approval-schema-test",
        "requestedAt": "2026-09-08T10:00:00Z",
        "requestedRevision": 1,
        "changeType": "CHANGED",
        "target": {"id": REQUEST_ID, "entityType": "Task"},
        "requestedByRoleAssignmentId": ROLE_ID,
        "reason": "Release the reviewed task",
        "operations": [
            {
                "op": "REPLACE",
                "path": "/status",
                "value": {"valueType": "STRING", "value": "ACTIVE"},
            }
        ],
    }


def receipt() -> dict:
    return {
        "receiptId": RECEIPT_ID,
        "requestHash": REQUEST_HASH,
        "contextHash": CONTEXT_HASH,
        "decidedAt": "2026-09-08T10:01:00Z",
        "validUntil": "2026-09-08T10:06:00Z",
        "outcome": "APPROVED",
        "roleAssignmentId": ROLE_ID,
        "memberId": MEMBER_ID,
        "attestation": "trusted-adapter:opaque-proof",
    }


def envelope() -> dict:
    return {
        "approvalProfileVersion": "1.0",
        "decisionKey": "Task.action.RELEASE",
        "proposal": proposal(),
        "requestHash": REQUEST_HASH,
        "contextHash": CONTEXT_HASH,
        "receipts": [receipt()],
    }


def policy_snapshot(mode: str, levels=None) -> dict:
    value = {
        "profileVersion": "1.0",
        "mode": mode,
        "roleIds": [POLICY_ROLE_ID],
    }
    if levels is not None:
        value["levels"] = levels
    return {
        "stateData": {
            "entityType": "RaN",
            "revision": 1,
            "properties": {
                "name": {"valueType": "STRING", "value": "Release approval"},
                "status": {"valueType": "STRING", "value": "ACTIVE"},
                "approvalPolicy": {"valueType": "OBJECT", "value": value},
            },
        },
        "relationshipData": [],
    }


def has_default(value) -> bool:
    if isinstance(value, dict):
        return "default" in value or any(has_default(item) for item in value.values())
    if isinstance(value, list):
        return any(has_default(item) for item in value)
    return False


class ApprovalEnvelopeSchemaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.request_schema = load_schema("jci-change-request.schema.json")
        cls.envelope_schema = load_schema("jci-approval-envelope.schema.json")
        cls.validator = validator_for(cls.envelope_schema, cls.request_schema)

    def assert_invalid(self, candidate: dict):
        with self.assertRaises(ValidationError):
            self.validator.validate(candidate)

    def test_complete_envelope_is_valid_and_base_request_stays_2_0(self):
        self.validator.validate(envelope())
        self.assertEqual(
            self.envelope_schema["properties"]["proposal"]["$ref"],
            "jci-change-request.schema.json",
        )
        candidate = envelope()
        candidate["proposal"]["approvalProfileVersion"] = "1.0"
        self.assert_invalid(candidate)

    def test_envelope_is_closed_and_every_top_level_field_is_required(self):
        for field in self.envelope_schema["required"]:
            with self.subTest(missing=field):
                candidate = envelope()
                del candidate[field]
                self.assert_invalid(candidate)

        candidate = envelope()
        candidate["implicitApproval"] = True
        self.assert_invalid(candidate)

    def test_receipt_is_closed_and_every_field_is_required(self):
        required = self.envelope_schema["$defs"]["approvalReceipt"]["required"]
        for field in required:
            with self.subTest(missing=field):
                candidate = envelope()
                del candidate["receipts"][0][field]
                self.assert_invalid(candidate)

        candidate = envelope()
        candidate["receipts"][0]["humanConfirmed"] = True
        self.assert_invalid(candidate)

    def test_invalid_profile_keys_hashes_identity_time_and_attestation_are_rejected(self):
        mutations = (
            ("approvalProfileVersion", "2.0"),
            ("decisionKey", "Task.action.COMPLETE"),
            ("requestHash", "A" * 64),
            ("contextHash", "short"),
        )
        for field, value in mutations:
            with self.subTest(field=field):
                candidate = envelope()
                candidate[field] = value
                self.assert_invalid(candidate)

        receipt_mutations = (
            ("receiptId", "not-a-uuid"),
            ("roleAssignmentId", "NOT-A-UUID"),
            ("memberId", "not-a-uuid"),
            ("decidedAt", "2026-09-08T10:01:00"),
            ("validUntil", "2026-09-08"),
            ("outcome", "ACCEPTED"),
            ("attestation", "   "),
        )
        for field, value in receipt_mutations:
            with self.subTest(receipt_field=field):
                candidate = envelope()
                candidate["receipts"][0][field] = value
                self.assert_invalid(candidate)

    def test_receipts_are_nonempty_and_exact_duplicates_are_rejected(self):
        candidate = envelope()
        candidate["receipts"] = []
        self.assert_invalid(candidate)

        candidate = envelope()
        candidate["receipts"].append(deepcopy(candidate["receipts"][0]))
        self.assert_invalid(candidate)

    def test_schema_intentionally_defines_no_defaults(self):
        self.assertFalse(has_default(self.envelope_schema))


class ApprovalPolicySnapshotSchemaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.snapshot_schema = load_schema("jci-history-snapshot.schema.json")
        cls.validator = validator_for(cls.snapshot_schema)

    def assert_invalid(self, candidate: dict):
        with self.assertRaises(ValidationError):
            self.validator.validate(candidate)

    def test_chain_requires_nonempty_unique_levels(self):
        self.validator.validate(
            policy_snapshot("ACCOUNTABLE_CHAIN", ["PiF1o", "PiF1t", "PiF2"])
        )
        for levels in (None, [], ["PiF1o", "PiF1o"], ["Task"]):
            with self.subTest(levels=levels):
                self.assert_invalid(policy_snapshot("ACCOUNTABLE_CHAIN", levels))

    def test_value_scope_allows_only_absent_or_empty_levels(self):
        self.validator.validate(policy_snapshot("VALUE_SCOPE"))
        self.validator.validate(policy_snapshot("VALUE_SCOPE", []))
        self.assert_invalid(policy_snapshot("VALUE_SCOPE", ["PiF2"]))

    def test_policy_is_closed_and_has_no_implicit_roles_or_profile(self):
        for field in ("profileVersion", "mode", "roleIds"):
            with self.subTest(missing=field):
                candidate = policy_snapshot("VALUE_SCOPE")
                del candidate["stateData"]["properties"]["approvalPolicy"]["value"][field]
                self.assert_invalid(candidate)

        candidate = policy_snapshot("VALUE_SCOPE")
        candidate["stateData"]["properties"]["approvalPolicy"]["value"]["roleIds"] = []
        self.assert_invalid(candidate)

        candidate = policy_snapshot("VALUE_SCOPE")
        candidate["stateData"]["properties"]["approvalPolicy"]["value"]["fallback"] = True
        self.assert_invalid(candidate)

        candidate = policy_snapshot("VALUE_SCOPE")
        candidate["stateData"]["properties"]["approvalPolicy"]["implicit"] = True
        self.assert_invalid(candidate)

    def test_approval_policy_is_ran_only_and_typed_as_object(self):
        candidate = policy_snapshot("VALUE_SCOPE")
        candidate["stateData"]["entityType"] = "Task"
        self.assert_invalid(candidate)

        candidate = policy_snapshot("VALUE_SCOPE")
        candidate["stateData"]["properties"]["approvalPolicy"]["valueType"] = "STRING"
        self.assert_invalid(candidate)

    def test_source_owned_approval_edges_are_not_snapshot_or_request_operations(self):
        request_schema = load_schema("jci-change-request.schema.json")
        request_relations = request_schema["$defs"]["operation"]["properties"][
            "relationshipType"
        ]["enum"]
        snapshot_relations = self.snapshot_schema["properties"]["relationshipData"][
            "items"
        ]["properties"]["relationshipType"]["enum"]
        self.assertNotIn("APPROVED_BY", request_relations)
        self.assertNotIn("APPROVED_BY", snapshot_relations)
        self.assertFalse(has_default(self.snapshot_schema["$defs"]["approvalPolicy"]))


if __name__ == "__main__":
    unittest.main()
