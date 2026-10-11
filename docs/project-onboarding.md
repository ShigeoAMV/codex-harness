# Projekt anbinden: die wichtigsten Hebel

Diese Anleitung ist der Arbeitsauftrag fuer den Codex im Zielprojekt. Vorhandene
Tools und Dokumentation weiterverwenden. Keine grossflaechige Neuentwicklung.

## 1. Ist-Zustand erfassen

- Projektanweisungen, Stack, Build-/Testbefehle, Datenhaltung und Deployment lesen.
- Vorhandene Checks ausfuehren; bestehende Fehler getrennt ausweisen.
- Kritische Nutzerablaeufe, Berechtigungs-/Tenant-Grenzen und sensible Daten kurz
  festhalten. Intern/public und moeglichen Schadensumfang bestimmen.

### Grosse Architekturhebel: bewaehrte Komponenten statt Eigenbau

Bei der Bestandsaufnahme und vor neuen sicherheitskritischen Funktionen diese
Entscheidungen explizit pruefen. Nur relevante Bausteine betrachten; keine neue
Dienstelandschaft und keine Migration ohne nachweisbaren Nutzen.

| Falls das Projekt ... | Bevorzugt evaluieren | Bleibt Aufgabe der Anwendung / des Betreibers |
| --- | --- | --- |
| oeffentliche Benutzerkonten braucht | Auth as a Service; alternativ geeignete vorhandene Framework-Auth oder Identity-Provider | Tokens/Sessions korrekt validieren, Rechte und Tenant-Grenzen serverseitig pruefen, negative Zugriffstests |
| Daten speichert | Gepflegte Datenzugriffsbibliothek mit parametrisierten Abfragen und Transaktionen | Ressourcenbesitz, Dateninvarianten, atomare Aenderungen und Migrationstests; ein ORM macht rohes SQL nicht automatisch sicher |
| Zahlungen annimmt | Gehosteter Checkout eines etablierten Zahlungsanbieters | Preise/Bestellungen serverseitig zuordnen, Webhooks verifizieren und idempotent verarbeiten; Browser-Erfolgsmeldung nicht als Zahlungsbeleg behandeln |
| Dateien annimmt | Bewaehrte Upload-Komponenten und privater Objektspeicher | Zugriff, Groessen-/Typgrenzen und sichere Auslieferung; ein Speicheranbieter macht Uploads nicht automatisch harmlos |
| oeffentlich betrieben wird | Gepflegter Reverse Proxy oder Plattform fuer TLS und passende Rate-/Ressourcenlimits | Admin-/Debug-/DB-Zugaenge nicht unnoetig exponieren; Limits an teuren und missbrauchsrelevanten Endpunkten testen |
| wichtige Daten/verbindlichen Betrieb hat | Managed Datenbank/Hosting pruefen, wenn eigener Patch-/Backup-Betrieb nicht verlaesslich abgedeckt ist | Zustaendigkeiten, Wiederherstellung und wenige handlungsrelevante Fehler-/Ausfallalarme nachweisen |

**Auth ist eine ausdrueckliche Architekturentscheidung:** bei oeffentlichen Diensten
mit Konten Managed Auth zuerst evaluieren, aber keine Konten hinzufuegen, wenn sie
nicht gebraucht werden. MFA, Account-Recovery, Sessions und Missbrauchsschutz passend
zum Risiko betrachten. Gepflegte SDKs/Protokollbibliotheken verwenden, keine eigene
Kryptografie entwickeln. Eine bewaehrte vorhandene Loesung nicht reflexartig ersetzen.
Authentifizierung beantwortet, wer jemand ist; die Anwendung muss weiterhin pruefen,
auf welche konkrete Ressource diese Person zugreifen darf.

Kurz mit dem Nutzer abwaegen: Wiederverwendung, Dienst oder Self-Hosting; erwartete
Risikoreduktion, verbleibender Betriebsaufwand, Datenschutz, Kosten bei realistischem
Wachstum und Wechselmoeglichkeit. Free-Tier ist keine dauerhafte Nullkosten-Garantie.
Die Vorgabe ohne Zusatzabos bleibt bestehen: keinen kostenpflichtigen Dienst buchen,
keine Daten uebermitteln und keine Migration allein aus dieser Empfehlung ableiten.
Eine gepflegte selbst betriebene Loesung ist gueltig, wenn ihre Betriebsaufgaben
abgedeckt sind. Entscheidung und offene Pflichten in vorhandener Projektdokumentation
festhalten; keine separate umfangreiche Bewertung fuer jeden Baustein.

Technische Referenzen: OWASP zu [Authentifizierung](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html),
[Berechtigungen](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html),
[SQL-Injection](https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html),
[Uploads](https://cheatsheetseries.owasp.org/cheatsheets/File_Upload_Cheat_Sheet.html),
[Zahlungsintegration](https://cheatsheetseries.owasp.org/cheatsheets/Third_Party_Payment_Gateway_Integration_Cheat_Sheet.html) und
[API-Sicherheit](https://cheatsheetseries.owasp.org/cheatsheets/REST_Security_Cheat_Sheet.html).

### Bestehende Anwendung stabilisieren

Bei grossen oder wenig abgesicherten Altbestaenden diesen Ablauf mit dem Nutzer
priorisieren und mit den folgenden Test-/Scanner-Schritten verbinden:

1. **Bereiche und Verbindungen erfassen:** die Anwendung in zusammenhaengende
   Bereiche gliedern, etwa Auth, Datenzugriff und zentrale Geschaeftsablaeufe. Wichtige
   Abhaengigkeiten, Datenfluesse und gemeinsame Helfer mit aufnehmen. Den gesamten
   relevanten Altbestand erfassen, nicht nur kuerzlich geaenderte Dateien.
2. **Sollverhalten klaeren:** Anforderungen aus vorhandener Dokumentation und
   Nutzerabsicht ableiten. Offene kritische Fragen mit dem Nutzer klaeren. Bestehendes
   Verhalten liefert Hinweise, ist aber kein Beweis fuer Korrektheit; bekannte Fehler
   nicht durch Tests als Sollzustand festschreiben.
3. **Nach Risiko pruefen:** zuerst Berechtigungen/Tenant-Grenzen, Secrets, Datenverlust,
   Transaktionen und oeffentliche Schnittstellen; danach wichtige Funktionsfehler und
   Wartbarkeit. Scanner breit einsetzen, Code-Reviews bereichsweise vertiefen und das
   Zusammenspiel der Bereiche pruefen. Ein PR-Review neuer Aenderungen ersetzt keinen
   Review des vorhandenen Bereichs einschliesslich seiner Abhaengigkeiten.
4. **Gezielt reparieren:** je Befund Reproduktion und aussagekraeftigen Test erstellen,
   eine kleine Reparatur umsetzen und separat reviewen lassen. Wo ein automatisierter
   Test nicht praktikabel ist, die reproduzierbare Pruefung und verbleibende Luecke
   dokumentieren. Funktionierendes Verhalten schuetzen; Refactoring nur fuer konkrete
   Probleme, kein pauschaler Rewrite und keine rein kosmetische Sanierung.
5. **Pruefstand sichtbar halten:** in der bestehenden Statustabelle je Bereich
   Prioritaet, Stand (offen/in Pruefung/geprueft mit Restbefunden/abgeschlossen),
   geprueften Commit, Umfang, Nachweise und offene Punkte festhalten. Abgeschlossen
   heisst: vereinbarte Kriterien erfuellt, Regression geprueft und Review erledigt;
   Ausnahmen bleiben sichtbar. Bei relevanten Aenderungen die betroffenen Nachweise
   aktualisieren. Ein gruener Scannerlauf bedeutet nicht, dass der Bereich umfassend
   geprueft oder die Anwendung fehlerfrei ist.

## 2. Tests und Scanner anbinden

- Die wichtigsten bisher ungeschuetzten Ablaeufe und negativen Berechtigungsfaelle
  testen. Bekannte Fehler nicht als erwartetes Verhalten festschreiben.
- **Frontend als manipulierbar behandeln:** Berechtigungen, Eingaben und
  Geschaeftsregeln muessen serverseitig gelten, auch ohne die vorgesehene UI.
  In der Testumgebung direkte API-Anfragen mit fremden Ressourcen-/Tenant-IDs,
  manipulierten Rollen/Preisen, fehlenden/ungueltigen Sessions und umgangener
  Formularvalidierung pruefen, soweit anwendbar. Erwartung: Ablehnung oder korrekt
  serverseitig bestimmte Werte, keine unberechtigte Datenfreigabe oder Zustandsaenderung.
  Keine privilegierten Backend-/Datenbank-Schluessel im Browser ausliefern. Getrennte
  Domains/Repositories, versteckte Buttons und CORS ersetzen keine Zugriffskontrolle.
- **Gitleaks:** geaenderte Inhalte schnell pruefen; vor Release relevante Git-Historie.
- **SAST:** OpenGrep, Semgrep oder vorhandene gleichwertige Checks passend zum Stack
  waehlen. Engine und Regeln auf konkrete Versionen pinnen; nicht zwei weitgehend
  gleiche Regelsaetze ohne gemessenen Zusatznutzen betreiben. CodeQL nur bei
  passender Sprachabdeckung und geklaerter Lizenz/Verfuegbarkeit.
- **Trivy:** Dependencies sowie vorhandene Container/IaC pruefen. Blockierende
  Schweregrade und Fehler-Exitcodes explizit konfigurieren; ein Report allein blockiert nicht.
- Werkzeuge aus offiziellen Quellen beziehen, Versionen und Regeln dokumentieren.
  Vorhandene gleichwertige Pruefungen mit dokumentierter Abdeckung weiterverwenden.
- Echte Befehle in `harness.checks.json` eintragen. Pflichtchecks explizit allen
  passenden `stages` zuordnen; die Stufen erben keine Checks voneinander.
- Mit synthetischen Fehlern in temporaeren Fixtures nachweisen, dass relevante
  Checks fehlschlagen. Keine echten Secrets und keine Testluecken im Produkt hinterlassen.
- Fuer jeden Pflichtcheck festhalten: exakter Befehl, Tool-/Regelversion, Zielumfang,
  tatsaechlich ausgefuehrte Tests/Dateien/Endpoints, Exitcode und frischer Report.
  Dependency-Scans brauchen zudem Advisory-Datenbankstand und erkannte Manifeste.
  Ein fehlendes Tool, null ausgefuehrte Tests, ignorierte Pflichtziele oder ein alter
  Report erfuellen die Abnahme nicht. Wo das Tool trotzdem 0 liefert, muss ein
  kleiner projektspezifischer Adapter diese Bedingungen pruefen und ungleich 0 liefern.
  Danach sowohl einen gueltigen Lauf als auch einen absichtlich fehlerhaften Lauf
  ueber `harness verify` pruefen. Den synthetischen Fund im Report kontrollieren;
  irgendein Fehlercode kann auch ein Toolabsturz sein.
- Abdeckung vor Toolanzahl: Trivy-Secret-Scanning und Gitleaks bzw. zwei SAST-Engines
  koennen sich stark ueberschneiden. Nur belegte Luecken rechtfertigen Doppelbetrieb.
  Fuer stdlib-only Python ohne Container/Dependencies sind fehlende solche Ziele
  ein dokumentiertes Nicht-anwendbar, kein erfolgreicher Dependency-Scan.

## 3. Einen separaten Reviewer waehlen

Standard: **frischer Codex-Review** mit Diff, Anforderungen und relevantem
Codekontext. Bestehende zugelassene externe Reviews koennen diese Aufgabe uebernehmen.
Greptile, CodeRabbit oder Qodo nicht zusaetzlich automatisch auf denselben Diff
ansetzen. Ein anderer Anbieter kann andere Fehler finden; das ist zu messen,
nicht aus Produktwerbung abzuleiten. Auch Codex verbraucht Kontingent.

Vor einem externen Pilot: Codefreigabe fuer genau dieses Repository, Datenhaltung,
App-Berechtigungen, aktuellen Tarif und Limits klaeren. Private GitHub-Sichtbarkeit
ist keine Datenfreigabe; ein Gratis-Tarif wird nicht vorausgesetzt. Keine Buchung
oder automatische Ueberschreitung ohne Zustimmung. Danach an einem kleinen
freigegebenen PR richtigen Commit, neue valide Findings, Fehlalarme und Aufwand
pruefen. Menschliche Integrationsschritte bleiben sichtbar offen.

| Frage / Anlass | Passende Pruefung |
| --- | --- |
| Lokaler Diff, normale Korrektheit | Normaler Codex-Review; Umfang nach Risiko |
| Kritischer Diff | Separater Review mit negativen Tests und gezieltem Security-Fokus |
| Repo-/Komponentenbestand unbekannt | Codex Security Standard Scan, falls verfuegbar und im genehmigten Budget |
| Hohes Risiko und verbleibende konkrete Unsicherheit | Deep Scan gezielt evaluieren; mehrere Durchlaeufe kosten zusaetzlich |
| Bereits validierter Befund | Kleine Reparatur und gezielte Verifikation statt erneutem Vollscan |

Skill-Verfuegbarkeit, Backend-Zugang und Abrechnung sind getrennte Voraussetzungen.
Aktuelle Konditionen im Konto pruefen; keine pauschale Aussage, Codex Security sei
kostenlos oder Bestandteil jedes Codex-Zugangs. Die [Bewertung](evaluation.md)
kennzeichnet den hier tatsaechlich verifizierten Quellenstand.

## 4. Pruefaufwand passend einsetzen

| Zeitpunkt | Pruefung |
| --- | --- |
| Entwicklung | Relevante schnelle Tests/Build-/Typ-/Lintchecks, Secret-Pruefung geaenderter Inhalte; bei reinen Dokumentationsaenderungen entsprechend leichtgewichtig |
| Kritische Aenderung | Negative Tests, passende Scanner und separater Review vor Merge/Release |
| Interner/Homelab-Release | Kritische Ablaeufe und passende Basisscanner; mehr bei sensiblen Daten oder hohen Berechtigungen |
| Public/Produktiv-Release | Vollstaendige relevante Suite, Basisscanner, geklaerte Review-Findings; Laufzeit-, Migrations-/Restore-Pruefungen soweit anwendbar |

Kritisch sind insbesondere Auth, Berechtigungen, Tenant-Isolation, Uploads, URL-Abrufe,
Secrets, Zahlungen/Transaktionen, Migrationen und Release-Steuerung. Fehlender Review
bleibt offen; er wird nicht durch eine Selbsteinschaetzung ersetzt. Entwicklung darf
weitergehen. Nicht nach jeder kleinen Aenderung alle Scans wiederholen.

ZAP fuer geeignete Webziele und Schemathesis fuer passende API-Schemas in isoliertem
Staging ergaenzen. Das optionale [Web/API-Profil](../templates/web-api-profile.md)
enthaelt Abnahmekriterien fuer authentifizierte Abdeckung und ASVS 5.0.
Shannon/Strix erst nach funktionierender Basis evaluieren.

## 5. Kurze Abnahme statt Papierberg

Eine Tabelle in bestehender Projektdokumentation genuegt:

| Baustein | Status | Nachweis / Grund / naechster Schritt |
| --- | --- | --- |
| Tests, Secrets, SAST, Dependencies, Review (je eine Zeile) | eingerichtet / fehlt / Ersatz / nicht anwendbar | Befehl, Commit, Versionen, ausgefuehrte Ziele, frischer Report und negativer Abnahmetest bzw. konkrete Begruendung |

Offene anwendbare Pflichtchecks blockieren die betroffene Freigabe, nicht den gesamten
Entwicklungsalltag. Ausnahmen brauchen menschliche Entscheidung mit Umfang und Ablaufdatum.
Ein gruenes `verify` bedeutet nur, dass konfigurierte Checks bestanden wurden; es
bescheinigt weder vollstaendige Abdeckung noch eine technisch getrennte Release-Freigabe.
Diese Grenze vor produktivem Betrieb gemaess `payload/WORKFLOWS.md` konkret einrichten.
