# Acceptance Report

<!-- ACCEPTANCE_RESULT: blocked -->

## 1. Result and baseline

- Skill version: 0.2
- Workflow checkpoint:
- Evidence register:
- Journey coverage:
- Baseline version:
- Maintained source:
- Standalone artifact:
- Overall result: blocked

## 2. Gate evidence

| Phase ID | Status | Artifact | Evidence or decision | Verification |
|---|---|---|---|---|

## 3. Requirement coverage

| Requirement ID | Confirmed rule | Implementation evidence IDs | Test or browser evidence IDs | Result | Notes |
|---|---|---|---|---|---|

Result values: `passed`, `deferred`, `out_of_scope`, `not_applicable`. Use `blocked`, `pending`, or `partial` only before final handoff and validate with `--allow-pending`.

Every `passed` row must reference `EVD-*` entries in `evidence-register.json`. Each entry must resolve to an existing artifact, have `result: passed`, match the report baseline, and include an ISO 8601 capture timestamp with timezone. Implementation evidence must use `kind: implementation`; test/browser evidence must use `kind: test` or `kind: browser`. Each referenced entry must contain a claim for the current Requirement ID with a supported claim type, scenario ID, and observable assertions. Placeholder values such as `not-run` and `not-implemented` are not evidence.

## 4. Automated checks

| Check | Command | Result | Evidence |
|---|---|---|---|

## 5. Browser verification

| Journey or state | Artifact tested | Environment | Data side effect | Viewport | Result | Evidence |
|---|---|---|---|---|---|---|

Explicitly test the generated standalone file, not only the development server.

Validate high-risk interactions, validations, and state transitions with `journey-coverage.json`; a passed journey must resolve to matching test/browser claims.

## 6. Visual QA

- Design QA artifact:
- Source visual:
- Implementation capture:
- Final result:
- Remaining P3 polish:

## 7. Standalone validation

- Contract markers:
- External dependencies:
- Offline browser result:
- Console result:

## 8. Deferred or blocked items

| Item | Reason | Owner | Decision or revisit condition | Affected phases |
|---|---|---|---|---|

Change the structured result marker and overall result only when all required final checks pass and no blocking item remains.
