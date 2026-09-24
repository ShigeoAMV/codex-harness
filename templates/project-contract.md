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
Actual fast checks, security checks and release checks. Record current baseline
failures separately. Map checks to important invariants, not only file coverage.

## Release and recovery
Artifact identity, human release owner, deployment/rollback method and restore
verification where persistent data exists. Record remaining risks and exceptions.
