# Business Prototype Handoff Contract

- Contract: `business-prototype-handoff`
- Version: `1.0.0`

This contract lets any stage package consume prior work without requiring another skill to be installed.

## Required artifact header

Every primary Markdown artifact begins with this metadata. Use `none` or an empty list instead of silently omitting a field.

```yaml
---
handoff_contract: business-prototype-handoff/1.0.0
stage: evidence | requirements | modeling | flows | specification | build | packaging | review
artifact: evidence-register | requirements-analysis | business-model | business-flows | prototype-spec | prototype-build-report | packaging-report | acceptance-report
status: draft | ready | blocked
baseline_version: string
inputs:
  - path-or-source-id
unresolved:
  - decision-or-blocker-id
next_stage: package-name | none
---
```

`ready` means the current stage exit gate passed. It does not approve later work. `blocked` means a missing decision prevents a reliable stage output. `draft` means useful work exists but the exit gate has not passed.

## Stable IDs

Preserve IDs across edits and downstream stages:

| Prefix | Meaning |
|---|---|
| `SRC-*` | source or evidence item |
| `US-*` | user story |
| `REQ-*` | atomic requirement |
| `DEC-*` | confirmed decision |
| `ROLE-*` | actor or role |
| `STATE-*` | canonical business state |
| `FLOW-*` | main flow or subflow |
| `PAGE-*` | page or dialog |
| `QA-*` | review finding |

Do not renumber confirmed IDs merely to close gaps.

## Required sections

Every primary artifact must make these items discoverable, using stage-appropriate headings:

1. scope and exclusions;
2. inputs and source IDs;
3. confirmed content;
4. assumptions and recommendations clearly separated from facts;
5. unresolved decisions and blockers;
6. downstream mappings or expected consumer;
7. exit-gate result.

## Consumer rules

- Verify the contract version and artifact status before relying on the artifact.
- A `ready` upstream artifact may be reused, but later conflicting user confirmation takes precedence and must be recorded.
- A `draft` artifact may provide evidence but cannot silently become an approved baseline.
- A `blocked` artifact does not authorize the next stage.
- Preserve source, story, requirement, decision, role, state, flow, and page IDs in downstream mappings.
- If an equivalent project artifact uses another filename, keep it and add the required metadata and mappings rather than duplicating it.

## Stage chain

| Stage | Primary artifact | Default next stage |
|---|---|---|
| evidence | `evidence-register.md` | `business-prototype-requirements` |
| requirements | `requirements-analysis.md` | `business-prototype-modeling` |
| modeling | `business-model.md` | `business-prototype-flows` |
| flows | `business-flows.md` | `business-prototype-specification` |
| specification | `prototype-spec.md` | `business-prototype-build` |
| build | `prototype-build-report.md` plus the selected prototype | `business-prototype-packaging` |
| packaging | `packaging-report.md` plus the selected deliverable | `business-prototype-review` |
| review | `acceptance-report.md` and optional `design-qa.md` | none |

The chain describes compatibility, not permission to continue. A stage skill stops after its own exit gate.

In the orchestrator, build and packaging outputs follow the recorded choices in [prototype-and-delivery.md](prototype-and-delivery.md). Consolidated outputs may reference the relevant sections instead of duplicating standalone reports.
