#!/usr/bin/env python3

import argparse
import collections
from datetime import datetime
import json
import re
import sys
from pathlib import Path

from evidence_contract import validate_evidence_register


FINAL_RESULTS = {"passed", "deferred", "out_of_scope", "not_applicable"}
PENDING_RESULTS = {"pending", "blocked", "partial"}
PLACEHOLDERS = {
    "-",
    "todo",
    "tbd",
    "pending",
    "not-run",
    "not run",
    "not-implemented",
    "not implemented",
    "n/a",
    "na",
    "待确认",
    "待回答",
    "未执行",
    "未实现",
}
EVIDENCE_PATTERN = re.compile(r"EVD-\d{3,}")
SOURCE_ID_PATTERN = re.compile(r"[A-Z][A-Z0-9_-]*-\d{3,}")
EVIDENCE_KINDS = {"implementation", "test", "browser"}
CLAIM_TYPES = {"presence", "interaction", "validation", "state_transition", "delivery"}
COVERAGE_VALUES = {
    "satisfied",
    "partial",
    "missing",
    "pending_confirmation",
    "deferred",
    "out_of_scope",
}


def read_required(path):
    if not path.is_file():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8")


def read_json_required(path):
    if not path.is_file():
        raise FileNotFoundError(path)
    return json.loads(path.read_text(encoding="utf-8"))


def table_rows(text, id_pattern):
    pattern = re.compile(f"^(?:{id_pattern})$")
    rows = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        if not line.lstrip().startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if cells and pattern.fullmatch(cells[0]):
            rows.append((line_number, cells))
    return rows


def duplicate_ids(rows):
    counts = collections.Counter(cells[0] for _, cells in rows)
    return sorted(identifier for identifier, count in counts.items() if count > 1)


def is_placeholder(value):
    return not value or value.strip().lower() in PLACEHOLDERS


def normalized_value(value):
    return value.strip().lower().replace("-", "_").replace(" ", "_")


def source_register_ids(text):
    identifiers = set()
    in_source_register = False
    for line in text.splitlines():
        if not line.lstrip().startswith("|"):
            if in_source_register:
                in_source_register = False
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        normalized_header = re.sub(r"[\s_-]+", "", cells[0].lower()) if cells else ""
        if normalized_header in {"sourceid", "来源id", "来源编号"}:
            in_source_register = True
            continue
        if not in_source_register or not cells:
            continue
        source_id = cells[0]
        if SOURCE_ID_PATTERN.fullmatch(source_id):
            identifiers.add(source_id)
    return identifiers


def is_iso_8601_timestamp(value):
    if not isinstance(value, str) or "T" not in value:
        return False
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return False
    return parsed.tzinfo is not None


def load_evidence_registry(path, expected_baseline, errors, forbidden_paths=()):
    if path is None:
        errors.append("passed acceptance rows require --evidence-register")
        return {}
    by_id, registry_errors = validate_evidence_register(
        path,
        expected_baseline,
        forbidden_paths=forbidden_paths,
    )
    errors.extend(registry_errors)
    return by_id


def referenced_ids(text, pattern):
    return set(re.findall(pattern, text))


def structured_result(text, marker_name, label):
    markers = re.findall(
        rf"<!--\s*{re.escape(marker_name)}\s*:\s*(passed|blocked|partial|pending)\s*-->",
        text,
        re.I,
    )
    summaries = re.findall(rf"{re.escape(label)}\s*:\s*(passed|blocked|partial|pending)", text, re.I)
    values = [value.lower() for value in markers + summaries]
    return values


def baseline_values(text):
    return [value.strip() for value in re.findall(r"baseline version\s*:\s*([^\n|]+)", text, re.I)]


def main():
    parser = argparse.ArgumentParser(description="Validate requirement coverage and acceptance evidence.")
    parser.add_argument("--requirements", required=True, type=Path)
    parser.add_argument("--acceptance", required=True, type=Path)
    parser.add_argument("--evidence-register", type=Path)
    parser.add_argument("--baseline-version")
    parser.add_argument("--design-qa", type=Path)
    parser.add_argument("--prototype-spec", type=Path)
    parser.add_argument("--workflow-state", type=Path)
    parser.add_argument("--journey-coverage", type=Path)
    parser.add_argument("--forbid-evidence-path", action="append", default=[], type=Path)
    parser.add_argument("--id-pattern", default=r"REQ-\d{3,}")
    parser.add_argument("--allow-pending", action="store_true")
    args = parser.parse_args()

    try:
        requirements = read_required(args.requirements)
        acceptance = read_required(args.acceptance)
        design_qa = read_required(args.design_qa) if args.design_qa else None
    except FileNotFoundError as error:
        print(f"ERROR: file not found: {error.args[0]}", file=sys.stderr)
        return 2

    requirement_rows = table_rows(requirements, args.id_pattern)
    acceptance_rows = table_rows(acceptance, args.id_pattern)
    registered_source_ids = source_register_ids(requirements)
    requirement_ids = {cells[0] for _, cells in requirement_rows}
    acceptance_ids = {cells[0] for _, cells in acceptance_rows}
    missing = sorted(requirement_ids - acceptance_ids)
    unknown = sorted(acceptance_ids - requirement_ids)
    errors = []

    workflow_decision_ids = None
    if args.workflow_state:
        try:
            workflow_data = read_json_required(args.workflow_state)
        except (FileNotFoundError, OSError, json.JSONDecodeError) as error:
            errors.append(f"invalid workflow state: {error}")
            workflow_decision_ids = set()
        else:
            workflow_decision_ids = {
                item.get("id")
                for item in workflow_data.get("decisions", [])
                if isinstance(item, dict) and item.get("id")
            }

    journey_ids = None
    if args.journey_coverage:
        try:
            journey_data = read_json_required(args.journey_coverage)
        except (FileNotFoundError, OSError, json.JSONDecodeError) as error:
            errors.append(f"invalid journey coverage: {error}")
            journey_ids = set()
        else:
            journey_ids = {
                item.get("id")
                for item in journey_data.get("journeys", [])
                if isinstance(item, dict) and item.get("id")
            }

    registry_schema = None
    if args.evidence_register and args.evidence_register.is_file():
        try:
            registry_schema = read_json_required(args.evidence_register).get("schema_version")
        except (OSError, json.JSONDecodeError):
            pass

    if registry_schema == "0.4" and args.baseline_version:
        for label, document in (("requirements", requirements), ("acceptance", acceptance)):
            values = baseline_values(document)
            if not values:
                errors.append(f"{label} document requires Baseline version")
            elif set(values) != {args.baseline_version}:
                errors.append(f"{label} baseline version does not match requested baseline")

    acceptance_results = structured_result(acceptance, "ACCEPTANCE_RESULT", "Overall result")
    if registry_schema == "0.4" and not acceptance_results:
        errors.append("acceptance report requires structured and human-readable overall results")
    elif acceptance_results:
        if len(set(acceptance_results)) != 1:
            errors.append("acceptance report contains contradictory overall results")
        elif acceptance_results[-1] != "passed" and not args.allow_pending:
            errors.append("acceptance report overall result is not passed")

    if not requirement_rows:
        errors.append("no requirement table rows found")
    for identifier in duplicate_ids(requirement_rows):
        errors.append(f"duplicate requirement ID: {identifier}")
    for identifier in duplicate_ids(acceptance_rows):
        errors.append(f"duplicate acceptance ID: {identifier}")
    if missing:
        errors.append(f"requirements missing from acceptance: {', '.join(missing)}")
    if unknown:
        errors.append(f"acceptance IDs absent from requirements: {', '.join(unknown)}")

    requirement_coverage = {}
    for line_number, cells in requirement_rows:
        identifier = cells[0]
        if len(cells) != 8:
            errors.append(f"{identifier} line {line_number}: requirement row must have exactly 8 columns")
            continue
        required_indexes = {
            1: "requirement",
            2: "source",
            3: "coverage",
            4: "evidence or gap",
            5: "decision",
            6: "prototype mapping",
            7: "acceptance mapping",
        }
        for index, label in required_indexes.items():
            if is_placeholder(cells[index]):
                errors.append(f"{identifier} line {line_number}: empty or placeholder {label}")
        source_ids = SOURCE_ID_PATTERN.findall(cells[2])
        if not source_ids:
            errors.append(f"{identifier} line {line_number}: source requires a registered Source ID")
        for source_id in source_ids:
            if source_id not in registered_source_ids:
                errors.append(f"{identifier} line {line_number}: unknown source ID {source_id}")
        decision_ids = referenced_ids(cells[5], r"\bDEC-\d{3,}\b")
        if workflow_decision_ids is not None:
            if not decision_ids:
                errors.append(f"{identifier} line {line_number}: decision requires a Decision ID")
            for decision_id in sorted(decision_ids - workflow_decision_ids):
                errors.append(f"{identifier} line {line_number}: unknown decision ID {decision_id}")
        referenced_journeys = referenced_ids(" ".join(cells[4:]), r"\bJNY-\d{3,}\b")
        if workflow_decision_ids is not None and referenced_journeys and journey_ids is None:
            errors.append(f"{identifier} line {line_number}: journey references require journey coverage")
        elif journey_ids is not None:
            for journey_id in sorted(referenced_journeys - journey_ids):
                errors.append(f"{identifier} line {line_number}: unknown journey ID {journey_id}")
        coverage = normalized_value(cells[3])
        requirement_coverage[identifier] = coverage
        if coverage not in COVERAGE_VALUES:
            errors.append(f"{identifier} line {line_number}: unsupported coverage {cells[3]!r}")

    passed_rows = []
    for line_number, cells in acceptance_rows:
        identifier = cells[0]
        if len(cells) != 6:
            errors.append(f"{identifier} line {line_number}: acceptance row must have exactly 6 columns")
            continue
        required_indexes = {1: "confirmed rule", 2: "implementation evidence", 3: "test or browser evidence", 4: "result"}
        for index, label in required_indexes.items():
            if is_placeholder(cells[index]):
                errors.append(f"{identifier} line {line_number}: empty or placeholder {label}")
        result = cells[4].lower().replace(" ", "_")
        allowed_results = FINAL_RESULTS | (PENDING_RESULTS if args.allow_pending else set())
        if result and result not in allowed_results:
            errors.append(f"{identifier} line {line_number}: unsupported result {cells[4]!r}")
        if result in {"deferred", "out_of_scope", "not_applicable"} and is_placeholder(cells[5]):
            errors.append(f"{identifier} line {line_number}: {result} requires notes")
        if result == "passed":
            passed_rows.append((line_number, cells))
            coverage = requirement_coverage.get(identifier)
            if coverage in {"partial", "missing", "pending_confirmation"}:
                errors.append(
                    f"{identifier} line {line_number}: coverage {coverage} cannot have result passed"
                )

    prototype_spec_path = args.prototype_spec or args.requirements.resolve().parent / "prototype-spec.md"
    prototype_spec = None
    if passed_rows:
        if not prototype_spec_path.is_file():
            errors.append(f"prototype specification not found: {prototype_spec_path}")
        else:
            prototype_spec = prototype_spec_path.read_text(encoding="utf-8")
            if registry_schema == "0.4":
                values = baseline_values(prototype_spec)
                if not values or set(values) != {args.baseline_version}:
                    errors.append("prototype specification baseline version does not match requested baseline")
            known_pages = referenced_ids(prototype_spec, r"\bPAGE-\d{3,}\b")
            known_acceptance = referenced_ids(prototype_spec, r"\bACC-\d{3,}\b")
            for line_number, cells in requirement_rows:
                requirement_id = cells[0]
                if len(cells) != 8:
                    continue
                for page_id in referenced_ids(cells[6], r"\bPAGE-\d{3,}\b"):
                    if page_id not in known_pages:
                        errors.append(f"{requirement_id} line {line_number}: unknown page ID {page_id}")
                for acceptance_id in referenced_ids(cells[7], r"\bACC-\d{3,}\b"):
                    if acceptance_id not in known_acceptance:
                        errors.append(
                            f"{requirement_id} line {line_number}: unknown acceptance mapping ID {acceptance_id}"
                        )

    evidence_by_id = {}
    if passed_rows:
        if not args.baseline_version:
            errors.append("passed acceptance rows require --baseline-version")
        else:
            evidence_by_id = load_evidence_registry(
                args.evidence_register,
                args.baseline_version,
                errors,
                forbidden_paths=(
                    args.requirements,
                    args.acceptance,
                    prototype_spec_path,
                    *args.forbid_evidence_path,
                ),
            )
        for line_number, cells in passed_rows:
            identifier = cells[0]
            for index, label, allowed_kinds in (
                (2, "implementation evidence", {"implementation"}),
                (3, "test or browser evidence", {"test", "browser"}),
            ):
                evidence_ids = EVIDENCE_PATTERN.findall(cells[index])
                if not evidence_ids:
                    errors.append(f"{identifier} line {line_number}: {label} requires an evidence ID")
                    continue
                for evidence_id in evidence_ids:
                    if evidence_id not in evidence_by_id:
                        errors.append(f"{identifier} line {line_number}: unknown evidence ID {evidence_id}")
                        continue
                    evidence = evidence_by_id[evidence_id]
                    if evidence.get("kind") not in allowed_kinds:
                        expected = "implementation" if index == 2 else "test or browser"
                        errors.append(
                            f"{identifier} line {line_number}: {label} requires kind {expected}: {evidence_id}"
                        )
                    claims = evidence.get("claims")
                    if isinstance(claims, list) and not any(
                        isinstance(claim, dict) and claim.get("requirement_id") == identifier
                        for claim in claims
                    ):
                        errors.append(
                            f"{identifier} line {line_number}: {evidence_id} has no claim for this requirement"
                        )

    if not args.allow_pending:
        pending_pattern = re.compile(r"\b(?:TODO|TBD)\b|待确认|待回答", re.I)
        if pending_pattern.search(requirements):
            errors.append("requirements contain unresolved pending markers")

    if design_qa is not None:
        marker = re.findall(r"<!--\s*DESIGN_QA_RESULT\s*:\s*(passed|blocked)\s*-->", design_qa, re.I)
        fallback = re.findall(r"final result\s*:\s*(passed|blocked)", design_qa, re.I)
        matches = [value.lower() for value in marker + fallback]
        if not matches:
            errors.append("design QA has no structured final result")
        elif len(set(matches)) != 1:
            errors.append("design QA contains contradictory final results")
        elif matches[-1] != "passed":
            errors.append("design QA final result is not passed")

    print(f"requirements={len(requirement_ids)}")
    print(f"acceptance_ids={len(acceptance_ids)}")
    print(f"evidence_ids={len(evidence_by_id)}")
    print(f"design_qa={'checked' if design_qa is not None else 'not_provided'}")
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("result=passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
