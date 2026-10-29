#!/usr/bin/env python3

import argparse
import sys
from pathlib import Path

from evidence_manifest_contract import validate_manifest


def main():
    parser = argparse.ArgumentParser(description="Validate source and page-level evidence coverage.")
    parser.add_argument("manifest", type=Path)
    args = parser.parse_args()

    if not args.manifest.is_file():
        print(f"ERROR: file not found: {args.manifest}", file=sys.stderr)
        return 2

    errors, counts = validate_manifest(args.manifest)
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
