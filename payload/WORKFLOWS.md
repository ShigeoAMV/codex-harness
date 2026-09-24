# Engineering workflow reference

Keep this proportional. Reuse existing project tooling and documentation. Integrate
the baseline below once per project, then run it according to risk; do not create a
documentation tree or run every scanner after every edit.

## Standard tool selection

| Purpose | Standard | Required decision at project onboarding |
| --- | --- | --- |
| Engineering | Superpowers | Reuse one existing supported installation; see README for accepted sources/version. Never add a second copy merely to change marketplace. |
| Separate PR review | Greptile preferred; fresh Codex review as fallback | Configure Greptile for the selected repository when code transmission is allowed and a no-extra-cost plan is available; otherwise record the reason and fallback |
| Secrets | Gitleaks | Integrate changed-content checks and relevant Git history scanning before release |
| Source security | OpenGrep | Pin engine and suitable rules for the project's supported languages |
| Dependencies / containers / IaC | Trivy | Enable applicable scanners and explicit blocking exit codes |
| Runtime checks | ZAP / Schemathesis | Add for relevant web/API targets in isolated staging |
| Agentic pentesting | Shannon / Strix | Later evaluation after the baseline works; not an onboarding dependency |

Existing equivalent checks may satisfy a baseline item when their coverage is
documented. Unsupported stacks or inapplicable targets need a short explanation,
not dummy checks. A missing applicable check remains a visible gap. Do not purchase
services or broaden code access to remove a gap.

## Prefer established components for high-risk responsibilities

At onboarding or when adding a relevant capability, identify which security-critical
responsibilities can be handled by maintained components rather than bespoke code.
For public services with user accounts, explicitly evaluate Auth as a Service first,
alongside suitable existing framework auth or an identity provider. If accounts are
not needed, do not add them. Preserve sound existing auth rather than migrating by default.
Use maintained protocol libraries/SDKs; assess MFA, recovery and session requirements.
The application still validates tokens/sessions and enforces resource permissions and
tenant boundaries server-side, with negative tests. Never implement custom cryptography.

Treat browser code, client state and request fields as attacker-controlled. The
backend must enforce permissions, validate input and preserve business invariants
without relying on hidden buttons, disabled fields or frontend validation. Never
ship privileged database/service credentials in frontend bundles. Separate domains,
repositories and CORS settings do not replace authorization. In authorized test
environments, exercise the API directly: foreign resource/tenant IDs, forged role or
price fields, missing/invalid sessions and bypassed UI validation. Verify rejection
or safe server-derived values, with no unauthorized data exposure or state changes.

Other high-leverage options, only where applicable: parameterized database access and
transaction support; hosted payment checkout with verified, idempotent webhooks;
private object storage with authorized uploads/downloads and size/type limits;
maintained reverse proxy/platform for TLS and abuse controls; managed databases/hosting
where patching, backup and recovery responsibilities would otherwise exceed capacity.
Keep admin/debug/database endpoints private where possible. Verify restore capability,
alerts and provider responsibilities; an external service is not a security guarantee.

For each relevant choice, briefly record reuse/service/self-hosting, benefit, residual
application duties, operating cost at expected usage, data policy and migration/exit
options. No paid service, new data transfer or automatic migration without the required
authorization. Free tiers are not guaranteed zero-cost production infrastructure.
Self-hosted maintained software is a valid option when its operating duties are owned.

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
6. Integrate the applicable Gitleaks/OpenGrep/Trivy checks with pinned tool/rule versions.
   Prove blocking behavior using synthetic secret/SAST/dependency fixtures in a temporary
   test area, not real secrets or vulnerable code left in the production branch.
7. Configure Greptile for the selected repository or record why it cannot be used.
   Define the fresh Codex-review fallback. Record each baseline item as configured,
   missing, fallback, or not applicable with a reason in existing project documentation.
   A successful onboarding report must not imply missing items have been installed.

For large or weakly tested existing applications, map coherent areas and their
dependencies across the relevant codebase, not only recent diffs. Confirm intended
behavior rather than treating existing bugs as requirements. Prioritize authorization,
data loss and exposed interfaces. For each finding: reproduce/test, make a focused
repair, run regression checks and obtain a separate review. Document a manual
reproduction and coverage gap if automation is impractical. Avoid blanket rewrites.
Track each area's reviewed commit, scope, evidence and remaining findings in existing
project documentation. Completion means the agreed criteria, regression checks and
review are satisfied, with exceptions visible; a clean scan alone is not a full audit.

## Risk and verification

Dev: relevant build/type/lint/tests plus a quick secret check for changed content.
Documentation-only work needs appropriate lightweight verification, not a full build.

Security-sensitive changes: negative auth/input/failure tests and a separate review
are required before merge/release. This includes auth, permissions, tenant isolation,
uploads, URL fetching, secrets, payments/transactions, migrations and release controls.
Prefer Greptile; use a fresh Codex context when data policy, quota or availability
prevents it. Give the reviewer the diff, relevant context and acceptance criteria.
Record reviewed commit, findings and disposition; review new relevant changes again.
If neither review path is available, mark review pending rather than self-approving.
Development can continue. Fresh Codex review shares model blind spots and is not an
independent model verdict. Property/mutation tests are useful where they reveal real gaps.

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

## Review budget and optional tools

Greptile is the preferred standard, not a mandatory service dependency. Reserve its
free allowance for critical and substantial PRs; do not spend it automatically on
every tiny change. Check actual account entitlements at setup; no paid upgrade or
automatic overage. A separate review never replaces deterministic tests or scanners.
Shannon/Strix: optional evaluation against explicitly authorized disposable staging,
synthetic data, no production credentials or access. Never require subscription
workarounds for the core workflow. Add tools only after a demonstrated coverage gap.
