# Requirements Analysis

## 1. Baseline and scope

- Objective:
- In scope:
- Out of scope:
- Business source of truth:
- Visual source of truth:
- Baseline version:
- Workflow mode:

## 2. Source register

| Source ID | Type | Owner | Version or date | Authority | Relevant scope | Notes |
|---|---|---|---|---|---|---|

Keep user instructions, business evidence, visual references, current behavior, and recommendations as distinct source types.
Every Source value in the requirement coverage table must resolve to a Source ID in this register.

## 3. Requirement coverage

| ID | Requirement | Source | Coverage | Evidence or gap | Decision | Prototype mapping | Acceptance mapping |
|---|---|---|---|---|---|---|---|

Coverage values: `satisfied`, `partial`, `missing`, `pending_confirmation`, `deferred`, `out_of_scope`.
`missing` and `pending_confirmation` coverage cannot have a final acceptance result of `passed`.
For interaction, validation, or state-transition requirements, include confirmed `JNY-*` IDs in Acceptance mapping.

## 4. Roles and permissions

| Role | Responsibility | Data scope | Pages | Allowed operations | Exceptions owned |
|---|---|---|---|---|---|

## 5. Status dictionary

| Canonical state | Business meaning | Entry event | Owner | Permitted operations | Editable | Next states | Terminal or recoverable | Role-facing labels |
|---|---|---|---|---|---|---|---|---|

## 6. Role-state-action matrix

| Canonical state | Role-facing state | Actor | Visible action | Preconditions | Resulting state | Next actor | Success feedback | Failure behavior |
|---|---|---|---|---|---|---|---|---|

## 7. Main flow and subflows

For each flow record its ID, actors, entry state, actions, branch conditions, resulting states, next owners, exceptions, and diagram location.

| Flow ID | Scope | Actors | Entry | Result | Diagram or description | Requirement IDs |
|---|---|---|---|---|---|---|

## 8. Confirmed decisions and decision queue

| Decision ID | Status | Date | Rule or question | Recommendation | Affected phases and artifacts | Supersedes or invalidates |
|---|---|---|---|---|---|---|

Decision status: `open`, `confirmed`, `superseded`, `deferred`.

## 9. Pending, deferred, and excluded items

| Item | Classification | Reason | Blocking | Owner | Revisit condition |
|---|---|---|---|---|---|
