# Freigabeprofil 1.0 – Umsetzung und Abnahme

[Dokumentationsübersicht](../README.md) · [English](../en/changes/JCI_APPROVAL_1_0.md)

## 1. Fachliche Entscheidung

Die [kanonische Spezifikation, Abschnitt 12.9](../JCI_CONTEXT.md#129-nachweisbare-menschliche-freigabe--profil-10) ergänzt das Regelpaket 2.0 um nachweisbare menschliche Freigaben. Die zehn Kernelemente und 24 gespeicherten Entitätstypen bleiben bestehen. Das neue `APPROVED_BY` trennt Genehmigung von `REQUESTED_BY`; sein Eigentümer ist ausschließlich das neue unveränderliche `ChangeEvent`. Höhere Zukunftsebenen können nun ebenfalls `ACCOUNTABLE_MEMBER` besitzen. Accountability allein verleiht keine Befugnis.

Task-Freigaben beginnen am `PiF1o`. Nur fehlende Befugnis erlaubt Eskalation über alle erforderlichen `CONTRIBUTES_TO`-Zweige bis höchstens `PiF2`. Ablehnung und Regelkonflikt werden nicht durch Aufstieg umgangen. Eine konkrete menschliche Bestätigung löst die reguläre SYNC-Verarbeitung aus; nur deren erfolgreicher Abschluss übernimmt `ACTIVE` oder `BLOCKED`. Abschluss und Zielerreichung bleiben getrennt.

## 2. Technischer Vertrag

- `approvalProfileVersion = "1.0"` ist eine erforderliche Handler-Fähigkeit für geschützte Vorgänge, keine stillschweigende Ausweitung alter 2.0-Implementierungen.
- [Freigabe-Envelope](../schemas/jci-approval-envelope.schema.json), unveränderter Basisauftrag, genaue Hashbindung und befristete authentifizierte Belege ersetzen ein behauptetes `human_confirmed = True`.
- Pending- und Ablehnungsbelege sind dauerhafte technische Workflowdaten. Das `ChangeEvent` samt Genehmigungskanten entsteht erst mit vollständiger Annahme; späteres Anhängen ist unzulässig.
- `RaN.approvalPolicy` benennt genaue Rollen und Freigabeebenen. Prüfung und Autorisierung verwenden die vorher gültige Graphsicht, nicht selbst erteilte Rechte des Kandidaten.
- Wertentscheidungen berücksichtigen alle betroffenen alten und neuen CiV-Werteträger. Eine ausdrücklich menschlich eingerichtete Anfangsbefugnis löst ausschließlich den Startfall vor der ersten zuständigen Policy; ihre Deaktivierung bleibt dauerhaft.
- [Referenzprüfungen](../../reference/jci_approval.py) und [Tests](../../tests/test_approval_rules.py) bilden die Entscheidungslogik ab. Produktive Identitätsprüfung, dauerhafte Speicherung und echte Neo4j-Transaktionen benötigen weiterhin einen vertrauenswürdigen Adapter.

## 3. Einführung ohne erfundene Historie

1. Bestehende Daten, Ereignisse und Hashes unverändert erhalten. Fehlende Genehmigungen nicht nachträglich erfinden.
2. Menschliche Identitäten und gegebenenfalls eng begrenzte Anfangsbefugnisse ausdrücklich registrieren; der technische Root ist kein menschlicher Genehmiger.
3. Benötigte Accountabilities und RaN-Freigabepolicies fachlich festlegen. Fehlende Ansprechpartner oder Befugnisse als Modelllücken anzeigen.
4. Profilfähiges, prüfsummengebundenes Handler-Paket und gemeinsame Commit-Sperre bereitstellen. Unbekannte Profile und direkte Umgehungsversuche abweisen.
5. Belege, Fristen, geänderte Grundlagen, Ablehnungen und Wiederholungen prüfen, bevor ein produktiver Schreibweg geöffnet wird.

## 4. Abnahme und verbleibende Befunde

Die Abnahme umfasst lokale Freigabe, begrenzte Eskalation, mehrere Zukunftszweige, fehlende Accountability, menschliche Ablehnung, technische Identitäten, abgelaufene Rollen und Belege, veränderte Aufträge und Policies, Idempotenz sowie die Trennung von Freigabe und Abschluss. Die gleiche Prüfung gilt erneut am geschützten Entscheidungspunkt.

Von den sechs diskutierten Befunden bearbeitet diese Änderung insbesondere die menschliche Bestätigung und den Freigabeteil der RaN-Ausführung. Sie behauptet keine vollständige allgemeine RaN-Grammatik. Historische Löschkorrekturen, die Eigentümerkollision bei terminalen `GOVERNS`-Zielen, allgemeine DRAFT-Kardinalitäten und vollständige Snapshot-/Neo4j-Modellvalidierung bleiben gesondert offen. Das Repository bleibt ein Modell mit ausführbaren Referenzprüfungen, keine fertige produktive SYNC-Engine.
