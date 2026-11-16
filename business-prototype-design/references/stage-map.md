# Stage Map

The orchestrator may use an installed stage package, but every stage has a local fallback.

| Stage | Optional stage package | Local fallback | Gate evidence |
|---|---|---|---|
| Evidence | `business-prototype-evidence` | `requirements-guide.md` source handling | sources, authority, conflicts, and visual/business truth identified |
| Requirements | `business-prototype-requirements` | `requirements-guide.md` | stories and atomic requirements scoped; no silent blocking ambiguity |
| Modeling | `business-prototype-modeling` | `role-state-and-flow.md` | role, permission, status, action, and ownership semantics confirmed |
| Flows | `business-prototype-flows` | `role-state-and-flow.md` | main and exception flows agree with the transition model |
| Specification | `business-prototype-specification` | `page-specification.md` | pages can be built without inventing business rules |
| Build | `business-prototype-build` | `prototype-and-delivery.md` plus `product-design-integration.md` | chosen prototype type satisfies the confirmed flows, page specifications, and visual standard |
| Packaging | `business-prototype-packaging` | `prototype-and-delivery.md` and, for offline HTML, `standalone-html-contract.md` | agreed deliverable is verified in the selected format |
| Review | `business-prototype-review` | `acceptance-and-handoff.md` | applicable checks trace to confirmed stages 4–7 and have reproducible evidence |

If a stage-package artifact uses the handoff contract and is `ready`, merge or reference it in the orchestrator's minimum artifact set without renumbering stable IDs.

For static prototype construction and image delivery, use the local reference. Apply the selected prototype and delivery scope when reusing a stage skill result.
