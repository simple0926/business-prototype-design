#!/usr/bin/env python3

import argparse
import json
import re
import sys
from pathlib import Path


JOURNEY_PATTERN = re.compile(r"JNY-\d{3,}")
EVIDENCE_PATTERN = re.compile(r"EVD-\d{3,}")
ALLOWED_CLAIM_TYPES = {"interaction", "validation", "state_transition"}
ALLOWED_RISK_TAGS = {
    "core_path",
    "cross_role",
    "permission",
    "validation",
    "exception",
    "retry",
    "batch",
    "persistence",
}


def read_json(path):
    if not path.is_file():
        raise FileNotFoundError(path)
    return json.loads(path.read_text(encoding="utf-8"))


def is_nonempty_text(value):
    return isinstance(value, str) and bool(value.strip())


def main():
    parser = argparse.ArgumentParser(
        description="Validate a manually derived journey checklist against passed test/browser evidence."
    )
    parser.add_argument("--journeys", required=True, type=Path)
    parser.add_argument("--evidence-register", required=True, type=Path)
    parser.add_argument("--baseline-version", required=True)
    parser.add_argument("--allow-pending", action="store_true")
    args = parser.parse_args()

    try:
        register = read_json(args.evidence_register)
        coverage = read_json(args.journeys)
    except FileNotFoundError as error:
        print(f"ERROR: file not found: {error.args[0]}", file=sys.stderr)
        return 2
    except json.JSONDecodeError as error:
        print(f"ERROR: invalid JSON: {error}", file=sys.stderr)
        return 2

    errors = []
    if coverage.get("schema_version") != "0.3":
        errors.append(f"unsupported journey schema_version: {coverage.get('schema_version')!r}")
    if coverage.get("baseline_version") != args.baseline_version:
        errors.append("journey baseline_version does not match requested baseline")
    if register.get("baseline_version") != args.baseline_version:
        errors.append("evidence register baseline_version does not match requested baseline")

    evidence_by_id = {}
    entries = register.get("evidence")
    if not isinstance(entries, list):
        errors.append("evidence register requires an evidence list")
        entries = []
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        evidence_id = entry.get("id")
        if isinstance(evidence_id, str):
            evidence_by_id[evidence_id] = entry

    journeys = coverage.get("journeys")
    if not isinstance(journeys, list) or not journeys:
        errors.append("journey coverage requires a nonempty journeys list")
        journeys = []

    seen = set()
    for journey in journeys:
        if not isinstance(journey, dict):
            errors.append("journey entry must be an object")
            continue
        journey_id = journey.get("id")
        if not isinstance(journey_id, str) or not JOURNEY_PATTERN.fullmatch(journey_id):
            errors.append(f"invalid journey ID: {journey_id!r}")
            continue
        if journey_id in seen:
            errors.append(f"duplicate journey ID: {journey_id}")
        seen.add(journey_id)

        for field in ("actor", "start_state", "action", "expected_state", "next_actor"):
            if not is_nonempty_text(journey.get(field)):
                errors.append(f"{journey_id}: missing {field}")

        claim_type = journey.get("claim_type")
        if claim_type not in ALLOWED_CLAIM_TYPES:
            errors.append(f"{journey_id}: unsupported claim_type {claim_type!r}")

        requirement_ids = journey.get("requirement_ids")
        if not isinstance(requirement_ids, list) or not requirement_ids or not all(
            is_nonempty_text(value) for value in requirement_ids
        ):
            errors.append(f"{journey_id}: requirement_ids must be a nonempty string list")
            requirement_ids = []

        risk_tags = journey.get("risk_tags")
        if not isinstance(risk_tags, list) or not risk_tags:
            errors.append(f"{journey_id}: risk_tags must be a nonempty list")
        else:
            unsupported = sorted(set(risk_tags) - ALLOWED_RISK_TAGS)
            if unsupported:
                errors.append(f"{journey_id}: unsupported risk tags: {', '.join(unsupported)}")

        result = journey.get("result")
        allowed_results = {"passed"} | ({"pending", "blocked"} if args.allow_pending else set())
        if result not in allowed_results:
            errors.append(f"{journey_id}: unsupported or unfinished result {result!r}")

        evidence_ids = journey.get("evidence_ids")
        if not isinstance(evidence_ids, list) or not evidence_ids:
            errors.append(f"{journey_id}: evidence_ids must be a nonempty list")
            evidence_ids = []

        referenced = []
        for evidence_id in evidence_ids:
            if not isinstance(evidence_id, str) or not EVIDENCE_PATTERN.fullmatch(evidence_id):
                errors.append(f"{journey_id}: invalid evidence ID {evidence_id!r}")
                continue
            evidence = evidence_by_id.get(evidence_id)
            if evidence is None:
                errors.append(f"{journey_id}: unknown evidence ID {evidence_id}")
                continue
            referenced.append(evidence)
            if evidence.get("kind") not in {"test", "browser"}:
                errors.append(f"{journey_id}: journey evidence must be test or browser: {evidence_id}")
            if evidence.get("result") != "passed":
                errors.append(f"{journey_id}: evidence is not passed: {evidence_id}")
            if evidence.get("baseline_version") != args.baseline_version:
                errors.append(f"{journey_id}: evidence baseline does not match: {evidence_id}")

        for requirement_id in requirement_ids:
            matching_claim = False
            for evidence in referenced:
                for claim in evidence.get("claims") or []:
                    if not isinstance(claim, dict):
                        continue
                    if (
                        claim.get("requirement_id") == requirement_id
                        and claim.get("scenario_id") == journey_id
                        and claim.get("claim_type") == claim_type
                        and isinstance(claim.get("assertions"), list)
                        and any(is_nonempty_text(assertion) for assertion in claim.get("assertions"))
                    ):
                        matching_claim = True
                        break
                if matching_claim:
                    break
            if not matching_claim:
                errors.append(
                    f"{journey_id}: no test/browser evidence claim binds {requirement_id} to this journey"
                )

    print(f"journeys={len(journeys)}")
    print(f"evidence_ids={len(evidence_by_id)}")
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("result=passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
