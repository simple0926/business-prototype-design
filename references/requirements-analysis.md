# Requirements Analysis

Use when requirements are incomplete, contradictory, or must be compared with an existing prototype.

## Source handling

Maintain separate registers for:

- user-authored instructions and confirmations;
- business evidence in PRDs, PDFs, screenshots, and existing systems;
- visual references;
- current implementation behavior;
- design recommendations and assumptions.

For a PDF, image set, slide deck, or screenshot-heavy source, maintain `evidence-manifest.json` at page or unit level. Record the inspection method, classification, evidence IDs, and explicit exclusion reason where applicable. When important information appears in images, render and visually inspect every in-scope unit; text extraction alone does not satisfy evidence coverage.

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

For interaction, validation, or state-transition requirements, include the reviewed `JNY-*` scenario IDs in the acceptance mapping once the P3/P4 model is confirmed. Do not invent journey IDs before the underlying rule is confirmed.

Every requirement Source ID must resolve to the source register. User instructions and confirmations are valid sources when explicitly registered; they do not need to appear in the image/PDF evidence manifest.

Classify coverage as `satisfied`, `partial`, `missing`, `pending confirmation`, `deferred`, or `out of scope`. Normalize `pending confirmation` as `pending_confirmation` in the delivery table. `missing` and `pending_confirmation` coverage may not have a final acceptance result of `passed`.

## Ask only implementation-changing questions

A question is blocking when the alternatives change at least one of:

- data model or identity;
- role permission or data scope;
- status meaning or transition;
- page or dialog inventory;
- required input and validation;
- system boundary, external effect, or acceptance result.

For each question explain the concrete scenario, affected implementation, mutually exclusive options when useful, and one recommendation. Ask the highest-impact unresolved question first. Record other discovered questions in the decision queue with dependencies so they are not lost or repeatedly rediscovered.

## Coverage matrix

Use a table with at least:

| ID | Requirement | Source | Coverage | Evidence or gap | Decision | Prototype mapping | Acceptance mapping |
|---|---|---|---|---|---|---|---|

This eight-column schema is authoritative. The delivery template and traceability validator must use the same column count and order.

Do not mark `satisfied` based only on labels. Verify behavior, constraints, permissions, and resulting state.

## P2 coverage self-review

Before closing P2, review every requirement against the agreed scope and record one of:

- the downstream model, flow, page, journey, delivery, or acceptance area it is expected to affect;
- a deliberate non-UI system effect;
- a confirmed deferred or out-of-scope decision;
- an unresolved gap that keeps P2 open.

This is a planning review. P2 must not pretend that later P3-P8 artifacts already exist, and a requirement does not need to map to artifacts that are genuinely irrelevant. The purpose is to prevent requirements from disappearing between analysis and design, not to manufacture empty links.

## Decision record

Record confirmed decisions with:

- decision ID and date;
- user-confirmed terminology;
- business rule;
- affected actors, states, pages, flows, data, and tests;
- superseded rule when applicable;
- deferred or excluded consequences.

Also record decision status (`open`, `confirmed`, `superseded`, or `deferred`) and the affected canonical phase IDs. When a decision supersedes an earlier rule, mark affected gates and artifacts `invalidated` in `prototype-workflow-state.json`; do not merely append a newer paragraph.

Store durable project-specific decisions in the project's designated decision file or `AGENTS.md` when that file is intended for project guidance.
