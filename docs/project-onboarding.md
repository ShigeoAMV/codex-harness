# Projekt anbinden: die wichtigsten Hebel

Diese Anleitung ist der Arbeitsauftrag fuer den Codex im Zielprojekt. Vorhandene
Tools und Dokumentation weiterverwenden. Keine grossflaechige Neuentwicklung.

## 1. Ist-Zustand erfassen

- Projektanweisungen, Stack, Build-/Testbefehle, Datenhaltung und Deployment lesen.
- Vorhandene Checks ausfuehren; bestehende Fehler getrennt ausweisen.
- Kritische Nutzerablaeufe, Berechtigungs-/Tenant-Grenzen und sensible Daten kurz
  festhalten. Intern/public und moeglichen Schadensumfang bestimmen.

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
- **Gitleaks:** geaenderte Inhalte schnell pruefen; vor Release relevante Git-Historie.
- **OpenGrep:** zur Sprache passende Regeln und Engine auf konkrete Versionen pinnen.
- **Trivy:** Dependencies sowie vorhandene Container/IaC pruefen. Blockierende
  Schweregrade und Fehler-Exitcodes explizit konfigurieren; ein Report allein blockiert nicht.
- Werkzeuge aus offiziellen Quellen beziehen, Versionen und Regeln dokumentieren.
  Vorhandene gleichwertige Pruefungen mit dokumentierter Abdeckung weiterverwenden.
- Echte Befehle in `harness.checks.json` eintragen. Pflichtchecks explizit allen
  passenden `stages` zuordnen; die Stufen erben keine Checks voneinander.
- Mit synthetischen Fehlern in temporaeren Fixtures nachweisen, dass relevante
  Checks fehlschlagen. Keine echten Secrets und keine Testluecken im Produkt hinterlassen.

## 3. Greptile als bevorzugten Reviewer einrichten

1. Klaeren, ob Code dieses Repositories an Greptile uebermittelt werden darf. Eine
   private GitHub-Sichtbarkeit allein ist keine Datenfreigabe. Bei Unklarheit lokal bleiben.
2. Den aktuell verfuegbaren kostenlosen Tarif und dessen Kontingent im Konto pruefen.
   Keine kostenpflichtige Buchung oder automatische Ueberschreitung aktivieren.
3. Die offizielle Greptile-GitHub-Integration fuer **dieses ausgewaehlte Repository**
   verbinden. Erforderliche Account-/Organisationsfreigaben erledigt der berechtigte
   Nutzer; Codex dokumentiert einen solchen offenen Schritt, statt ihn als erledigt zu melden.
4. An einem kleinen PR einen Review ausloesen und pruefen, dass Findings zum richtigen
   Commit eintreffen. Review-Regeln auf wichtige Projektinvarianten ausrichten.
5. Kontingent bevorzugt fuer kritische und umfangreiche PRs verwenden. Die konkrete
   Ausloesung nach den verfuegbaren Integrationseinstellungen waehlen; keine ungetestete
   automatische Risikoerkennung voraussetzen.

Wenn Datenfreigabe, Kontingent oder Verfuegbarkeit fehlen: **separater frischer
Codex-Review** mit Diff, Anforderungen und relevantem Codekontext. Gruende fuer den
Ersatz festhalten. Beide Reviewer koennen Fehler uebersehen; Testergebnisse bleiben
verbindlich. Greptile ist Standard, keine unersetzliche Freigabeinstanz.

Anbieterquellen fuer die Einrichtung: [Greptile-Dokumentation](https://www.greptile.com/docs/introduction),
[Tarife](https://www.greptile.com/pricing), [Datenverarbeitung](https://www.greptile.com/security).

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
Staging ergaenzen. Shannon/Strix erst nach funktionierender Basis evaluieren.

## 5. Kurze Abnahme statt Papierberg

Eine Tabelle in bestehender Projektdokumentation genuegt:

| Baustein | Status | Nachweis / Grund / naechster Schritt |
| --- | --- | --- |
| Tests, Gitleaks, OpenGrep, Trivy, Review (je eine Zeile) | eingerichtet / fehlt / Ersatz / nicht anwendbar | Befehl und letzter Lauf bzw. konkrete Begruendung |

Offene anwendbare Pflichtchecks blockieren die betroffene Freigabe, nicht den gesamten
Entwicklungsalltag. Ausnahmen brauchen menschliche Entscheidung mit Umfang und Ablaufdatum.
Ein gruenes `verify` bedeutet nur, dass konfigurierte Checks bestanden wurden; es
bescheinigt weder vollstaendige Abdeckung noch eine technisch getrennte Release-Freigabe.
Diese Grenze vor produktivem Betrieb gemaess `payload/WORKFLOWS.md` konkret einrichten.
