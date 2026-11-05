#!/usr/bin/env python3

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def normalized_header(value):
    return re.sub(r"[\s_-]+", "", value.strip().lower())


def table_rows_by_header(text, aliases):
    aliases = {normalized_header(value) for value in aliases}
    rows = []
    active = False
    for line in text.splitlines():
        if not line.lstrip().startswith("|"):
            active = False
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if cells and normalized_header(cells[0]) in aliases:
            active = True
            continue
        if not active or not cells or re.fullmatch(r":?-{3,}:?", cells[0]):
            continue
        rows.append(cells)
    return rows


def contains_any(text, patterns):
    return any(re.search(pattern, text, re.I) for pattern in patterns)


def contains_positive_signal(text, patterns, negations=()):
    scrubbed = text
    for negation in negations:
        scrubbed = re.sub(negation, " ", scrubbed, flags=re.I)
    return contains_any(scrubbed, patterns)


def run(label, command):
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    print(f"[{label}] rc={result.returncode}")
    if result.stdout.strip():
        print(result.stdout.strip())
    if result.stderr.strip():
        print(result.stderr.strip(), file=sys.stderr)
    return result.returncode


def main():
    parser = argparse.ArgumentParser(description="Validate a complete business-prototype-design 0.3 package.")
    parser.add_argument("--workflow-state", required=True, type=Path)
    parser.add_argument("--requirements", required=True, type=Path)
    parser.add_argument("--prototype-spec", required=True, type=Path)
    parser.add_argument("--acceptance", required=True, type=Path)
    parser.add_argument("--evidence-register", required=True, type=Path)
    parser.add_argument("--standalone", required=True, type=Path)
    parser.add_argument("--baseline-version", required=True)
    parser.add_argument("--evidence-manifest", type=Path)
    parser.add_argument("--journey-coverage", type=Path)
    parser.add_argument("--design-qa", type=Path)
    args = parser.parse_args()

    try:
        workflow = json.loads(args.workflow_state.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        print(f"ERROR: invalid workflow state: {error}", file=sys.stderr)
        return 2
    try:
        evidence_register = json.loads(args.evidence_register.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        print(f"ERROR: invalid evidence register: {error}", file=sys.stderr)
        return 2
    try:
        requirements_text = args.requirements.read_text(encoding="utf-8")
        prototype_spec_text = args.prototype_spec.read_text(encoding="utf-8")
    except OSError as error:
        print(f"ERROR: cannot read package contract: {error}", file=sys.stderr)
        return 2

    errors = []
    if workflow.get("schema_version") != "0.4":
        errors.append("final 0.3 package requires workflow schema_version 0.4")
    if workflow.get("skill_version") != "0.3":
        errors.append("final package requires skill_version 0.3")
    if evidence_register.get("schema_version") != "0.4":
        errors.append("final 0.3 package requires evidence register schema_version 0.4")
    if workflow.get("baseline_version") != args.baseline_version:
        errors.append("workflow baseline_version does not match requested baseline")
    if workflow.get("evidence_profile") == "image_bearing" and not args.evidence_manifest:
        errors.append("image-bearing package requires --evidence-manifest")
    if workflow.get("journey_profile") == "high_risk" and not args.journey_coverage:
        errors.append("high-risk package requires --journey-coverage")
    if workflow.get("visual_profile") == "comparison_required" and not args.design_qa:
        errors.append("visual comparison package requires --design-qa")

    source_rows = table_rows_by_header(requirements_text, {"Source ID", "来源 ID", "来源编号"})
    source_ids = {row[0] for row in source_rows if row}
    image_source_ids = {
        row[0]
        for row in source_rows
        if len(row) > 1 and contains_any(
            row[1],
            (
                r"\bpdf\b", r"\bimage\b", r"\bpng\b", r"\bjpe?g\b", r"\bgif\b",
                r"\bwebp\b", r"\bsvg\b", r"\bfigma\b", r"\bpptx?\b", r"\bkeynote\b",
                r"screenshot", r"slide", r"wireframe", r"mockup", r"图片", r"截图", r"幻灯", r"线框图", r"设计稿",
            ),
        )
    }
    if image_source_ids and workflow.get("evidence_profile") != "image_bearing":
        errors.append("requirements contain image-bearing sources but evidence_profile is not image_bearing")
    if workflow.get("evidence_profile") == "text_only":
        declared_sources = set(workflow.get("text_source_ids") or [])
        if declared_sources != source_ids:
            errors.append("workflow text_source_ids must exactly match the requirements source register")
    if args.evidence_manifest:
        try:
            manifest = json.loads(args.evidence_manifest.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            errors.append(f"invalid evidence manifest: {error}")
        else:
            manifest_source_ids = {
                item.get("source_id")
                for item in manifest.get("sources", [])
                if isinstance(item, dict) and item.get("source_id")
            }
            if not manifest_source_ids.issubset(source_ids):
                errors.append("evidence manifest contains Source IDs absent from requirements")
            if not image_source_ids.issubset(manifest_source_ids):
                errors.append("image-bearing requirement sources are missing from evidence manifest")

    role_rows = table_rows_by_header(requirements_text, {"Role", "角色"})
    state_rows = table_rows_by_header(requirements_text, {"Canonical state", "规范状态", "标准状态"})
    business_text = requirements_text + "\n" + prototype_spec_text
    approval_signal = contains_positive_signal(
        business_text,
        (r"\bapproval\b", r"\bapprove\b", r"\breviewer\b", r"审批", r"审核", r"批准"),
        (r"\bno approval(?: flow)?\b", r"\bwithout approval\b", r"不涉及审批", r"无需审批"),
    )
    if workflow.get("mode") == "lite":
        risk = workflow.get("risk_profile") or {}
        if not role_rows or not state_rows:
            errors.append("final Lite package requires machine-readable Role and Canonical state tables")
        if risk.get("actor_count") != len(role_rows):
            errors.append("Lite actor_count does not match the requirements Role table")
        if risk.get("canonical_state_count") != len(state_rows):
            errors.append("Lite canonical_state_count does not match the requirements Canonical state table")
        inferred_flags = {
            "has_permission_rules": contains_positive_signal(business_text, (r"\bpermission\b", r"\bauthori[sz]ation\b", r"access control", r"权限", r"授权"), (r"\bno permission rules?\b", r"不涉及权限")),
            "handles_money": contains_positive_signal(business_text, (r"\bpayment\b", r"\bamount\b", r"\bmoney\b", r"金额", r"支付", r"付款", r"结算"), (r"\bno (?:money|payment|amount)\b", r"不涉及(?:金额|支付|付款|结算)")),
            "allows_deletion": contains_positive_signal(business_text, (r"\bdelete\b", r"\bdeletion\b", r"删除"), (r"\bno delet(?:e|ion)\b", r"不涉及删除")),
            "has_external_effects": contains_positive_signal(business_text, (r"\bwebhook\b", r"\bpublish\b", r"send email", r"外部副作用", r"发布", r"发送邮件"), (r"\bno external effects?\b", r"无外部副作用", r"不涉及外部")),
            "handles_sensitive_data": contains_positive_signal(business_text, (r"\bsensitive\b", r"\bprivacy\b", r"\bpii\b", r"敏感", r"隐私", r"身份证"), (r"\bno sensitive data\b", r"不涉及敏感数据", r"不涉及隐私")),
            "has_approval_flow": approval_signal,
        }
        for flag, inferred in inferred_flags.items():
            if inferred and risk.get(flag) is not True:
                errors.append(f"Lite risk_profile conflicts with contract signal: {flag}")

    if (len(role_rows) >= 2 or len(state_rows) >= 3 or approval_signal) and workflow.get("journey_profile") != "high_risk":
        errors.append("cross-role, multi-state, or approval scope requires journey_profile high_risk")

    visual_target = re.search(r"(?im)^-\s*Selected visual target\s*:\s*(.+)$", prototype_spec_text)
    if visual_target and not contains_any(visual_target.group(1), (r"out of scope", r"\bnone\b", r"不在范围", r"无视觉对照")):
        if workflow.get("visual_profile") != "comparison_required":
            errors.append("prototype specification declares a visual target but visual_profile is not comparison_required")

    phase_values = workflow.get("phases")
    if not isinstance(phase_values, dict):
        errors.append("workflow phases must be an object")
        phase_values = {}
    terminal = {"confirmed", "reused", "not_applicable"}
    unfinished = sorted(
        phase_id
        for phase_id, phase in phase_values.items()
        if not isinstance(phase, dict) or phase.get("status") not in terminal
    )
    if unfinished:
        errors.append(f"final package has nonterminal phases: {', '.join(unfinished)}")
    if not isinstance(phase_values.get("P8_HANDOFF"), dict) or phase_values["P8_HANDOFF"].get("status") not in {"confirmed", "reused"}:
        errors.append("final package requires confirmed or reused P8_HANDOFF")

    workflow_root = args.workflow_state.resolve().parent
    def resolve_workflow_path(value):
        if not value:
            return None
        clean = str(value).split("#", 1)[0]
        path = Path(clean)
        return path.resolve() if path.is_absolute() else (workflow_root / path).resolve()

    expected_state_paths = {
        "evidence_register": args.evidence_register,
        "evidence_manifest": args.evidence_manifest,
        "journey_coverage": args.journey_coverage,
    }
    for field, argument_path in expected_state_paths.items():
        state_path = resolve_workflow_path(workflow.get(field))
        if argument_path is not None and state_path != argument_path.resolve():
            errors.append(f"workflow {field} does not match package argument")

    recorded_artifacts = {
        resolve_workflow_path(artifact)
        for phase in phase_values.values()
        if isinstance(phase, dict)
        for artifact in phase.get("artifacts") or []
    }
    required_artifacts = {
        args.requirements.resolve(),
        args.prototype_spec.resolve(),
        args.acceptance.resolve(),
        args.evidence_register.resolve(),
        args.standalone.resolve(),
    } | {
        path.resolve()
        for path in (args.evidence_manifest, args.journey_coverage, args.design_qa)
        if path is not None
    }
    missing_artifacts = sorted(str(path) for path in required_artifacts - recorded_artifacts)
    if missing_artifacts:
        errors.append(f"package arguments missing from workflow artifacts: {', '.join(missing_artifacts)}")
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    commands = [
        (
            "workflow",
            [sys.executable, str(ROOT / "validate-workflow-state.py"), str(args.workflow_state)],
        ),
        (
            "traceability",
            [
                sys.executable,
                str(ROOT / "validate-traceability.py"),
                "--requirements", str(args.requirements),
                "--prototype-spec", str(args.prototype_spec),
                "--acceptance", str(args.acceptance),
                "--evidence-register", str(args.evidence_register),
                "--baseline-version", args.baseline_version,
                "--workflow-state", str(args.workflow_state),
            ]
            + (["--design-qa", str(args.design_qa)] if args.design_qa else [])
            + (["--journey-coverage", str(args.journey_coverage)] if args.journey_coverage else [])
            + [item for path in (
                args.workflow_state,
                args.evidence_manifest,
                args.journey_coverage,
                args.design_qa,
            ) if path for item in ("--forbid-evidence-path", str(path))],
        ),
        (
            "standalone",
            [sys.executable, str(ROOT / "validate-standalone-html.py"), str(args.standalone)],
        ),
    ]
    if args.evidence_manifest:
        commands.append((
            "manifest",
            [
                sys.executable,
                str(ROOT / "validate-evidence-manifest.py"),
                str(args.evidence_manifest),
                "--evidence-register", str(args.evidence_register),
                "--baseline-version", args.baseline_version,
                "--require-schema", "0.4",
            ],
        ))
    if args.journey_coverage:
        commands.append((
            "journeys",
            [
                sys.executable,
                str(ROOT / "validate-journey-coverage.py"),
                "--journeys", str(args.journey_coverage),
                "--evidence-register", str(args.evidence_register),
                "--requirements", str(args.requirements),
                "--baseline-version", args.baseline_version,
                "--require-schema", "0.4",
            ],
        ))

    failed = [label for label, command in commands if run(label, command) != 0]
    if failed:
        print(f"ERROR: package validation failed: {', '.join(failed)}", file=sys.stderr)
        return 1
    print("package_result=passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
