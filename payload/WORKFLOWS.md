# Engineering workflow reference

Keep this proportional. Reuse existing project tooling and documentation. Do not
create a documentation tree or install scanners merely to satisfy a template.

## Adopt an existing application

1. Read repository instructions and identify entrypoints, stack, test/build commands,
   data stores, auth/roles, external interfaces and deployment mechanism.
2. Run the current checks and report existing failures separately from new changes.
3. Capture critical user flows, security boundaries and relevant negative cases in
   one short project contract. Add an authorization matrix only when roles/resources warrant it.
4. Add focused tests around important unprotected behavior. Fix highest-impact
   findings in small changes, with a reproduction and regression test where possible.
5. Connect actual project commands to harness.checks.json. No dummy successful checks.
   Missing tools or commands block a configured stage, not unrelated development.

## Risk and verification

Dev: relevant build/type/lint/tests plus a quick secret check for changed content.
Documentation-only work needs appropriate lightweight verification, not a full build.

Security-sensitive changes: add negative auth/input/failure tests and focused fresh
review. Fresh Codex review helps but shares model blind spots. Do not require a paid
review service. Property/mutation tests are useful where they reveal real test gaps.

Internal/homelab release: critical behavior, secrets and relevant dependency checks.
Increase coverage when sensitive data, broad permissions or availability warrant it.

Public/production release: build/type/lint, relevant unit/integration/E2E, negative
authorization, pinned OpenGrep rules and engine, Gitleaks, Trivy, and runtime checks
where applicable. Add Schemathesis for a suitable API schema, ZAP for a running web
target, migration/restore tests for affected persistent data. Do not invent schema
coverage or call a skipped authenticated scan complete. Record exclusions and why.

Project owners choose and review the actual required commands. The runner does not
infer completeness or certify security from an exit code. Trivy and similar tools
must be configured to exit nonzero at the project's blocking severity threshold.
Tool/rule versions and advisory database timestamps belong in project evidence.

## Findings

For a finding, record reproduction/evidence, affected behavior, severity, action and
remaining uncertainty. Do not broadly suppress old findings. A bounded legacy
baseline must identify findings and owner; exceptions need scope and expiry.
Unresolved critical/high findings block public/production release unless the human
owner explicitly accepts the documented risk. AI confidence is not an exception.

## Release boundary

The ordinary harness runner is a development verifier, not a trusted release gate:
the coding agent can edit the runner, project commands and local reports.

For a binding release decision, use a separately administered verifier/policy and a
fresh exact-commit checkout. Run project build/test code in a disposable context with
no release/signing/production credentials, and restricted access to the verifier.
Record commit, artifact SHA-256, tool/rule versions, test results and approved exceptions.
The separate release authority validates that evidence and deploys that exact artifact;
do not rebuild a different artifact after approval. Sign evidence only outside the
untrusted build/test context. A protected folder on the same unrestricted account
and a Markdown prohibition are not technical isolation.

## Optional tools

Greptile: use only if code transmission is permitted and the free allowance suffices.
Shannon/Strix: optional evaluation against explicitly authorized disposable staging,
synthetic data, no production credentials or access. Never require subscription
workarounds for the core workflow. Add tools only after a demonstrated coverage gap.
