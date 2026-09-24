# Gemeinsam zum passenden Projekt-Setup

Starte Codex im Zielprojekt und gib ihm diesen Auftrag. Bei einem privaten Repository
braucht die Instanz GitHub-Zugriff oder einen lokalen Clone des Harness.

> Lies START-HERE.md aus https://github.com/ShigeoAMV/codex-harness auf dem
> freigegebenen Stand v0.1.2 und fuehre das folgende Onboarding mit mir fuer das
> aktuelle Projekt durch. Bleibe schlank, priorisiere die groessten Hebel und nutze
> vorhandene Loesungen weiter.

## Auftrag an Codex

1. **Erst selbst nachsehen.** Lies die Projektanweisungen sowie die
   [README](README.md) und die [Anleitung zur Projektanbindung](docs/project-onboarding.md)
   dieses Harness. Pruefe Stack, Architektur, vorhandene Tests/Scanner, CI und
   Deployment. Fuehre geeignete vorhandene, nicht destruktive Checks aus und trenne
   bestehende Fehler von neuen. Pruefe den Harness-Installationsstand. Keine Secrets
   ausgeben und keine produktiven Systeme testweise veraendern.

2. **Nur echte Luecken erfragen.** Fasse dein Verstaendnis kurz zusammen. Klaere mit
   mir nur offene Entscheidungen: Nutzung und Zielzustand (Homelab, intern, public,
   produktiv), sensible Daten, wichtige Ablaeufe und erlaubte externe Codeverarbeitung.
   Stelle wenige konkrete Fragen mit einer Empfehlung; frage nichts, was du selbst
   im Repository feststellen kannst. Vorhandene Antworten gelten weiter.

3. **Passenden Umfang vorschlagen.** Zeige kurz: jetzt noetig, spaeter sinnvoll oder
   nicht anwendbar, jeweils mit Begruendung. Beruecksichtige Projekt-/Security-Vertrag,
   kritische Tests, Greptile mit frischem Codex-Review als Ersatz, Gitleaks, OpenGrep,
   Trivy sowie passende CI-/Laufzeit-/Recovery- und Release-Pruefungen. Zusaetzliche
   Skills und Shannon/Strix nur bei konkretem Nutzen. Keine Zusatzabos. Waehle wenige
   priorisierte Schritte mit sichtbaren Abnahmekriterien und unterscheide schnelle
   Entwicklungschecks von umfassenderen Release-Pruefungen.

4. **Mit mir abstimmen, dann umsetzen.** Lass mich den vorgeschlagenen Umfang einmal
   bestaetigen oder korrigieren. Setze danach die vereinbarten Schritte selbststaendig
   in kleinen, ueberpruefbaren Aenderungen um; keine erneute Freigabe fuer jede Routine.
   Installiere einen fehlenden Harness gemaess README. Binde geeignete Checks ein und
   pruefe deren Fehlererkennung. Neue Codeuebermittlung, Account-Freigaben und
   produktive Aktionen brauchen die jeweils passende Autorisierung; ein bestaetigter
   allgemeiner Plan ersetzt diese nicht. Arbeite an unabhaengigen Schritten weiter,
   wenn ein einzelner Zugang fehlt.

5. **Den Stand festhalten.** Fuehre eine kurze Tabelle in vorhandener
   Projektdokumentation, sonst in `docs/harness-status.md`: Baustein, Status
   (eingerichtet/geprueft/offen/bewusst ausgeschlossen), Nachweis oder Begruendung und
   naechster Schritt. Ein installiertes Tool ist noch keine gepruefte Integration.
   Melde am Ende, was nachweislich funktioniert und was fehlt. Bei erneutem Onboarding
   hier anknuepfen, statt bereits erledigte Einrichtung zu wiederholen.
