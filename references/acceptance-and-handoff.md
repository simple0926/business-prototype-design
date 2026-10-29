# Acceptance And Handoff

Use before declaring the prototype complete.

## Four evidence layers

Before evaluating these layers, validate `prototype-workflow-state.json`. Every completed or reused gate must point to its artifact and evidence; an invalidated or blocked gate prevents a passed handoff.

Validate `evidence-manifest.json` before accepting P1 evidence coverage. For final `passed` rows, validate `evidence-register.json`: each implementation and test/browser evidence ID must resolve to an existing artifact with `result: passed`, the same baseline version, and an ISO 8601 capture timestamp with timezone. Evidence `kind` is limited to `implementation`, `test`, or `browser`; implementation columns accept only `implementation`, while test/browser columns accept `test` or `browser`. Nonempty placeholders such as `not-run` and `not-implemented` are not evidence.

Every Evidence entry used by a passed row also contains a nonempty `claims` list. Each claim binds one Requirement ID to a supported claim type (`presence`, `interaction`, `validation`, `state_transition`, or `delivery`), a stable scenario ID, and observable assertions. A real file that has no claim for the current Requirement does not prove that Requirement.

Validate `journey-coverage.json` for high-risk interactions, validations, and state transitions. A passed journey must resolve every listed Requirement ID to a matching passed test/browser claim with the same Journey ID and claim type. The checklist is reviewed from confirmed P3/P4 models; it is not produced by guessing from free-form text.

Passing a validator proves only the machine-checkable contract named by that validator. It does not prove that a requirement is the right requirement, that an assertion expresses the confirmed business meaning, that the visual target was interpreted correctly, or that an external effect really occurred. Keep mechanical contract results and semantic acceptance conclusions separate.

## Browser environment boundary

Classify the browser target before executing a journey:

- local prototype, disposable fixture, or authorized test environment: state-changing journeys may run with test data;
- live or environment-unknown system: remain read-only unless the user explicitly authorizes the specific external effect;
- sensitive-data surface: use synthetic or redacted data and do not retain secrets in screenshots, logs, or evidence artifacts.

Record the environment and expected data side effect in browser evidence. Do not ask for repeated confirmation for ordinary local prototype interactions already in scope, and do not treat the permission to build a prototype as permission to mutate a live system.

### Business acceptance

- Every in-scope requirement maps to implemented behavior or an explicit deferral.
- Actors, permissions, states, operations, and flow diagrams agree.
- Non-UI backend effects are labeled as such and are not invented as user-visible statuses.
- Deferred and out-of-scope roles or flows have not leaked into the prototype.

### Functional acceptance

- Primary navigation and end-to-end journeys work.
- Every reviewed high-risk journey has a requirement-bound test or browser assertion.
- Status-dependent actions appear and disappear correctly.
- Required fields, character limits, file limits, disabled states, confirmations, and feedback work.
- Relevant empty, error, stale, permission-denied, partial-success, and retry states are covered.
- Batch operations report eligibility and per-item outcomes.

### Visual acceptance

- The rendered implementation has been compared with the selected visual truth at the same viewport and state.
- Product Design P0, P1, and P2 findings are resolved when Product Design applies.
- Overflow, truncation, density, spacing, focus, contrast, and persistent controls have been inspected.

### Delivery acceptance

- Build and automated tests pass.
- Browser console and primary flows have been checked.
- Standalone HTML works offline and contains its required resources.
- Requirements, diagrams, page guides, tests, acceptance report, and version record are synchronized.
- The workflow checkpoint uses the same baseline version and phase IDs as the acceptance report.
- The journey checklist and evidence claims use the same baseline and Requirement IDs.

## Acceptance report structure

For each requirement include:

| Requirement ID | Confirmed rule | Implementation evidence IDs | Test or browser evidence IDs | Result | Notes |
|---|---|---|---|---|---|

Do not claim `passed` without observable evidence. When verification is blocked, state the blocker and the unverified surface.

Do not use one broad test report as evidence for unrelated requirements. Reuse is allowed only when that Evidence entry declares a separate claim for every Requirement it proves.

Use the structured `<!-- ACCEPTANCE_RESULT: ... -->` marker from the template so automated checks can distinguish a draft from a passed report.

## Handoff

Lead with the working artifact or preview. Then provide:

- standalone HTML and maintained source location;
- concise scope summary;
- important confirmed rules;
- test, browser, design QA, and offline validation results;
- unresolved or deferred items;
- checkpoint mode, baseline version, and any not-applicable phases;
- one useful next action.

Do not deploy, publish, or create a share link unless the user asked for that external action.
