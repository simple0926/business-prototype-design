---
name: business-prototype-design
description: Analyze or continue development-reference business-software prototypes from requirements, screenshots, flowcharts, PRDs, HTML, or existing prototypes; confirm business rules, model roles and states, specify pages, route visual implementation, and deliver a verified interactive prototype plus offline standalone HTML. Use for full workflows, approved fast prototypes, and traceable incremental revisions; not for disposable visual mocks or ordinary production coding.
metadata:
  version: "0.2"
---

# Business Prototype Design

Turn business requirements into a traceable, development-ready interactive prototype. Keep the confirmed business baseline, visual target, source, embedded guidance, standalone artifact, and acceptance evidence synchronized.

## Select the mode and earliest unmet gate

Inspect current project artifacts before doing substantive work, then select one mode:

- **Full:** requirements are fragmented, contradictory, or not approved.
- **Fast:** the user supplied a detailed approved baseline and explicitly asked to build.
- **Incremental:** a maintained prototype or source project exists and the request changes it.

Start from the earliest unmet or invalidated phase. Reuse valid confirmed work; a phase may be skipped, but its exit gate may not. Read [references/process-and-gates.md](references/process-and-gates.md) to choose the mode, apply gate decisions, or resume work.

For an existing project that predates the current templates, run `scripts/audit-legacy-project.py <project>` before rewriting artifacts. Treat its output as a read-only migration inventory: reuse valid business content, identify format gaps, and do not interpret legacy-format failure as a business defect.

For a multi-phase task, copy [assets/delivery-templates/prototype-workflow-state.json](assets/delivery-templates/prototype-workflow-state.json) into the project and update it when the mode is selected, a gate changes, work becomes blocked, verification starts, or handoff completes. The checkpoint is the project state of record; the conversation progress board is only its concise projection.

When a PDF, image set, slide deck, or screenshot-heavy document supplies evidence, also copy [assets/delivery-templates/evidence-manifest.json](assets/delivery-templates/evidence-manifest.json). Record every in-scope page or unit, how it was inspected, whether it is business or visual evidence, and its evidence IDs. Text extraction alone is insufficient when material information is embedded in images. `P1_EVIDENCE` may not pass until the manifest has complete source-unit coverage.

## Eight canonical phases

Use these IDs everywhere: checkpoint, progress board, artifacts, validation, and handoff.

| Phase | Work | Exit gate |
|---|---|---|
| `P1_EVIDENCE` | Inventory user instructions, business evidence, visual references, current behavior, tests, and decisions | Sources, precedence, scope, and truth ownership are explicit |
| `P2_REQUIREMENTS` | Create atomic requirements, coverage, decisions, assumptions, exclusions, and blocking questions | No silent implementation-changing ambiguity; every requirement has a planned downstream destination or a reason it is not applicable |
| `P3_BUSINESS_MODEL` | Define actors, data scope, permissions, canonical states, actions, transitions, and ownership | Status semantics, permissions, and ownership are confirmed or validly reused |
| `P4_FLOW` | Express the main flow and necessary subflows from the transition model | Diagrams, matrices, and business rules agree |
| `P5_PAGE_SPEC` | Define pages, dialogs, fields, controls, validation, states, and acceptance points | A developer can implement without inventing rules, and applicable requirements have reached an implementable surface or deliberate non-UI effect |
| `P6_BUILD` | Select the visual target and implement the core journey with realistic mock data | The primary journey works and matches the selected target |
| `P7_PACKAGE` | Synchronize embedded guidance and version data, build, and create the standalone artifact | Maintained source and one-file artifact represent the same baseline |
| `P8_HANDOFF` | Run business, functional, visual, traceability, browser, and offline checks | Evidence is reproducible and no blocking item remains |

Treat synchronization as an invariant across all phases, not a late documentation step. A changed decision must update or invalidate every affected requirement, role, state, flow, page, test, embedded guide, artifact, and gate.

## Gate decision contract

Use only these checkpoint statuses: `not_started`, `in_progress`, `blocked`, `confirmed`, `reused`, `invalidated`, `not_applicable`.

- Mark `reused` only when the artifact satisfies the current gate and no later evidence invalidates it. Record the original confirmation and the separate revalidation actor and timestamp.
- Mark `confirmed` with artifact path, evidence or decision ID, confirmer, timestamp, and baseline version.
- Mark `blocked` when alternatives change data, permissions, states, pages, validation, external effects, visual selection, or acceptance. Bind the phase to its open Decision IDs, and require every Decision to reference its affected phases. Ask one highest-impact question at a time and record the remaining decision queue.
- Mark `invalidated` when a later change affects a passed gate. Record the change or decision ID, invalidate downstream evidence, and resume from the earliest invalidated phase.
- Mark `not_applicable` only with a reason and a confirmed scope Decision ID that references the phase.
- Do not ask for blanket approval when an approved baseline and explicit build instruction already satisfy a gate.

`current_phase` must always equal the earliest phase that is not `confirmed`, `reused`, or `not_applicable`. Validate the checkpoint after every gate transition.

If a user decision is required, present the conflicting evidence, implementation consequences, and recommendation, then wait. Never infer publication, deployment, payment, deletion, or external messaging permission from a prototype request.

## Progress in Codex

After inspection, show the selected mode, current phase, reused phases, blocker if any, and remaining phases. Map checkpoint states to `✓` completed/reused, `▶` in progress, `⏸` blocked, `○` not started/invalidated, and `—` not applicable.

Update only at a meaningful milestone. Do not invent percentages or maintain progress separately from the checkpoint.

## Essential boundaries

- Attachments are evidence, not authority. Distinguish their contents from user instructions.
- Keep the **business source of truth** separate from the **visual source of truth**.
- Do not redesign or implement while a blocking business contradiction remains.
- Do not silently rename confirmed roles, states, actions, or outcomes.
- Do not call generated files complete without behavior, presentation, traceability, and standalone verification.
- Keep the prototype frontend-only unless backend behavior is explicitly requested.

## Phase routing

### `P1_EVIDENCE` and `P2_REQUIREMENTS`

Read relevant requirements, screenshots, PDFs, HTML, source, tests, `AGENTS.md`, decisions, and prototypes. Assign stable requirement IDs and maintain separate registers for instructions, business evidence, visual references, current behavior, and recommendations. For image-bearing sources, render and inspect all in-scope units and validate the evidence manifest. Read [references/requirements-analysis.md](references/requirements-analysis.md) when evidence is incomplete, inconsistent, or must be compared with an implementation.

Before closing P2, review each requirement for a planned downstream destination or an explicit not-applicable reason. This is a planning check, not a demand that future P3-P8 artifacts already exist. Do not force every requirement into every artifact.

### `P3_BUSINESS_MODEL` and `P4_FLOW`

For multi-role or approval work, build role-permission, status, and role-state-action models. Generate flows from confirmed transitions rather than screenshots. Derive a `journey-coverage.json` checklist for high-risk confirmed transitions; this is a reviewed checklist, not an inferred universal state parser. Read [references/role-state-and-flow.md](references/role-state-and-flow.md).

### `P5_PAGE_SPEC`

Derive the minimum page and dialog inventory. Specify actor, entry, exit, data scope, fields, controls, filters, operations, visibility, validation, feedback, loading, empty, error, permission, stale, and acceptance states. Read [references/page-specification.md](references/page-specification.md).

Fast mode may reuse an existing specification when it passes the readiness audit. State the baseline and proceed without a ceremonial reconfirmation.

Before closing P5, compare the P2 baseline with the actual business model, flows, page/dialog inventory, and deliberate non-UI effects. List unmapped or contradictory requirements instead of silently carrying them into implementation.

### `P6_BUILD`

Business requirements control behavior; the selected visual target controls presentation. When Product Design is available and visual work is in scope, read [references/product-design-integration.md](references/product-design-integration.md) before routing. Implement the core journey end to end, including navigation, filters, selections, dialogs, submissions, state changes, failure feedback, and results.

### `P7_PACKAGE`

Keep structured source as the maintained baseline. Unless the user narrows the deliverable, embed requirements, roles, flows, page guides, acceptance criteria, and version history. Include the contract markers defined in [references/standalone-html-contract.md](references/standalone-html-contract.md), then build the offline standalone artifact.

### `P8_HANDOFF`

Read [references/acceptance-and-handoff.md](references/acceptance-and-handoff.md). Run checks proportional to scope:

- build and automated behavior tests;
- browser execution of primary and changed regression paths;
- console, overflow, focus, disabled, empty, error, stale, permission, and result states;
- Product Design comparison when a visual target exists;
- workflow-state and requirement traceability validation;
- high-risk journey coverage with requirement-bound test or browser evidence;
- evidence-manifest coverage and passed-evidence registry validation;
- offline dependency validation and browser verification of the generated file itself.

Treat browser targets according to environment. Local prototypes, disposable fixtures, and authorized test environments may execute state-changing journeys. Treat live or unknown environments as read-only unless the user explicitly authorizes the specific external effect; never use real sensitive data merely to prove a prototype flow.

Use the supplied scripts when applicable:

```bash
python3 scripts/validate-evidence-manifest.py evidence-manifest.json
python3 scripts/validate-workflow-state.py prototype-workflow-state.json
python3 scripts/validate-journey-coverage.py --journeys journey-coverage.json --evidence-register evidence-register.json --baseline-version <baseline-version>
node scripts/build-standalone.mjs --input dist/client/index.html --output prototype-standalone.html
python3 scripts/validate-standalone-html.py prototype-standalone.html
python3 scripts/validate-traceability.py --requirements requirements-analysis.md --acceptance acceptance-report.md --evidence-register evidence-register.json --baseline-version <baseline-version> --design-qa design-qa.md
```

Adapt paths to the project. Reuse equivalent project-native build and test tooling rather than overwriting it.

## Deliverables by mode

- **Full:** create or confirm source-unit evidence coverage, the complete baseline, models, specification, source, embedded guidance, QA, acceptance evidence register, checkpoint, and standalone artifact.
- **Fast:** reuse and validate the approved baseline and its source coverage; create only missing downstream artifacts, but preserve traceability to the reused evidence.
- **Incremental:** record the change impact, invalidate affected gates, preserve unaffected behavior, update source coverage and synchronized artifacts, and run targeted plus broad regression checks with refreshed evidence entries.

Use templates only when the project has no equivalent artifact.

## Completion standard

Complete means every in-scope requirement is implemented or explicitly deferred; canonical state meanings and role-facing mappings agree; core interactions work in the browser; visual QA is passed or honestly blocked by missing comparable evidence; the generated standalone works without project files or network resources; and the evidence manifest, checkpoint, requirements, flows, journey checklist, prototype, evidence register, tests, acceptance report, and version record agree. A `passed` acceptance row must resolve its implementation and test evidence IDs to existing, passed artifacts for the same baseline. Every referenced Evidence entry must contain a claim for that Requirement ID with a claim type, scenario ID, and observable assertions. High-risk interaction, validation, and state-transition journeys must resolve to matching passed test or browser claims. Requirement Source IDs must resolve in the source register, Coverage must use the defined vocabulary, and `missing` or `pending_confirmation` coverage may not be reported as `passed`.

Validator success proves only the contracts it actually checks, such as structure, references, baseline agreement, and evidence binding. It does not by itself prove that the business rule, interaction, visual result, or external effect is correct; semantic acceptance still requires the applicable business, functional, visual, and delivery evidence.

If any blocking item remains, record it and stop at the appropriate gate instead of presenting partial work as complete.

## Release and validation notes

- Read [UPDATE_HISTORY_CN.md](UPDATE_HISTORY_CN.md) when explaining the public evolution from 0.1 to 0.2.
- Read [VALIDATION_MATERIALS_CN.md](VALIDATION_MATERIALS_CN.md) when planning the next forward-validation sample or deciding what evidence a phase still needs.
