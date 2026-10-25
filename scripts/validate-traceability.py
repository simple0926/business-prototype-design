#!/usr/bin/env python3

import argparse
import re
import sys
from pathlib import Path


def read_required(path):
    if not path.is_file():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="Check requirement coverage and QA evidence.")
    parser.add_argument("--requirements", required=True, type=Path)
    parser.add_argument("--acceptance", required=True, type=Path)
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

    pattern = re.compile(args.id_pattern)
    requirement_ids = set(pattern.findall(requirements))
    acceptance_ids = set(pattern.findall(acceptance))
    missing = sorted(requirement_ids - acceptance_ids)
    unknown = sorted(acceptance_ids - requirement_ids)
    errors = []

    if not requirement_ids:
        errors.append("no requirement IDs found")
    if missing:
        errors.append(f"requirements missing from acceptance: {', '.join(missing)}")
    if unknown:
        errors.append(f"acceptance IDs absent from requirements: {', '.join(unknown)}")

    if not args.allow_pending:
        pending_pattern = re.compile(r"\b(?:TODO|TBD)\b|待确认|待回答", re.I)
        if pending_pattern.search(requirements):
            errors.append("requirements contain unresolved pending markers")

    if design_qa is not None:
        matches = re.findall(r"final result\s*:\s*(passed|blocked)", design_qa, re.I)
        if not matches:
            errors.append("design QA has no final result")
        elif matches[-1].lower() != "passed":
            errors.append("design QA final result is not passed")

    print(f"requirements={len(requirement_ids)}")
    print(f"acceptance_ids={len(acceptance_ids)}")
    print(f"design_qa={'checked' if design_qa is not None else 'not_provided'}")

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print("result=passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
