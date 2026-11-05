#!/usr/bin/env python3

import argparse
import sys
from pathlib import Path

from evidence_contract import validate_evidence_register
from evidence_manifest_contract import validate_manifest


def main():
    parser = argparse.ArgumentParser(description="Validate source and page-level evidence coverage.")
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--evidence-register", type=Path)
    parser.add_argument("--baseline-version")
    parser.add_argument("--require-schema", choices=("0.3", "0.4"))
    args = parser.parse_args()

    if not args.manifest.is_file():
        print(f"ERROR: file not found: {args.manifest}", file=sys.stderr)
        return 2

    evidence_ids = None
    errors = []
    if args.evidence_register:
        if not args.baseline_version:
            errors.append("--evidence-register requires --baseline-version")
        else:
            evidence_by_id, evidence_errors = validate_evidence_register(
                args.evidence_register,
                args.baseline_version,
                require_schema=args.require_schema,
            )
            evidence_ids = set(evidence_by_id)
            errors.extend(evidence_errors)
    manifest_errors, counts = validate_manifest(
        args.manifest,
        evidence_ids=evidence_ids,
        expected_baseline=args.baseline_version,
        require_schema=args.require_schema,
    )
    errors.extend(manifest_errors)
    print(f"sources={counts['sources']}")
    print(f"units={counts['units']}")
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("result=passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
