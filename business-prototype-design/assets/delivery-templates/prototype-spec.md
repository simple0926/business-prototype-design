---
handoff_contract: business-prototype-handoff/1.0.0
stage: specification
artifact: prototype-spec
status: draft
baseline_version: none
inputs: []
unresolved: []
next_stage: business-prototype-build
---

# Prototype Specification

## 1. Module boundary

- Primary user outcome:
- Included actors:
- Included US:
- Included journeys:
- Exclusions:

### 1.1 Visual target (one per surface)

Reuse the design standard the user has chosen, including an existing product UI when selected. If the choice is open, present suitable options with tradeoffs and record the user’s selection before stage 6.

| Surface (web admin / dashboard / app) | Selected visual target | Source | Status |
|---|---|---|---|

## 2. Page and dialog inventory

| PAGE | Name | Type (page / dialog) | Surface | REQ and US | Actor | Entry | Exit | Status context | Editability |
|---|---|---|---|---|---|---|---|---|---|

## 3. Page specifications

### PAGE-001 Page name

- Business scenario:
- Supporting REQ and US:
- Primary actor:
- Layout regions:
- Entry and exit:
- Data scope:

#### 3.1 Type variant matrix

Write "no variants" when there are none.

| Variant | Fields shown | Fields hidden | Rule differences | Source |
|---|---|---|---|---|

#### 3.2 Fields

Retained after: this page only / this session / after submit / display only.

| Field ID | Field | Control | Data type | Data source | Required | Default | Validation | Editable when | Permission | Retained after | Applies to | REQ | Evidence (SRC) | Status (confirmed / to confirm / to verify) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|

#### 3.3 Options, auto-generated fields, cross-field rules

| Field ID | Option value | Display text | Condition | Source |
|---|---|---|---|---|

| Auto-generated field | Generation rule | Source |
|---|---|---|

| Rule | Fields involved | Condition and result | Source |
|---|---|---|---|

#### 3.4 Filters, table, and operations

For lists, specify columns and formatting, filters and reset, sort, pagination, selection scope and batch eligibility where applicable.

| Action | Visible by role and state | Disabled when | Confirmation or input | Submission checks | Success, next state and destination | Failure and recovery | Repeat-click and audit |
|---|---|---|---|---|---|---|---|

#### 3.5 States and exceptions

List applicable states and their evidence. Label proposed states with ASM IDs and raise an OQ for any assumption that would change a business rule.

| State | What is shown | Source (evidence or ASM) |
|---|---|---|
| Normal | | |
| Empty | | |
| Loading | | |
| Error | | |
| Permission denied | | |
| Stale or conflict | | |
| Partial result or retry, when applicable | | |

#### 3.6 Acceptance criteria

Use one stable AC ID per observable criterion. Mark `visual` for criteria an image can demonstrate and `runtime` for behavior requiring execution. Split criteria that need both kinds of evidence. Confirm the covered behaviors and relevant failure paths before marking the specification ready.

| AC | REQ | Verification (visual / runtime) | Observable criterion | Fields or source |
|---|---|---|---|---|
| AC-001 | | | | |

## 4. Surface correspondence

Fill in when the same function appears on several surfaces.

| Function | Web admin | Dashboard | App | Differences |
|---|---|---|---|---|

## 5. Aliases

Keep the authoritative name.

| Authoritative name | Alias | Where it appears | Authoritative source |
|---|---|---|---|

## 6. Traceability matrix

Maintain the mapping here from stage 5. Keep the AC tables above as the inventory of criteria. Record confirmed deferred or out-of-scope requirements in the requirement baseline.

| REQ | US | ROLE | STATE / ACT | FLOW | PAGE | Prototype element | AC | Result | Evidence |
|---|---|---|---|---|---|---|---|---|---|
