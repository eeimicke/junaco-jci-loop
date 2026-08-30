import json
import re
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker, ValidationError


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
TRANSLATION_MANIFEST = DOCS / "i18n" / "translation-manifest.json"

ENTITY_TYPES = {
    "PiH", "CiV", "RaN", "SYNC", "PiF2", "PiF1s", "PiF1t", "PiF1o",
    "RoFOrg", "RoFOrgRelationship", "RoFTeam", "RoFTeamMember", "RoFRole",
    "RoleAssignment", "Task", "SuccessCriterion", "Result", "Verification",
    "Evidence", "ERoFObject", "ChangeEvent", "SyncEvent", "RaNConflict",
    "HistoricalCorrection",
}

RELATIONSHIPS = {
    "PROVIDES_CONTEXT_TO", "INSCRIBES_PURPOSE_IN", "CONTRIBUTES_TO",
    "HAS_SUCCESS_CRITERIA", "ACCOUNTABLE_MEMBER", "DECOMPOSES_INTO",
    "DEPENDS_ON", "RESPONSIBLE_TEAM", "EXECUTED_BY", "USES", "PRODUCES",
    "EVALUATES", "CHECKS", "USES_EVIDENCE", "SUPERSEDES", "HAS_TEAM",
    "HAS_MEMBER", "HAS_ROLE", "HAS_ASSIGNMENT", "IN_TEAM", "ACTIVATES_ROLE",
    "SOURCE_ORG", "TARGET_ORG", "REPRESENTED_BY", "OWNED_BY", "GOVERNS",
    "APPLIES_IN", "CONFLICTING_RULE", "AFFECTS", "DETECTED_BY", "RESOLVED_BY",
    "RESOLVED_THROUGH", "CREATED_BY", "REQUESTED_BY", "CORRECTED_BY",
    "CHANGED_BY", "TRIGGERS", "EXECUTES", "REPLACED_BY",
    "HAS_HISTORICAL_STATE", "CREATES_HISTORY", "CORRECTS", "CAUSED_BY",
    "CREATES_CORRECTION", "TARGETS_HISTORY",
}


def read(name: str) -> str:
    return (DOCS / name).read_text(encoding="utf-8")


def heading_signature(content: str) -> list[tuple[int, str | None]]:
    """Return heading levels and stable numeric section identifiers."""
    signature = []
    for hashes, title in re.findall(r"(?m)^(#{1,6})\s+(.+?)\s*$", content):
        number = re.match(r"(\d+(?:\.\d+)*)\b", title)
        signature.append((len(hashes), number.group(1) if number else None))
    return signature


def table_signature(content: str) -> list[tuple[int, tuple[int, ...]]]:
    """Return row and column counts for each Markdown table in document order."""
    tables = []
    current = []
    for line in content.splitlines() + [""]:
        if line.lstrip().startswith("|") and line.rstrip().endswith("|"):
            current.append(line.count("|") - 1)
        elif current:
            tables.append((len(current), tuple(current)))
            current = []
    return tables


def fenced_block_signature(content: str) -> list[str]:
    """Return fence languages in their original document order."""
    return re.findall(r"(?m)^```([^\s`]*)\s*$", content)[::2]


class SpecificationConsistencyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.context = read("JCI_CONTEXT.md")
        cls.ontology = read("JCI_ONTOLOGY.md")
        cls.rules = read("JCI_GRAPH_RULES.md")
        cls.sync = read("JCI_SYNC_SPEC.md")
        cls.neo4j = read("implementations/neo4j/JCI_NEO4J_SCHEMA.md")

    def test_every_entity_is_in_context_and_ontology(self):
        for entity in ENTITY_TYPES:
            with self.subTest(entity=entity):
                self.assertIn(f"`{entity}`", self.context)
                self.assertRegex(self.ontology, rf"\b{re.escape(entity)}\b")

    def test_every_relationship_is_canonical_and_implemented(self):
        combined_implementation = self.ontology + self.rules + self.sync + self.neo4j
        for relationship in RELATIONSHIPS:
            with self.subTest(relationship=relationship):
                self.assertIn(relationship, self.context)
                self.assertIn(relationship, combined_implementation)

    def test_required_structured_types_exist(self):
        for type_name in (
            "TypedValue", "StateSnapshot", "RelationshipSnapshot",
            "TypedValueMap", "RuleExpression", "SyncDefinition",
        ):
            self.assertIn(type_name, self.context)

    def test_neo4j_validates_complete_sync_event_result(self):
        """The Neo4j projection must enforce every canonical SyncEvent result field."""
        required_properties = (
            "startedAt", "completedAt", "outcome", "affectedCount",
            "changedCount", "historyCount", "correctionCount", "conflictCount",
        )
        for property_name in required_properties:
            with self.subTest(property=property_name):
                self.assertIn(
                    f"event.{property_name} IS NULL",
                    self.neo4j,
                    f"Explizite Nullprüfung für SyncEvent.{property_name} fehlt",
                )

        graph_derived_counts = {
            "affectedCount": "actualAffectedCount",
            "historyCount": "actualHistoryCount",
            "correctionCount": "actualCorrectionCount",
            "conflictCount": "actualConflictCount",
        }
        for stored, actual in graph_derived_counts.items():
            with self.subTest(count=stored):
                self.assertIn(f"event.{stored} <> {actual}", self.neo4j)

        self.assertIn("deduplizierten Transaktions-Write-Set", self.neo4j)
        self.assertIn("zählen nicht zu `changedCount`", self.neo4j)
        self.assertNotIn("[:CHANGES]", self.neo4j)

    def test_six_clarified_invariants_are_projected_across_specifications(self):
        """Every normative layer must retain the six clarified model decisions."""
        normative_layers = {
            "context": self.context,
            "ontology": self.ontology,
            "graph rules": self.rules,
            "sync specification": self.sync,
            "Neo4j projection": self.neo4j,
        }
        required_terms = (
            "runId",
            "requestedRevision",
            "TARGETS_HISTORY",
            "evaluatedResultRevision",
            "checkedCriterionRevision",
            "bootstrapKey",
            "baseHistoryViewHash",
            "correctedFields",
            "HistoryView",
        )
        for layer_name, content in normative_layers.items():
            for term in required_terms:
                with self.subTest(layer=layer_name, term=term):
                    self.assertIn(term, content)

        schema_dir = DOCS / "schemas"
        request_schema = (schema_dir / "jci-change-request.schema.json").read_text(
            encoding="utf-8"
        )
        result_schema = (schema_dir / "jci-sync-result.schema.json").read_text(
            encoding="utf-8"
        )
        jsonld_context = (schema_dir / "jci-context.jsonld").read_text(
            encoding="utf-8"
        )
        for term in (
            "idempotencyKey",
            "requestedRevision",
            "expectedHistoryViewHash",
            "correctedFields",
        ):
            with self.subTest(exchange_schema="request", term=term):
                self.assertIn(term, request_schema)
        for term in ("runId", "affectedEntityIds", "conflictIds"):
            with self.subTest(exchange_schema="result", term=term):
                self.assertIn(term, result_schema)
        for term in (
            "runId",
            "requestedRevision",
            "evaluatedResultRevision",
            "checkedCriterionRevision",
            "bootstrapKey",
            "baseHistoryViewHash",
        ):
            with self.subTest(exchange_schema="jsonld", term=term):
                self.assertIn(term, jsonld_context)

    def test_core_chapters_have_examples(self):
        for chapter in range(3, 13):
            pattern = rf"## {chapter}\..*?(?=\n## {chapter + 1}\.|\Z)"
            match = re.search(pattern, self.context, flags=re.S)
            self.assertIsNotNone(match, f"Kapitel {chapter} fehlt")
            self.assertIn("Beispiel", match.group(0), f"Kapitel {chapter} hat kein Beispiel")

    def test_resolved_open_items_are_not_listed(self):
        stale = (
            "Priorisierung konkurrierender `RaN`",
            "vollständige Traversierungsmatrix je Entitäts- und Beziehungstyp",
            "semantische Abbruchgrenzen für sehr große Graphen",
            "technische Repräsentation komplexer historischer Eigenschaften",
        )
        for phrase in stale:
            self.assertNotIn(phrase, self.sync + self.neo4j)

    def test_no_merge_markers(self):
        for path in DOCS.rglob("*.md"):
            content = path.read_text(encoding="utf-8")
            self.assertNotRegex(content, r"(?m)^(<<<<<<<|=======|>>>>>>>)")

    def test_machine_readable_schemas_are_valid_json(self):
        expected = {
            "jci-change-request.schema.json",
            "jci-sync-result.schema.json",
            "jci-context.jsonld",
        }
        schema_dir = DOCS / "schemas"
        self.assertTrue(expected.issubset({path.name for path in schema_dir.iterdir()}))
        for name in expected:
            with self.subTest(schema=name):
                data = json.loads((schema_dir / name).read_text(encoding="utf-8"))
                self.assertIsInstance(data, dict)
                self.assertIn("@context" if name.endswith(".jsonld") else "$schema", data)

    def test_exchange_schemas_are_valid_and_enforce_conditional_invariants(self):
        """Version 1.1 must distinguish create, correction and run outcomes."""
        schema_dir = DOCS / "schemas"
        request_schema = json.loads(
            (schema_dir / "jci-change-request.schema.json").read_text(encoding="utf-8")
        )
        result_schema = json.loads(
            (schema_dir / "jci-sync-result.schema.json").read_text(encoding="utf-8")
        )
        Draft202012Validator.check_schema(request_schema)
        Draft202012Validator.check_schema(result_schema)
        request_validator = Draft202012Validator(
            request_schema, format_checker=FormatChecker()
        )
        result_validator = Draft202012Validator(
            result_schema, format_checker=FormatChecker()
        )

        base_request = {
            "schemaVersion": "1.1",
            "requestId": "11111111-1111-4111-8111-111111111111",
            "idempotencyKey": "create-task-1",
            "requestedAt": "2026-08-30T10:00:00+02:00",
            "requestedRevision": None,
            "changeType": "CREATED",
            "target": {
                "id": "22222222-2222-4222-8222-222222222222",
                "entityType": "Task",
            },
            "requestedByRoleAssignmentId": "33333333-3333-4333-8333-333333333333",
            "reason": "Neuen atomaren Task anlegen",
            "operations": [
                {
                    "op": "ADD",
                    "path": "/name",
                    "value": {"valueType": "STRING", "value": "API erweitern"},
                }
            ],
        }
        request_validator.validate(base_request)

        invalid_created = dict(base_request, requestedRevision=1)
        with self.assertRaises(ValidationError):
            request_validator.validate(invalid_created)

        value = {"valueType": "STRING", "value": "Team A"}
        correction_request = {
            **base_request,
            "idempotencyKey": "correct-history-1",
            "requestedRevision": 1,
            "changeType": "HISTORICAL_CORRECTION",
            "target": {
                "id": "44444444-4444-4444-8444-444444444444",
                "entityType": "PiH",
            },
            "historicalCorrection": {
                "correctionType": "ADDITION",
                "reason": "Historische Teamzuordnung belegt",
                "valueSchemaVersion": "1.0",
                "expectedHistoryViewHash": "a" * 64,
                "correctedFields": ["/stateData/team"],
                "previousValue": {
                    "/stateData/team": {"valueType": "NULL", "value": None}
                },
                "correctedValue": {"/stateData/team": value},
            },
        }
        correction_request.pop("operations")
        request_validator.validate(correction_request)

        invalid_correction = dict(correction_request, operations=base_request["operations"])
        with self.assertRaises(ValidationError):
            request_validator.validate(invalid_correction)

        base_result = {
            "schemaVersion": "1.1",
            "requestId": base_request["requestId"],
            "runId": "55555555-5555-4555-8555-555555555555",
            "syncEventId": "66666666-6666-4666-8666-666666666666",
            "outcome": "FAILED",
            "completedAt": "2026-08-30T10:01:00+02:00",
            "affectedCount": 0,
            "changedCount": 0,
            "historyCount": 0,
            "correctionCount": 0,
            "conflictCount": 0,
            "affectedEntityIds": [],
            "conflictIds": [],
            "errors": [{"code": "TARGET_UNRESOLVED", "message": "Ziel nicht auflösbar"}],
        }
        result_validator.validate(base_result)

        invalid_success = dict(base_result, outcome="SUCCESS", errors=[])
        with self.assertRaises(ValidationError):
            result_validator.validate(invalid_success)

    def test_public_jsonld_namespace_matches_vocabulary_page(self):
        namespace = "https://eeimicke.github.io/junaco-jci-loop/ns/jci/1.0#"
        context = json.loads((DOCS / "schemas/jci-context.jsonld").read_text(encoding="utf-8"))
        self.assertEqual(context["@context"]["@vocab"], namespace)
        self.assertEqual(context["@context"]["jci"], namespace)

        vocabulary_page = DOCS / "ns/jci/1.0/index.html"
        self.assertTrue(vocabulary_page.is_file())
        page = vocabulary_page.read_text(encoding="utf-8")
        self.assertIn(namespace, page)
        for term in ENTITY_TYPES | RELATIONSHIPS:
            with self.subTest(vocabulary_term=term):
                self.assertIn(f"<code>{term}</code>", page)

    def test_markdown_tables_have_consistent_column_counts(self):
        for path in DOCS.rglob("*.md"):
            expected = None
            for line_number, line in enumerate(
                path.read_text(encoding="utf-8").splitlines(), start=1
            ):
                is_table_row = line.lstrip().startswith("|") and line.rstrip().endswith("|")
                if not is_table_row:
                    expected = None
                    continue
                column_markers = line.count("|")
                if expected is None:
                    expected = column_markers
                self.assertEqual(
                    expected,
                    column_markers,
                    f"Uneinheitliche Markdown-Tabelle in {path}:{line_number}",
                )

    def test_translation_manifest_is_complete_and_resolvable(self):
        manifest = json.loads(TRANSLATION_MANIFEST.read_text(encoding="utf-8"))
        self.assertEqual(manifest["canonicalLanguage"], "de")
        self.assertEqual(manifest["translationLanguage"], "en")
        self.assertEqual(manifest["canonicalModel"], "docs/JCI_CONTEXT.md")

        seen_sources = set()
        seen_targets = set()
        for pair in manifest["pairs"]:
            with self.subTest(pair=pair):
                self.assertIn(pair["status"], {"synchronized", "review-required"})
                source = ROOT / pair["source"]
                target = ROOT / pair["target"]
                self.assertTrue(source.is_file(), f"Fehlende deutsche Quelle: {source}")
                self.assertTrue(target.is_file(), f"Fehlende englische Fassung: {target}")
                self.assertNotIn(pair["source"], seen_sources)
                self.assertNotIn(pair["target"], seen_targets)
                seen_sources.add(pair["source"])
                seen_targets.add(pair["target"])

    def test_synchronized_translations_are_structurally_equivalent(self):
        manifest = json.loads(TRANSLATION_MANIFEST.read_text(encoding="utf-8"))
        for pair in manifest["pairs"]:
            if pair["status"] != "synchronized":
                continue
            source = (ROOT / pair["source"]).read_text(encoding="utf-8")
            target = (ROOT / pair["target"]).read_text(encoding="utf-8")
            with self.subTest(pair=pair):
                self.assertEqual(heading_signature(source), heading_signature(target))
                self.assertEqual(table_signature(source), table_signature(target))
                self.assertEqual(fenced_block_signature(source), fenced_block_signature(target))

    def test_reader_facing_markdown_is_manifested_or_declared_bilingual(self):
        manifest = json.loads(TRANSLATION_MANIFEST.read_text(encoding="utf-8"))
        manifested = {
            entry[key]
            for entry in manifest["pairs"]
            for key in ("source", "target")
        }
        deliberate_single_files = {
            "README.md",
            ".github/pull_request_template.md",
        }
        markdown = {
            path.relative_to(ROOT).as_posix()
            for path in ROOT.rglob("*.md")
            if ".git" not in path.parts
        }
        self.assertFalse(
            markdown - manifested - deliberate_single_files,
            "Markdown-Dateien ohne Übersetzungspaar oder erklärte Ausnahme",
        )

    def test_translations_preserve_canonical_identifiers(self):
        manifest = json.loads(TRANSLATION_MANIFEST.read_text(encoding="utf-8"))
        technical_terms = ENTITY_TYPES | RELATIONSHIPS
        for pair in manifest["pairs"]:
            source = (ROOT / pair["source"]).read_text(encoding="utf-8")
            target = (ROOT / pair["target"]).read_text(encoding="utf-8")
            required = {term for term in technical_terms if term in source}
            with self.subTest(target=pair["target"]):
                self.assertFalse(
                    required - {term for term in technical_terms if term in target},
                    f"Kanonische Bezeichner fehlen in {pair['target']}",
                )

    def test_local_markdown_links_resolve(self):
        link_pattern = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
        roots = [ROOT / name for name in (
            "README.md", "LICENSE.md", "NOTICE.md", "GOVERNANCE.md",
            "CONTRIBUTING.md", "AGENTS.md", "LICENSE.en.md", "NOTICE.en.md",
            "GOVERNANCE.en.md", "CONTRIBUTING.en.md", "AGENTS.en.md",
        )]
        markdown_files = [path for path in roots if path.is_file()]
        markdown_files.extend(DOCS.rglob("*.md"))

        for path in markdown_files:
            content = path.read_text(encoding="utf-8")
            for raw_target in link_pattern.findall(content):
                target = raw_target.strip().strip("<>").split("#", 1)[0]
                if not target or re.match(r"^(https?://|mailto:)", target):
                    continue
                resolved = (path.parent / target).resolve()
                with self.subTest(path=path, target=raw_target):
                    self.assertTrue(resolved.exists(), f"Toter lokaler Link: {path} -> {raw_target}")

    def test_mermaid_sources_use_only_canonical_relationships(self):
        diagram_dir = DOCS / "diagrams" / "sources"
        self.assertTrue(diagram_dir.is_dir())
        for path in diagram_dir.glob("*.mmd"):
            content = path.read_text(encoding="utf-8")
            self.assertRegex(content, r"(?m)^flowchart\s+(TD|TB|LR|RL|BT)$")
            labels = re.findall(r"\|([A-Z][A-Z_]+)\|", content)
            with self.subTest(diagram=path.name):
                self.assertFalse(
                    set(labels) - RELATIONSHIPS,
                    f"Nicht kanonische Beziehungen in {path.name}",
                )

    def test_complete_example_covers_entities_rules_and_sync_outcomes(self):
        required_terms = ENTITY_TYPES | {
            "RULE", "NORM", "POLICY", "CONSTRAINT", "LAW",
            "REQUIRE", "PROHIBIT", "PERMIT",
            "GLOBAL", "ORGANIZATION", "TEAM", "ENTITY",
            "PRIORITY_TIE", "UNEVALUABLE",
            "SUCCESS", "CONFLICT", "FAILED",
        }
        examples = (
            DOCS / "guides" / "JCI_EXAMPLE.md",
            DOCS / "en" / "guides" / "JCI_EXAMPLE.md",
        )
        for path in examples:
            content = path.read_text(encoding="utf-8")
            with self.subTest(example=path):
                missing = {term for term in required_terms if term not in content}
                self.assertFalse(missing, f"Begriffe fehlen in {path}: {sorted(missing)}")

    def test_complete_example_diagram_sources_exist(self):
        expected = {
            "example-complete-entity-map.mmd",
            "example-purpose-future.mmd",
            "example-organisation.mmd",
            "example-task-execution.mmd",
            "example-environment.mmd",
            "example-ran-types.mmd",
            "example-ran-conflict.mmd",
            "example-sync-outcomes.mmd",
            "example-history-correction.mmd",
        }
        diagram_dir = DOCS / "diagrams" / "sources"
        self.assertTrue(expected.issubset({path.name for path in diagram_dir.glob("*.mmd")}))

    def test_complete_example_language_versions_are_structurally_synchronized(self):
        german = (DOCS / "guides" / "JCI_EXAMPLE.md").read_text(encoding="utf-8")
        english = (DOCS / "en" / "guides" / "JCI_EXAMPLE.md").read_text(encoding="utf-8")
        german_chapters = re.findall(r"(?m)^## (\d+)\.", german)
        english_chapters = re.findall(r"(?m)^## (\d+)\.", english)
        self.assertEqual(german_chapters, english_chapters)
        self.assertEqual(german_chapters, [str(number) for number in range(1, 14)])

        german_relationships = {term for term in RELATIONSHIPS if term in german}
        english_relationships = {term for term in RELATIONSHIPS if term in english}
        self.assertEqual(german_relationships, english_relationships)


if __name__ == "__main__":
    unittest.main()
