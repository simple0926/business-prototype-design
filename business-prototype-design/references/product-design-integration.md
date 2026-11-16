# Product Design Integration

Use for visual standard selection and fidelity checks for interactive or static prototypes. Route to Product Design when available.

## Ownership boundary

This skill owns:

- business evidence and requirement confirmation;
- actors, permissions, states, actions, and flows;
- page-level functional specification;
- embedded developer documentation;
- traceability, delivery in the selected format, and business acceptance.

Product Design owns:

- minimum visual brief and intended user outcome;
- visual target selection or ideation;
- faithful frontend implementation from the selected target;
- rendered visual comparison and design QA;
- sharing only when the user explicitly asks for it.

Do not copy Product Design's focused skills into this skill. Load the current available Product Design index and follow its router because plugin behavior may evolve.

## Routing

1. If the request is a UX critique, use Product Design audit before implementing changes.
2. If a screenshot, Figma frame, mockup, source image, live URL, or existing design system is selected, use it as visual truth and route to the appropriate focused implementation skill.
3. If no visual standard has been selected, propose suitable options and describe the tradeoffs. Have the user select the standard before producing the prototype.
4. Compare the rendered interactive view or static image with the selected visual reference. Use Product Design QA when available.
5. Use Product Design sharing only after explicit user authorization to publish or deploy.

## Precedence rules

- Confirmed business requirements control behavior, permissions, data, and state transitions.
- The selected visual target controls layout, hierarchy, density, spacing, color, typography, and visible component anatomy.
- Existing product tokens and components take precedence over inventing a new design system when editing an existing app.
- When visual content contradicts confirmed business behavior, preserve the business behavior and report the visual mismatch.

## Visual target gate

Reuse an already approved visual standard or reference. Existing screenshots from the business system may satisfy this gate even when they cover only representative pages; document how the design language extends to new pages.

## Design QA gate

Compare the same viewport, route, content, theme, and interaction state. Evaluate at least:

- typography and wrapping;
- spacing, density, proportions, radii, and elevation;
- colors and semantic tokens;
- image and icon fidelity;
- app-specific copy and visible data;
- core interaction states and responsive behavior.

Fix all actionable P0, P1, and P2 findings, recapture, and compare again. Keep the latest `design-qa.md` in the project. If comparable evidence is unavailable, mark QA blocked instead of claiming a visual pass.

## Fallback

If Product Design is unavailable, apply the same selection and comparison against the approved standard with available tools. Record the comparison evidence and any verification limits.
