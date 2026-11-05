# Standalone HTML Contract

Use before packaging an offline deliverable.

## Source and artifact relationship

Maintain structured source code as the editable baseline. The standalone HTML is a generated delivery artifact, not the primary file for continued manual editing.

Recommended pipeline:

```text
confirmed requirements and models
→ component-based prototype source
→ embedded requirements, diagrams, guides, and version data
→ production build
→ inline JavaScript, CSS, SVG, fonts, and images
→ standalone validation
→ browser verification of the generated file
```

## Required contents

Unless scope is narrowed, the standalone artifact contains:

- all in-scope prototype pages and dialogs;
- change summary and current baseline;
- roles and permissions;
- business flow descriptions and embedded diagrams;
- status and operation rules;
- page rules and field definitions;
- data, exceptions, and acceptance criteria;
- version history;
- realistic mock data needed for demonstrations.

Wrap each substantive embedded section in paired HTML comment markers. Marker-only comments or empty sections do not satisfy the contract:

```html
<!-- BPD:REQUIREMENTS:START -->...substantive content...<!-- BPD:REQUIREMENTS:END -->
<!-- BPD:ROLES:START -->...substantive content...<!-- BPD:ROLES:END -->
<!-- BPD:FLOWS:START -->...substantive content...<!-- BPD:FLOWS:END -->
<!-- BPD:PAGE_GUIDES:START -->...substantive content...<!-- BPD:PAGE_GUIDES:END -->
<!-- BPD:VERSION:START -->...substantive content...<!-- BPD:VERSION:END -->
```

If the user explicitly narrows the standalone deliverable and one or more sections are not applicable, record that scope decision in the checkpoint and acceptance report. Only then use `--skip-contract-markers` and add explicit `--require` values for the remaining contract.

## Offline dependency rules

- No external JavaScript or stylesheet dependency.
- No local sibling-file dependency for required images, fonts, diagrams, or data.
- SVG flowcharts are inline markup or encoded data.
- Required images and fonts are data URLs or otherwise embedded into the bundle.
- Core interactions do not require a development server, API, login, or network connection.
- Ordinary hyperlinks may remain when informational, but must not be required for prototype operation.
- Static `blob:` URLs are not portable delivery dependencies. Generate blobs at runtime from embedded data or use data URLs.
- Dynamic imports, workers, service workers, manifests, preload targets, and fetched local files must be bundled or eliminated from the required journey.
- Static ES imports, `export ... from`, and CSS `@import` must also be bundled or eliminated.
- Block/line comments and CSS identifier escapes do not bypass the rule. The generic validator permits only one data-URL candidate in `srcset`; use separately embedded `<picture>` sources when multiple offline variants are required.
- Every asset resolved by the generic builder must remain inside the real build root after symlink resolution; parent-directory and symlink escapes are rejected.

## Build strategy

For a Vite-style build, first produce optimized client assets. Then inline the generated CSS and JavaScript into the built HTML. Configure the build for a single JavaScript chunk or otherwise inline the full chunk graph. Transform CSS URLs, fonts, images, icons, media, manifests, and preload targets so the final validator finds no required external dependency.

Use `scripts/build-standalone.mjs` as a generic starting point only when the project has one generated module script, one or more generated stylesheets, and no unresolved secondary asset graph. Prefer a project-native single-file build when it is more capable.

## Validation

Run `scripts/validate-standalone-html.py` and then open the generated HTML itself in a browser. The validator checks the five paired, substantive contract sections by default. Test navigation and the primary journey from the standalone file, not only from the development server.

Check:

- nonempty inline CSS and JavaScript;
- no external script, stylesheet, image, media, `srcset` candidate, or CSS URL dependency;
- no relative CSS URL, static blob URL, dynamic import, worker, service worker, or required fetch dependency;
- required document sections and diagrams are present;
- browser console has no blocking errors;
- routes, back actions, dialogs, and fixed controls still work;
- layout remains usable at the target viewport.
