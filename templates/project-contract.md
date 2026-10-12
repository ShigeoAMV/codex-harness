# Project contract

Fill only what matters for this application. Reuse existing documentation.

## Purpose and critical flows
Expected outcomes and acceptance criteria; important behavior that must not regress.

## Boundaries and data
Internal/public exposure, sensitive data, actors, resource ownership, roles,
tenant boundaries and external services. Document allowed code transmission.

## Failure and abuse cases
Negative authorization/input cases, partial failures and retry behavior.
Add a compact resource/action/actor authorization table when applicable.

## Verification
For each critical flow, record the source of expected behavior (requirement, API
contract or agreed acceptance criterion), the relevant unit/integration/end-to-end
coverage, and the observable outcome. Choose the lowest layer that catches the
relevant failure; not every flow needs all three. Identify real test dependencies,
substituted services and untested boundaries; mocks alone do not prove integration.
Use isolated test environments or authorized sandboxes.

Actual fast checks, security checks and release checks. Record current baseline
failures separately. Map checks to important invariants, not only file coverage.
For each required check record its scope, tool/rule/database versions, executed
test/target counts, fresh report and a synthetic failing acceptance case. Record
unreached targets and skips explicitly. Choose one primary separate reviewer;
verify data permission and budget before using an external provider. For relevant
web/API targets, adapt `web-api-profile.md` and prove authenticated coverage.

## Release and recovery
Artifact identity, human release owner, deployment/rollback method and restore
verification where persistent data exists. Record remaining risks and exceptions.
