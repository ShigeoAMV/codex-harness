# Optionales Web/API-Profil

Nur fuer Projekte mit entsprechenden Schnittstellen. Dies ist eine Abnahmevorlage,
keine fertige Scannerkonfiguration und kein zusaetzlicher Pflichtdienst des Harness.
Bestehende Tests und Dokumentation weiterverwenden.

## Ziel und Autorisierung

Vor aktiven Tests explizit autorisierte, isolierte Testumgebung, Host-/Pfadumfang,
erlaubte Methoden, Rate/Zeitbudget und Abbruchkriterien dokumentieren. Synthetische
Daten und Testkonten, keine Produktivzugriffe. Auch Schemathesis kann mutierende
Anfragen erzeugen; auch ein Scan mit Login kann Daten loeschen. Restore/Reset
vorbereiten. Netzreichweite technisch auf erlaubte Ziele begrenzen.

## Risikobasierte Abdeckung

| Bereich | Nachweis |
| --- | --- |
| Authentifizierung | Gueltige, fehlende, abgelaufene und manipulierte Sessions/Tokens; Logout/Recovery soweit anwendbar |
| Berechtigungen | Direkte API-Anfragen je Rolle und Aktion; eigene/fremde Ressourcen, IDOR/BOLA, Cross-Tenant-Zugriff und Rollenwechsel |
| Dateninvarianten | Manipulierte Preise/Rollen, wiederholte Transaktionen, Mass Assignment und Fehlerpfade; keine unberechtigte Zustandsaenderung |
| ZAP | Reale Webziele mit erreichter URL-/Rollenliste; Scanmodus und blockierende Regeln festhalten |
| Schemathesis | Passendes versioniertes OpenAPI-/GraphQL-Schema, tatsaechlich erreichte Operationen, Reproduktion/Seed und Report |
| ASVS 5.0.0 | Relevante Anforderungen mit versionierten IDs auf Tests/manuelle Nachweise abbilden; keine pauschale ASVS-Konformitaetsbehauptung |

Eine Authentifizierung ist erst nachgewiesen, wenn eine geschuetzte Kontrollroute
mit Testidentitaet ihren erwarteten Inhalt liefert. HTTP 200 einer Loginseite ist
kein Nachweis. Rollen und Tenants separat pruefen, Coverage mit der Soll-Liste
vergleichen und Loginverlust waehrend des Scans erkennen. Nicht erreichte Bereiche
als Luecke melden; positive Loginproben ersetzen keine negativen Autorisierungstests.

## Einbindung

Toolversionen und Regeln pinnen; Secrets ueber die freigegebene Runtime beziehen,
nicht in `argv`, Reports oder Git. Scans nach Risiko in `security`/`release`
eintragen, nicht automatisch bei jedem Edit. Ein Projektadapter muss Finding-
Schwellen, Konfigurationsfehler, null Operationen, verlorene Authentifizierung und
fehlende Pflichtabdeckung mit einem Fehlercode melden. Originalreport, Testanzahl,
Ziel, Rollen, Commit, Versionen und Ausnahmen mit Ablaufdatum speichern.

Vor Abnahme einen bekannten synthetischen Fehler nachweisen und anschliessend
einen bereinigten Lauf ausfuehren. ZAP/Schemathesis erkennen nicht automatisch jede
Geschaeftsregel oder Tenant-Grenze; die expliziten negativen Anwendungstests bleiben.
Shannon/Strix nur als begrenzten Pilot mit gesonderter Autorisierung, Kostenlimit
und gemessenem Zusatznutzen evaluieren.

Primarquellen: [ASVS 5.0.0](https://github.com/OWASP/ASVS/tree/v5.0.0),
[ZAP](https://github.com/zaproxy/zaproxy),
[Schemathesis](https://github.com/schemathesis/schemathesis).
