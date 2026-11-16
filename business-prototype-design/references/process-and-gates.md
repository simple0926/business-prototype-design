# Process And Gates

Use this reference to select the starting mode, resume work, or decide whether a phase can be skipped.

## Core rule

Inspect existing artifacts and start from the earliest unmet quality gate. Reuse valid confirmed work; do not repeat it for ceremony. A phase is optional when its output already exists and remains valid. Apply each exit criterion to the selected prototype and delivery scope.

## Modes

### Full workflow

Use when requirements are fragmented, conflicting, or not approved.

Expected path: evidence inventory → requirements → business model → flows → page specification → prototype type and design choice → construction → selected delivery → acceptance.

### Fast prototype

Use when the user supplies a detailed baseline and explicitly asks to build from it.

Perform a short readiness audit. If the baseline defines actors, key states, operations, pages, validations, and a visual target or established design system, proceed without replaying earlier phases. Ask only when a missing rule materially changes implementation.

### Incremental revision

Use when a runnable prototype or maintained source project exists.

Inspect the current behavior and source before editing. Convert feedback into atomic changes, map the impact, preserve unaffected behavior, update synchronized artifacts, and run targeted plus broad regression checks.

## Eight phases

| Phase | Main work | Required output | Exit gate |
|---|---|---|---|
| 1. Evidence inventory | Read relevant user requests, attachments, current files, tests, and decisions | Source register section in `requirements-analysis.md`; business and visual truth identified | Sources and precedence are explicit |
| 2. Requirement analysis | Form user stories when useful; assign priorities; split atomic requirements; identify gaps, conflicts, assumptions, and deferrals | Story and requirement coverage, priority rationale, decisions, and blocking questions in `requirements-analysis.md` | Scope decisions are explicit; no silent implementation-changing ambiguity |
| 3. Business modeling | Define actors, permissions, states, actions, transitions, ownership | Role-permission and role-state-action sections in `requirements-analysis.md` | Status semantics and ownership are confirmed |
| 4. Flow confirmation | Express who does what in each stage and result | Main flow, subflows, and text descriptions in `requirements-analysis.md` | Diagrams and business rules agree |
| 5. Page specification | Map rules to pages, dialogs, fields, controls, validation, states | Page inventory and detailed rules in `prototype-spec.md` | The prototype can be built without inventing business rules |
| 6. Prototype construction | Confirm the prototype type and design standard, then follow approved flows and page specifications | Runnable interactive source and runtime checks, or static images for agreed pages and states | Output satisfies the confirmed behavior or visual scope for the chosen type |
| 7. Delivery format | Confirm the delivery format and agreed inventory | Verified offline HTML or prototype images | Output meets the selected format and agreed coverage |
| 8. Verification and handoff | Check the confirmed outputs and decisions from stages 4–7 | Acceptance report and Design QA when a selected visual target applies | Applicable checks pass or have an approved deferral; evidence is reproducible |

## Readiness audit for a fast prototype

Check only these minimums:

- scope and primary user outcome;
- prioritized in-scope user stories or equivalent atomic requirements;
- actors and data scope;
- statuses, available actions, and resulting transitions;
- page and dialog inventory;
- key fields, requiredness, validation, and visibility;
- exception or rejection paths that affect the core flow;
- visual target or existing design language;
- explicit user instruction to use the baseline for implementation.

If all are sufficient, state which baseline is being used and continue. Do not ask for an additional blanket approval.

## Resuming interrupted work

Prefer project artifacts over chat memory. Read the current decision record, requirement baseline, prototype specification, source, test results, and acceptance report. Determine:

1. latest confirmed baseline;
2. completed phases and evidence;
3. unfinished or invalidated outputs;
4. next safe action.

If chat statements conflict with the latest confirmed project file, surface the conflict rather than guessing.
