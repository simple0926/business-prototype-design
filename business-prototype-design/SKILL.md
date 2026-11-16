---
name: business-prototype-design
description: Orchestrate an end-to-end business-software prototype from evidence through requirements, modeling, flows, page specification, user-selected interactive or static prototype, optional offline HTML, and acceptance. Reuse valid stage artifacts, start at the earliest unmet gate, and work without requiring any stage skill to be installed. Not for production architecture, database design, delivery planning, or ordinary production coding.
---

# Business Prototype Design Orchestrator

Coordinate the complete workflow while keeping a confirmed business baseline, a selected visual standard, and traceable acceptance criteria. This package is fully functional on its own.

## Route from the earliest unmet gate

Read [references/stage-map.md](references/stage-map.md) and [references/process-and-gates.md](references/process-and-gates.md). Inspect supplied artifacts, validate their status against [references/handoff-contract.md](references/handoff-contract.md), and begin at the earliest gate that is not demonstrably ready.

- Reuse confirmed artifacts; do not replay a stage for ceremony.
- Use a matching stage skill when helpful. Apply this orchestrator’s stage 6–8 choices and gates when the stage skill assumes a different output.
- When it is unavailable, use this package's local references.
- Do not mechanically copy every future stage-skill rule into this orchestrator. Adopt only independently validated rules that also pass an end-to-end regression.

## Global control

Show a compact eight-stage progress board after inspection. Use `✓`, `▶`, `⏸`, `○`, or `—`. Update it only when the starting stage is chosen, a gate passes, work blocks, verification begins, or the workflow completes.

Maintain throughout the workflow:

- source precedence and stable IDs;
- confirmed scope and decisions;
- story, requirement, role, state, flow, page, prototype, and acceptance mappings;
- separate business and visual sources of truth;
- explicit deferred and out-of-scope items.

Ask one highest-impact question only when alternatives change scope, identity, permission, state semantics, page inventory, required input, system boundary, prototype type, design standard, delivery format, or acceptance. Reuse selections already made by the user.

## Stage sequence

1. evidence inventory;
2. requirements and scope;
3. roles, permissions, states, and operations;
4. business flows;
5. page-level specification;
6. build the prototype type and visual standard selected by the user;
7. prepare the delivery format selected by the user;
8. business, functional, visual, and delivery review.

The stage map identifies the optional stage package and local fallback reference for each stage. Reuse a stage result when its exit gate is already satisfied. For stages 6 and 7, read [references/prototype-and-delivery.md](references/prototype-and-delivery.md).

## Scope boundary

Keep production technology selection, physical database schema, system architecture, development sequencing, and delivery milestones outside this skill. Record only functional data, behavior, and interaction constraints needed for an unambiguous prototype.

## Minimum artifact set

Consolidate related work instead of creating one document per stage unless separate ownership or review justifies a split:

1. `requirements-analysis.md` for evidence, scope, stories, requirements, decisions, roles, states, operations, and flows;
2. `prototype-spec.md` for page and dialog rules and traceability;
3. the selected prototype and evidence of its agreed coverage;
4. the selected delivery artifact, verified offline HTML or prototype images;
5. `acceptance-report.md` and `design-qa.md` when visual comparison is required.

Reuse equivalent project artifacts. Adapt [delivery templates](assets/delivery-templates) in the project and keep their handoff fields. User story cards are optional.

## Completion gate

Read [references/acceptance-and-handoff.md](references/acceptance-and-handoff.md). Verify the agreed baseline from stages 4–7 with evidence for every applicable criterion and the selected delivery format. Report the exact blocker and affected scope when a required check cannot be completed.
