# Design QA

Use when a selected visual standard must be checked. Align the reference and the rendered prototype or image by page, viewport, content, theme and state.

## 1. Comparison baseline

- Source visual:
- Implementation route and state:
- Viewport:
- Theme:
- Comparable evidence available: yes / no

## 2. Findings

Use the finding priorities of the applicable design workflow. Record decision IDs for user-approved deviations and open an OQ when a finding may change a business rule.

| QA | Priority | Area | Source expectation | Observed implementation | Round | Resolution (fixed / deviation kept / pending) | Evidence | OQ |
|---|---|---|---|---|---|---|---|---|

## 3. Recheck

| QA | Recheck evidence | Result |
|---|---|---|

## 4. Checked items

Overflow, truncation, density, spacing, focus, contrast, persistent controls.

| Item | Result | Notes |
|---|---|---|

## 5. Result

- Remaining deviations (S1, S2):
- Blocker when comparison is unavailable:
- Final result: blocked

Set the result to one of `passed`, `failed`, or `blocked`. Use `blocked` when the selected standard cannot be checked against comparable output.
