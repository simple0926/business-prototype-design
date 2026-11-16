#!/usr/bin/env python3

import argparse
import re
import sys
from pathlib import Path


def read_required(path):
    if not path.is_file():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8")


def check_legacy(args, requirements, acceptance, design_qa):
    """Keep the requirement-only check available to earlier reports."""
    errors = []
    pattern = re.compile(args.id_pattern)
    requirement_ids = set(pattern.findall(requirements))
    acceptance_ids = set(pattern.findall(acceptance))
    missing = sorted(requirement_ids - acceptance_ids)
    unknown = sorted(acceptance_ids - requirement_ids)

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

    return errors


def markdown(text):
    return re.sub(r"(?ms)^ {0,3}(`{3,}|~{3,})[^\n]*\n.*?^ {0,3}\1[ \t]*$", "", text)


def cells(line):
    return [part.strip() for part in re.split(r"(?<!\\)\|", line.strip()[1:-1])]


def table_rows(text, required_columns):
    lines = markdown(text).splitlines()
    header = []
    for index, line in enumerate(lines):
        line = line.strip()
        if not (line.startswith("|") and line.endswith("|")):
            header = []
            continue
        row = cells(line)
        if index + 1 < len(lines) and re.fullmatch(r"\s*\|(?:\s*:?-+:?\s*\|)+\s*", lines[index + 1]):
            names = [name.lower() for name in row]
            header = names if required_columns <= set(names) else []
        elif header and not re.fullmatch(r"\|(?:\s*:?-+:?\s*\|)+", line):
            yield dict(zip(header, row)), len(row) == len(header)


def field(text, label, allowed, errors):
    values = re.findall(
        rf"(?im)^[ \t]*(?:[-*][ \t]+)?{re.escape(label)}:[ \t]*(.*)$", markdown(text)
    )
    if len(values) != 1 or values[0].strip().lower() not in allowed:
        errors.append(f"{label}: expected one value from {', '.join(sorted(allowed))}")
        return None
    return values[0].strip().lower()


def filled(value):
    return bool(value.strip(" `*_-—–/")) and not re.fullmatch(
        r"(?:todo|tbd|none|n/?a|pending|placeholder|待补充|待确认)", value.strip(), re.I
    )


def check_format(acceptance, design_qa, errors):
    prototype = field(acceptance, "Prototype type", {"interactive", "static"}, errors)
    delivery = field(acceptance, "Delivery format", {"offline-html", "images"}, errors)
    visual = field(acceptance, "Design QA", {"passed", "failed", "blocked", "n/a"}, errors)
    image = field(acceptance, "Image delivery", {"passed", "failed", "blocked", "n/a"}, errors)
    offline = field(acceptance, "Offline conclusion", {"verified offline", "static only", "failed", "n/a"}, errors)
    overall = field(acceptance, "Overall result", {"completed", "not complete"}, errors)

    if design_qa is None:
        if visual != "n/a":
            errors.append("Design QA must be N/A with --no-visual-target")
    else:
        final = field(design_qa, "Final result", {"passed", "failed", "blocked"}, errors)
        if final != "passed" or final != visual:
            errors.append("Design QA must pass and match the report for a selected standard")

    if delivery == "images" and (image != "passed" or offline != "n/a"):
        errors.append("image delivery requires a passed image check and offline N/A")
    if delivery == "offline-html" and (prototype != "interactive" or offline != "verified offline" or image != "n/a"):
        errors.append("offline HTML requires an interactive prototype, verified offline, and image N/A")
    expected_layers = {
        "business": "passed",
        "functional": "n/a" if prototype == "static" else "passed",
        "visual": visual,
        "delivery": "passed",
    }
    for row, valid in table_rows(acceptance, {"layer", "conclusion", "basis"}):
        layer = row.get("layer", "").lower()
        expected = expected_layers.pop(layer, None)
        if (not valid or expected is None or row["conclusion"].lower() != expected
                or not filled(row["basis"])):
            errors.append(f"{layer}: invalid layer conclusion or missing basis")
    for layer in expected_layers:
        errors.append(f"{layer}: missing layer conclusion")

    recorded_stages = set()
    for row, valid in table_rows(acceptance, {"confirmed input", "artifact/version", "decision ids"}):
        stage = re.match(r"stage ([4-7])\b", row.get("confirmed input", ""), re.I)
        if valid and stage and (filled(row["artifact/version"]) or filled(row["decision ids"])):
            recorded_stages.add(stage[1])
    for stage in sorted(set("4567") - recorded_stages):
        errors.append(f"stage {stage}: missing confirmed acceptance baseline")

    if overall != "completed":
        errors.append("report does not claim completion")
    return prototype


def check_strict(args, requirements, spec, acceptance, design_qa):
    errors = []
    prototype = check_format(acceptance, design_qa, errors)
    id_pattern = re.compile(args.id_pattern)
    scope = {}
    scope_column = "scope decision"
    for row, valid in table_rows(requirements, {"req", scope_column}):
        req = row.get("req", "")
        decision = row.get(scope_column, "").lower()
        if not valid or not id_pattern.fullmatch(req) or req in scope or decision not in {
            "included", "deferred", "out of scope"
        }:
            errors.append(f"invalid or duplicate requirement row: {req}")
            continue
        scope[req] = decision
    if not scope:
        errors.append("no requirement rows with a scope decision found")

    criteria = {}
    verification = "verification (visual / runtime)"
    for row, valid in table_rows(spec, {"req", "ac", verification}):
        req, ac, kind = (row.get(name, "") for name in ("req", "ac", verification))
        key = req, ac
        if (not valid or req not in scope or not re.fullmatch(r"AC-\d+", ac)
                or key in criteria or kind not in {"visual", "runtime"}):
            errors.append(f"invalid or duplicate specification criterion: {req}/{ac}")
            continue
        criteria[key] = kind
    specified = {req for req, _ in criteria}
    for req, decision in scope.items():
        if decision == "included" and req not in specified:
            errors.append(f"{req}: no criterion in the specification")

    expected = set(criteria)
    expected.update((req, "—") for req, decision in scope.items()
                    if decision == "deferred" and req not in specified)
    seen = set()
    columns = {"req", "ac", "artifact evidence", "verification evidence", "result", "notes"}
    for row, valid in table_rows(acceptance, columns):
        req, ac = (row.get(name, "") for name in ("req", "ac"))
        key = req, ac
        if not valid or key in seen or (key not in expected and not (ac == "—" and scope.get(req) == "out of scope")):
            errors.append(f"invalid, unexpected or duplicate acceptance row: {req}/{ac}")
            continue
        seen.add(key)
        decision = scope[req]
        result = row["result"].lower()
        kind = criteria.get(key)
        decision_note = bool(re.search(r"\bDEC-[\w-]+\b", row["notes"]))
        if result == "passed":
            if decision != "included" or (prototype == "static" and kind == "runtime"):
                errors.append(f"{req}/{ac}: this scope cannot claim a pass")
            evidence = row["verification evidence"] if kind == "runtime" else row["artifact evidence"]
            if not filled(evidence):
                errors.append(f"{req}/{ac}: passed row lacks {kind} evidence")
        elif result == "deferred":
            if not decision_note or decision == "out of scope":
                errors.append(f"{req}/{ac}: deferred requires a recorded decision")
        elif result == "n/a":
            allowed = decision == "out of scope" or (prototype == "static" and kind == "runtime")
            if not allowed or not decision_note:
                errors.append(f"{req}/{ac}: N/A requires an applicable scope decision")
        else:
            errors.append(f"{req}/{ac}: {result or 'missing result'} prevents completion")
    for req, ac in sorted(expected - seen):
        errors.append(f"{req}/{ac}: missing acceptance row")

    for report in (requirements, acceptance):
        for row, valid in table_rows(report, {"oq", "blocking (yes / no)", "status (open / answered)", "affects"}):
            oq = row.get("oq", "")
            if not valid:
                errors.append(f"{oq}: malformed open question row")
                continue
            if row["blocking (yes / no)"].lower() == "yes" and row["status (open / answered)"].lower() != "answered":
                affected = [match[0] for match in id_pattern.finditer(row["affects"])]
                if not affected or any(scope.get(req) not in {"deferred", "out of scope"} for req in affected):
                    errors.append(f"{oq}: open blocking question")

    print(f"requirements={len(scope)}")
    print(f"criteria={len(criteria)}")
    return errors


def main():
    parser = argparse.ArgumentParser(description="Check acceptance report consistency and traceability.")
    parser.add_argument("--requirements", required=True, type=Path)
    parser.add_argument("--acceptance", required=True, type=Path)
    parser.add_argument("--spec", type=Path, help="page specification, required for criterion reports")
    visual = parser.add_mutually_exclusive_group()
    visual.add_argument("--design-qa", type=Path)
    visual.add_argument("--no-visual-target", action="store_true")
    parser.add_argument("--id-pattern", default=r"REQ-\d{3,}")
    parser.add_argument("--allow-pending", action="store_true", help="legacy requirement-only check")
    args = parser.parse_args()

    try:
        re.compile(args.id_pattern)
        requirements = read_required(args.requirements)
        acceptance = read_required(args.acceptance)
        design_qa = read_required(args.design_qa) if args.design_qa else None
        spec = read_required(args.spec) if args.spec else None
    except (OSError, UnicodeError, re.error) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2

    uses_current_report = (
        bool(re.search(r"(?im)^\s*(?:-\s+)?(?:Prototype type|Delivery format):", acceptance))
        or any(table_rows(acceptance, {"req", "ac", "result"}))
    )
    if uses_current_report and spec is None:
        parser.error("criterion reports require --spec")
    if spec is not None:
        if not (args.design_qa or args.no_visual_target):
            parser.error("give --design-qa or --no-visual-target for criterion reports")
        if args.allow_pending:
            parser.error("--allow-pending is for legacy reports")
        errors = check_strict(args, requirements, spec, acceptance, design_qa)
    else:
        errors = check_legacy(args, requirements, acceptance, design_qa)
        if not errors:
            print("legacy requirement-only check")

    for error in errors:
        print(f"ERROR: {error}")
    print("result=failed" if errors else "result=passed")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
