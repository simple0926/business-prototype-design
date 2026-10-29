#!/usr/bin/env python3

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
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


def run_python(script, *args):
    return subprocess.run(
        [sys.executable, str(SCRIPTS / script), *map(str, args)],
        capture_output=True,
        text=True,
        check=False,
    )


def run_node(script, *args):
    return subprocess.run(
        ["node", str(SCRIPTS / script), *map(str, args)],
        capture_output=True,
        text=True,
        check=False,
    )


def phase(status="not_started", **overrides):
    value = {
        "status": status,
        "baseline_version": None,
        "artifacts": [],
        "evidence": [],
        "decision_ids": [],
        "confirmed_by": None,
        "confirmed_at": None,
        "revalidated_by": None,
        "revalidated_at": None,
        "reason": None,
        "scope_decision_id": None,
        "invalidated_by": None,
    }
    value.update(overrides)
    return value


def workflow_state(current_phase="P1_EVIDENCE"):
    return {
        "schema_version": "0.3",
        "skill_version": "0.2",
        "mode": "full",
        "scope_id": "SCOPE-001",
        "baseline_version": "B-001",
        "evidence_manifest": "evidence-manifest.json",
        "journey_coverage": "journey-coverage.json",
        "current_phase": current_phase,
        "phases": {phase_id: phase() for phase_id in PHASE_IDS},
        "decisions": [],
        "open_decisions": [],
        "invalidated_artifacts": [],
        "last_verified_at": None,
        "next_safe_action": "Continue the current phase.",
    }


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")


def write_evidence_manifest(path, source_path, total_units=1, included_units=None):
    included_units = list(range(1, total_units + 1)) if included_units is None else included_units
    write_json(
        path,
        {
            "schema_version": "0.3",
            "sources": [
                {
                    "source_id": "SRC-001",
                    "path": str(source_path),
                    "kind": "pdf",
                    "authority": "business_and_visual_evidence",
                    "total_units": total_units,
                    "requires_visual_review": True,
                    "units": [
                        {
                            "unit_id": f"page-{number:03d}",
                            "sequence": number,
                            "inspected": True,
                            "inspection_methods": ["text", "render"],
                            "classification": "mixed",
                            "evidence_ids": [f"SRC-001-P{number:03d}"],
                            "notes": "Reviewed.",
                        }
                        for number in included_units
                    ],
                }
            ],
        },
    )


def write_traceability_files(
    root,
    requirement_columns=8,
    placeholder_evidence=False,
    requirement_source="SRC-001",
    coverage="satisfied",
    implementation_kind="implementation",
    test_kind="test",
    implementation_captured_at="2026-10-28T10:00:00+08:00",
):
    requirements = root / "requirements.md"
    acceptance = root / "acceptance.md"
    registry = root / "evidence-register.json"
    implementation = root / "implementation.txt"
    test_result = root / "test-result.txt"
    implementation.write_text("implemented", encoding="utf-8")
    test_result.write_text("passed", encoding="utf-8")

    if requirement_columns == 8:
        requirements.write_text(
            """# Requirements

| Source ID | Type | Owner | Version or date | Authority | Relevant scope | Notes |
|---|---|---|---|---|---|---|
| SRC-001 | user instruction | user | 2026-10-28 | business | REQ-001 | direct input |

| ID | Requirement | Source | Coverage | Evidence or gap | Decision | Prototype mapping | Acceptance mapping |
|---|---|---|---|---|---|---|---|
| REQ-001 | Submit request | {requirement_source} | {coverage} | Confirmed by DEC-001 | DEC-001 | PAGE-001#submit | ACC-001 |
""".format(requirement_source=requirement_source, coverage=coverage),
            encoding="utf-8",
        )
    else:
        requirements.write_text(
            """# Requirements

| ID | Requirement | Source | Coverage | Decision | Prototype mapping | Acceptance mapping |
|---|---|---|---|---|---|---|
| REQ-001 | Submit request | SRC-001 | satisfied | DEC-001 | PAGE-001#submit | ACC-001 |
""",
            encoding="utf-8",
        )

    implementation_evidence = "not-implemented" if placeholder_evidence else "EVD-001"
    test_evidence = "not-run" if placeholder_evidence else "EVD-002"
    acceptance.write_text(
        f"""# Acceptance

| Requirement ID | Confirmed rule | Implementation evidence | Test or browser evidence | Result | Notes |
|---|---|---|---|---|---|
| REQ-001 | Submit request | {implementation_evidence} | {test_evidence} | passed | verified |
""",
        encoding="utf-8",
    )
    write_json(
        registry,
        {
            "schema_version": "0.3",
            "baseline_version": "B-001",
            "evidence": [
                {
                    "id": "EVD-001",
                    "kind": implementation_kind,
                    "claims": [
                        {
                            "requirement_id": "REQ-001",
                            "claim_type": "presence",
                            "scenario_id": "SCN-REQ-001-IMPLEMENTATION",
                            "assertions": ["The submit control is implemented."],
                        }
                    ],
                    "path": implementation.name,
                    "result": "passed",
                    "baseline_version": "B-001",
                    "captured_at": implementation_captured_at,
                },
                {
                    "id": "EVD-002",
                    "kind": test_kind,
                    "claims": [
                        {
                            "requirement_id": "REQ-001",
                            "claim_type": "interaction",
                            "scenario_id": "SCN-REQ-001-SUBMIT",
                            "assertions": ["Submitting the request produces the expected result."],
                        }
                    ],
                    "path": test_result.name,
                    "result": "passed",
                    "baseline_version": "B-001",
                    "captured_at": "2026-10-28T10:01:00+08:00",
                },
            ],
        },
    )
    return requirements, acceptance, registry


def write_journey_coverage(path, result="passed"):
    write_json(
        path,
        {
            "schema_version": "0.3",
            "baseline_version": "B-001",
            "journeys": [
                {
                    "id": "JNY-001",
                    "requirement_ids": ["REQ-001"],
                    "claim_type": "state_transition",
                    "actor": "Requester",
                    "start_state": "draft",
                    "action": "Submit request",
                    "expected_state": "submitted",
                    "next_actor": "Reviewer",
                    "risk_tags": ["core_path", "cross_role"],
                    "evidence_ids": ["EVD-002"],
                    "result": result,
                }
            ],
        },
    )


class TraceabilityContractTests(unittest.TestCase):
    def test_complete_traceability_passes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            requirements, acceptance, registry = write_traceability_files(root)

            result = run_python(
                "validate-traceability.py",
                "--requirements",
                requirements,
                "--acceptance",
                acceptance,
                "--evidence-register",
                registry,
                "--baseline-version",
                "B-001",
            )

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_seven_column_requirement_table_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            requirements, acceptance, registry = write_traceability_files(root, requirement_columns=7)

            result = run_python(
                "validate-traceability.py",
                "--requirements",
                requirements,
                "--acceptance",
                acceptance,
                "--evidence-register",
                registry,
                "--baseline-version",
                "B-001",
            )

            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("8 columns", result.stderr)

    def test_placeholder_evidence_cannot_pass(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            requirements, acceptance, registry = write_traceability_files(root, placeholder_evidence=True)

            result = run_python(
                "validate-traceability.py",
                "--requirements",
                requirements,
                "--acceptance",
                acceptance,
                "--evidence-register",
                registry,
                "--baseline-version",
                "B-001",
            )

            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("evidence ID", result.stderr)

    def test_missing_evidence_artifact_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            requirements, acceptance, registry = write_traceability_files(root)
            (root / "test-result.txt").unlink()

            result = run_python(
                "validate-traceability.py",
                "--requirements",
                requirements,
                "--acceptance",
                acceptance,
                "--evidence-register",
                registry,
                "--baseline-version",
                "B-001",
            )

            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("evidence path not found", result.stderr)

    def test_unsupported_evidence_kind_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            requirements, acceptance, registry = write_traceability_files(
                root, implementation_kind="banana"
            )

            result = run_python(
                "validate-traceability.py",
                "--requirements",
                requirements,
                "--acceptance",
                acceptance,
                "--evidence-register",
                registry,
                "--baseline-version",
                "B-001",
            )

            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("unsupported evidence kind", result.stderr)

    def test_evidence_kind_must_match_acceptance_column(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            requirements, acceptance, registry = write_traceability_files(
                root, implementation_kind="test", test_kind="implementation"
            )

            result = run_python(
                "validate-traceability.py",
                "--requirements",
                requirements,
                "--acceptance",
                acceptance,
                "--evidence-register",
                registry,
                "--baseline-version",
                "B-001",
            )

            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("implementation evidence requires kind implementation", result.stderr)

    def test_invalid_capture_timestamp_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            requirements, acceptance, registry = write_traceability_files(
                root, implementation_captured_at="not-a-date"
            )

            result = run_python(
                "validate-traceability.py",
                "--requirements",
                requirements,
                "--acceptance",
                acceptance,
                "--evidence-register",
                registry,
                "--baseline-version",
                "B-001",
            )

            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("captured_at must be ISO 8601", result.stderr)

    def test_requirement_source_must_exist_in_source_register(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            requirements, acceptance, registry = write_traceability_files(
                root, requirement_source="SRC-404"
            )

            result = run_python(
                "validate-traceability.py",
                "--requirements",
                requirements,
                "--acceptance",
                acceptance,
                "--evidence-register",
                registry,
                "--baseline-version",
                "B-001",
            )

            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("unknown source ID SRC-404", result.stderr)

    def test_unsupported_requirement_coverage_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            requirements, acceptance, registry = write_traceability_files(
                root, coverage="banana"
            )

            result = run_python(
                "validate-traceability.py",
                "--requirements",
                requirements,
                "--acceptance",
                acceptance,
                "--evidence-register",
                registry,
                "--baseline-version",
                "B-001",
            )

            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("unsupported coverage", result.stderr)

    def test_missing_coverage_cannot_have_passed_acceptance(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            requirements, acceptance, registry = write_traceability_files(
                root, coverage="missing"
            )

            result = run_python(
                "validate-traceability.py",
                "--requirements",
                requirements,
                "--acceptance",
                acceptance,
                "--evidence-register",
                registry,
                "--baseline-version",
                "B-001",
            )

            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("coverage missing cannot have result passed", result.stderr)

    def test_evidence_requires_claims(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            requirements, acceptance, registry = write_traceability_files(root)
            value = json.loads(registry.read_text(encoding="utf-8"))
            value["evidence"][0].pop("claims")
            write_json(registry, value)

            result = run_python(
                "validate-traceability.py",
                "--requirements", requirements,
                "--acceptance", acceptance,
                "--evidence-register", registry,
                "--baseline-version", "B-001",
            )

            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("nonempty claims list", result.stderr)

    def test_evidence_claim_must_bind_current_requirement(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            requirements, acceptance, registry = write_traceability_files(root)
            value = json.loads(registry.read_text(encoding="utf-8"))
            value["evidence"][1]["claims"][0]["requirement_id"] = "REQ-999"
            write_json(registry, value)

            result = run_python(
                "validate-traceability.py",
                "--requirements", requirements,
                "--acceptance", acceptance,
                "--evidence-register", registry,
                "--baseline-version", "B-001",
            )

            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("has no claim for this requirement", result.stderr)

    def test_evidence_claim_requires_assertions(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            requirements, acceptance, registry = write_traceability_files(root)
            value = json.loads(registry.read_text(encoding="utf-8"))
            value["evidence"][0]["claims"][0]["assertions"] = []
            write_json(registry, value)

            result = run_python(
                "validate-traceability.py",
                "--requirements", requirements,
                "--acceptance", acceptance,
                "--evidence-register", registry,
                "--baseline-version", "B-001",
            )

            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("assertions must be a nonempty list", result.stderr)


class JourneyCoverageContractTests(unittest.TestCase):
    def test_valid_journey_coverage_passes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _, _, registry = write_traceability_files(root)
            value = json.loads(registry.read_text(encoding="utf-8"))
            value["evidence"][1]["claims"][0] = {
                "requirement_id": "REQ-001",
                "claim_type": "state_transition",
                "scenario_id": "JNY-001",
                "assertions": ["The request moves from draft to submitted and the reviewer owns the next action."],
            }
            write_json(registry, value)
            journeys = root / "journey-coverage.json"
            write_journey_coverage(journeys)

            result = run_python(
                "validate-journey-coverage.py",
                "--journeys", journeys,
                "--evidence-register", registry,
                "--baseline-version", "B-001",
            )

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_journey_without_matching_evidence_claim_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _, _, registry = write_traceability_files(root)
            journeys = root / "journey-coverage.json"
            write_journey_coverage(journeys)

            result = run_python(
                "validate-journey-coverage.py",
                "--journeys", journeys,
                "--evidence-register", registry,
                "--baseline-version", "B-001",
            )

            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("no test/browser evidence claim binds", result.stderr)

    def test_pending_journey_cannot_pass_final_validation(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _, _, registry = write_traceability_files(root)
            journeys = root / "journey-coverage.json"
            write_journey_coverage(journeys, result="pending")

            result = run_python(
                "validate-journey-coverage.py",
                "--journeys", journeys,
                "--evidence-register", registry,
                "--baseline-version", "B-001",
            )

            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("unfinished result", result.stderr)


class LegacyAuditTests(unittest.TestCase):
    def test_legacy_project_is_reported_as_migration_needed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "requirements.md").write_text(
                "# Requirements\n\n| Source ID | Source |\n|---|---|\n| SRC-001 | User |\n\n### REQ-FUNC-001 Submit request\n",
                encoding="utf-8",
            )
            (root / "acceptance-report.md").write_text(
                "| ID | Requirement | Evidence | Result |\n|---|---|---|---|\n| R-001 | Submit | Screenshot | passed |\n",
                encoding="utf-8",
            )
            (root / "prototype.html").write_text(
                "<html><style>body{}</style><script>document.body.dataset.ready='1'</script></html>",
                encoding="utf-8",
            )

            result = run_python("audit-legacy-project.py", root, "--format", "json")

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            report = json.loads(result.stdout)
            self.assertEqual(report["classification"], "migration_needed")
            statuses = {item["artifact"]: item["status"] for item in report["findings"]}
            self.assertEqual(statuses["requirements"], "needs_migration")
            self.assertEqual(statuses["acceptance report"], "needs_migration")
            self.assertEqual(statuses["standalone HTML"], "needs_migration")


class EvidenceManifestContractTests(unittest.TestCase):
    def test_complete_visual_pdf_coverage_passes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "requirements.pdf"
            source.write_bytes(b"pdf fixture")
            manifest = root / "evidence-manifest.json"
            write_evidence_manifest(manifest, source, total_units=3)

            result = run_python("validate-evidence-manifest.py", manifest)

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_missing_pdf_page_coverage_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "requirements.pdf"
            source.write_bytes(b"pdf fixture")
            manifest = root / "evidence-manifest.json"
            write_evidence_manifest(manifest, source, total_units=3, included_units=[1, 3])

            result = run_python("validate-evidence-manifest.py", manifest)

            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("missing unit coverage", result.stderr)


class StandaloneContractTests(unittest.TestCase):
    def test_builder_embeds_css_assets_and_output_validates(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            assets = root / "assets"
            assets.mkdir()
            source = root / "index.html"
            output = root / "prototype-standalone.html"
            (assets / "font.woff2").write_bytes(b"test-font")
            (assets / "style.css").write_text(
                "@font-face { src: url('./font.woff2'); } body { color: #111; }",
                encoding="utf-8",
            )
            (assets / "app.js").write_text(
                'document.body.dataset.ready = "true";',
                encoding="utf-8",
            )
            markers = " ".join(
                ["BPD:REQUIREMENTS", "BPD:ROLES", "BPD:FLOWS", "BPD:PAGE_GUIDES", "BPD:VERSION"]
            )
            source.write_text(
                f"""<!doctype html><html><head><link rel="stylesheet" href="assets/style.css"></head>
<body><!-- {markers} --><script type="module" src="assets/app.js"></script></body></html>""",
                encoding="utf-8",
            )

            build = run_node("build-standalone.mjs", "--input", source, "--output", output)
            self.assertEqual(build.returncode, 0, build.stdout + build.stderr)
            validation = run_python("validate-standalone-html.py", output)
            self.assertEqual(validation.returncode, 0, validation.stdout + validation.stderr)
            self.assertIn("data:font/woff2;base64,", output.read_text(encoding="utf-8"))

    def test_embedded_artifact_with_contract_markers_passes(self):
        with tempfile.TemporaryDirectory() as directory:
            html = Path(directory) / "prototype.html"
            markers = " ".join(
                ["BPD:REQUIREMENTS", "BPD:ROLES", "BPD:FLOWS", "BPD:PAGE_GUIDES", "BPD:VERSION"]
            )
            html.write_text(
                f"""<!doctype html>
<html><head><style>body {{ color: #111; }}</style></head>
<body><!-- {markers} --><script>document.body.dataset.ready = "true";</script></body></html>
""",
                encoding="utf-8",
            )

            result = run_python("validate-standalone-html.py", html)

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_relative_css_dependencies_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            html = Path(directory) / "prototype.html"
            html.write_text(
                """<!doctype html>
<html><head><style>@font-face { src: url(./font.woff2); }</style></head>
<body><script>document.body.dataset.ready = "true";</script></body></html>
""",
                encoding="utf-8",
            )

            result = run_python("validate-standalone-html.py", html)

            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("css url", result.stderr.lower())


class WorkflowStateContractTests(unittest.TestCase):
    def test_distributed_workflow_template_passes(self):
        template = ROOT / "assets" / "delivery-templates" / "prototype-workflow-state.json"

        result = run_python("validate-workflow-state.py", template)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_current_phase_must_match_earliest_actionable_phase(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            state = workflow_state(current_phase="P8_HANDOFF")
            state["phases"]["P1_EVIDENCE"] = phase(
                "confirmed",
                baseline_version="B-001",
                artifacts=["evidence-manifest.json"],
                evidence=["SRC-001"],
                confirmed_by="user",
                confirmed_at="2026-10-28T10:00:00+08:00",
            )
            state["phases"]["P2_REQUIREMENTS"] = phase(
                "blocked", decision_ids=["DEC-001"]
            )
            state["decisions"] = [
                {
                    "id": "DEC-001",
                    "status": "open",
                    "affected_phases": ["P2_REQUIREMENTS"],
                    "question": "Define the transfer contract.",
                    "recommended_option": "Confirm retry and receipt semantics.",
                }
            ]
            state["open_decisions"] = ["DEC-001"]
            source = root / "requirements.pdf"
            source.write_bytes(b"pdf fixture")
            write_evidence_manifest(root / "evidence-manifest.json", source)
            state_path = root / "prototype-workflow-state.json"
            write_json(state_path, state)

            result = run_python("validate-workflow-state.py", state_path)

            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("earliest actionable phase", result.stderr)

    def test_valid_blocked_checkpoint_passes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            state = workflow_state(current_phase="P2_REQUIREMENTS")
            state["phases"]["P1_EVIDENCE"] = phase(
                "confirmed",
                baseline_version="B-001",
                artifacts=["evidence-manifest.json"],
                evidence=["SRC-001"],
                confirmed_by="user",
                confirmed_at="2026-10-28T10:00:00+08:00",
            )
            state["phases"]["P2_REQUIREMENTS"] = phase(
                "blocked", decision_ids=["DEC-001"]
            )
            state["decisions"] = [
                {
                    "id": "DEC-001",
                    "status": "open",
                    "affected_phases": ["P2_REQUIREMENTS"],
                    "question": "Define the transfer contract.",
                    "recommended_option": "Confirm retry and receipt semantics.",
                }
            ]
            state["open_decisions"] = ["DEC-001"]
            source = root / "requirements.pdf"
            source.write_bytes(b"pdf fixture")
            write_evidence_manifest(root / "evidence-manifest.json", source)
            state_path = root / "prototype-workflow-state.json"
            write_json(state_path, state)

            result = run_python("validate-workflow-state.py", state_path)

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_blocked_phase_requires_bound_decision(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            state = workflow_state(current_phase="P1_EVIDENCE")
            state["phases"]["P1_EVIDENCE"] = phase("blocked", decision_ids=[])
            state["decisions"] = [
                {
                    "id": "DEC-001",
                    "status": "open",
                    "affected_phases": ["P2_REQUIREMENTS"],
                    "question": "Unrelated question.",
                    "recommended_option": "Resolve later.",
                }
            ]
            state["open_decisions"] = ["DEC-001"]
            state_path = root / "prototype-workflow-state.json"
            write_json(state_path, state)

            result = run_python("validate-workflow-state.py", state_path)

            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("decision_ids", result.stderr)

    def test_reused_phase_requires_revalidation_metadata(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            state = workflow_state(current_phase="P2_REQUIREMENTS")
            source = root / "requirements.pdf"
            source.write_bytes(b"pdf fixture")
            write_evidence_manifest(root / "evidence-manifest.json", source)
            state["phases"]["P1_EVIDENCE"] = phase(
                "reused",
                baseline_version="B-001",
                artifacts=["evidence-manifest.json"],
                evidence=["SRC-001"],
                confirmed_by="user",
                confirmed_at="2026-10-20T10:00:00+08:00",
            )
            state_path = root / "prototype-workflow-state.json"
            write_json(state_path, state)

            result = run_python("validate-workflow-state.py", state_path)

            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("revalidated_at", result.stderr)

    def test_valid_reused_phase_passes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            state = workflow_state(current_phase="P2_REQUIREMENTS")
            source = root / "requirements.pdf"
            source.write_bytes(b"pdf fixture")
            write_evidence_manifest(root / "evidence-manifest.json", source)
            state["phases"]["P1_EVIDENCE"] = phase(
                "reused",
                baseline_version="B-001",
                artifacts=["evidence-manifest.json"],
                evidence=["SRC-001"],
                confirmed_by="user",
                confirmed_at="2026-10-20T10:00:00+08:00",
                revalidated_by="verifier",
                revalidated_at="2026-10-28T10:00:00+08:00",
            )
            state_path = root / "prototype-workflow-state.json"
            write_json(state_path, state)

            result = run_python("validate-workflow-state.py", state_path)

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_not_applicable_requires_reason_and_scope_decision(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            state = workflow_state(current_phase="P2_REQUIREMENTS")
            state["phases"]["P1_EVIDENCE"] = phase("not_applicable")
            state_path = root / "prototype-workflow-state.json"
            write_json(state_path, state)

            result = run_python("validate-workflow-state.py", state_path)

            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("scope_decision_id", result.stderr)

    def test_valid_not_applicable_phase_passes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            state = workflow_state(current_phase="P2_REQUIREMENTS")
            state["phases"]["P1_EVIDENCE"] = phase(
                "not_applicable",
                reason="No external evidence is in scope.",
                scope_decision_id="DEC-001",
            )
            state["decisions"] = [
                {
                    "id": "DEC-001",
                    "status": "confirmed",
                    "affected_phases": ["P1_EVIDENCE"],
                    "question": "Is external evidence in scope?",
                    "recommended_option": "Exclude external evidence for this scoped task.",
                }
            ]
            state_path = root / "prototype-workflow-state.json"
            write_json(state_path, state)

            result = run_python("validate-workflow-state.py", state_path)

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
