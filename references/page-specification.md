# Page Specification

Use before building a new module or whenever existing requirements do not let a developer implement pages without inventing rules.

## Page inventory

For each page or dialog record:

- stable page ID and name;
- page type;
- primary actor and task;
- entry and exit;
- data scope and status context;
- upstream and downstream surfaces;
- whether the page is editable, read-only, or status-dependent.

## List pages

Specify:

- columns, data type, source, formatting, truncation, and fixed columns;
- filters, input type, allowed values, dependencies, reset behavior, and matching rules;
- sort, pagination, selection, select-all scope, and batch eligibility;
- row actions and exact visibility rules by role and status;
- empty, loading, error, permission-denied, stale, and partial-result states.

## Detail and form pages

For every field define:

| Field | Control | Data type | Source | Required | Default | Validation | Editable when | Permission | Persistence |
|---|---|---|---|---|---|---|---|---|---|

Also specify grouping, hierarchy, read-only presentation, attachment behavior, character and file limits, and dependent fields.

## Actions and dialogs

For each action define:

- display condition and disabled condition;
- confirmation or additional input;
- validation and transaction-time revalidation;
- success and failure feedback;
- state transition and next destination;
- repeat-click and idempotency expectations;
- audit record where relevant.

## Embedded page guide

Each main prototype page should expose a compact developer guide covering:

- business scenario;
- page function and logic;
- users and permissions;
- page actions;
- input requirements and limits;
- filters and limits;
- operation field definitions;
- data type and source;
- field dictionary;
- states and permissions;
- exceptions and boundaries;
- acceptance points.

Keep this guide collapsible or otherwise secondary to the operational interface.

## Acceptance readiness

A page specification is ready when:

- all fields and controls have types and constraints;
- every operation has status and permission rules;
- the happy path and relevant failure paths are explicit;
- visual requirements have a source or are clearly labeled recommendations;
- each requirement maps to a visible behavior or deliberate non-UI system effect.
