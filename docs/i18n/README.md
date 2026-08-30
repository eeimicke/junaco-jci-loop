# Übersetzungsregeln

## Verbindlichkeit

- `docs/JCI_CONTEXT.md` ist die kanonische fachliche Quelle.
- Dateien unter `docs/en/` sind kontrollierte englische Übersetzungen.
- Eine Übersetzung darf keine Entität, Beziehung, Kardinalität oder Regel hinzufügen, entfernen oder umdeuten.
- Kanonische Bezeichner wie `PiF1o`, `RoleAssignment`, `EXECUTED_BY` und Statuswerte werden nicht übersetzt.
- Technische Artefakte werden nicht dupliziert.

## Pflege

Eine Änderung an einer deutschen Quelldatei setzt die zugehörige Übersetzung zunächst auf `review-required`. Nach inhaltlichem Abgleich wird sie wieder als `synchronized` markiert. Der automatische Test prüft Dateipaare, Kapitel, Entitätstypen, Beziehungen und Mermaid-Blöcke.

Rechtliche Übersetzungen sind als unverbindliche Verständnishilfe gekennzeichnet. Maßgeblich bleibt die deutsche Fassung beziehungsweise der verlinkte rechtsverbindliche Lizenztext.

