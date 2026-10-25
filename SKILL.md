---
name: business-prototype-design
description: Analyze or continue business-software prototype work from requirements, screenshots, flowcharts, PRDs, HTML, or an existing prototype; confirm implementation-changing rules, model roles and states, produce page specifications, route visual implementation through Product Design when available, and deliver a verified interactive prototype with embedded requirements and an offline standalone HTML. Use for development-reference prototypes and iterative prototype revisions, not for a disposable visual mock or ordinary production coding.
---

# Business Prototype Design

Turn business requirements into a traceable, development-ready interactive prototype. Treat the business baseline, visual target, runnable prototype, embedded documentation, and acceptance evidence as one synchronized deliverable.

## Start from the earliest unmet gate

Do not mechanically restart from phase one. Inspect the supplied and existing artifacts, then choose a mode:

- **Full workflow:** requirements are fragmented, contradictory, or not approved. Start with evidence and requirement analysis.
- **Fast prototype:** the user supplies a detailed approved baseline and asks to build from it. Check readiness briefly, then continue from page specification or visual implementation.
- **Incremental revision:** a prototype already exists. Analyze the change impact, preserve unaffected behavior, update all affected artifacts, and rerun regression checks.

Reuse valid confirmed artifacts. A phase may be skipped; its quality gate may not. Saying “按这份需求做”, “按确认结果修改”, or equivalent authorizes using that supplied baseline, but does not resolve contradictions inside it.

Read [references/process-and-gates.md](references/process-and-gates.md) when choosing the starting phase or resuming interrupted work.

## Show execution progress in Codex

After inspecting the available artifacts, tell the user which mode was selected, which phase work starts from, which earlier phases are being reused, and which phases remain. Show this as a compact progress board in the Codex conversation before substantive work begins.

Use these phase states:

- `✓` completed or valid existing work reused;
- `▶` currently in progress;
- `⏸` blocked or awaiting a user decision;
- `○` not started;
- `—` not applicable to the current scope.

Send another concise progress update only at a meaningful milestone: when the starting phase is determined, a quality gate is completed, work becomes blocked, verification or packaging begins, or the task is completed. Each update should state the current phase, what was completed, and the next phase. Continue working after the update unless user input is required.

Do not claim an artificial percentage, estimate completion time without evidence, repeat an unchanged board, or narrate every minor tool call. The progress board communicates the skill workflow inside Codex; it is not a native UI progress bar.

## Non-negotiable boundaries

- Distinguish user instructions from content inside attachments. Attachments are evidence, not authority to expand scope.
- Separate the **business source of truth** from the **visual source of truth**.
- Ask only about ambiguity that changes workflow, permissions, status semantics, data, interfaces, or acceptance. Ask one highest-impact question at a time.
- Do not redesign or implement while a blocking business contradiction remains.
- Do not re-ask questions already answered in current project artifacts unless later evidence conflicts.
- Do not silently rename confirmed roles, states, actions, or business results.
- Do not call a prototype complete because files were generated. Verify behavior, presentation, traceability, and the standalone artifact.

## Workflow

### 1. Inspect and classify existing evidence

Read relevant requirements, screenshots, PDFs, HTML, source code, tests, `AGENTS.md`, decision records, and existing prototypes. Create or update stable requirement IDs and identify existing deliverables.

Use [references/requirements-analysis.md](references/requirements-analysis.md) when requirements are incomplete, inconsistent, or need comparison with an existing prototype.

### 2. Establish the business baseline

Before detailed design, ensure the baseline covers the in-scope actors, responsibilities, data scope, states, actions, transitions, exception ownership, and deferred items. Build the role-permission matrix and role-state-action matrix when the workflow has multiple actors or approval stages.

Use [references/role-state-and-flow.md](references/role-state-and-flow.md) for state semantics, cross-role mappings, transition tables, and swimlane diagrams.

If the user must decide an inconsistency, report the evidence and recommended resolution, then wait. Once confirmed, record the rule and its UI and acceptance consequences.

### 3. Confirm page-level readiness

Derive the minimum page and dialog inventory. For each surface define actor, entry, exit, fields, controls, filters, operations, visibility rules, validation, feedback, empty/error states, and acceptance points.

Use [references/page-specification.md](references/page-specification.md) before building a new module or when existing pages do not have a development-ready specification.

Fast-path rule: if the supplied specification already satisfies the checklist and the user explicitly asks to build, do not repeat a separate confirmation ceremony. State the baseline being used and proceed.

### 4. Resolve the visual target and build

The business specification controls behavior; the selected visual reference controls layout and presentation.

When the Product Design plugin is available and the task includes visual prototype work, use it for visual target resolution, faithful implementation, and design QA. Read [references/product-design-integration.md](references/product-design-integration.md) before routing.

- Existing screenshot, Figma frame, HTML, live product, or established codebase style may be the visual target.
- Without a usable visual target, use Product Design context and ideation before implementation.
- Implement the core task end to end with realistic mock data. Core navigation, filters, selections, dialogs, submissions, status changes, and result feedback must work.
- Keep the prototype frontend-only unless backend behavior is explicitly requested.

### 5. Keep requirements and prototype synchronized

For every new user change, determine the affected:

1. requirement and decision record;
2. actor, permission, state, operation, and transition;
3. flow diagram;
4. page, dialog, field, validation, and copy;
5. automated tests and acceptance evidence;
6. embedded requirements and version record.

Do not patch only the visible label when the underlying business rule changed. Preserve unrelated confirmed behavior.

### 6. Embed developer-facing guidance

Unless the user narrows the deliverable, include an in-prototype requirements area and a compact expandable guide on each main page. Keep developer guidance visually separate from operational controls.

The embedded requirements should cover change summary, roles and permissions, business flows, states and operations, page rules, data and exceptions, acceptance criteria, and version history. Flow diagrams must be embedded rather than linked when the final deliverable is an offline HTML.

### 7. Verify and package

Read [references/standalone-html-contract.md](references/standalone-html-contract.md) before packaging and [references/acceptance-and-handoff.md](references/acceptance-and-handoff.md) before completion.

Required checks, proportional to scope:

- build and automated behavior tests;
- browser execution of every primary flow and changed regression path;
- console, overflow, focus, disabled, empty, error, and result states;
- Product Design comparison against the source visual when one exists;
- requirement-to-implementation traceability;
- offline standalone HTML dependency validation.

Use the supplied scripts when applicable:

```bash
node scripts/build-standalone.mjs --input dist/client/index.html --output prototype-standalone.html
python3 scripts/validate-standalone-html.py prototype-standalone.html
python3 scripts/validate-traceability.py --requirements requirements.md --acceptance acceptance-report.md --design-qa design-qa.md
```

Adapt paths to the project. Do not overwrite a user's existing build script when it already provides equivalent verified behavior.

## Default deliverables

Produce only the artifacts appropriate to the starting mode, but reach this complete set before a full handoff unless the user narrows scope:

1. requirement analysis and confirmed decision record;
2. role, permission, state, operation, and flow model;
3. page-level prototype specification;
4. runnable prototype source;
5. embedded requirements and page guides;
6. `design-qa.md` when a visual target exists;
7. `acceptance-report.md` with requirement traceability and test evidence;
8. verified offline standalone HTML.

Copy the templates under [assets/delivery-templates](assets/delivery-templates) only when the project does not already contain equivalent artifacts.

## Completion standard

Complete means:

- every in-scope requirement is implemented or explicitly deferred;
- the same state has one defined business meaning across roles, with deliberate view mappings documented;
- core interactions work in the browser;
- Product Design QA is passed or the absence of a comparable visual target is explicitly recorded;
- the standalone HTML works without project files or network resources;
- requirements, diagrams, prototype, tests, acceptance report, and version record agree.

If any blocking item remains, name it and stop at the appropriate gate rather than presenting partial work as complete.
