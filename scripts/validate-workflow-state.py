#!/usr/bin/env python3

import argparse
import json
import sys
from pathlib import Path

from evidence_manifest_contract import validate_manifest


PHASE_IDS = [
    "P1_EVIDENCE",
    "P2_REQUIREMENTS",
    "P3_BUSINESS_MODEL",
    "P4_FLOW",
    "P5_PAGE_SPEC",
    "P6_BUILD",
    "P7_PACKAGE",
    "P8_HANDOFF",
]
STATUSES = {
    "not_started",
    "in_progress",
    "blocked",
    "confirmed",
    "reused",
    "invalidated",
    "not_applicable",
}
TERMINAL_STATUSES = {"confirmed", "reused", "not_applicable"}
DECISION_STATUSES = {"open", "confirmed", "superseded", "deferred"}


def resolve_artifact(root, value):
    clean = str(value).split("#", 1)[0]
    path = Path(clean)
    return path if path.is_absolute() else (root / path).resolve()


def main():
    parser = argparse.ArgumentParser(description="Validate a business prototype workflow checkpoint.")
    parser.add_argument("state", type=Path)
    args = parser.parse_args()

    if not args.state.is_file():
        print(f"ERROR: file not found: {args.state}", file=sys.stderr)
        return 2

    try:
        state = json.loads(args.state.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        print(f"ERROR: invalid JSON: {error}", file=sys.stderr)
        return 2

    root = args.state.resolve().parent
    errors = []
    required_fields = (
        "schema_version",
        "skill_version",
        "mode",
        "baseline_version",
        "evidence_manifest",
        "journey_coverage",
        "current_phase",
        "phases",
        "decisions",
        "open_decisions",
        "next_safe_action",
    )
    for field in required_fields:
        if field not in state or state[field] in (None, "", {}):
            if field in {"decisions", "open_decisions"} and state.get(field) == []:
                continue
            errors.append(f"missing required field: {field}")

    if state.get("schema_version") != "0.3":
        errors.append(f"unsupported schema_version: {state.get('schema_version')!r}")
    if state.get("skill_version") != "0.2":
        errors.append(f"unsupported skill_version: {state.get('skill_version')!r}")
    if state.get("mode") not in {"full", "fast", "incremental"}:
        errors.append(f"unsupported mode: {state.get('mode')!r}")
    if state.get("current_phase") not in PHASE_IDS:
        errors.append(f"unsupported current_phase: {state.get('current_phase')!r}")

    decisions = state.get("decisions", [])
    decision_by_id = {}
    if not isinstance(decisions, list):
        errors.append("decisions must be a list")
        decisions = []
    for decision in decisions:
        if not isinstance(decision, dict):
            errors.append("decision entry must be an object")
            continue
        decision_id = decision.get("id")
        if not decision_id:
            errors.append("decision entry requires id")
            continue
        if decision_id in decision_by_id:
            errors.append(f"duplicate decision ID: {decision_id}")
        decision_by_id[decision_id] = decision
        if decision.get("status") not in DECISION_STATUSES:
            errors.append(f"{decision_id}: unsupported decision status {decision.get('status')!r}")
        affected = decision.get("affected_phases")
        if not isinstance(affected, list) or not affected:
            errors.append(f"{decision_id}: affected_phases must be a nonempty list")
        elif any(phase_id not in PHASE_IDS for phase_id in affected):
            errors.append(f"{decision_id}: affected_phases contains an unknown phase")

    open_decisions = state.get("open_decisions", [])
    if not isinstance(open_decisions, list):
        errors.append("open_decisions must be a list")
        open_decisions = []
    open_set = set(open_decisions)
    if len(open_set) != len(open_decisions):
        errors.append("open_decisions contains duplicate IDs")
    expected_open = {identifier for identifier, value in decision_by_id.items() if value.get("status") == "open"}
    if open_set != expected_open:
        errors.append("open_decisions must exactly match decisions with status open")

    phases = state.get("phases", {})
    if not isinstance(phases, dict):
        errors.append("phases must be an object")
        phases = {}
    for phase_id in PHASE_IDS:
        if phase_id not in phases:
            errors.append(f"missing phase: {phase_id}")
    for phase_id in phases:
        if phase_id not in PHASE_IDS:
            errors.append(f"unknown phase: {phase_id}")

    baseline_version = state.get("baseline_version")
    for phase_id in PHASE_IDS:
        phase = phases.get(phase_id)
        if not isinstance(phase, dict):
            if phase is not None:
                errors.append(f"{phase_id}: phase entry must be an object")
            continue
        status = phase.get("status")
        if status not in STATUSES:
            errors.append(f"{phase_id}: unsupported status {status!r}")
            continue

        if status in {"confirmed", "reused"}:
            if phase.get("baseline_version") != baseline_version:
                errors.append(f"{phase_id}: {status} phase baseline_version must match workflow baseline")
            if not phase.get("artifacts"):
                errors.append(f"{phase_id}: {status} phase requires artifacts")
            if not phase.get("evidence"):
                errors.append(f"{phase_id}: {status} phase requires evidence")
            if not phase.get("confirmed_by"):
                errors.append(f"{phase_id}: {status} phase requires confirmed_by")
            if not phase.get("confirmed_at"):
                errors.append(f"{phase_id}: {status} phase requires confirmed_at")
            for artifact in phase.get("artifacts") or []:
                if not resolve_artifact(root, artifact).exists():
                    errors.append(f"{phase_id}: artifact path not found: {artifact}")

        if status == "reused":
            if not phase.get("revalidated_by"):
                errors.append(f"{phase_id}: reused phase requires revalidated_by")
            if not phase.get("revalidated_at"):
                errors.append(f"{phase_id}: reused phase requires revalidated_at")

        if status == "blocked":
            decision_ids = phase.get("decision_ids")
            if not isinstance(decision_ids, list) or not decision_ids:
                errors.append(f"{phase_id}: blocked phase requires decision_ids")
            else:
                for decision_id in decision_ids:
                    decision = decision_by_id.get(decision_id)
                    if decision is None:
                        errors.append(f"{phase_id}: unknown blocked decision ID: {decision_id}")
                        continue
                    if decision_id not in open_set or decision.get("status") != "open":
                        errors.append(f"{phase_id}: blocked decision must be open: {decision_id}")
                    if phase_id not in decision.get("affected_phases", []):
                        errors.append(f"{phase_id}: decision {decision_id} does not reference this phase")
                    if not decision.get("question") or not decision.get("recommended_option"):
                        errors.append(f"{decision_id}: open decision requires question and recommended_option")

        if status == "not_applicable":
            if not phase.get("reason"):
                errors.append(f"{phase_id}: not_applicable phase requires reason")
            scope_decision_id = phase.get("scope_decision_id")
            if not scope_decision_id:
                errors.append(f"{phase_id}: not_applicable phase requires scope_decision_id")
            else:
                decision = decision_by_id.get(scope_decision_id)
                if decision is None:
                    errors.append(f"{phase_id}: unknown scope_decision_id: {scope_decision_id}")
                elif decision.get("status") != "confirmed" or phase_id not in decision.get("affected_phases", []):
                    errors.append(f"{phase_id}: scope decision must be confirmed and reference this phase")

        if status == "invalidated" and not phase.get("invalidated_by"):
            errors.append(f"{phase_id}: invalidated phase requires invalidated_by")

    actionable = [
        phase_id
        for phase_id in PHASE_IDS
        if isinstance(phases.get(phase_id), dict) and phases[phase_id].get("status") not in TERMINAL_STATUSES
    ]
    expected_current = actionable[0] if actionable else "P8_HANDOFF"
    if state.get("current_phase") in PHASE_IDS and state.get("current_phase") != expected_current:
        errors.append(
            f"current_phase must match earliest actionable phase: expected {expected_current}, got {state.get('current_phase')}"
        )

    p1_status = phases.get("P1_EVIDENCE", {}).get("status") if isinstance(phases.get("P1_EVIDENCE"), dict) else None
    if p1_status in {"confirmed", "reused"}:
        manifest_value = state.get("evidence_manifest")
        manifest_path = resolve_artifact(root, manifest_value) if manifest_value else None
        if manifest_path is None or not manifest_path.is_file():
            errors.append(f"P1_EVIDENCE: evidence manifest not found: {manifest_value}")
        else:
            manifest_errors, _ = validate_manifest(manifest_path)
            errors.extend(f"P1_EVIDENCE: {error}" for error in manifest_errors)

    p8_status = phases.get("P8_HANDOFF", {}).get("status") if isinstance(phases.get("P8_HANDOFF"), dict) else None
    if p8_status in {"confirmed", "reused"}:
        journey_value = state.get("journey_coverage")
        journey_path = resolve_artifact(root, journey_value) if journey_value else None
        if journey_path is None or not journey_path.is_file():
            errors.append(f"P8_HANDOFF: journey coverage not found: {journey_value}")

    if not isinstance(state.get("invalidated_artifacts", []), list):
        errors.append("invalidated_artifacts must be a list")

    print(f"mode={state.get('mode')}")
    print(f"current_phase={state.get('current_phase')}")
    print(f"phases={len(phases)}")
    print(f"decisions={len(decision_by_id)}")
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print("result=passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
