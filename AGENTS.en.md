# Working rules for agents

> Controlled English translation of `AGENTS.md`. The German file controls agent behaviour in this repository.

## Canonical source

Read `docs/JCI_CONTEXT.md` completely before any content change. It is the canonical specification of the JUNACO Continuous Integration Model for Organisations and the JCI Loop.

## Domain rules

- Never silently invent, remove, or reinterpret core elements, graph objects, relationships, or cardinalities.
- Identify affected elements, relationships, and rules before semantic change.
- Report conflicts with the canonical specification before changing the model.
- Check impacts on all ten core elements and preserve Task-to-`CiV` traceability.
- Do not replace human model decisions with automated assumptions.

## Change discipline

- Use a dedicated branch and pull request.
- Explain domain changes and execute automated checks.
- Do not publish, push, or merge without explicit instruction.
- Change `LICENSE.md`, `NOTICE.md`, `GOVERNANCE.md`, and `.github/CODEOWNERS` only on explicit instruction.

## Rights and sources

Identify third-party content and sources, do not assume rights, clarify external model contributions before acceptance, and observe the separation between model, thesis, software, applications, and third-party material in `LICENSE.md`.

