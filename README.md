# Codex Harness

[![Harness CI](https://github.com/ShigeoAMV/codex-harness/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/ShigeoAMV/codex-harness/actions/workflows/ci.yml)

Ein gemeinsamer, schlanker Codex-Standard fuer Windows und Linux. Schnell entwickeln,
risikobasiert pruefen. Keine zusaetzlichen Abos, Python-Pakete oder Hintergrunddienste.

**Voraussetzungen:** Git, Python 3.11+ und Codex mit Plugin-Unterstuetzung.
Der Harness aendert keine Full-Access-, Modell-, Account- oder Sandbox-Einstellungen.

**Projekt gemeinsam mit Codex einrichten:** [Hier starten](START-HERE.md).
Der kurze Startauftrag fuehrt durch Bestandsaufnahme, offene Entscheidungen,
Priorisierung und Umsetzung mit dir.

## Auf einer weiteren Maschine starten

```sh
git clone --branch main https://github.com/ShigeoAMV/codex-harness.git
cd codex-harness
git rev-parse HEAD
```

`main` enthaelt den aktuellen Stand. Die ausgegebene Commit-SHA fuer weitere
Maschinen festhalten; vor Installation den zugehoerigen CI-Lauf pruefen. Der alte
Tag `v0.1.6` enthaelt die nachfolgenden Runner-, CI- und Superpowers-Aenderungen
nicht. Die Manifestversion allein identifiziert diese Weiterentwicklung nicht;
massgeblich ist die Commit-SHA.

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

### Superpowers: stets aktuell halten

**Superpowers soll stets aktuell sein; der Harness schreibt keine Version und
keinen Commit vor.** Genau eine aktive Installation aus `openai-curated-remote`
oder dem offiziellen `superpowers-dev` weiterverwenden. Bei Aufgabenstart native
Plugin-Updates pruefen und verfuegbare Aktualisierungen anwenden. Die kuratierte
Installation ueber die Codex-Pluginverwaltung aktualisieren; deren bereitgestellter
Stand kann vom Upstream abweichen. Keine zweite Kopie nur fuer den Harness anlegen.

Desktop und CLI koennen unterschiedliche Plugin-Kataloge zeigen. Ein fehlender
CLI-Eintrag beweist deshalb nicht, dass Superpowers in der App fehlt. Bei unklarer
Inventur die Einschraenkung melden und zuerst die tatsaechlich verwendete Umgebung
pruefen. Nicht vorsorglich ein weiteres Plugin installieren. Ist eine Aktualisierung
nicht pruefbar oder moeglich, die Einschraenkung melden und die vorhandene
Installation weiterverwenden, ohne sie als nachweislich aktuell zu bezeichnen.

**Nur wenn Superpowers tatsaechlich fehlt:** lokale Codex-`config.toml` sichern und
den offiziellen Marketplace ohne Versions-/Commit-Pin einrichten:

```sh
codex plugin marketplace add obra/superpowers --ref main
codex plugin add superpowers@superpowers-dev
codex plugin list --json
```

Fuer eine bestehende offizielle `superpowers-dev`-Installation einen alten festen
`ref` nach Sicherung der Konfiguration gezielt auf `main` umstellen. Quelle und
andere Einstellungen erhalten. Anschliessend den nativen Updateweg verwenden:

```sh
codex plugin marketplace upgrade superpowers-dev
codex plugin add superpowers@superpowers-dev
codex plugin list --json
```

Die Befehlsform ist mit Codex CLI 0.159.2 geprueft. Die konkrete Aktualisierung
braucht eine schreibbare native Plugininstallation; der Cloud-Skillkatalog ist
keine solche lokale Installation. Nach einem Update neue Codex-Aufgabe starten.

Diese nativen Plugin-Befehle werden durch `harness rollback` nicht rueckgaengig
gemacht. Bestehende Marketplace-Registrierungen nicht blind ersetzen. Sind wirklich
zwei Kopien aktiv, eine passende behalten und die andere deaktivieren. Andere Plugins
bleiben erhalten. Qodo ist keine Abhaengigkeit und wird vom Harness nicht aufgerufen.

## Updates und Rollback

Updates des **Harness selbst** sind bewusst, nicht automatisch. Auf allen Rechnern denselben freigegebenen
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
`status` prueft ausserdem genau eine aktive Superpowers-Installation aus den
akzeptierten Quellen und bei `superpowers-dev` die offizielle Git-Quelle.
Die gemeldete Version dient nur der Inventur; es gibt keine Versions- oder
Commit-Pflicht. `freshness: "not_checked"` bedeutet, dass dieser lokale Status
keinen Online-Updatecheck durchfuehrt. Die kuratierte Installation braucht keine
zusaetzliche Marketplace-Registrierung. Die Inventur ist kein Integritaetsnachweis
jedes Plugin-Cachefiles.

Lokale Sicherungen und Zustand: `CODEX_HOME/harness/`. Bei einem unterbrochenen Lauf
erst `status`, Sicherungen und laufende Prozesse pruefen. Eine verwaiste `install.lock`
nicht blind entfernen. Die JSON-Sicherungen enthalten Base64-kodierte Originaldateien;
bei einer Unterbrechung zwischen Dateischreibvorgaengen stehen diese zur Wiederherstellung
bereit. Sie bleiben lokal und werden nicht in dieses Repository hochgeladen.

## Ein bestehendes Projekt anbinden

Der Standard ist **Superpowers + separater Codex-Review + passende deterministische
Checks**. Gitleaks prueft Secrets; OpenGrep/Semgrep oder vorhandene gleichwertige
SAST-Pruefungen den Quellcode; Trivy relevante Dependencies, Container und IaC.
Die konkrete Auswahl folgt dem Stack und belegter Abdeckung. Greptile, CodeRabbit
und Qodo sind optionale Alternativen zum PR-Review, wenn Datenfreigabe, Kontingent
und Mehrwert geklaert sind. Kein Gratis-Tarif und kein Qualitaetsvorsprung werden
vorausgesetzt. ZAP/Schemathesis kommen bei passenden Web-/API-Projekten dazu.

Die kurze [Anleitung zur Projektanbindung](docs/project-onboarding.md) beschreibt
Einrichtung, Ersatzloesungen und Abnahme. Die Installation dieses Harness allein
verbindet keine Review-Dienste und installiert keine Scanner. Der jeweilige Projekt-Codex
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

Der Bericht enthaelt Start-/Abschlusszeit, Python-Version, Plattform, Runner- und
Konfigurations-Hash sowie gestartete und nicht gestartete Checks. Bei ungueltiger
Konfiguration ist `selection_complete: false`: eine leere `not_run`-Liste beweist
dann keine vollstaendige Ausfuehrung. Timeout und Unterbrechung haben getrennte
Fehlergruende. Toolversionen, Scanner-Regeln, Testanzahlen und originale Reports
muessen die Projektbefehle liefern; der Runner kann ihre Semantik nicht erraten.
Ein Tool mit Exitcode 0 trotz null Tests, uebersprungener Ziele oder Findings wird
ohne passenden Projektadapter nicht automatisch erkannt.

Release-Pruefungen verlangen einen sauberen Git-Stand und erkennen Aenderungen daran
waehrend des Laufs. **Dieser Runner ist kein unabhaengiges Release-Gate.** Der Agent
kann ihn und Projektbefehle veraendern. Die technische Release-Grenze, isolierte
Ausfuehrung und Bindung an den Artefakt-Hash werden beim produktiven Projekt umgesetzt.

Ein separat vorgegebener voller Commit kann zusaetzlich gebunden werden:

```sh
bash harness.sh verify --project /pfad/app --stage release --expected-commit <volle-commit-sha>
```

Ein abweichender Commit stoppt vor dem ersten Check. Den Soll-Commit aus dem
Review-/CI-Auftrag beziehen; `git rev-parse HEAD` am selben ungeprueften Checkout
liefert allein keine unabhaengige Sollvorgabe. Diese Option ist kein Release-Gate.

## Pruefung dieses Pakets

```sh
python3 -m unittest discover -s tests -v
```

Windows: `python` statt `python3`. Tests nutzen temporaere Codex-Verzeichnisse und
fuehren Installation, Wiederholung, Update und Rollback ueber echte Shell-Einstiege aus.
Sie testen auch Drift, unveraenderte Nutzerregeln, Pfade mit Leerzeichen sowie
absichtliche Fehler, fehlende Befehle und Timeouts. Keine Kundensoftware wird veraendert.

Der Workflow `.github/workflows/ci.yml` prueft Linux/Windows mit Python 3.11/3.14,
Ruff, Actionlint und Gitleaks samt synthetischem Fehlertest. Actions sind per Commit,
Werkzeugdownloads per Version und SHA-256 gepinnt. Keine Runtime-Pakete erforderlich.
Das lokale `harness.checks.json` startet in **allen drei Stufen nur die Python-Tests**;
die CI-Scanner sind separate Jobs, keine Security-Garantie fuer angebundene Projekte.

Fuer dieses Repository wurde am 2026-10-11 das aktive Ruleset fuer `main`
geprueft: Pull Requests, alle vier `Tests (...)`-Checks und `Lint and secrets`
aus GitHub Actions sowie ein aktueller PR-Branch sind erforderlich. Loeschen und
Force-Pushes sind gesperrt. Die Zahl erforderlicher Review-Freigaben ist 0; ein
separater Review bleibt Arbeitsablauf, wird also nicht technisch erzwungen.

Bei angebundenen Projekten CI und Rulesets separat einrichten und pruefen; diese
Einstellungen werden durch den Harness nicht uebertragen. Vertraute Reviews
fuer Workflow-/Policy-Aenderungen, geschuetzte Branches und eine separate
Release-Identitaet sind Einstellungen des Zielrepositories. Fork-PRs laufen auf
kurzlebigen GitHub-Runnern mit Leserechten, ohne Secrets oder Deployment.
Bei privaten Repositories vorhandenes Actions-Kontingent/Budget beachten.

Recherche, begruendete Nicht-Aenderungen und aktuelle Pruefgrenzen:
[kritische Bewertung](docs/evaluation.md). Optional:
[Web/API-Abnahme](templates/web-api-profile.md).

## Startauftrag fuer ein Zielprojekt

> Lies START-HERE.md aus https://github.com/ShigeoAMV/codex-harness auf dem
> aktuellen Stand von main, halte die verwendete Commit-SHA fest und fuehre
> das Onboarding mit mir fuer mein Projekt durch.

Referenzen: [Codex AGENTS.md](https://learn.chatgpt.com/docs/agent-configuration/agents-md),
[Superpowers, aktueller Stand](https://github.com/obra/superpowers).
