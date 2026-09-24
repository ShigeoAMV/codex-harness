# Portable baseline implementation

Approved brief: shared Codex instructions for Windows/Linux, full-access development,
risk-based checks, no additional subscriptions. Existing applications remain untouched.
The Debian application is handled in its own Codex session after this repository is ready.

1. Implement a standard-library installer with managed AGENTS block, local backups,
   idempotence, explicit revision updates, status and reversible rollback.
2. Add concise global rules and on-demand workflow reference; use upstream Superpowers,
   pinned through the native Codex marketplace rather than vendoring a second framework.
3. Add a fail-closed project check runner and templates, without guessing application commands.
4. Test Windows and Linux, review, publish a private repository, install locally.

Decisions: keep Superpowers installation in native Codex commands, separate from the
managed rule installer. Its config/cache backups and migration are documented separately.
No custom skills or paid Qodo dependency in v1. No broad automatic scanner installation.
This is a fresh, isolated repository on build/portable-baseline; no existing checkout is changed.

Validation: unittest integration tests, actual PowerShell/Bash entrypoints, temporary HOME
directories, Git revision checks, deliberately failing/missing project checks.

Progress: installer and runner implemented with regression tests. First tests failed
before implementation; Windows and Linux shell integration passed. Fresh reviewer
found three issues: interrupted transaction recovery, plugin identity validation,
Windows timeout cleanup. Each reproduced as a failing regression test and fixed.
Additional pin validation rejects mutable marketplace refs. No paid backend invoked.
