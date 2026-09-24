# Codex Harness

Ein gemeinsamer, schlanker Codex-Standard fuer Windows und Linux. Schnell entwickeln,
risikobasiert pruefen. Keine zusaetzlichen Abos, Python-Pakete oder Hintergrunddienste.

**Voraussetzungen:** Git, Python 3.11+ und Codex mit Plugin-Unterstuetzung.
Der Harness aendert keine Full-Access-, Modell-, Account- oder Sandbox-Einstellungen.

## Auf einer weiteren Maschine starten

```sh
git clone https://github.com/ShigeoAMV/codex-harness.git
cd codex-harness
git checkout v0.1.1
```

Linux:

```sh
bash harness.sh install
bash harness.sh status
```

Windows, PowerShell:

```powershell
.\harness.ps1 install
.\harness.ps1 status
```

Bei Bedarf `HARNESS_PYTHON` auf den Python-Pfad setzen. `CODEX_HOME` wird beachtet;
alternativ `--codex-home PATH` verwenden. Jede Codex-Instanz braucht die Installation
in ihrem eigenen Benutzer-/Codex-Verzeichnis. Danach eine neue Codex-Aufgabe starten.

### Superpowers einmalig angleichen

Keine Skill-Kopie: den offiziellen Marketplace auf den geprueften Commit pinnen.
Vorher eine lokale Sicherung der Codex-`config.toml` anlegen. Die folgenden nativen
Codex-Befehle verwalten Marketplace und Plugin; `harness rollback` macht sie nicht rueckgaengig.

```sh
codex plugin marketplace add obra/superpowers --ref 5bf4e78011075bcfc0dc295f0724994cd123ee71
codex plugin add superpowers@superpowers-dev
codex plugin list --json
```

Falls `superpowers-dev` bereits mit einem anderen Stand registriert ist, nach der
Konfigurationssicherung zuerst `codex plugin marketplace remove superpowers-dev`
ausfuehren und direkt mit den beiden Installationsbefehlen oben neu registrieren.
Das entfernt die Marketplace-Registrierung, nicht andere Plugins. Schlaegt die neue
Registrierung fehl, die gesicherte Konfiguration wiederherstellen.

Genau eine Superpowers-Installation in Version 6.4.1 aktiv lassen. Eine weitere
Installation in den Codex-Plugin-Einstellungen deaktivieren, nicht ihre Dateien
loeschen. Desktop und CLI koennen unterschiedliche Plugin-Kataloge zeigen; deshalb
nach dem Neustart auch im Desktop pruefen. Andere Plugins bleiben erhalten. Qodo ist
keine Abhaengigkeit und wird vom Harness nicht aufgerufen.

## Updates und Rollback

Updates sind bewusst, nicht automatisch. Auf allen Rechnern denselben freigegebenen
Commit verwenden. Zuerst dessen Diff ansehen, dann:

```sh
git fetch origin --tags
git checkout <freigegebene-vollstaendige-commit-sha>
bash harness.sh update --ref <dieselbe-vollstaendige-commit-sha>
bash harness.sh status
```

Windows verwendet dieselben Argumente mit `.\harness.ps1`. `rollback` stellt jeweils
den vorherigen Regelstand wieder her; nach der ersten Installation die urspruenglichen
Dateien. Es setzt weder den Git-Checkout noch Plugins zurueck. Danach bei Bedarf den
passenden Checkout waehlen.

Der Installer verwaltet nur den markierten Abschnitt in `AGENTS.md` sowie
`harness/WORKFLOWS.md` im Codex-Verzeichnis. Andere Anweisungen bleiben erhalten.
Lokale Aenderungen im verwalteten Teil blockieren Update/Rollback. Eigene Regeln
ausserhalb des Blocks pflegen. `AGENTS.override.md` wird als Vorrangkonflikt gemeldet.
Projekt-/Firmenregeln und MCP-Konfigurationen werden weder ersetzt noch synchronisiert.
Semantische Widersprueche brauchen einen Review; `status` erkennt Dateidrift, keine Bedeutung.
`status` prueft ausserdem die erwartete Plugin-ID, Version und Marketplace-Quelle
mit Commit-Pin. Es ist eine Inventur, kein Integritaetsnachweis jedes Plugin-Cachefiles.

Lokale Sicherungen und Zustand: `CODEX_HOME/harness/`. Bei einem unterbrochenen Lauf
erst `status`, Sicherungen und laufende Prozesse pruefen. Eine verwaiste `install.lock`
nicht blind entfernen. Die JSON-Sicherungen enthalten Base64-kodierte Originaldateien;
bei einer Unterbrechung zwischen Dateischreibvorgaengen stehen diese zur Wiederherstellung
bereit. Sie bleiben lokal und werden nicht in dieses Repository hochgeladen.

## Ein bestehendes Projekt anbinden

Der Standard ist **Superpowers + Greptile mit Codex-Review als Ersatz + Gitleaks,
OpenGrep und Trivy**. Greptile wird bei der Projektanbindung eingerichtet oder der
Verzicht begruendet. Kritische Aenderungen brauchen einen separaten Review; ein
bestimmter Anbieter ist dafuer nicht zwingend. ZAP/Schemathesis kommen bei passenden
Web-/API-Projekten dazu, Shannon/Strix erst spaeter.

Die kurze [Anleitung zur Projektanbindung](docs/project-onboarding.md) beschreibt
Einrichtung, Ersatzloesungen und Abnahme. Die Installation dieses Harness allein
verbindet weder Greptile noch installiert sie Scanner. Der jeweilige Projekt-Codex
setzt diese Schritte fuer die konkrete Anwendung um und weist offene Punkte aus.

Im Projekt dessen Anweisungen und Stack lesen, aktuelle Tests ausfuehren, kritische
Flows und Grenzen erfassen. Die Vorlagen unter `templates/` sind optional; bestehende
Dokumentation weiterverwenden. Das leere Check-Template besteht absichtlich keine Pruefung.

`harness.checks.json` beschreibt die **tatsaechlichen** Projektbefehle, beispielsweise:

```json
{
  "schema": 1,
  "profile": "internal",
  "checks": [
    {
      "name": "tests",
      "stages": ["dev", "security", "release"],
      "argv": ["{python}", "-m", "unittest", "discover", "-s", "tests"],
      "timeout_seconds": 120
    }
  ]
}
```

`{python}` bezeichnet den Interpreter des Harness. Sonstige Argumente werden unveraendert
uebergeben; keine implizite Shell. Shellskripte ausdruecklich mit `bash` oder PowerShell
aufrufen. Keine Secrets als Argumente. `stages` ist explizit, ohne Vererbung; gemeinsame
Pflichtchecks daher in alle passenden Stufen aufnehmen. `profile` dokumentiert
`internal` oder `public`; es installiert keine Scanner und erzeugt keine Sicherheitsgarantie.

```sh
bash /pfad/codex-harness/harness.sh verify --project /pfad/app --stage dev
```

Weitere Stufen: `security`, `release`. Ergebnis: `.harness-evidence/result.json` im
Projekt, dieses Verzeichnis dort in `.gitignore` aufnehmen. Exitcodes: **0** alle
konfigurierten Checks bestanden; **1** Check fehlgeschlagen; **2** Konfigurations-/Toolfehler.
Der erste Fehler stoppt die Suite; weitere Checks erscheinen als `not_run`. Timeout,
fehlendes Tool und leere Stufe gelten nie als Erfolg. Alte PASS-Berichte werden vor
dem Lauf ungueltig gemacht. Logs laufen ins Terminal; der Bericht speichert Metadaten.

Release-Pruefungen verlangen einen sauberen Git-Stand und erkennen Aenderungen daran
waehrend des Laufs. **Dieser Runner ist kein unabhaengiges Release-Gate.** Der Agent
kann ihn und Projektbefehle veraendern. Die technische Release-Grenze, isolierte
Ausfuehrung und Bindung an den Artefakt-Hash werden beim produktiven Projekt umgesetzt.

## Pruefung dieses Pakets

```sh
python3 -m unittest discover -s tests -v
```

Windows: `python` statt `python3`. Tests nutzen temporaere Codex-Verzeichnisse und
fuehren Installation, Wiederholung, Update und Rollback ueber echte Shell-Einstiege aus.
Sie testen auch Drift, unveraenderte Nutzerregeln, Pfade mit Leerzeichen sowie
absichtliche Fehler, fehlende Befehle und Timeouts. Keine Kundensoftware wird veraendert.

## Fuer die Debian-Codex-Aufgabe

> Lies README.md dieses Harness. Installiere den freigegebenen Stand fuer diese
> Codex-Instanz, pruefe den Status und gleiche Superpowers ab. Danach inventarisiere
> meinen Webdienst, fuehre vorhandene Checks aus und schlage die wenigen wichtigsten
> Verbesserungen vor. Arbeite docs/project-onboarding.md ab: integriere passende
> Tests sowie Gitleaks, OpenGrep und Trivy; richte Greptile bei erlaubter Codeuebermittlung
> ein oder dokumentiere den frischen Codex-Review als Ersatz. Weise fehlende Bausteine
> aus. Keine umfassende Neuentwicklung und kein Tool-Zoo.

Referenzen: [Codex AGENTS.md](https://learn.chatgpt.com/docs/agent-configuration/agents-md),
[Superpowers, gepinnter Stand](https://github.com/obra/superpowers/tree/5bf4e78011075bcfc0dc295f0724994cd123ee71).
