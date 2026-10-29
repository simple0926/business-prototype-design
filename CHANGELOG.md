# Changelog

This file uses the public release sequence. The public `0.2` consolidates the internally validated development work that previously used later internal version labels; those historical packages remain unchanged.

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
