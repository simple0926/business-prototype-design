# Process And Gates

Use this reference to select the starting mode, resume work, or decide whether a phase can be skipped.

## Core rule

Inspect existing artifacts and start from the earliest unmet quality gate. Reuse valid confirmed work; do not repeat it for ceremony. A phase is optional when its output already exists and remains valid. Its exit criteria are never optional.

## Modes

### Full workflow

Use when requirements are fragmented, conflicting, or not approved.

Expected path: evidence inventory → requirement analysis → business model → flow confirmation → page specification → visual target → prototype → package and acceptance.

### Fast prototype

Use when the user supplies a detailed baseline and explicitly asks to build from it.

Perform a short readiness audit. If the baseline defines actors, key states, operations, pages, validations, and a visual target or established design system, proceed without replaying earlier phases. Ask only when a missing rule materially changes implementation.

### Incremental revision

Use when a runnable prototype or maintained source project exists.

Inspect the current behavior and source before editing. Convert feedback into atomic changes, map the impact, preserve unaffected behavior, update synchronized artifacts, and run targeted plus broad regression checks.

## Eight phases

| Phase | Main work | Required output | Exit gate |
|---|---|---|---|
| 1. Evidence inventory | Read relevant user requests, attachments, current files, tests, and decisions | Source register; business and visual truth identified | Sources and precedence are explicit |
| 2. Requirement analysis | Split atomic requirements; identify gaps, conflicts, assumptions, deferrals | Coverage matrix; decision log; blocking questions | No silent implementation-changing ambiguity |
| 3. Business modeling | Define actors, permissions, states, actions, transitions, ownership | Role-permission and role-state-action matrices | Status semantics and ownership are confirmed |
| 4. Flow confirmation | Express who does what in each stage and result | Main flow, subflows, text descriptions | Diagrams and business rules agree |
| 5. Page specification | Map rules to pages, dialogs, fields, controls, validation, states | Page inventory and detailed specification | A developer can implement without inventing rules |
| 6. Visual and interaction build | Select visual truth and implement the core journey | Runnable source and realistic prototype data | Primary flow works and matches the chosen target |
| 7. Synchronization and packaging | Embed requirements, diagrams, page guides, and version history | Maintained source plus standalone artifact | One-file artifact contains the agreed baseline |
| 8. Verification and handoff | Run tests, browser checks, design QA, traceability, offline validation | Design QA and acceptance report | No unresolved blocking issue; evidence is reproducible |

## Readiness audit for a fast prototype

Check only these minimums:

- scope and primary user outcome;
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
