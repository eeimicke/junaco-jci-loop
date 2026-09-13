import unittest
from pathlib import Path

import yaml

from reference import jci_rules


ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = ROOT / "model" / "jci-model.yaml"


class YamlModelConsistencyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with MODEL_PATH.open(encoding="utf-8") as stream:
            cls.model = yaml.safe_load(stream)

    def test_stored_entity_types_match_reference(self):
        non_node_elements = set(self.model["conventions"]["nonNodeCoreElements"])
        yaml_entity_types = set(self.model["coreElements"]) - non_node_elements

        self.assertEqual(yaml_entity_types, set(jci_rules.ENTITY_TYPES))

    def test_yaml_relationship_names_are_canonical(self):
        canonical = {context[1] for context in jci_rules.RELATIONSHIP_OWNERS}
        declared = set()

        for element in self.model["coreElements"].values():
            for section in (
                "requiredRelationships",
                "requiredRelationshipsWhenActive",
                "optionalRelationships",
            ):
                for relationship in element.get(section, []):
                    declared.add(relationship["relationship"])

        declared.update(entry["type"] for entry in self.model["relationships"])
        self.assertTrue(declared)
        self.assertTrue(declared <= canonical, sorted(declared - canonical))

    def test_declared_relationship_contexts_exist_in_reference(self):
        for source_type, element in self.model["coreElements"].items():
            for section in (
                "requiredRelationships",
                "requiredRelationshipsWhenActive",
                "optionalRelationships",
            ):
                for relationship in element.get(section, []):
                    target = relationship.get("target")
                    source = relationship.get("source")
                    if not isinstance(target, str) or not isinstance(source, str):
                        continue
                    if source == "historized JCIEntity":
                        continue

                    if relationship.get("direction", "outgoing") == "incoming":
                        context = source, relationship["relationship"], source_type
                    else:
                        context = source_type, relationship["relationship"], target

                    with self.subTest(context=context):
                        owners = jci_rules.revision_owners(*context)
                        self.assertTrue(owners <= {"source", "target"})

    def test_pih_contract_is_explicit(self):
        pih = self.model["coreElements"]["PiH"]
        self.assertFalse(pih["canHistorize"])
        self.assertIn("PiH -> PiH", pih["forbiddenRelationships"])

        required = {
            (item["relationship"], item["cardinality"])
            for item in pih["requiredRelationships"]
        }
        self.assertIn(("HAS_HISTORICAL_STATE", "1"), required)
        self.assertIn(("CREATES_HISTORY", "1"), required)

        validation_ids = {rule["id"] for rule in self.model["validationRules"]}
        self.assertIn("pihBeforeChange", validation_ids)
        self.assertIn("noPiHRecursion", validation_ids)

    def test_future_derivation_chain_is_declared(self):
        expected = {
            "PiF2": ["CiV"],
            "PiF1s": ["PiF2"],
            "PiF1t": ["PiF1s"],
            "PiF1o": ["PiF1t"],
        }
        for entity_type, parents in expected.items():
            with self.subTest(entity_type=entity_type):
                self.assertEqual(self.model["coreElements"][entity_type]["derivedFrom"], parents)

        self.assertEqual(
            self.model["previewRules"][1]["path"],
            ["DECOMPOSES_INTO", "CONTRIBUTES_TO", "INSCRIBES_PURPOSE_IN"],
        )


if __name__ == "__main__":
    unittest.main()
