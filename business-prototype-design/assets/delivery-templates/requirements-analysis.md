---
handoff_contract: business-prototype-handoff/1.0.0
stage: requirements
artifact: requirements-analysis
status: draft
baseline_version: none
inputs: []
unresolved: []
next_stage: business-prototype-modeling
---

# Requirements Analysis

This combined artifact can hold stages 1–4. Record each stage's result and supporting section independently. The contract header describes the current handoff.

| Stage | Section or artifact | Result | Evidence or blocker |
|---|---|---|---|
| Evidence | §2 | draft | |
| Requirements | §1, §3, §4 | draft | |
| Modeling | §5, §6 | draft | |
| Flows | §7 | draft | |

## 1. Baseline and scope

- Objective:
- Business source of truth:
- Visual source of truth:
- Current approved version:

### 1.1 Scope baseline

| Item | Scope decision (included / deferred / out of scope) | Source | DEC / OQ |
|---|---|---|---|

### 1.2 Business limits

Record only limits the evidence states. Delete this section if there are none.

| Object | Limit | Value | Source | Status (confirmed / to confirm) |
|---|---|---|---|---|

### 1.3 Deployment and compliance constraints

Record only what the evidence states. No technology selection.

| Constraint | Content | Source | Effect on the prototype |
|---|---|---|---|

## 2. Source register

| SRC | Source | Type | Authority or precedence | Version or date | Relevant scope | Conflicts or access limits |
|---|---|---|---|---|---|---|
| SRC-001 | | | | | | |

## 3. User stories and priority

Use project-specific priority definitions when they exist. Otherwise: P0 breaks the primary outcome or core journey if omitted; P1 materially improves an important journey; P2 improves a detail, edge case, or lower-frequency scenario.

| US | Actor | Trigger or context | Intended action | Business outcome | Acceptance conditions | Source | Priority | Rationale and omission impact | Dependencies | Scope decision |
|---|---|---|---|---|---|---|---|---|---|---|
| US-001 | | | | | | | | | | |

## 4. Requirement coverage

Coverage values: satisfied / partial / missing / pending confirmation / deferred / out of scope. Record the actor, trigger, behavior, constraints and observable result in each atomic requirement. Link an unresolved rule to its OQ and any confirmed deferral or exclusion to its decision.

| REQ | US | Requirement | Priority | Scope decision | Source | Coverage | Evidence or gap | DEC / OQ |
|---|---|---|---|---|---|---|---|---|
| REQ-001 | | | | | | | | |

## 5. Roles and permissions

### 5.1 Roles and data scope

Record any tentative data scope as an ASM. Open a blocking OQ when the choice changes visibility or permitted actions.

| ROLE | Name | Responsibility | Data scope | Pages | Exceptions owned | Source | Status |
|---|---|---|---|---|---|---|---|

### 5.2 Permission matrix

| ROLE | STATE | ACT | Allowed (yes / no / to confirm) | Data scope | Evidence |
|---|---|---|---|---|---|

## 6. States and operations

### 6.1 States

| STATE | Canonical state | Role-facing state | Owning object | Responsible actor | Terminal or recoverable | Meaning | Source |
|---|---|---|---|---|---|---|---|

### 6.2 Operations and transitions

Give every nonterminal state a legal exit and an owner. Label background effects separately from visible state changes. This table can also serve as the text transition table for §7.

| ACT | Operation | Actor (ROLE) | From STATE | Trigger | Guard | To STATE | Next actor | Side effects | REQ / evidence |
|---|---|---|---|---|---|---|---|---|---|

### 6.3 Exception and reverse branches

Write only what the evidence states. Put the rest in open questions.

| Scenario (reject / timeout / cancel / retry) | Condition | System handling | Action after recovery | Evidence | Status |
|---|---|---|---|---|---|

## 7. Flows

### 7.1 Flow list

| FLOW | Name | Variant | ROLE involved | Nodes map to STATE | Edges map to ACT |
|---|---|---|---|---|---|

### 7.2 Main flow

### 7.3 Subflows and exceptions

For each branch, identify the relevant transition, condition, result and next responsible actor. Check the diagram against the text transition table.

### 7.4 Diagrams

Use a diagram when it clarifies the flow. For offline HTML delivery, embed diagrams as self-contained SVG or images.

## 8. Confirmed decisions

| DEC | Date | Confirmed rule | Affected artifacts | Supersedes |
|---|---|---|---|---|

## 9. Pending, deferred, and excluded items

### 9.1 Deferred and out of scope

| Item | REQ | Classification | Reason | Reassess when | DEC / OQ |
|---|---|---|---|---|---|

### 9.2 Assumptions

| ASM | Content | Impact if wrong | Who confirms |
|---|---|---|---|

### 9.3 Open questions

| OQ | Question | Blocking (yes / no) | Status (open / answered) | Affects | Owner |
|---|---|---|---|---|---|

## 10. Traceability matrix

Maintain the mapping here through stage 4. Starting in stage 5, point to the maintained matrix in `prototype-spec.md`. Identify non-UI effects explicitly.

| REQ | US | ROLE | STATE / ACT | FLOW | PAGE | Prototype element | AC | Result | Evidence |
|---|---|---|---|---|---|---|---|---|---|
