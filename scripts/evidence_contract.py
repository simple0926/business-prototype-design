#!/usr/bin/env python3

import hashlib
import json
import mimetypes
import re
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path


SUPPORTED_SCHEMAS = {"0.3", "0.4"}
EVIDENCE_PATTERN = re.compile(r"EVD-\d{3,}")
REQUIREMENT_PATTERN = re.compile(r"REQ-\d{3,}")
EVIDENCE_KINDS = {"implementation", "test", "browser"}
CLAIM_TYPES = {"presence", "interaction", "validation", "state_transition", "delivery"}
PLACEHOLDERS = {
    "", "-", "todo", "tbd", "pending", "not-run", "not run", "not-implemented",
    "not implemented", "n/a", "na", "待确认", "待回答", "未执行", "未实现",
    "replace with", "replace-with", "lorem ipsum", "placeholder", "dummy evidence",
    "fake evidence", "sample only",
}


def is_placeholder(value):
    normalized = str(value or "").strip().lower()
    return not normalized or any(
        normalized == marker or normalized.startswith(f"{marker} ")
        for marker in PLACEHOLDERS
    )


def is_iso_8601_timestamp(value):
    if not isinstance(value, str) or "T" not in value:
        return False
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return False
    return parsed.tzinfo is not None


def sha256_file(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def normalized_text_digest(path):
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None
    normalized = " ".join(text.split())
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def resolve_path(base, value):
    path = Path(value)
    return path.resolve() if path.is_absolute() else (base / path).resolve()


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def parse_test_artifact(path):
    text = path.read_text(encoding="utf-8", errors="replace")
    suffix = path.suffix.lower()
    if suffix == ".json":
        try:
            result = json.loads(text)
        except json.JSONDecodeError as error:
            return None, f"invalid JSON test result: {error}"
        if not isinstance(result, dict):
            return None, "JSON test result must be an object"
        total = result.get("test_count", result.get("tests"))
        failed = result.get("failed", result.get("failures"))
        passed = result.get("passed")
        if not isinstance(total, int) or not isinstance(failed, int):
            return None, "JSON test result requires integer test_count/tests and failed/failures"
        if failed != 0 or (isinstance(passed, int) and passed != total):
            return None, "JSON test result reports failed tests"
        return total, None
    if suffix == ".xml":
        try:
            root = ET.fromstring(text)
        except ET.ParseError as error:
            return None, f"invalid JUnit XML: {error}"
        suites = [root] if root.tag.endswith("testsuite") else list(root.iter("testsuite"))
        if not suites:
            return None, "JUnit XML has no testsuite"
        total = sum(int(suite.attrib.get("tests", "0")) for suite in suites)
        failed = sum(
            int(suite.attrib.get("failures", "0")) + int(suite.attrib.get("errors", "0"))
            for suite in suites
        )
        if total < 1 or failed:
            return None, "JUnit XML reports no tests or failed tests"
        return total, None

    plan = re.search(r"(?m)^1\.\.(\d+)\s*$", text)
    ok_count = len(re.findall(r"(?m)^ok\s+\d+\b", text))
    not_ok_count = len(re.findall(r"(?m)^not ok\s+\d+\b", text))
    if not plan:
        return None, "test evidence must be parseable TAP, JUnit XML, or structured JSON"
    total = int(plan.group(1))
    if total < 1 or not_ok_count or ok_count != total:
        return None, "TAP result count or status is inconsistent"
    return total, None


def validate_browser_artifact(path, entry):
    try:
        result = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        return [f"browser evidence must be structured JSON: {error}"]
    errors = []
    if not isinstance(result, dict):
        return ["browser evidence JSON must be an object"]
    for field in ("environment", "target", "viewport"):
        if result.get(field) != entry.get(field):
            errors.append(f"browser evidence {field} does not match registry")
    steps = result.get("steps")
    assertions = result.get("assertions")
    if not isinstance(steps, list) or not steps:
        errors.append("browser evidence requires nonempty steps")
    if not isinstance(assertions, list) or not assertions:
        errors.append("browser evidence requires nonempty assertions")
    elif any(not isinstance(item, dict) or item.get("passed") is not True for item in assertions):
        errors.append("browser evidence contains a failed or malformed assertion")
    if result.get("console_errors") != []:
        errors.append("browser evidence console_errors must be an empty list")
    if not isinstance(result.get("network_requests"), list):
        errors.append("browser evidence network_requests must be a list")
    return errors


def validate_evidence_register(path, expected_baseline, forbidden_paths=(), require_schema=None):
    path = Path(path)
    errors = []
    if not path.is_file():
        return {}, [f"evidence register not found: {path}"]
    try:
        registry = read_json(path)
    except (OSError, json.JSONDecodeError) as error:
        return {}, [f"invalid evidence register JSON: {error}"]

    schema = registry.get("schema_version")
    if schema not in SUPPORTED_SCHEMAS:
        errors.append(f"unsupported evidence register schema_version: {schema!r}")
    if require_schema and schema != require_schema:
        errors.append(f"evidence register schema_version must be {require_schema!r}")
    if registry.get("baseline_version") != expected_baseline:
        errors.append("evidence register baseline_version does not match requested baseline")

    forbidden = {path.resolve()} | {Path(item).resolve() for item in forbidden_paths if item is not None}
    forbidden_files = [item for item in forbidden if item.is_file()]
    forbidden_digests = {sha256_file(item) for item in forbidden_files}
    forbidden_text_digests = {
        digest for item in forbidden_files if (digest := normalized_text_digest(item)) is not None
    }
    entries = registry.get("evidence")
    if not isinstance(entries, list):
        errors.append("evidence register requires an evidence list")
        return {}, errors

    by_id = {}
    for entry in entries:
        if not isinstance(entry, dict):
            errors.append("evidence entry must be an object")
            continue
        evidence_id = entry.get("id")
        if not isinstance(evidence_id, str) or not EVIDENCE_PATTERN.fullmatch(evidence_id):
            errors.append(f"invalid evidence ID: {evidence_id!r}")
            continue
        if evidence_id in by_id:
            errors.append(f"duplicate evidence ID: {evidence_id}")
        by_id[evidence_id] = entry

        for field in ("kind", "path", "result", "baseline_version", "captured_at"):
            if not entry.get(field):
                errors.append(f"{evidence_id}: missing {field}")
        kind = entry.get("kind")
        if kind not in EVIDENCE_KINDS:
            errors.append(f"{evidence_id}: unsupported evidence kind {kind!r}")
        if not is_iso_8601_timestamp(entry.get("captured_at")):
            errors.append(f"{evidence_id}: captured_at must be ISO 8601 with timezone")
        if entry.get("result") != "passed":
            errors.append(f"{evidence_id}: evidence result is not passed")
        if entry.get("baseline_version") != expected_baseline:
            errors.append(f"{evidence_id}: evidence baseline_version does not match")

        resolved = None
        evidence_path = entry.get("path")
        if evidence_path:
            resolved = resolve_path(path.resolve().parent, evidence_path)
            if not resolved.is_file():
                errors.append(f"{evidence_id}: evidence path is not a file: {evidence_path}")
            elif resolved in forbidden or any(resolved.samefile(item) for item in forbidden_files):
                errors.append(f"{evidence_id}: evidence path cannot point to a contract it claims to prove: {evidence_path}")
            elif sha256_file(resolved) in forbidden_digests:
                errors.append(f"{evidence_id}: evidence content duplicates a forbidden contract")
            elif (
                (text_digest := normalized_text_digest(resolved)) is not None
                and text_digest in forbidden_text_digests
            ):
                errors.append(f"{evidence_id}: normalized evidence text duplicates a forbidden contract")
            else:
                try:
                    sample = resolved.read_bytes()[:4096]
                    decoded = sample.decode("utf-8", errors="ignore").strip().lower()
                    if decoded and any(
                        marker in decoded
                        for marker in (
                            "lorem ipsum", "not-run", "not implemented", "placeholder evidence",
                            "dummy evidence", "fake evidence", "sample only",
                        )
                    ):
                        errors.append(f"{evidence_id}: evidence artifact contains placeholder content")
                except OSError as error:
                    errors.append(f"{evidence_id}: cannot read evidence artifact: {error}")

        if schema == "0.4" and resolved is not None and resolved.is_file():
            expected_hash = entry.get("sha256")
            expected_bytes = entry.get("bytes")
            expected_media_type = entry.get("media_type")
            if not isinstance(expected_hash, str) or not re.fullmatch(r"[0-9a-f]{64}", expected_hash):
                errors.append(f"{evidence_id}: sha256 must be a lowercase 64-character digest")
            elif sha256_file(resolved) != expected_hash:
                errors.append(f"{evidence_id}: sha256 does not match evidence artifact")
            if not isinstance(expected_bytes, int) or expected_bytes < 1:
                errors.append(f"{evidence_id}: bytes must be a positive integer")
            elif resolved.stat().st_size != expected_bytes:
                errors.append(f"{evidence_id}: bytes does not match evidence artifact")
            guessed_media_type = mimetypes.guess_type(resolved.name)[0] or "application/octet-stream"
            if expected_media_type != guessed_media_type:
                errors.append(
                    f"{evidence_id}: media_type must match artifact type: expected {guessed_media_type!r}"
                )

        claims = entry.get("claims")
        if not isinstance(claims, list) or not claims:
            errors.append(f"{evidence_id}: evidence requires a nonempty claims list")
        else:
            for index, claim in enumerate(claims, start=1):
                prefix = f"{evidence_id} claim {index}"
                if not isinstance(claim, dict):
                    errors.append(f"{prefix}: claim must be an object")
                    continue
                requirement_id = claim.get("requirement_id")
                if not isinstance(requirement_id, str) or not REQUIREMENT_PATTERN.fullmatch(requirement_id):
                    errors.append(f"{prefix}: invalid requirement_id {requirement_id!r}")
                if claim.get("claim_type") not in CLAIM_TYPES:
                    errors.append(f"{prefix}: unsupported claim_type {claim.get('claim_type')!r}")
                if is_placeholder(claim.get("scenario_id")):
                    errors.append(f"{prefix}: missing scenario_id")
                assertions = claim.get("assertions")
                if not isinstance(assertions, list) or not assertions:
                    errors.append(f"{prefix}: assertions must be a nonempty list")
                elif any(is_placeholder(assertion) for assertion in assertions):
                    errors.append(f"{prefix}: assertions contain an empty or placeholder value")

        if schema == "0.4" and kind == "test":
            if is_placeholder(entry.get("command")):
                errors.append(f"{evidence_id}: test evidence requires command")
            if entry.get("exit_code") != 0:
                errors.append(f"{evidence_id}: test evidence exit_code must be 0")
            if not isinstance(entry.get("test_count"), int) or entry.get("test_count") < 1:
                errors.append(f"{evidence_id}: test evidence test_count must be at least 1")
            if is_placeholder(entry.get("result_summary")):
                errors.append(f"{evidence_id}: test evidence requires result_summary")
            if resolved is not None and resolved.is_file():
                actual_count, parse_error = parse_test_artifact(resolved)
                if parse_error:
                    errors.append(f"{evidence_id}: {parse_error}")
                elif actual_count != entry.get("test_count"):
                    errors.append(f"{evidence_id}: test_count does not match parsed test artifact")
        if schema == "0.4" and kind == "browser":
            for field in ("environment", "target", "viewport", "result_summary", "command"):
                if is_placeholder(entry.get(field)):
                    errors.append(f"{evidence_id}: browser evidence requires {field}")
            if entry.get("exit_code") != 0:
                errors.append(f"{evidence_id}: browser evidence exit_code must be 0")
            if resolved is not None and resolved.is_file():
                errors.extend(f"{evidence_id}: {error}" for error in validate_browser_artifact(resolved, entry))

    return by_id, errors
