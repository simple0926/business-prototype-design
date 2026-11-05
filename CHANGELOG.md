# Changelog

This file uses the public release sequence. The public `0.2` consolidates the internally validated development work that previously used later internal version labels; those historical packages remain unchanged.

## 0.3 - 2026-11-05

### Public outcome

Hardens the 0.2 traceability skeleton into a package-level contract: final evidence is file-identity bound, cross-artifact references resolve, invalidation propagates, and standalone packaging rejects build-root escape and unresolved static dependencies.

### Added

- Lite mode with machine-checked escalation thresholds.
- Artifact schema `0.4`, confirmation provenance, continuation gates, evidence digests, byte counts, media types, and execution metadata.
- `validate-package.py` as the canonical final validator across workflow, traceability, standalone, manifest, and journey contracts.
- A complete three-page, two-role, four-state golden sample with passing package output.
- Thirty-two adversarial, package-consistency, and golden-sample tests; total contract tests increase from 30 to 62.

### Fixed

- Reject direct or byte-identical requirement/acceptance self-evidence, placeholder evidence content, directory artifacts, invalid timestamps, dangling Source/Decision/Journey/Evidence IDs, and unresolved Page/Acceptance mappings.
- Parse schema 0.4 test evidence as TAP, JUnit XML, or structured JSON; require structured browser evidence with reproducible command metadata.
- Cross-check Lite counts and risk signals, source profiles, journey profiles, and visual profiles against the package contracts.
- Reject contradictory acceptance/design results and fully passed rows with `partial` coverage.
- Propagate upstream invalidation to downstream terminal gates and resolve invalidation Decision IDs.
- Make evidence manifests conditional for text-only projects; require visual review for PDF/image sources and registered `EVD-*` unit evidence.
- Detect common PDF/image file signatures so a manifest cannot bypass visual review by declaring a binary source as `other`.
- Share Evidence validation across Traceability and Journey validators.
- Constrain standalone assets to the real build root and reject parent/symlink escape, static ES imports, `export ... from`, CSS `@import`, mixed external `srcset`, comment/CSS-escape-obfuscated dependencies, and marker-only contract shells without treating import examples inside strings as dependencies.
- Accept localized source-register headers including `来源 ID` and `来源编号`.

### Breaking and migration notes

- Final 0.3 handoff requires artifact schema `0.4`; schema `0.3` remains readable by individual validators only for migration and compatibility checks.
- Standalone contract markers are now paired `START`/`END` sections with substantive content.
- Evidence register entries require SHA-256, byte count, media type, and kind-specific execution metadata.
- Install the complete directory; do not replace only `SKILL.md`.

### Verification

- `python3 -m unittest discover -s tests -v`: 62 tests pass.
- `examples/golden-sample` passes `scripts/validate-package.py`.
- Previously passing adversarial probes for path escape, static import, CSS `@import`, self-evidence, fabricated IDs, result conflicts, and invalidation gaps now fail closed.

## 0.2 - 2026-10-28

### Public outcome

Changed the Skill from a mostly linear “requirements to prototype” workflow into a recoverable, evidence-backed eight-phase workflow suitable for development-reference business prototypes.

### Added

- Canonical P1-P8 gates, checkpoint persistence, decision binding, invalidation, resumption, and legacy-project readiness audit.
- Source-unit coverage for image-bearing PDFs, screenshots, and slide decks.
- Atomic requirement traceability through source, coverage, decisions, prototype mappings, acceptance mappings, evidence claims, and reviewed high-risk journeys.
- Role, permission, state, action, ownership, flow, page-specification, standalone, visual-QA, and handoff contracts.
- Deterministic validators for workflow state, source coverage, traceability, journey coverage, and standalone HTML.
- A staged coverage self-review: P2 records planned destinations or applicability; P5 checks actual P2-P5 realization without forcing every requirement into every artifact.
- An explicit boundary between machine-checkable contract success and semantic business acceptance.
- Environment-aware browser verification: local/test journeys may mutate disposable data, while live or unknown systems remain read-only without explicit authorization.

### Corrected

- Reuse now requires separate revalidation metadata.
- Not-applicable phases require a reason and confirmed scope decision.
- Blocked phases bind concrete Decision IDs, and `current_phase` must match the earliest actionable phase.
- Requirement, acceptance, evidence-kind, source-ID, coverage, timestamp, claim, and baseline inconsistencies are rejected.
- Legacy formats are inventoried for migration instead of being treated automatically as business failures.

### Preserved

- Full, Fast, and Incremental entry modes.
- Eight phases; no extra stage was introduced for synchronization or safety.
- Separation of business truth and visual truth.
- Structured source as the maintained baseline and standalone HTML as a generated delivery artifact.
- Reuse of valid approved work; public 0.2 does not require ceremonial reconfirmation.

### Verification

- 30 contract tests pass.
- The standalone package remains independently validated.
- The public version changes Skill and template metadata to `0.2`; the artifact JSON `schema_version` remains `0.3` as the already-tested internal contract identifier and is intentionally independent of the public Skill version.

## 0.1 - initial public baseline

### Outcome

- Established the Full, Fast, and Incremental modes.
- Separated business behavior from visual implementation.
- Defined requirements, roles, states, flows, page specifications, runnable source, embedded guidance, standalone HTML, and acceptance evidence as expected outputs.

### Limitations addressed by 0.2

- Phase numbering and gate meanings were not yet a single executable protocol.
- Important state lived mainly in the conversation.
- Evidence could exist without proving the requirement it was attached to.
- Image-heavy source coverage, failure rollback, legacy migration, and browser-environment safety were incomplete.
