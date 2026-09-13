import unittest

from reference.jci_rules import (
    TERMINAL, may_transition, aggregate_contributions, composite_status,
    ran_decision, valid_sync_lifecycle, valid_created_outcome,
    valid_historical_target, verification_is_applicable, valid_bootstrap,
    valid_historical_correction_commit, valid_correction_value_maps,
    valid_civ_model, valid_ran_protection,
)

class ModelRuleTests(unittest.TestCase):
    def test_active_ran_protects_coherent_civ_and_pif2_pair(self):
        """Eine aktive RaN schützt WHY und regelt dessen konkrete Umsetzung."""
        base = {
            "status": "ACTIVE",
            "protected_civ_ids": ["civ-security"],
            "protected_pif2_ids": ["pif2-trusted-platform"],
            "inscriptions": {("civ-security", "pif2-trusted-platform")},
            "governed_types": ["Task", "Verification", "RoFRole"],
            "human_confirmed": True,  # structural fixture, never an auth proof
        }
        self.assertTrue(valid_ran_protection(**base))
        self.assertFalse(valid_ran_protection(**(base | {"protected_civ_ids": []})))
        self.assertFalse(valid_ran_protection(**(base | {"protected_pif2_ids": []})))
        self.assertFalse(valid_ran_protection(**(base | {"governed_types": []})))
        self.assertFalse(valid_ran_protection(**(base | {"inscriptions": set()})))
        self.assertFalse(valid_ran_protection(**(base | {"governed_types": ["PiF2"]})))
        self.assertFalse(valid_ran_protection(**(base | {"human_confirmed": False})))
        self.assertFalse(valid_ran_protection(**(base | {"scope_compatible": False})))

        # Nicht jeder CiV eines PiF2 muss durch dieselbe RaN geschützt werden.
        self.assertTrue(valid_ran_protection(**(base | {
            "inscriptions": {
                ("civ-security", "pif2-trusted-platform"),
                ("civ-clarity", "pif2-trusted-platform"),
            },
        })))

    def test_civ_dimensions_holder_and_derived_pif2_scope(self):
        """Ein Wert ist dreidimensional, eindeutig getragen und scope-konsistent."""
        base = {
            "value_id": "civ-clarity-org",
            "not_civ": "Entscheidungen bleiben nicht absichtlich unklar.",
            "self_civ": "Wir machen Entscheidungen nachvollziehbar.",
            "to_serve_civ": "Kunden erhalten verlässliche Orientierung.",
            "holder_id": "org-junaco",
            "holder_type": "RoFOrg",
            "informed_by_ids": ["civ-clarity-member-anna"],
            "pif2_holder_sets": [["org-junaco", "org-junaco"]],
        }
        self.assertTrue(valid_civ_model(**base))
        self.assertFalse(valid_civ_model(**(base | {"self_civ": ""})))
        self.assertFalse(valid_civ_model(**(base | {"informed_by_ids": ["civ-clarity-org"]})))
        self.assertFalse(valid_civ_model(**(base | {"pif2_holder_sets": [["org-junaco", "team-board"]]})))
        self.assertFalse(valid_civ_model(**(base | {
            "holder_type": "RoFTeamMember", "holder_member_type": "TECHNICAL",
        })))
        self.assertTrue(valid_civ_model(**(base | {
            "holder_id": "member-anna", "holder_type": "RoFTeamMember",
            "holder_member_type": "HUMAN", "pif2_holder_sets": [["member-anna"]],
        })))

    def test_terminal_statuses_cannot_reopen(self):
        """
        JCI-Einordnung:
        Terminale Status kennzeichnen fachlich abgeschlossene Zustände. Dazu
        gehören erreichte Zukunftszustände, abgeschlossene Tätigkeiten,
        ersetzte oder aufgehobene Entitäten, unveränderliche Dokumentationen
        und gelöste Regelkonflikte.

        Beispiel:
        Ein Task „Kundenportal veröffentlichen“ ist bereits `COMPLETED`.
        Weitere Arbeit darf diesen abgeschlossenen Task nicht wieder auf
        `ACTIVE` setzen. Eine fachliche Fortsetzung benötigt eine neue Entität.

        Erwartete JCI-Logik:
        Keiner der terminalen Status darf in einen veränderbaren Status
        zurückwechseln. Dadurch bleibt der zeitliche Verlauf eindeutig und
        ein abgeschlossener Zustand wird nicht nachträglich umgedeutet.
        """
        for status in TERMINAL:
            # Für jeden terminalen Status wird derselbe unzulässige Versuch
            # geprüft: Ein bereits abgeschlossener Task soll wieder aktiv werden.
            self.assertFalse(may_transition("Task", status, "ACTIVE"))

    def test_process_artifacts_are_created_terminal(self):
        """
        JCI-Einordnung:
        `PiH`, `ChangeEvent`, `SyncEvent` und `HistoricalCorrection` sind
        unveränderliche Prozess- und Historisierungsobjekte. `ChangeEvent`
        beschreibt bereits einen angenommenen Auftrag; die übrigen drei
        beschreiben abgeschlossene historische oder technische Tatsachen.
        Alle werden direkt mit `RECORDED` angelegt.

        Beispiel:
        Nach einem beendeten Synchronisationslauf dokumentiert ein
        `SyncEvent`, welche SYNC-Definition ausgeführt wurde und wie der Lauf
        endete. Dieses Ereignis darf anschließend nicht zum Entwurf werden.

        Erwartete JCI-Logik:
        Die Objekte dürfen ausschließlich neu als `RECORDED` entstehen. Ein
        Wechsel von `RECORDED` nach `DRAFT` ist ausgeschlossen. Eine spätere
        historische Berichtigung erfolgt als neues `HistoricalCorrection`-
        Objekt und überschreibt das vorhandene Dokument nicht.
        """
        for entity_type in ("PiH", "ChangeEvent", "SyncEvent", "HistoricalCorrection"):
            # Das Prozessobjekt darf unmittelbar im unveränderlichen Zustand
            # RECORDED erzeugt werden.
            self.assertTrue(may_transition(entity_type, None, "RECORDED"))

            # Ein dokumentierter Vorgang darf nicht wieder geöffnet werden.
            self.assertFalse(may_transition(entity_type, "RECORDED", "DRAFT"))

    def test_task_blocking_and_completion(self):
        """
        JCI-Einordnung:
        Ein `Task` ist operative Arbeit zur Realisierung eines `PiF1o`.
        Notwendige Vorgänger werden über `DEPENDS_ON` verbunden. SYNC prüft
        diese Abhängigkeiten, bevor ein Task ausgeführt oder beendet wird.

        Beispiel:
        Der Task „Kundenportal veröffentlichen“ hängt vom Task
        „Sicherheitsprüfung abschließen“ ab. Fehlt diese Voraussetzung, wird
        die Produktivsetzung blockiert. Wird die Prüfung im selben SyncRun
        erfüllt und sind auch alle Abschlussbedingungen erfüllt, darf der
        blockierte Task unmittelbar abgeschlossen werden.

        Erwartete JCI-Logik:
        Ein aktiver Task darf `BLOCKED` werden. Ein blockierter Task darf bei
        vollständig erfüllten Bedingungen `COMPLETED` erreichen. Der
        terminale Status `COMPLETED` darf anschließend nicht wieder geöffnet
        werden.
        """
        # Eine notwendige Abhängigkeit ist nicht mehr erfüllt.
        self.assertTrue(may_transition("Task", "ACTIVE", "BLOCKED"))

        # Abhängigkeit und Abschlussbedingungen werden gemeinsam erfüllt.
        self.assertTrue(may_transition("Task", "BLOCKED", "COMPLETED"))

        # Der abgeschlossene Task bleibt unveränderlich abgeschlossen.
        self.assertFalse(may_transition("Task", "COMPLETED", "ACTIVE"))

    def test_future_contribution_modes(self):
        """
        JCI-Einordnung:
        Die Zukunftselemente sind vom konkreteren zum übergeordneten Zustand
        über `CONTRIBUTES_TO` verbunden: `PiF1o → PiF1t → PiF1s → PiF2`.
        `contributionMode` legt fest, wie direkte Beiträge aggregiert werden.

        Beispiel:
        Zum taktischen Zustand „Kundenservice ist digitalisiert“ tragen die
        operativen Zustände „Kundenportal ist produktiv“ und „Supportsystem
        ist produktiv“ bei. Bei `ALL` müssen beide erreicht sein. Bei `ANY`
        genügt mindestens einer der aktuellen Beiträge.

        Erwartete JCI-Logik:
        `ALL` verlangt ausschließlich erreichte aktuelle Beiträge. `ANY`
        verlangt mindestens einen erreichten aktuellen Beitrag. Ersetzte und
        aufgehobene Beiträge zählen nicht; bleiben nur solche Beiträge übrig,
        darf der übergeordnete Zustand nicht als erreicht gelten.
        """
        # Beide aktuellen Beiträge sind erreicht: ALL ist erfüllt.
        self.assertTrue(aggregate_contributions("ALL", ["ACHIEVED", "ACHIEVED"]))

        # Ein Beitrag ist noch aktiv: ALL ist noch nicht erfüllt.
        self.assertFalse(aggregate_contributions("ALL", ["ACHIEVED", "ACTIVE"]))

        # Für ANY genügt der eine bereits erreichte Beitrag.
        self.assertTrue(aggregate_contributions("ANY", ["ACHIEVED", "ACTIVE"]))

        # Ersetzte oder aufgehobene Beiträge sind nicht aktuell. Ohne einen
        # aktuellen Beitrag kann auch ANY nicht erfüllt werden.
        self.assertFalse(aggregate_contributions("ANY", ["REVOKED", "REPLACED"]))

    def test_composite_task_aggregation(self):
        """
        JCI-Einordnung:
        Ein `COMPOSITE`-Task strukturiert Arbeit und wird nicht selbst durch
        ein `RoleAssignment` ausgeführt. Sein Status wird aus den direkten
        Untertasks abgeleitet. Die ausführbare Arbeit liegt in `ATOMIC`-Tasks.

        Beispiel:
        „Kundenportal bereitstellen“ besteht aus „Oberfläche entwickeln“,
        „Sicherheitsprüfung durchführen“ und „Produktivsetzung durchführen“.
        Der Gesamtstatus muss den tatsächlichen Arbeitsstand dieser direkten
        Untertasks widerspiegeln.

        Erwartete JCI-Logik:
        Nur Entwürfe ergeben `DRAFT`, nur abgeschlossene Untertasks ergeben
        `COMPLETED`, und eine Mischung aus Entwurf und Abschluss bedeutet
        laufende Arbeit (`ACTIVE`). Ohne aktive Arbeit führt ein blockierter
        Untertask zu `BLOCKED`. Aufgehobene und ersetzte Untertasks bleiben gespeichert, z?hlen jedoch
        nicht mehr zum aktuellen Umfang; ein leerer aktueller Umfang ist ung?ltig.
        """
        # Alle Untertasks sind noch Entwürfe.
        self.assertEqual(composite_status("DRAFT", ["DRAFT", "DRAFT"]), "DRAFT")

        # Sämtliche direkten Untertasks sind abgeschlossen.
        self.assertEqual(composite_status("ACTIVE", ["COMPLETED", "COMPLETED"]), "COMPLETED")

        # Die Mischung zeigt, dass der Gesamtvorgang bereits läuft.
        self.assertEqual(composite_status("ACTIVE", ["DRAFT", "COMPLETED"]), "ACTIVE")

        # Mindestens ein erforderlicher Untertask kann nicht fortgesetzt werden.
        self.assertEqual(composite_status("ACTIVE", ["BLOCKED", "COMPLETED"]), "BLOCKED")

        # Ein aufgehobener, weiterhin eingebundener Untertask ist keine
        # zulässige Grundlage für eine automatische Statusaggregation.
        self.assertEqual(composite_status("ACTIVE", ["REVOKED", "COMPLETED"]), "COMPLETED")

    def test_ran_effects_and_real_conflict(self):
        """
        JCI-Einordnung:
        `RaN` beschreibt Regeln und Normen. Abhängig von `effect` kann eine
        zutreffende Regel eine Entscheidung erlauben (`PERMIT`), verlangen
        (`REQUIRE`) oder verweigern (`PROHIBIT`). SYNC vergleicht alle auf
        dieselbe konkrete Entscheidung anwendbaren Regeln.

        Beispiel:
        Für „Kundenportal produktiv setzen“ erlaubt eine Regel die Freigabe
        nach erfolgreichem Test. Eine andere Regel verbietet dieselbe Freigabe
        ohne Datenschutzprüfung. Sind beide Bedingungen gleichzeitig
        zutreffend, entstehen für dieselbe Entscheidung `ALLOW` und `DENY`.

        Erwartete JCI-Logik:
        Erst die gleichzeitige Erlaubnis und Verweigerung derselben
        Entscheidung bildet einen echten Widerspruch. Eine nicht zutreffende
        `PROHIBIT`-Regel trifft keine Entscheidung. Eine nicht erfüllte
        `REQUIRE`-Regel verweigert die Entscheidung und stellt zunächst eine
        Regelverletzung dar, nicht automatisch einen `RaNConflict`.
        """
        # Die zutreffende PERMIT-Regel erlaubt die Produktivsetzung.
        allow = ran_decision("PERMIT", True)

        # Die zutreffende PROHIBIT-Regel verweigert dieselbe Entscheidung.
        deny = ran_decision("PROHIBIT", True)

        # ALLOW und DENY zeigen den fachlichen Widerspruch, den SYNC danach
        # anhand von decisionKey, Scope und Priorität vollständig bewertet.
        self.assertEqual({allow, deny}, {"ALLOW", "DENY"})

        # Ein Verbot, dessen Bedingung nicht zutrifft, bleibt ohne Entscheidung.
        self.assertEqual(ran_decision("PROHIBIT", False), "NO_DECISION")

        # Eine verpflichtende, aber nicht erfüllte Bedingung verweigert die
        # Entscheidung. Allein daraus entsteht noch kein Regelkonflikt.
        self.assertEqual(ran_decision("REQUIRE", False), "DENY")

    def test_change_event_sync_run_lifecycle(self):
        """Ein SyncEvent dokumentiert genau einen bereits beendeten Lauf."""
        # Lauf A ist beendet, Lauf B läuft noch. Nur A darf bereits als
        # unveränderliches SyncEvent am ChangeEvent hängen.
        self.assertTrue(valid_sync_lifecycle(["A", "B"], ["A"], ["A"]))

        # Ein Ereignis für den noch laufenden Lauf B wäre eine vorweggenommene
        # Abschlussdokumentation und ist daher unzulässig.
        self.assertFalse(valid_sync_lifecycle(["A", "B"], ["A"], ["A", "B"]))

        # Ein Retry ist ein eigener Lauf und darf nach seinem Abschluss ein
        # zweites Ereignis mit einer anderen runId erzeugen.
        self.assertTrue(valid_sync_lifecycle(["A", "B"], ["A", "B"], ["A", "B"]))

    def test_created_has_no_fictitious_history(self):
        """CREATED beginnt bei Revision 1 und historisiert keine Revision 0."""
        self.assertTrue(valid_created_outcome(
            target_existed_before=False,
            requested_revision=None,
            outcome="SUCCESS",
            target_exists_after=True,
            target_revision_after=1,
            changed_by_count=1,
            target_history_count=0,
        ))
        self.assertTrue(valid_created_outcome(
            target_existed_before=False,
            requested_revision=None,
            outcome="FAILED",
            target_exists_after=False,
            target_revision_after=None,
            changed_by_count=0,
            target_history_count=0,
        ))

        # Eine bereits belegte Ziel-ID ist kein CREATED-Ausgangspunkt.
        self.assertFalse(valid_created_outcome(
            target_existed_before=True,
            requested_revision=None,
            outcome="SUCCESS",
            target_exists_after=True,
            target_revision_after=1,
            changed_by_count=1,
            target_history_count=0,
        ))

    def test_historical_correction_targets_exact_pih(self):
        """TARGETS_HISTORY und CORRECTS müssen dasselbe PiH adressieren."""
        self.assertTrue(valid_historical_target(
            change_type="HISTORICAL_CORRECTION",
            changed_by_count=0,
            target_history_ids=["pih-1"],
            corrected_history_id="pih-1",
            requested_revision=1,
        ))

        # Die Korrektur darf nicht stillschweigend auf ein anderes PiH zeigen.
        self.assertFalse(valid_historical_target(
            change_type="HISTORICAL_CORRECTION",
            changed_by_count=0,
            target_history_ids=["pih-1"],
            corrected_history_id="pih-2",
            requested_revision=1,
        ))

    def test_verification_is_bound_to_target_revisions(self):
        """Nur eine Verification der aktuellen Zielrevisionen ist anwendbar."""
        common = {
            "result_status": "COMPLETED",
            "criterion_status": "ACTIVE",
            "same_pif1o": True,
            "result_revision": 3,
            "criterion_revision": 2,
            "evaluated_result_revision": 3,
            "checked_criterion_revision": 2,
            "superseded": False,
        }
        self.assertTrue(verification_is_applicable(**common))

        # Nach der Änderung des Kriteriums auf Revision 3 bleibt der Nachweis
        # erhalten, zählt aber nicht mehr zur aktuellen Zielerreichung.
        stale = dict(common, criterion_revision=3)
        self.assertFalse(verification_is_applicable(**stale))

    def test_bootstrap_is_single_closed_trust_root(self):
        """Der Bootstrap ist vollständig, atomar und nicht wiederholbar."""
        required = {
            "RoFOrg", "RoFTeam", "RoFTeamMember", "RoFRole",
            "RoleAssignment", "SYNC",
        }
        self.assertTrue(valid_bootstrap(
            graph_was_empty=True,
            root_keys=["ROOT"],
            required_types=required,
            created_types=required,
            created_statuses={entity_type: "ACTIVE" for entity_type in required},
            revisions={entity_type: 1 for entity_type in required},
            created_at_values={"2026-08-30T09:00:00+02:00"},
            valid_from_values={"2026-08-30T09:00:00+02:00"},
            entities_without_creator=["RoleAssignment:ROOT"],
        ))

        # Ein zweites Root oder ein Bootstrap in einem bestehenden Graphen
        # würde die Vertrauenswurzel mehrdeutig machen.
        self.assertFalse(valid_bootstrap(
            graph_was_empty=False,
            root_keys=["ROOT", "ROOT"],
            required_types=required,
            created_types=required,
            created_statuses={entity_type: "ACTIVE" for entity_type in required},
            revisions={entity_type: 1 for entity_type in required},
            created_at_values={"2026-08-30T09:00:00+02:00"},
            valid_from_values={"2026-08-30T09:00:00+02:00"},
            entities_without_creator=["RoleAssignment:ROOT"],
        ))

        # Ein zwar vollständiger, aber als DRAFT erzeugter Minimalgraph wäre
        # nicht handlungsfähig: Das Root-RoleAssignment könnte den ersten
        # regulären Auftrag nicht unter einer aktiven SYNC-Definition stellen.
        draft_statuses = {entity_type: "ACTIVE" for entity_type in required}
        draft_statuses["RoleAssignment"] = "DRAFT"
        self.assertFalse(valid_bootstrap(
            graph_was_empty=True,
            root_keys=["ROOT"],
            required_types=required,
            created_types=required,
            created_statuses=draft_statuses,
            revisions={entity_type: 1 for entity_type in required},
            created_at_values={"2026-08-30T09:00:00+02:00"},
            valid_from_values={"2026-08-30T09:00:00+02:00"},
            entities_without_creator=["RoleAssignment:ROOT"],
        ))

    def test_historical_corrections_are_conflict_safe(self):
        """Disjunkte Felder sind parallel möglich; Überlappungen sind streng."""
        history_hash = "a" * 64

        # Eine Ergänzung eines bisher unberührten Felds darf neben der
        # bestehenden Korrektur aktiv werden.
        self.assertTrue(valid_historical_correction_commit(
            expected_hash=history_hash,
            current_hash=history_hash,
            corrected_fields=["/stateData/properties/taskType"],
            active_field_sets=[{"/stateData/properties/name"}],
            superseded_indexes=[],
        ))

        # Dasselbe Feld darf nur durch vollständiges Ersetzen genau einer
        # aktiven Vorgängerkorrektur geändert werden.
        self.assertTrue(valid_historical_correction_commit(
            expected_hash=history_hash,
            current_hash=history_hash,
            corrected_fields=["/stateData/properties/name", "/stateData/properties/taskType"],
            active_field_sets=[{"/stateData/properties/name"}],
            superseded_indexes=[0],
        ))

        # Ein inzwischen veralteter HistoryView-Hash verhindert Lost Updates.
        self.assertFalse(valid_historical_correction_commit(
            expected_hash="b" * 64,
            current_hash=history_hash,
            corrected_fields=["/stateData/properties/taskType"],
            active_field_sets=[],
            superseded_indexes=[],
        ))

        # Der ergänzte Pfad muss in beiden Wertemengen vorkommen; sein alter
        # Wert ist ausdrücklich NULL, weil er in der Basissicht fehlte.
        self.assertTrue(valid_correction_value_maps(
            correction_type="ADDITION",
            corrected_fields=["/stateData/properties/taskType"],
            previous_values={
                "/stateData/properties/taskType": {"valueType": "NULL", "value": None}
            },
            corrected_values={
                "/stateData/properties/taskType": {"valueType": "STRING", "value": "Team A"}
            },
        ))

        # Ein zusätzliches, nicht deklariertes Map-Feld wäre eine versteckte
        # Änderung außerhalb von correctedFields und ist deshalb ungültig.
        self.assertFalse(valid_correction_value_maps(
            correction_type="CORRECTION",
            corrected_fields=["/stateData/properties/taskType"],
            previous_values={
                "/stateData/properties/taskType": {"valueType": "STRING", "value": "Team B"},
                "/stateData/properties/name": {"valueType": "STRING", "value": "Anna"},
            },
            corrected_values={
                "/stateData/properties/taskType": {"valueType": "STRING", "value": "Team A"}
            },
        ))


if __name__ == "__main__":
    unittest.main()
