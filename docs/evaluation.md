# Kritische Bewertung und Entscheidungen

Stand: **2026-10-11**. Bewerteter Ausgangscommit:
`4db60adbc334118300e7619743a7bbda94318543` (Harness 0.1.6).
Ziel ist ein allgemeiner, schlanker Codex-Harness; die Tests dieses Pakets sind
keine Security-Tests spaeter angebundener Anwendungen.

## Bestand vor Aenderungen

Der Git-Stand war sauber. Python 3.12.14/Git 2.52.0 unter Linux:
37 Tests erfasst, **36 bestanden, ein Windows-Test uebersprungen**, keine Fehler.
Die Suite prueft reale Bash-Einstiege, temporaere Git-Repositories, Installation,
Idempotenz, exakte Update-Revision, Rollback, Nutzerdatenerhalt, Drift, Symlinks,
Timeouts und absichtlich fehlerhafte Befehle. Die Plugininventur wird in Unit-Tests
simuliert; diese Tests belegen keine echte Marketplace-Verbindung.

| Bestandteil | Tatsaechlicher Stand / Urteil |
| --- | --- |
| `harness.py`, Bash/PowerShell | Kleiner stdlib-Installer, markierter AGENTS-Block, atomare Einzeldateischreibvorgaenge, Sicherungen und Drift-Schutz. Behalten. Mehrdatei-Updates sind nicht crash-atomar; Backups/Lock nach Unterbrechung weiter manuell untersuchen. |
| `payload/AGENTS.md`, `WORKFLOWS.md` | Anweisungen fuer Verhalten, Tests und Reviews. Kein technischer Zugriffsschutz und kein erzwungenes Release-Gate. |
| `checks.py` | Echte konfigurierte Prozesse ohne implizite Shell, Timeouts, Stop beim ersten Fehler, atomarer Ergebnisbericht und Invalidierung alter PASS-Berichte. Lokale Entwickler-Evidenz. |
| `harness.checks.json` | `dev`, `security`, `release` fuehren denselben Python-Testbefehl aus; `release` verlangt zusaetzlich sauberes Git. Keine Security-Scanner installiert/ausgefuehrt. |
| Templates und Projekt-Onboarding | Gute risikobasierte Hinweise, leeres JSON-Template scheitert absichtlich. Scannerintegration, externe Reviews und Anwendungstests sind Auftraege an das Zielprojekt, keine vorhandene Funktion. |
| CI/CD | Keine Workflow-Datei; Windows-Nachweise aus historischer Dokumentation hier nicht reproduziert. Keine nachgewiesene Branch Protection oder Deployment-Pipeline. |
| Superpowers | Manifest verlangt 6.4.1; offizieller Tag dereferenziert auf den vorhandenen Pin `5bf4e78011075bcfc0dc295f0724994cd123ee71`. Genau eine akzeptierte Quelle, kein reflexartiger Quellenwechsel. |
| Cloud-Installation | Lokale Testinstallation funktioniert. Plattform-CODEX_HOME schreibgeschuetzt; CLI-Inventur liefert keinen Superpowers-Eintrag, waehrend Skills in der Sitzung vorliegen. Vollstaendige Plugin-Ausrichtung nicht bestaetigt. |

## Quellen und Grenzen der Recherche

Offizielle GitHub-Dateien, Git-Refs, Release-Artefakte und PyPI sind erreichbar.
Direkte Abrufe von `developers.openai.com`, `openai.com`, `api.github.com`,
`docs.github.com`, Greptile-/CodeRabbit-/Qodo-Preisseiten und `semgrep.dev/pricing`
wurden vom Netzwerkproxy mit **403** abgewiesen. Wo moeglich wurden die offiziellen
Dokumentationsquellen auf GitHub gelesen. TLS-/Checksum-Pruefung blieb aktiv.
Kein unabhaengiger aktueller Vergleich aller Reviewer war damit verifizierbar;
**keine Rangliste der Erkennungsqualitaet und keine gesicherten Preisangaben**.

Abrufdatum aller folgenden Quellen: 2026-10-11. `main`/`master`/`develop` sind
bewegliche Informationsquellen, keine Installationspins. Die in CI verwendeten
Versionen/Hashes stehen in den Workflow-/Requirements-Dateien.

| Thema | Primarquellen / verifizierbarer Stand | Folgerung |
| --- | --- | --- |
| Codex | [Release 0.162.1](https://github.com/openai/codex/releases/tag/rust-v0.162.1), 2026-10-09; lokal CLI 0.159.2, `--help` und `features list`; [Config-Schema](https://github.com/openai/codex/blob/main/codex-rs/core/config.schema.json) | Lokal sind `review`, Plugins, Hooks und Multi-Agent-Funktionen sichtbar; Hooks/Plugins/Multi-Agent als stable gemeldet. UI-, Account- und Cloud-Verfuegbarkeit separat pruefen. Kein automatisches CLI-Upgrade. |
| AGENTS/Skills | Bestehende native Skill-Bereitstellung und Codex-Konfiguration; [offizielle AGENTS-Doku](https://developers.openai.com/codex/guides/agents-md) direkt nicht erreichbar | Vorhandene Anweisungs-/Skill-Mechanismen nutzen. Globale Regeln respektieren Projektregeln; kein eigenes Agentenframework oder zusaetzlicher Hook-Executor. Hooks fuehren Code aus und brauchen gepruefte Quellen. |
| Superpowers | [Release Notes](https://github.com/obra/superpowers/blob/v7.0.0/RELEASE-NOTES.md), 6.4.2 vom 2026-09-25 und 7.0.0 vom 2026-10-09; v7-Commit `bb92a77741419a4ab5f06e711a283343f1ada0c3` per Git-Tag bestaetigt | 6.4.2 aendert Planungsumfang; 7 aendert Brainstorming und Windows-Hooks. Historischer Recherchebeleg, keine Versionspflicht. Nutzervorgabe: stets ueber native Updates aktuell halten. |
| Greptile | [Pricing](https://www.greptile.com/pricing), [Security](https://www.greptile.com/security); aktuelle Seiten hier nicht verifiziert | Kein Beleg fuer garantierten Gratis-Tarif oder generelle Ueberlegenheit. Optionaler Pilot nach Daten-/Kostenfreigabe statt obligatorischer Standard. |
| CodeRabbit | [Pricing](https://www.coderabbit.ai/pricing) hier blockiert | Ernsthafter externer Review-Kandidat; aktuelle Tarife/Leistung in diesem Lauf unbekannt. Kein zusaetzlicher Bot ohne Vergleich auf eigenen Fehlerfaellen. |
| Qodo | [PR-Agent README](https://github.com/qodo-ai/pr-agent), [Pricing](https://www.qodo.ai/pricing/) blockiert | README trennt das Community-/Legacy-Projekt vom aktuellen Qodo-Produkt. OSS-PR-Agent weder als Funktions- noch als Kostenbeleg fuer Qodo verwenden. Vorhandene Skills beweisen keine Codefreigabe. |
| Codex Review/Security | Lokaler `codex review`-Befehl und bereitgestellter Security-Skillkatalog; [Security-Ankuendigung](https://openai.com/index/codex-security-now-in-research-preview/), [Pricing](https://developers.openai.com/codex/pricing) hier blockiert | Review aktuell nutzbarer Mechanismus; Security Standard/Deep sind unterschiedliche Workflows. Backend-Berechtigung und Kosten nicht getestet. Keine neuen Scans/Abos zur blossen Evaluierung gestartet. |
| Gitleaks | [README](https://github.com/gitleaks/gitleaks/tree/v8.30.1), [Release/Checksums](https://github.com/gitleaks/gitleaks/releases/tag/v8.30.1) | Gepinnte CLI ohne zusaetzliche Review-App einsetzen. RegEx-/Entropie-Erkennung braucht Canary; sauberer Lauf beweist keine Geheimnisfreiheit. |
| OpenGrep / Semgrep | [OpenGrep](https://github.com/opengrep/opengrep), [Semgrep](https://github.com/semgrep/semgrep) | Beide bieten regelbasierte SAST; OpenGrep dokumentiert Sprach-/Taint-Erweiterungen. Das ist kein unabhaengiger Qualitaetsbeweis. Engine, Regeln, Lizenz, Dateiausschluesse und Sprachabdeckung getrennt pruefen; passende vorhandene Loesung behalten. |
| CodeQL | [CodeQL README/Lizenzhinweis](https://github.com/github/codeql#license) | Zusaetzliche datenflussorientierte Analyse kann sinnvoll sein; CLI separat lizenziert, Closed-Source-Nutzung verlangt geklaerte Berechtigung. Nicht automatisch fuer private Projekte aktivieren. |
| Trivy | [README/Scannerziele](https://github.com/aquasecurity/trivy) | CVE/SBOM/Container/IaC sinnvoll bei realen Zielen und frischer Datenbank. Secrets ueberschneiden sich mit Gitleaks. Keine eigene Dependency-/Container-Pipeline fuer dieses stdlib-Paket erfinden. |
| ZAP / Schemathesis | [ZAP](https://github.com/zaproxy/zaproxy), [Schemathesis](https://github.com/schemathesis/schemathesis) | Unterschiedliche Laufzeit-/Schemaabdeckung. Optionales Web/API-Profil, keine Dienste fuer dieses CLI-Repository. Login-/Rollenabdeckung und mutierende Requests explizit pruefen. |
| ASVS | [ASVS 5.0.0](https://github.com/OWASP/ASVS/tree/v5.0.0), Mai 2025; offizielles README bezeichnet 5.0.0 weiterhin als stable | Als versionierten risikobasierten Katalog verwenden, nicht als Scanner oder behauptetes Zertifikat. |
| Shannon / Strix | [Shannon](https://github.com/KeygraphHQ/shannon), [Strix](https://github.com/usestrix/strix) | Beide dokumentieren autonome Pentests und Modellanbindung; API-, Abo- oder lokale Modelle koennen Ressourcen/Kosten verursachen. Shannon AGPL-3.0, Strix Apache-2.0 laut README. Herstellerbenchmarks und deren Verweise nicht als unabhaengig nachgemessen darstellen. Spaeter begrenzter Staging-Pilot. |
| GitHub Actions | [Offizieller Quelltext der Security-Doku](https://github.com/github/docs/blob/main/content/actions/reference/security/secure-use.md) | Minimale Tokens, SHA-Pins, untrusted PR-Code ohne Secrets auf kurzlebigen Runnern, kein `pull_request_target` mit PR-Checkout. CI-Evidenz allein ist keine vertrauenswuerdige Release-Freigabe. |
| Schlanke Alternativen | [Ruff 0.17.0](https://pypi.org/project/ruff/0.17.0/), PyPI-Upload 2026-10-09; [Actionlint 1.7.12](https://github.com/rhysd/actionlint/releases/tag/v1.7.12) | Deterministische Python-Fehler-/Workflow-Pruefung mit geringem Zusatzaufwand, keine weiteren KI-Reviews. Ruff hier nur Korrektheitsregeln, kein umfassender SAST-Ersatz. |

Native Funktionen ersetzen hier die Notwendigkeit eigener Agenten-/Hook-Orchestrierung,
nicht die projektspezifischen Tests oder den kleinen portablen Installer. Das
AGENTS-/WORKFLOWS-Modell bleibt bewusst einfacher als eine eigene Policy-Engine.

## Gegenpruefung und priorisierte Entscheidungen

Der [kurze Umsetzungsplan](improvement-plan.md) wurde vor Codeaenderungen festgehalten.
Prioritaet: Runner-Diagnose und reproduzierbare CI vor weiteren Tools.

1. **CI ja, automatisches Deployment nein.** Vier Testkombinationen plus ein
   Linux-Qualitaetsjob sind fuer das kleine Paket ausreichend. Neue Downloads
   vergroessern die Supply-Chain-Flaeche; deshalb SHA-Pins, Checksums und kleine
   Werkzeugsammlung. Neue Pins bewusst pruefen; kein selbst aktualisierender Installer.
2. **Security-Baseline als Abdeckungsentscheidung.** Gitleaks/OpenGrep/Trivy koennen
   sich sinnvoll ergaenzen, sind aber kein universell bestes Dreierpaket. Vorhandene
   gleichwertige Tools erhalten, Doppel-Secret-/SAST-Scans nur bei nachgewiesener
   Luecke. Harness-CI: Gitleaks real; kein OpenGrep-Regelpaket vorgetaeuscht. Breitere
   SAST-Abdeckung dieses Pakets bleibt eine spaetere gezielte Evaluation.
3. **Ein primaerer separater Review.** Codex ist bereits Teil des Workflows.
   Ein externer Reviewer braucht neue Datenfreigabe, ggf. Kosten und Maintenance.
   Verschiedene Modelle koennen andere Fehler finden, aber ohne eigenen Pilot ist
   paralleler Betrieb kein belegter Gewinn. Vergleichskriterien: neue bestaetigte
   Findings, Fehlalarme, Latenz, Token-/Tarifverbrauch und Pflege pro PR.
4. **Security Standard/Deep nach Frage.** Diff-Review fuer Aenderungen, gezielter
   Security-Review fuer Trust Boundaries, Standard fuer unbekannten Bestand,
   Deep nur fuer verbleibende Hochrisikofragen. Wiederholte breite Scans kosten
   Zeit/Kontingent und duplizieren Befunde. Kein automatischer Kauf/Eskalationspfad.
5. **Evidence erweitern, nicht ueberversprechen.** Nicht gestartete Checks auch
   bei Git-Vorbedingungsfehlern, Runtime/Runner-Hash und Abschlusszeit verbessern
   Diagnose. `--expected-commit` verhindert Verwechslungen, nicht Manipulation.
   Keine generischen Scannerparser, Signierschluessel oder Reportdatenbank einbauen.
6. **Superpowers stets aktuell halten (Nutzervorgabe).** Die urspruengliche
   Empfehlung, den Pin beizubehalten, wurde ausdruecklich verworfen. Manifest und
   Statuspruefung enthalten keine feste Version oder Commitbindung mehr.
   Bestehende native Installation bei Aufgabenstart aktualisieren; eine bewegliche
   offizielle Git-Quelle ist erlaubt. Akzeptierte Quelle und genau eine aktive
   Kopie bleiben erforderlich. Versionen dienen nur der Inventur; lokaler Status
   behauptet mit `freshness: not_checked` keinen erfolgreich ausgefuehrten Updatecheck.
   Cloud-/Marketplace-Einschraenkungen sichtbar melden, ohne eine zweite Kopie anzulegen.

Empirisch nicht belegt: allgemeine Praezisions-/Recall-Rangfolge der Scanner und
Reviewer, aktuelle Kontoentitlements/Kosten, Windows-Plugin-Kompatibilitaet,
Produktionswirksamkeit der Web/API-Vorlage. Keine dieser Annahmen begruendet eine
verpflichtende neue kostenpflichtige Integration.

## Release-Grenze und verbleibende Pflichten

Ein Agent kann Runner, Tests, Konfiguration und lokale Reports aendern. Auch ein
gepinntes CI-Workflow im selben PR kann manipuliert werden. Der Runner-Hash ist
Identifikation, keine Signatur und kein Integritaetsnachweis gegen diesen Akteur.
Sauberes Git erfasst beispielsweise keine ignorierten Laufzeitdateien; ein
hermetischer Build ist dadurch nicht hergestellt.

Fuer eine verbindliche Freigabe: gepruefte und geschuetzte Workflow-/Policy-Aenderungen,
exakter freigegebener Commit, getrennte Build-/Test- und Release-Berechtigungen,
wegwerfbare Runner ohne Produktions-/Signiergeheimnisse und ein separat kontrollierter
Release-Schritt. Dieser bindet Commit, Tool-/Regel-/DB-Versionen, Testberichte,
Ausnahmen und **Hash des tatsaechlich freizugebenden Artefakts**. Nach Freigabe
nicht neu bauen. Signatur/Attestation nur in dieser getrennten Instanz; eine
Signatur auf einem vom ungeprueften Build selbst behaupteten PASS schafft keine
Vertrauensgrenze. Branch Protection/Rulesets mit erforderlichen Checks und Review
fuer Workflow-/Policy-Dateien sind extern zu konfigurieren und hier nicht bestaetigt.

## Validierung dieser Aenderungen

Geprueft wurde der veraenderte Arbeitsstand, keine neue veroeffentlichte Version.
Acht Tests kamen hinzu. Die bisherigen Tests der festen Superpowers-Version und
des Commit-Pins wurden gemaess Nutzervorgabe durch versionsunabhaengige Inventur-
und Quellenpruefungen ersetzt; die uebrigen Assertions wurden nicht abgeschwaecht.
Die Runner-Regressionen zeigten vor der Reparatur unter anderem die akzeptierte
Boolean-Schemaversion und fehlende `not_run`-/Timeout-Metadaten. Danach bestand
die vollstaendige Suite einschliesslich realem CLI-Test fuer den erwarteten Commit.

| Pruefung | Ergebnis |
| --- | --- |
| Linux, Python 3.11.17 | 45 Tests erfasst: 44 bestanden, ein Windows-Test uebersprungen |
| Linux, Python 3.12.14 | 45 Tests erfasst: 44 bestanden, ein Windows-Test uebersprungen; der vorherige 44-Test-Stand wurde auch ueber `bash harness.sh verify --project . --stage dev` mit Exit 0 geprueft |
| Linux, Python 3.14.8 | 45 Tests erfasst: 44 bestanden, ein Windows-Test uebersprungen |
| Ruff 0.17.0 | `ruff check --select E9,F63,F7,F82 harness.py checks.py tests` bestanden |
| Actionlint 1.7.12 | Workflow-Pruefung bestanden (`-shellcheck=""`; kein ShellCheck-Lauf); alle fuenf CI-Shellbloecke zusaetzlich mit `bash -n` geprueft |
| Gitleaks 8.30.1 | Alle sieben lokal vorhandenen Git-Commits und aktueller Arbeitsbaum ohne Fund; Redaction aktiv |
| Gitleaks-Canary | Generierter, synthetischer GitHub-Token: Exit 1 **und** `github-pat` im JSON-Report bestaetigt. Eine alphabetische Vorversion wurde absichtlich durch die Standard-Stopwordliste ignoriert; keine Scannerregel wurde fuer den Test abgeschwaecht. |
| CI-Schritte lokal | Exakte Run-Bloecke fuer Ruff/Actionlint, Canary und Historien-Scan bestanden; Installationspins/Checksums separat verifiziert |
| Separater frischer Codex-Review | Source-Diff, neue CI und Dokumentation geprueft; keine konkreten Aenderungsbefunde. Reviewer fuehrte selbst die 44 Tests, Actionlint, Canary und Historien-Scan aus. Kein neuer externer Review-Dienst benutzt. |
| Folge-Review zur Superpowers-Vorgabe | Keine konkreten Befunde; alle 19 Installer-/Status-Tests separat bestanden. Native Aktualisierung mangels schreibbarer Installation nicht ausgefuehrt. |
| Git-Whitespace-Pruefung | `git diff --check` bestanden |

Identifikation der geprueften Ausfuehrungsdateien (SHA-256, keine Signatur):

- `checks.py`: `de48b7484ac03dfb3d16df9a9cd37df55798c17f587f277cdd5bcc1fad91de86`
- `.github/workflows/ci.yml`: `64ccf9092ff7d3d34b06f47d4fc113498375935c779ed592c2a26e10127688e7`

**Offen:** echter Windows-/GitHub-Actions-Lauf, Branch-/Workflow-Schutz,
Plugininventur/Upgrade-Kompatibilitaet und aktuelle Anbieterpreise/Kontingente.
Lokales Actionlint validiert Syntax, nicht GitHub-Berechtigungen oder Runnerbetrieb.
Es wurden keine Web-/API-Ziele gescannt, kein OpenGrep-/Trivy-/CodeQL-Vollscan
durchgefuehrt und keine Produktion veraendert. Deren fehlende Anwendungsziele bzw.
ausstehende projektbezogene Auswahl sind keine bestandenen Security-Pruefungen.
