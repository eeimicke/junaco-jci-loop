# Governance of the JCI repository

> Controlled English translation of `GOVERNANCE.md`.

## 1. Purpose

This document governs how changes to the JCI model specification are proposed, reviewed, and accepted. `docs/JCI_CONTEXT.md` is the canonical domain source.

## 2. Current single-maintainer operation

Domain and technical approval currently rest with the repository owner. Even self-authored changes should use a branch and pull request so rationale and validation remain traceable. A second human approval is not mandatory in single-maintainer operation. Administrative bypass is limited to restoring a working repository configuration and must be explained.

## 3. Change classes

| Class | Meaning | Required review |
|---|---|---|
| Editorial | spelling, formatting, or links without semantic change | formal check and self-review |
| Clarification | clearer wording with unchanged semantics | comparison with the whole specification |
| Semantic | changes to elements, relationships, cardinalities, or rules | full model and dependency review |
| Rights | licence, source, or rights attribution change | separate rights review |

New core elements and changes to history, synchronisation, or rights architecture are always semantic changes.

## 4. Decision path

```text
proposal → domain rationale → affected model review → consistency and rights review
→ documented decision → canonical specification change
```

Automation may report formal errors and possible conflicts. It never decides domain correctness.

## 5. Third-party contributions

External contributors may submit issues and proposals. Creative model content is accepted only after origin, ownership, and permission under the applicable licence are documented. Submission alone transfers no rights. Separate written rights are required if JUNACO is to license a contribution commercially.

## 6. Multi-maintainer transition

When at least two permanent approvers exist, governance should add approval by another person, mandatory code-owner review, dismissal of stale approvals after new commits, and separate approval for licence and rights changes.

