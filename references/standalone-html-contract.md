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

## Offline dependency rules

- No external JavaScript or stylesheet dependency.
- No local sibling-file dependency for required images, fonts, diagrams, or data.
- SVG flowcharts are inline markup or encoded data.
- Required images and fonts are data URLs or otherwise embedded into the bundle.
- Core interactions do not require a development server, API, login, or network connection.
- Ordinary hyperlinks may remain when informational, but must not be required for prototype operation.

## Build strategy

For a Vite-style build, first produce optimized client assets. Then inline the generated CSS and JavaScript into the built HTML. Configure or transform other emitted assets so the final validator finds no required external dependency.

Use `scripts/build-standalone.mjs` as a generic starting point when the project has one generated module script and one or more generated stylesheets. Adapt the project's existing build when it is more capable.

## Validation

Run `scripts/validate-standalone-html.py` and then open the generated HTML itself in a browser. Test navigation and the primary journey from the standalone file, not only from the development server.

Check:

- nonempty inline CSS and JavaScript;
- no external script, stylesheet, image, media, or CSS URL dependency;
- required document sections and diagrams are present;
- browser console has no blocking errors;
- routes, back actions, dialogs, and fixed controls still work;
- layout remains usable at the target viewport.
