# Acceptance And Handoff

Use before declaring the prototype complete.

## Four evidence layers

### Business acceptance

- Every in-scope requirement maps to implemented behavior or an explicit deferral.
- Actors, permissions, states, operations, and flow diagrams agree.
- Non-UI backend effects are labeled as such and are not invented as user-visible statuses.
- Deferred and out-of-scope roles or flows have not leaked into the prototype.

### Functional acceptance

- Primary navigation and end-to-end journeys work.
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

## Acceptance report structure

For each requirement include:

| Requirement ID | Confirmed rule | Implementation evidence | Test or browser evidence | Result | Notes |
|---|---|---|---|---|---|

Do not claim `passed` without observable evidence. When verification is blocked, state the blocker and the unverified surface.

## Handoff

Lead with the working artifact or preview. Then provide:

- standalone HTML and maintained source location;
- concise scope summary;
- important confirmed rules;
- test, browser, design QA, and offline validation results;
- unresolved or deferred items;
- one useful next action.

Do not deploy, publish, or create a share link unless the user asked for that external action.
