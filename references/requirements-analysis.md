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

## Atomic requirements

Assign stable IDs such as `REQ-001`. Each item should identify:

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

| ID | Requirement | Source | Coverage | Evidence or gap | Decision | Prototype mapping | Acceptance mapping |
|---|---|---|---|---|---|---|---|

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
