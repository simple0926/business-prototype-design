#!/usr/bin/env python3

import json
import hashlib
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from test_contracts import (
    PHASE_IDS,
    ROOT,
    contract_sections,
    phase,
    run_python,
    workflow_state,
    write_evidence_manifest,
    write_json,
    write_traceability_files,
)


def refresh_evidence_entry(sample_root, entry):
    artifact = sample_root / entry["path"]
    payload = artifact.read_bytes()
    entry["sha256"] = hashlib.sha256(payload).hexdigest()
    entry["bytes"] = len(payload)


def copy_golden_sample(destination):
    sample = ROOT / "examples" / "golden-sample"
    copied = destination / "golden-sample"
    shutil.copytree(sample, copied)
    return copied


def run_golden_package(sample, include_journey=True):
    arguments = [
        "--workflow-state", sample / "prototype-workflow-state.json",
        "--requirements", sample / "requirements-analysis.md",
        "--prototype-spec", sample / "prototype-spec.md",
        "--acceptance", sample / "acceptance-report.md",
        "--evidence-register", sample / "evidence-register.json",
        "--standalone", sample / "prototype-standalone.html",
        "--baseline-version", "B-GOLDEN-001",
    ]
    if include_journey:
        arguments.extend(["--journey-coverage", sample / "journey-coverage.json"])
    return run_python("validate-package.py", *arguments)


class TraceabilityHardeningTests(unittest.TestCase):
    def validate(self, requirements, acceptance, registry):
        return run_python(
            "validate-traceability.py",
            "--requirements", requirements,
            "--acceptance", acceptance,
            "--evidence-register", registry,
            "--baseline-version", "B-001",
        )

    def test_requirements_document_cannot_be_its_own_evidence(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            requirements, acceptance, registry = write_traceability_files(root)
            value = json.loads(registry.read_text(encoding="utf-8"))
            for entry in value["evidence"]:
                entry["path"] = requirements.name
                entry["claims"][0]["assertions"] = ["lorem ipsum"]
            write_json(registry, value)

            result = self.validate(requirements, acceptance, registry)

            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_page_and_acceptance_mappings_must_resolve(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            requirements, acceptance, registry = write_traceability_files(root)
            text = requirements.read_text(encoding="utf-8")
            requirements.write_text(
                text.replace("PAGE-001#submit", "PAGE-999#ghost").replace("ACC-001", "ACC-999"),
                encoding="utf-8",
            )

            result = self.validate(requirements, acceptance, registry)

            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_blocked_report_marker_cannot_pass(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            requirements, acceptance, registry = write_traceability_files(root)
            acceptance.write_text(
                "<!-- ACCEPTANCE_RESULT: blocked -->\n- Overall result: blocked\n"
                + acceptance.read_text(encoding="utf-8"),
                encoding="utf-8",
            )

            result = self.validate(requirements, acceptance, registry)

            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_localized_source_header_is_supported(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            requirements, acceptance, registry = write_traceability_files(root)
            requirements.write_text(
                requirements.read_text(encoding="utf-8").replace("Source ID", "来源 ID"),
                encoding="utf-8",
            )

            result = self.validate(requirements, acceptance, registry)

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_contradictory_design_qa_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            requirements, acceptance, registry = write_traceability_files(root)
            design_qa = root / "design-qa.md"
            design_qa.write_text(
                "<!-- DESIGN_QA_RESULT: passed -->\n- Final result: blocked\n",
                encoding="utf-8",
            )

            result = run_python(
                "validate-traceability.py",
                "--requirements", requirements,
                "--acceptance", acceptance,
                "--evidence-register", registry,
                "--baseline-version", "B-001",
                "--design-qa", design_qa,
            )

            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_contract_copy_cannot_be_renamed_as_evidence(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            requirements, acceptance, registry = write_traceability_files(root)
            copied = root / "renamed-contract.txt"
            copied.write_bytes(requirements.read_bytes() + b"\n")
            value = json.loads(registry.read_text(encoding="utf-8"))
            value["evidence"][0]["path"] = copied.name
            write_json(registry, value)

            result = self.validate(requirements, acceptance, registry)

            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_placeholder_phrase_in_evidence_artifact_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            requirements, acceptance, registry = write_traceability_files(root)
            (root / "test-result.txt").write_text("placeholder evidence only", encoding="utf-8")

            result = self.validate(requirements, acceptance, registry)

            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)


class WorkflowHardeningTests(unittest.TestCase):
    def test_lite_mode_accepts_only_low_risk_scope(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            state = workflow_state(current_phase="P1_EVIDENCE")
            state["mode"] = "lite"
            state["risk_profile"] = {
                "actor_count": 1,
                "canonical_state_count": 2,
                "has_permission_rules": False,
                "handles_money": False,
                "allows_deletion": False,
                "has_external_effects": False,
                "handles_sensitive_data": False,
                "has_approval_flow": False,
            }
            state_path = root / "prototype-workflow-state.json"
            write_json(state_path, state)

            result = run_python("validate-workflow-state.py", state_path)

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_lite_mode_rejects_multi_actor_scope(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            state = workflow_state(current_phase="P1_EVIDENCE")
            state["mode"] = "lite"
            state["risk_profile"] = {
                "actor_count": 2,
                "canonical_state_count": 2,
                "has_permission_rules": False,
                "handles_money": False,
                "allows_deletion": False,
                "has_external_effects": False,
                "handles_sensitive_data": False,
                "has_approval_flow": False,
            }
            state_path = root / "prototype-workflow-state.json"
            write_json(state_path, state)

            result = run_python("validate-workflow-state.py", state_path)

            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_fabricated_confirmation_and_dangling_evidence_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "requirements.pdf"
            source.write_bytes(b"fixture")
            manifest = root / "evidence-manifest.json"
            write_evidence_manifest(manifest, source)
            dummy = root / "artifact.txt"
            dummy.write_text("lorem ipsum", encoding="utf-8")
            (root / "journey-coverage.json").write_text("{}", encoding="utf-8")
            state = workflow_state(current_phase="P8_HANDOFF")
            for phase_id in PHASE_IDS:
                state["phases"][phase_id] = phase(
                    "confirmed",
                    baseline_version="B-001",
                    artifacts=[manifest.name if phase_id == "P1_EVIDENCE" else dummy.name],
                    evidence=["EVD-DOES-NOT-EXIST"],
                    confirmed_by="invented-user",
                    confirmed_at="not-a-timestamp",
                )
            state_path = root / "prototype-workflow-state.json"
            write_json(state_path, state)

            result = run_python("validate-workflow-state.py", state_path)

            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_upstream_invalidation_propagates_downstream(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            artifact = root / "artifact.txt"
            artifact.write_text("verified artifact", encoding="utf-8")
            state = workflow_state(current_phase="P1_EVIDENCE")
            state["decisions"] = [{
                "id": "DEC-001",
                "status": "confirmed",
                "affected_phases": PHASE_IDS,
            }]
            state["phases"]["P1_EVIDENCE"] = phase("invalidated", invalidated_by="DEC-001")
            for phase_id in PHASE_IDS[1:]:
                state["phases"][phase_id] = phase(
                    "confirmed",
                    baseline_version="B-001",
                    artifacts=[artifact.name],
                    evidence=["EVD-001"],
                    confirmed_by="user",
                    confirmed_at="2026-11-04T10:00:00+08:00",
                )
            state_path = root / "prototype-workflow-state.json"
            write_json(state_path, state)

            result = run_python("validate-workflow-state.py", state_path)

            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_text_only_p1_does_not_require_manifest(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "requirements.md"
            source.write_text("# Requirements\n", encoding="utf-8")
            state = workflow_state(current_phase="P2_REQUIREMENTS")
            state["evidence_profile"] = "text_only"
            state["evidence_manifest"] = None
            state["text_source_ids"] = ["SRC-001"]
            state["phases"]["P1_EVIDENCE"] = phase(
                "confirmed",
                baseline_version="B-001",
                artifacts=[source.name],
                evidence=["SRC-001"],
                confirmed_by="user",
                confirmed_at="2026-11-04T10:00:00+08:00",
            )
            state_path = root / "prototype-workflow-state.json"
            write_json(state_path, state)

            result = run_python("validate-workflow-state.py", state_path)

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


class ManifestAndJourneyHardeningTests(unittest.TestCase):
    def test_manifest_rejects_fabricated_evidence_id(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "requirements.pdf"
            source.write_bytes(b"fixture")
            manifest = root / "evidence-manifest.json"
            write_evidence_manifest(manifest, source)
            value = json.loads(manifest.read_text(encoding="utf-8"))
            value["sources"][0]["units"][0]["evidence_ids"] = ["MADE-UP-EVIDENCE"]
            write_json(manifest, value)

            result = run_python("validate-evidence-manifest.py", manifest)

            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_pdf_cannot_disable_visual_review(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "requirements.pdf"
            source.write_bytes(b"fixture")
            manifest = root / "evidence-manifest.json"
            write_evidence_manifest(manifest, source)
            value = json.loads(manifest.read_text(encoding="utf-8"))
            value["sources"][0]["requires_visual_review"] = False
            value["sources"][0]["units"][0]["inspection_methods"] = ["text"]
            write_json(manifest, value)

            result = run_python("validate-evidence-manifest.py", manifest)

            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_pdf_file_cannot_be_declared_as_other_kind(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "requirements.pdf"
            source.write_bytes(b"%PDF-1.7\nfixture")
            manifest = root / "evidence-manifest.json"
            write_evidence_manifest(manifest, source)
            value = json.loads(manifest.read_text(encoding="utf-8"))
            value["sources"][0]["kind"] = "other"
            value["sources"][0]["requires_visual_review"] = False
            value["sources"][0]["units"][0]["inspection_methods"] = ["text"]
            write_json(manifest, value)

            result = run_python("validate-evidence-manifest.py", manifest)

            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_journey_rejects_unvalidated_registry_entry(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            journeys = root / "journey-coverage.json"
            evidence = root / "evidence-register.json"
            write_json(journeys, {
                "schema_version": "0.3",
                "baseline_version": "B-001",
                "journeys": [{
                    "id": "JNY-001",
                    "requirement_ids": ["REQ-404"],
                    "claim_type": "state_transition",
                    "actor": "Requester",
                    "start_state": "draft",
                    "action": "Submit",
                    "expected_state": "submitted",
                    "next_actor": "Reviewer",
                    "risk_tags": ["core_path"],
                    "evidence_ids": ["EVD-001"],
                    "result": "passed",
                }],
            })
            write_json(evidence, {
                "baseline_version": "B-001",
                "evidence": [{
                    "id": "EVD-001",
                    "kind": "test",
                    "result": "passed",
                    "baseline_version": "B-001",
                    "path": "does-not-exist",
                    "captured_at": "not-a-time",
                    "claims": [{
                        "requirement_id": "REQ-404",
                        "claim_type": "state_transition",
                        "scenario_id": "JNY-001",
                        "assertions": ["lorem ipsum"],
                    }],
                }],
            })

            result = run_python(
                "validate-journey-coverage.py",
                "--journeys", journeys,
                "--evidence-register", evidence,
                "--baseline-version", "B-001",
            )

            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)


class StandaloneHardeningTests(unittest.TestCase):
    def test_css_import_and_static_module_import_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            html = Path(directory) / "prototype.html"
            markers = " ".join([
                "BPD:REQUIREMENTS", "BPD:ROLES", "BPD:FLOWS", "BPD:PAGE_GUIDES", "BPD:VERSION"
            ])
            html.write_text(
                "<style>@import 'https://example.invalid/x.css';x{color:red}</style>"
                f"<!-- {markers} -->"
                "<script type='module'>import './missing.js';</script>",
                encoding="utf-8",
            )

            result = run_python("validate-standalone-html.py", html)

            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_comment_obfuscation_and_mixed_srcset_are_rejected(self):
        cases = {
            "srcset_without_descriptor": (
                "<style>x{color:red}</style>",
                "<img srcset=\"data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///ywAAAAAAQABAAACAUwAOw==, https://example.invalid/leak.png 2x\">",
                "<script>document.body.dataset.ready='yes'</script>",
            ),
            "css_escape": (
                "<style>@\\69mport 'https://example.invalid/x.css';x{color:red}</style>",
                "",
                "<script>document.body.dataset.ready='yes'</script>",
            ),
            "javascript_line_comment": (
                "<style>x{color:red}</style>",
                "",
                "<script type='module'>import//comment\n'./missing.js';</script>",
            ),
        }
        for label, fragments in cases.items():
            with self.subTest(label=label), tempfile.TemporaryDirectory() as directory:
                html = Path(directory) / "prototype.html"
                html.write_text("".join(fragments) + contract_sections(), encoding="utf-8")

                result = run_python("validate-standalone-html.py", html)

                self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_import_examples_inside_strings_are_allowed(self):
        with tempfile.TemporaryDirectory() as directory:
            html = Path(directory) / "prototype.html"
            html.write_text(
                "<style>p::before{content:\"@import 'example-only.css'\"}</style>"
                + contract_sections()
                + "<script>const text=`import './example-only.js'`;document.body.dataset.text=text</script>",
                encoding="utf-8",
            )

            result = run_python("validate-standalone-html.py", html)

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


class GoldenSampleAndBuilderTests(unittest.TestCase):
    def test_golden_sample_package_passes(self):
        sample = ROOT / "examples" / "golden-sample"
        result = run_python(
            "validate-package.py",
            "--workflow-state", sample / "prototype-workflow-state.json",
            "--requirements", sample / "requirements-analysis.md",
            "--prototype-spec", sample / "prototype-spec.md",
            "--acceptance", sample / "acceptance-report.md",
            "--evidence-register", sample / "evidence-register.json",
            "--journey-coverage", sample / "journey-coverage.json",
            "--standalone", sample / "prototype-standalone.html",
            "--baseline-version", "B-GOLDEN-001",
        )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_package_rejects_workflow_argument_mismatch(self):
        sample = ROOT / "examples" / "golden-sample"
        with tempfile.TemporaryDirectory() as directory:
            copied_register = Path(directory) / "evidence-register.json"
            copied_register.write_text(
                (sample / "evidence-register.json").read_text(encoding="utf-8"),
                encoding="utf-8",
            )
            result = run_python(
                "validate-package.py",
                "--workflow-state", sample / "prototype-workflow-state.json",
                "--requirements", sample / "requirements-analysis.md",
                "--prototype-spec", sample / "prototype-spec.md",
                "--acceptance", sample / "acceptance-report.md",
                "--evidence-register", copied_register,
                "--journey-coverage", sample / "journey-coverage.json",
                "--standalone", sample / "prototype-standalone.html",
                "--baseline-version", "B-GOLDEN-001",
            )

            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_package_rejects_nonterminal_handoff(self):
        sample = ROOT / "examples" / "golden-sample"
        with tempfile.TemporaryDirectory() as directory:
            state = json.loads((sample / "prototype-workflow-state.json").read_text(encoding="utf-8"))
            for phase_value in state["phases"].values():
                phase_value["artifacts"] = [
                    str((sample / path).resolve()) for path in phase_value.get("artifacts", [])
                ]
            state["evidence_register"] = str((sample / "evidence-register.json").resolve())
            state["journey_coverage"] = str((sample / "journey-coverage.json").resolve())
            state["phases"]["P8_HANDOFF"]["status"] = "not_started"
            state_path = Path(directory) / "prototype-workflow-state.json"
            write_json(state_path, state)
            result = run_python(
                "validate-package.py",
                "--workflow-state", state_path,
                "--requirements", sample / "requirements-analysis.md",
                "--prototype-spec", sample / "prototype-spec.md",
                "--acceptance", sample / "acceptance-report.md",
                "--evidence-register", sample / "evidence-register.json",
                "--journey-coverage", sample / "journey-coverage.json",
                "--standalone", sample / "prototype-standalone.html",
                "--baseline-version", "B-GOLDEN-001",
            )

            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_package_rejects_lite_profile_that_conflicts_with_business_model(self):
        with tempfile.TemporaryDirectory() as directory:
            sample = copy_golden_sample(Path(directory))
            state_path = sample / "prototype-workflow-state.json"
            state = json.loads(state_path.read_text(encoding="utf-8"))
            state["mode"] = "lite"
            state["risk_profile"] = {
                "actor_count": 1,
                "canonical_state_count": 2,
                "has_permission_rules": False,
                "handles_money": False,
                "allows_deletion": False,
                "has_external_effects": False,
                "handles_sensitive_data": False,
                "has_approval_flow": False,
            }
            state["journey_profile"] = "none"
            state["journey_coverage"] = None
            write_json(state_path, state)

            result = run_golden_package(sample, include_journey=False)

            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_package_rejects_text_profile_for_image_bearing_source(self):
        for source_type in ("PDF image screenshot baseline", "PNG Figma wireframe baseline"):
            with self.subTest(source_type=source_type), tempfile.TemporaryDirectory() as directory:
                sample = copy_golden_sample(Path(directory))
                requirements = sample / "requirements-analysis.md"
                requirements.write_text(
                    requirements.read_text(encoding="utf-8").replace(
                        "approved text baseline", source_type
                    ),
                    encoding="utf-8",
                )

                result = run_golden_package(sample)

                self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_package_rejects_cross_artifact_id_mismatches(self):
        mutations = {
            "decision": ("DEC-001", "DEC-999"),
            "journey": ("JNY-001", "JNY-999"),
            "source": ("SRC-001", "SRC-999"),
        }
        for label, (old, new) in mutations.items():
            with self.subTest(label=label), tempfile.TemporaryDirectory() as directory:
                sample = copy_golden_sample(Path(directory))
                requirements = sample / "requirements-analysis.md"
                requirements.write_text(
                    requirements.read_text(encoding="utf-8").replace(old, new),
                    encoding="utf-8",
                )

                result = run_golden_package(sample)

                self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_package_rejects_content_identical_contract_evidence(self):
        with tempfile.TemporaryDirectory() as directory:
            sample = copy_golden_sample(Path(directory))
            copied = sample / "evidence" / "implementation-copy.txt"
            copied.write_bytes((sample / "requirements-analysis.md").read_bytes())
            registry_path = sample / "evidence-register.json"
            registry = json.loads(registry_path.read_text(encoding="utf-8"))
            registry["evidence"][0]["path"] = "evidence/implementation-copy.txt"
            registry["evidence"][0]["media_type"] = "text/plain"
            refresh_evidence_entry(sample, registry["evidence"][0])
            write_json(registry_path, registry)

            result = run_golden_package(sample)

            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_golden_sample_behavior_runner_matches_recorded_output(self):
        sample = ROOT / "examples" / "golden-sample"
        result = subprocess.run(
            ["node", "verify-sample.mjs"],
            cwd=sample,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(
            result.stdout,
            (sample / "evidence" / "test-results.tap").read_text(encoding="utf-8"),
        )
        trace_result = subprocess.run(
            ["node", "verify-sample.mjs", "--trace-json"],
            cwd=sample,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(trace_result.returncode, 0, trace_result.stdout + trace_result.stderr)
        self.assertEqual(
            trace_result.stdout,
            (sample / "evidence" / "dom-harness-results.json").read_text(encoding="utf-8"),
        )

    def test_builder_rejects_parent_path_escape(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            project = root / "project"
            project.mkdir()
            (root / "outside.css").write_text("body{color:red}", encoding="utf-8")
            (root / "outside.js").write_text("document.body.dataset.leaked='yes'", encoding="utf-8")
            source = project / "index.html"
            output = project / "out.html"
            source.write_text(
                "<link rel='stylesheet' href='../outside.css'>"
                "<script src='../outside.js'></script>",
                encoding="utf-8",
            )

            result = subprocess.run(
                ["node", str(ROOT / "scripts" / "build-standalone.mjs"),
                 "--input", str(source), "--output", str(output)],
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_builder_rejects_symlink_escape(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            project = root / "project"
            project.mkdir()
            outside = root / "outside.css"
            outside.write_text("body{color:red}", encoding="utf-8")
            (project / "linked.css").symlink_to(outside)
            (project / "app.js").write_text("document.body.dataset.ready='yes'", encoding="utf-8")
            source = project / "index.html"
            output = project / "out.html"
            source.write_text(
                "<link rel='stylesheet' href='linked.css'><script src='app.js'></script>",
                encoding="utf-8",
            )

            result = subprocess.run(
                ["node", str(ROOT / "scripts" / "build-standalone.mjs"),
                 "--input", str(source), "--output", str(output)],
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_builder_rejects_static_module_import(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "style.css").write_text("body{color:#111}", encoding="utf-8")
            (root / "app.js").write_text("import './missing.js';", encoding="utf-8")
            source = root / "index.html"
            output = root / "out.html"
            source.write_text(
                "<link rel='stylesheet' href='style.css'>"
                "<script type='module' src='app.js'></script>",
                encoding="utf-8",
            )

            result = subprocess.run(
                ["node", str(ROOT / "scripts" / "build-standalone.mjs"),
                 "--input", str(source), "--output", str(output)],
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_builder_rejects_comment_obfuscated_imports(self):
        cases = {
            "javascript": ("body{color:#111}", "/*comment*/ import/*comment*/ './missing.js';"),
            "css": ("@import/**/'https://example.invalid/x.css';body{color:#111}", "document.body.dataset.ready='yes'"),
            "javascript_line_comment": ("body{color:#111}", "import//comment\n'./missing.js';"),
            "css_escape": ("@\\69mport 'https://example.invalid/x.css';body{color:#111}", "document.body.dataset.ready='yes'"),
        }
        for label, (css, javascript) in cases.items():
            with self.subTest(label=label), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                (root / "style.css").write_text(css, encoding="utf-8")
                (root / "app.js").write_text(javascript, encoding="utf-8")
                source = root / "index.html"
                output = root / "out.html"
                source.write_text(
                    "<link rel='stylesheet' href='style.css'>"
                    "<script type='module' src='app.js'></script>",
                    encoding="utf-8",
                )

                result = subprocess.run(
                    ["node", str(ROOT / "scripts" / "build-standalone.mjs"),
                     "--input", str(source), "--output", str(output)],
                    capture_output=True,
                    text=True,
                    check=False,
                )

                self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_builder_allows_import_examples_inside_strings(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "style.css").write_text(
                "p::before{content:\"@import 'example-only.css'\"}", encoding="utf-8"
            )
            (root / "app.js").write_text(
                "const text=`import './example-only.js'`;document.body.dataset.text=text",
                encoding="utf-8",
            )
            source = root / "index.html"
            output = root / "out.html"
            source.write_text(
                "<link rel='stylesheet' href='style.css'>"
                "<script src='app.js'></script>",
                encoding="utf-8",
            )

            result = subprocess.run(
                ["node", str(ROOT / "scripts" / "build-standalone.mjs"),
                 "--input", str(source), "--output", str(output)],
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
