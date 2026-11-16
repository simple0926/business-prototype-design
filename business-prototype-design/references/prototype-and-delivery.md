# Prototype Construction And Delivery

Use for stages 6 and 7. Carry forward decisions already made in the user's request or confirmed project artifacts. Capture choices, agreed coverage, and any changes with DEC IDs in the existing project records.

## Stage 6 — Construct the chosen prototype

Use the confirmed flow model from stage 4 and page specification from stage 5. Before producing the prototype, establish which type the user wants and which design standard to follow. Offer suitable design options with tradeoffs when the standard is open. The user selects the type and the standard. Reuse an existing design system or reference when the user selected it. See [product-design-integration.md](product-design-integration.md).

Implement the confirmed page inventory, state and permission rules, fields, validation, layout, and feedback within the chosen scope. Confirm changes to any of these rules before using them as the baseline. Keep provisional examples and mock data identifiable as such.

| User's choice | Required output | Evidence before handoff |
|---|---|---|
| Interactive prototype | Runnable source or maintained prototype, mapped to pages and criteria | Build or launch record, core journey and relevant exception checks, renders compared with the selected design standard |
| Static prototype images | Images covering the agreed pages, dialogs and key states | Image-to-page/state inventory and comparisons with the selected design standard. Confirm which execution-only criteria are outside the chosen scope and retain them in the acceptance mapping. |

If the stage 7 format is already specified, use it to plan the work. For example, a request for offline interaction calls for an interactive prototype. When a stated format and prototype choice conflict, resolve the choice before building.

## Stage 7 — Prepare the chosen delivery

Ask which delivery the user wants when it is still open. Record the selected format, covered pages and states, and the agreed deliverables. Offer offline HTML for interactive prototypes and images from either an interactive or a static prototype. The authoring output and the delivery format serve separate decisions.

- **Offline HTML.** Use [standalone-html-contract.md](standalone-html-contract.md), build the single file, verify embedded content and dependencies, then open that exact file offline and test the agreed interactive journeys.
- **Images.** Export the agreed pages and key states. Record file, page or dialog ID, state, and viewport. Open the exported images to check legibility, completeness, and correspondence to the chosen design.

Hand off the stage 4 flow baseline, stage 5 specification, stage 6 prototype decision and evidence, and stage 7 delivery decision and inventory to acceptance.
