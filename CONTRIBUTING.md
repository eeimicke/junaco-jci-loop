# Zum JCI-Modell beitragen

Beiträge sind willkommen, werden aber kontrolliert geprüft. Maßgeblich sind `docs/JCI_CONTEXT.md`, `GOVERNANCE.md`, `LICENSE.md` und `NOTICE.md`.

## Ablauf

1. Für Fehler oder Vorschläge zunächst ein Issue anlegen.
2. Änderungen in einem eigenen Branch vornehmen.
3. Einen Pull Request gegen `main` eröffnen.
4. Die Pull-Request-Vorlage vollständig ausfüllen.
5. Automatische Prüfungen erfolgreich abschließen.
6. Die dokumentierte fachliche Freigabe abwarten.

Direkte Pushes auf `main` sind nicht Teil des regulären Arbeitsablaufs.

## Fachliche Anforderungen

Bei einer Modelländerung müssen mindestens angegeben werden:

- Anlass und Ziel,
- Art der Änderung,
- betroffene JCI-Kernelemente und Graphobjekte,
- betroffene Beziehungen, Richtungen und Kardinalitäten,
- Auswirkungen auf `RaN`, `RoF`, `ERoF`, `SYNC` und `PiH`,
- Auswirkungen auf die Rückverfolgbarkeit zu `CiV`,
- vorhandene Konflikte oder noch offene Entscheidungen.

Eine Änderung darf nicht allein deshalb übernommen werden, weil die technischen Prüfungen erfolgreich sind.

## Rechte an Beiträgen

Beitragende müssen zur Einreichung aller Inhalte berechtigt sein. Quellen und Drittinhalte sind vollständig zu kennzeichnen.

Mit der Einreichung eines zur Übernahme bestimmten Modellbeitrags erklärt die beitragende Person, dass sie den Beitrag unter CC BY-NC-SA 4.0 bereitstellen darf. Daraus entsteht keine automatische Übertragung weitergehender oder kommerzieller Nutzungsrechte an JUNACO. Solche Rechte erfordern eine gesonderte schriftliche Vereinbarung.

Bis zu dieser Rechteklärung können externe Ideen als Issue diskutiert werden, ohne ihren konkreten Text oder ihre konkrete Darstellung in die Modellspezifikation zu übernehmen.

## Lizenz- und Governance-Dateien

Änderungen an `LICENSE.md`, `NOTICE.md`, `GOVERNANCE.md`, `AGENTS.md` oder `.github/CODEOWNERS` müssen im Pull Request ausdrücklich als solche gekennzeichnet und gesondert begründet werden.
