# Acceptance And Handoff

Use at stage 8. Review the user-confirmed baseline from stages 4–7 and record the artifact version or DEC IDs that identify each input.

| Stage | Confirmed reference | Acceptance focus |
|---|---|---|
| 4. Flows | Main flow, exceptions, conditions, state transitions and ownership | Coverage of confirmed paths, results and handoffs |
| 5. Specification | Inventory, fields, permissions, rules, states and ACs | One evidence-backed result per confirmed requirement and criterion |
| 6. Construction | Prototype type, selected design standard, agreed scope and approved changes | Visual fidelity and, for interactive prototypes, observed runtime behavior |
| 7. Delivery | Chosen format and scope of deliverables | Verification of the actual offline HTML or exported images |

Use the latest confirmed decisions. Treat a discrepancy as a finding until the user confirms a change. Trace a critical flow or exception from the stage 4 baseline through the stage 5 AC, stage 6 evidence, and stage 7 deliverable.

## Evidence and result rules

Use `passed`, `failed`, `blocked`, `deferred`, or `N/A` in the acceptance table. These values describe acceptance outcomes. Use the coverage vocabulary in [requirements-guide.md](requirements-guide.md) in the requirements baseline.

- `passed` records an observable artifact or check. Record a file or capture for visual criteria. For runtime criteria, record a reproducible executed test or journey, including its observed result.
- `failed` records an observed mismatch. `blocked` gives the missing evidence, affected surface and unblock condition.
- `deferred` cites the confirmed DEC for the deferral. Use `N/A` with a reason and the applicable DEC for runtime criteria outside the agreed static scope or for recorded exclusions.
- Use a row per REQ/AC pair from the specification. A requirement deferred or excluded before specification can have a single row with `—` in AC and its decision in Notes. Give non-UI requirements an observable runtime criterion when they are in scope.
- An open blocking OQ affecting the confirmed scope blocks completion. Record assumptions, approved deviations, deferrals and open questions with their IDs.

## Four layer conclusions

- **Business.** Trace confirmed actors, scope, permissions, flow, state and action rules. For a static prototype, review the agreed screen and state representations of those rules.
- **Functional.** For interactive prototypes, verify the primary journey and relevant invalid, stale and permission-denied actions. Images exported from interactive prototypes use the existing executed evidence for functional acceptance. If the user chose static images as the prototype, runtime acceptance is `N/A` for the agreed scope.
- **Visual.** Compare the deliverable and selected visual standard at matching page, viewport, content, theme and state. A missing comparison for a selected standard is `blocked`. With an explicitly agreed absence of a benchmark on a reused baseline, record `N/A` and cite the decision. Keep approved deviations traceable.
- **Delivery.** For offline HTML, require the actual standalone file, dependency scan and offline runtime check. A static scan alone is `blocked`. For images, inspect the exported files for agreed coverage, legibility and correct state. Offline verification is `N/A` for image delivery.

## Report and consistency check

Use [the acceptance report template](../assets/delivery-templates/acceptance-report.md). Record the report's completeness separately from product acceptance. The report can be ready with a failed or blocked product outcome when the coverage and evidence are documented. State `Completed` only when all applicable criteria and delivery checks pass or have an explicit approved deferral, and no in-scope issue blocks acceptance. Otherwise state `Not complete` and name the gate, scope and unblock condition.

Run the report consistency check on filled artifacts:

```bash
python3 scripts/validate-traceability.py \
  --requirements requirements-analysis.md \
  --spec prototype-spec.md \
  --acceptance acceptance-report.md \
  --design-qa design-qa.md
```

Use `--no-visual-target` in place of `--design-qa` only for a confirmed absence of a visual benchmark. The script checks rows, required evidence references, and selected delivery conclusions. Verify linked evidence and runtime behavior directly.

## Handoff

Lead with the selected deliverable or preview, then the acceptance result, important confirmed rules, and evidence references. Include the maintained editable source when applicable. Report deviations, deferrals and unverified surfaces with the conditions for resolving them. Publish or share externally only when authorized.
