# Übersetzungsregeln

## Verbindlichkeit

- `docs/JCI_CONTEXT.md` ist die kanonische fachliche Quelle.
- Dateien unter `docs/en/` sind kontrollierte englische Übersetzungen.
- Eine Übersetzung darf keine Entität, Beziehung, Kardinalität oder Regel hinzufügen, entfernen oder umdeuten.
- Kanonische Bezeichner wie `PiF1o`, `RoleAssignment`, `EXECUTED_BY` und Statuswerte werden nicht übersetzt.
- Technische Artefakte werden nicht dupliziert.

## Strukturgleichheit

Deutsch ist die kanonische Sprache. Jede im Übersetzungsmanifest geführte
englische Fassung muss strukturgleich zur deutschen Quelldatei sein.
Strukturgleich bedeutet:

1. gleiche Kapitel und Unterkapitel in derselben Reihenfolge,
2. gleiche Überschriftenebenen,
3. gleiche Tabellen mit derselben Anzahl und Reihenfolge der Zeilen und Spalten,
4. gleiche Code- und Mermaid-Blöcke an derselben inhaltlichen Stelle,
5. gleiche Beispiele, Regeln und Ausnahmen sowie
6. gleiche kanonische JCI-Bezeichner, Kardinalitäten und Statuswerte.

Nur der erklärende Text wird übersetzt. Eine englische Kurzfassung gilt nicht
als Übersetzung der vollständigen deutschen Quelle. Zusätzliche rechtliche
Hinweise dürfen außerhalb des spiegelgleichen Dokumentkörpers stehen, müssen
aber im Übersetzungsmanifest ausdrücklich als Ausnahme gekennzeichnet sein.

## Pflege

Eine Änderung an einer deutschen Quelldatei setzt die zugehörige Übersetzung zunächst auf `review-required`. Nach vollständigem strukturellem und inhaltlichem Abgleich wird sie wieder als `synchronized` markiert. Der automatische Test prüft Dateipaare, Überschriftenstruktur, Tabellenstruktur, Codeblöcke, Entitätstypen, Beziehungen und Mermaid-Blöcke.

Leserorientierte Markdown-Dateien erhalten grundsätzlich ein im Manifest
dokumentiertes Sprachpaar. Bewusst zweisprachige Einzeldateien wie die
Repository-Startseite und sprachneutrale technische Artefakte werden als
Ausnahmen geführt. JSON-Schemas, JSON-LD-Kontexte, Tests, Workflows und
kanonische Mermaid-Quellen werden nicht dupliziert. Sichtbarer Erklärungstext
in solchen Artefakten muss entweder sprachneutral oder kontrolliert
zweisprachig sein.

Rechtliche Übersetzungen sind als unverbindliche Verständnishilfe gekennzeichnet. Maßgeblich bleibt die deutsche Fassung beziehungsweise der verlinkte rechtsverbindliche Lizenztext.

