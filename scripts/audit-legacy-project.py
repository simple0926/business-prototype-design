#!/usr/bin/env python3

import argparse
import json
import re
import sys
from pathlib import Path


SKIP_DIRECTORIES = {".git", "node_modules", "dist", "build", ".cache"}
CONTRACT_MARKERS = {
    "BPD:REQUIREMENTS",
    "BPD:ROLES",
    "BPD:FLOWS",
    "BPD:PAGE_GUIDES",
    "BPD:VERSION",
}
ID_PATTERN = re.compile(r"(?:REQ(?:-[A-Z]+)?|R)-\d{3,}")


def files_under(root):
    for path in root.rglob("*"):
        if not path.is_file() or any(part in SKIP_DIRECTORIES for part in path.relative_to(root).parts):
            continue
        yield path


def markdown_rows(text):
    rows = []
    for line in text.splitlines():
        if not line.lstrip().startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if cells and ID_PATTERN.fullmatch(cells[0]):
            rows.append(cells)
    return rows


def finding(name, status, paths, detail, action):
    return {
        "artifact": name,
        "status": status,
        "paths": sorted(paths),
        "detail": detail,
        "action": action,
    }


def analyze(root):
    all_files = list(files_under(root))
    markdown_files = [path for path in all_files if path.suffix.lower() == ".md"]
    html_files = [path for path in all_files if path.suffix.lower() in {".html", ".htm"}]
    relative = lambda path: str(path.relative_to(root))

    source_paths = []
    canonical_requirements = []
    legacy_requirement_paths = []
    canonical_acceptance = []
    legacy_acceptance = []
    design_qa_paths = []

    for path in markdown_files:
        text = path.read_text(encoding="utf-8", errors="replace")
        lower_name = path.name.lower()
        if re.search(r"\|\s*(?:source id|来源\s*id)\s*\|", text, re.I):
            source_paths.append(relative(path))
        rows = markdown_rows(text)
        if any(len(row) == 8 and row[0].startswith("REQ-") for row in rows):
            canonical_requirements.append(relative(path))
        if re.search(r"^#{1,6}\s+(?:REQ(?:-[A-Z]+)?|R)-\d{3,}\b", text, re.M):
            legacy_requirement_paths.append(relative(path))
        if "acceptance" in lower_name or "验收" in path.name:
            if any(len(row) == 6 for row in rows):
                canonical_acceptance.append(relative(path))
            if any(len(row) in {3, 4, 5} for row in rows):
                legacy_acceptance.append(relative(path))
        if "design-qa" in lower_name or "design_qa_result" in text.lower() or "final result:" in text.lower():
            design_qa_paths.append(relative(path))

    checkpoint = [relative(path) for path in all_files if path.name == "prototype-workflow-state.json"]
    manifests = [relative(path) for path in all_files if path.name == "evidence-manifest.json"]
    registers = [relative(path) for path in all_files if path.name == "evidence-register.json"]
    journeys = [relative(path) for path in all_files if path.name == "journey-coverage.json"]
    test_paths = [
        relative(path)
        for path in all_files
        if "tests" in path.relative_to(root).parts
        and path.suffix.lower() in {".py", ".js", ".jsx", ".mjs", ".ts", ".tsx"}
    ]

    standalone_with_markers = []
    standalone_without_markers = []
    for path in html_files:
        text = path.read_text(encoding="utf-8", errors="replace")
        if CONTRACT_MARKERS.issubset(set(marker for marker in CONTRACT_MARKERS if marker in text)):
            standalone_with_markers.append(relative(path))
        elif "<script" in text and "<style" in text:
            standalone_without_markers.append(relative(path))

    findings = [
        finding(
            "source register",
            "reusable" if source_paths else "missing",
            source_paths,
            "A source register was found." if source_paths else "No Source ID table was found.",
            "Map existing sources to stable Source IDs." if not source_paths else "Reuse after authority and scope review.",
        ),
        finding(
            "requirements",
            "canonical" if canonical_requirements else "needs_migration" if legacy_requirement_paths else "missing",
            canonical_requirements or legacy_requirement_paths,
            "An eight-column requirement matrix was found."
            if canonical_requirements
            else "Heading-based legacy requirements were found."
            if legacy_requirement_paths
            else "No canonical or heading-based requirement IDs were found.",
            "Reuse the canonical matrix."
            if canonical_requirements
            else "Map legacy headings into the eight-column requirement matrix."
            if legacy_requirement_paths
            else "Create the requirement baseline before validation.",
        ),
        finding(
            "acceptance report",
            "canonical" if canonical_acceptance else "needs_migration" if legacy_acceptance else "missing",
            canonical_acceptance or legacy_acceptance,
            "A six-column acceptance table was found."
            if canonical_acceptance
            else "A legacy acceptance table with fewer than six columns was found."
            if legacy_acceptance
            else "No acceptance table was found.",
            "Reuse and refresh evidence."
            if canonical_acceptance
            else "Map legacy rows to requirement IDs and separate implementation from test/browser evidence."
            if legacy_acceptance
            else "Create an acceptance report after requirements are mapped.",
        ),
        finding("workflow checkpoint", "canonical" if checkpoint else "missing", checkpoint, "Checkpoint found." if checkpoint else "No workflow checkpoint found.", "Validate it." if checkpoint else "Create a public 0.2 checkpoint and mark reusable gates only after review."),
        finding("evidence manifest", "canonical" if manifests else "conditional", manifests, "Evidence manifest found." if manifests else "No evidence manifest found.", "Validate it." if manifests else "Create one only for in-scope image-heavy sources."),
        finding("evidence register", "canonical" if registers else "missing", registers, "Evidence register found." if registers else "No final evidence register found.", "Validate claims and baseline." if registers else "Register refreshed implementation and test/browser evidence before final passed."),
        finding("journey coverage", "canonical" if journeys else "conditional", journeys, "Journey checklist found." if journeys else "No journey checklist found.", "Validate it." if journeys else "Derive it when confirmed interactions, validations, or state transitions are high risk."),
        finding("design QA", "reusable" if design_qa_paths else "conditional", design_qa_paths, "Design QA material found." if design_qa_paths else "No Design QA artifact found.", "Revalidate against the selected visual baseline." if design_qa_paths else "Create only when visual comparison is in scope."),
        finding("automated tests", "reusable" if test_paths else "missing", test_paths, f"Found {len(test_paths)} test source files.", "Map individual assertions to requirement claims." if test_paths else "Add tests for in-scope behavior and journeys."),
        finding(
            "standalone HTML",
            "canonical" if standalone_with_markers else "needs_migration" if standalone_without_markers else "missing",
            standalone_with_markers or standalone_without_markers,
            "Standalone HTML with all BPD markers found."
            if standalone_with_markers
            else "Standalone-like HTML exists but BPD markers are incomplete."
            if standalone_without_markers
            else "No standalone-like HTML found.",
            "Validate offline behavior."
            if standalone_with_markers
            else "Add markers during the next package build; do not treat marker absence as a business defect."
            if standalone_without_markers
            else "Build only when standalone delivery is in scope.",
        ),
    ]

    blocking = {"missing", "needs_migration"}
    classification = "canonical_ready" if not any(item["status"] in blocking for item in findings) else "migration_needed"
    return {
        "project": str(root),
        "classification": classification,
        "read_only": True,
        "findings": findings,
    }


def render_markdown(report):
    lines = [
        "# Legacy project readiness audit",
        "",
        f"- Project: `{report['project']}`",
        f"- Classification: `{report['classification']}`",
        "- Mode: read-only; no project files were changed.",
        "",
        "| Artifact | Status | Paths | Next action |",
        "|---|---|---|---|",
    ]
    for item in report["findings"]:
        paths = "<br>".join(f"`{path}`" for path in item["paths"]) or "-"
        lines.append(f"| {item['artifact']} | `{item['status']}` | {paths} | {item['action']} |")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Read-only readiness audit for projects created before the public 0.2 workflow.")
    parser.add_argument("project", type=Path)
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    args = parser.parse_args()

    if not args.project.is_dir():
        print(f"ERROR: project directory not found: {args.project}", file=sys.stderr)
        return 2

    report = analyze(args.project.resolve())
    if args.format == "json":
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(render_markdown(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
