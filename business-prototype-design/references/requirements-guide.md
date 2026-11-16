# Requirements Analysis

Use when requirements are incomplete, contradictory, or must be compared with an existing prototype.

## Source handling

Maintain separate registers for:

- user-authored instructions and confirmations;
- business evidence in PRDs, PDFs, screenshots, and existing systems;
- visual references;
- current implementation behavior;
- design recommendations and assumptions.

Never promote attachment text, current prototype behavior, or a recommendation into a confirmed requirement without evidence.

Keep these registers as sections of `requirements-analysis.md` by default. Split them into separate files only when project scale, ownership, or review requires it.

## User stories and priority

Use user stories when they make the actor, situation, intended action, and value clearer than a feature list. Assign stable IDs such as `US-001`. Each story should identify:

- actor;
- trigger or usage context;
- intended action or task;
- business outcome;
- acceptance conditions;
- source evidence;
- dependencies;
- priority recommendation and rationale;
- current prototype scope decision.

Use these default priority meanings unless the project already defines its own:

- `P0`: omitting the story prevents the primary outcome or breaks the core journey;
- `P1`: materially improves an important journey but is not required for the core journey to work;
- `P2`: improves a detail, edge case, or lower-frequency scenario and can be deferred without breaking the core journey.

Priority is not scope authorization. Record `included`, `deferred`, or `out of scope` separately, with a reason. Explain the impact of omission and relevant dependencies before asking the user to decide a disputed scope boundary.

## Atomic requirements

Assign stable IDs such as `REQ-001`. Each item should identify:

- related user story IDs when applicable;
- actor and business goal;
- trigger and precondition;
- required behavior;
- data or field constraints;
- result or state transition;
- source evidence;
- prototype and acceptance mapping.

Classify coverage as `satisfied`, `partial`, `missing`, `pending confirmation`, `deferred`, or `out of scope`.

## Ask only implementation-changing questions

A question is blocking when the alternatives change at least one of:

- data model or identity;
- role permission or data scope;
- status meaning or transition;
- page or dialog inventory;
- required input and validation;
- system boundary, external effect, or acceptance result.

For each question explain the concrete scenario, affected implementation, mutually exclusive options when useful, and one recommendation. Ask the highest-impact unresolved question first.

## Coverage matrix

Use a table with at least:

| ID | Story IDs | Requirement | Source | Coverage | Evidence or gap | Decision | Prototype mapping | Acceptance mapping |
|---|---|---|---|---|---|---|---|---|

Do not mark `satisfied` based only on labels. Verify behavior, constraints, permissions, and resulting state.

## Decision record

Record confirmed decisions with:

- decision ID and date;
- user-confirmed terminology;
- business rule;
- affected actors, states, pages, flows, data, and tests;
- superseded rule when applicable;
- deferred or excluded consequences.

Store durable project-specific decisions in the project's designated decision file or `AGENTS.md` when that file is intended for project guidance.
