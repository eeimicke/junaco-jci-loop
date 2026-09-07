# Kanonische Diagrammquellen

[Deutsch](README.md) · [English](README.en.md)

Die `.mmd`-Dateien enthalten die strukturell verbindlichen Mermaid-Quellen der Dokumentationsgrafiken. Übersetzte Dokumente dürfen Beschriftungen übersetzen, aber keine JCI-Entität oder Beziehung verändern.

| Datei                                                                | Inhalt                                             |
| -------------------------------------------------------------------- | -------------------------------------------------- |
| [`jci-loop.mmd`](jci-loop.mmd)                                       | Gesamtzusammenhang des Loops                       |
| [`entity-model.mmd`](entity-model.mmd)                               | Typordnung der gespeicherten Entitäten             |
| [`future-chain.mmd`](future-chain.mmd)                               | Zukunftskette und WHY-Pfad                         |
| [`rof-model.mmd`](rof-model.mmd)                                     | Organisation, Team, Mitglied und Rollenaktivierung |
| [`erof-model.mmd`](erof-model.mmd)                                   | personengebundener Umweltkontext                   |
| [`task-verification.mmd`](task-verification.mmd)                     | Arbeit, Ergebnis und Prüfung                       |
| [`ran-evaluation.mmd`](ran-evaluation.mmd)                           | Regelauswertung und Konflikt                       |
| [`sync-history.mmd`](sync-history.mmd)                               | Änderung, Synchronisation und Historisierung       |
| [`example-complete-entity-map.mmd`](example-complete-entity-map.mmd) | Vollständige Entitätskarte des Beispiels           |
| [`example-purpose-future.mmd`](example-purpose-future.mmd)           | Werte, Zweck, Zukunft und Erfolgskriterium         |
| [`example-organisation.mmd`](example-organisation.mmd)               | Organisation, Team, Rollen und Partnerschaft       |
| [`example-task-execution.mmd`](example-task-execution.mmd)           | Task-Hierarchie und ausdrückliche Voraussetzungen  |
| [`example-environment.mmd`](example-environment.mmd)                 | Personengebundene Umwelt und Schutz                |
| [`example-ran-types.mmd`](example-ran-types.mmd)                     | Regeltypen, Wirkung und Geltungsbereich            |
| [`example-ran-conflict.mmd`](example-ran-conflict.mmd)               | Nachvollziehbarer Regelkonflikt                    |
| [`example-sync-outcomes.mmd`](example-sync-outcomes.mmd)             | Geschützter Abschluss und drei SYNC-Ausgänge       |
| [`example-history-correction.mmd`](example-history-correction.mmd)   | Unveränderte PiH und Korrekturüberlagerung         |

Benannte JCI-Kanten verwenden ausschließlich kanonische Beziehungsnamen. Unbenannte Prozesspfeile und gestrichelte Erläuterungen beschreiben Ablauf oder Prüfbedingungen; sie führen keine neuen gespeicherten JCI-Beziehungen ein. Die Diagramme zu Tasks, Prüfung, SYNC und Korrektur ergänzen die [Logikänderungen 2.0](../../changes/JCI_LOGIC_2_0.md). Der gemeinsame Abschlussgraph bleibt eine abgeleitete Sicht auf vorhandene `DECOMPOSES_INTO`- und `DEPENDS_ON`-Kanten.
