import unittest


TERMINAL = {"ACHIEVED", "COMPLETED", "REPLACED", "REVOKED", "RECORDED", "RESOLVED"}


def may_transition(entity_type: str, source: str | None, target: str) -> bool:
    """Prüft einen Statuswechsel nach dem gemeinsamen JCI-Statusmodell.

    `entity_type` bestimmt, welche Statuswerte und Übergänge für die konkrete
    `JCIEntity` zulässig sind. `source = None` bezeichnet die erstmalige
    Erzeugung. Die Funktion bildet nur die Übergangsmatrix ab; zusätzliche
    Bedingungen wie Pflichtbeziehungen, anwendbare `RaN` oder vollständige
    WHY- und WHO-Pfade werden im vollständigen SYNC-Ablauf geprüft.

    Beispiel:
    Ein aktiver `Task` darf wegen einer unerfüllten Abhängigkeit `BLOCKED`
    werden. Ein bereits `COMPLETED` Task darf dagegen nicht erneut `ACTIVE`
    werden, weil `COMPLETED` ein terminaler Zustand ist.
    """
    # Terminale Zustände werden nicht wieder geöffnet. Eine fachliche
    # Fortsetzung wird im JCI-Modell als neue Entität angelegt.
    if source in TERMINAL:
        return False

    # Unveränderliche Historisierungs- und Prozessobjekte entstehen direkt
    # als RECORDED und besitzen keinen späteren Statuswechsel. ChangeEvent
    # dokumentiert dabei bereits den angenommenen Auftrag; SyncEvent erst den
    # Abschluss eines technischen Versuchs.
    if entity_type in {"PiH", "ChangeEvent", "SyncEvent", "HistoricalCorrection"}:
        return source is None and target == "RECORDED"

    # Eine Verification wird erst gespeichert, wenn die abgeschlossene
    # Bewertung von Result und SuccessCriterion vollständig feststeht.
    if entity_type == "Verification":
        return source is None and target == "COMPLETED"

    # Ein erkannter RaNConflict beginnt offen und kann nach einer bestätigten
    # fachlichen Auflösung genau einmal RESOLVED werden.
    if entity_type == "RaNConflict":
        return (source, target) in {(None, "OPEN"), ("OPEN", "RESOLVED")}

    # Tasks besitzen zusätzlich BLOCKED und COMPLETED, weil Abhängigkeiten
    # ihre Ausführung verhindern und ihre Arbeit abgeschlossen werden kann.
    if entity_type == "Task":
        return (source, target) in {
            (None, "DRAFT"), ("DRAFT", "ACTIVE"), ("DRAFT", "BLOCKED"),
            ("DRAFT", "REVOKED"), ("ACTIVE", "BLOCKED"),
            ("ACTIVE", "COMPLETED"), ("ACTIVE", "REPLACED"),
            ("ACTIVE", "REVOKED"), ("BLOCKED", "ACTIVE"),
            ("BLOCKED", "COMPLETED"), ("BLOCKED", "REPLACED"),
            ("BLOCKED", "REVOKED"),
        }
    # Ein Result kann nach vollständiger Erzeugung abgeschlossen werden.
    if entity_type == "Result" and (source, target) == ("ACTIVE", "COMPLETED"):
        return True

    # Zukunftselemente dürfen bei erfüllten Zielbedingungen ACHIEVED werden.
    if entity_type in {"PiF2", "PiF1s", "PiF1t", "PiF1o"} and (
        source, target
    ) == ("ACTIVE", "ACHIEVED"):
        return True

    # Alle übrigen veränderlichen Fachentitäten verwenden diesen gemeinsamen
    # Grundzyklus von Entwurf, Aktivierung, Ersetzung oder Aufhebung.
    return (source, target) in {
        (None, "DRAFT"), ("DRAFT", "ACTIVE"), ("DRAFT", "REVOKED"),
        ("ACTIVE", "REPLACED"), ("ACTIVE", "REVOKED"),
    }


def aggregate_contributions(mode: str, statuses: list[str]) -> bool:
    """Bestimmt, ob direkte Zukunftsbeiträge den Zielzustand erfüllen.

    Die Funktion bildet die Aggregation entlang der Zukunftskette
    `PiF1o → PiF1t → PiF1s → PiF2` ab. `statuses` enthält die Statuswerte der
    direkten `CONTRIBUTES_TO`-Beiträge eines übergeordneten Elements.

    `ALL` verlangt, dass alle aktuellen direkten Beiträge `ACHIEVED` sind.
    `ANY` verlangt mindestens einen erreichten aktuellen Beitrag. Ersetzte
    und aufgehobene Entitäten zählen nicht als aktuelle Beiträge. Gibt es
    danach keinen aktuellen Beitrag, kann der Zielzustand nicht erreicht sein.

    Beispiel:
    Tragen „Kundenportal produktiv“ und „Supportsystem produktiv“ zu einem
    taktischen Zustand bei, verlangt `ALL` beide Erfolge. Bei `ANY` genügt
    einer der beiden erreichten Zustände.
    """
    # REPLACED und REVOKED beschreiben keine aktuellen Beiträge. Ein gültiger
    # Nachfolger müsste als eigene aktuelle Entität in statuses enthalten sein.
    current = [s for s in statuses if s not in {"REPLACED", "REVOKED"}]

    # Ohne mindestens einen aktuellen direkten Beitrag darf kein
    # übergeordnetes Zukunftselement automatisch ACHIEVED werden.
    if not current:
        return False

    # ALL bildet eine vollständige gemeinsame Zielerreichung ab.
    if mode == "ALL":
        return all(s == "ACHIEVED" for s in current)

    # ANY bildet alternative Wege zum selben übergeordneten Ziel ab.
    if mode == "ANY":
        return any(s == "ACHIEVED" for s in current)

    # Andere Modi sind nicht Bestandteil der kanonischen JCI-Spezifikation.
    raise ValueError("unknown contributionMode")


def aggregate_composite(statuses: list[str]) -> str:
    """Leitet den Status eines COMPOSITE-Tasks aus direkten Untertasks ab.

    Ein `COMPOSITE`-Task strukturiert operative Arbeit, wird aber nicht selbst
    durch ein `RoleAssignment` ausgeführt. Deshalb entsteht sein Status aus
    den direkten Untertasks. Die Liste `statuses` enthält deren effektive
    Statuswerte, nachdem korrekt eingebundene Nachfolger ersetzter Tasks
    berücksichtigt wurden.

    Beispiel:
    „Kundenportal bereitstellen“ besteht aus Entwicklung, Sicherheitsprüfung
    und Produktivsetzung. Sobald ein Untertask arbeitet, ist der Parent
    `ACTIVE`. Erst wenn alle drei abgeschlossen sind, wird er `COMPLETED`.
    """
    # Ein Composite ohne Untertasks ist unvollständig. REPLACED oder REVOKED
    # zeigen hier, dass die wirksame Nachfolge bzw. Bereinigung nicht korrekt
    # vorbereitet wurde und daher keine sichere Aggregation möglich ist.
    if not statuses or any(s in {"REPLACED", "REVOKED"} for s in statuses):
        return "CONFLICT"

    # Solange alle direkten Untertasks Entwürfe sind, bleibt auch der Parent
    # ein Entwurf.
    if all(s == "DRAFT" for s in statuses):
        return "DRAFT"

    # Der Parent ist erst abgeschlossen, wenn jeder direkte Untertask
    # abgeschlossen ist.
    if all(s == "COMPLETED" for s in statuses):
        return "COMPLETED"

    # Ein aktiver Untertask oder eine Mischung aus vorbereiteter und bereits
    # abgeschlossener Arbeit bedeutet, dass der Gesamtvorgang läuft.
    if "ACTIVE" in statuses or (
        "DRAFT" in statuses and "COMPLETED" in statuses
    ):
        return "ACTIVE"

    # Ohne aktive Arbeit bestimmt ein blockierter Untertask den Parentstatus.
    if "BLOCKED" in statuses:
        return "BLOCKED"

    # Nicht spezifizierte Kombinationen werden nicht stillschweigend gedeutet.
    return "CONFLICT"


def ran_decision(effect: str, condition: bool) -> str:
    """Übersetzt eine ausgewertete RaN in ihre einzelne Entscheidung.

    `condition` gibt an, ob die normalisierte Bedingung der Regel auf den
    geprüften Kontext zutrifft. Das Ergebnis ist die Bewertung genau einer
    Regel. Ob mehrere Regeln einen echten Widerspruch bilden und welche
    Priorität gilt, entscheidet erst der vollständige SYNC-Ablauf.

    Beispiel:
    Eine zutreffende Regel `PROHIBIT`, die eine Produktivsetzung ohne
    Datenschutzfreigabe verbietet, ergibt `DENY`. Trifft ihre Bedingung nicht
    zu, liefert sie `NO_DECISION` und beeinflusst diese Entscheidung nicht.
    """
    # REQUIRE erlaubt nur bei erfüllter Pflicht; andernfalls liegt eine
    # Regelverletzung vor und die Entscheidung wird verweigert.
    if effect == "REQUIRE":
        return "ALLOW" if condition else "DENY"

    # PROHIBIT verweigert nur, wenn die Verbotsbedingung tatsächlich zutrifft.
    if effect == "PROHIBIT":
        return "DENY" if condition else "NO_DECISION"

    # PERMIT erlaubt bei zutreffender Bedingung, erzeugt andernfalls aber
    # keine automatische Verweigerung.
    if effect == "PERMIT":
        return "ALLOW" if condition else "NO_DECISION"

    # Andere Effekte sind im kanonischen RaN-Modell nicht definiert.
    raise ValueError("unknown RaN effect")


def valid_sync_lifecycle(
    scheduled_run_ids: list[str],
    completed_run_ids: list[str],
    sync_event_run_ids: list[str],
) -> bool:
    """Prüft die 1:1-Abbildung beendeter technischer Läufe auf SyncEvents.

    Ein angenommenes `ChangeEvent` darf zunächst nur einen eingeplanten,
    noch laufenden `SyncRun` besitzen. Erst Abschluss oder kontrollierter
    Abbruch erzeugen ein unveränderliches `SyncEvent`. Wiederholungsversuche
    verwenden neue `runId`-Werte und erzeugen jeweils ein weiteres Ereignis.

    Beispiel:
    Lauf A ist beendet, Lauf B läuft noch. Dann muss genau für A ein
    `SyncEvent` existieren. Ein Ereignis für B wäre verfrüht; zwei Ereignisse
    für A würden denselben Versuch doppelt dokumentieren.
    """
    # Jeder beendete Lauf muss zuvor eingeplant und jede ID eindeutig sein.
    if len(set(scheduled_run_ids)) != len(scheduled_run_ids):
        return False
    if len(set(completed_run_ids)) != len(completed_run_ids):
        return False
    if not set(completed_run_ids).issubset(scheduled_run_ids):
        return False

    # SyncEvents dürfen nur für beendete Läufe existieren und bilden diese
    # Menge exakt ab. Noch laufende Versuche bleiben ereignislos.
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
    history_count: int,
) -> bool:
    """Prüft den Sonderfall `CREATED` ohne erfundenen Ausgangszustand.

    Das Ziel eines `CREATED`-Auftrags darf bei Annahme noch nicht existieren
    und besitzt deshalb keine angeforderte Ausgangsrevision. Nur ein
    erfolgreicher Commit legt Revision 1 samt genau einer `CHANGED_BY`-
    Beziehung an. Weil vorher kein Zustand vorhanden war, entsteht kein PiH.

    Beispiel:
    Ein neuer Task mit freier UUID wird erfolgreich erzeugt. Er beginnt mit
    Revision 1 und verweist auf sein ChangeEvent; ein „Task Revision 0“ wird
    weder konstruiert noch historisiert.
    """
    if target_existed_before or requested_revision is not None or history_count != 0:
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
    """Prüft die eindeutige Adressierung einer historischen Korrektur.

    `HISTORICAL_CORRECTION` ändert keine aktuelle Quellentität. Das
    `ChangeEvent` zeigt deshalb nicht über `CHANGED_BY`, sondern genau über
    `TARGETS_HISTORY` auf ein unveränderliches PiH. Bei Erfolg muss die
    erzeugte Korrektur über `CORRECTS` dasselbe PiH bezeichnen.
    """
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
    """Bestimmt, ob eine Verification für die Zielaggregation noch gilt.

    Eine Verification ist eine abgeschlossene Aussage über genau eine
    Result- und SuccessCriterion-Revision. Ändert sich eines der Prüfziele,
    bleibt die Verification als Nachweis erhalten, ist aber nicht mehr auf
    den aktuellen Modellzustand anwendbar.

    Beispiel:
    Revision 3 eines Ergebnisses wurde gegen Revision 2 des Kriteriums
    geprüft. Nach Änderung des Kriteriums auf Revision 3 muss eine neue
    Verification entstehen; die alte darf PiF1o nicht auf ACHIEVED setzen.
    """
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
    """Prüft die geschlossene einmalige Vertrauenswurzel des JCI-Graphen.

    Der Bootstrap ist nur im vollständig leeren Graphen zulässig. Er legt
    Organisation, Team, technisches Mitglied, Rolle, Root-RoleAssignment und
    aktive SYNC-Definition atomar an. Alle sechs Entitäten müssen sofort
    `ACTIVE`, auf Revision 1 und auf denselben Gültigkeitsbeginn gesetzt
    werden. Nur das Root-RoleAssignment darf ohne `CREATED_BY` bleiben;
    danach gelten die normalen Provenienzregeln.
    """
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
) -> bool:
    """Prüft konkurrierende Ergänzungen zur wirksamen HistoryView.

    Feldfremde Korrekturen dürfen nebeneinander aktiv sein. Überlappt eine
    neue Korrektur bestehende Felder, muss sie genau eine aktive Korrektur
    vollständig ersetzen. Der Hashvergleich verhindert, dass ein Auftrag
    unbemerkt auf einer zwischenzeitlich veralteten historischen Sicht
    committed wird.
    """
    if expected_hash != current_hash:
        return False
    if not corrected_fields or corrected_fields != sorted(set(corrected_fields)):
        return False

    new_fields = set(corrected_fields)
    overlaps = [
        index for index, active_fields in enumerate(active_field_sets)
        if new_fields & active_fields
    ]
    if not overlaps:
        return not superseded_indexes

    # Eine Überlappung mit mehreren aktiven Korrekturen ist nicht eindeutig.
    # Bei genau einer muss die neue Korrektur deren gesamte Feldmenge tragen;
    # zusätzliche, bisher unberührte Felder sind dabei zulässig.
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
    """Prüft die vollständige Feldbindung der Korrekturwerte.

    Beide Wertemengen müssen exakt dieselben kanonischen Pfade wie
    `correctedFields` enthalten. Bei `ADDITION` darf zuvor gerade kein Wert
    wirksam gewesen sein; dies wird ausdrücklich als typisiertes `NULL`
    gespeichert und nicht durch ein fehlendes Map-Feld angedeutet.
    """
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
    """Prüft die drei CiV-Dimensionen und den abgeleiteten Scope."""
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


def valid_ran_protection(
    *,
    status: str,
    protected_civ_ids: list[str],
    protected_pif2_ids: list[str],
    inscriptions: set[tuple[str, str]],
    governed_types: list[str],
    human_confirmed: bool = True,
    scope_compatible: bool = True,
) -> bool:
    """Prüft Schutzgegenstand, Kohärenz und konkrete RaN-Umsetzung."""
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


class ModelRuleTests(unittest.TestCase):
    def test_active_ran_protects_coherent_civ_and_pif2_pair(self):
        """Eine aktive RaN schützt WHY und regelt dessen konkrete Umsetzung."""
        base = {
            "status": "ACTIVE",
            "protected_civ_ids": ["civ-security"],
            "protected_pif2_ids": ["pif2-trusted-platform"],
            "inscriptions": {("civ-security", "pif2-trusted-platform")},
            "governed_types": ["Task", "Verification", "RoFRole"],
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
        Untertask zu `BLOCKED`. Ein weiterhin eingebundener aufgehobener oder
        nicht korrekt ersetzter Untertask erzeugt einen Konflikt.
        """
        # Alle Untertasks sind noch Entwürfe.
        self.assertEqual(aggregate_composite(["DRAFT", "DRAFT"]), "DRAFT")

        # Sämtliche direkten Untertasks sind abgeschlossen.
        self.assertEqual(aggregate_composite(["COMPLETED", "COMPLETED"]), "COMPLETED")

        # Die Mischung zeigt, dass der Gesamtvorgang bereits läuft.
        self.assertEqual(aggregate_composite(["DRAFT", "COMPLETED"]), "ACTIVE")

        # Mindestens ein erforderlicher Untertask kann nicht fortgesetzt werden.
        self.assertEqual(aggregate_composite(["BLOCKED", "COMPLETED"]), "BLOCKED")

        # Ein aufgehobener, weiterhin eingebundener Untertask ist keine
        # zulässige Grundlage für eine automatische Statusaggregation.
        self.assertEqual(aggregate_composite(["REVOKED", "COMPLETED"]), "CONFLICT")

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
            history_count=0,
        ))
        self.assertTrue(valid_created_outcome(
            target_existed_before=False,
            requested_revision=None,
            outcome="FAILED",
            target_exists_after=False,
            target_revision_after=None,
            changed_by_count=0,
            history_count=0,
        ))

        # Eine bereits belegte Ziel-ID ist kein CREATED-Ausgangspunkt.
        self.assertFalse(valid_created_outcome(
            target_existed_before=True,
            requested_revision=None,
            outcome="SUCCESS",
            target_exists_after=True,
            target_revision_after=1,
            changed_by_count=1,
            history_count=0,
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
            corrected_fields=["/stateData/team"],
            active_field_sets=[{"/stateData/owner"}],
            superseded_indexes=[],
        ))

        # Dasselbe Feld darf nur durch vollständiges Ersetzen genau einer
        # aktiven Vorgängerkorrektur geändert werden.
        self.assertTrue(valid_historical_correction_commit(
            expected_hash=history_hash,
            current_hash=history_hash,
            corrected_fields=["/stateData/owner", "/stateData/team"],
            active_field_sets=[{"/stateData/owner"}],
            superseded_indexes=[0],
        ))

        # Ein inzwischen veralteter HistoryView-Hash verhindert Lost Updates.
        self.assertFalse(valid_historical_correction_commit(
            expected_hash="b" * 64,
            current_hash=history_hash,
            corrected_fields=["/stateData/team"],
            active_field_sets=[],
            superseded_indexes=[],
        ))

        # Der ergänzte Pfad muss in beiden Wertemengen vorkommen; sein alter
        # Wert ist ausdrücklich NULL, weil er in der Basissicht fehlte.
        self.assertTrue(valid_correction_value_maps(
            correction_type="ADDITION",
            corrected_fields=["/stateData/team"],
            previous_values={
                "/stateData/team": {"valueType": "NULL", "value": None}
            },
            corrected_values={
                "/stateData/team": {"valueType": "STRING", "value": "Team A"}
            },
        ))

        # Ein zusätzliches, nicht deklariertes Map-Feld wäre eine versteckte
        # Änderung außerhalb von correctedFields und ist deshalb ungültig.
        self.assertFalse(valid_correction_value_maps(
            correction_type="CORRECTION",
            corrected_fields=["/stateData/team"],
            previous_values={
                "/stateData/team": {"valueType": "STRING", "value": "Team B"},
                "/stateData/owner": {"valueType": "STRING", "value": "Anna"},
            },
            corrected_values={
                "/stateData/team": {"valueType": "STRING", "value": "Team A"}
            },
        ))


if __name__ == "__main__":
    unittest.main()
