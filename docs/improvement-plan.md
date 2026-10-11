# Gezielte Verbesserung des Harness

Stand: 2026-10-11. Ausgangspunkt: `4db60adbc334118300e7619743a7bbda94318543`.
Auftrag: Qualitaet und Sicherheit bei geringem Wartungsaufwand verbessern;
kleine Verbesserungen autonom, keine neuen kostenpflichtigen Dienste oder externe
Codefreigaben. Umsetzung direkt im vorhandenen isolierten Cloud-Checkout.

## Entscheidungen vor der Umsetzung

| Prioritaet | Entscheidung | Nutzen / Gegenargument |
| --- | --- | --- |
| Behalten | Python-Standardbibliothek, Wrapper, markierte Regeln, Backups, Drift-Schutz, explizite Updates | Bereits getestete kleine Implementierung; Rewrite schafft neue Fehler |
| Jetzt 1 | Runner: nicht gestartete Checks auch bei Vorbedingungen melden, Abschlusszeit/Runtime/Runner-Hash, erwarteten Commit optional pruefen | Bessere Diagnose und reproduzierbare Zuordnung; weiterhin keine Freigabeinstanz |
| Jetzt 2 | Ein CI-Workflow: Linux/Windows, Python 3.11/3.14, kleiner Ruff-Check, Actionlint, Gitleaks CLI | Wiederkehrende Tests und Secretschutz; gepinnte Downloads erzeugen Pflegeaufwand und CI verbraucht Kontingent |
| Jetzt 3 | Anbieterneutraler separater Review, risikobasierte Scannerwahl, optionales Web/API-Profil, Recherchebericht | Entfernt unbelegte Gratis-/Ueberlegenheitsannahmen; Dokumentation erzwingt keine technische Freigabe |
| Laufend | Superpowers ueber native Updates aktuell halten, ohne Versions-/Commit-Pflicht | Ausdrueckliche Nutzervorgabe; bestehende Quelle erhalten und Updatehindernisse sichtbar melden |
| Spaeter | Kontoabhaengige Codex-Security-Funktionen, CodeQL, externe Reviewer | Erst Datenfreigabe, Kontingent und zusaetzlichen Erkenntnisgewinn nachweisen |
| Nicht hinzufuegen | Eigene Hook-/Agentenplattform, automatische Deep Scans, mehrere parallele KI-Reviewer, lokales Signieren als Release-Gate | Mehr Kosten, Ausfuehrungsrechte und Scheinsicherheit ohne nachgewiesenen Nutzen |

Keine neue Runner-Konfigurationssprache fuer Toolversionen oder Scanner-Reportparser:
projektspezifische Adapter kennen deren Semantik besser. Ein Null-Exit allein kann
weder Testanzahl noch authentifizierte Abdeckung beweisen. CI-Artefakte und lokale
Hashes verbessern Nachvollziehbarkeit, verhindern aber keine Manipulation durch
jemanden, der den Runner bzw. Workflow aendern kann.

## Umsetzung und Abnahme

- [x] `tests/test_checks.py`, `checks.py`, `harness.py`: Regressionen zuerst fuer
  vorzeitigen Abbruch, falschen/exakten Commit, Schema-Boolean, Timeout-Grund und
  Evidence-Metadaten. Bestehendes Schema 1 und Exitcodes 0/1/2 erhalten.
- [x] `.github/workflows/ci.yml`, `.github/requirements-ci.txt`: ein Workflow ohne
  Secrets, Schreibrechte oder privilegierte PR-Trigger; Actions per SHA, Downloads
  per SHA-256; Shell-Einstiege und echte Tests auf beiden Betriebssystemen.
- [x] `README.md`, `START-HERE.md`, `payload/`, `docs/project-onboarding.md`,
  `templates/`: Anbieterneutralitaet und praktisch pruefbare Abnahme konsistent
  dokumentieren. Web/API-Anleitung nur fuer passende Zielprojekte.
- [x] `docs/evaluation.md`: Bestand, Quellenstand, Gegenargumente, nicht verifizierte
  Markt-/Kostenannahmen und tatsaechliche Ergebnisse festhalten.
- [x] Vollstaendige Suite, Linux-CLI, Linter und Scanner mit negativem Canary
  ausfuehren; frischen separaten Review einholen und Findings bearbeiten.

Besondere Review-Faelle: nie gestartete Checks bei Vorbedingungsfehlern;
veraenderter Checkout nach erfolgreichen Befehlen; ungueltige Konfiguration statt
stillem PASS; fehlerhafte Toolinstallation; keine Tokens/Secrets in PR-Ausfuehrung.
Abgeschlossen am 2026-10-11: Die [GitHub-CI](https://github.com/ShigeoAMV/codex-harness/actions/runs/38132881892)
bestand auf Linux und Windows. Das aktive `main`-Ruleset wurde ueber die GitHub-API
geprueft: PR-Pflicht, fuenf erforderliche GitHub-Actions-Checks, aktueller PR-Branch,
kein Loeschen oder Force-Push. Review-Freigaben sind mit 0 konfiguriert; der separate
Review wird nicht durch dieses Ruleset erzwungen. Details und verbleibende Grenzen
stehen in der [Bewertung](evaluation.md).
