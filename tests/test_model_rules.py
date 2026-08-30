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
    # als RECORDED und besitzen keinen späteren Statuswechsel.
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


class ModelRuleTests(unittest.TestCase):
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
        unveränderliche Prozess- und Historisierungsobjekte. Sie beschreiben
        abgeschlossene Tatsachen und werden direkt mit `RECORDED` angelegt.

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


if __name__ == "__main__":
    unittest.main()
