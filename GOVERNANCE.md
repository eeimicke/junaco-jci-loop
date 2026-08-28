# Governance des JCI-Repositorys

## 1. Zweck

Dieses Dokument regelt, wie Änderungen an der Spezifikation des JCI-Modells vorgeschlagen, geprüft und übernommen werden. Die kanonische fachliche Quelle ist `docs/JCI_CONTEXT.md`.

## 2. Verantwortlichkeit im Einzelbetrieb

Im aktuellen Einzelbetrieb liegt die fachliche und technische Freigabe beim Repository-Inhaber. Er darf Änderungen erstellen, prüfen und selbst zusammenführen. Auch eigene Änderungen sollen über einen Branch und einen Pull Request erfolgen, damit Begründung und Prüfergebnis nachvollziehbar bleiben.

Eine zweite menschliche Freigabe ist im Einzelbetrieb nicht verpflichtend. Ein administrativer Regel-Bypass ist nur für die Wiederherstellung einer funktionsfähigen Repository-Konfiguration vorgesehen und muss im betreffenden Pull Request begründet werden.

## 3. Änderungsklassen

| Klasse | Bedeutung | Erforderliche Prüfung |
| --- | --- | --- |
| Redaktionell | Rechtschreibung, Formatierung oder Links ohne Bedeutungsänderung | formale Prüfung und Selbstkontrolle |
| Präzisierung | verständlichere Beschreibung bei unveränderter Semantik | Abgleich mit der gesamten Spezifikation |
| Semantische Änderung | Änderung von Elementen, Beziehungen, Kardinalitäten oder Regeln | vollständige Modell- und Abhängigkeitsprüfung |
| Rechteänderung | Änderung an Lizenz, Quellen oder Rechtezuordnung | gesonderte Rechteprüfung |

Neue JCI-Kernelemente und Änderungen an der Historisierungs-, Synchronisations- oder Rechtearchitektur gelten immer als semantische Änderungen.

## 4. Entscheidungsweg

```text
Vorschlag
→ fachliche Begründung
→ Prüfung betroffener Elemente und Beziehungen
→ Prüfung von Konsistenz und Rechten
→ dokumentierte Entscheidung
→ Änderung der kanonischen Spezifikation
```

Eine automatische Prüfung darf formale Fehler und mögliche Widersprüche melden. Sie entscheidet nicht über die fachliche Richtigkeit einer Modelländerung.

## 5. Beiträge Dritter

Externe Personen dürfen Fehler und Modellvorschläge als Issues einreichen. Ein externer Pull Request mit schöpferischen Modellinhalten wird erst übernommen, wenn Herkunft, Rechteinhaberschaft und die Berechtigung zur Veröffentlichung unter der geltenden Lizenz dokumentiert sind.

Die bloße Übermittlung eines Beitrags überträgt keine Rechte an die JUNACO Organisationsentwicklungs GmbH. Soll JUNACO einen Beitrag zusätzlich kommerziell lizenzieren dürfen, ist vor der Übernahme eine gesonderte Rechtevereinbarung erforderlich.

## 6. Übergang zum Mehrpersonenbetrieb

Sobald mindestens zwei dauerhaft freigabeberechtigte Personen vorhanden sind, soll die Governance erweitert werden:

- mindestens eine Freigabe durch eine andere Person,
- verpflichtende Code-Owner-Freigabe,
- Zurücksetzen alter Freigaben nach neuen Commits,
- gesonderte Freigabe für Lizenz- und Rechteänderungen.

Die Aktivierung dieser Regeln ist als eigene Governance-Änderung zu dokumentieren.

