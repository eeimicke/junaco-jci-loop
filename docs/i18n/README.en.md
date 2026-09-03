# Translation rules

## Authority

- [`docs/JCI_CONTEXT.md`](../JCI_CONTEXT.md) is the canonical domain source.
- Files below `docs/en/` are controlled English translations.
- A translation must not add, remove, or reinterpret any entity, relationship, cardinality, or rule.
- Canonical identifiers such as `PiF1o`, `RoleAssignment`, `EXECUTED_BY`, and status values are not translated.
- Technical artifacts are not duplicated.

## Structural equivalence

German is the canonical language. Every English version listed in the
translation manifest must be structurally equivalent to its German source.
Structural equivalence means:

1. the same chapters and subsections in the same order,
2. the same heading levels,
3. the same tables with the same number and order of rows and columns,
4. the same code and Mermaid blocks at the same semantic position,
5. the same examples, rules, and exceptions, and
6. the same canonical JCI identifiers, cardinalities, and status values.

Only explanatory prose is translated. An English summary is not a translation
of the complete German source. Additional legal notices may appear outside the
mirrored document body only when the translation manifest explicitly declares
that exception.

## Maintenance

A change to a German source initially changes its translation status to
`review-required`. The status may return to `synchronized` only after a full
structural and semantic comparison. Automated tests compare file pairs,
heading structure, table structure, code blocks, entity types, relationships,
and Mermaid blocks.

Reader-facing Markdown files normally have a language pair recorded in the
manifest. Deliberately bilingual single files, such as the repository landing
page, and language-neutral technical artifacts are recorded as exceptions.
JSON schemas, JSON-LD contexts, tests, workflows, and canonical Mermaid sources
are not duplicated. User-facing explanatory text in those artifacts must be
language-neutral or maintained bilingually.

Legal translations are marked as non-binding reading aids. The German version
or the linked legally binding license text remains authoritative.
