# JCI-Neo4j-Laufzeit

Diese Laufzeit verbindet die JCI-Referenzprüfungen mit echten, expliziten Neo4j-Transaktionen. Der technische Koordinator liegt in [`jci_runtime/neo4j_store.py`](../../../jci_runtime/neo4j_store.py). Maßgeblich bleiben der [kanonische Kontext](../../JCI_CONTEXT.md), die [SYNC-Spezifikation](../../JCI_SYNC_SPEC.md) und das [Neo4j-Schema](JCI_NEO4J_SCHEMA.md).

Der Koordinator übernimmt den technischen Transaktionsrahmen. Ein vollständiges, vertrauenswürdiges Regelpaket muss weiterhin die fachlichen Entscheidungen, Autorisierung und sämtliche Modellbedingungen prüfen. Die vorhandenen Referenzmodule bilden ausgewählte Regeln und das Freigabeprofil ab; ihre Verwendung allein ergibt keine vollständige produktive SYNC-Engine.

## 1. Technischer Rahmen und fachliche Verantwortung

Alle JCI-Schreibwege desselben Modellbestands benötigen dieselbe technische Schreibsperre. Die Sperre wird vor entscheidungsrelevanten Lesezugriffen erworben und bis zum Commit oder Rollback gehalten. Sie gilt über Organisationsgrenzen hinweg. Ein weiterer Schreibweg, der diesen Vertrag umgeht, würde die Zusage einer konsistenten Entscheidungsgrundlage aufheben.

Neo4j verwendet standardmäßig Read Committed. Das Schreiben und anschließende Entfernen einer temporären Property am gemeinsamen Gate erwirbt den benötigten Schreiblock; dieser bleibt bis zum Transaktionsende bestehen. Grundlage ist die [offizielle Beschreibung konkurrierender Zugriffe](https://neo4j.com/docs/operations-manual/current/database-internals/concurrent-data-access/).

Der Koordinator verwendet explizite Driver-Transaktionen. Fehler und insbesondere ein unbekannter Commit-Ausgang benötigen eine gezielte Wiederaufnahme; eine automatisch erneut ausgeführte fachliche Callback-Funktion wäre dafür kein ausreichender Vertrag. Die Driver-Grundlage beschreibt [Run your own transactions](https://neo4j.com/docs/python-manual/current/transactions/).

Das geprüfte Regelpaket muss zur verwendeten aktiven `SYNC`-Definition, ihren Profilversionen und ihrer `implementationChecksum` passen. Für geschützte Vorgänge gehört `approvalProfileVersion = "1.0"` zur erforderlichen Fähigkeit. Weder die bloße Existenz einer Definition noch eine vom Antragsteller behauptete Paketkennung begründet Ausführungsbefugnis.

Fachliche Prüf- und Schreibfunktionen laufen in der vom Koordinator geöffneten Transaktion. Sie müssen die gesamte relevante Sicht einschließlich erforderlicher Abwesenheiten frisch lesen, den vollständigen Kandidaten prüfen und Zeitbedingungen am serverseitigen `decisionAt` auswerten. Sie dürfen keine eigene Transaktion öffnen und keine externen Nebenwirkungen auslösen. Es gibt keinen fachlich erlaubenden Standardvalidator.

## 2. Konkrete API und erforderliches Regelpaket

`Neo4jStore(driver, *, database, rules, transaction_timeout=30)` übernimmt einen vom Aufrufer verwalteten Neo4j-Driver. Die Datenbank wird ausdrücklich angegeben. Der Konstruktor eröffnet keine Verbindung, installiert keine Strukturen und verändert keinen Graphen. `transaction_timeout` begrenzt die Transaktionsdauer einschließlich des Wartens auf Sperren.

| Methode                                                       | Vertrag                                                                                                                                       |
| ------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------- |
| `install()`                                                   | Installiert wiederholbar technische Constraints und den Gate. Administrativer Einrichtungsschritt; kein fachlicher Bootstrap.                 |
| `accept(payload, *, run_id)`                                  | Prüft Transportprofil, aktive SYNC-Definition und Zielrevision; speichert nach erfolgreichem Annahme-Hook Auftrag und ersten Run atomar.      |
| `claim(run_id, worker_id, *, expected_fence=None)`            | Übernimmt einen noch offenen Run mit neuem Fencing-Token; bei einem laufenden Run muss der aktuelle Token ausdrücklich angegeben werden.      |
| `retry(previous_run_id, *, run_id)`                           | Plant nach dokumentiertem `FAILED` oder `CONFLICT` genau einen neuen Run für denselben unveränderten Auftrag; gleiche Planung ist idempotent. |
| `execute(token)`                                              | Führt genau einen geschützten Versuch aus und gibt das bestätigte Ergebnis zurück; keine automatische Wiederholung der Hooks.                 |
| `recover(run_id)`                                             | Liest unter dem Gate den dauerhaften Runzustand, den aktuellen Token und ein vorhandenes Ergebnis.                                            |
| `finish_failed(token, *, outcome, error_code, error_message)` | Dokumentiert nach geklärtem Ausgang ausdrücklich `FAILED` oder `CONFLICT`; führt das Fachdelta nicht erneut aus.                              |

`accept` liefert `AcceptedRequest(request_id, idempotency_key, run_id)`. Eine identische erneute Annahme liefert den bereits geplanten ersten Run; eine dabei mitgesendete neue Run-ID plant keinen zweiten Lauf. `claim` liefert `RunToken(request_id, run_id, worker_id, fence)`. `recover` liefert `Recovery(state, token, result)`; mögliche Zustände sind `QUEUED`, `RUNNING`, `SUCCESS`, `CONFLICT` und `FAILED`.

Der Scheduler entscheidet ausdrücklich, wann ein laufender Run übernommen werden soll. Er liest zunächst `recover(run_id)` und verwendet dessen `token.fence` als `expected_fence`. Der Koordinator implementiert keine automatische Worker-Ausfallerkennung oder Lease-Verlängerung. Ein veralteter Token verliert die Schreibbefugnis; ein bereits abgeschlossenes Ergebnis kann unverändert gelesen werden.

`retry(previous_run_id, *, run_id)` liefert `AcceptedRequest` und plant ausdrücklich genau einen neuen Versuch nach einem bereits dokumentierten `FAILED` oder `CONFLICT`. Payload, `requestedRevision`, `requestId`, `idempotencyKey` und `ChangeEvent` bleiben unverändert; nur der neue Run erhält eine neue Identität. Dieselbe Wiederholungsplanung mit derselben Run-ID ist idempotent. Eine andere zweite Nachfolger-ID wird abgewiesen. Ein laufender Versuch oder unbekannter Ausgang muss zuerst geklärt und abgeschlossen werden. Ein bereits erfolgreicher Auftrag wird nicht erneut eingeplant; die wiederholte Abfrage einer schon vorhandenen Nachfolgeplanung erzeugt keinen weiteren Run.

`recover` bleibt auf den angegebenen Versuch bezogen: Das Ergebnis eines früheren `FAILED` oder `CONFLICT` bleibt auch nach einem späteren `SUCCESS` desselben Auftrags lesbar. Eine Wiederholung auf unveränderter, inzwischen veralteter Zielrevision behebt den Revisionskonflikt nicht; für eine andere gewünschte Ausgangsrevision ist ein neuer Auftrag erforderlich.

Das Objekt `rules` muss `package = RulePackage(sync_id, sync_revision, implementation_checksum, schema_version="2.0", approval_profile_version="1.0")` und alle folgenden Methoden bereitstellen:

| Hook                                                                         | Erforderliche Leistung                                                                                                                                       |
| ---------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `accept(tx, payload, run_id, accepted_at)`                                   | Antragsteller authentifizieren, Freigabepflicht ableiten, menschliche Belege prüfen sowie unveränderliches ChangeEvent und Provenienz speichern.             |
| `evaluate(tx, payload)`                                                      | Vollständige aktuelle Grundlage lesen und Kandidat als Mapping mit `readRevisions` und eindeutigen `changedEntityIds` bilden.                                |
| `validate_at(tx, payload, candidate, context)`                               | Alle zeitabhängigen Modell- und Freigabebedingungen an `context.decision_at` erneut prüfen; ausschließlich `True` erlaubt das Schreiben.                     |
| `apply(tx, payload, candidate, context)`                                     | Geprüftes Eigentümerdelta, PiH, erforderliche technische Freigabesperrmerker, SyncEvent und Provenienz speichern; vollständiges `JCISyncResult` zurückgeben. |
| `document_failure(tx, payload, context, outcome, error_code, error_message)` | Ausschließlich Abschluss- und gegebenenfalls Konfliktdokumentation schreiben; vollständiges `JCISyncResult` zurückgeben.                                     |

`ExecutionContext` enthält `request_id`, `run_id`, `worker_id`, `fence`, `graph_epoch`, `started_at` und `decision_at`. Die Hooks dürfen die technischen Request-, Run-, Commit- und Outbox-Belege des Koordinators nicht verändern. Ihre Abfragen müssen innerhalb der übergebenen Transaktion ausgewertet werden. Nicht unterstützte Regeln oder Vorgänge werden abgewiesen.

Nach `validate_at` friert der Koordinator `readRevisions` und `changedEntityIds` ein und gleicht die angegebenen Leserevisionen mit dem gesperrten Graphen ab. Als neu deklarierte Eigentümer müssen vor `apply` tatsächlich im Graphen fehlen; bestehende geänderte Eigentümer benötigen ihre maßgebliche Leserevision. Nach `apply` prüft er für bestehende geänderte Eigentümer Revision `+1` und genau ein zugehöriges PiH mit passender `originalEntityId` und `originalRevision`; neue Eigentümer beginnen mit Revision 1 ohne PiH. Diese begrenzten Persistenzprüfungen ergänzen die Pflicht des Regelpakets, das vollständige tatsächliche Fachdelta korrekt abzuleiten.

Der Koordinator vergleicht Paketkennung und Prüfsumme mit der gespeicherten aktiven SYNC-Definition. Die vertrauenswürdige Installation muss zuvor nachweisen, dass die Prüfsumme tatsächlich das geladene, geprüfte Implementierungsartefakt bezeichnet. Der Koordinator berechnet keine Prüfsumme beliebiger Python-Objekte und ergänzt keine fehlende fachliche Validierung. Insbesondere reichen gelieferte Revisions- und Änderungslisten allein nicht als Beleg ihrer fachlichen Vollständigkeit.

Das folgende Integrationsbeispiel setzt einen eingerichteten Gate, eine passende aktive SYNC-Definition und das vollständige vertrauenswürdige Regelpaket voraus:

```python
from jci_runtime.neo4j_store import Neo4jStore


def process_request(driver, trusted_rules, payload, run_id, worker_id):
    store = Neo4jStore(driver, database="neo4j", rules=trusted_rules)
    accepted = store.accept(payload, run_id=run_id)
    previous = store.recover(accepted.run_id)
    if previous.result is not None:
        return previous.result
    token = store.claim(accepted.run_id, worker_id)
    return store.execute(token)
```

Der Aufrufer behandelt `CommitOutcomeUnknown` durch `recover` für dieselbe Run-ID. Nach einem gewöhnlichen Validierungsfehler erfolgt ebenfalls zuerst der Abgleich, anschließend gegebenenfalls `finish_failed`. Die gezeigte Funktion ist keine automatische Retry-Schleife. UI und Speicherung wartender oder abgelehnter Freigabevorschläge, Authentifizierung sowie Zustellung und Quittierung der Outbox benötigen eigene Integrationen.

## 3. Dauerhafter Auftrag und geschützter Abschluss

Die Annahme bindet den vollständigen kanonischen Payload unveränderlich an `requestId` und `idempotencyKey`. Ziel, angeforderte Revision, Profile, Operationen und gegebenenfalls Freigabebelege bleiben wiederherstellbar. Derselbe Auftrag kann technisch wiederholt werden; eine andere Ausgangsrevision oder ein anderer Inhalt benötigt einen neuen Auftrag.

Ein technischer Run besitzt eine eigene `runId` und einen Fencing-Token. Bei einer Übernahme durch einen anderen Worker darf der frühere Eigentümer keine fachliche Änderung oder widersprechende Abschlussdokumentation mehr speichern. Auch Recovery verwendet den gemeinsamen Gate und prüft zuerst den dauerhaft gespeicherten Ausgang.

Bei `SUCCESS` gehören Fachdelta, zugeordnete `PiH`, Beziehungen, historische Korrekturen, genau ein `SyncEvent`, der Erfolgsbeleg und die Outbox in dieselbe atomare Transaktion. Das tatsächliche Fachdelta bestimmt Revisionen und Zähler. Neue Ziele beginnen mit Revision 1 ohne eigenes PiH; geänderte vorhandene Eigentümer erhalten genau eine neue Revision und ein PiH. Ein No-op erzeugt keine fiktive Historie und wird trotzdem dauerhaft als verarbeitet markiert.

Ein bestätigter Rollback übernimmt kein Fachdelta. Die erforderliche `FAILED`- oder `CONFLICT`-Abschlussdokumentation wird unter dem Gate nachgeholt. Bei unbekanntem Commit-Ausgang muss zuerst der Beleg derselben `runId` gelesen werden. Solange der Ausgang nicht geklärt ist, darf die Fachänderung nicht erneut ausgeführt werden. Ein bereits gespeicherter Erfolg wird unverändert zurückgegeben.

Die technische `graphEpoch` macht auch revisionsneutrale JCI-Schreibvorgänge sichtbar. Sie ersetzt weder den Gate noch die abschließende Zeitprüfung. `decisionAt` bezeichnet den geschützten fachlichen Prüfzeitpunkt; `completedAt` bezeichnet den Abschluss. Gültigkeit bei einer späteren externen Handlung wird dadurch nicht garantiert.

Outbox-Inhalte werden erst nach Commit zugestellt. Nach einem Dispatcher-Absturz kann dieselbe Nachricht erneut geliefert werden. Der Empfänger muss anhand der stabilen Ereigniskennung deduplizieren; eine erfolgreiche Fachtransaktion bedeutet keine automatisch genau einmal ausgeführte externe Wirkung.

## 4. Installation und reale Integrationstests

Die Abhängigkeiten werden im Repository-Stamm installiert:

```powershell
python -m pip install -r requirements-dev.txt
python -m pip install -r requirements-runtime.txt
```

Für eine lokale Testinstanz steht [`compose.neo4j-test.yml`](../../../compose.neo4j-test.yml) bereit. Sie verwendet das offizielle Community-Image `neo4j:2026.08.1`, veröffentlicht ausschließlich Bolt auf `127.0.0.1:17687` und bindet keine Host-Datenverzeichnisse ein. HTTP/HTTPS sind deaktiviert. Die ausgeschaltete Authentifizierung gilt ausschließlich für diesen isolierten lokalen Testdienst. Der Community-Tag hat keinen Editionszusatz; siehe [Neo4j in Docker](https://neo4j.com/docs/operations-manual/current/docker/introduction/).

Mit laufendem Docker-Dienst und Docker Compose wird die Instanz gestartet und bis zur Bereitschaft gewartet:

```powershell
docker compose -f compose.neo4j-test.yml up -d --wait
```

`--wait` berücksichtigt den konfigurierten Healthcheck; siehe [docker compose up](https://docs.docker.com/reference/cli/docker/compose/up/). Ist bereits eine andere lokale Testinstanz auf Port 17687 aktiv, wird entweder diese verwendet oder zuerst beendet.

Die Integrationstests benötigen eine ausschließlich dafür bereitgestellte Neo4j-Instanz. Der folgende Aufruf verwendet die Standarddatenbank `neo4j`; die URI ist an die eigene isolierte Instanz anzupassen:

```powershell
$env:JCI_NEO4J_TEST_URI = "bolt://127.0.0.1:17687"
$env:JCI_NEO4J_TEST_CONFIRM = "isolated"
$env:JCI_NEO4J_TEST_DATABASE = "neo4j"
python -B -m unittest discover -s tests/integration -v
```

Benötigt die Testinstanz Authentifizierung, werden `JCI_NEO4J_TEST_USER` und `JCI_NEO4J_TEST_PASSWORD` zusätzlich aus einer lokalen, geschützten Konfiguration gesetzt. Zugangsdaten gehören weder in diese Dokumentation noch ins Repository. Die Bestätigung `isolated` bezeichnet bewusst einen entbehrlichen Testbestand; produktive oder gemeinsam genutzte Datenbanken sind kein zulässiges Testziel.

`JCI_NEO4J_TEST_DATABASE` ist optional und verwendet ohne Angabe `neo4j`. Die Tests erzeugen eigene Objekte mit neuen UUIDs und führen keinen Datenbankreset oder globale Löschung aus. Testdaten bleiben in der isolierten Instanz zur Prüfung erhalten.

Nach dem Testen werden ausschließlich der Compose-Testdienst und seine zugehörigen entbehrlichen Volumes entfernt:

```powershell
docker compose -f compose.neo4j-test.yml down --volumes
```

Dabei werden die lokalen Testdaten dieser Instanz verworfen; siehe [docker compose down](https://docs.docker.com/reference/cli/docker/compose/down/). Der Job `neo4j-integration` in [GitHub Actions](../../../.github/workflows/validate.yml) startet denselben Image-Tag als isolierten Dienst und führt die Integrationstests bei Pull Requests und Pushes auf `main` aus. Dort wird Bolt über den lokalen Port 7687 bereitgestellt.

Die Suite prüft konkurrierende Aufträge, neu hinzukommende und revisionsneutrale Entscheidungsdaten, Ziel- und Paketrevisionen, Ablaufzeiten, Rollback, veraltete Fencing-Tokens, verlorene Antworten bei `accept` und `execute`, ausdrückliche Wiederholungen über `retry`, den finalen Lesenachweis und Manipulationsversuche an diesem Nachweis. Ein eigener Fall beendet einen echten Worker-Prozess vor Commit und prüft anschließend Rollback, Recovery und Wiederholung.

Diese Fälle verwenden den realen Transaktionskoordinator mit einem begrenzten Test-Regelpaket. Sie belegen keine Server- oder Stromausfallsicherheit und ersetzen weder eine vollständige fachliche JCI-End-to-End-Prüfung noch eine produktive Identitätsintegration. Ein übersprungener Testlauf ohne konfigurierte Datenbank ist kein Nachweis von Transaktionsisolation. Die reine Referenzsuite bleibt separat ausführbar:

```powershell
python -B -m unittest discover -s tests -v
```

## 5. Historische Korrekturen und bestehende Daten

Die Referenzkorrektur vergleicht vollständige Beziehungseinträge mit der unmittelbar vorherigen wirksamen `HistoryView`. Das gilt auch dann, wenn eine frühere `ADDITION` die Beziehung erst ergänzt hat. `CORRECTION` und `CLARIFICATION` dürfen Richtung, Beziehungstyp, Gegenentitäts-ID oder Gegenentitätstyp unter derselben Adresse nicht verändern. Beim Wiederaufbau werden zusätzlich die Identitäten entlang der gespeicherten `SUPERSEDES`-Kette geprüft.

Zulässige Änderungen von Beziehungseigenschaften bleiben möglich. Die Sicht überlagert weiterhin ausschließlich aktive absolute `correctedValue`-Werte auf den unveränderten Ursprung. Frühere `previousValue`-Bedingungen werden nicht erneut gegen das Original-PiH geprüft. Regressionen decken sowohl den unzulässigen Typwechsel als auch gültige aufeinanderfolgende Änderungen von `validFrom` und `validUntil` ab.

Die Einrichtung technischer Laufzeitstrukturen ist weder ein fachlicher Bootstrap noch eine automatische Datenmigration. Bei einem vorhandenen Bestand müssen vor der Aktivierung Profile, gültige Zustände, Revisionseigentum, Task-/Kriterienumfänge, gemischte Abschlusszyklen und historische Korrekturketten geprüft werden. Unklare Fälle benötigen nachvollziehbare fachliche Entscheidungen.

Alte PiH, Korrekturen und gespeicherte Hashes bleiben unverändert. Für jedes tatsächlich vorhandene Altprofil ist ein ausdrücklich geprüfter Resolver erforderlich; erhaltene Legacy-Schemas allein implementieren diesen Resolver nicht. Der Koordinator erfindet weder historische Freigaben noch neue Identitäten und schreibt alte Snapshots nicht automatisch auf Profil 2.0 um. Vor-/Nachvalidierung, Sicherung und eine konkrete Migration bleiben ein eigener Einführungsschritt, sofern Altdaten vorhanden sind.

## 6. Auswirkungen auf den Loop und verbleibende Integration

Alle zehn Kernelemente behalten ihre fachliche Bedeutung: `CiV` bewahrt die menschliche Wertentscheidung; `PiF2`, `PiF1s`, `PiF1t` und `PiF1o` behalten ihre Zukunfts- und Beitragslogik; `RaN` liefert die Regeln; `RoF` die nachgewiesenen Akteure; `ERoF` die getrennten Umwelt- und Nutzungsbedingungen. `SYNC` erhält einen ausführbaren technischen Transaktionsrahmen. `PiH` entsteht weiterhin ausschließlich bei tatsächlicher Ablösung vorhandener Zustände. Die WHY-Rückverfolgbarkeit bleibt erhalten, und technische Laufzeitbelege werden nicht zu zusätzlichen JCI-Kernelementen.

Für eine produktive Einführung müssen das vollständige versionierte Regelpaket, die vertrauenswürdige Identitäts- und Freigabeprüfung, alle fachlichen Schreibwege, die Betriebsrechte, der Outbox-Empfänger und gegebenenfalls der Altprofil-Resolver zusammen bereitstehen. Ein Test-Regelpaket darf nicht als produktiver Modellvalidator registriert werden. Offene fachliche Spezifikationsfragen werden durch die technische Transaktionsschicht nicht entschieden.
