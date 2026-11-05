# Golden Sample Prototype Specification

- Baseline version: B-GOLDEN-001
- Primary user outcome: Submit and approve a service request.
- Included actors: Requester, Reviewer
- Included journeys: JNY-001
- Selected visual target: Functional neutral workbench; visual comparison is out of scope.

## Page inventory

| Page ID | Name | Actor | Entry | Exit | Requirement IDs |
|---|---|---|---|---|---|
| PAGE-001 | Request list | Requester | App start | PAGE-002 | REQ-001 |
| PAGE-002 | Request editor | Requester | Create or edit | PAGE-001 | REQ-001, REQ-002, REQ-004 |
| PAGE-003 | Review queue | Reviewer | Role switch | PAGE-001 | REQ-003 |

## Acceptance points

| Acceptance ID | Requirement ID | Observable result |
|---|---|---|
| ACC-001 | REQ-001 | Create opens an editable draft and saving returns to the list. |
| ACC-002 | REQ-002 | Submit changes the request from draft to submitted. |
| ACC-003 | REQ-003 | Approve changes the submitted request to approved. |
| ACC-004 | REQ-004 | Submit with an empty title shows validation feedback and keeps draft state. |

