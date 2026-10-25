# Product Design Integration

Use this reference only when the task includes visual design, faithful implementation, or visual QA and the Product Design plugin is available.

## Ownership boundary

This skill owns:

- business evidence and requirement confirmation;
- actors, permissions, states, actions, and flows;
- page-level functional specification;
- embedded developer documentation;
- traceability, standalone packaging, and business acceptance.

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
3. If no visual target exists, use Product Design context and ideation. Follow its selection gate before coding.
4. After implementation, run Product Design design QA with both the source visual and rendered implementation.
5. Use Product Design sharing only after explicit user authorization to publish or deploy.

## Precedence rules

- Confirmed business requirements control behavior, permissions, data, and state transitions.
- The selected visual target controls layout, hierarchy, density, spacing, color, typography, and visible component anatomy.
- Existing product tokens and components take precedence over inventing a new design system when editing an existing app.
- When visual content contradicts confirmed business behavior, preserve the business behavior and report the visual mismatch.

## Visual target gate

Do not build a polished visual prototype from prose alone when Product Design requires a selected visual target. Existing screenshots from the business system may satisfy this gate even when they cover only representative pages; document how the design language extends to new pages.

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

If Product Design is unavailable, preserve the same business gates and use the best available UI implementation workflow. State that visual comparison is limited, capture browser evidence, and do not claim Product Design verification.
