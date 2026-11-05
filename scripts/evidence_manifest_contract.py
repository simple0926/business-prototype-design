#!/usr/bin/env python3

import json
import re
from pathlib import Path

from evidence_contract import sha256_file


CLASSIFICATIONS = {"business", "visual", "mixed", "out_of_scope"}
VISUAL_METHODS = {"render", "visual"}
EVIDENCE_PATTERN = re.compile(r"EVD-\d{3,}")
SUPPORTED_SCHEMAS = {"0.3", "0.4"}


def inferred_binary_kind(path):
    suffix = path.suffix.lower()
    try:
        header = path.read_bytes()[:16]
    except OSError:
        return None
    if suffix == ".pdf" or header.startswith(b"%PDF-"):
        return "pdf"
    if suffix in {".png", ".jpg", ".jpeg", ".gif", ".webp", ".avif", ".bmp", ".tif", ".tiff"}:
        return "image"
    if header.startswith((b"\x89PNG\r\n\x1a\n", b"\xff\xd8\xff", b"GIF87a", b"GIF89a")):
        return "image"
    if header.startswith(b"RIFF") and header[8:12] == b"WEBP":
        return "image"
    return None


def resolve_path(base, value):
    path = Path(value)
    return path if path.is_absolute() else (base / path).resolve()


def load_manifest(path):
    try:
        return json.loads(path.read_text(encoding="utf-8")), []
    except (OSError, json.JSONDecodeError) as error:
        return None, [f"invalid evidence manifest: {error}"]


def validate_manifest(path, evidence_ids=None, expected_baseline=None, require_schema=None):
    path = Path(path).resolve()
    manifest, errors = load_manifest(path)
    if manifest is None:
        return errors, {"sources": 0, "units": 0}

    schema = manifest.get("schema_version")
    if schema not in SUPPORTED_SCHEMAS:
        errors.append(f"unsupported evidence manifest schema_version: {manifest.get('schema_version')!r}")
    if require_schema and schema != require_schema:
        errors.append(f"evidence manifest schema_version must be {require_schema!r}")
    if schema == "0.4":
        if not manifest.get("baseline_version"):
            errors.append("evidence manifest requires baseline_version")
        elif expected_baseline and manifest.get("baseline_version") != expected_baseline:
            errors.append("evidence manifest baseline_version does not match")

    sources = manifest.get("sources")
    if not isinstance(sources, list) or not sources:
        errors.append("evidence manifest requires a nonempty sources list")
        return errors, {"sources": 0, "units": 0}

    source_ids = set()
    unit_count = 0
    for source in sources:
        if not isinstance(source, dict):
            errors.append("source entry must be an object")
            continue
        source_id = source.get("source_id")
        if not source_id:
            errors.append("source entry requires source_id")
            source_id = "<missing>"
        elif source_id in source_ids:
            errors.append(f"duplicate source_id: {source_id}")
        source_ids.add(source_id)

        source_path = source.get("path")
        if not source_path:
            errors.append(f"{source_id}: source path is required")
        else:
            resolved_source = resolve_path(path.parent, source_path)
            if not resolved_source.is_file():
                errors.append(f"{source_id}: source path not found: {source_path}")
            else:
                inferred_kind = inferred_binary_kind(resolved_source)
                if inferred_kind and source.get("kind") != inferred_kind:
                    errors.append(f"{source_id}: source kind must match detected {inferred_kind} file")
                if schema == "0.4":
                    if source.get("sha256") != sha256_file(resolved_source):
                        errors.append(f"{source_id}: source sha256 does not match")
                    if source.get("bytes") != resolved_source.stat().st_size:
                        errors.append(f"{source_id}: source bytes does not match")
        if not source.get("authority"):
            errors.append(f"{source_id}: authority is required")
        if source.get("kind") not in {"pdf", "image", "document", "code", "other"}:
            errors.append(f"{source_id}: unsupported kind {source.get('kind')!r}")
        if source.get("kind") in {"pdf", "image"} and source.get("requires_visual_review") is not True:
            errors.append(f"{source_id}: PDF and image sources require visual review")

        total_units = source.get("total_units")
        if not isinstance(total_units, int) or total_units < 1:
            errors.append(f"{source_id}: total_units must be a positive integer")
            continue
        units = source.get("units")
        if not isinstance(units, list):
            errors.append(f"{source_id}: units must be a list")
            continue
        unit_count += len(units)
        sequences = []
        for unit in units:
            if not isinstance(unit, dict):
                errors.append(f"{source_id}: unit entry must be an object")
                continue
            sequence = unit.get("sequence")
            if not isinstance(sequence, int):
                errors.append(f"{source_id}: unit sequence must be an integer")
                continue
            sequences.append(sequence)
            unit_label = unit.get("unit_id") or f"unit-{sequence}"
            if unit.get("inspected") is not True:
                errors.append(f"{source_id}/{unit_label}: unit is not inspected")
            methods = set(unit.get("inspection_methods") or [])
            if not methods:
                errors.append(f"{source_id}/{unit_label}: inspection_methods are required")
            if source.get("requires_visual_review") is True and not methods.intersection(VISUAL_METHODS):
                errors.append(f"{source_id}/{unit_label}: visual review requires render or visual inspection")
            classification = unit.get("classification")
            if classification not in CLASSIFICATIONS:
                errors.append(f"{source_id}/{unit_label}: unsupported classification {classification!r}")
            if classification == "out_of_scope":
                if not unit.get("notes"):
                    errors.append(f"{source_id}/{unit_label}: out_of_scope unit requires notes")
            else:
                unit_evidence_ids = unit.get("evidence_ids")
                if not isinstance(unit_evidence_ids, list) or not unit_evidence_ids:
                    errors.append(f"{source_id}/{unit_label}: in-scope unit requires evidence_ids")
                else:
                    for evidence_id in unit_evidence_ids:
                        if not isinstance(evidence_id, str) or not EVIDENCE_PATTERN.fullmatch(evidence_id):
                            errors.append(f"{source_id}/{unit_label}: invalid evidence ID {evidence_id!r}")
                        elif evidence_ids is not None and evidence_id not in evidence_ids:
                            errors.append(f"{source_id}/{unit_label}: unknown evidence ID {evidence_id}")

        expected = set(range(1, total_units + 1))
        actual = set(sequences)
        missing = sorted(expected - actual)
        duplicates = sorted(number for number in actual if sequences.count(number) > 1)
        out_of_range = sorted(actual - expected)
        if missing:
            errors.append(f"{source_id}: missing unit coverage: {', '.join(map(str, missing))}")
        if duplicates:
            errors.append(f"{source_id}: duplicate unit coverage: {', '.join(map(str, duplicates))}")
        if out_of_range:
            errors.append(f"{source_id}: out-of-range units: {', '.join(map(str, out_of_range))}")

    return errors, {"sources": len(sources), "units": unit_count}
