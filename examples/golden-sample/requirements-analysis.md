# Golden Sample Requirements

- Baseline version: B-GOLDEN-001
- Workflow mode: full
- Objective: Let a requester submit a service request and a reviewer approve it.

## Source register

| Source ID | Type | Owner | Version or date | Authority | Relevant scope | Notes |
|---|---|---|---|---|---|---|
| SRC-001 | approved text baseline | product owner | 2026-11-04 | business | REQ-001..REQ-004 | Golden sample input |

## Requirement coverage

| ID | Requirement | Source | Coverage | Evidence or gap | Decision | Prototype mapping | Acceptance mapping |
|---|---|---|---|---|---|---|---|
| REQ-001 | Requester can open the request list and create a draft. | SRC-001 | satisfied | Implemented in the standalone artifact | DEC-001 | PAGE-001, PAGE-002 | ACC-001 |
| REQ-002 | Requester can submit a complete draft and transfer ownership to Reviewer. | SRC-001 | satisfied | JNY-001 covers the state transition | DEC-001 | PAGE-002 | ACC-002, JNY-001 |
| REQ-003 | Reviewer can approve a submitted request. | SRC-001 | satisfied | Executable DOM-harness evidence covers approval | DEC-001 | PAGE-003 | ACC-003 |
| REQ-004 | Required title validation prevents an incomplete submission. | SRC-001 | satisfied | Test evidence covers validation | DEC-001 | PAGE-002 | ACC-004 |

## Roles and four canonical states

| Role | Responsibility | Data scope | Pages | Allowed operations | Exceptions owned |
|---|---|---|---|---|---|
| Requester | Create and submit requests | Own requests | PAGE-001, PAGE-002 | create, edit, submit | Fix validation errors |
| Reviewer | Review submitted requests | Submitted requests | PAGE-003 | approve | Resolve review exceptions |

| Canonical state | Business meaning | Owner | Next states |
|---|---|---|---|
| new | No draft exists yet | Requester | draft |
| draft | Request is editable | Requester | submitted |
| submitted | Awaiting review | Reviewer | approved |
| approved | Review completed | Reviewer | terminal |

