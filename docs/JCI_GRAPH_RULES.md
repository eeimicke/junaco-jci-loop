# JCI-Graphregeln

## Status und Zweck

Dieses Dokument spezifiziert künftig die technologieunabhängigen Regeln und Invarianten des JCI-Graphen. Die fachliche Bedeutung der Elemente und Beziehungen wird ausschließlich durch [JCI_CONTEXT.md](JCI_CONTEXT.md) festgelegt.

## Inhalt dieser Spezifikation

Die Graphregeln sollen verbindlich festlegen:

- Kardinalitäten aller gespeicherten Beziehungen,
- Bedingungen für Entwurf, aktiven und abgeschlossenen Zustand,
- zulässige Quell- und Zieltypen,
- Eindeutigkeits- und Vollständigkeitsregeln,
- Regeln für `RoFOrg`, Teams, Mitglieder, Rollen und `RoleAssignment`,
- Zyklusfreiheit und Elternregeln für `SUBSIDIARY`,
- personengebundene Ableitung der `ERoF`,
- Regeln für Result, Verification und SuccessCriterion,
- Historisierbarkeit und Unveränderlichkeit von `PiH`, `ChangeEvent` und `SyncEvent`.

## Abgrenzung

Dieses Dokument beschreibt, welche Graphzustände gültig sind. Es beschreibt nicht, wie `SYNC` den Graphen traversiert oder wie eine konkrete Datenbank die Regeln technisch erzwingt.

## Noch zu spezifizieren

- vollständige Invarianten je Entitäts- und Beziehungstyp,
- Statusübergänge und ihre Vorbedingungen,
- Aggregation mehrerer Erfolgskriterien,
- Parent- und Subtask-Regeln,
- Konflikt- und Prioritätsregeln für `RaN`,
- Validierungsregeln für historische Zustände.
