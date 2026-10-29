#!/usr/bin/env python3

import argparse
import collections
from datetime import datetime
import json
import re
import sys
from pathlib import Path


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
        if cells and cells[0].lower() == "source id":
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


def load_evidence_registry(path, expected_baseline, errors):
    if path is None:
        errors.append("passed acceptance rows require --evidence-register")
        return {}
    try:
        registry = read_json_required(path)
    except FileNotFoundError:
        errors.append(f"evidence register not found: {path}")
        return {}
    except json.JSONDecodeError as error:
        errors.append(f"invalid evidence register JSON: {error}")
        return {}

    if registry.get("schema_version") != "0.3":
        errors.append(f"unsupported evidence register schema_version: {registry.get('schema_version')!r}")
    if registry.get("baseline_version") != expected_baseline:
        errors.append("evidence register baseline_version does not match requested baseline")
    entries = registry.get("evidence")
    if not isinstance(entries, list):
        errors.append("evidence register requires an evidence list")
        return {}

    by_id = {}
    for entry in entries:
        if not isinstance(entry, dict):
            errors.append("evidence entry must be an object")
            continue
        evidence_id = entry.get("id")
        if not evidence_id or not EVIDENCE_PATTERN.fullmatch(evidence_id):
            errors.append(f"invalid evidence ID: {evidence_id!r}")
            continue
        if evidence_id in by_id:
            errors.append(f"duplicate evidence ID: {evidence_id}")
        by_id[evidence_id] = entry
        for field in ("kind", "path", "result", "baseline_version", "captured_at"):
            if not entry.get(field):
                errors.append(f"{evidence_id}: missing {field}")
        if entry.get("kind") not in EVIDENCE_KINDS:
            errors.append(f"{evidence_id}: unsupported evidence kind {entry.get('kind')!r}")
        captured_at = entry.get("captured_at")
        if captured_at and not is_iso_8601_timestamp(captured_at):
            errors.append(f"{evidence_id}: captured_at must be ISO 8601 with timezone")
        if entry.get("result") != "passed":
            errors.append(f"{evidence_id}: evidence result is not passed")
        if entry.get("baseline_version") != expected_baseline:
            errors.append(f"{evidence_id}: evidence baseline_version does not match")
        claims = entry.get("claims")
        if not isinstance(claims, list) or not claims:
            errors.append(f"{evidence_id}: evidence requires a nonempty claims list")
        else:
            for index, claim in enumerate(claims, start=1):
                prefix = f"{evidence_id} claim {index}"
                if not isinstance(claim, dict):
                    errors.append(f"{prefix}: claim must be an object")
                    continue
                if is_placeholder(str(claim.get("requirement_id") or "")):
                    errors.append(f"{prefix}: missing requirement_id")
                if claim.get("claim_type") not in CLAIM_TYPES:
                    errors.append(f"{prefix}: unsupported claim_type {claim.get('claim_type')!r}")
                if is_placeholder(str(claim.get("scenario_id") or "")):
                    errors.append(f"{prefix}: missing scenario_id")
                assertions = claim.get("assertions")
                if not isinstance(assertions, list) or not assertions:
                    errors.append(f"{prefix}: assertions must be a nonempty list")
                elif any(is_placeholder(str(assertion)) for assertion in assertions):
                    errors.append(f"{prefix}: assertions contain an empty or placeholder value")
        evidence_path = entry.get("path")
        if evidence_path:
            resolved = Path(evidence_path)
            if not resolved.is_absolute():
                resolved = (path.resolve().parent / resolved).resolve()
            if not resolved.exists():
                errors.append(f"{evidence_id}: evidence path not found: {evidence_path}")
    return by_id


def main():
    parser = argparse.ArgumentParser(description="Validate requirement coverage and acceptance evidence.")
    parser.add_argument("--requirements", required=True, type=Path)
    parser.add_argument("--acceptance", required=True, type=Path)
    parser.add_argument("--evidence-register", type=Path)
    parser.add_argument("--baseline-version")
    parser.add_argument("--design-qa", type=Path)
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
            if coverage in {"missing", "pending_confirmation"}:
                errors.append(
                    f"{identifier} line {line_number}: coverage {coverage} cannot have result passed"
                )

    evidence_by_id = {}
    if passed_rows:
        if not args.baseline_version:
            errors.append("passed acceptance rows require --baseline-version")
        else:
            evidence_by_id = load_evidence_registry(args.evidence_register, args.baseline_version, errors)
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
        matches = marker or fallback
        if not matches:
            errors.append("design QA has no structured final result")
        elif matches[-1].lower() != "passed":
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
