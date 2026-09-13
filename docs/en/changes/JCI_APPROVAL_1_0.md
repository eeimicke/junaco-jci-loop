# Approval profile 1.0 – implementation and acceptance

[Documentation overview](../README.md) · [Deutsch](../../changes/JCI_APPROVAL_1_0.md)

## 1. Domain decision

The [canonical specification, section 12.9](../JCI_CONTEXT.md#129-verifiable-human-approval--profile-10) extends rule package 2.0 with verifiable human approvals. The ten core elements and 24 stored entity types remain unchanged. New `APPROVED_BY` separates approval from `REQUESTED_BY`; its only owner is the new immutable `ChangeEvent`. Higher future levels may now also have `ACCOUNTABLE_MEMBER`. Accountability alone grants no authority.

Task release starts at `PiF1o`. Only lack of authority permits escalation along every required `CONTRIBUTES_TO` branch, up to `PiF2`. Rejection and rule conflict cannot be bypassed by ascending. A specific human confirmation initiates normal SYNC processing; only its successful completion applies `ACTIVE` or `BLOCKED`. Completion and achievement remain separate.

## 2. Technical contract

- `approvalProfileVersion = "1.0"` is a required handler capability for protected changes, not a silent extension of older 2.0 implementations.
- The [approval envelope](../../schemas/jci-approval-envelope.schema.json), unchanged base request, exact hash binding, and time-limited authenticated receipts replace an asserted `human_confirmed = True`.
- Pending and rejection receipts are durable technical workflow data. The `ChangeEvent` and approval edges arise only on complete acceptance; appending approvals later is prohibited.
- `RaN.approvalPolicy` identifies exact roles and approval levels. Validation and authorization use the previously valid graph, not rights self-granted by the candidate.
- Value decisions consider every affected previous and candidate CiV holder. Enrollment authority explicitly established by a human addresses only initial setup before the first responsible policy; its disablement remains permanent.
- [Reference validation](../../../reference/jci_approval.py) and [tests](../../../tests/test_approval_rules.py) implement decision logic. Production identity verification, durable persistence, and real Neo4j transactions still require a trusted adapter.

## 3. Adoption without invented history

1. Preserve existing data, events, and hashes. Do not invent approvals retrospectively.
2. Explicitly register human identities and, where necessary, narrowly scoped enrollment authority; the technical root is not a human approver.
3. Explicitly establish required accountabilities and RaN approval policies. Display missing contacts or authority as model gaps.
4. Deploy a profile-capable, checksum-bound handler package and shared commit gate. Reject unknown profiles and direct bypass attempts.
5. Check receipts, deadlines, changed grounds, rejections, and retries before enabling a production write path.

## 4. Acceptance and remaining findings

Acceptance covers local approval, bounded escalation, multiple future branches, missing accountability, human rejection, technical identities, expired roles and receipts, changed requests and policies, idempotency, and separation of approval from completion. The same validation applies again at the protected decision point.

Of the six discussed findings, this change particularly addresses human confirmation and the approval portion of RaN execution. It does not claim a complete general RaN grammar. Historical removal corrections, ownership collisions involving terminal `GOVERNS` targets, general DRAFT cardinalities, and full snapshot/Neo4j model validation remain separately open. The repository remains a model with executable reference checks, not a finished production SYNC engine.
