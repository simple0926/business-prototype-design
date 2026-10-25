# Role, State, And Flow Modeling

Use for multi-role workbenches, approvals, task routing, review flows, rejection, resubmission, terminal actions, or cross-role status views.

## Role and permission matrix

For every actor define:

- organizational responsibility;
- visible data scope;
- permitted pages;
- create, edit, submit, assign, approve, reject, return, void, view, import, and export permissions when applicable;
- ownership of exceptions and corrections;
- system actions versus human actions.

Do not create a role because a label appears in a screenshot; require business evidence or user confirmation.

## Status dictionary

For every status define:

- canonical name and business meaning;
- entry event;
- responsible actor;
- permitted operations;
- editability;
- next states;
- terminal or recoverable classification;
- how other roles see the same underlying task.

The same status name must mean the same business condition across roles. When views intentionally differ, document a mapping from one canonical lifecycle state to each role-facing label. If meanings differ, use different status names.

## Role-state-action matrix

Use this minimum structure:

| Canonical state | Role-facing state | Actor | Visible actions | Preconditions | Resulting state | Next actor | Notes |
|---|---|---|---|---|---|---|---|

Treat an operation, a user-visible status, and a backend data effect as separate concepts. For example, an approval operation may yield an approved UI status while storage is only a backend effect.

## Transition quality checks

- Every nonterminal state has an owner and at least one valid exit.
- Every visible action has a precondition, result, success feedback, and failure behavior.
- Reject, return, modify, resubmit, ignore, cancel, and void are not interchangeable.
- A destructive or irreversible result has confirmation and an audit consequence.
- Batch actions define eligibility, partial success, and per-item results.
- Cross-role mapping does not create contradictory statuses for the same event.

## Flow diagrams

Build diagrams from the confirmed transition model, not from visual guesswork.

Each flow description must answer:

- who acts;
- in which business stage;
- on which task or data;
- what action is taken;
- what condition branches the flow;
- what result and next owner follow.

Use one main flow for the end-to-end path and separate subflows where detail would make the main flow unreadable. Keep detailed subflow nodes out of the prototype navigation when those roles are explicitly outside prototype scope.

Before handoff, compare diagram nodes and transitions against the status dictionary, role-state-action matrix, prototype, and acceptance tests.
