# JCI-SYNC-Spezifikation

## Status und Zweck

Dieses Dokument spezifiziert künftig den technologieunabhängigen Ablauf von `SYNC`. Die fachliche Bedeutung von `SYNC`, `ChangeEvent`, `SyncEvent` und `PiH` richtet sich nach [JCI_CONTEXT.md](JCI_CONTEXT.md).

## Verbindlicher Ausgangspunkt

Der derzeit festgelegte Zusammenhang lautet:

```text
historisierbare JCIEntity ── CHANGED_BY ──► ChangeEvent
ChangeEvent ── TRIGGERS ──► SyncEvent
SyncEvent ── AFFECTS ──► JCIEntity
SyncEvent ── CREATES_HISTORY ──► PiH
historisierbare JCIEntity ── HAS_HISTORICAL_STATE ──► PiH
```

Nur eine tatsächliche Änderung eines bereits vorhandenen Zustands erzeugt ein `PiH`. `PiH`, `ChangeEvent` und `SyncEvent` sind unveränderlich und werden nicht erneut historisiert.

## Inhalt dieser Spezifikation

Die SYNC-Spezifikation soll verbindlich festlegen:

- Startpunkt und Eingaben eines Synchronisationslaufs,
- erlaubte Beziehungstypen und Traversierungsrichtungen,
- direkte und indirekte Betroffenheit,
- Abbruchbedingungen und Zyklenerkennung,
- Prüfung von `RaN`, Kardinalitäten und Invarianten,
- Unterscheidung zwischen Betroffenheit und tatsächlicher Änderung,
- Erzeugung und Verknüpfung von `PiH`,
- Konfliktbehandlung und nicht automatisch entscheidbare Fälle,
- Inhalt und Abschlussstatus eines `SyncEvent`,
- Idempotenz, Wiederholung und Fehlerbehandlung.

## Noch zu spezifizieren

- Traversierungsmatrix je Entitäts- und Beziehungstyp,
- maximale oder semantische Traversierungstiefe,
- Reihenfolge der Prüfungen,
- Regeln für parallele Änderungen,
- Priorisierung konkurrierender `RaN`,
- technikunabhängige Ein- und Ausgabeformate.
