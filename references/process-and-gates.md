# Process And Gates

Use this reference to select a mode, decide a gate, persist workflow state, or resume interrupted work.

## Canonical phase IDs

The only phase sequence is:

1. `P1_EVIDENCE`
2. `P2_REQUIREMENTS`
3. `P3_BUSINESS_MODEL`
4. `P4_FLOW`
5. `P5_PAGE_SPEC`
6. `P6_BUILD`
7. `P7_PACKAGE`
8. `P8_HANDOFF`

Synchronization is a cross-phase invariant. Do not create a ninth “sync later” phase.

## Mode selection

### Full

Use when requirements are fragmented, conflicting, or not approved. Expected path starts at `P1_EVIDENCE` and normally reaches all eight gates.

### Fast

Use when the user provides a detailed approved baseline and explicitly asks to build. Audit the baseline against actors, states, operations, pages, validation, exception paths, and visual direction. Mark satisfied earlier gates `reused`; start at the earliest gap. Do not request a blanket approval when the existing instruction is already valid gate evidence.

### Incremental

Use when a maintained source project or runnable prototype exists. Inspect current behavior before editing. Convert feedback into atomic changes, map impact, mark affected gates `invalidated`, preserve unaffected work, and resume at the earliest invalidated gate.

## Gate decision

Every phase entry in `prototype-workflow-state.json` uses one status:

| Status | Meaning | Required evidence |
|---|---|---|
| `not_started` | No work or reusable result yet | None |
| `in_progress` | Work is active and unblocked | Current artifact paths when available |
| `blocked` | A user decision or external prerequisite prevents safe progress | Phase-bound Decision IDs, affected phases, next question |
| `confirmed` | Exit criteria were met in this workflow | Artifact paths, evidence IDs, confirmer, timestamp |
| `reused` | Existing approved work still meets the gate | Artifact paths, approval/source evidence, original confirmation, revalidation actor and timestamp |
| `invalidated` | Later evidence or a change made the result unsafe to reuse | Invalidating decision/change ID and affected artifacts |
| `not_applicable` | Phase output is genuinely outside the agreed scope | Reason and scope decision |

The checkpoint must encode those requirements directly:

- every `confirmed` or `reused` phase records the workflow `baseline_version`;
- every `reused` phase has `revalidated_by` and `revalidated_at`, separate from the original confirmation;
- every `blocked` phase has nonempty `decision_ids`; every referenced open Decision lists the phase in `affected_phases` and contains the current question and recommendation;
- every `not_applicable` phase has `reason` and a confirmed `scope_decision_id` that lists the phase;
- `current_phase` is the earliest phase whose status is not `confirmed`, `reused`, or `not_applicable`; when all phases are terminal, it is `P8_HANDOFF`.

### When to ask the user

Ask when alternatives change data identity, role or scope, status meaning, page inventory, required input, validation, external effect, selected visual target, or acceptance result. Present the evidence, mutually exclusive choices when useful, implementation impact, and one recommendation. Ask only the highest-impact unresolved question; keep the remaining queue in the decision record.

Do not ask when an existing approved artifact unambiguously satisfies the exit gate and remains valid.

### Invalidation

For every new decision or change:

1. identify affected requirements, actors, permissions, states, transitions, flows, pages, tests, guides, and artifacts;
2. mark their gates `invalidated` and record `invalidated_by`;
3. keep unrelated gates unchanged;
4. resume from the earliest invalidated phase;
5. re-run targeted checks and the broad regression set required by the changed risk.

## Deliverable matrix

`new` means create unless the project has an equivalent artifact. `reuse` means validate and reference an existing artifact. `conditional` depends on scope or visual evidence.

| Artifact | Full | Fast | Incremental |
|---|---|---|---|
| Workflow checkpoint | new | new | new or update |
| Source-unit evidence manifest | new for image-bearing sources | reuse and revalidate | update affected sources/units |
| Evidence and requirement baseline | new | reuse | update affected items |
| Role, state, action, and flow model | new | reuse | update if invalidated |
| Reviewed journey coverage | new for high-risk transitions | reuse or complete gaps | update affected journeys |
| Page specification | new | reuse or complete gaps | update affected pages |
| Runnable maintained source | new | new | update |
| Embedded requirements and page guides | new | new or update | update affected content |
| Design QA | conditional | conditional | conditional for changed views |
| Acceptance report | new | new | update with regression evidence |
| Passed-evidence register | new for final acceptance | new for final acceptance | update changed evidence |
| Offline standalone HTML | new unless narrowed | new unless narrowed | rebuild unless explicitly excluded |

## Checkpoint lifecycle

Copy the workflow-state template at the start of a multi-phase task. Update it when:

- the mode and starting phase are selected;
- a gate becomes confirmed, reused, blocked, invalidated, or not applicable;
- the baseline version changes;
- verification begins;
- handoff completes.

The progress board must be derived from the checkpoint. Do not keep a contradictory state only in conversation.

For PDF, image-set, slide, or screenshot-heavy evidence, also copy `evidence-manifest.json`. A source with `total_units: N` must contain exactly one inspected record for each unit `1..N`. When `requires_visual_review` is true, every unit must include `render` or `visual` in `inspection_methods`. An in-scope unit requires evidence IDs; an excluded unit requires a reason.

For multi-role, approval, validation-heavy, or exception-heavy workflows, also copy `journey-coverage.json`. Draft it from confirmed P3/P4 transitions and update it whenever a relevant requirement, state, action, owner, or expected result changes. It becomes final only when every in-scope journey resolves to matching passed test/browser claims.

Run:

```bash
python3 scripts/validate-evidence-manifest.py evidence-manifest.json
python3 scripts/validate-workflow-state.py prototype-workflow-state.json
python3 scripts/validate-journey-coverage.py --journeys journey-coverage.json --evidence-register evidence-register.json --baseline-version <baseline-version>
```

## Resuming interrupted work

Prefer project artifacts over chat memory:

For a project created before the current templates, first run `python3 scripts/audit-legacy-project.py <project>`. Use the report to map reusable content and migration gaps; it is not a final acceptance result and does not modify the project.

1. read and validate `prototype-workflow-state.json`;
2. confirm that referenced artifacts still exist;
3. read the latest decisions, baseline, specification, source, tests, and acceptance report relevant to the current or invalidated phase;
4. compare modification/version evidence and surface conflicts;
5. set `next_safe_action` and continue from the earliest unmet or invalidated gate.

If the checkpoint conflicts with a later confirmed project artifact, report the conflict and use the user-confirmed latest baseline. Do not silently guess.
